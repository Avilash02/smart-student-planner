# 📘 Smart Student Planner

A modern, production-ready Django web application for students to manage tasks, exams, and daily study schedules with built-in Google OAuth 2.0 Single Sign-On and username/password authentication.

🚀 **Live Deployment:** [https://smart-student-planner-n42l.onrender.com/](https://smart-student-planner-n42l.onrender.com/)

---

## 🌟 Key Features

| Feature | Description |
|---|---|
|  **Dual Authentication** | Seamless 1-click Google Sign-In (OAuth 2.0) or standard Username/Email & Password |
|  **Task Management** | Full CRUD, priority sorting (High/Medium/Low), and one-click completion toggle |
|  **Smart Highlighting** | Real-time indicators for overdue tasks, due today, and due tomorrow |
|  **Exam Tracker** | Countdown badges (Today!, Tomorrow, X days remaining) and upcoming/past separation |
|  **Study Planner** | Daily scheduled study sessions with duration tracking and completion checkoffs |
|  **Dynamic Dashboard** | Live stats, animated progress bar, and smart next-task recommendations |
|  **Security & Isolation** | Strict per-student data ownership; users cannot view or edit others' data |
|  **Production-Ready** | Deployed on Render with WhiteNoise static files and PostgreSQL support |

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Clone the repository & create a virtual environment
```bash
git clone https://github.com/Avilash02/smart-student-planner.git
cd smart-student-planner
python -m venv venv
```
Activate the virtual environment:
* **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
* **Windows (CMD):** `.\venv\Scripts\activate.bat`
* **macOS / Linux:** `source venv/bin/activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your local `.env` file
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
*(On Windows CMD: `copy .env.example .env`)*

In your `.env` file:
* Set `DJANGO_DEBUG=True`
* Set `SECRET_KEY=your-local-dev-secret-key`
* Leave `DATABASE_URL` blank to automatically use local SQLite (`db.sqlite3`)
* Fill in your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (if testing Google Sign-In)

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Start the local development server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser.

---

## 🧪 Running Automated Tests

Run the full automated test suite (38 tests covering authentication, Google OAuth compatibility, student record isolation, task/exam/study CRUD, and dashboard calculations):

```bash
python manage.py test
```

---

## 🚀 Production Deployment on Render

### Step 1: Create a Hosted PostgreSQL Database on Neon (Optional)
1. Go to [Neon Console](https://console.neon.tech/) and create a free account.
2. Click **Create Project** (e.g. `student-planner-db`).
3. Under your project dashboard, find the **Connection Details** box.
4. Copy the connection string (ensure `Pooled connection` is selected and `sslmode=require` is present). It looks like:
   ```text
   postgresql://user:password@ep-sample-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Configure Web Service on Render
* **Name**: `smart-student-planner`
* **Runtime**: `Python 3`
* **Build Command**: `./build.sh`
* **Start Command**: `gunicorn smart_student_planner.wsgi:application`
* **Environment Variables**:
  * `SECRET_KEY`: *(Auto-generated random key)*
  * `DJANGO_DEBUG`: `False`
  * `DATABASE_URL`: *(Your Neon PostgreSQL connection string)*
  * `GOOGLE_CLIENT_ID`: *(Your Google OAuth Client ID)*
  * `GOOGLE_CLIENT_SECRET`: *(Your Google OAuth Client Secret)*
  * `SECURE_SSL_REDIRECT`: `True`
  * `PYTHON_VERSION`: `3.12.8`

### Step 3: Add Render Callback URL to Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/) $\rightarrow$ **APIs & Services $\rightarrow$ Credentials**.
2. Open your OAuth 2.0 Client ID.
3. Under **Authorized redirect URIs**, click **+ ADD URI** and add:
   ```text
   https://smart-student-planner-n42l.onrender.com/accounts/google/login/callback/
   ```
4. Click **Save**.

---

## 🔒 Security Practices Implemented

* **Strict Secret Separation**: No hardcoded secrets, keys, or credentials in source code. All configuration is loaded from environment variables via `python-dotenv`.
* **Zero Wildcard Hosts**: `ALLOWED_HOSTS` uses explicit domain lists and automatically validates Render hostnames.
* **HTTPS & Reverse Proxy Protection**: `SECURE_PROXY_SSL_HEADER` configured to prevent redirect loops behind Render's reverse proxy.
* **Secure Cookie Transmission**: `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` enabled in production.
* **HTTP Strict Transport Security (HSTS)**: Automatic SSL redirect and HSTS preload headers enabled when `DEBUG=False`.
* **WhiteNoise Static Delivery**: High-performance, compressed static asset delivery with zero external storage requirements.
