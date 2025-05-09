# 🔐 Authentication System (FastAPI + Google OAuth2)

A production-ready authentication system built with **FastAPI**, supporting both **email/password** and **Google Sign-In**. This system ensures secure, scalable, and maintainable authentication workflows for modern applications.

---

## 🚀 Features

### Email/Password Authentication
- ✅ User registration with name, email, and secure password.
- ✅ Enforced password complexity (8+ characters, 1 uppercase, 1 number, 1 special character).
- ✅ Email verification with time-limited OTP.
- ✅ Prevention of duplicate email registration.

### Google Sign-In
- ✅ OAuth 2.0 integration with Google accounts.
- ✅ Auto-link Google emails with existing accounts.
- ✅ Support for both sign-up and login flows.

### Session Management
- ✅ JWT-based access tokens.

### Password Reset
- ✅ Reset-password flow via email-based OTP.
- ✅ Time-limited, secure OTP verification.
- ✅ Password update post OTP verification.

### Profile Management
- ✅ Get and update user profile info.
- ✅ Handle profile picture and display name updates.

---

## 🧱 Tech Stack

| Layer        | Technology             |
|--------------|-------------------------|
| Backend      | FastAPI                 |
| Auth         | OAuth2 + JWT            |
| Database     | PostgreSQL + SQLAlchemy |
| ORM          | SQLAlchemy (async)      |
| Email        | Mock (for development)  |

---

## 📁 Project Structure

```
Authentication/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       │   ├── endpoints.py
│   │       │   ├── schema.py
│   │       │   ├── service.py
│   │       │   └── repository.py
│   │       └── user/
│   │           ├── endpoints.py
│   │           ├── schema.py
│   │           ├── service.py
│   │           └── repository.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── google_oauth.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── migrations/
|   |   |   ├── versions/
│   │   |   ├── alembic.ini
│   │   |   ├── env.py
│   │   |   └── script.py.mako
│   │   └── models/
│   │       ├── user.py
│   │       ├── otp.py
│   │       └── blacklisted_token.py
│   ├── services/
│   │   └── mock_email_service.py
│   ├── utils/
│   │   ├── hashing.py
│   │   └── otp.py
│   └── main.py
├── profile_pictures/                # Stores uploaded profile images
├── .gitignore 
├── .env                      
├── README.md                        
├── requirements.txt                 # Python package dependencies
└── myvenv/                          # Virtual environment (should be in .gitignore)

```

---

## 🔑 API Endpoints
### 🔐 Authentication APIs

| Method | Path                              | Description                                       |
|--------|-----------------------------------|---------------------------------------------------|
| POST   | `/auth/register`                  | Register with email, name, and password           |
| POST   | `/auth/login`                     | Login with email and password                     |
| POST   | `/auth/logout`                    | Invalidate the current JWT access token           |
| POST   | `/auth/resend-verification-otp`   | Resend email verification OTP                     |
| POST   | `/auth/verify-email`              | Verify OTP and activate account                   |
| POST   | `/auth/request-password-reset`    | Send password reset OTP                           |
| POST   | `/auth/reset-password`            | Reset password via OTP                            |

---

### 🌐 Google OAuth2 APIs

| Method | Path                              | Description                                       |
|--------|-----------------------------------|---------------------------------------------------|
| GET    | `/api/v1/auth/google-login`       | Redirect to Google OAuth Sign-In                  |
| GET    | `/api/v1/auth/google-callback`    | Handle Google OAuth callback and log in           |

---

### 👤 User Profile APIs

| Method | Path                              | Description                                       |
|--------|-----------------------------------|---------------------------------------------------|
| GET    | `/user/profile`                   | Fetch current user's profile                      |
| PATCH  | `/user/profile`                   | Update profile info (name or profile picture)     |

---

## ⚙️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/khanduja-kunal/Authentication
cd Authentication
```

### 2. Create `.env`
```ini
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/auth_db
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/auth_db
SECRET_KEY=your_super_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
OTP_LIFETIME_MINUTES=10
RESEND_COOLDOWN_SECONDS=60
MAIL_SENDER=support@system.com
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
alembic -c app/db/migrations/alembic.ini upgrade head
```

### 5. Start the server
```bash
uvicorn app.main:app --reload
```
## 📄 License

MIT License ©

---

## 🙋‍♂️ Contributions Welcome

Pull requests, feedback, and issues are always welcome. Let's improve authentication together!
