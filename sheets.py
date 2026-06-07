import gspread
from google.oauth2.service_account import Credentials
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheet(spreadsheet_id: str):
    creds_file = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).sheet1

def save_booking(spreadsheet_id: str, data: dict) -> str:
    sheet = get_sheet(spreadsheet_id)
    booking_id = "BK" + datetime.datetime.now().strftime("%d%H%M%S")
    row = [
        booking_id,
        data.get("name", "—"),
        data.get("phone", "—"),
        data.get("date", "—"),
        data.get("time", "—"),
        data.get("service", "—"),
        "pending",
        "واتساب",
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ]
    sheet.append_row(row)
    return booking_id