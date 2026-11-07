from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, DateTime, func
from ..extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(db.String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price_cents: Mapped[int] = mapped_column(nullable=False)
    qty_in_stock: Mapped[int] = mapped_column(nullable=False, default=0)
    archived: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)