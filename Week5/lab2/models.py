from __future__ import annotations

from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    books: Mapped[List["Book"]] = relationship(back_populates="author")


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    slug: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)

    books: Mapped[List["Book"]] = relationship(back_populates="category")


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(db.String(100), nullable=False)

    reviews: Mapped[List["Review"]] = relationship(back_populates="user")


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(200), nullable=False)
    isbn: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    price_vnd: Mapped[int] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False, default=0)

    author_id: Mapped[int] = mapped_column(db.ForeignKey("authors.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(db.ForeignKey("categories.id"), nullable=False)

    author: Mapped[Author] = relationship(back_populates="books")
    category: Mapped[Category] = relationship(back_populates="books")
    reviews: Mapped[List["Review"]] = relationship(back_populates="book")


class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    book_id: Mapped[int] = mapped_column(db.ForeignKey("books.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)

    book: Mapped[Book] = relationship(back_populates="reviews")
    user: Mapped[User] = relationship(back_populates="reviews")
