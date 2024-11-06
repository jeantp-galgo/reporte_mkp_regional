import gspread
from oauth2client.service_account import ServiceAccountCredentials

def conectarse_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_sheet/key-google-sheets.json', scope)

    return gspread.authorize(creds)