import glob
import re
import sys
import zipfile
from multiprocessing import Pool

import pandas as pd

CELLS = {
    'A3': 'title',
    'B3': 'name',
    'H3': 'cls',
    'A5': 'flight',
    'D7': 'dep',
    'H7': 'arr',
    'A9': 'date',
    'C9': 'time',
    'H11': 'seat',
    'B13': 'pnr',
    'E13': 'ticket',
}


def read_strings(z):
    xml = z.read('xl/sharedStrings.xml').decode()
    items = re.findall(r'<si>(.*?)</si>', xml, re.S)
    return [''.join(re.findall(r'<t[^>]*>(.*?)</t>', item, re.S)) for item in items]


def read_file(path):
    z = zipfile.ZipFile(path)
    strings = read_strings(z)
    rows = []
    for name in z.namelist():
        if not name.startswith('xl/worksheets/sheet'):
            continue
        xml = z.read(name).decode()
        row = {}
        for col, num, is_str, value in re.findall(r'<c r="([A-H])(\d+)"( t="s")?[^>]*><v>(.*?)</v></c>', xml):
            key = CELLS.get(col + num)
            if key:
                row[key] = strings[int(value)] if is_str else value
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == '__main__':
    files = sorted(glob.glob(sys.argv[1] + '/*.xlsx'))
    with Pool() as pool:
        tables = pool.map(read_file, files)
    df = pd.concat(tables, ignore_index=True)
    df.to_csv(sys.argv[2], index=False)
    print(df.shape)
