import camelot


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
            print("%s, %s, %s" % (tower_number, floor_number, flat_number))
            vacant[tower_number][floor_number][flat_number] = False
    return vacant

def build_vacant():
    vacant_1 = [[True for i in range(8)] for i in range(37)]
    for item in [0, 1, 2, 3, 4, 14, 24, 34]:
        vacant_1[item] = []
    vacant_2 = [[True for i in range(10)] for i in range(37)]
    for i, ele in enumerate(vacant_2):
        ele[8] = False
        vacant_2[i] = ele
    for item in [0, 1, 2, 3, 4, 14, 24, 34]:
        vacant_2[item] = []
    return [vacant_1, vacant_2]

if __name__ == '__main__':
    parsed = camelot.read_pdf('./test.pdf', pages='all')
    vacant = build_vacant()
    for item in parsed:
        vacant = construct(vacant, item)
    print(vacant)
