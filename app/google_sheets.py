"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026

This code is provided for viewing and personal use only.
Do not redistribute or claim authorship. See LICENSE for terms.
"""
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Scopes for Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Path to service account JSON key
CREDENTIALS_FILE = "credentials.json"
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Alternative: load credentials from env variable as JSON string
# GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")


def get_client():
    """Returns authorized gspread client."""
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    else:
        # Fallback: read from env variable
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not creds_json:
            raise FileNotFoundError(
                "Neither credentials.json nor GOOGLE_CREDENTIALS_JSON env var found."
            )
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)


def get_worksheet(sheet_id: str, worksheet_name: str = "Bookings"):
    """Returns a specific worksheet by name. Creates if not exists."""
    client = get_client()
    spreadsheet = client.open_by_key(sheet_id)

    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="10")


def ensure_headers(worksheet):
    """Checks headers, creates them if sheet is empty."""
    headers = ["ID", "Username", "Name", "Phone", "Master", "Service", "Date", "Time", "Created At"]
    existing = worksheet.row_values(1)
    if not existing:
        worksheet.append_row(headers)
        worksheet.format("A1:I1", {"textFormat": {"bold": True}})


def append_booking(tg_id: int, username: str, name: str, phone: str,
                   master: str, service: str, date: str, time: str):
    """
    Appends one booking row to the end of Google Sheet.
    Called from handlers.py after successful booking.
    """
    ws = get_worksheet(SHEET_ID, "Bookings")
    ensure_headers(ws)

    from datetime import datetime
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [tg_id, username or "", name, phone, master, service, date, time, created_at]
    ws.append_row(row, value_input_option="USER_ENTERED")


async def sync_all_appointments(get_all_appointments_func):
    """
    Full sync of all DB appointments into Google Sheets.
    Pass your rq.get_all_appointments coroutine here.
    """
    appointments = await get_all_appointments_func()

    ws = get_worksheet(SHEET_ID, "Bookings")
    ensure_headers(ws)

    # Clear old data (keep headers)
    ws.clear()
    ensure_headers(ws)

    rows = []
    for a in appointments:
        rows.append([
            getattr(a, 'tg_id', getattr(a, 'id', '')),
            getattr(a, 'username', '') or "",
            getattr(a, 'name', ''),
            getattr(a, 'phone', ''),
            getattr(a, 'master', ''),
            getattr(a, 'service', ''),
            getattr(a, 'date', ''),
            getattr(a, 'time', ''),
            getattr(a, 'created_at', ''),
        ])

    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")
    return len(rows)
