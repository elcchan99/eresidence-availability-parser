import camelot
import csv

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
    # 0 stands for not for sale, 1 for vacant, 2 for saled
    vacant_1 = [[1 for i in range(8)] for i in range(37)]
    for item in [0, 1, 2, 3, 4, 14, 24, 34]:
        vacant_1[item] = [0 for i in range(8)]
    vacant_2 = [[1 for i in range(10)] for i in range(37)]
    for i, ele in enumerate(vacant_2):
        ele[8] = 0
        vacant_2[i] = ele
    for item in [0, 1, 2, 3, 4, 14, 24, 34]:
        vacant_2[item] = [0 for i in range(10)]
    return [vacant_1, vacant_2]

if __name__ == '__main__':
    parsed = camelot.read_pdf('./test.pdf', pages='all')
    vacant = build_vacant()
    for item in parsed:
        vacant = construct(vacant, item)
    with open('tower1.csv', 'w+') as t1:
        csvWriter = csv.writer(t1, delimiter=',')
        csvWriter.writerows(vacant[0])
    with open('tower2.csv', 'w+') as t2:
        csvWriter = csv.writer(t2, delimiter=',')
        csvWriter.writerows(vacant[1])
