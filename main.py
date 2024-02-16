'''
    Mangas.io downloader
    @Egsagon
'''

import os
import tqdm
import json
import utils
import pwinput
import zipfile
import requests

creds = {
    'email': input('[*] Email > '),
    'password': pwinput.pwinput('[*] Password > ')
}

with open('query.graphql') as file:
    query = file.read()

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
    'operationName': 'getReadingChapter',
    'variables': {'slug': manga_slug, 'quality': 'HD'},
    'query': query
}

print('[>] Executing query')
awaiter = utils.awaiter()
awaiter.run()

res = session.post(
    'https://api.mangas.io/api',
    data = json.dumps(payload, separators = (',', ':')),
    headers = headers | {'Content-Length': str(len(creds))}
)

awaiter.stop()

if not res.ok:
    print(f'[-] \033[91mError {res.status_code}: {res.reason}\033[0m')
    exit()

volumes = res.json()['data']['manga']['volumes']

chapters = []
for volume in volumes:
    chapters += volume['chapters']

chapters_count = len(chapters)

print(f'[>] \033[92mSucess! This manga has {len(volumes)} volumes and {chapters_count} chapters\033[0m')

start = int(input('[*] Select chapter start (default=0) > '))
end = int(input('[*] Select chapter end  (default=-1) > '))

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

    for i in tqdm.tqdm(range(start, end), desc = 'Total'):        
        for page in tqdm.tqdm(chapters[i]['pages'], desc = f'Chapter {i}', leave = False):
            
            url = page['image']['url']
            
            page_name = f'ch{i}-p{page["number"]}'
            
            if page.get('isDoublePage'):
                page_name += '-double'
            
            res = session.get(url, headers = headers)
            res.raise_for_status()
            
            archive.writestr(page_name + '.webp', res.content)

print(f'[>] \033[92mSuccess! CBZ archive has been saved as `{archive_name}`.\033[90m')

# EOF