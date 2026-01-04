import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ✅ Get API key from environment (Render-compatible)
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=API_KEY)


def check_resume(resume_text: str, role_name: str = "Software Engineer", requirements: str = "Programming skills AND CS/IT education") -> str:
    prompt = f"""
You are an ATS resume screening system.

Evaluate the resume below for the position: {role_name}

Job Requirements:
{requirements}

Rules:
- If the candidate meets the core job requirements → ELIGIBLE
- Otherwise → NOT ELIGIBLE

Respond with ONLY one word:
ELIGIBLE or NOT ELIGIBLE

Resume:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": f"You are a strict technical recruiter evaluating for a {role_name} role."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()
