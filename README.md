<img src="https://github.com/Egsagon/mangue/blob/cf8c6233cc0e096749bb813edb3d91ba8e092493/mangue.png" width="600px">

> [!WARNING]
> This is probably against mangas.io terms or service.

> [!CAUTION]
> I don't know if they will ban accounts for this, so avoid mass downloading. You may want to fine-tune the delays in the configuration according to your download needs.

## Installation & usage

- Stable: See [latest build](https://github.com/Egsagon/mangue/releases/latest).

- Dev:
```
git clone https://github.com/Egsagon/mangue
cd mangue
pip install -r requirements.txt
py mangue.py
```

## Configuration

| You can create/modify the `config.json` file to you needs.
| **key**                     | **description**                                                        | **default**|
|:----------------------------|:-----------------------------------------------------------------------|:-----------|
| `credentials`               | Email and password or your mangas.io account if you want to auto login | None       |
| `proxies`                   | Dictionnary maping schemes to proxy addresses you want to use          | None       |
| `max_download_attempts`     | Maximum download attempts before giving up (in seconds)                | 3          |
| `download_attempts_delay`   | Delay between each failed request before retrying (in seconds)         | 3          |
| `chapter_download_interval` | Delay between each chapter download (in seconds)                       | 5          |

# License

Licensed under GPLv3. See the `LICENSE` file.

The Software is provided “as is”, without warranty of any kind, express or implied, In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
