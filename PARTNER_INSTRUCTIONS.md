# 📘 Инструкция для партнёра — Bookstore Project

> Привет! Этот документ — твоя полная инструкция по работе над проектом.
> Стек: Python + FastAPI + PostgreSQL + Docker

---

## 1. Что уже сделано (партнёр 1)

| Модуль | Файл(ы) | Что делает |
|---|---|---|
| Конфиг | `app/config.py`, `.env.example` | Переменные окружения |
| БД | `app/database.py` | SQLAlchemy подключение |
| Модели | `app/models/` | Все таблицы БД |
| Схемы | `app/schemas/` | Pydantic валидация |
| Auth | `app/routers/auth.py` | Регистрация / логин |
| Книги | `app/routers/books.py` | CRUD книг, авторов, жанров |
| Миграции | `alembic/` | Схема БД |
| Docker | `Dockerfile`, `docker-compose.yml` | Запуск всего стека |

---

## 2. Что делаешь ты (партнёр 2)

Твои задачи — корзина, заказы, отзывы и тесты. Весь нужный код уже есть в репо, твоя задача — **понять его, дописать** если нужно, **покрыть тестами** и добавить **ревью через Pull Request**.

### Твои файлы:
```
app/routers/cart.py       ← корзина (уже написан, изучи и расширь)
app/routers/orders.py     ← заказы (уже написан, изучи и расширь)
app/routers/reviews.py    ← отзывы (уже написан, изучи и расширь)
tests/test_orders.py      ← твои тесты (дополни)
tests/test_reviews.py     ← напиши сам (см. раздел 5)
scripts/seed.py           ← данные для БД (можешь добавить своих данных)
```

---

## 3. Настройка окружения

### Шаг 1 — Клонируй репозиторий

```bash
git clone https://github.com/<ваш-репо>/bookstore.git
cd bookstore
```

### Шаг 2 — Создай виртуальное окружение

**В PyCharm:**
- File → Settings → Project → Python Interpreter
- Нажми шестерёнку → Add → Virtualenv Environment → OK
- PyCharm сам предложит установить зависимости из `requirements.txt`

**Или вручную в терминале:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Шаг 3 — Настрой `.env`

```bash
cp .env.example .env
```

Открой `.env` и при необходимости измени `DATABASE_URL` под свою локальную PostgreSQL:
```
DATABASE_URL=postgresql://bookstore_user:bookstore_pass@localhost:5432/bookstore_db
```

### Шаг 4 — Запусти через Docker (самый простой способ)

```bash
docker-compose up --build
```

Всё поднимается автоматически: PostgreSQL + приложение + мок оплаты.

Приложение: http://localhost:8000  
Swagger: http://localhost:8000/docs

---

## 4. Работа через Git — это важно для оценки!

Комиссия смотрит **историю коммитов** — они должны быть от обоих участников.

### Workflow:

```bash
# 1. Перед началом работы — получи последние изменения
git pull origin main

# 2. Создай свою ветку для каждой задачи
git checkout -b feature/reviews-endpoint

# 3. Работай, делай коммиты часто (каждые 30-60 мин)
git add .
git commit -m "feat: add review creation endpoint with rating validation"

# 4. Ещё коммиты по ходу работы
git commit -m "test: add integration tests for reviews"
git commit -m "fix: prevent duplicate review from same user"

# 5. Отправь ветку на GitHub
git push origin feature/reviews-endpoint

# 6. На GitHub создай Pull Request → попроси партнёра сделать ревью
# Партнёр оставляет минимум 1-2 комментария, потом нажимает Merge
```

### Правила коммитов (соблюдай формат):
```
feat: добавил новый функционал
fix: исправил баг
test: добавил тесты
docs: обновил документацию
refactor: переработал код без изменения функционала
```

### Минимальный план веток:
| Ветка | Кто делает | Что |
|---|---|---|
| `feature/cart-endpoints` | Партнёр 2 | Изучить и расширить cart.py |
| `feature/orders-endpoints` | Партнёр 2 | Изучить и расширить orders.py |
| `feature/reviews-endpoints` | Партнёр 2 | Изучить и расширить reviews.py |
| `feature/additional-tests` | Партнёр 2 | Написать test_reviews.py |

---

