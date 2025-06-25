# RM Platform Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL
- Redis (optional, for caching/token blacklisting)
- pip, virtualenv

## 1. Clone the Repository
```
git clone <repo-url>
cd RM_Platform
```

## 2. Environment Variables
Copy `.env.example` to `.env` and fill in all required values:
```
cp .env.example .env
```

## 3. Install Dependencies
```
pip install -r requirements.txt
```

## 4. Database Setup
- Create the PostgreSQL database and user as specified in `.env`.
- Run migrations:
```
python manage.py migrate
```

## 5. Collect Static Files
```
python manage.py collectstatic
```

## 6. Create Logging Directory
Ensure the `logs/` directory exists and is writable by the application.

## 7. Run the Application
```
python manage.py runserver 0.0.0.0:8000
```

## 8. Security & Production
- Set `DJANGO_DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` and `ALLOWED_IPS`.
- Use a secure `DJANGO_SECRET_KEY` and `JWT_SECRET`.
- Set up HTTPS and secure proxy headers.
- Configure email backend for password reset/verification.

## 9. Additional Notes
- For production, use a WSGI server (gunicorn/uwsgi) and a reverse proxy (nginx).
- Set up regular backups for the database.
- Monitor logs and configure log rotation.
- Review and update environment variables as needed.

## 10. Troubleshooting
- Check logs in the `logs/` directory for errors.
- Ensure all environment variables are set.
- Verify database and cache connectivity.

---
For more details, see `docs/ARCHITECTURE.md` and the project README.
