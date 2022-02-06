import os
from pprint import pprint
import json
import requests as requests
from datetime import date, timedelta

def get_dates_and_values(sourse_str):
    dict_of_dates_and_values = {}
    for day in sourse_str.split('<Record Date=')[1:]:
        dict_of_dates_and_values.update({day[1:11]:
                                             float(day[day.find("<Value>") + len('<Value>'):
                                                       day.find("</Value>")].replace(',', '.'))})
    return dict_of_dates_and_values


def find_min_avr_max(dates_n_values):
    dict_of_min_avr_max = {'min_value': {'Date': list(dates_n_values.keys())[0],
                                         'value': dates_n_values.get(list(dates_n_values.keys())[0])},
                           'avr_value': {'value': dates_n_values.get(list(dates_n_values.keys())[0])},
                           'max_value': {'Date': list(dates_n_values.keys())[0],
                                         'value': dates_n_values.get(list(dates_n_values.keys())[0])}}
    count = 0
    sum_val = 0.0
    for dt, value in dates_n_values.items():
        if value < dict_of_min_avr_max.get('min_value').get('value'):
            dict_of_min_avr_max.update({'min_value': {'Date': dt, 'value': value}})
        if value > dict_of_min_avr_max.get('max_value').get('value'):
            dict_of_min_avr_max.update({'max_value': {'Date': dt, 'value': value}})
        count = count + 1
        sum_val = sum_val + value
    dict_of_min_avr_max.update({'avr_value': {'value': round(sum_val / count, 4)}})
    return dict_of_min_avr_max


def req_VAL_NM_daydelta(Valuta_ID, daydelta):
    DateNow = date.today().strftime("%d/%m/%Y")
    DateFrom = date.today() - timedelta(days=daydelta)
    DateFrom = DateFrom.strftime("%d/%m/%Y")
    url = f'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={DateFrom}&date_req2={DateNow}&VAL_NM_RQ={Valuta_ID}'
    response = requests.get(url)
    return response

def req_VAL_dict():
    res_dict = {}
    url = f"https://www.cbr.ru/scripts/XML_val.asp?d=0"
    response = requests.get(url)
    for val_str in response.text.split('Item ID=')[1:]:
        res_dict.update({val_str[1:7]:
                             {"Name": val_str[val_str.find("<Name>") + len('<Name>'): val_str.find("</Name>")],
                              "EngName": val_str[val_str.find("<EngName>") + len('<EngName>'): val_str.find("</EngName>")],
                              "Nominal": val_str[val_str.find("<Nominal>") + len('<Nominal>'): val_str.find("</Nominal>")],
                              "ParentCode": val_str[val_str.find("<ParentCode>")
                                                    + len('<ParentCode>'): val_str.find("</ParentCode>")].strip()}
                         })
    return res_dict


def make_csv_file(valutes_dict, rez_dict):
    with open('result_csv.csv', 'w') as fp:
        fp.write("ID, Name, EngName, Nominal, min value, min date, avr value, max value, max date\n")
    with open('result_csv.csv', 'a') as f:
        for val_id in rez_dict.keys():
            f.write(val_id + ",")
            f.write(valutes_dict.get(val_id).get('Name') +",")
            f.write(valutes_dict.get(val_id).get('EngName') + ",")
            f.write(valutes_dict.get(val_id).get('Nominal') + ",")
            f.write(str(rez_dict.get(val_id).get('min_value').get('value')) + ",")
            f.write(rez_dict.get(val_id).get('min_value').get('Date') + ",")
            f.write(str(rez_dict.get(val_id).get('avr_value').get('value')) + ",")
            f.write(str(rez_dict.get(val_id).get('max_value').get('value')) + ",")
            f.write(rez_dict.get(val_id).get('max_value').get('Date'))
            f.write("\n")

def gen_human_str(valutes_dict, rez_dict):
    max_name_len = 0
    for val_id in valutes_dict.keys():
        if len(valutes_dict.get(val_id).get('Name')) > max_name_len:
            max_name_len = len(valutes_dict.get(val_id).get('Name'))
    print('Курсs обмена валют за указанный период:')
    for val_id in rez_dict.keys():
        print(
            f" {valutes_dict.get(val_id).get('Name').rjust(max_name_len, ' ') } -  "
            f"минимум ({rez_dict.get(val_id).get('min_value').get('Date')}): "
            f"{(str(rez_dict.get(val_id).get('min_value').get('value'))).ljust(7, '0').rjust(8, ' ')},    "
            f"максимум ({rez_dict.get(val_id).get('max_value').get('Date')}):   "
            f"{(str(rez_dict.get(val_id).get('max_value').get('value'))).ljust(7, '0').rjust(8, ' ')},    "
            f"средний {(str(rez_dict.get(val_id).get('avr_value').get('value'))).ljust(7, '0').rjust(8, ' ')},"
        )


if __name__ == '__main__':
    print(f"Данная программа запросит курсы перевода различных валют в рубли, "
          f"и укажет для каждой валюты минимальное, среднее и максимальное значения.\n"
          f"Результаты будут выведены в консоль, а так же *.json и *.csv файлы.")
    try:
        valutes_dict = req_VAL_dict()
        print("Есть связь с сервером центробанка, запрашиваем данные.")
    except:
        print("Сбой связи с сервером центробанка.")
    rez_dict = {}
    for val_id in valutes_dict.keys():
        try:
            rez_dict.update({val_id: find_min_avr_max(get_dates_and_values(req_VAL_NM_daydelta(val_id, 90).text))})
        except:
            pass
    with open('result_json.json', 'w') as fp:
        json.dump(rez_dict, fp, indent=4)
    make_csv_file(valutes_dict, rez_dict)
    gen_human_str(valutes_dict, rez_dict)
    os.system('pause')
