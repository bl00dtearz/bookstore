"""Initial schema — all tables

Revision ID: 0001
Revises: 
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('customer', 'admin', name='userrole'), nullable=False, server_default='customer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # authors
    op.create_table('authors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_authors_id', 'authors', ['id'])
    op.create_index('ix_authors_name', 'authors', ['name'])

    # genres
    op.create_table('genres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_genres_id', 'genres', ['id'])
    op.create_index('ix_genres_name', 'genres', ['name'], unique=True)

    # books
    op.create_table('books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cover_url', sa.String(500), nullable=True),
        sa.Column('isbn', sa.String(20), nullable=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('authors.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('isbn'),
    )
    op.create_index('ix_books_id', 'books', ['id'])
    op.create_index('ix_books_title', 'books', ['title'])
    op.create_index('ix_books_author_id', 'books', ['author_id'])
    op.create_index('ix_books_title_price', 'books', ['title', 'price'])

    # book_genre (many-to-many)
    op.create_table('book_genre',
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('genre_id', sa.Integer(), sa.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True),
    )

    # carts
    op.create_table('carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_carts_id', 'carts', ['id'])
    op.create_index('ix_carts_user_id', 'carts', ['user_id'])

    # cart_items
    op.create_table('cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), sa.ForeignKey('carts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cart_items_id', 'cart_items', ['id'])
    op.create_index('ix_cart_items_cart_id', 'cart_items', ['cart_id'])
    op.create_index('ix_cart_items_book_id', 'cart_items', ['book_id'])

    # orders
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.Enum('pending','paid','processing','shipped','delivered','cancelled', name='orderstatus'), nullable=False, server_default='pending'),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('payment_id', sa.String(100), nullable=True),
        sa.Column('shipping_address', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])

    # order_items
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_order_items_id', 'order_items', ['id'])
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('ix_order_items_book_id', 'order_items', ['book_id'])

    # reviews
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('book_id', sa.Integer(), sa.ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('rating >= 1.0 AND rating <= 5.0', name='ck_review_rating'),
        sa.UniqueConstraint('user_id', 'book_id', name='uq_user_book_review'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'])
    op.create_index('ix_reviews_user_id', 'reviews', ['user_id'])
    op.create_index('ix_reviews_book_id', 'reviews', ['book_id'])


def downgrade():
    op.drop_table('reviews')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('cart_items')
    op.drop_table('carts')
    op.drop_table('book_genre')
    op.drop_table('books')
    op.drop_table('genres')
    op.drop_table('authors')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS orderstatus")
