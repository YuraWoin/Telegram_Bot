"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026

This code is provided for viewing and personal use only.
Do not redistribute or claim authorship. See LICENSE for terms.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()   

from sqlalchemy import select
from app.database.models import Base, Category, Item, engine, async_session

db_url = os.getenv('DATABASE_URL', 'НЕ ЗАДАНО → fallback на SQLite!')
print(f"🗄️  seed.py працює з: {db_url.split('@')[-1] if '@' in db_url else db_url}")

class DatabaseSeeder:
    def __init__(self, session):
        self.session = session
        self.cats_cache = {}

    async def sync_categories(self, categories_list):
        pending = categories_list.copy()
        while pending:
            initial_len = len(pending)
            result = await self.session.execute(select(Category))
            self.cats_cache = {c.name: c.id for c in result.scalars().all()}

            for cat_tuple in pending[:]:
                name, parent_name = cat_tuple
                if name in self.cats_cache:
                    pending.remove(cat_tuple)
                    continue

                if parent_name is None or parent_name in self.cats_cache:
                    parent_id = self.cats_cache.get(parent_name)
                    self.session.add(Category(name=name, parent_id=parent_id))
                    pending.remove(cat_tuple)

            await self.session.flush()

            if len(pending) == initial_len:
                break

    async def sync_items(self, items_dict):
        result = await self.session.execute(select(Category))
        self.cats_cache = {c.name: c.id for c in result.scalars().all()}

        for cat_name, items in items_dict.items():
            cat_id = self.cats_cache.get(cat_name)
            if not cat_id:
                continue

            for name, desc, price in items:
                exists = await self.session.scalar(
                    select(Item).where(Item.name == name, Item.category == cat_id)
                )
                if not exists:
                    self.session.add(Item(
                        name=name,
                        description=desc,
                        price=price,
                        category=cat_id
                    ))


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:   # ← ВИПРАВЛЕНО
        async with session.begin():
            seeder = DatabaseSeeder(session)
            await seeder.sync_categories(CATEGORIES)
            await seeder.sync_items(ITEMS)


# ============================================================
# CATEGORIES FOR: BEAUTY SALON | BARBERSHOP | STO | CAFE | SHOP
# ============================================================

CATEGORIES = [
    # ===== BEAUTY SALON & BARBERSHOP =====
    ("Beauty Services", None),
    ("Hair", "Beauty Services"),
    ("Nails", "Beauty Services"),
    ("Makeup", "Beauty Services"),
    ("Brows", "Beauty Services"),
    ("Barber", "Beauty Services"),

    # ===== STO (AUTO SERVICE) =====
    ("STO Services", None),
    ("Diagnostics", "STO Services"),
    ("Oil Change", "STO Services"),
    ("Engine Repair", "STO Services"),
    ("Suspension", "STO Services"),
    ("Tires", "STO Services"),
    ("Electrics", "STO Services"),

    # ===== CAFE =====
    ("Food Menu", None),
    ("Breakfast", "Food Menu"),
    ("Lunch", "Food Menu"),
    ("Dinner", "Food Menu"),
    ("Drinks", "Food Menu"),
    ("Desserts", "Food Menu"),

    # ===== SHOP =====
    ("Shop Products", None),
    ("Electronics", "Shop Products"),
    ("Clothing", "Shop Products"),
    ("Home & Garden", "Shop Products"),
    ("Sports", "Shop Products"),
]


# ============================================================
# ITEMS / SERVICES / PRODUCTS
# ============================================================

