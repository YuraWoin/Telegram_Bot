import logging
import asyncio
from google_sheets import append_booking, SHEET_ID

logging.basicConfig(level=logging.INFO)

asyncio.run(append_booking(SHEET_ID, 123, "test_user", "Тест", "+380501234567",
                           "Майстер", "Стрижка", "2026-10-20", "12:00"))