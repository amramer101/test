# RM Platform

A modular, scalable Django platform for resource and user management, featuring authentication, authorization (RBAC), user profiles, gamification (points, levels, badges), and more. Designed for extensibility, security, and modern API-first development.

---

## Table of Contents
- [Project Vision](#project-vision)
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Apps](#apps)
- [Setup](#setup)
- [Example .env](#example-env)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Project Vision

**RM Platform** aims to provide a robust, extensible backend for modern web and mobile applications. It is designed to:
- Enable rapid development of secure, feature-rich platforms
- Support user engagement and growth through gamification
- Be easy to extend, customize, and maintain for teams of all sizes
- Follow best practices for security, code quality, and scalability

---

## Overview

RM Platform is a Django-based backend designed for modern web and mobile applications. It provides robust user management, authentication, authorization, and a gamification system to drive user engagement. The architecture supports clean separation of concerns, easy extension, and best practices for security and maintainability.

---

## Architecture

- **Modular apps** for each domain (authentication, users, authorization, gamification, etc.)
- **API-first**: RESTful endpoints with versioning (`/api/v1/`)
- **RBAC**: Role-based access control for fine-grained permissions
- **Gamification**: Points, levels, badges, and activity logs
- **Shared utilities**: Common models, permissions, exceptions, validators, and signals
- **Custom middleware**: Security, logging, and rate limiting
- **Environment-based settings** for dev, prod, and testing
- **12-factor app principles**: Configuration via environment variables, statelessness, and portability

---

## Features
- User registration, login, password reset, and profile management
- JWT authentication and session management
- Role and permission management (RBAC)
- Audit logging and soft delete for models
- Gamification: points, levels, badges, and progress bar
- Admin management for all core models
- API endpoints for all major features
- Extensible shared utilities and signals
- Customizable permissions and validators
- Easy integration with frontend frameworks (React, Vue, etc.)

---

## Project Structure

```
RM_Platform/
├── apps/
│   ├── authentication/   # Auth logic (JWT, registration, login)
│   ├── authorization/    # RBAC: roles, permissions, assignments
│   ├── users/            # User profiles, preferences, search
│   ├── gamification/     # Points, levels, badges, activity log
│   └── shared/           # Base models, permissions, exceptions, utils
├── api/                  # API versioning and routing
├── config/               # Django settings, URLs, WSGI/ASGI
├── core/                 # Core domain logic
├── middleware/           # Custom middleware
├── infrastructure/       # Email, cache, storage, database config
├── templates/            # Email and other templates
├── requirements/         # Environment-specific requirements
├── manage.py             # Django management script
└── README.md             # Project documentation
```

---

## Apps

### **authentication**
Handles all aspects of user authentication:
- User registration, login, logout, and password reset
- JWT-based authentication for secure, stateless sessions
- Email verification and password reset flows
- API endpoints for all authentication actions

### **authorization**
Implements Role-Based Access Control (RBAC):
- Define roles (e.g., admin, user, moderator)
- Assign permissions to roles and users
- Enforce permissions at the API and model level
- Services for permission checks and role management

### **users**
Manages user profiles and preferences:
- UserProfile model extends the user with phone, picture, preferences
- Endpoints for profile update, search, and "me" endpoint
- Admin and API access to user data

### **gamification**
Drives user engagement through points, levels, and badges:
- Award points for actions (registration, login, etc.)
- Track user levels, progress, badges, and activity log
- Admin endpoints for awarding points/badges and managing levels/badges
- Automatic point and badge awarding via signals
- See [`apps/gamification/README.md`](apps/gamification/README.md) for details

### **shared**
Provides cross-cutting utilities and base classes:
- Abstract base models (UUID, timestamps, audit, soft delete)
- Shared permissions, exceptions, validators, pagination, utils, signals, constants, enums
- Central place for reusable logic and DRY code

---

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd RM_Platform
   ```
2. **Create a PostgreSQL database and user:**
   - Start PostgreSQL if not already running.
   - Enter the PostgreSQL shell:
     ```bash
     sudo -u postgres psql
     ```
   - Create a database and user (replace `rm_platform` and `password` as needed):
     ```sql
     CREATE DATABASE rm_platform;
     CREATE USER rm_platform_user WITH PASSWORD 'password';
     GRANT ALL PRIVILEGES ON DATABASE rm_platform TO rm_platform_user;
     \q
     ```
   - Update your `.env` or settings with these credentials.
3. **Create a virtual environment and install requirements:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and set your secrets and DB config.
5. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
8. **Access the admin:**
   - Visit `http://localhost:8000/admin/` to manage users, roles, badges, etc.

---

## Example .env

```
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=rm_platform
DB_USER=rm_platform_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Email (example)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
```

---

## API Overview

- All endpoints are under `/api/v1/`
- JWT authentication is required for most endpoints
- See each app's `urls.py` and DRF schema for details

**Key Endpoints:**
- `/api/v1/authentication/` — Register, login, logout, password reset
- `/api/v1/users/` — Profile, update, search, preferences
- `/api/v1/authorization/` — Roles, permissions, assignments
- `/api/v1/gamification/` — Points, levels, badges, activity log

### Example: Register a User
```http
POST /api/v1/authentication/register/
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "YourPassword123!"
}
```

### Example: Get User Profile (Authenticated)
```http
GET /api/v1/users/me/
Authorization: Bearer <your-jwt-token>
```

---

## Testing

- Run all tests:
  ```bash
  python manage.py test
  ```
- Add your own tests in each app's `tests/` directory
- Use tools like `pytest`, `pytest-django`, `coverage` for advanced testing

---

## Troubleshooting

- **Django Debug Toolbar error during tests:**
  - The debug toolbar should not be installed when `DEBUG=False` (as in tests). Remove it from `INSTALLED_APPS` or conditionally include it only when not testing.
- **Static files warning:**
  - If you see a warning about `STATICFILES_DIRS`, ensure the referenced directory exists or update your settings.
- **Database connection issues:**
  - Double-check your `.env` and PostgreSQL setup. Ensure the DB is running and credentials are correct.
- **Migrations not applying:**
  - Run `python manage.py makemigrations` and `python manage.py migrate`.
- **No tests found:**
  - Ensure your test files are named `test_*.py` and are in the correct `tests/` directories.

---

## Contributing

1. Fork the repo and create a feature branch
2. Write clear, well-documented code and tests
3. Run tests and ensure code quality (use `flake8`, `black`, etc.)
4. Submit a pull request with a clear description

**Code Style:**
- Follow PEP8 and Django best practices
- Use docstrings and comments for clarity
- Keep code DRY and modular

---

## License

This project is licensed under the MIT License. See `LICENSE` for details. 