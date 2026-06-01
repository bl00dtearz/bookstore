# Bookstore API

Online bookstore backend — SDF Final Project  
**Stack:** FastAPI · PostgreSQL · SQLAlchemy · Alembic · Docker

---

## Quick start (Docker — recommended)

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd bookstore

# 2. Copy environment config
cp .env.example .env

# 3. Start everything (app + DB + mock payment service)
docker-compose up --build

# App is now live at http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

The first boot automatically runs migrations and seeds the database with test data.

**Test accounts:**
| Role     | Email                   | Password   |
|----------|-------------------------|------------|
| Admin    | admin@bookstore.com     | admin1234  |
| Customer | alice@example.com       | alice1234  |

---

## Local development (without Docker)

**Requirements:** Python 3.11+, PostgreSQL 14+

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL

# Run migrations
alembic upgrade head

# Seed the database
python scripts/seed.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

---

## Running tests

```bash
# All tests with coverage report
pytest

# Quick run without coverage
pytest --no-cov -v

# Single test file
pytest tests/test_auth.py -v
```

Coverage report is generated in `htmlcov/index.html`.

---

## API overview

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### Auth

| Method | Endpoint         | Auth     | Description            |
|--------|------------------|----------|------------------------|
| POST   | /auth/register   | None     | Register a new user    |
| POST   | /auth/login      | None     | Login, get JWT token   |
| GET    | /auth/me         | Bearer   | Get current user info  |

### Books

| Method | Endpoint             | Auth     | Description                              |
|--------|----------------------|----------|------------------------------------------|
| GET    | /books               | None     | List books (search, filter, pagination)  |
| GET    | /books/{id}          | None     | Get single book with avg rating          |
| POST   | /books               | Admin    | Create a book                            |
| PUT    | /books/{id}          | Admin    | Update a book                            |
| DELETE | /books/{id}          | Admin    | Delete a book                            |
| GET    | /books/authors       | None     | List all authors                         |
| POST   | /books/authors       | Admin    | Create an author                         |
| GET    | /books/genres        | None     | List all genres                          |
| POST   | /books/genres        | Admin    | Create a genre                           |

**Book search parameters:** `?search=dune&genre_id=1&author_id=2&min_price=5&max_price=20&skip=0&limit=20`

### Cart

| Method | Endpoint              | Auth     | Description            |
|--------|-----------------------|----------|------------------------|
| GET    | /cart                 | Bearer   | View cart              |
| POST   | /cart/items           | Bearer   | Add item to cart       |
| PUT    | /cart/items/{id}      | Bearer   | Update item quantity   |
| DELETE | /cart/items/{id}      | Bearer   | Remove item from cart  |
| DELETE | /cart                 | Bearer   | Clear cart             |

### Orders

| Method | Endpoint                   | Auth     | Description              |
|--------|----------------------------|----------|--------------------------|
| POST   | /orders                    | Bearer   | Place order from cart    |
| GET    | /orders                    | Bearer   | List my orders           |
| GET    | /orders/{id}               | Bearer   | Get order details        |
| PUT    | /orders/{id}/status        | Admin    | Update order status      |

### Reviews

| Method | Endpoint                        | Auth     | Description             |
|--------|---------------------------------|----------|-------------------------|
| GET    | /books/{id}/reviews             | None     | List book reviews       |
| POST   | /books/{id}/reviews             | Bearer   | Add a review (1x/book)  |
| DELETE | /books/{id}/reviews/{review_id} | Bearer   | Delete your review      |

---

## Example requests (curl)

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com", "password": "john1234"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "john1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Browse books
curl http://localhost:8000/books?search=dune

# Add to cart
curl -X POST http://localhost:8000/cart/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "quantity": 2}'

# Place order
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address": "123 Main St, Almaty"}'
```

---

## Architecture

```
Client (Postman/browser)
    ↓
FastAPI (port 8000) — JWT auth, request logging, OpenAPI docs
    ↓
Service layer — business logic (search, order, reviews)
    ↓
SQLAlchemy ORM ← Alembic migrations
    ↓
PostgreSQL (port 5432)

Mock payment service (port 8001) — simulates payment gateway
```

**Design patterns used:** Repository pattern, Dependency Injection (FastAPI `Depends`), MVC-like separation (routers / services / models)

---

## Security measures

- Passwords hashed with bcrypt (salt rounds = 12)
- JWT tokens with expiry (default: 60 min)
- Role-based access control (customer vs admin)
- Input validation via Pydantic (type checking, constraints)
- SQL injection prevention via SQLAlchemy ORM (parameterized queries)
- Environment variables for all secrets (never hardcoded)
- Stock validation before order placement

---

## Team

| Member   | Responsibility                                      |
|----------|-----------------------------------------------------|
| Partner 1 | Backend (models, auth, books, Docker)              |
| Partner 2 | Backend (orders, reviews, tests, seed data)        |
