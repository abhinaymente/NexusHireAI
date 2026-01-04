# 🚀 Comprehensive Deployment Guide

To make your project live and ready for interviews, follow these steps to host both your **Backend (API)** and **Frontend (UI)**.

---

## Part 1: Host the Backend (FastAPI)
We recommend using **Render** (it's free and easy).

1.  **Push to GitHub**: Create a repository and push your `backend/` folder.
2.  **Create a New Web Service**:
    *   Log in to [Render.com](https://render.com).
    *   Click **New +** > **Web Service**.
    *   Select your repository.
3.  **Configure Service**:
    *   **Name**: `hire-ai-backend`
    *   **Root Directory**: `backend`
    *   **Environment**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  **Add Environment Variables**:
    *   Go to the **Environment** tab in Render.
    *   Add everything from your locally working `.env` file:
        *   `GROQ_API_KEY`: (Your Key)
        *   `GOOGLE_CREDENTIALS`: (The Base64 string)
        *   `SECRET_KEY`: (Any long random string of your choice for security)
        *   `GMAIL_TOKEN`: (The Base64 string - optional if using SMTP)
5.  **Copy the URL**: Once deployed, Render will give you a URL (e.g., `https://hire-ai-backend.onrender.com`).

---

## Part 2: Connect and Host the Frontend
We recommend **Netlify** or **Vercel**.

1.  **Update the API URL**:
    *   Open `frontend/config.js`.
    *   Change the `API_URL` to your **newly created Render URL** from Part 1.
    *   Save the file.
2.  **Deploy**:
    *   Drag and drop your `frontend/` folder into the Netlify "Drop" area, OR
    *   Connect it to your GitHub repo (select the `frontend/` folder as the root).
3.  **Public Link**: Netlify will give you a public URL (e.g., `https://hire-ai-screener.netlify.app`).

---

## 💡 Important Interview Tips for Deployment

-   **Cold Starts**: Explain to the interviewer that free services like Render "sleep" after inactivity. *"When you first open the site, it might take 30 seconds to wake up the backend—that is a limitation of the free hosting tier, but the architecture itself is designed for 24/7 production scaling."*
-   **Static Hosting**: Mention that the frontend is a **Static Web App**, making it extremely fast to load across the world via CDNs (Content Delivery Networks).
-   **Persistence**: Note that while SQLite is great for demos, in a massive enterprise setup, you would replace it with **Render's Managed PostgreSQL** (which stays the same in your code because of SQLAlchemy!).

---

**Your project is now officially globally accessible! 🌍🚀**
