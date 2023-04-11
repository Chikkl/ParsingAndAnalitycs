import requests
from fake_useragent import UserAgent
import json
import time
import os
from socket import error as SocketError


ua = UserAgent()

headers = {
    "useragent":ua.random,
}

class ParserRU():
    """Класс представляет необходимый набор функционала для сбора данных через API с сайта hh.ru
    Каждая функция содержит краткое описание того, что она делает."""
    
    PROFESSIONAL_ROLES = ['156', '160', '10', '12', '150', '25', '165', '34', '36', '73', '155', '96',
                              '164', '104', '157', '107', '112', '113', '148', '114', '116', '121', '124', '125', '126']
    ALL_NEED_ROLES = ('156', '160', '10', '12', '150', '25', '165', '34', '36', '73', '155', '96',
                              '164', '104', '157', '107', '112', '113', '148', '114', '116', '121', '124', '125', '126')
    EXP = ["noExperience", "between1And3", "between3And6", "moreThan6"]

    @staticmethod
    def get_time(t = time.localtime()) -> str:
        """Функция возвращает текущее время"""
        current_time = time.strftime("%H : %M : %S", t)
        return current_time

    @staticmethod
    def get_areas() -> list:
        """Функция для получения всех зон для парсинга (включает в себя все субъекты РФ и два города федерального значения [Москва, Санкт-Петербург])"""
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
                    # else:                                                                # Если у зоны нет внутренних зон
                    #     areas.append([element['areas'][i]['id'],
                    #                   element['areas'][i]['name']])
        return areas

    @staticmethod
    def get_vacancies_per_page(page:int = 0, area:str = '1', prof_role:str = '156', exp = ("noExperience", "between1And3", "between3And6", "moreThan6")) -> list:
        """Функция для получения всех вакансий с определённой страницы"""
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

    @staticmethod
    def get_vacancies_with_specific_id(id:str, list_with_t:list, retry:int=5) -> list:
        ''' Функция для получения определённой вакансии по её id'''
        try:
            req = requests.get(f'https://api.hh.ru/vacancies/{id}', headers=headers)
        except Exception as ex:
            if retry:
                print(f"Не удалось получить вакансию - 'https://hh.ru/vacancy/{id}'")
                list_with_t.append(f"[{req.status_code}] Не удалось получить вакансию - {id} ('https://hh.ru/vacancy/{id}')")

                with open('trabl.json', "w", encoding="utf-8") as f:
                            json.dump(list_with_t, f, indent=4, ensure_ascii=False)

                time.sleep(3)
                return ParserRU.get_vacancies_with_specific_id(id, retry=(retry - 1))
            else:
                 return
        else:
             return req

    @classmethod
    def vacancies_saver(cls, page: int, area: list, role: str, list_with_trabl:list, dop_num:int = 0,) -> None:
        """Функция сохраняет полученные вакансии с определённой страницы в отдельный файл с расширением .json"""
        js_objs = []
        js_obj = json.loads(ParserRU.get_vacancies_per_page(page, area[0], role))
        for i in range(len(js_obj["items"])):
                        
                        id = js_obj["items"][i]["id"]

                        req = ParserRU.get_vacancies_with_specific_id(id, list_with_trabl)

                        if req:
                            
                            obj = json.loads(req.content.decode())

                            vacancie = {                                #Словарь хранит в себе список всех необходимых нам полей из получаемой вакансии
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

                            js_objs.append(vacancie)
                            req.close()
                            
                            time.sleep(0.6)
                        else:
                            continue

        if not os.path.exists('./areas/'):
                os.makedirs('./areas/')

        nextFileName = './areas/{}.json'.format(str(area[1])+'_'+str(page)+str(dop_num))

        with open(nextFileName, "w", encoding="utf-8") as f:
                            json.dump(js_objs, f, indent=4, ensure_ascii=False)

        if (js_obj["pages"] - page) <= 1:
            return

    @staticmethod
    def join_all_area():
        """Функция объединяет все полученные вакансии по каждой отдельной зоне в один файл."""
        all_vacancies = []
        for fl in os.listdir('./areas/'):
            with open('./areas/{}'.format(fl), encoding='utf8') as f:
                jsonText = json.load(f)
                for i in jsonText:
                    all_vacancies.append(i)

        with open("all_vacancies.json", "w", encoding='utf8') as fh:
            json.dump(all_vacancies, fh, indent=4, ensure_ascii=False)

    @classmethod
    def start_parsing(cls):
        """Конечная функция. Координирует работу всех остальных функций. Для начала она получает список всех зон.
        После чего начинает перебирать все вакансии в этой зоне и обрабатывает их исходя из выполняемых условий."""
        print(f"Время начала сбора данных {cls.get_time()}")
        areas = [["1", "Москва"], ["2", "Санкт-петербург"]]
        areas.extend(cls.get_areas())
        list_with_trabl = []

        total_vacancies = 0                  # Переменная хранит в себе кол-во всех вакансий
        area_list_id = 1                    # Переменная хранит в себе кол-во пройденных зон

        for area in areas:
            vac = json.loads(cls.get_vacancies_per_page(0, area[0], cls.ALL_NEED_ROLES))
            count_vacancies = vac['found']
            pages = vac['pages']
            print('[{0}/{1}] Область: {2} ({3}) - Вакансий: {4}'.format(area_list_id, len(areas), area[1], area[0], count_vacancies))
                
            if count_vacancies > 2000:                           # Если вакансий по запросу больше 2к, разбиваем этот запрос на подзапросы по специализации
                dop_num = 0
                for role in cls.PROFESSIONAL_ROLES:
                    need_vac = json.loads(cls.get_vacancies_per_page(0, area[0], role))
                    c_v= need_vac['found']
                    pag = need_vac['pages']
                    if c_v > 2000:                              # Если вакансий по запросу больше 2к, разбиваем этот запрос на подзапросы по опыту
                        for exp in cls.EXP:
                            exp_vac = json.loads(cls.get_vacancies_per_page(0, area[0], role, exp))
                            page_exp = exp_vac['pages']
                            for page in range(page_exp):
                                cls.vacancies_saver(page, area, role, list_with_trabl, dop_num)
                                time.sleep(0.5)
                                dop_num+=1
                            time.sleep(0.5)
                    else:
                        for page in range(pag):
                            cls.vacancies_saver(page, area, role, list_with_trabl, dop_num)
                            time.sleep(0.5)
                        dop_num+=1
                        time.sleep(0.5)
                time.sleep(0.5)
            else:                                               # Иначе собираем все вакансии, по всем специализациям сразу
                role = cls.ALL_NEED_ROLES
                for page in range(pages):
                    cls.vacancies_saver(page, area, role, list_with_trabl)
                    time.sleep(0.5)

            area_list_id+=1
            total_vacancies+=count_vacancies


            if count_vacancies != 0:
                print(f"Добавленно {count_vacancies} вакансий")

        print(f"Вакансии собраны, всего {total_vacancies}", end="\n\n")

