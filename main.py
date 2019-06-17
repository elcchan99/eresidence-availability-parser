import sys
import camelot
import csv

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1GvzNnqIsr06iV7JaXeL-FjGiJu4R72ENPf9yAQ9i89o'
SHEET_NAME = 'availability'

def construct(vacant, table):
    if table.shape == (12, 11):
        df = table.df
        tower = df[3][4:].to_list()
        floor = df[4][4:].to_list()
        flat = df[5][4:].to_list()
        for i in range(len(tower)):
            tower_number = 0 if tower[i] == 'Tower 1\n第一座' else 1
            floor_number = int(floor[i][:-2])
            flat_number = ord(flat[i]) - 65
            vacant[tower_number][floor_number][flat_number] = 2
    return vacant


def build_vacant():
    # 0 stands for not for sale, 1 for vacant, 2 for sold
    vacant_1 = [[1 for i in range(8)] for i in range(37)]
    # no such floors
    for item in [0, 1, 2, 3, 4, 14, 24, 34]:
        vacant_1[item] = [0 for i in range(8)]
    vacant_2 = [[1 for i in range(10)] for i in range(37)]
    for i, ele in enumerate(vacant_2[:]):
        # not for sold
        ele[6] = 0
        vacant_2[i] = ele
    for item in [0, 1, 2, 3, 4, 14, 24, 34]:
        vacant_2[item] = [0 for i in range(10)]
    return [vacant_1, vacant_2]


def write_csv(filename, vacant):
    with open(filename, 'w+') as t1:
        csvWriter = csv.writer(t1, delimiter=',')
        csvWriter.writerows(vacant)


def login_google():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def update_sheet(service, shtRange, data):
    data.reverse()
    values = data
    print(f'total row: {len(values)}')
    print(f'total col: {len(values[0])}')
    valRange = f'{SHEET_NAME}!{shtRange}'
    body = {'values': values, 'majorDimension': 'ROWS', 'range': valRange}

    print(f'range {valRange}')
    # print(f'body {body}')
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=valRange,
        valueInputOption='RAW',
        body=body
    ).execute()
    print(f'result {result}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "test.pdf"

    if len(sys.argv) > 2 and sys.argv[2] in ['csv', 'sheet']:
        mode = sys.argv[2]
    else:
        mode = 'csv'

    print(f"file: {file}")
    print(f"mode: {mode}")

    from_pdf = (".pdf" in file)
    if from_pdf: 
        print('parsing PDF...')
        parsed = camelot.read_pdf('./{}'.format(file), pages='all')
        print('massaging data...')
        vacant = build_vacant()
        for item in parsed:
            vacant = construct(vacant, item)
    else:
        vacant = []
        with open('tower1.csv') as t1:
            vacant.append([r for r in csv.reader(t1, delimiter=',')])
        with open('tower2.csv') as t2:
            vacant.append([r for r in csv.reader(t2, delimiter=',')])

    if mode == 'csv':
        write_csv('tower1.csv', vacant[0])
        write_csv('tower2.csv', vacant[1])
    else:
        print(f'logging into google...')
        creds = login_google()
        service = build('sheets', 'v4', credentials=creds)

        print(f'updating google sheet...')
        update_sheet(service, 'B2:I38', vacant[0])
        update_sheet(service, 'K2:T38', vacant[1])

