'''
    Mangas.io downloader
    origin: github.com/Egsagon/mangue
    License: GPLv3
'''

from mangue import Mangasio

print('''\033[38;5;208m
    ┌──────────────────────────────────┐
    │ MANGUE - Mangas.io downloader    │
    │ base: github.com/Egsagon/mangue  │
    └──────────────────────────────────┘
\033[0m''')

import traceback

if __name__ == '__main__':

    try:
        m_io = Mangasio()

        if not m_io.auth():
            print("Fail to login")
            exit(1)

        # ================== manga exists ? ================= #

        if not m_io.manga_exists(input('[ + ] Manga slug > ')):
            print('[ - ] \033[91mError: Manga "{name}" not found.\033[0m'.format(name=m_io.manga.name))
            exit(1)

        manga = m_io.manga
        print(f'[ > ] \033[92mManga found! Has {manga.chapters_length()} chapters available.\033[0m')
        print('[ > ] Here is the list of chapters [\033[92m{}\033[0m].'.format(
                "\033[0m, \033[92m".join(str(c.number) for c in manga.chapters)
        ))

        # ============== Select download range ============== #

        start = float(input(f'[ + ] Select chapter start (default={manga.first_chapter().number}) > ') or manga.first_chapter().number)
        end = float(input(f'[ + ] Select chapter end  (default={manga.last_chapter().number}) > ') or manga.last_chapter().number)

        while not m_io.check_range(start, end):
            print('[ - ] \033[91mError: Please give correct start and end chapters.\033[0m')

            start = float(input(f'[ + ] Select chapter start (default={manga.first_chapter().number}) > ') or manga.first_chapter().number)
            end = float(input(f'[ + ] Select chapter end  (default={manga.last_chapter().number}) > ') or manga.last_chapter().number)

        print(f'[ > ] Has to download from chapter {start} until {end} ?')  # human readability
        input('[ + ] Press enter to confirm > ')

        # ============== Start download ============== #

        try:
            m_io.download_range(start, end)
        except FileExistsError:
            print('[ - ] \033[91mError: CBZ archive already exists in cwd.\033[0m')
            exit(1)

    except Exception as err:

        print(f'\033[91mUnexpected {err.__class__.__name__} error:')
        traceback.print_tb(err.__traceback__)
        print(f'{err}\033[0m', end='')

    input('\n\nScript terminated. Press <Enter> to close window.')
