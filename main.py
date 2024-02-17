'''
    Mangas.io downloader
    @Egsagon
'''

import os
import time
import tqdm
import json
import pwinput
import zipfile
import requests

if os.path.exists('./creds.json'):
    print('[*] Using creds file')
    with open('./creds.json') as file:
        creds = json.load(file)

else:
    creds = {
        'email': input('[*] Email > '),
        'password': pwinput.pwinput('[*] Password > ')
    }

with open('ch.graphql') as file:
    ch_query = file.read()

with open('vol.graphql') as file:
    vol_query = file.read()

session = requests.Session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Content-Type': 'application/json; charset=utf-8'
}

auth = session.post(
    url = 'https://api.mangas.io/auth/login',
    data = json.dumps(creds, separators = (',', ':')),
    headers = headers | {'Content-Length': str(len(creds))}
)

if not auth.ok:
    print(f'[-] \033[91mError {auth.status_code}: {auth.reason}\033[0m')
    exit()

auth_data = auth.json()
user_data = auth_data.get('user')
user_token = auth_data.get('token')

print(f'[>] \033[92mSuccess! Logged in as `{user_data["email"]}`\033[0m')

headers['authorization'] = 'Bearer ' + user_token

manga_slug = input('[*] Manga slug > ')

payload = {
    'operationName': 'getVolumes',
    'variables': {'slug': manga_slug},
    'query': vol_query
}

res = session.post(
    'https://api.mangas.io/api',
    data = json.dumps(payload, separators = (',', ':')),
    headers = headers | {'Content-Length': str(len(creds))}
)

if not res.ok:
    print(f'[-] \033[91mError {res.status_code}: {res.reason}\033[0m')
    exit()

manga = res.json()['data']['manga']

if not manga:
    print('[-] \033[91mError: Manga not found.\033[0m')
    exit()

volumes = manga['volumes']

chapters = []
for volume in volumes:
    chapters += volume['chapters']

chapters_count = len(chapters)

print(f'[>] \033[92mSucess! This manga has {len(volumes)} volumes and {chapters_count} chapters\033[0m')

start = int(input('[*] Select chapter start (default=0) > ') or 0 )
end =   int(input('[*] Select chapter end  (default=-1) > ') or -1)

if start < 0: start = chapters_count - start
if end   < 0: end   = chapters_count - end

print(f'[>] Downloading {end - start} chapters.')
input('[*] Press enter to confirm > ')

if start == 0 and end == chapters_count - 1:
    archive_name = f'{manga_slug}.cbz'

else:
    archive_name = f'{manga_slug}-ch{start}-ch{end}.cbz'

if os.path.exists(archive_name):
    print('[-] \033[91mError: CBZ archive already exists in cwd.')
    exit()

with zipfile.ZipFile(archive_name, 'w') as archive:

    '''
    for i in tqdm.tqdm(range(start, end), desc = 'Total'):
        for page in tqdm.tqdm(chapters[i]['pages'], desc = f'Chapter {i}', leave = False):
            
            url = page['image']['url']
            page_name = f'ch{i}-p{page["number"]}'
            
            if page.get('isDoublePage'):
                page_name += '-double'
            
            for i in range(3):
                res = session.get(url, headers = headers)
                
                if res.ok: break
            
                print(f'\n033[93mError {res.status_code}: {res.reason} | {res.content}')
                time.sleep(10)
            
            archive.writestr(page_name + '.webp', res.content)
    '''
    
    for chapter in tqdm.tqdm(range(start, end), desc = 'Total'):
        
        payload = {
            'operationName': 'getChapter',
            'variables': {'slug': manga_slug, 'chapterNb': chapter},
            'query': ch_query
        }

        res = session.post(
            'https://api.mangas.io/api',
            data = json.dumps(payload, separators = (',', ':')),
            headers = headers | {'Content-Length': str(len(creds))}
        )
        
        print(res.content)
        break

print(f'[>] \033[92mSuccess! CBZ archive has been saved as `{archive_name}`.\033[90m')

# EOF