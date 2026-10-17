import os
import json
import asyncio
import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = "credentials.json"
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
HEADERS = ["ID", "Username", "Name", "Phone", "Master", "Service", "Date", "Time", "Created At"]

_client = None
_ready_sheets: set[str] = set()


def get_client():
    global _client
    if _client is None:
        if os.path.exists(CREDENTIALS_FILE):
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        else:
            creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if not creds_json:
                raise FileNotFoundError("Не знайдено ні credentials.json, ні змінної середовища GOOGLE_CREDENTIALS_JSON")
            creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def get_worksheet(sheet_id: str, name: str = "Bookings"):
    spreadsheet = get_client().open_by_key(sheet_id)
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=1000, cols=len(HEADERS))

    if sheet_id not in _ready_sheets:
        if not ws.row_values(1):
            ws.append_row(HEADERS, value_input_option="RAW")
            ws.format("A1:I1", {"textFormat": {"bold": True}})
        _ready_sheets.add(sheet_id)
    return ws


# ---------- Один запис ----------

def _append_booking(sheet_id, tg_id, username, name, phone, master, service, date, time):
    ws = get_worksheet(sheet_id)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [tg_id, username or "", name, phone, master, service, date, time, created_at]
    ws.append_row(row, value_input_option="RAW")


async def append_booking(sheet_id: str, tg_id: int, username: str, name: str,
                         phone: str, master: str, service: str, date: str, time: str):
    """Не кидає виняток: збій таблиці не ламає запис клієнта."""
    try:
        await asyncio.to_thread(
            _append_booking, sheet_id, tg_id, username, name, phone, master, service, date, time
        )
    except Exception:
        log.exception("Google Sheets append failed (sheet_id=%s)", sheet_id)


# ---------- Повна синхронізація ----------

def _s(v):
    return "" if v is None else str(v)


def _sync_all(sheet_id: str, rows: list[list]):
    ws = get_worksheet(sheet_id)
    ws.clear()
    ws.update(range_name="A1", values=[HEADERS] + rows, value_input_option="RAW")
    ws.format("A1:I1", {"textFormat": {"bold": True}})


async def sync_all_appointments(get_all_appointments_func, sheet_id: str) -> int:
    appointments = await get_all_appointments_func()
    rows = [
        [
            _s(getattr(a, "tg_id", getattr(a, "id", ""))),
            _s(getattr(a, "username", "")),
            _s(getattr(a, "name", "")),
            _s(getattr(a, "phone", "")),
            _s(getattr(a, "master", "")),
            _s(getattr(a, "service", "")),
            _s(getattr(a, "date", "")),
            _s(getattr(a, "time", "")),
            _s(getattr(a, "created_at", "")),
        ]
        for a in appointments
    ]
    await asyncio.to_thread(_sync_all, sheet_id, rows)
    return len(rows)
