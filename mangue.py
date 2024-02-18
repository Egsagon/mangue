'''
    Mangas.io downloader
    github.com/Egsagon/mangue
    License: GPLv3
'''

import os
import time
import tqdm
import json
import traceback

import pwinput
import zipfile
import requests

# ============== Configuration ============== #

config = {}
if os.path.exists('./config.json'):
    with open('./config.json') as file:
        config = json.load(file)

PROXIES                = config.get('proxies')
MAX_ATTEMPTS           = config.get('max_download_attempts',     3)
ATTEMPT_DELAY          = config.get('download_attempts_delay',   3)
CHAPTER_INTERVAL_DELAY = config.get('chapter_download_interval', 3)

BAR_FORMAT = '{desc} {bar} {percentage:.1f}% [{elapsed}<{remaining}]'

# =========================================== #

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Content-Type': 'application/json; charset=utf-8'
}

GRAPHQL = '''
# Checks if a manga exists
query exists($slug: String) {
    manga(slug: $slug) {
        _id
        chapterCount
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

def main() -> None:
    
    session = requests.Session()
        
    # ============== Get credentials ============== #

    autocreds: dict = config.get('credentials')

    if autocreds and all(autocreds.values()):
        print('[ > ] Using creds file')
        creds = config['credentials']

    else:
        creds = {
            'email': input('[ + ] Email > '),
            'password': pwinput.pwinput('[ + ] Password > ')
        }

    # ============== Authentification ============== #

    auth = session.post(
        url = 'https://api.mangas.io/auth/login',
        data = json.dumps(creds, separators = (',', ':')),
        headers = HEADERS | {'Content-Length': str(len(creds))}
    )

    if not auth.ok:
        print(f'[ - ] \033[91mError {auth.status_code}: {auth.reason}.\033[0m Check your credentials')
        return

    auth_data = auth.json()
    user_data = auth_data.get('user')
    user_token = auth_data.get('token')

    print(f'[ > ] \033[92mSuccess! Logged in as `{user_data["email"]}`\033[0m')

    HEADERS['authorization'] = 'Bearer ' + user_token

    # ============== Check if manga exists ============== #

    def query(_operation: str, _variables: dict[str]) -> dict | list:
        '''
        Perform a GraphQL query.
        '''
        
        payload = {
            'operationName': _operation,
            'variables': _variables,
            'query': GRAPHQL
        }

        res = session.post(
            'https://api.mangas.io/api',
            data = json.dumps(payload, separators = (',', ':')),
            headers = HEADERS
        )
        
        res.raise_for_status()
        return res.json()['data']

    manga_slug = input('[ + ] Manga slug > ')

    res = query('exists', dict(slug = manga_slug))['manga']

    if not res:
        print('[ - ] \033[91mError: Manga not found.\033[0m')
        return
        
    chapters_count = res['chapterCount']

    print(f'[ > ] \033[92mManga found! Has {chapters_count} chapters available.\033[0m')

    # ============== Select download range ============== #

    start = int(input('[ + ] Select chapter start (default=1) > ') or +1)
    end   = int(input('[ + ] Select chapter end  (default=-1) > ') or -1)

    if start < 0: start = chapters_count - start
    if end   < 0: end   = chapters_count - end

    print(f'[ > ] Downloading {end - start} chapters.')
    input('[ + ] Press enter to confirm > ')

    if start == 1 and end == chapters_count - 1:
        archive_name = f'{manga_slug}.cbz'

    else:
        archive_name = f'{manga_slug}-ch{start}-ch{end}.cbz'

    if os.path.exists(archive_name):
        print('[ - ] \033[91mError: CBZ archive already exists in cwd.')
        return

    # ============== Start download ============== #

    with zipfile.ZipFile(archive_name, 'w') as archive:

        for chapter in tqdm.tqdm(range(start, end),
                                desc = 'Progress',
                                colour = 'magenta',
                                bar_format = BAR_FORMAT,
                                ascii = ' ─'):
            
            res = query('getChapter', dict(slug = manga_slug, chapterNb = chapter))
            chapter_data = res['manga']['chapter']
        
            for page in tqdm.tqdm(chapter_data['pages'],
                                desc = f'CH-{str(chapter).zfill(5)}',
                                leave = False,
                                bar_format = BAR_FORMAT,
                                ascii = ' ─'):
        
                pid = page['_id']
                
                page_name = f'ch{chapter}-pg{page["number"]}'
                
                if page['isDoublePage']:
                    page_name += '-double'
                
                for i in range(MAX_ATTEMPTS):
                
                    res = query('getImage', dict(id = pid, quality = 'HD'))
                    image = res['page']['image']
                    res = session.get(image['url'], headers = HEADERS)
                    
                    if res.ok:
                        archive.writestr(page_name + '.webp', res.content)
                        break
                    
                    print(f'\n[ - ] \033[93mError {res.status_code}: {res.reason} | {res.content}\033[0m')
                    time.sleep(ATTEMPT_DELAY)
                
                else:
                    print(f'\n[ - ] \033[91mError: Failed to fetch image after {MAX_ATTEMPTS} attempts.\033[0m')
            
            time.sleep(CHAPTER_INTERVAL_DELAY)

    print(f'[ > ] \033[92mSuccess! CBZ archive has been saved as `{archive_name}`.\033[90m')

if __name__ == '__main__':
    
    try:
        main()
    
    except Exception as err:
        
        print(f'\033[91mUnexpected {err.__class__.__name__} error:')
        traceback.print_tb(err.__traceback__)
        print('\033[0m', end = '')
    
    input('\n\nScript terminated. Press <Enter> to close window.')

# EOF