## 5. Твоя задача — написать `tests/test_reviews.py`

Создай файл `tests/test_reviews.py` со следующим содержимым:

```python
from tests.conftest import get_token


def test_list_reviews_empty(client, sample_book):
    resp = client.get(f"/books/{sample_book.id}/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_review(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 4.5, "comment": "Great book!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 4.5
    assert data["comment"] == "Great book!"
    assert data["user_name"] == "Alice"


def test_create_review_invalid_rating(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 6.0},   # выше максимума
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_duplicate_review_blocked(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 3.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Second review on same book — should fail
    resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 5.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_delete_own_review(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    create_resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 2.0, "comment": "Not great"},
        headers={"Authorization": f"Bearer {token}"},
    )
    review_id = create_resp.json()["id"]

    resp = client.delete(
        f"/books/{sample_book.id}/reviews/{review_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


def test_delete_other_users_review_forbidden(client, regular_user, admin_user, sample_book):
    # Alice создаёт отзыв
    alice_token = get_token(client, "alice@test.com", "alice1234")
    create_resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 5.0},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    review_id = create_resp.json()["id"]

    # Admin пытается удалить — но не может (только сам автор)
    admin_token = get_token(client, "admin@test.com", "admin1234")
    resp = client.delete(
        f"/books/{sample_book.id}/reviews/{review_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 403


def test_review_on_nonexistent_book(client, regular_user):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post(
        "/books/9999/reviews",
        json={"rating": 3.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
```

Запусти тесты:
```bash
pytest tests/test_reviews.py -v
```

---

## 6. Проверь что всё работает через Swagger

1. Открой http://localhost:8000/docs
2. Нажми `POST /auth/login` → введи `alice@example.com` / `alice1234`
3. Скопируй `access_token`
4. Нажми кнопку **Authorize** (замочек вверху) → вставь токен
5. Теперь можешь тестировать защищённые эндпоинты прямо из браузера

---

## 7. Запуск всех тестов с покрытием

```bash
pytest
```

Откроет отчёт в `htmlcov/index.html` — там видно какие строки кода покрыты тестами.  
**Цель: ≥ 50% coverage** (для ABET PI 2.3).

---

## 8. Что спросят на защите — твоя часть

Готовься объяснить:

**Cart:**
- Как создаётся корзина? (автоматически при первом обращении)
- Что происходит при добавлении товара которого нет в наличии?
- Почему у каждого пользователя только одна корзина?

**Orders:**
- Опиши полный флоу: от корзины до оплаченного заказа
- Что такое `unit_price` в `order_items` и зачем он нужен?
- Что делает `_call_payment_mock`?
- Какие статусы может иметь заказ?

**Reviews:**
- Почему один пользователь может оставить только один отзыв на книгу?
- Где в коде это проверяется? (UniqueConstraint в модели + проверка в роутере)
- Как вычисляется средний рейтинг книги?

**Тесты:**
- Что такое fixture в pytest? Покажи пример
- Почему тесты используют SQLite а не PostgreSQL?
- Что такое `conftest.py`?

---

## 9. GitHub Projects — Task Board

Зайди на GitHub репозиторий → вкладка **Projects** → создай доску:

| Колонка | Задачи партнёра 2 |
|---|---|
| **Todo** | Изучить cart.py, Написать test_reviews.py, Настроить окружение |
| **In Progress** | (переноси когда начал) |
| **Done** | (переноси когда закончил и сделал PR) |

Это нужно для **ABET PI 5.1** (вклад в команду виден через task board).

---

## 10. Чеклист перед сдачей

- [ ] Склонировал репо и запустил через Docker
- [ ] Все 24 теста проходят (`pytest --no-cov`)
- [ ] Написал `tests/test_reviews.py` (7 тестов)
- [ ] Сделал минимум 2 Pull Request с ревью от партнёра
- [ ] В task board есть выполненные задачи
- [ ] Можешь объяснить: cart, orders, reviews, тесты

---

## Контакты

Если что-то не работает — пиши партнёру. Основные команды:

```bash
docker-compose up --build    # запустить всё
docker-compose down -v       # остановить и удалить данные
pytest --no-cov -v           # тесты без coverage (быстро)
pytest -v                    # тесты с coverage отчётом
docker-compose logs app      # логи приложения
```
