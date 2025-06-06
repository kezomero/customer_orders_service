# 🛒 Customer Orders Management API

A **Django REST API** for managing customers and orders, featuring **SMS notifications via Africa’s Talking**, **JWT and OIDC authentication via Auth0**, and **auto-generated API documentation**.

---

## ✨ Features

- ✅ Customer CRUD operations
- ✅ Order management with SMS updates
- ✅ Africa's Talking SMS integration
- ✅ JWT + OIDC (Auth0) authentication
- ✅ Swagger/OpenAPI documentation
- ✅ PostgreSQL or MySQL support
- ✅ Unit testing with coverage

---

## 🧰 Prerequisites

- Python 3.9+
- Redis (for sessions or async support)
- A relational DB (PostgreSQL or MySQL)
- [Africa’s Talking sandbox](https://account.africastalking.com/)
- [Auth0 account](https://auth0.com/)

---

## ⚙️ Installation

### 1. Clone the Repo

```bash
git clone https://github.com/kezomero/customer_orders_service.git
cd customer_orders_service
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠️ Environment Setup

Create a `.env` file in the root directory with the following variables:

```ini
DEBUG=True

# DB Config - choose one
DB_ENGINE=django.db.backends.mysql       # or use django.db.backends.postgresql
DB_NAME=customers_orders
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306  # 5432 for PostgreSQL

# Africa's Talking
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_api_key

# Django
DJANGO_SECRET_KEY=your-secret-key

# Auth0 OIDC
OIDC_RP_CLIENT_ID=your-client-id
OIDC_RP_CLIENT_SECRET=your-client-secret
OIDC_DOMAIN=your-auth0-domain
```

---

## 🗃️ Database Setup

### For MySQL:

```bash
mysql -u root -p
CREATE DATABASE customers_orders;
```

### For PostgreSQL:

```bash
psql -U postgres
CREATE DATABASE customers_orders;
```

Run migrations:

```bash
python manage.py migrate
```

---

## 🚀 Running the Server

```bash
python manage.py runserver
```

Visit: [http://localhost:8000/swagger/](http://localhost:8000/swagger/) for API docs and testing

---

## 🔐 Authentication

### OIDC Login (via Auth0):

Visit http://localhost:8000/api/oidc/login/ on web browser for authentication and redirection for tokens which you can then use to authenticate the API this is OIDC for authorization only and not creating customers
Visit http://localhost:8000/api/oidc/logout/ for logging out

## 📲 Africa’s Talking Setup

1. Sign up on [Africa's Talking](https://account.africastalking.com)
2. Use the sandbox credentials in your `.env` file
3. Verify your phone number on https://simulator.africastalking.com/
4. Use their API key and `sandbox` username

---

## 🔐 Auth0 Setup

1. Go to [Auth0 dashboard](https://manage.auth0.com/)
2. Create a new "Regular Web Application"
3. Note your `Client ID`, `Client Secret`, and domain
4. Add callback URLs (http://localhost:8000/api/oidc/callback/) to the settings
5. Use the relevant values in the `.env`

---

## 🧪 Testing

```bash
coverage run manage.py test
coverage report
```

---
