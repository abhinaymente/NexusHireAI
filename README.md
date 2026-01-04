# 🚀 NexusHire AI | Enterprise Resume Screener

NexusHire AI is a professional, full-stack recruitment automation platform that uses Generative AI to screen hundreds of resumes in seconds. Built with a focus on **security, multi-tenancy, and whitelabeling**, it allows recruiters to automate the entire screening-to-outreach pipeline.

## 🔗 Live Demo
- **Frontend (Vercel)**: [https://nexus-hire-ai.vercel.app/](https://nexus-hire-ai.vercel.app/)
- **Backend (Render)**: [https://nexushireai.onrender.com](https://nexushireai.onrender.com)

---

## 🌟 Key Features
- **🤖 LLM-Powered Evaluation**: Integration with **Groq (Llama 3.1)** for precise, requirement-based resume screening.
- **🔐 Enterprise Security**: Secure **JWT-based authentication** with PBKDF2 password hashing.
- **🏢 Multi-Tenancy**: Strict data isolation—recruiters only see their own screening batches and results.
- **🎨 Custom Whitelabeling**: Branding support for company names, taglines, and personalized email templates.
- **📧 SMTP Automation**: Dual-mode support for **Implicit SSL** and **STARTTLS**, allowing recruiters to use their own corporate email domains.
- **💾 Persistent History**: Full database integration with **SQLAlchemy** for historical batch tracking.
- **📈 Professional Dashboard**: Real-time progress tracking, analytics, and one-click **CSV export**.

---

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy (ORM), Jose (JWT), Passlib.
- **AI/LLM**: Groq Cloud API.
- **Frontend**: Modern Vanilla JS, CSS3 (Glassmorphism), HTML5.
- **Infrastructure**: Render (Service), Vercel (Client), SQLite (Database).

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/abhinaymente/NexusHireAI.git
cd NexusHireAI
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
GROQ_API_KEY=your_key
SECRET_KEY=your_random_secret
GOOGLE_CREDENTIALS=base64_encoded_json
GMAIL_TOKEN=base64_encoded_json
```

---

## 👤 Author
**Abhinay Mente**  
Computer Science Engineering Student  

- Focused on **Backend Engineering** and **AI Automation**.
- Passionate about building scalable, secure, and user-centric systems.

📌 *This project demonstrates the integration of LLMs with enterprise-grade features like JWT auth and multi-tenancy to solve real-world recruitment challenges.*
