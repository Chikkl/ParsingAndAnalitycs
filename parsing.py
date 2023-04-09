import requests
from fake_useragent import UserAgent
import json
import time
import os
from socket import error as SocketError
import errno


def get_time(t = time.localtime()):
    """Возвращает текущее время"""
    current_time = time.strftime("%H : %M : %S", t)
    return current_time

print(get_time())

# ЗАДАЧИ
# Записывать какой-то параметр для того, чтобы не перезаписывать всё с нуля, а начинать с уже известного
# TimeoutError: [Errno 110] Connection timed out нужно починить
# exceptions.ReadTimeoutError: HTTPSConnectionPool(host='api.hh.ru', port=443): Read timed out. (read timeout=None) 

ua = UserAgent()

headers = {
    "useragent":ua.random,
}

def get_areas_ru() -> list:
    req = requests.get('https://api.hh.ru/areas', headers=headers)
    req.close()
    js_obj = json.loads(req.content.decode())
    areas = []
    for element in js_obj:
        for i in range(len(element['areas'])):
            if element['areas'][i]["parent_id"] == '113':                     # Проверка на принадлежность стране
                if len(element['areas'][i]['areas']) != 0:                      # Если у зоны есть внутренние зоны
                    areas.append([element['areas'][i]['id'],
                                  element['areas'][i]['name']])
                    # for j in range(len(element['areas'][i]['areas'])):
                        # areas.append([element['areas'][i]['areas'][j]['id'],
                        #              element['areas'][i]['areas'][j]['name']])
                # else:                                                                # Если у зоны нет внутренних зон
                #     areas.append([element['areas'][i]['id'],
                #                  element['areas'][i]['name']])
    return areas


areas = get_areas_ru()

professional_roles = ['156', '160', '10', '12', '150', '25', '165', '34', '36', '73', '155', '96',
                              '164', '104', '157', '107', '112', '113', '148', '114', '116', '121', '124', '125', '126']


all_need_roles = ('156', '160', '10', '12', '150', '25', '165', '34', '36', '73', '155', '96',
                              '164', '104', '157', '107', '112', '113', '148', '114', '116', '121', '124', '125', '126')

def get_vacaniec_per_page(page:int = 0, area:str = '1', prof_role:str = '156') -> list:
    params={
        "area":area,
        "professional_role":prof_role,
        "only_with_salary":True,
        "page":page,
        "employment":("full", "part","probation"),
        "experience":("noExperience", "between1And3", "between3And6", "moreThan6"),
        "per_page":100
    }

    req = requests.get('https://api.hh.ru/vacancies/', params, headers=headers)
    data = req.content.decode()
    req.close()
    return data

def get_vacancie_from_page(id:str, list_with_t:list) -> list:
    ''' Функция для получения определённой вакансии по её id'''
    for _ in range(5):
        try:
            req = requests.get(f'https://api.hh.ru/vacancies/{id}', headers=headers)
            return req
        except Exception as e:
            print(f"Не удалось получить вакансию - 'https://hh.ru/vacancy/{id}'")
            list_with_t.append(f"[{req.status_code}] Не удалось получить вакансию - {id} ('https://hh.ru/vacancy/{id}')")


            with open('trabl.json', "w", encoding="utf-8") as f:
                        json.dump(list_with_t, f, indent=4, ensure_ascii=False)
            
            time.sleep(3)
    return 

# Добавить проверку получаемых типов данных (?Вывод получаемого значения?)
# Сделать перед циклом трай эксепт и 

all_trabl = []

def vacancies_saver(page: int, area: list, role: str) -> None:
    js_objs = []

    js_obj = json.loads(get_vacaniec_per_page(page, area[0], role))
    for i in range(len(js_obj["items"])):
                    
                    id = js_obj["items"][i]["id"]

                    req = get_vacancie_from_page(id, all_trabl)

                    if req:
                        
                        obj = json.loads(req.content.decode())

                        vacanies = {
                            "id":obj["id"],
                            "premium":obj["premium"],
                            "name":obj["name"],
                            "area":obj["area"],
                            "salary":obj["salary"],
                            "type":obj["type"],
                            "address":obj["address"],
                            "experience":obj["experience"],
                            "schedule":obj["schedule"],
                            "employment":obj["employment"],
                            "department":obj["department"],
                            "contacts":obj["contacts"],
                            "key_skills":obj["key_skills"],
                            "professional_roles":obj["professional_roles"],
                            "employer":obj["employer"],
                            "url":obj["alternate_url"],
                            "published_at":obj["published_at"],
                            "working_days":obj["working_days"],
                            "working_time_intervals":obj["working_time_intervals"],
                            "working_time_modes":obj["working_time_modes"]
                        }

                        js_objs.append(vacanies)
                        req.close()
                        
                        time.sleep(0.6)
                    else:
                         continue

    if not os.path.exists('./areas/'):
            os.makedirs('./areas/')

    nextFileName = './areas/{}.json'.format(str(area[1])+'_'+str(page))

    with open(nextFileName, "w", encoding="utf-8") as f:
                        json.dump(js_objs, f, indent=4, ensure_ascii=False)

    if (js_obj["pages"] - page) <= 1:
        return


total_vacaniec = 0
area_list_id = 0

for area in areas:
    vac = json.loads(get_vacaniec_per_page(0, area[0], all_need_roles))
    count_vacaniec = vac['found']
    pages = vac['pages']
    appended = 0
    print('[{0}/{1}] Область: {2} ({3}) - Вакансий: {4}'.format(area_list_id, len(areas), area[1], area[0], count_vacaniec))
    
    if count_vacaniec > 2000:
        for role in professional_roles:
            for page in range(pages):

                vacancies_saver(page, area, role)
                time.sleep(0.5)
    else:
        role = all_need_roles
        for page in range(pages):
            vacancies_saver(page, area, role)
            time.sleep(0.5)

    area_list_id+=1
    total_vacaniec+=count_vacaniec


    if count_vacaniec != 0:
        print(f"Добавленно {count_vacaniec} вакансий")

print(f"Вакансии собраны, всего {total_vacaniec}", end="\n\n")
# print(get_time())

