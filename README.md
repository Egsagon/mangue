# Mangue

Mangas.io downloader

> [!WARNING]
> This is probably against mangas.io terms or service.

> [!CAUTION]
> I don't know if they will ban accounts for this, so avoid mass downloading. You may want to fine-tune the delays in the configuration according to your download needs.

## Installation
```sh
git clone https://github.com/Egsagon/mangue
cd mangue
pip install -r requirements.txt
py main.py
```

## Usage

1. Get a manga slug (found in mangas URL)
    - For exemple: https://www.mangas.io/lire/undead-unluck
    - The manga slug will be undead-unluck

2. Start script
    - `py main.py`

```
[ + ] Email > my@mail.com
[ + ] Password > *************
[ > ] Sucess! Logged in as `my@mail.com`
[ + ] Manga slug > undead-unluck
[ > ] Manga found! Has 134 chapters available.
[ + ] Select chapter start (default=1) >
[ + ] Select chapter end  (default=-1) > 2
[ > ] Downloading 1 chapters. Press enter to confirm >
...
[ > ] Success! CBZ archive has been saved as `undead-unluck-ch1.cbz`.
```

> [!NOTE]
> You can create a `creds.json` file in cwd to automatically login. Set `email` and `password` keys.

# License

Licensed under GPLv3. See the `LICENSE` file.

The Software is provided “as is”, without warranty of any kind, express or implied, In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
