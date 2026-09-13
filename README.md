# 🤖 Telegram Business Bot — ShablonYuStack

A universal Telegram bot for businesses: beauty salons, barbershops, auto repair shops (STO), cafes, online stores. Clients book appointments, order food, buy products — all in one bot. Admin panel with Google Sheets sync.

---

## 🧪 Try the Bot

Want to see it in action before setting anything up? Open the demo bot in Telegram and try the menus yourself:

https://t.me/ShablonYuStackBot

Send `/start` and walk through Price List, Booking, Order Food, or Shop to get a feel for the flow before customizing it for your own business.

---

## ✨ Features

### For Clients
| Command / Button | What It Does |
|---|---|
| 💳 **Price List** | Browse categories, subcategories, and prices for services/products |
| 📅 **Booking** | Book a master (beauty/barber) — choose master → category → service → date → time |
| 🔧 **STO Booking** | Book auto service — choose mechanic → work category → service → date → time |
| 🍽 **Order Food** | Order from cafe menu — choose category → dish → name + phone |
| 🛒 **Shop** | Online store — browse products → cart (+/- quantity) → checkout (name, phone, address) |
| ⭐ **Reviews** | Link to Instagram for reviews |
| ℹ️ **About** | Info about the business |

### For Admins
| Command | What It Does |
|---|---|
| `/admin` | Enter admin panel (only for IDs from `.env`) |
| 📋 All bookings | View all bookings/orders with delete option |
| 💰 Change price | Change price for any service/product |
| ➕ Add service | Add new service/product to DB |
| 🗑 Delete service | Remove service/product |
| 🔄 Sync to Sheets | Manual sync of all bookings to Google Sheet |

### Automation
- ✅ New bookings auto-saved to **SQLite/PostgreSQL**
- ✅ New bookings auto-pushed to **Google Sheets**
- ✅ Admins get notified about every new booking/order
- ✅ Cart works in-memory, clears after checkout

---

## 🛠 Tech Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot API
- **SQLAlchemy 2.x + aiosqlite** — ORM and async DB
- **python-dotenv** — environment variables
- **gspread** — Google Sheets integration
- **Docker** — containerization

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YuraWoin/Telegram_Bot.git
cd Telegram_Bot
```

### 2. Get your bot token
Talk to [@BotFather](https://t.me/BotFather) on Telegram, create a new bot, and copy the token it gives you.

### 3. Configure environment variables
Copy the example env file and fill in your own values:
```bash
cp .env.example .env
```
Then open `.env` and set:
```
BOT_TOKEN=your_token_from_botfather
ADMIN_IDS=123456789,987654321
GOOGLE_SHEET_ID=your_google_sheet_id
```

---

## ▶️ Option A — Run Locally (no Docker)

```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                # seed the DB with categories/items
python main.py                # start the bot
```

## 🐳 Option B — Run with Docker

**Build the image:**
```bash
docker build -t telegram_bot .
```

**Run the container**, passing your token and other secrets as environment variables (don't hardcode them in the Dockerfile):
```bash
docker run -d --name my_telegram_bot \
  -e BOT_TOKEN=your_token_from_botfather \
  -e ADMIN_IDS=123456789,987654321 \
  -e GOOGLE_SHEET_ID=your_google_sheet_id \
  telegram_bot
```

**Or, simpler — use Docker Compose**, which reads variables straight from your `.env` file:
```bash
docker-compose up -d --build
```

To check logs or stop the bot:
```bash
docker logs -f my_telegram_bot
docker stop my_telegram_bot
```

---

## 📁 Project Structure

```
telegram_bot/
├── .env                      # Environment variables (do not commit!)
├── .env.example              # Template for required env vars
├── .gitignore
├── credentials.json          # Google Cloud key (do not commit!)
├── db.sqlite3                # Database (if SQLite)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── main.py                   # Entry point
├── seed.py                   # Seed DB with categories and items
├── README.md                 # This file
├── image/                    # Stickers, photos for bot
│   ├── sticker.webp
│   └── photo_2026-02-21_17-02-34.jpg
└── app/
    ├── __init__.py
    ├── handlers.py           # All bot handlers
    ├── keyboard.py           # Keyboards
    ├── info.py               # "About" texts
    ├── middlewsres.py        # Middleware
    ├── google_sheets.py      # Google Sheets integration
    └── database/
        ├── __init__.py
        ├── models.py         # SQLAlchemy models
        └── requests.py       # DB queries
```

---

## 🔧 Customize for Your Business

### 1. Replace Categories and Items
Open `seed.py`, find the `CATEGORIES` and `ITEMS` sections — replace with your own. Then run:
```bash
python seed.py
```

### 2. Replace Masters / Mechanics
Open `handlers.py`, find these dicts:
- `MASTER_CATEGORIES` — for beauty/barbershop
- `STO_MASTERS` — for auto repair

### 3. Replace Texts and Photos
- `app/info.py` — "About" text
- `image/` — replace sticker and photo with yours
- `handlers.py` — Instagram link in the `vidguk` handler

### 4. Google Sheets
1. Create a Google Sheet.
2. Share it with the service account email (found in `credentials.json`).
3. Copy the sheet ID from the sheet's URL and paste it into `.env` as `GOOGLE_SHEET_ID`.

---

## 📝 License

```
MIT License

Copyright (c) 2026 Yura Woin / ShablonYuStack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> ⚠️ **Copyright:** This code is the intellectual property of **Yura Woin / ShablonYuStack**. When using, forking, or modifying, keep the original authorship and a link to the repository. Commercial use by third parties without the author's written consent is prohibited.

---

## 👤 Contacts

- **Author:** YuraWoin
- **Project:** [Telegram_Bot](https://github.com/YuraWoin/Telegram_Bot.git)
- **Instagram:** @your_business_handle

---

*Built with ❤️ by junior dev under team lead supervision*
