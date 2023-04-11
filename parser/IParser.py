import time

class IParser:
    def get_time(t = time.localtime()):
        raise NotImplementedError
    def get_areas() -> list:
        raise NotImplementedError
    def get_vacaniec_per_page(page:int = 0, area:str = '1', prof_role:str = '156', exp = ("noExperience", "between1And3", "between3And6", "moreThan6")) -> list:
        raise NotImplementedError
    def get_vacancie_with_specific_id(id:str, list_with_t:list, retry:int=5) -> list:
        raise NotImplementedError
    def vacancies_saver(cls, page: int, area: list, role: str, list_with_trabl:list, dop_num:int = 0,) -> None:
        raise NotImplementedError
    def join_all_area():
        raise NotImplementedError
    def start_parsing(cls):
        raise NotImplementedError
