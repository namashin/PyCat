import asyncio
import configparser
import os
import subprocess
import threading
from typing import List, Optional

import psutil
import pystray
import win32api
import win32event
from PIL import Image
from win32.lib import winerror

from logger import Logger

INI_FILE_PATH = "./ini/settings.ini"
LOG_PATH = "./log/mia_cat"

# make logger
logger = Logger(LOG_PATH)

# white cat icon
WHITE_CAT_ICONS = [Image.open(f"./res/cat/white_cat_{i}.ico") for i in range(5)]
# black cat icon
BLACK_CAT_ICONS = [Image.open(f"./res/cat/black_cat_{i}.ico") for i in range(5)]
# white horse icon
WHITE_HORSE_ICONS = [Image.open(f"./res/horse/white_horse_{i}.ico") for i in range(14)]
# black horse icon
BLACK_HORSE_ICONS = [Image.open(f"./res/horse/black_horse_{i}.ico") for i in range(14)]
# white parrot icon
WHITE_PARROT_ICONS = [
    Image.open(f"./res/parrot/white_parrot_{i}.ico") for i in range(10)
]
# black parrot icon
BLACK_PARROT_ICONS = [
    Image.open(f"./res/parrot/black_parrot_{i}.ico") for i in range(10)
]

RUNNING_ANIMALS_MAPPING = {
    "white_cat": WHITE_CAT_ICONS,
    "black_cat": BLACK_CAT_ICONS,
    "white_horse": WHITE_HORSE_ICONS,
    "black_horse": BLACK_HORSE_ICONS,
    "white_parrot": WHITE_PARROT_ICONS,
    "black_parrot": BLACK_PARROT_ICONS,
}


def find_exe_abspath(exe_name: str) -> Optional[str]:
    for root, dirs, files in os.walk(os.environ["ProgramFiles"]):
        if exe_name in files:
            return os.path.join(root, exe_name)

    for root, dirs, files in os.walk(os.environ["ProgramFiles(x86)"]):
        if exe_name in files:
            return os.path.join(root, exe_name)

    return None


# TODO You can add new application you want
APP_PATH = {
    "wechat": find_exe_abspath("WeChat.exe"),
    "qq": find_exe_abspath("QQ.exe"),
    "chrome": find_exe_abspath("chrome.exe"),
}


class MiaCat(object):
    def __init__(self, running_animal: str) -> None:
        self.running_animal = running_animal
        self.running_animal_icons = RUNNING_ANIMALS_MAPPING[running_animal]
        self.is_running = False
        self.even_loop = None
        self.mia_cat_mutex = None

        # animal menus
        cat_menu = pystray.Menu(
            pystray.MenuItem(
                "White Cat",
                lambda icon, item: self.change_running_animal(
                    "white_cat", WHITE_CAT_ICONS
                ),
            ),
            pystray.MenuItem(
                "Black Cat",
                lambda icon, item: self.change_running_animal(
                    "black_cat", BLACK_CAT_ICONS
                ),
            ),
        )
        horse_menu = pystray.Menu(
            pystray.MenuItem(
                "White Horse",
                lambda icon, item: self.change_running_animal(
                    "white_horse", WHITE_HORSE_ICONS
                ),
            ),
            pystray.MenuItem(
                "Black Horse",
                lambda icon, item: self.change_running_animal(
                    "black_horse", BLACK_HORSE_ICONS
                ),
            ),
        )
        parrot_menu = pystray.Menu(
            pystray.MenuItem(
                "White Parrot",
                lambda icon, item: self.change_running_animal(
                    "white_parrot", WHITE_PARROT_ICONS
                ),
            ),
            pystray.MenuItem(
                "Black Parrot",
                lambda icon, item: self.change_running_animal(
                    "black_parrot", BLACK_PARROT_ICONS
                ),
            ),
        )
        # sub menus
        animal_menus = pystray.Menu(
            pystray.MenuItem("Cat", cat_menu),
            pystray.MenuItem("Horse", horse_menu),
            pystray.MenuItem("Parrot", parrot_menu),
        )

        # application menus
        app_menus = pystray.Menu(
            pystray.MenuItem("WeChat", lambda icon, item: self.start_exe("wechat")),
            pystray.MenuItem("QQ", lambda icon, item: self.start_exe("qq")),
            pystray.MenuItem("Chrome", lambda icon, item: self.start_exe("chrome")),
        )

        # main menus
        main_menus = pystray.Menu(
            pystray.MenuItem("Animals", animal_menus),
            pystray.MenuItem("Apps", app_menus),
            pystray.MenuItem("Exit", self.stop_mia_cat),
        )

        self.mia_cat = pystray.Icon(
            name="MiaCat",
            title="CPU : " + str(self.get_cpu_percent()),
            icon=self.running_animal_icons[0],
            menu=main_menus,
        )

    def start_mia_cat(self) -> None:
        # ? already launched
        self.mia_cat_mutex = win32event.CreateMutex(None, 0, "mia_cat_mutex")
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            logger.error("MiaCat is running. Exiting.")
            return

        self.is_running = True

        self.even_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.even_loop)

        main_thread = threading.Thread(target=lambda: asyncio.run(self.start_running()))
        main_thread.start()

        self.mia_cat.run()

        logger.info(f"Start MiaCat Application")
        main_thread.join()

    def stop_mia_cat(self) -> None:
        self.is_running = False
        self.even_loop.stop()
        self.mia_cat.stop()

        logger.info(f"Stop MiaCat Application")

        # update current run animal
        config.set("animal", "run_animal", self.running_animal)
        with open(INI_FILE_PATH, "w") as cf:
            config.write(cf)

        # release the mutex
        win32api.CloseHandle(self.mia_cat_mutex)

    async def start_running(self) -> None:
        while self.is_running:
            await self.run_animal()

    async def run_animal(self) -> None:
        cpu_percent = self.get_cpu_percent()
        self.mia_cat.title = f"CPU: {str(cpu_percent)} %"

        # adjust the speed based on CPU usage
        sleep_duration = 0.01 / (cpu_percent / 100 + 0.1)

        for animal_icon in self.running_animal_icons:
            await asyncio.sleep(sleep_duration)
            self.mia_cat.icon = animal_icon

    def change_running_animal(
        self, new_running_animal: str, new_animal_icons: List[Image.Image]
    ) -> None:
        logger.info(
            f"Animal switched from {self.running_animal} to {new_running_animal}"
        )

        self.running_animal = new_running_animal
        self.running_animal_icons = new_animal_icons
        self.mia_cat.icon = self.running_animal_icons[0]

    def start_exe(self, app_name: str) -> None:
        if APP_PATH[app_name] is None:
            logger.error(
                f'Application name "{app_name}" is called, but could not find path'
            )
            return

        try:
            subprocess.Popen([APP_PATH[app_name]])
            logger.info(f"{app_name} started as subprocess")
        except subprocess.CalledProcessError as ex:
            logger.error(
                f"Subprocess failed with return code {ex.returncode}. Output: {ex.output}"
            )
        except Exception as ex:
            logger.error(f"Error during subprocess execution: {ex}")

    def get_cpu_percent(self) -> float:
        return psutil.cpu_percent()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(INI_FILE_PATH)

    # get last running animal
    run_animal = config.get("animal", "run_animal")

    # app start
    mia_cat = MiaCat(run_animal)
    mia_cat.start_mia_cat()

    """
    【activate conda】
    conda activate mia_cat
    
    【pyinstaller exe command】
    pyinstaller mia_cat.py logger.py --clean --name=mia_cat.exe --onefile --noconsole --icon=res/app.ico
    """
