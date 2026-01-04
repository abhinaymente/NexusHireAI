import sys
import os
from unittest.mock import MagicMock, patch, ANY

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock environment before imports to prevent RuntimeError
with patch.dict('os.environ', {'GROQ_API_KEY': 'mock_key', 'GOOGLE_CREDENTIALS': 'e30='}):
    import ai_evaluator
    from ai_evaluator import check_resume
    from email_sender import send_email

@patch("ai_evaluator.client")
def test_ai_evaluator_dynamic_role(mock_groq):
    print("Testing AI Evaluator with Dynamic Role...")
    
    # Mock AI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "ELIGIBLE"
    mock_groq.chat.completions.create.return_value = mock_response
    
    resume_text = "Experienced Data Scientist with expertise in Python."
    
    # Test for Data Scientist role
    decision = check_resume(resume_text, role_name="Data Scientist", requirements="Deep knowledge of Python")
    print(f"Data Scientist Decision: {decision}")
    
    # Verify the prompt contained the role name
    args, kwargs = mock_groq.chat.completions.create.call_args
    prompt = kwargs['messages'][1]['content']
    assert "Data Scientist" in prompt
    print("AI prompt correctly included dynamic role.")

@patch("email_sender.get_gmail_service")
@patch("email_sender.smtplib.SMTP")
@patch("email_sender.smtplib.SMTP_SSL")
def test_email_branding(mock_smtp_ssl, mock_smtp, mock_gmail):
    print("\nTesting Email Branding and Logic...")
    
    # Mock Gmail Service
    mock_service = MagicMock()
    mock_gmail.return_value = mock_service
    
    # 1. Test Whitelabeling (Gmail)
    send_email(
        "test@example.com", 
        "ELIGIBLE\nMeet: https://meet.google.com/abc",
        company_name="SpaceX",
        tagline="Making life multi-planetary",
        role_name="Rocket Scientist"
    )
    
    # Verify Gmail API called
    args, kwargs = mock_service.users().messages().send.call_args
    print("Gmail API test passed (Whitelabeling parameters accepted)")

    # 2. Test SMTP SSL Logic (Port 465)
    send_email(
        "test@example.com",
        "NOT ELIGIBLE",
        company_name="Tesla",
        use_own_smtp=True,
        smtp_config={"host": "smtp.tesla.com", "port": 465, "user": "hr@tesla.com", "password": "xyz"}
    )
    
    mock_smtp_ssl.assert_called_with("smtp.tesla.com", 465, context=ANY)
    print("SMTP SSL test passed (Port 465 path triggered)")

    # 3. Test SMTP STARTTLS Logic (Port 587)
    send_email(
        "test@example.com",
        "NOT ELIGIBLE",
        company_name="Apple",
        use_own_smtp=True,
        smtp_config={"host": "smtp.apple.com", "port": 587, "user": "hr@apple.com", "password": "xyz"}
    )
    
    mock_smtp.assert_called_with("smtp.apple.com", 587)
    print("SMTP STARTTLS test passed (Port 587 path triggered)")

if __name__ == "__main__":
    try:
        test_ai_evaluator_dynamic_role()
        test_email_branding()
        print("\nALL BACKEND VERIFICATIONS PASSED!")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
