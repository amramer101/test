# RM Platform API Documentation

This document provides an overview of all API endpoints available in the RM Platform, organized by version and domain. The API follows RESTful principles and is versioned under `/api/v1/`.

---

## Table of Contents
- [Authentication](#authentication)
- [Users](#users)
- [Authorization](#authorization)
- [Gamification](#gamification)
- [Courses](#courses)
- [Shop](#shop)
- [Social](#social)

---

## Authentication
**Base Path:** `/api/v1/auth/`

| Endpoint                | Method | Description                |
|------------------------|--------|----------------------------|
| `/register/`           | POST   | Register a new user        |
| `/login/`              | POST   | Login with credentials     |
| `/logout/`             | POST   | Logout current user        |
| `/password-reset/`     | POST   | Request password reset     |
| `/profile/`            | GET    | Get user profile           |
| `/jwt/login/`          | POST   | Obtain JWT token           |
| `/jwt/refresh/`        | POST   | Refresh JWT token          |

---

## Users
**Base Path:** `/api/v1/users/`

| Endpoint | Method | Description         |
|----------|--------|---------------------|
| `/`      | GET    | List users          |
| `/`      | POST   | Create a new user   |
| `/<id>/` | GET    | Retrieve user       |
| `/<id>/` | PUT    | Update user         |
| `/<id>/` | PATCH  | Partial update user |
| `/<id>/` | DELETE | Delete user         |

---

## Authorization
**Base Path:** `/api/v1/authorization/`

| Endpoint         | Method | Description                |
|------------------|--------|----------------------------|
| `/roles/`        | CRUD   | Manage roles               |
| `/permissions/`  | CRUD   | Manage permissions         |
| `/user-roles/`   | CRUD   | Assign roles to users      |

---

## Gamification
**Base Path:** `/api/v1/gamification/`

| Endpoint           | Method | Description                  |
|--------------------|--------|------------------------------|
| `/profile/`        | CRUD   | User point profile           |
| `/leaderboard/`    | CRUD   | Leaderboard                  |
| `/streaks/`        | CRUD   | User streaks                 |
| `/quests/`         | CRUD   | Quests                       |
| `/challenges/`     | CRUD   | Challenges                   |
| `/events/`         | CRUD   | Gamification events          |
| `/achievements/`   | CRUD   | User achievements            |

---

## Courses
**Base Path:** `/api/v1/courses/`

| Endpoint                        | Method | Description                        |
|---------------------------------|--------|------------------------------------|
| `/categories/`                  | CRUD   | Manage course categories           |
| `/courses/`                     | CRUD   | Manage courses                     |
| `/courses/<course_id>/sections/`| CRUD   | Manage sections in a course        |
| `/sections/<section_id>/lessons/`| CRUD  | Manage lessons in a section        |
| `/enrollments/`                 | CRUD   | Manage enrollments                 |
| `/reviews/`                     | CRUD   | Manage course reviews              |

---

## Shop
**Base Path:** `/api/v1/shop/`

| Endpoint         | Method | Description                |
|------------------|--------|----------------------------|
| `/categories/`   | CRUD   | Manage shop categories     |
| `/items/`        | CRUD   | Manage shop items          |
| `/purchases/`    | CRUD   | Manage purchases           |
| `/inventory/`    | CRUD   | User inventory             |

---

## Social
**Base Path:** `/api/v1/social/`

| Endpoint                | Method | Description                |
|-------------------------|--------|----------------------------|
| `/comments/`            | CRUD   | Manage comments            |
| `/likes/`               | CRUD   | Manage likes               |
| `/shares/`              | CRUD   | Manage shares              |
| `/discussions/`         | CRUD   | Manage discussions         |
| `/discussion-replies/`  | CRUD   | Manage discussion replies  |
| `/referrals/`           | CRUD   | Manage referrals           |
| `/following/`           | CRUD   | Manage user following      |
| `/feed/`                | CRUD   | Activity feed              |

---

## API Versioning
- All endpoints are versioned under `/api/v1/`.
- Future versions will be available under `/api/v2/`, etc.

## Notes
- All endpoints follow RESTful conventions.
- JWT authentication is used for protected endpoints.
- For detailed request/response schemas, see the OpenAPI/Swagger docs at `/api/docs/`.
