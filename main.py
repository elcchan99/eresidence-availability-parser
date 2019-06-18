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
    if table.shape[1] == 11:
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
    vacant_1 = [[0 for i in range(8)] for i in range(37)]
    with open('tower1.txt') as t1:
        for line in t1:
            floor = int(line.rstrip()[:-1])
            block = ord(line.rstrip()[-1:]) - 65
            vacant_1[floor][block] = 1

    vacant_2 = [[0 for i in range(10)] for i in range(37)]
    with open('tower2.txt') as t2:
        for line in t2:
            floor = int(line.rstrip()[:-1])
            block = ord(line.rstrip()[-1:]) - 65
            vacant_2[floor][block] = 1

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
        t1_start = 'B2'
        t1_row = len(vacant[0])
        t1_col = len(vacant[0][0])
        t1_end = chr(ord(t1_start[0]) + t1_col) + str(int(t1_start[1]) + t1_row)
        t2_start = chr(ord(t1_end.split(':')[0][0]) + 1) + '2'
        t2_row = len(vacant[1])
        t2_col = len(vacant[1][0])
        t2_end = chr(ord(t2_start[0]) + t2_col) + str(int(t2_start[1]) + t2_row)
        update_sheet(service, f'{t1_start}:{t1_end}', vacant[0])
        update_sheet(service, f'{t2_start}:{t2_end}', vacant[1])

