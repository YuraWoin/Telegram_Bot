"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026

This code is provided for viewing and personal use only.
Do not redistribute or claim authorship. See LICENSE for terms.
"""
from app.database.models import async_session
from app.database.models import User, Category, Item
from app.database.models import Appointment
from datetime import datetime
from sqlalchemy import select, update

async def add_appointment(tg_id, username, name, phone, master, service, date, time):
    async with async_session() as session:
        session.add(Appointment(
            tg_id=tg_id,
            username=username,
            name=name,
            phone=phone,
            master=master,
            service=service,
            date=date,
            time=time
        ))
        await session.commit()

async def get_booked_times(date):
    async with async_session() as session:
        result = await session.scalars(
            select(Appointment).where(
                Appointment.date == date,
                Appointment.status != 'cancelled'
            )
        )
        return [a.time for a in result.all()]


async def set_user(tg_id):
    async with async_session() as sesion:
        try:
            user = await sesion.scalar(select(User).where(User.tg_id == tg_id))

            if not user:
                sesion.add(User(tg_id=tg_id))
                await sesion.commit()
                print('operation to bd')
        except Exception as e:
            print('ERROR', e)


async def get_categories():
    async with async_session() as sesion:
        return await sesion.scalars(select(Category).where(Category.parent_id == None))

async def get_categories_item(category_id):
    async with async_session() as sesion:
        return await sesion.scalars(select(Item).where(Item.category == category_id))

    
async def get_item(item_id):
    async with async_session() as sesion:
        return await sesion.scalar(select(Item).where(Item.id == item_id))
    
async def get_root_categories():
    async with async_session() as sesion:
        return await sesion.scalars(select(Category).where(Category.parent_id == None))

async def get_subcategories(parent_id):
    async with async_session() as sesion:
        return await sesion.scalars(select(Category).where(Category.parent_id == parent_id))

async def get_booking_categories():
    async with async_session() as session:
        return await session.scalars(
            select(Category).where(
                Category.parent_id == None,
                Category.name != 'Догляд за волоссям'
            )
        )

async def get_all_appointments():
    async with async_session() as session:
        result = await session.scalars(
            select(Appointment).where(Appointment.is_deleted == False)
        )
        return result.all()

async def update_item_price(item_id, new_price):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        item.price = new_price
        await session.commit()

async def get_all_items():
    async with async_session() as session:
        result = await session.scalars(select(Item))
        return result.all()

async def get_all_categories():
    async with async_session() as session:
        result = await session.scalars(select(Category))
        return result.all()



async def delete_appointment(appointment_id):
    async with async_session() as session:
        a = await session.scalar(select(Appointment).where(Appointment.id == appointment_id))
        if a:
            a.is_deleted = True
            await session.commit()

async def delete_item(item_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
        if item:
            await session.delete(item)
            await session.commit()
