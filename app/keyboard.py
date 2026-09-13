"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026
"""
import asyncio
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.database.requests as rq


# ==================== MAIN INLINE KEYBOARD ====================

def main_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Price List", callback_data="btn_price_list"),
            InlineKeyboardButton(text="📅 Booking", callback_data="btn_booking")
        ],
        [
            InlineKeyboardButton(text="🔧 STO Booking", callback_data="btn_sto_booking"),
            InlineKeyboardButton(text="🍽 Order Food", callback_data="btn_order_food")
        ],
        [
            InlineKeyboardButton(text="🛒 Shop", callback_data="btn_shop")
        ],
        [
            InlineKeyboardButton(text="⭐ Reviews", callback_data="btn_reviews"),
            InlineKeyboardButton(text="ℹ️ About", callback_data="btn_about")
        ]
    ])


# Для зворотної сумісності (якщо десь потрібна нижня клава)
rpbt = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Price List"), KeyboardButton(text="Booking")],
        [KeyboardButton(text="STO Booking"), KeyboardButton(text="Order Food")],
        [KeyboardButton(text="Shop")],
        [KeyboardButton(text="Reviews"), KeyboardButton(text="About")],
    ],
    resize_keyboard=True
)


# ==================== INLINE KEYBOARDS ====================

async def categories():
    cats = await rq.get_root_categories()
    keyboard = InlineKeyboardBuilder()
    if cats:
        for cat in cats:
            keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="🏠 Main Menu", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()


async def subcategories(cat_id: int):
    subs = await rq.get_subcategories(cat_id)
    keyboard = InlineKeyboardBuilder()
    if subs:
        for sub in subs:
            keyboard.add(InlineKeyboardButton(text=sub.name, callback_data=f"category_{sub.id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Back", callback_data="back_to_categories"))
    keyboard.add(InlineKeyboardButton(text="🏠 Main Menu", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()


async def item(cat_id: int):
    items = await rq.get_categories_item(cat_id)
    keyboard = InlineKeyboardBuilder()
    if items:
        for item_obj in items:
            keyboard.add(InlineKeyboardButton(text=f"{item_obj.name} — {item_obj.price}", callback_data=f"item_{item_obj.id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Back", callback_data="to_categories"))
    keyboard.add(InlineKeyboardButton(text="🏠 Main Menu", callback_data="to_main"))
    return keyboard.adjust(1).as_markup()


def dates_keyboard():
    keyboard = InlineKeyboardBuilder()
    today = datetime.now()
    for i in range(7):
        date_obj = today + timedelta(days=i)
        date_str = date_obj.strftime("%Y-%m-%d")
        display = date_obj.strftime("%d.%m.%Y")
        keyboard.add(InlineKeyboardButton(text=display, callback_data=f"book_date_{date_str}"))
    keyboard.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_booking"))
    return keyboard.adjust(1).as_markup()


async def times_keyboard(date: str):
    times = [
        "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
    ]
    keyboard = InlineKeyboardBuilder()
    for t in times:
        keyboard.add(InlineKeyboardButton(text=t, callback_data=f"book_time_{t}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Back", callback_data="book_date_back"))
    keyboard.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_booking"))
    return keyboard.adjust(3).as_markup()