# 🧠 JobBoard — Modern Django + Elasticsearch Job Portal

A full-featured **Job Board Platform** built with **Django REST Framework**, **Elasticsearch**, **Redis caching**, **Celery**, and **JWT Authentication**.  
Supports recruiters posting jobs, applicants applying & saving jobs, full-text search with typo tolerance + autocomplete, email notifications, and more.

---

## 🚀 Features

### 🔍 Job Search
- Full-text & fuzzy search with **Elasticsearch**
- Handles **typos** and **misspellings**
- **Autocomplete** suggestions (e.g., typing `devop` → suggests `DevOps Engineer`)
- Per-query **Redis caching** for performance

### 💼 Job Management
- Recruiters can create/update jobs
- Admins approve or reject jobs
- Applicants browse only approved listings
- Filter by location, salary, job type, experience level

### 🧾 Applications
- Applicants can apply for jobs with **resume upload**
- Recruiters receive notifications (via Celery task/email)
- Application statuses: `sent`, `viewed`, `shortlisted`, `rejected`

### ❤️ Saved Jobs
- Applicants can save/unsave jobs
- Prevents duplicate saves

### ✉️ Email System
- Registration verification emails
- Password reset flow
- Celery async email tasks

### 🔐 Authentication
- JWT-based login (SimpleJWT)
- Registration + email verification
- Password reset + confirmation

### ⚙️ Architecture
- PostgreSQL + Redis + Elasticsearch stack
- Dockerized for easy setup
- CI-friendly with Pytest + Django test suite

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend Framework | Django 5 + Django REST Framework |
| Database | PostgreSQL 15 |
| Search Engine | Elasticsearch 8 |
| Message Broker / Cache | Redis 7 |
| Task Queue | Celery 5 |
| Auth | JWT (djangorestframework-simplejwt) |
| Media Uploads | Django File/Image Fields |
| Frontend Ready | CORS-enabled REST API |
| Containerization | Docker + docker-compose |

---

## 🐳 Quickstart (via Docker)

```bash
# 1️⃣ Clone the repo
git clone https://github.com/<your-username>/JobBoard.git
cd JobBoard

# 2️⃣ Build and start all services
make up   # or docker-compose up --build

# 3️⃣ Run migrations & create superuser
make migrate
docker-compose exec web python manage.py createsuperuser

# 4️⃣ Run tests
make test

# App runs at http://localhost:8000
```
--- 

### Default services
| Service | URL / Port |
|----------|------------|
| 🐍 Django API | [http://localhost:8000](http://localhost:8000) |
| 🐘 PostgreSQL | `localhost:5432` |
| 🔁 Redis | `localhost:6379` |
| 🔎 Elasticsearch | [http://localhost:9200](http://localhost:9200`) |

---

## 🧰 Developer Commands

| Command | Description |
|----------|-------------|
| `make up` | Start Docker containers |
| `make down` | Stop containers |
| `make bash` | Open bash shell in web container |
| `make migrate` | Run Django migrations |
| `make test` | Run the pytest suite |