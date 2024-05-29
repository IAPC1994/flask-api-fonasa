
def tupleToArrayDict(column_names, data):
    arr = []
    for row in data:
        row_dict = dict(zip(column_names, row))
        arr.append(row_dict)
    return arr