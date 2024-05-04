import asyncio
import configparser
import os
import platform
import subprocess
import threading
from typing import List

import psutil
import pystray
from PIL import Image

import utils

IS_WINDOWS = (platform.system() == "Windows")

RUNNING_ANIMALS_MAPPING = {
    "white_cat": [Image.open(f"./res/cat/white_cat_{i}.png") for i in range(5)],
    "black_cat": [Image.open(f"./res/cat/black_cat_{i}.png") for i in range(5)],
    "white_horse": [Image.open(f"./res/horse/white_horse_{i}.png") for i in range(14)],
    "black_horse": [Image.open(f"./res/horse/black_horse_{i}.png") for i in range(14)],
    "white_parrot": [Image.open(f"./res/parrot/white_parrot_{i}.png") for i in range(10)],
    "black_parrot": [Image.open(f"./res/parrot/black_parrot_{i}.png") for i in range(10)],
}

if IS_WINDOWS:
    WINDOWS_APP_PATH = {
        "wechat": utils.find_windows_abspath("WeChat.exe"),
        "qq": utils.find_windows_abspath("QQ.exe"),
        "chrome": utils.find_windows_abspath("chrome.exe"),
    }
else:
    MAC_APP_PATH = {
        "wechat": utils.find_mac_abspath("WeChat.app"),
        "qq": utils.find_mac_abspath("QQ.app"),
        "chrome": utils.find_mac_abspath("Google Chrome.app")
    }


class PyCat(object):
    def __init__(self, running_animal: str) -> None:
        self.running_animal = running_animal
        self.running_animal_icons = RUNNING_ANIMALS_MAPPING[running_animal]
        self.even_loop = None

        self.py_cat = pystray.Icon(
            name="py_cat",
            title="CPU : " + str(self.get_cpu_percent()),
            icon=self.running_animal_icons[0],
            menu=self.make_menu(),
        )

    def make_menu(self) -> pystray.Menu:
        cat_menu = pystray.Menu(
            pystray.MenuItem(
                "While Cat",
                lambda icon, item: self.change_running_animal("white_cat",
                                                              RUNNING_ANIMALS_MAPPING["white_cat"]),
            ),
            pystray.MenuItem(
                "Black Cat",
                lambda icon, item: self.change_running_animal("black_cat",
                                                              RUNNING_ANIMALS_MAPPING["black_cat"]), ),
        )

        horse_menu = pystray.Menu(
            pystray.MenuItem(
                "White Horse",
                lambda icon, item: self.change_running_animal("white_horse",
                                                              RUNNING_ANIMALS_MAPPING["white_horse"]), ),
            pystray.MenuItem(
                "Black Horse",
                lambda icon, item: self.change_running_animal("black_horse",
                                                              RUNNING_ANIMALS_MAPPING["black_horse"]), ),
        )

        parrot_menu = pystray.Menu(
            pystray.MenuItem(
                "White Parrot",
                lambda icon, item: self.change_running_animal("white_parrot",
                                                              RUNNING_ANIMALS_MAPPING["white_parrot"]), ),
            pystray.MenuItem(
                "Black Parrot",
                lambda icon, item: self.change_running_animal("black_parrot",
                                                              RUNNING_ANIMALS_MAPPING["black_parrot"]), ),
        )

        # animal menus
        animal_menus = pystray.Menu(
            pystray.MenuItem("Cat", cat_menu),
            pystray.MenuItem("Horse", horse_menu),
            pystray.MenuItem("Parrot", parrot_menu)
        )

        # application menus
        mac_app_menus = pystray.Menu(
            pystray.MenuItem("WeChat", lambda icon, item: self.launch_app("wechat")),
            pystray.MenuItem("QQ", lambda icon, item: self.launch_app("qq")),
            pystray.MenuItem("Chrome", lambda icon, item: self.launch_app("chrome")),
        )

        # main menus
        main_menus = pystray.Menu(
            pystray.MenuItem("Animals", animal_menus),
            pystray.MenuItem("Apps", mac_app_menus),
            pystray.MenuItem("Exit", self.end),
        )

        return main_menus

    def start(self) -> None:
        if self.is_app_running():
            return

        self.even_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.even_loop)

        main_thread = threading.Thread(target=lambda: asyncio.run(self.start_running()))
        main_thread.daemon = True
        main_thread.start()

        self.py_cat.run()

    def end(self) -> None:
        self.even_loop.stop()
        self.py_cat.stop()

        config.set("animal", "run_animal", self.running_animal)
        with open(INI_FILE_PATH, "w") as cf:
            config.write(cf)

        os.remove(LOCK_FILE_PATH)

    async def start_running(self) -> None:
        while True:
            await self.run_animal()

    async def run_animal(self) -> None:
        cpu_percent = self.get_cpu_percent()
        self.py_cat.title = f"CPU: {str(cpu_percent)} %"

        # adjust the speed based on CPU usage
        sleep_duration = 0.01 / (cpu_percent / 100 + 0.1)

        for animal_icon in self.running_animal_icons:
            await asyncio.sleep(sleep_duration)
            self.py_cat.icon = animal_icon

    def change_running_animal(self, new_running_animal: str, new_animal_icons: List[Image.Image]) -> None:
        self.running_animal = new_running_animal
        self.running_animal_icons = new_animal_icons

    def launch_app(self, app_name: str) -> None:
        if IS_WINDOWS:
            app_path = WINDOWS_APP_PATH[app_name]
        else:
            app_path = MAC_APP_PATH[app_name]

        if app_path is None:
            return

        if IS_WINDOWS:
            proc = subprocess.Popen([app_path])
        else:
            proc = subprocess.Popen(["open", "-a", app_path])

        proc.wait()

    def get_cpu_percent(self) -> float:
        return psutil.cpu_percent()

    def is_app_running(self) -> bool:
        if os.path.exists(LOCK_FILE_PATH):
            return True

        with open(LOCK_FILE_PATH, "w") as f:
            f.write("PyCat is running.")

        return False


if __name__ == "__main__":
    INI_FILE_PATH = "./ini/settings.ini"
    LOCK_FILE_PATH = "./py_cat.lock"

    config = configparser.ConfigParser()
    config.read(INI_FILE_PATH)

    # get last running animal
    run_animal = config.get("animal", "run_animal", fallback="white_cat")

    # app start
    py_cat = PyCat(run_animal)
    py_cat.start()
