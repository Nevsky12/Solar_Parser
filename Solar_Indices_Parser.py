import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
import os


def get_html(url: str):
    r = requests.get(url)
    return r.text


def get_all_links(html: str, url: str):
    soup = BeautifulSoup(html, 'lxml')
    link = url
    file_links = set()

    tds = soup.find('table').find_all('td')

    for td in tds:
        file_link = td.findNext('a')
        if file_link is not None:
            result_link = file_link.get('href')
            if result_link == 'SOLFSMY.TXT' or result_link == 'SOLRESAP.TXT':
                file_links.add(result_link)

    for file_linkers in file_links:
        get_file = requests.get(f"{link}{file_linkers}").content
        with open(f"{file_linkers}", 'wb') as result_file:
            result_file.write(get_file)


def create_data_for_res_file(current_line_flux: List[str], current_line_magnitude: List[str]):
    return current_line_flux[2] + ',' + current_line_magnitude[3] + ',' + current_line_magnitude[4] + ',' + \
           current_line_magnitude[5] + ',' + current_line_magnitude[6] + ',' + current_line_magnitude[7] + ',' + \
           current_line_magnitude[8] + ',' + current_line_magnitude[9] + ',' + current_line_magnitude[10] + ',' + \
           current_line_flux[3] + ',' + current_line_flux[4] + ',' + current_line_flux[5] + ',' + \
           current_line_flux[6] + ',' + current_line_flux[7] + ',' + current_line_flux[8] + '\n'


def make_csv_for_JB2006(start_date: datetime, end_date: datetime, csv_name='jachnia_si.csv'):
    with open("SOLFSMY.TXT", 'r', encoding='utf-8') as SOLFMY_file, open("SOLRESAP.TXT", 'r',
                                                                         encoding='utf-8') as SOLRESAP_file, open(
        csv_name, 'w'):

        for i in range(4):
            SOLFMY_file.readline()
            SOLRESAP_file.readline()
        for i in range(23):
            SOLRESAP_file.readline()

        current_line_flux = SOLFMY_file.readline()

        index_birth_date = datetime(year=int(current_line_flux[2:6]), month=1, day=1)
        index_now_date = datetime.today()
        if start_date < index_birth_date or end_date > index_now_date:
            raise Exception(
                "Даты не попадают в допустимый диапазон от: " + str(index_birth_date) + " до: " + str(index_now_date))
        if start_date > end_date:
            raise Exception("Начальная дата больше конечной")

        start_date_delta = (start_date - index_birth_date).days

        current_line_flux = current_line_flux.split()
        current_line_magnitude = SOLRESAP_file.readline().split()

        for i in range(start_date_delta):
            current_line_flux = SOLFMY_file.readline().split()
            current_line_magnitude = SOLRESAP_file.readline().split()

        try:
            with open("jachnia_lala.csv", 'w') as result_file:
                result_file.write('jd,ap1,ap2,ap3,ap4,ap5,ap6,ap7,ap8,F10,F81,S10,S10B,XM10,XM10B\n')
                result_file.write(create_data_for_res_file(current_line_flux, current_line_magnitude))

                end_date_delta = (end_date - start_date).days
                for i in range(end_date_delta):
                    current_line_flux = SOLFMY_file.readline().split()
                    current_line_magnitude = SOLRESAP_file.readline().split()
                    result_file.write(create_data_for_res_file(current_line_flux, current_line_magnitude))
        except FileNotFoundError:
            print("Файла больше нет!")


def main():
    url = 'https://sol.spacenvironment.net/jb2008/indices/'
    get_all_links(get_html(url), url)
    make_csv_for_JB2006(datetime(year=2017, month=1, day=1), datetime(year=2022, month=4, day=5), 'jachnia_lala.csv')

    path_MY = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'SOLFSMY.TXT')
    path_AP = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'SOLRESAP.TXT')
    os.remove(path_MY)
    os.remove(path_AP)


if __name__ == '__main__':
    main()
