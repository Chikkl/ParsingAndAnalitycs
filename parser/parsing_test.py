import requests      # Для запросов по API
import json          # Для обработки полученных результатов
import time          # Для задержки между запросами
from fake_useragent import UserAgent  # Для изменения 


def get_vacaniec_per_page(page:int = 0) -> list:
    params={
        "area":113,
        "professional_role":('156', '160', '10', '12', '150', '25', '165', '34', '36', '73', '155', '96',
                              '164', '104', '157', '107', '112', '113', '148', '114', '116', '121', '124', '125', '126'),
        "only_with_salary":True,
        "page":page,
        "employment":("full", "part","probation"),
        "experience":("noExperience", "between1And3", "between3And6", "moreThan6"),
        "per_page":100
    }

    req = requests.get('https://api.hh.ru/vacancies/', params, headers={"useragent":ua.random})
    print(req)
    print(req.text)
    data = req.content.decode()
    req.close()
    return data

start = time.time()
ua = UserAgent()
js_objs = []
count_vacaniec = 0

for page in range(0,50):
    headers = {
        "useragent":ua.random
    }
    js_obj = json.loads(get_vacaniec_per_page(page))

    for i in range(len(js_obj["items"])):
        id = js_obj["items"][i]["id"]

        req = requests.get(f'https://api.hh.ru/vacancies/{id}', headers=headers)
        req.close()

        js_objs.append(json.loads(req.content.decode()))

        count_vacaniec += 1

        print(f"Appended {count_vacaniec} vacaniec")

        time.sleep(0.3)

    if (js_obj["pages"] - page) <= 1:
        break
    
    with open("all_vacaniec.json", "w", encoding="utf-8") as f:
        json.dump(js_objs, f, indent=4, ensure_ascii=False)

    time.sleep(0.2)


print("Вакансии собраны", end="\n\n")

end = time.time() - start # Конец работы программы

print(end) ## вывод времени работы программы
