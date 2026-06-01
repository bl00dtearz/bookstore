"""
Seed script — populates the database with realistic test data.
Run: python scripts/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.book import Author, Genre, Book
from app.services.auth import hash_password

def seed():
    db = SessionLocal()
    try:
        # ── Users ─────────────────────────────────────────────────────────────
        admin = User(name="Admin User", email="admin@bookstore.com",
                     password_hash=hash_password("admin1234"), role=UserRole.admin)
        customer = User(name="Alice Reader", email="alice@example.com",
                        password_hash=hash_password("alice1234"))
        db.add_all([admin, customer])
        db.flush()

        # ── Genres ────────────────────────────────────────────────────────────
        genres = {name: Genre(name=name) for name in
                  ["Fiction", "Science Fiction", "Mystery", "Biography", "Programming"]}
        db.add_all(genres.values())
        db.flush()

        # ── Authors ───────────────────────────────────────────────────────────
        authors = {
            "George Orwell": Author(name="George Orwell", bio="British novelist and essayist"),
            "Frank Herbert": Author(name="Frank Herbert", bio="Author of the Dune series"),
            "Agatha Christie": Author(name="Agatha Christie", bio="Queen of Crime fiction"),
            "Robert Martin": Author(name="Robert C. Martin", bio="Software engineer and author"),
        }
        db.add_all(authors.values())
        db.flush()

        # ── Books ──────────────────────────────────────────────────────────────
        books = [
            Book(title="1984", price=12.99, stock=50,
                 description="A dystopian social science fiction novel.",
                 isbn="9780451524935",
                 author=authors["George Orwell"],
                 genres=[genres["Fiction"]]),
            Book(title="Dune", price=14.99, stock=30,
                 description="An epic science fiction novel set in a far future feudal society.",
                 isbn="9780441013593",
                 author=authors["Frank Herbert"],
                 genres=[genres["Science Fiction"], genres["Fiction"]]),
            Book(title="Murder on the Orient Express", price=10.99, stock=25,
                 description="A classic mystery novel featuring Hercule Poirot.",
                 isbn="9780062693662",
                 author=authors["Agatha Christie"],
                 genres=[genres["Mystery"]]),
            Book(title="Clean Code", price=34.99, stock=40,
                 description="A handbook of agile software craftsmanship.",
                 isbn="9780132350884",
                 author=authors["Robert Martin"],
                 genres=[genres["Programming"]]),
            Book(title="Animal Farm", price=9.99, stock=60,
                 description="A satirical allegorical novella.",
                 isbn="9780451526342",
                 author=authors["George Orwell"],
                 genres=[genres["Fiction"]]),
        ]
        db.add_all(books)
        db.commit()
        print("✅ Database seeded successfully!")
        print("   Admin:    admin@bookstore.com / admin1234")
        print("   Customer: alice@example.com  / alice1234")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
