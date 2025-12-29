# Online-store (Prototype)

---

## 🚀 Getting Started

These instructions will help you set up the project locally for development

---

## 📦 Prerequisites

Make sure you have the following installed:

- **Python 3.10+** (or your preferred version)
- **pip**
- **Docker Desktop**
  Download here: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- **Docker Compose** (included with Docker Desktop)

---

## 🛠 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/prakashtaz0091/online-store/
cd online-store
```

---

### 2️⃣ Create and activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

1. Rename the example environment file from `.env.example` to `.env`

2. Open `.env` and **set your own values** (database credentials, Django secret key, etc.).

---

### 🔐 Generate a Django Secret Key

Run the following command to generate a secure Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it into your `.env` file as:

```env
DJANGO_SECRET=your_generated_secret_key
```

---

## 🐘 PostgreSQL with Docker

This project uses **PostgreSQL** via Docker for local development.

### Start PostgreSQL locally

Make sure Docker Desktop is running, then execute, in the project directory in a terminal:

```bash
docker compose up
```

This will:

- Start a PostgreSQL container
- Expose the database to your Django application
- Use credentials defined in your `.env` file

- Keep defaults to connect to the running PostgreSQL container.

```python
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

To stop the containers:

```bash
docker compose down
```

---

## 🧩 Database Setup

After PostgreSQL is running:

```bash
python manage.py migrate
```

(Optional) Create a superuser:

```bash
python manage.py createsuperuser
```

---

## ▶️ Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000/
```

---

## 📝 Notes

- Always keep `.env` files **out of version control**, e.g., inside `.gitignore` keep `.env`
- Ensure Docker Desktop is running before starting PostgreSQL
- Use strong, unique values for secrets in production

---
