import json
import os
import zipfile
import time

import pwinput
import requests
import tqdm

from .manga import Manga
from .chapter import Chapter


class Mangasio:
    BAR_FORMAT = '{desc} {bar} {percentage:.1f}% [{elapsed}<{remaining}]'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Content-Type': 'application/json; charset=utf-8'
    }

    GRAPHQL = '''
    # Checks if a manga exists
    query exists($slug: String) {
        manga(slug: $slug) {
            _id
            title
            chapterCount
            volumes {
                chapters {
                    title
                    number
                }
            }
        }
    }

    # Get all image id in one chapter 
    query getChapter($slug: String, $chapterNb: Float) {
        manga(slug: $slug) {
            chapter(number: $chapterNb) {
                pages {
                    _id
                    number
                    isDoublePage
                }
            }
        }
    }

    # Get a single image url
    query getImage($id: ID!, $quality: PageType) {
        page(id: $id) {
            image(type: $quality) {
                url
            }
        }
    }
    '''

    MAX_ATTEMPTS = 3
    ATTEMPT_DELAY = 3
    CHAPTER_INTERVAL_DELAY = 5

    def __init__(self):
        self.manga = Manga.make()
        self._session = requests.Session()
        self.__config = self._get_config()
        self._check_credentials()

    @staticmethod
    def _read_file_conf() -> dict | None:
        try:
            if os.path.exists('./config.json'):
                with open('./config.json') as file:
                    return json.load(file)

        except Exception as err:
            print(f'\033[91mError while parsing config: `{err}`\033[0m\n')
            print('Make sure your config file has the following format:')
            print('''
        {
            "credentials": {
                "email": null,
                "password": null
            },

            "proxies": null,
            "max_download_attempts": 3,
            "download_attempts_delay": 3,
            "chapter_download_interval": 5
        }
                    ''')

            input('\n\nPress <Enter> to close window.')

            return None

    def _get_config(self) -> dict:
        config = self._read_file_conf()

        if config is None:
            return {
                "credentials": {
                    "email": None,
                    "password": None
                },

                "proxies": None,
                "max_download_attempts": self.MAX_ATTEMPTS,
                "download_attempts_delay": self.ATTEMPT_DELAY,
                "chapter_download_interval": self.CHAPTER_INTERVAL_DELAY
            }

        return config

    def _check_credentials(self) -> None:
        credentials = self.__config.get('credentials')
        if not all(credentials.values()):
            self.__config['credentials']['email'] = input('[ + ] Email > ')
            self.__config['credentials']['password'] = pwinput.pwinput('[ + ] Password > ')

    def _get_credentials(self) -> dict[str, str]:
        return self.__config.get('credentials')

    def auth(self) -> bool:
        """
        Try to connect the user

        :return:
        """

        response = self._session.post(
                url='https://api.mangas.io/auth/login',
                data=json.dumps(self._get_credentials(), separators=(',', ':')),
                headers=self.HEADERS | {'Content-Length': str(len(self._get_credentials()))}
        )

        if not response.ok:
            print(f'[ - ] \033[91mError {response.status_code}: {response.reason}.\033[0m Check your credentials')
            return False

        auth_data = response.json()
        user_data = auth_data.get('user')
        user_token = auth_data.get('token')

        print(f'[ > ] \033[92mSuccess! Logged in as `{user_data["email"]}`\033[0m')

        self.HEADERS['authorization'] = 'Bearer ' + user_token

        return True

    def _query(self, operation: str, variables: dict[str]) -> dict | list:
        """
        Perform a GraphQL query.
        """

        payload = {
            'operationName': operation,
            'variables': variables,
            'query': self.GRAPHQL
        }

        res = self._session.post(
                'https://api.mangas.io/api',
                data=json.dumps(payload, separators=(',', ':')),
                headers=self.HEADERS
        )

        res.raise_for_status()

        return res.json()['data']

    def manga_exists(self, slug: str) -> bool:
        self.manga.name = slug
        result = self._query('exists', dict(slug=slug))['manga']

        if not result:
            return False

        for volume in result.get('volumes'):
            for chapter in volume.get('chapters'):
                self.manga.chapters.append(Chapter(chapter.get('title'), chapter.get('number')))

        return True

    def download_range(self, start: float, end: float):
        chap_numbers = [c.number for c in self.manga.chapters]

        if chap_numbers.count(start) == 0 or chap_numbers.count(end) == 0:
            raise "Please give correct start and end chapters"

        if start > end:
            temp = start
            start = end
            end = temp

        all_manga = start == self.manga.first_chapter().number and end == self.manga.last_chapter().number

        if all_manga:
            archive_name = f'{self.manga.name}.cbz'
        else:
            archive_name = f'{self.manga.name}-ch{str(start)}-ch{end}.cbz'
            self._remove_useless_chapters(start, end)

        if os.path.exists(archive_name):
            raise FileExistsError

        self._download(archive_name)

    def _remove_useless_chapters(self, start: float, end: float):
        self.manga.chapters = list(filter(lambda c: start <= c.number <= end, self.manga.chapters))

    def _download(self, archive_name):
        print(f'[ > ] \033[92mDownloading \033[01m{archive_name}\033[0m')
        with zipfile.ZipFile(archive_name, 'w') as archive:

            for chapter in tqdm.tqdm(self.manga.chapters,
                                     desc='[ # ] Progress',
                                     colour='magenta',
                                     bar_format='{desc} {bar} {percentage:.1f}% [{n_fmt}/{total_fmt} chapters]',
                                     ascii=' ─'):

                res = self._query('getChapter', dict(slug=self.manga.name, chapterNb=chapter.number))
                chapter_data = res['manga']['chapter']

                for page in tqdm.tqdm(chapter_data['pages'],
                                      desc=f'[ # ] CH-{str(chapter.number)} : {chapter.title}',
                                      leave=False,
                                      bar_format='{desc} {bar} {percentage:.1f}% [{n_fmt}/{total_fmt} pages]',
                                      ascii=' ─'):

                    pid = page['_id']

                    page_name = f'ch{chapter.number}-pg{page["number"]}'

                    if page['isDoublePage']:
                        page_name += '-double'

                    for i in range(self.MAX_ATTEMPTS):

                        res = self._query('getImage', dict(id=pid, quality='HD'))
                        image = res['page']['image']
                        res = self._session.get(image['url'], headers=self.HEADERS)

                        if res.ok:
                            archive.writestr(page_name + '.webp', res.content)
                            break

                        print(f'\n[ - ] \033[93mError {res.status_code}: {res.reason} | {res.content}\033[0m')
                        time.sleep(self.ATTEMPT_DELAY)

                    else:
                        print(f'\n[ - ] \033[91mError: Failed to fetch image after {self.MAX_ATTEMPTS} attempts.\033[0m')

                time.sleep(self.CHAPTER_INTERVAL_DELAY)

        print(f'[ > ] \033[92mSuccess! CBZ archive has been saved as \033[01m{archive_name}\033[0m\033[92m.\033[0m')
