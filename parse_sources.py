import json
import re
import xml.etree.ElementTree as ET

import pandas as pd

RAW = '..'
OUT = 'data'


def read_forum():
    data = json.load(open(f'{RAW}/FrequentFlyerForum-Profiles.json', encoding='utf8'))
    profiles = []
    flights = []
    for p in data['Forum Profiles']:
        cards = [f"{c['programm']} {c['Number'].strip()}" for c in p['Loyality Programm']]
        profiles.append({
            'nick': p['NickName'],
            'sex': p['Sex'],
            'first': p['Real Name']['First Name'],
            'last': p['Real Name']['Last Name'],
            'passports': ';'.join(p['Travel Documents'][0]['Passports'] or []),
            'cards': ';'.join(cards),
        })
        for f in p['Registered Flights']:
            flights.append({
                'nick': p['NickName'],
                'date': f['Date'],
                'flight': f['Flight'],
                'dep': f['Departure']['Airport'],
                'arr': f['Arrival']['Airport'],
                'dep_country': f['Departure']['Country'],
                'arr_country': f['Arrival']['Country'],
            })
    pd.DataFrame(profiles).to_parquet(f'{OUT}/forum_profiles.parquet')
    pd.DataFrame(flights).to_parquet(f'{OUT}/forum_flights.parquet')


def read_pointz():
    root = ET.parse(f'{RAW}/PointzAggregator-AirlinesData.xml').getroot()
    rows = []
    for user in root:
        name = user.find('name')
        for card in user.iter('card'):
            for a in card.iter('activity'):
                rows.append({
                    'uid': user.get('uid'),
                    'first': name.get('first'),
                    'last': name.get('last'),
                    'card': card.get('number'),
                    'flight': a.findtext('Code'),
                    'date': a.findtext('Date'),
                    'dep': a.findtext('Departure'),
                    'arr': a.findtext('Arrival'),
                    'fare': a.findtext('Fare'),
                })
    pd.DataFrame(rows).to_parquet(f'{OUT}/pointz.parquet')


def read_skyteam():
    rows = []
    current = []
    date = flight = None
    for line in open(f'{RAW}/SkyTeam-Exchange.yaml', encoding='utf8'):
        m_date = re.match(r"'(\d{4}-\d\d-\d\d)':", line)
        m_flight = re.match(r'  (\w+):$', line)
        m_card = re.match(r'      (\w\w \d+): \{CLASS: (\w), FARE: (\w+)\}', line)
        m_from = re.match(r'    FROM: (\w+)', line)
        m_to = re.match(r'    TO: (\w+)', line)
        if m_date:
            date = m_date[1]
        elif m_flight:
            flight = m_flight[1]
        elif m_card:
            current.append({'date': date, 'flight': flight, 'card': m_card[1], 'cls': m_card[2], 'fare': m_card[3]})
        elif m_from:
            for r in current:
                r['dep'] = m_from[1]
        elif m_to:
            for r in current:
                r['arr'] = m_to[1]
            rows += current
            current = []
    pd.DataFrame(rows).to_parquet(f'{OUT}/skyteam.parquet')


def read_sirena():
    cols = {
        'name': (0, 60), 'birth': (60, 72), 'date': (72, 84), 'time': (84, 96),
        'arr_date': (96, 108), 'arr_time': (108, 120), 'flight': (120, 126), 'codeshare': (126, 132),
        'dep': (132, 138), 'arr': (138, 144), 'pnr': (144, 150), 'ticket': (150, 168),
        'doc': (168, 180), 'seat': (180, 186), 'meal': (186, 192), 'cls': (192, 198),
        'fare': (198, 204), 'baggage': (204, 216), 'info': (216, 276), 'agent': (276, 336),
    }
    df = pd.read_fwf(f'{RAW}/Sirena-export-fixed.tab', colspecs=list(cols.values()), names=list(cols),
                     skiprows=1, dtype=str, encoding='utf8')
    df['card'] = df['info'].str.extract(r'FF#(\w\w \d+)')[0]
    df = df.drop(columns='info')
    df.to_parquet(f'{OUT}/sirena.parquet')


read_forum()
read_pointz()
read_skyteam()
read_sirena()
print('ok')
