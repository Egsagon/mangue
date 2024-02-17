import time
import threading

_awaiter_chars = '/-\\|'

class awaiter:
    
    def __init__(self, desc: str = '') -> None:
        self.index = 0
        self.speed = .3
        self.desc = desc
        self.running = False
    
    def run(self) -> None:
        self.index = 0
        self.running = True
        thread = threading.Thread(target = self._thread)
        thread.start()
    
    def _thread(self) -> None:
        while self.running:
            print('\r[' + _awaiter_chars[self.index % len(_awaiter_chars)] + f'] {self.desc}', end = '')
            self.index += 1
            time.sleep(self.speed)
        
        print('\r', end = '')
    
    def stop(self) -> None:
        self.running = False
        time.sleep(self.speed)
        print('\r', end = '')

# EOF