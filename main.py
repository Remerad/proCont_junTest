from pprint import pprint
from json import dumps
import requests as requests
from xmljson import badgerfish as bf
from datetime import date, timedelta

def get_average_value(sourse_str):
    list_of_rec = []
    for day in sourse_str.split('Id="R01235"><Nominal>1</Nominal>'):
        if day.startswith("<Value>"):
            print(day)
            list_of_rec.append(
                {float(day[day.find("<Value>")+len('<Value>'):day.find("</Value>")].replace(',', '.')):
                 day[day.find("Date=\"")+len("Date=\""):-2]}
            )
    if len(list_of_rec) > 1:
        list_of_rec[-1].update(
            {list(list_of_rec[-1].keys())[0]:
             date.today().strftime("%d.%m.%Y")}
        )

    return list_of_rec


if __name__ == '__main__':
    DateNow = date.today().strftime("%d/%m/%Y")
    DateFrom = date.today() - timedelta(days=61)
    DateFrom = DateFrom.strftime("%d/%m/%Y")
    url = f'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={DateFrom}&date_req2={DateNow}&VAL_NM_RQ=R01235'
    response = requests.get(url)
    pprint(get_average_value(response.text))
    #'http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=05/12/2021&date_req2=05/02/2022&VAL_NM_RQ=R01235'


