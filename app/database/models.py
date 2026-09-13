"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026

This code is provided for viewing and personal use only.
Do not redistribute or claim authorship. See LICENSE for terms.
"""
import os
from sqlalchemy import BigInteger, String, ForeignKey, select, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession


DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    if os.getenv('RENDER'):
        raise RuntimeError('DATABASE_URL не заданий у продакшн-середовищі (Render)!')
    DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3'
    print('⚠️  DATABASE_URL не знайдено — використовується локальний SQLite')
else:
    # Render видає postgresql://, а SQLAlchemy async потребує +asyncpg
    if DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
    db_url_masked = DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL
    print(f'🗄️  models.py підключається до: {db_url_masked}')

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=True)


class Item(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(120))
    price: Mapped[str] = mapped_column(String(20))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))


class Appointment(Base):
    __tablename__ = 'appointments'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    master: Mapped[str] = mapped_column(String(50))
    service: Mapped[str] = mapped_column(String(100))
    date: Mapped[str] = mapped_column(String(10))
    time: Mapped[str] = mapped_column(String(5))
    status: Mapped[str] = mapped_column(String(20), default='pending')
    is_deleted: Mapped[bool] = mapped_column(default=False)


# ==================== ФУНКЦІЇ ====================

async def set_user(tg_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()


async def get_all_categories():
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.parent_id == None))
        return result.scalars().all()


async def get_root_categories():
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.parent_id == None))
        return result.scalars().all()


async def get_subcategories(cat_id: int):
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.parent_id == cat_id))
        return result.scalars().all()


async def get_item(item_id: int):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.id == item_id))
        return result.scalar_one_or_none()


async def get_categories_item(cat_id: int):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.category == cat_id))
        return result.scalars().all()


async def get_all_items():
    async with async_session() as session:
        result = await session.execute(select(Item))
        return result.scalars().all()


async def update_item_price(item_id: int, price: str):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if item:
            item.price = price
            await session.commit()


async def add_item(name: str, desc: str, price: str, cat_id: int):
    async with async_session() as session:
        item = Item(name=name, description=desc, price=price, category=cat_id)
        session.add(item)
        await session.commit()


async def delete_item(item_id: int):
    async with async_session() as session:
        await session.execute(delete(Item).where(Item.id == item_id))
        await session.commit()


async def add_appointment(tg_id: int, username: str, name: str, phone: str,
                          master: str, service: str, date: str, time: str):
    async with async_session() as session:
        appointment = Appointment(
            tg_id=tg_id,
            username=username,
            name=name,
            phone=phone,
            master=master,
            service=service,
            date=date,
            time=time
        )
        session.add(appointment)
        await session.commit()
        return appointment


async def get_all_appointments():
    async with async_session() as session:
        result = await session.execute(
            select(Appointment).where(Appointment.is_deleted == False)
        )
        return result.scalars().all()


async def delete_appointment(appointment_id: int):
    async with async_session() as session:
        result = await session.execute(select(Appointment).where(Appointment.id == appointment_id))
        appointment = result.scalar_one_or_none()
        if appointment:
            appointment.is_deleted = True
            await session.commit()


# ==================== ІНІЦІАЛІЗАЦІЯ ====================

async def init_db():
    """Створити таблиці при запуску бота"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

__all__ = ['async_session', 'Base', 'User', 'Category', 'Item', 'Appointment', 'init_db']
