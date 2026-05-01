import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google API setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("Attendance").sheet1


def mark_attendance(name, time, date):
    sheet.append_row([name, time, date])