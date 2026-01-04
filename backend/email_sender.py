import os
import base64
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from gmail_client import get_gmail_service

load_dotenv()

def send_email(to_email: str, decision: str, company_name: str = "DUDE TECH", tagline: str = "Building smart hiring systems", role_name: str = "Software Engineer", use_own_smtp: bool = False, smtp_config: dict = None):
    """
    Sends email using either Gmail API or a custom SMTP server.
    """
    
    # Decisions markers
    is_eligible = decision.startswith("ELIGIBLE")
    
    # Subject Line
    if is_eligible:
        subject = f"🎉 Interview Invitation – {role_name} | {company_name}"
    else:
        subject = f"Application Update – {role_name} | {company_name}"

    # Email Branding
    BRAND_GRADIENT = "linear-gradient(135deg,#667eea,#764ba2)"
    HEADER_BG = BRAND_GRADIENT if is_eligible else "#111827"

    # HTML Body
    if is_eligible:
        meet_link = decision.split("Meet:")[-1].strip() if "Meet:" in decision else "#"
        body_content = f"""
              <p>Hello,</p>
              <p>Thank you for applying for the <strong>{role_name}</strong> position at <strong>{company_name}</strong>.</p>
              <p>After reviewing your resume, we are happy to inform you that your profile has been <strong>shortlisted</strong>.</p>
              <div style="background:#eef2ff;padding:16px;border-radius:10px;margin:20px 0;">
                <p style="margin:0;"><strong>📅 Interview Details</strong></p>
                <p style="margin:8px 0;">Mode: Google Meet</p>
                <p style="margin:8px 0;">Meeting Link:<br/><a href="{meet_link}" style="color:#4f46e5;">{meet_link}</a></p>
              </div>
        """
    else:
        body_content = f"""
              <p>Hello,</p>
              <p>Thank you for your interest in the <strong>{role_name}</strong> position at <strong>{company_name}</strong>.</p>
              <p>After careful review, we will not be moving forward with your application at this time.</p>
        """

    html_body = f"""
    <html>
    <body style="margin:0;background:#f4f6fc;font-family:Arial,sans-serif;">
      <div style="max-width:600px;margin:30px auto;background:#ffffff;
                  border-radius:14px;overflow:hidden;
                  box-shadow:0 15px 40px rgba(0,0,0,0.2)">
        <div style="background:{HEADER_BG};padding:26px;color:white;">
          <h2 style="margin:0;">{company_name}</h2>
          <p style="margin:6px 0 0;font-size:14px;">{tagline}</p>
        </div>
        <div style="padding:26px;color:#1a202c;">
          {body_content}
          <p style="margin-top:28px;">Best regards,<br/><strong>Hiring Team</strong><br/>{company_name}</p>
        </div>
        <div style="background:#f8fafc;padding:14px;text-align:center;font-size:12px;color:#6b7280;">
          © {company_name} · AI-powered recruitment platform
        </div>
      </div>
    </body>
    </html>
    """

    # Create message
    msg = MIMEMultipart("alternative")
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, "html"))

    if use_own_smtp and smtp_config:
        # Use Custom SMTP
        host = smtp_config.get("host")
        port = int(smtp_config.get("port", 465))
        user = smtp_config.get("user")
        password = smtp_config.get("password")
        
        msg['From'] = user
        try:
            context = ssl.create_default_context()
            
            # Port 465 is typically for implicit SSL
            if port == 465:
                with smtplib.SMTP_SSL(host, port, context=context) as server:
                    server.login(user, password)
                    server.sendmail(user, to_email, msg.as_string())
            else:
                # Ports like 25, 587 are for STARTTLS
                with smtplib.SMTP(host, port) as server:
                    server.starttls(context=context)
                    server.login(user, password)
                    server.sendmail(user, to_email, msg.as_string())
            print(f"Email sent via SMTP ({host}:{port})")
        except Exception as e:
            print(f"SMTP Error ({host}:{port}): {e}")
            raise e
    else:
        # Fallback to Gmail API
        msg['From'] = f"{company_name} <me>"
        try:
            service = get_gmail_service()
            raw_string = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            message = service.users().messages().send(userId="me", body={'raw': raw_string}).execute()
            print(f"Email sent via Gmail API! Message Id: {message['id']}")
        except Exception as e:
            print(f"Gmail API Error: {e}")
            raise e
