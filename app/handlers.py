"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026
"""
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import F
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

import app.keyboard as kb
import app.database.requests as rq
import app.info as inf
import os
import json
from app.middlewsres import TestMiddleware
from app.google_sheets import append_booking, sync_all_appointments
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()
router.message.middleware(TestMiddleware())
load_dotenv()

admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip().strip("'").strip('"')) for x in admin_ids_str.split(",") if x.strip()]


# ==================== STATES ====================

class AdminStates(StatesGroup):
    change_price_item = State()
    change_price_value = State()
    add_name = State()
    add_desc = State()
    add_price = State()
    add_category = State()


class Reg(StatesGroup):
    master = State()
    service = State()
    date = State()
    time = State()
    name = State()
    number = State()


class CartStates(StatesGroup):
    checkout_name = State()
    checkout_phone = State()
    checkout_address = State()


class CafeStates(StatesGroup):
    cafe_name = State()
    cafe_phone = State()


class STOReg(StatesGroup):
    master = State()
    service = State()
    date = State()
    time = State()
    name = State()
    number = State()


# ==================== MASTERS ====================

MASTER_CATEGORIES = {
    "Galyna": ["Волосся", "Нігті", "Макіяж", "Брови"],
    "Natala": ["Волосся", "Нігті", "Макіяж", "Брови"],
    "Tanya": ["Волосся", "Нігті", "Макіяж", "Брови"],
    "Andriana": ["Макіяж", "Брови"],
}

MASTERS_CATEGORIES = {
    "Oleksiy": ["Діагностика", "Заміна оливи", "Ремонт двигуна", "Підвіска", "Шини", "Електрика"],
    "Dmytro": ["Діагностика", "Заміна оливи", "Ремонт двигуна", "Підвіска", "Шини", "Електрика"],
    "Serhiy": ["Діагностика", "Заміна оливи", "Ремонт двигуна", "Електрика"],
}

STO_MASTERS = MASTERS_CATEGORIES


# ==================== CART STORAGE ====================

user_carts = {}


# ==================== START & MAIN MENU ====================

START_TEXT = (
    "Вітаємо у нашому бізнес-чат-боті! 🌸\n\n"
    "Тут ви можете записатися на прийом, замовити їжу, обрати товари онлайн і переглянути прайс-лист.\n\n"
    "💳 <b>Прайс-лист:</b> Переглянути вартість послуг.\n"
    "📅 <b>Запис:</b> Запис у салон.\n"
    "🔧 <b>Запис СТО:</b> Запис на автосервіс.\n"
    "🍽 <b>Замовити їжу:</b> Меню кафе.\n"
    "🛒 <b>Магазин:</b> Перегляд товарів і кошик.\n\n"
    "Оберіть опцію нижче:"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    sticker_file_id = ('sticker.webp'),
    await message.answer_sticker(
        sticker=sticker_file_id
    )
    await message.answer(
        f"Вітаємо, {message.from_user.first_name}!\n\n" + START_TEXT,
        reply_markup=kb.main_inline(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "to_main")
async def to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"Вітаємо, {callback.from_user.first_name}!\n\n" + START_TEXT,
        reply_markup=kb.main_inline(),
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== MINI APP BRIEFS (WebApp sendData) ====================

@router.message(F.web_app_data)
async def webapp_brief(message: Message):
    """Бриф з міні-апки YuStack (sendData) → форвард власнику."""
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        return
    if not isinstance(data, dict) or data.get("type") != "brief":
        return

    name = str(data.get("name") or "").strip() or str(data.get("from") or "—").strip() or "—"
    niche = str(data.get("niche") or "—").strip() or "—"
    pain = str(data.get("pain") or "—").strip() or "—"
    sender = message.from_user
    who = f"@{sender.username}" if sender.username else f"id {sender.id}"

    text = (
        "<b>Новий бриф з міні-апки</b>\n\n"
        f"👤 Імʼя: {name}\n"
        f"🏷 Ніша: {niche}\n"
        f"💬 Що болить: {pain}\n"
        f"🔗 Від: {who}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(chat_id=admin_id, text=text, parse_mode="HTML")
        except Exception:
            pass

    try:
        await message.answer("Дякую! Бриф отримано. Оцінку і наступні кроки напишу сюди.")
    except Exception:
        pass


# ==================== PRICE LIST ====================

@router.message(F.text == "Прайс-лист")
async def catalog_msg(message: Message):
    await message.answer("Оберіть категорію:", reply_markup=await kb.categories())


@router.callback_query(F.data == "btn_price_list")
async def catalog_cb(callback: CallbackQuery):
    await callback.message.edit_text("Оберіть категорію:", reply_markup=await kb.categories())
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def category(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[1])
    subs = list(await rq.get_subcategories(cat_id))
    if subs:
        await callback.message.edit_text("Оберіть підкатегорію:", reply_markup=await kb.subcategories(cat_id))
    else:
        await callback.message.edit_text("Оберіть послугу для перегляду деталей:", reply_markup=await kb.item(cat_id))
    await callback.answer()


@router.callback_query(F.data == "to_categories")
async def to_categories(callback: CallbackQuery):
    await callback.message.edit_text("Оберіть категорію:", reply_markup=await kb.categories())
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    await callback.message.edit_text("Оберіть категорію:", reply_markup=await kb.categories())
    await callback.answer()


@router.callback_query(F.data.startswith("item_"))
async def category_item(callback: CallbackQuery):
    item_data = await rq.get_item(int(callback.data.split("_")[1]))
    await callback.message.edit_text(
        f"🔹 {item_data.name}\n📝 {item_data.description}\n💰 Ціна: {item_data.price}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"category_{item_data.category}")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )
    await callback.answer()


# ==================== INFO / REVIEWS ====================

@router.message(F.text == "Відгуки")
async def vidguk_msg(message: Message):
    await message.answer(
        "⭐ Ви можете переглянути відгуки на нашій сторінці в Instagram:\nhttps://www.instagram.com/yustack7/",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📸 Відкрити Instagram", url="https://www.instagram.com/yustack7/")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )


@router.callback_query(F.data == "btn_reviews")
async def vidguk_cb(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ Ви можете переглянути відгуки на нашій сторінці в Instagram:\nhttps://www.instagram.com/yustack7/",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📸 Відкрити Instagram", url="https://www.instagram.com/yustack7/")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )
    await callback.answer()


@router.message(F.text == "Про нас")
async def info_msg(message: Message):
    await message.answer(
        inf.infofo,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )


@router.callback_query(F.data == "btn_about")
async def info_cb(callback: CallbackQuery):
    await callback.message.edit_text(
        inf.infofo,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )
    await callback.answer()


# ==================== BEAUTY / BARBERSHOP BOOKING ====================

@router.message(F.text == "Запис")
async def zapus_msg(message: Message, state: FSMContext):
    await rq.set_user(message.from_user.id)
    await state.set_state(Reg.master)

    keyboard_rows = []
    for master_key in MASTER_CATEGORIES.keys():
        keyboard_rows.append([InlineKeyboardButton(text=f"✂️ {master_key}", callback_data=f"master_{master_key}")])
    keyboard_rows.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")])
    await message.answer("Оберіть майстра:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))


@router.callback_query(F.data == "btn_booking")
async def zapus_cb(callback: CallbackQuery, state: FSMContext):
    await rq.set_user(callback.from_user.id)
    await state.set_state(Reg.master)

    keyboard_rows = []
    for master_key in MASTER_CATEGORIES.keys():
        keyboard_rows.append([InlineKeyboardButton(text=f"✂️ {master_key}", callback_data=f"master_{master_key}")])
    keyboard_rows.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")])
    await callback.message.edit_text("Оберіть майстра:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
    await callback.answer()


@router.callback_query(F.data.startswith("master_"), Reg.master)
async def choose_master(callback: CallbackQuery, state: FSMContext):
    master_key = callback.data.replace("master_", "")
    await state.update_data(master=f"Майстер {master_key}")
    await state.set_state(Reg.service)

    allowed = MASTER_CATEGORIES.get(master_key, [])
    cats = await rq.get_all_categories()
    keyboard = InlineKeyboardBuilder()
    for cat in cats:
        if cat.name in allowed:
            keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=f"book_cat_{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking"))
    await callback.message.edit_text("Оберіть категорію послуг:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data.startswith("book_cat_"), Reg.service)
async def choose_service_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    items = list(await rq.get_categories_item(cat_id))
    keyboard = InlineKeyboardBuilder()
    for item_obj in items:
        keyboard.add(InlineKeyboardButton(text=f"{item_obj.name} — {item_obj.price}", callback_data=f"book_service_{item_obj.id}_{item_obj.name}"))
    keyboard.add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking"))
    await callback.message.edit_text("Оберіть послугу:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data.startswith("book_service_"), Reg.service)
async def choose_service(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 3)
    service_name = parts[3] if len(parts) > 3 else parts[2]
    await state.update_data(service=service_name)
    await state.set_state(Reg.date)
    await callback.message.edit_text("Оберіть дату:", reply_markup=kb.dates_keyboard())


@router.callback_query(F.data.startswith("book_date_"), Reg.date)
async def choose_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split("_", 2)[2]
    await state.update_data(date=date)
    await state.set_state(Reg.time)
    await callback.message.edit_text("Оберіть час:", reply_markup=await kb.times_keyboard(date))


@router.callback_query(F.data == "book_date_back", Reg.time)
async def back_to_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.date)
    await callback.message.edit_text("Оберіть дату:", reply_markup=kb.dates_keyboard())


@router.callback_query(F.data.startswith("book_time_"), Reg.time)
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split("_", 2)[2]
    await state.update_data(time=time)
    await state.set_state(Reg.name)
    await callback.message.delete()
    await callback.message.answer(
        "Введіть ваше ім'я та прізвище:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")]
        ])
    )


@router.message(Reg.name, F.text)
async def zapus_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer(
        "Введіть ваш номер телефону або натисніть кнопку нижче:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(Reg.number, F.contact)
async def zapus_number_contact(message: Message, state: FSMContext):
    await _finish_beauty_booking(message, state, message.contact.phone_number)


@router.message(Reg.number, F.text)
async def zapus_number_text(message: Message, state: FSMContext):
    await _finish_beauty_booking(message, state, message.text)


async def _finish_beauty_booking(message: Message, state: FSMContext, number: str):
    await state.update_data(number=number)
    data = await state.get_data()
    await state.clear()

    await rq.add_appointment(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=data['name'],
        phone=data['number'],
        master=data['master'],
        service=data['service'],
        date=data['date'],
        time=data['time']
    )

    try:
        append_booking(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            name=data['name'],
            phone=data['number'],
            master=data['master'],
            service=data['service'],
            date=data['date'],
            time=data['time']
        )
    except Exception as e:
        print(f"[Google Sheets Error] {e}")

    await message.answer(
        "✅ Ви успішно записані!\n\n"
        f"👤 {data['name']}\n"
        f"📱 {data['number']}\n"
        f"💇 {data['master']}\n"
        f"✂️ {data['service']}\n"
        f"📅 {data['date']} о {data['time']}\n\n"
        "Дякуємо за запис! 🌸",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"🔔 Новий запис!\n\n"
                     f"👤 {data['name']}\n"
                     f"📱 {data['number']}\n"
                     f"💇 {data['master']}\n"
                     f"✂️ {data['service']}\n"
                     f"📅 {data['date']} о {data['time']}"
            )
        except Exception:
            pass


@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Запис скасовано", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
    ]))


# ==================== STO BOOKING ====================

@router.message(F.text == "Запис СТО")
async def sto_start_msg(message: Message, state: FSMContext):
    await rq.set_user(message.from_user.id)
    await state.set_state(STOReg.master)

    keyboard_rows = []
    for master_key in STO_MASTERS.keys():
        keyboard_rows.append([InlineKeyboardButton(text=f"🔧 {master_key}", callback_data=f"sto_master_{master_key}")])
    keyboard_rows.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")])
    await message.answer("Оберіть механіка:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))


@router.callback_query(F.data == "btn_sto_booking")
async def sto_start_cb(callback: CallbackQuery, state: FSMContext):
    await rq.set_user(callback.from_user.id)
    await state.set_state(STOReg.master)

    keyboard_rows = []
    for master_key in STO_MASTERS.keys():
        keyboard_rows.append([InlineKeyboardButton(text=f"🔧 {master_key}", callback_data=f"sto_master_{master_key}")])
    keyboard_rows.append([InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")])
    await callback.message.edit_text("Оберіть механіка:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_rows))
    await callback.answer()


@router.callback_query(F.data.startswith("sto_master_"), STOReg.master)
async def sto_choose_master(callback: CallbackQuery, state: FSMContext):
    master_key = callback.data.replace("sto_master_", "")
    await state.update_data(master=f"Механік {master_key}")
    await state.set_state(STOReg.service)

    allowed = STO_MASTERS.get(master_key, [])
    cats = await rq.get_all_categories()
    keyboard = InlineKeyboardBuilder()
    for cat in cats:
        if cat.name in allowed:
            keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=f"sto_cat_{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking"))
    await callback.message.edit_text("Оберіть категорію послуг:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data.startswith("sto_cat_"), STOReg.service)
async def sto_choose_service(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    items = list(await rq.get_categories_item(cat_id))
    keyboard = InlineKeyboardBuilder()
    for item_obj in items:
        keyboard.add(InlineKeyboardButton(text=f"{item_obj.name} — {item_obj.price}", callback_data=f"sto_service_{item_obj.id}_{item_obj.name}"))
    keyboard.add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking"))
    await callback.message.edit_text("Оберіть послугу:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data.startswith("sto_service_"), STOReg.service)
async def sto_service_selected(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 3)
    service_name = parts[3] if len(parts) > 3 else parts[2]
    await state.update_data(service=service_name)
    await state.set_state(STOReg.date)
    await callback.message.edit_text("Оберіть дату:", reply_markup=kb.dates_keyboard())


@router.callback_query(F.data.startswith("book_date_"), STOReg.date)
async def sto_choose_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split("_", 2)[2]
    await state.update_data(date=date)
    await state.set_state(STOReg.time)
    await callback.message.edit_text("Оберіть час:", reply_markup=await kb.times_keyboard(date))


@router.callback_query(F.data == "book_date_back", STOReg.time)
async def sto_back_to_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(STOReg.date)
    await callback.message.edit_text("Оберіть дату:", reply_markup=kb.dates_keyboard())


@router.callback_query(F.data.startswith("book_time_"), STOReg.time)
async def sto_choose_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split("_", 2)[2]
    await state.update_data(time=time)
    await state.set_state(STOReg.name)
    await callback.message.delete()
    await callback.message.answer(
        "Введіть ваше ім'я:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")]
        ])
    )


@router.message(STOReg.name, F.text)
async def sto_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(STOReg.number)
    await message.answer(
        "Введіть ваш номер телефону або натисніть кнопку нижче:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(STOReg.number, F.contact)
async def sto_number_contact(message: Message, state: FSMContext):
    await _finish_sto_booking(message, state, message.contact.phone_number)


@router.message(STOReg.number, F.text)
async def sto_number_text(message: Message, state: FSMContext):
    await _finish_sto_booking(message, state, message.text)


async def _finish_sto_booking(message: Message, state: FSMContext, number: str):
    await state.update_data(number=number)
    data = await state.get_data()
    await state.clear()

    await rq.add_appointment(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=data['name'],
        phone=data['number'],
        master=data['master'],
        service=data['service'],
        date=data['date'],
        time=data['time']
    )

    try:
        append_booking(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            name=data['name'],
            phone=data['number'],
            master=data['master'],
            service=data['service'],
            date=data['date'],
            time=data['time']
        )
    except Exception as e:
        print(f"[Google Sheets Error] {e}")

    await message.answer(
        "✅ Запис на СТО підтверджено!\n\n"
        f"👤 {data['name']}\n"
        f"📱 {data['number']}\n"
        f"🔧 {data['master']}\n"
        f"⚙️ {data['service']}\n"
        f"📅 {data['date']} о {data['time']}\n\n"
        "Чекаємо на вас на СТО! 🚗",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"🔧 Новий запис на СТО!\n\n"
                     f"👤 {data['name']}\n"
                     f"📱 {data['number']}\n"
                     f"🔧 {data['master']}\n"
                     f"⚙️ {data['service']}\n"
                     f"📅 {data['date']} о {data['time']}"
            )
        except Exception:
            pass


# ==================== CAFE ORDER ====================

@router.message(F.text == "Замовити їжу")
async def cafe_menu_msg(message: Message):
    await _show_cafe_menu(message)


@router.callback_query(F.data == "btn_order_food")
async def cafe_menu_cb(callback: CallbackQuery):
    await _show_cafe_menu(callback)
    await callback.answer()


async def _show_cafe_menu(event):
    root_cats = await rq.get_root_categories()
    food_cat = next((c for c in root_cats if c.name == "Меню їжі"), None)

    if food_cat:
        subs = list(await rq.get_subcategories(food_cat.id))
    else:
        all_cats = await rq.get_all_categories()
        subs = [c for c in all_cats if c.name in ["Сніданки", "Обіди", "Вечері", "Напої", "Десерти"]]

    keyboard = InlineKeyboardBuilder()
    for cat in subs:
        keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=f"cafe_cat_{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main"))

    text = "Оберіть категорію їжі:"
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard.adjust(2).as_markup())
    else:
        await event.answer(text, reply_markup=keyboard.adjust(2).as_markup())


@router.callback_query(F.data.startswith("cafe_cat_"))
async def cafe_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    subs = list(await rq.get_subcategories(cat_id))
    if subs:
        keyboard = InlineKeyboardBuilder()
        for sub in subs:
            keyboard.add(InlineKeyboardButton(text=sub.name, callback_data=f"cafe_cat_{sub.id}"))
        keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="cafe_back"))
        keyboard.add(InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main"))
        await callback.message.edit_text("Оберіть підкатегорію:", reply_markup=keyboard.adjust(2).as_markup())
    else:
        items = list(await rq.get_categories_item(cat_id))
        keyboard = InlineKeyboardBuilder()
        for item_obj in items:
            keyboard.add(InlineKeyboardButton(text=f"{item_obj.name} — {item_obj.price}", callback_data=f"cafe_item_{item_obj.id}_{item_obj.name}"))
        keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="cafe_back"))
        keyboard.add(InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main"))
        await callback.message.edit_text("Оберіть страву:", reply_markup=keyboard.adjust(1).as_markup())
    await callback.answer()


@router.callback_query(F.data == "cafe_back")
async def cafe_back(callback: CallbackQuery):
    await _show_cafe_menu(callback)


@router.callback_query(F.data.startswith("cafe_item_"))
async def cafe_choose_item(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_", 3)
    item_name = parts[3] if len(parts) > 3 else parts[2]
    await state.update_data(cafe_order=item_name)
    await state.set_state(CafeStates.cafe_name)
    await callback.message.answer("Введіть ваше ім'я:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")]
    ]))


@router.message(CafeStates.cafe_name, F.text)
async def cafe_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CafeStates.cafe_phone)
    await message.answer(
        "Введіть ваш номер телефону або натисніть кнопку нижче:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(CafeStates.cafe_phone, F.contact)
async def cafe_phone_contact(message: Message, state: FSMContext):
    await _cafe_finish(message, state, message.contact.phone_number)


@router.message(CafeStates.cafe_phone, F.text)
async def cafe_phone_text(message: Message, state: FSMContext):
    await _cafe_finish(message, state, message.text)


async def _cafe_finish(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    await state.clear()

    await rq.add_appointment(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=data['name'],
        phone=phone,
        master="Кафе",
        service=data['cafe_order'],
        date="Н/Д",
        time="Н/Д"
    )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"🍽 Нове замовлення з кафе!\n\n"
                     f"👤 {data['name']}\n"
                     f"📱 {phone}\n"
                     f"🍕 {data['cafe_order']}"
            )
        except Exception:
            pass

    await message.answer(
        "✅ Замовлення оформлено!\n\n"
        f"👤 {data['name']}\n"
        f"📱 {phone}\n"
        f"🍕 {data['cafe_order']}\n\n"
        "Дякуємо! Ваше замовлення готується. 🍽",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )


# ==================== SHOP / CART ====================

@router.message(F.text == "Магазин")
async def shop_catalog_msg(message: Message):
    await _show_shop_catalog(message)


@router.callback_query(F.data == "btn_shop")
async def shop_catalog_cb(callback: CallbackQuery):
    await _show_shop_catalog(callback)
    await callback.answer()


async def _show_shop_catalog(event):
    root_cats = await rq.get_root_categories()
    shop_cat = next((c for c in root_cats if c.name == "Товари магазину"), None)

    if shop_cat:
        subs = list(await rq.get_subcategories(shop_cat.id))
    else:
        all_cats = await rq.get_all_categories()
        subs = [c for c in all_cats if c.name in ["Електроніка", "Одяг", "Дім і сад", "Спорт"]]

    keyboard = InlineKeyboardBuilder()
    for cat in subs:
        keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=f"shop_cat_{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="🛒 Кошик", callback_data="view_cart"))
    keyboard.add(InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main"))

    text = "Оберіть категорію товарів:"
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard.adjust(2).as_markup())
    else:
        await event.answer(text, reply_markup=keyboard.adjust(2).as_markup())


@router.callback_query(F.data.startswith("shop_cat_"))
async def shop_category(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[2])
    subs = list(await rq.get_subcategories(cat_id))
    if subs:
        keyboard = InlineKeyboardBuilder()
        for sub in subs:
            keyboard.add(InlineKeyboardButton(text=sub.name, callback_data=f"shop_cat_{sub.id}"))
        keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="shop_back"))
        keyboard.add(InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main"))
        await callback.message.edit_text("Оберіть підкатегорію:", reply_markup=keyboard.adjust(2).as_markup())
    else:
        items = list(await rq.get_categories_item(cat_id))
        keyboard = InlineKeyboardBuilder()
        for item_obj in items:
            keyboard.add(InlineKeyboardButton(text=f"🛒 {item_obj.name} — {item_obj.price}", callback_data=f"add_cart_{item_obj.id}"))
        keyboard.add(InlineKeyboardButton(text="🛒 Кошик", callback_data="view_cart"))
        keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="shop_back"))
        await callback.message.edit_text("Оберіть товар для додавання в кошик:", reply_markup=keyboard.adjust(1).as_markup())
    await callback.answer()


@router.callback_query(F.data == "shop_back")
async def shop_back(callback: CallbackQuery):
    await _show_shop_catalog(callback)


@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[2])
    item_data = await rq.get_item(item_id)
    user_id = callback.from_user.id

    if user_id not in user_carts:
        user_carts[user_id] = []

    found = False
    for cart_item in user_carts[user_id]:
        if cart_item["id"] == item_id:
            cart_item["qty"] += 1
            found = True
            break

    if not found:
        user_carts[user_id].append({
            "id": item_id,
            "name": item_data.name,
            "price": item_data.price,
            "qty": 1
        })

    await callback.answer(f"{item_data.name} додано в кошик")


@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await callback.answer("Кошик порожній")
        await callback.message.edit_text("🛒 Ваш кошик порожній", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍 До магазину", callback_data="btn_shop")],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ]))
        return

    text = "🛒 Ваш кошик:\n\n"
    for item_obj in cart:
        text += f"• {item_obj['name']} x{item_obj['qty']} — {item_obj['price']}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="checkout_cart")],
        [InlineKeyboardButton(text="🗑 Очистити кошик", callback_data="clear_cart")],
        [InlineKeyboardButton(text="◀️ Назад до магазину", callback_data="shop_back")],
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    user_carts.pop(callback.from_user.id, None)
    await callback.answer("Кошик очищено")
    await callback.message.edit_text("🛒 Кошик порожній", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 До магазину", callback_data="btn_shop")],
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
    ]))


@router.callback_query(F.data == "checkout_cart")
async def checkout_cart(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await callback.answer("Кошик порожній")
        return
    await state.set_state(CartStates.checkout_name)
    await callback.message.answer("Введіть ваше ім'я:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")]
    ]))


@router.message(CartStates.checkout_name, F.text)
async def cart_checkout_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CartStates.checkout_phone)
    await message.answer(
        "Введіть ваш номер телефону або натисніть кнопку нижче:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(CartStates.checkout_phone, F.contact)
async def cart_checkout_phone_contact(message: Message, state: FSMContext):
    await _cart_checkout_address(message, state, message.contact.phone_number)


@router.message(CartStates.checkout_phone, F.text)
async def cart_checkout_phone_text(message: Message, state: FSMContext):
    await _cart_checkout_address(message, state, message.text)


async def _cart_checkout_address(message: Message, state: FSMContext, phone: str):
    await state.update_data(phone=phone)
    await state.set_state(CartStates.checkout_address)
    await message.answer("Введіть адресу доставки або коментар:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_booking")]
    ]))


@router.message(CartStates.checkout_address, F.text)
async def cart_checkout_address(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    cart = user_carts.get(message.from_user.id, [])
    cart_text = "\n".join([f"• {item_obj['name']} x{item_obj['qty']}" for item_obj in cart])

    await rq.add_appointment(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=data['name'],
        phone=data['phone'],
        master="Інтернет-магазин",
        service=f"Order:\n{cart_text}",
        date="Н/Д",
        time="Н/Д"
    )

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"🛒 Нове замовлення з магазину!\n\n"
                     f"👤 {data['name']}\n"
                     f"📱 {data['phone']}\n"
                     f"📦\n{cart_text}\n"
                     f"📍 {message.text}"
            )
        except Exception:
            pass

    await message.answer(
        "✅ Замовлення оформлено!\n\n"
        f"👤 {data['name']}\n"
        f"📱 {data['phone']}\n"
        f"📦\n{cart_text}\n"
        f"📍 {message.text}\n\n"
        "Дякуємо за замовлення! 🛒",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="to_main")]
        ])
    )
    user_carts.pop(message.from_user.id, None)


# ==================== ADMIN PANEL ====================

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Доступ заборонено")
        return
    await message.answer("👑 Адмін-панель", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Усі записи", callback_data="admin_appointments")],
        [InlineKeyboardButton(text="💰 Змінити ціну", callback_data="admin_price")],
        [InlineKeyboardButton(text="➕ Додати послугу", callback_data="admin_add")],
        [InlineKeyboardButton(text="🗑 Видалити послугу", callback_data="admin_delete_item")],
        [InlineKeyboardButton(text="🔄 Синхронізувати з Sheets", callback_data="admin_sync_sheets")],
    ]))


@router.callback_query(F.data == "back_admin")
async def back_admin(callback: CallbackQuery):
    await callback.message.edit_text("👑 Адмін-панель", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Усі записи", callback_data="admin_appointments")],
        [InlineKeyboardButton(text="💰 Змінити ціну", callback_data="admin_price")],
        [InlineKeyboardButton(text="➕ Додати послугу", callback_data="admin_add")],
        [InlineKeyboardButton(text="🗑 Видалити послугу", callback_data="admin_delete_item")],
        [InlineKeyboardButton(text="🔄 Синхронізувати з Sheets", callback_data="admin_sync_sheets")],
    ]))


@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Скасовано", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
    ]))


# ---- Bookings ----

@router.callback_query(F.data == "admin_appointments")
async def admin_appointments(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    appointments = await rq.get_all_appointments()
    if not appointments:
        await callback.message.edit_text("📋 Записів ще немає", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
        ]))
        return
    await callback.message.edit_text("📋 Усі записи:")
    for a in appointments:
        text = (f"👤 {a.name} | 📱 {a.phone}\n"
                f"💇 {a.master} | ✂️ {a.service}\n"
                f"📅 {a.date} о {a.time}")
        await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Видалити", callback_data=f"del_appointment_{a.id}")]
        ]))
    await callback.message.answer("👆 Кінець списку", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
    ]))


@router.callback_query(F.data.startswith("del_appointment_"))
async def del_appointment(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    appointment_id = int(callback.data.split("_")[2])
    await rq.delete_appointment(appointment_id)
    await callback.message.delete()
    await callback.answer("✅ Видалено")


# ---- Sync to Google Sheets ----

import asyncio
import logging

log = logging.getLogger(__name__)
_sync_lock = asyncio.Lock()

BACK_KB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️ Back", callback_data="back_admin")]
])


@router.callback_query(F.data == "admin_sync_sheets")
async def admin_sync_ask(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer()
        return
    await callback.message.edit_text(
        "⚠️ Таблицю буде повністю перезаписано даними з бази. "
        "Усе, що додавали в таблиці вручну, зникне. Продовжити?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Так, синхронізувати",
                                  callback_data="admin_sync_sheets_confirm")],
            [InlineKeyboardButton(text="◀️ Back", callback_data="back_admin")],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_sync_sheets_confirm")
async def admin_sync_sheets(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer()
        return
    if _sync_lock.locked():
        await callback.answer("Синхронізація вже виконується", show_alert=True)
        return

    await callback.answer()
    async with _sync_lock:
        try:
            await callback.message.edit_text("⏳ Синхронізую...")
            count = await sync_all_appointments(rq.get_all_appointments, SHEET_ID)
            await callback.message.edit_text(
                f"✅ Synced {count} bookings to Google Sheets", reply_markup=BACK_KB
            )
        except Exception:
            log.exception("Sheets sync failed")
            await callback.message.edit_text(
                "❌ Помилка синхронізації. Деталі в логах.", reply_markup=BACK_KB
            )


# ---- Prices ----

@router.callback_query(F.data == "admin_price")
async def admin_price(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    items = await rq.get_all_items()
    keyboard = InlineKeyboardBuilder()
    for item_obj in items:
        keyboard.add(InlineKeyboardButton(text=f"{item_obj.name} — {item_obj.price}", callback_data=f"price_item_{item_obj.id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin"))
    await callback.message.edit_text("Оберіть послугу для зміни ціни:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data.startswith("price_item_"))
async def price_choose_item(callback: CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[2])
    await state.update_data(item_id=item_id)
    await state.set_state(AdminStates.change_price_value)
    await callback.message.edit_text("Введіть нову ціну:")


@router.message(AdminStates.change_price_value, F.text)
async def price_set_value(message: Message, state: FSMContext):
    data = await state.get_data()
    await rq.update_item_price(data["item_id"], message.text)
    await state.clear()
    await message.answer("✅ Ціну оновлено", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
    ]))


# ---- Add service ----

@router.callback_query(F.data == "admin_add")
async def admin_add(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminStates.add_name)
    await callback.message.answer("Введіть назву послуги:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_fsm")]
    ]))


@router.message(AdminStates.add_name, F.text)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_desc)
    await message.answer("Введіть опис:")


@router.message(AdminStates.add_desc, F.text)
async def add_item_desc(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await state.set_state(AdminStates.add_price)
    await message.answer("Введіть ціну:")


@router.message(AdminStates.add_price, F.text)
async def add_item_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdminStates.add_category)
    cats = await rq.get_root_categories()
    keyboard = InlineKeyboardBuilder()
    for cat in cats:
        keyboard.add(InlineKeyboardButton(text=cat.name, callback_data=f"addcat_{cat.id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_fsm"))
    await message.answer("Оберіть категорію:", reply_markup=keyboard.adjust(2).as_markup())


@router.callback_query(F.data.startswith("addcat_"), AdminStates.add_category)
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[1])
    subs = list(await rq.get_subcategories(cat_id))
    if subs:
        keyboard = InlineKeyboardBuilder()
        for sub in subs:
            keyboard.add(InlineKeyboardButton(text=sub.name, callback_data=f"addcat_{sub.id}"))
        keyboard.add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_fsm"))
        await callback.message.edit_text("Оберіть підкатегорію:", reply_markup=keyboard.adjust(2).as_markup())
    else:
        data = await state.get_data()
        await rq.add_item(data["name"], data["desc"], data["price"], cat_id)
        await state.clear()
        await callback.message.edit_text("✅ Послугу додано", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
        ]))


# -------------------delete service------------------
@router.callback_query(F.data == "admin_delete_item")
async def admin_delete_item(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    items = await rq.get_all_items()
    keyboard = InlineKeyboardBuilder()
    for item_obj in items:
        keyboard.add(InlineKeyboardButton(text=item_obj.name, callback_data=f"delete_item_{item_obj.id}"))
    keyboard.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin"))
    await callback.message.edit_text("Оберіть послугу для видалення:", reply_markup=keyboard.adjust(1).as_markup())


@router.callback_query(F.data.startswith("delete_item_"))
async def confirm_delete_item(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    item_id = int(callback.data.split("_")[2])
    await rq.delete_item(item_id)
    await callback.message.edit_text("✅ Послугу видалено", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_admin")]
    ]))
