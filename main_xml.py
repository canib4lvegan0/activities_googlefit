import os
import xml.etree.ElementTree as ET
from decimal import Decimal

ROOT_PATH = 'Takeout/Fit/Atividades'

TotalTimeTag = '{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}TotalTimeSeconds'

# def extract_name(n: str) -> str:
#     return n.split('_')[5].lower().split('.')[0].split(',')[0].split(' ')[0]


def scan_xml_file(path_file):
    tree = ET.parse(path_file)
    activities = tree.getroot()[0]

    data = {
        'name': path_file.split('/')[-1],
        'datetime': '',
        'sport': '',
        'duration': 0,
    }

    for activity in activities:
        try:
            data['sport'] = activity.attrib['Sport']
        except AttributeError:
            pass

        try:
            data['datetime'] = activity[0].text
        except AttributeError:
            pass

        try:
            for tag in activity[1].findall(TotalTimeTag):
                if Decimal(tag.text) > 2_400:
                    data['duration'] = Decimal(tag.text)
        except AttributeError:
            pass

    return data


def map_files(path_dir):
    files = tuple(os.scandir(path_dir))
    total_files = len(files)
    mapped = 0

    for f in files:
        mapped += 1
        print(f'Mapping file {f.name}... \t\t{mapped} de {total_files}')
        yield scan_xml_file(f'{ROOT_PATH}/{f.name}')


if __name__ == '__main__':
    ds = tuple(map_files(ROOT_PATH))

    """ Set of practiced sports """
    ds_sports = {act['sport'] for act in ds}
    # print(f'\nSports -> {ds_sports}\n')

    """ Activities by sports """
    ds_by_sport = dict.fromkeys(ds_sports, 0)
    for act in ds:
        ds_by_sport[act['sport']] = ds_by_sport[act['sport']] + 1
    # print(f'Activities by -> {ds_by_sport}\n')

    """ Activities by year (2021) """
    ds_by_year = tuple(filter(lambda act: act['datetime'][:4:] == '2021', ds))
    # print(f'Count activities by year (2021) -> {len(ds_by_year)}')
    # print(f'Activities by year (2021) -> {ds_by_year}\n')

    """ Activities by duration (>= 2400s) """
    ds_by_duration = tuple(filter(lambda act: act['duration'] >= 2_400, ds_by_year))
    # print(f'Count activities in 2021 with > 2400s duration-> {len(filtered_duration)}\n')
    # print(f'Number of activities by duration (>= 2400s)-> {len(ds_by_duration)}')
    # for act in ds_by_duration:
    #     print(f"{act['datetime'][:10:]}\t\t{act['sport']}\t\t{act['duration']}")

    """ Activities sorted by date """
    ds_sorted_date = sorted(ds_by_duration, key=lambda act: act['datetime'])
    # print(f'Activities sorted by date')
    # for act in ds_sorted_date:
    #     print(f"{act['datetime'][:10:]}\t\t{act['sport']}\t\t{act['duration']}")

    """ Activities classified by month """
    ds_months = list({act['datetime'][:7:] for act in ds_sorted_date})
    ds_months.sort()
    months = dict.fromkeys(ds_months, 0)
    for act in ds_sorted_date:
        months[act['datetime'][:7:]] = months[act['datetime'][:7:]] + 1
    print(f'Activities classified by month -> {months}\n')
