import traceback
from functools import wraps
import aiohttp
from bs4 import BeautifulSoup


class LKS:
    def __init__(self, session: aiohttp.ClientSession, email: str, password: str):
        self.session = session
        self.email = email
        self.password = password

    @staticmethod
    def __print_response(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            print("========================= " + func.__name__ + " ============================")
            try:
                print(performed_func := await func(self, *args, **kwargs))
                return performed_func
            except Exception:
                print(traceback.format_exc())
            finally:
                print("========================= " + func.__name__ + " ============================")

        return wrapper

    async def auth(self):
        response_login_json = await self.__login_json()
        if not response_login_json:
            return {'error': 'Error in self.__login_json', 'is_auth': False}
        csrf_token: str | None = response_login_json.get('csrftoken')
        status_code = await self.__login(csrf_token)
        if status_code == 302:
            status_code = await self.__auth_php_login()
            if status_code != 302:
                return {'error': 'Error in self.__auth_php_login', 'is_auth': False}
            return {'error': None, 'is_auth': True}
        return {'error': 'Not valid email or password data', 'is_auth': False}

    @__print_response
    async def __login_json(self) -> dict | None:
        async with self.session.get('https://login.mirea.ru/login.json/') as response:
            return await response.json()

    @__print_response
    async def __login(self, csrf_token) -> int:
        headers = {
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryn57x0D890Wj7k3wS',
            'x-csrftoken': csrf_token,
            'Referer': 'https://lk.mirea.ru/'
        }
        data = '\r\n------WebKitFormBoundaryn57x0D890Wj7k3wS\r\n' \
               'Content-Disposition: form-data; name="login"\r\n\r\n' \
               f'{self.email}\r\n' \
               '------WebKitFormBoundaryn57x0D890Wj7k3wS\r\n' \
               'Content-Disposition: form-data; name="password"\r\n\r\n' \
               f'{self.password}\r\n' \
               '------WebKitFormBoundaryn57x0D890Wj7k3wS\r\n' \
               'Content-Disposition: form-data; name="scope"\r\n\r\n' \
               'student\r\n' \
               '------WebKitFormBoundaryn57x0D890Wj7k3wS--\r\n'
        async with self.session.post('https://login.mirea.ru/login/', headers=headers, data=data,
                                     allow_redirects=False) as response:
            return response.status

    @__print_response
    async def __auth_php_login(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'AUTH_FORM': 'Y',
            'TYPE': 'AUTH',
            'USER_LOGIN': self.email,
            'USER_PASSWORD': self.password,
            'USER_REMEMBER': 'Y'
        }
        async with self.session.post('https://lk.mirea.ru/auth.php?login=yes', headers=headers, data=data,
                                     allow_redirects=False) as response:
            return response.status

    @__print_response
    async def get_profile(self) -> tuple[dict, dict, dict]:
        async with self.session.get('https://lk.mirea.ru/') as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            zero_student_data = {}
            student_name = soup.find(class_="student-name").text.strip()
            zero_student_data['ФИО'] = student_name
            student_age = soup.find(class_='student-age').text.strip()
            zero_student_data['Возраст'] = student_age
            student_birthdate = soup.find(class_='student-birthdate').text.strip()[1:-1]
            zero_student_data['День рождения'] = student_birthdate

            table_profile = soup.find_all(class_='profile-part-wrap')[-1]
            rows_profile = table_profile.find_all('tr')
            data_list_profile = []

            # Проходим по строкам таблицы
            for row in rows_profile:
                cells = row.find_all('td')
                cell_data = [cell.text for cell in cells]
                data_list_profile.extend(cell_data)

            first_profile_data = {key.strip().capitalize(): value.strip().lower() for key, value in
                                  zip(data_list_profile[:4], data_list_profile[4:])}

            table = soup.find(class_='profile-table')
            rows_profile = table.find_all('tr')

            data_list_profile = []

            # Проходим по строкам таблицы
            for row in rows_profile:
                cells = row.find_all('td')
                cell_data = [cell.text for cell in cells]
                data_list_profile.extend(cell_data)

            second_profile_data = {key.strip().replace(':', '').capitalize(): value.strip().lower() for key, value in
                                   zip(data_list_profile[::2], data_list_profile[1::2])}
            return zero_student_data, first_profile_data, second_profile_data

    @__print_response
    async def export_cookies(self) -> dict:
        # Получите список всех куки с помощью session.cookie_jar
        cookies = self.session.cookie_jar
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie.key] = cookie.value

        return cookies_dict

    @__print_response
    async def import_cookies(self, cookies_dict: dict):
        # Преобразуйте словарь обратно в куки
        cookies = {key: aiohttp.Cookie(key=key, value=value) for key, value in cookies_dict.items()}

        # Установите куки в новую сессию
        for cookie in cookies.values():
            self.session.cookie_jar.update_cookies(cookie)