ITEMS = {
    # ---------- BEAUTY SALON ----------
    "Hair": [
        ("Womens Haircut", "Professional womens haircut with styling", "30-50 USD"),
        ("Mens Haircut", "Mens haircut with clipper and scissors", "20-35 USD"),
        ("Hair Coloring", "Full hair coloring with premium dye", "50-120 USD"),
        ("Balayage", "Hand-painted balayage technique", "80-150 USD"),
        ("Keratin Treatment", "Smoothing keratin treatment", "100-200 USD"),
        ("Hair Botox", "Deep restoration hair botox", "80-150 USD"),
        ("Hair Styling", "Event styling and updo", "40-80 USD"),
    ],
    "Nails": [
        ("Classic Manicure", "Trim, shape, cuticle care, polish", "15 USD"),
        ("Gel Polish", "Gel polish with prep", "25 USD"),
        ("Nail Extensions", "Acrylic or gel extensions", "40 USD"),
        ("Pedicure", "Classic pedicure with scrub", "30 USD"),
        ("Nail Art", "Custom nail art design", "10-30 USD"),
    ],
    "Makeup": [
        ("Day Makeup", "Natural day makeup", "40 USD"),
        ("Evening Makeup", "Evening / event makeup", "60 USD"),
        ("Wedding Makeup", "Bridal makeup with trial", "120 USD"),
        ("Makeup Lesson", "1-on-1 makeup lesson", "80 USD"),
    ],
    "Brows": [
        ("Brow Shaping", "Wax or thread brow shaping", "12 USD"),
        ("Brow Tinting", "Henna or dye brow tinting", "18 USD"),
        ("Brow Lamination", "Brow lamination treatment", "30 USD"),
        ("Brow Combo", "Shaping + tinting + lamination", "50 USD"),
    ],
    "Barber": [
        ("Mens Haircut", "Classic mens haircut", "18 USD"),
        ("Beard Trim", "Beard shaping and trim", "12 USD"),
        ("Hot Towel Shave", "Traditional hot towel shave", "20 USD"),
        ("Hair Tattoo", "Creative hair tattoo design", "25 USD"),
        ("Beard Coloring", "Beard and mustache coloring", "15 USD"),
    ],

    # ---------- STO ----------
    "Diagnostics": [
        ("Computer Diagnostics", "Full ECU scan and error reading", "30 USD"),
        ("Electrical Diagnostics", "Wiring and sensor check", "25 USD"),
        ("Suspension Check", "Full suspension inspection", "20 USD"),
        ("Pre-Purchase Inspection", "Complete car condition report", "50 USD"),
    ],
    "Oil Change": [
        ("Engine Oil Change", "Oil + OEM filter replacement", "40 USD"),
        ("Transmission Oil Change", "ATF or CVT fluid change", "60 USD"),
        ("Filter Replacement", "Air, cabin, fuel filters", "15-30 USD"),
        ("Full Fluid Service", "All fluids top-up and check", "80 USD"),
    ],
    "Engine Repair": [
        ("Timing Belt Replacement", "Belt + tensioner + water pump", "200-400 USD"),
        ("Gasket Replacement", "Head gasket or valve cover", "150-300 USD"),
        ("Engine Overhaul", "Full engine rebuild", "1000-3000 USD"),
        ("Turbo Repair", "Turbocharger diagnostics and repair", "300-800 USD"),
    ],
    "Suspension": [
        ("Shock Absorber Replacement", "Front or rear shocks", "80-150 USD"),
        ("Spring Replacement", "Coil spring replacement", "60-100 USD"),
        ("Wheel Alignment", "3D alignment and camber adjustment", "30 USD"),
        ("Control Arm Replacement", "Wishbone / control arm", "50-100 USD"),
    ],
    "Tires": [
        ("Tire Mounting", "Mount and balance 4 tires", "40 USD"),
        ("Wheel Balancing", "Per wheel balancing", "8 USD"),
        ("Tire Repair", "Puncture repair with patch", "15 USD"),
        ("Seasonal Swap", "Summer / winter tire swap", "30 USD"),
    ],
    "Electrics": [
        ("Battery Replacement", "Battery test and replacement", "50-150 USD"),
        ("Alternator Repair", "Alternator rebuild or replace", "100-250 USD"),
        ("Wiring Repair", "Short circuit or harness repair", "40-100 USD"),
        ("Starter Repair", "Starter motor diagnostics", "80-200 USD"),
    ],

    # ---------- CAFE ----------
    "Breakfast": [
        ("Scrambled Eggs & Toast", "Fluffy eggs with butter toast", "8 USD"),
        ("Pancakes with Syrup", "3 stack with maple syrup", "9 USD"),
        ("Oatmeal Bowl", "With berries and honey", "7 USD"),
        ("Croissant & Coffee", "Butter croissant + espresso", "6 USD"),
        ("English Breakfast", "Eggs, bacon, beans, toast", "12 USD"),
    ],
    "Lunch": [
        ("Soup of the Day", "Chef's seasonal soup", "6 USD"),
        ("Caesar Salad", "Chicken, parmesan, croutons", "10 USD"),
        ("Classic Burger", "Beef patty, cheese, fries", "12 USD"),
        ("Pasta Carbonara", "Creamy bacon pasta", "11 USD"),
        ("Chicken Wrap", "Grilled chicken with veggies", "9 USD"),
    ],
    "Dinner": [
        ("Ribeye Steak", "300g with grilled vegetables", "25 USD"),
        ("Grilled Salmon", "With asparagus and lemon", "22 USD"),
        ("Mushroom Risotto", "Creamy arborio rice", "16 USD"),
        ("Chicken Wings", "BBQ or spicy, 10 pcs", "14 USD"),
        ("Pizza Margherita", "Classic tomato and mozzarella", "13 USD"),
    ],
    "Drinks": [
        ("Espresso", "Double shot", "3 USD"),
        ("Cappuccino", "With latte art", "4 USD"),
        ("Latte", "Vanilla or caramel", "4.5 USD"),
        ("Fresh Orange Juice", "Squeezed on spot", "5 USD"),
        ("Berry Smoothie", "Strawberry, blueberry, banana", "6 USD"),
        ("Lemonade", "Mint and lime", "4 USD"),
    ],
    "Desserts": [
        ("Cheesecake", "New York style", "7 USD"),
        ("Tiramisu", "Classic Italian", "8 USD"),
        ("Ice Cream Scoop", "3 flavors to choose", "4 USD"),
        ("Chocolate Lava Cake", "With vanilla ice cream", "9 USD"),
        ("Apple Pie", "With cinnamon", "6 USD"),
    ],

    # ---------- SHOP ----------
    "Electronics": [
        ("Smartphone X1", "6.1 inch OLED, 128GB", "699 USD"),
        ("Laptop Pro 14", "M3 chip, 16GB RAM", "1299 USD"),
        ("Wireless Headphones", "ANC, 30h battery", "199 USD"),
        ("Power Bank 20000mAh", "Fast charge 65W", "45 USD"),
        ("Smart Watch", "GPS, heart rate monitor", "299 USD"),
    ],
    "Clothing": [
        ("Cotton T-Shirt", "Premium organic cotton", "25 USD"),
        ("Slim Fit Jeans", "Stretch denim", "55 USD"),
        ("Bomber Jacket", "Water resistant", "89 USD"),
        ("Running Sneakers", "Breathable mesh", "79 USD"),
        ("Hoodie", "Fleece lined", "45 USD"),
    ],
    "Home & Garden": [
        ("LED Desk Lamp", "Dimmable, USB-C", "35 USD"),
        ("Ergonomic Chair", "Mesh back, lumbar support", "199 USD"),
        ("Ceramic Plant Pot", "Set of 3", "29 USD"),
        ("Tool Set 45pcs", "Chrome vanadium", "49 USD"),
        ("Smart Bulb Kit", "RGB, app controlled", "39 USD"),
    ],
    "Sports": [
        ("Adjustable Dumbbells", "2x 20kg", "149 USD"),
        ("Yoga Mat", "Non-slip, 6mm", "35 USD"),
        ("Resistance Bands Set", "5 levels + handles", "19 USD"),
        ("Protein Powder 1kg", "Whey isolate, chocolate", "45 USD"),
        ("Jump Rope", "Speed rope with bearings", "15 USD"),
    ],
}


if __name__ == "__main__":
    asyncio.run(seed())
