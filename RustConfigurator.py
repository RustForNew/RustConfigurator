# -*- coding: utf-8 -*-

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import os
import sys
import shutil
import subprocess
import psutil
import vdf
import winreg
import threading
import webbrowser
import re
import json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import requests
from packaging import version
from collections import defaultdict
import random # UI: Добавлено для узоров

# --- КОНФИГУРАЦИЯ ---
APP_NAME = "RustConfigurator"
VERSION = "2.0.0" # Версия обновлена
WINDOW_SIZE = "1000x850"

# --- API КОНФИГУРАЦИЯ ---
BM_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6Ijg1ODU0NzU4NmVhOTUyYWMiLCJpYXQiOjE3NjkwODk0ODQsIm5iZiI6MTc2OTA4OTQ4NCwiaXNzIjoiaHR0cHM6Ly93d3cuYmF0dGxlbWV0cmljcy5jb20iLCJzdWIiOiJ1cm46dXNlcjoxMTM5NDU5In0.AMHBfg9rFeE9VK6Z-Q-e4WfWedEkSEk79oNwPTvowYc"
BM_API_URL = "https://api.battlemetrics.com/servers"

# --- ДАННЫЕ ДЛЯ КАЛЬКУЛЯТОРОВ ---

# Стоимость крафта 1 единицы взрывчатки
CRAFT_COSTS = {
    "С4": {"Уголь": 3000, "Сера": 2200, "Металл. фрагменты": 200, "Топливо низкого качества": 60, "Ткань": 5, "Микросхемы": 2},
    "Ракеты": {"Уголь": 1950, "Сера": 1400, "Металл. фрагменты": 100, "Топливо низкого качества": 30, "Железная труба": 2},
    "Сачели": {"Уголь": 720, "Сера": 480, "Металл. фрагменты": 80, "Ткань": 10, "Веревка": 1},
    "Взрывные патроны": {"Уголь": 60, "Сера": 50, "Металл. фрагменты": 10},
    "Скоростные ракеты": {"Уголь": 300, "Сера": 200, "Металл. фрагменты": 0, "Топливо низкого качества": 0, "Железная труба": 1},
    "Молотовы": {"Ткань": 10, "Топливо низкого качества": 50}
}

# Стоимость рейда в единицах взрывчатки
RAID_DATA = {
    "Деревянная стена": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 2}},
        {"method": "Сачели", "cost": {"Сачели": 3}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 56}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 9}},
        {"method": "Молотовы", "cost": {"Молотовы": 4}},
    ],
    "Каменная стена": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 4}},
        {"method": "Сачели", "cost": {"Сачели": 10}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 200}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 32}},
    ],
    "Железная (металлическая) стена": [
        {"method": "С4", "cost": {"С4": 4}},
        {"method": "Ракеты", "cost": {"Ракеты": 8}},
        {"method": "Сачели", "cost": {"Сачели": 23}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 400}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 67}},
    ],
    "МВК (Armored) стена": [
        {"method": "С4", "cost": {"С4": 8}},
        {"method": "Ракеты", "cost": {"Ракеты": 15}},
        {"method": "Сачели", "cost": {"Сачели": 46}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 800}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 134}},
    ],
    "Деревянная дверь": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 1}},
        {"method": "Сачели", "cost": {"Сачели": 2}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 20}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 4}},
        {"method": "Молотовы", "cost": {"Молотовы": 2}},
    ],
    "Железная дверь": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 2}},
        {"method": "Сачели", "cost": {"Сачели": 4}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 63}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 11}},
    ],
    "МВК (Armored) дверь": [
        {"method": "С4", "cost": {"С4": 3}},
        {"method": "Ракеты", "cost": {"Ракеты": 5}},
        {"method": "Сачели", "cost": {"Сачели": 12}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 200}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 34}},
    ],
    "Гаражная дверь": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 3}},
        {"method": "Сачели", "cost": {"Сачели": 9}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 150}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 25}},
    ],
    "Деревянная оконная решетка": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 2}},
        {"method": "Сачели", "cost": {"Сачели": 3}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 56}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 9}},
        {"method": "Молотовы", "cost": {"Молотовы": 4}},
    ],
    "Железная оконная решетка": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 4}},
        {"method": "Сачели", "cost": {"Сачели": 12}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 200}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 31}},
    ],
    "МВК оконная решетка": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 6}},
        {"method": "Сачели", "cost": {"Сачели": 18}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 300}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 50}},
    ],
    "Окно из укрепленного стекла": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 4}},
        {"method": "Сачели", "cost": {"Сачели": 12}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 200}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 34}},
    ],
    "Деревянные ворота": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 3}},
        {"method": "Сачели", "cost": {"Сачели": 6}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 112}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 24}},
        {"method": "Молотовы", "cost": {"Молотовы": 7}},
    ],
    "Каменные ворота": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 4}},
        {"method": "Сачели", "cost": {"Сачели": 10}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 200}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 32}},
    ],
    "Высокая деревянная стена": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 3}},
        {"method": "Сачели", "cost": {"Сачели": 6}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 112}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 24}},
        {"method": "Молотовы", "cost": {"Молотовы": 7}},
    ],
    "Высокая каменная стена": [
        {"method": "С4", "cost": {"С4": 2}},
        {"method": "Ракеты", "cost": {"Ракеты": 4}},
        {"method": "Сачели", "cost": {"Сачели": 10}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 200}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 32}},
    ],
    "Шкаф (Tool Cupboard)": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 1}},
        {"method": "Сачели", "cost": {"Сачели": 1}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 10}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 2}},
        {"method": "Молотовы", "cost": {"Молотовы": 1}},
    ],
    "Решётчатый настил": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 1}},
        {"method": "Сачели", "cost": {"Сачели": 4}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 63}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 12}},
    ],
    "Люк с лестницей": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 1}},
        {"method": "Сачели", "cost": {"Сачели": 4}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 63}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 11}},
    ],
    "Металлическая витрина": [
        {"method": "С4", "cost": {"С4": 3}},
        {"method": "Ракеты", "cost": {"Ракеты": 6}},
        {"method": "Сачели", "cost": {"Сачели": 18}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 300}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 50}},
    ],
    "Автоматическая турель": [
        {"method": "С4", "cost": {"С4": 1}},
        {"method": "Ракеты", "cost": {"Ракеты": 2}},
        {"method": "Скоростные ракеты", "cost": {"Скоростные ракеты": 3}},
        {"method": "Взрывные патроны", "cost": {"Взрывные патроны": 96}},
    ],
}

RECYCLER_DATA_NORMAL = {
    "Старая микросхема": [{"item": "Металлолом", "quantity": 20}, {"item": "МВК", "quantity": 1}],
    "Пустой баллон пропана": [{"item": "Металлолом", "quantity": 1}, {"item": "Фрагменты металла", "quantity": 50}],
    "Шестерни": [{"item": "Металлолом", "quantity": 10}, {"item": "Фрагменты металла", "quantity": 13}],
    "Металлическое лезвие": [{"item": "Металлолом", "quantity": 2}, {"item": "Фрагменты металла", "quantity": 15}],
    "Металлическая труба": [{"item": "Металлолом", "quantity": 5}, {"item": "МВК", "quantity": 1}],
    "Металлическая пружина": [{"item": "Металлолом", "quantity": 10}, {"item": "МВК", "quantity": 1}],
    "Корпус винтовки": [{"item": "Металлолом", "quantity": 25}, {"item": "МВК", "quantity": 2}],
    "Корпус SMG": [{"item": "Металлолом", "quantity": 15}, {"item": "МВК", "quantity": 2}],
    "Корпус полуавтоматического оружия": [{"item": "Металлолом", "quantity": 15}, {"item": "МВК", "quantity": 2}, {"item": "Фрагменты металла", "quantity": 75}],
    "Дорожные знаки": [{"item": "Металлолом", "quantity": 5}, {"item": "МВК", "quantity": 1}],
    "Верёвка": [{"item": "Ткань", "quantity": 15}],
    "Тканевый чехол (брезент)": [{"item": "Ткань", "quantity": 50}],
    "Электрический предохранитель": [{"item": "Металлолом", "quantity": 20}],
    "Камера видеонаблюдения": [{"item": "Старые микросхемы", "quantity": 2}, {"item": "МВК", "quantity": 2}],
    "Компьютер наблюдения": [{"item": "Старые микросхемы", "quantity": 3}, {"item": "МВК", "quantity": 1}, {"item": "Фрагменты металла", "quantity": 50}],
}

RECYCLER_DATA_SAFEZONE = {
    "Старая микросхема": [{"item": "Металлолом", "quantity": "16"}, {"item": "МВК", "quantity": "1"}],
    "Пустой баллон пропана": [{"item": "Металлолом", "quantity": "1"}, {"item": "Фрагменты металла", "quantity": "40"}],
    "Шестерни": [{"item": "Металлолом", "quantity": "8"}, {"item": "Фрагменты металла", "quantity": "10-11"}],
    "Металлическое лезвие": [{"item": "Металлолом", "quantity": "1"}, {"item": "Фрагменты металла", "quantity": "12"}],
    "Металлическая труба": [{"item": "Металлолом", "quantity": "4"}, {"item": "МВК", "quantity": "1"}],
    "Металлическая пружина": [{"item": "Металлолом", "quantity": "8"}, {"item": "МВК", "quantity": "1"}],
    "Корпус винтовки": [{"item": "Металлолом", "quantity": "20"}, {"item": "МВК", "quantity": "2"}],
    "Корпус SMG": [{"item": "Металлолом", "quantity": "12"}, {"item": "МВК", "quantity": "2"}],
    "Корпус полуавтоматического оружия": [{"item": "Металлолом", "quantity": "12"}, {"item": "МВК", "quantity": "2"}, {"item": "Фрагменты металла", "quantity": "60"}],
    "Дорожные знаки": [{"item": "Металлолом", "quantity": "4"}, {"item": "МВК", "quantity": "1"}],
    "Верёвка": [{"item": "Ткань", "quantity": "12"}],
    "Тканевый чехол (брезент)": [{"item": "Ткань", "quantity": "40"}],
    "Электрический предохранитель": [{"item": "Металлолом", "quantity": "16"}],
    "Камера видеонаблюдения": [{"item": "Старые микросхемы", "quantity": "1-2"}, {"item": "МВК", "quantity": "1-2"}],
    "Компьютер наблюдения": [{"item": "Старые микросхемы", "quantity": "2"}, {"item": "МВК", "quantity": "1"}, {"item": "Фрагменты металла", "quantity": "40"}],
}

BUILD_COSTS = {
    "Фундамент (Дерево)": {"Дерево": 200}, "Фундамент (Камень)": {"Камень": 300}, "Фундамент (Металл)": {"Металл": 200}, "Фундамент (МВК)": {"МВК": 20},
    "Стена (Дерево)": {"Дерево": 100}, "Стена (Камень)": {"Камень": 150}, "Стена (Металл)": {"Металл": 100}, "Стена (МВК)": {"МВК": 10},
    "Пол (Дерево)": {"Дерево": 100}, "Пол (Камень)": {"Камень": 150}, "Пол (Металл)": {"Металл": 100}, "Пол (МВК)": {"МВК": 10},
    "Дверной проем (Дерево)": {"Дерево": 100}, "Дверной проем (Камень)": {"Камень": 150}, "Дверной проем (Металл)": {"Металл": 100}, "Дверной проем (МВК)": {"МВК": 10},
    "Оконный проем (Дерево)": {"Дерево": 100}, "Оконный проем (Камень)": {"Камень": 150}, "Оконный проем (Металл)": {"Металл": 100}, "Оконный проем (МВК)": {"МВК": 10},
}

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И КОНСТАНТЫ ---
def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

PROFILES = {
    "🔫 Combat": "Комбат.cfg", "🎨 Красивая картинка": "Топ графика.cfg",
    "⚖️ Средние настройки": "Баланс.cfg", "🖥️ Слабый ПК": "Макс производительность.cfg"
}
STEAM_PROCESS_NAME = "steam.exe"
GITHUB_REPO_OWNER = "RustForNew"
GITHUB_REPO_NAME = "RustConfigurator"
LATEST_VERSION_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/master/latest_version.txt"
GITHUB_RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases"
RUS_TO_ENG_KEY_MAP = {
    'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']',
    'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';', 'э': "'", 'я': 'z',
    'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n', 'ь': 'm', 'б': ',', 'ю': '.', '.': '/', 'ё': '`'
}
DEFAULT_RUST_COMMANDS = {
    'consoletoggle', '+forward', '+backward', '+left', '+right', '+attack', '+attack2', '+attack3', '+ping', '+slot1',
    '+slot2', '+slot3', '+slot4', '+slot5', '+slot6', '+holsteritem', '+sprint', '+altlook', '+reload', '+jump',
    '+duck', '+use', '+voice', '+map', 'chat.open', '+invnext', '+invprev', 'inventory.toggle', 'inventory.togglecrafting',
    'lighttoggle', 'inventory.examineheld', '+compass', '+hoverloot', '+gestures', '+pets', '+firemode', 'clan.toggleclan',
    '+prevskin', '+nextskin', '+focusmap', '+notec', '+noted', '+notee', '+notef', '+noteg', '+notea', '+noteb',
    '+notesharpmod', '+noteoctaveupmod', '+zoomincrease', '+zoomdecrease', '+opentutorialhelp', 'swapseats',
    'swaptoseat 0', 'swaptoseat 1', 'swaptoseat 2', 'swaptoseat 3', 'swaptoseat 4', 'swaptoseat 5', 'swaptoseat 6',
    'swaptoseat 7', '+wireslackup', '+wireslackdown', 'kill'
}

# --- НОВЫЕ ЦВЕТОВЫЕ ПЕРЕМЕННЫЕ ДЛЯ UI ---
class AppColors:
    # Основные цвета фона
    BG_COLOR = ("#F0F2F5", "#1D2125")
    FRAME_BG_COLOR = ("#FFFFFF", "#24282C")
    FRAME_BORDER_COLOR = ("#E0E2E5", "#33373B")
    
    # Цвета текста
    TEXT_COLOR = ("#1C1E21", "#E4E6EB")
    TEXT_SECONDARY_COLOR = ("#65676B", "#B0B3B8")
    
    # Цвета элементов управления
    BUTTON_HOVER_COLOR = ("#E4E6EB", "#3A3B3C")
    INPUT_BG_COLOR = ("#F0F2F5", "#3A3B3C")
    INPUT_BORDER_COLOR = ("#CED0D4", "#4E4F50")
    
    # Акцентный цвет (будет меняться пользователем)
    ACCENT_COLOR = "#3275F2"
    
    # UI: Цвета для фонового узора
    PATTERN_LINE_COLOR_DARK = "#28385b"
    PATTERN_LINE_COLOR_LIGHT = "#D0D8E8"

class EntryWithContextMenu(ctk.CTkEntry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self.cut)
        self.context_menu.add_command(label="Копировать", command=self.copy)
        self.context_menu.add_command(label="Вставить", command=self.paste)
        self.bind("<Button-3>", self.show_context_menu)
        self.bind("<Control-m>", self.handle_paste_event) 
        self.bind("<Control-v>", self.handle_paste_event)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def cut(self):
        self.event_generate("<<Cut>>")

    def copy(self):
        self.event_generate("<<Copy>>")

    def paste(self):
        try:
            clipboard_content = self.clipboard_get()
            if self.cget("state") == "normal":
                self.insert(self.index(tk.INSERT), clipboard_content)
        except tk.TclError:
            pass

    def handle_paste_event(self, event=None):
        self.paste()
        return "break"

class TextboxWithContextMenu(ctk.CTkTextbox):
    def __init__(self, *args, **kwargs):
        self._current_state = kwargs.get("state", "normal") 
        super().__init__(*args, **kwargs)
        
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self.cut)
        self.context_menu.add_command(label="Копировать", command=self.copy)
        self.context_menu.add_command(label="Вставить", command=self.paste)
        self.bind("<Button-3>", self.show_context_menu)
        self.bind("<Control-m>", self.handle_paste_event) 
        self.bind("<Control-v>", self.handle_paste_event)

    def configure(self, **kwargs):
        if "state" in kwargs:
            self._current_state = kwargs["state"]
        super().configure(**kwargs)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def cut(self):
        self.event_generate("<<Cut>>")

    def copy(self):
        self.event_generate("<<Copy>>")

    def paste(self):
        try:
            clipboard_content = self.clipboard_get()
            original_state = self._current_state
            
            if original_state == "disabled":
                super().configure(state="normal")
                
            self.insert(self.index(tk.INSERT), clipboard_content)
            
            if original_state == "disabled":
                super().configure(state="disabled")
        except tk.TclError:
            pass

    def handle_paste_event(self, event=None):
        self.paste()
        return "break"

class RustConfiguratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.settings_window = None # Для окна настроек
        self.accent_color = AppColors.ACCENT_COLOR # Цвет по умолчанию
        self._is_closing = False # FIX: Флаг для отслеживания процесса закрытия окна

        self.configure(fg_color=AppColors.BG_COLOR)
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry(WINDOW_SIZE)
        self.resizable(True, True)
        self.minsize(1000, 850)
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # UI: Холст для фонового узора
        self.background_canvas = ctk.CTkCanvas(self, borderwidth=0, highlightthickness=0)
        self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Widget.lower(self.background_canvas) # Явный вызов метода из базового класса
        self.bind("<Configure>", self.draw_background_pattern) # Перерисовываем при изменении размера окна

        self.steam_path = None
        self.rust_path = None
        self.steam_exe_path = None
        self.icons = {}
        self.bind_entries = {}
        self.favorite_servers = []

        # --- ИЗМЕНЕНИЕ: Стилизация вкладок ---
        self.tab_view = ctk.CTkTabview(self, 
                                       fg_color=AppColors.FRAME_BG_COLOR,
                                       segmented_button_fg_color=AppColors.FRAME_BG_COLOR,
                                       segmented_button_selected_color=self.accent_color,
                                       segmented_button_unselected_color=AppColors.FRAME_BG_COLOR,
                                       segmented_button_selected_hover_color=self.accent_color,
                                       segmented_button_unselected_hover_color=AppColors.BUTTON_HOVER_COLOR,
                                       text_color=AppColors.TEXT_COLOR,
                                       command=self.on_tab_change)
        self.tab_view.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        self.tab_view.add("Основные настройки")
        self.tab_view.add("Бинды")
        self.tab_view.add("Калькуляторы")
        self.tab_view.add("Менеджер серверов")
        self.tab_view.add("Анализ боя")
        self.tab_view.add("Доп настройка")
        self.tab_view.add("О создателе")
        self.tab_view.set("Основные настройки")

        self.create_main_tab()
        self.create_binds_tab()
        self.create_calculators_tab()
        self.create_server_manager_tab()
        self.create_combat_log_tab()
        self.create_advanced_tab()
        self.create_about_tab()
        
        # --- ИЗМЕНЕНИЕ: Добавлена кнопка настроек ---
        self.create_settings_button()

        # --- ИЗМЕНЕНИЕ: Стилизация лог-панели ---
        self.log_textbox = ctk.CTkTextbox(self, state="disabled", wrap="word", 
                                          font=("Consolas", 11), height=120, 
                                          border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, 
                                          fg_color=AppColors.FRAME_BG_COLOR,
                                          text_color=AppColors.TEXT_SECONDARY_COLOR)
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_closing) # FIX: Устанавливаем протокол закрытия

        self.log("Приложение запущено.")
        self.initialize_paths()
        self.after(200, self.start_update_check_thread)
        self.after(500, self.show_new_instructions)
        self.after(100, self.draw_background_pattern) # UI: Первоначальная отрисовка узора

    # FIX: Метод для чистого закрытия приложения
    def on_closing(self):
        self._is_closing = True
        self.destroy()

    # UI: Метод для отрисовки фонового узора
    def draw_background_pattern(self, event=None):
        # FIX: Защита от вызова на уничтоженном виджете или во время закрытия
        if self._is_closing or not hasattr(self, "background_canvas") or not self.background_canvas.winfo_exists():
            return

        self.background_canvas.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Определяем цвет фона и линий в зависимости от темы
        bg_color = self._apply_appearance_mode(AppColors.BG_COLOR)
        line_color = self._apply_appearance_mode((AppColors.PATTERN_LINE_COLOR_LIGHT, AppColors.PATTERN_LINE_COLOR_DARK))
        
        self.background_canvas.configure(bg=bg_color)

        # Рисуем диагональные линии
        for i in range(-width, width + height, 20):
            self.background_canvas.create_line(i, 0, i - height, height, fill=line_color, width=1)
            
        tk.Widget.lower(self.background_canvas)

    def create_main_tab(self):
        main_tab = self.tab_view.tab("Основные настройки")
        main_tab.grid_columnconfigure(0, weight=1)
        main_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        
        main_frame = ctk.CTkFrame(main_tab, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, fill="x", expand=False)
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main_frame, text="Выберите профиль настроек:", font=ctk.CTkFont(size=16, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.profile_combobox = ctk.CTkComboBox(main_frame, values=list(PROFILES.keys()), state="readonly", height=35, font=("", 14),
                                                fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR,
                                                button_color=self.accent_color, dropdown_fg_color=AppColors.FRAME_BG_COLOR,
                                                text_color=AppColors.TEXT_COLOR)
        self.profile_combobox.set(list(PROFILES.keys())[0])
        self.profile_combobox.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.apply_button = ctk.CTkButton(main_frame, text="Применить настройки", command=self.start_apply_thread, height=40, font=("", 14, "bold"),
                                          fg_color=self.accent_color, hover_color=self.accent_color)
        self.apply_button.grid(row=2, column=0, padx=10, pady=20, sticky="ew")

    def create_binds_tab(self):
        self.binds_tab = self.tab_view.tab("Бинды")
        self.binds_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        self.binds_tab.grid_columnconfigure(0, weight=1)
        self.binds_tab.grid_rowconfigure(1, weight=1)
        
        # --- ИЗМЕНЕНИЕ: Добавлен новый бинд "Зум экрана" ---
        self.managed_binds_definitions = [
            ("auto_run", 'Автобег (отключается кнопкой движения вперед)', 'forward;sprint'),
            ("quick_loot", 'Быстрый сбор (удерживать)', '+use'),
            ("screen_zoom", 'Зум экрана', '+fov 90;fov 70'), # <--- НОВЫЙ БИНД
            ("craft_bandage", 'Создать 1 бинт', 'craft.add -2072273936 1'),
            ("craft_syringe", 'Создать 1 шприц', 'craft.add 1079279582 1'),
            ("craft_arrows_5", 'Создать 5 стрел', 'craft.add -1234735557 5'),
            ("toggle_fps", 'Показать/скрыть информацию о FPS', 'perf 0; perf 1; perf 2; perf 3'),
            ("console_combatlog", 'Открыть консоль и комбатлог', 'consoletoggle;combatlog'),
            ("toggle_streamer", 'Включить/выключить режим стримера', 'streamermode false; streamermode true'),
            ("craft_barricade_wood", 'Создать 1 деревянную баррикаду', 'craft.add 1373240771 1'),
            ("craft_barricade_stone", 'Создать 1 каменную баррикаду', 'craft.add 15388698 1'),
            ("craft_cupboard", 'Создать 1 шкаф (Tool Cupboard)', 'craft.add -97956382 1'),
            ("craft_metal_door", 'Создать 1 металлическую двойную дверь', 'craft.add 1390353317 1'),
            ("suicide", 'Суицид', 'kill')
        ]
        
        managed_frame = ctk.CTkFrame(self.binds_tab, fg_color="transparent")
        managed_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        managed_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(managed_frame, text="Управляемые бинды (оставьте поле пустым для удаления):", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 15), sticky="w")
        for i, (key, description, command) in enumerate(self.managed_binds_definitions):
            ctk.CTkLabel(managed_frame, text=description, anchor="w", text_color=AppColors.TEXT_COLOR).grid(row=i + 1, column=0, padx=(10, 5), pady=5, sticky="w")
            entry = EntryWithContextMenu(managed_frame, placeholder_text="Клавиша",
                                         fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
            entry.grid(row=i + 1, column=1, padx=(5, 10), pady=5, sticky="ew")
            self.bind_entries[key] = {"entry": entry, "command": command}
        self.apply_binds_button = ctk.CTkButton(managed_frame, text="Применить изменения биндов", command=self.start_apply_binds_thread,
                                                fg_color=self.accent_color, hover_color=self.accent_color)
        self.apply_binds_button.grid(row=len(self.managed_binds_definitions) + 1, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        
        custom_frame = ctk.CTkFrame(self.binds_tab, fg_color="transparent")
        custom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        custom_frame.grid_columnconfigure(0, weight=1)
        custom_frame.grid_rowconfigure(1, weight=1)
        header_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text="Ваши остальные бинды (кроме стандартных):", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header_frame, text="🔄", width=30, command=self.populate_binds_from_file, fg_color="transparent", border_width=1, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR).grid(row=0, column=1, sticky="e")
        self.custom_binds_frame = ctk.CTkScrollableFrame(custom_frame, label_text="", fg_color="transparent")
        self.custom_binds_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.custom_binds_frame.grid_columnconfigure(1, weight=1)

    def create_calculators_tab(self):
        calc_tab = self.tab_view.tab("Калькуляторы")
        calc_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        calc_tab.grid_columnconfigure(0, weight=1)
        calc_tab.grid_rowconfigure(0, weight=1)

        calc_notebook = ctk.CTkTabview(calc_tab, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, 
                                       fg_color=AppColors.FRAME_BG_COLOR,
                                       segmented_button_fg_color=AppColors.FRAME_BG_COLOR,
                                       segmented_button_selected_color=self.accent_color,
                                       segmented_button_unselected_color=AppColors.FRAME_BG_COLOR,
                                       segmented_button_selected_hover_color=self.accent_color,
                                       segmented_button_unselected_hover_color=AppColors.BUTTON_HOVER_COLOR,
                                       text_color=AppColors.TEXT_COLOR)
        calc_notebook.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        calc_notebook.add("Рейд")
        calc_notebook.add("Постройка и Содержание")
        calc_notebook.add("Переработчик")

        # --- ВКЛАДКА РЕЙД-КАЛЬКУЛЯТОРА ---
        raid_sub_tab = calc_notebook.tab("Рейд")
        raid_sub_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        raid_sub_tab.grid_columnconfigure(0, weight=3)
        raid_sub_tab.grid_columnconfigure(1, weight=2)
        raid_sub_tab.grid_rowconfigure(0, weight=1)

        raid_input_frame = ctk.CTkFrame(raid_sub_tab, fg_color="transparent")
        raid_input_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        raid_input_frame.grid_columnconfigure(0, weight=1)
        raid_input_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(raid_input_frame, text="Цели для рейда", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, pady=(5,10))

        self.raid_table_frame = ctk.CTkScrollableFrame(raid_input_frame, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        self.raid_table_frame.grid(row=1, column=0, sticky="nsew")
        self.raid_table_frame.grid_columnconfigure(0, weight=2)
        self.raid_table_frame.grid_columnconfigure(1, weight=1)
        self.raid_item_entries = {}
        for i, item_name in enumerate(RAID_DATA.keys()):
            ctk.CTkLabel(self.raid_table_frame, text=item_name, text_color=AppColors.TEXT_COLOR).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = EntryWithContextMenu(self.raid_table_frame, width=80, placeholder_text="0",
                                         fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry.bind("<KeyRelease>", self.calculate_total_raid_cost)
            self.raid_item_entries[item_name] = entry

        raid_result_frame = ctk.CTkFrame(raid_sub_tab, fg_color="transparent")
        raid_result_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        raid_result_frame.grid_columnconfigure(0, weight=1)
        raid_result_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(raid_result_frame, text="Самый дешевый способ (по сере)", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, pady=(5,10))

        self.raid_cheapest_frame = ctk.CTkScrollableFrame(raid_result_frame, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        self.raid_cheapest_frame.grid(row=1, column=0, sticky="nsew")
        self.raid_cheapest_frame.grid_columnconfigure(1, weight=1)

        # --- ВКЛАДКА ПОСТРОЙКИ И СОДЕРЖАНИЯ ---
        build_sub_tab = calc_notebook.tab("Постройка и Содержание")
        build_sub_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        build_sub_tab.grid_columnconfigure(0, weight=1)
        build_sub_tab.grid_rowconfigure(0, weight=1)
        build_input_frame = ctk.CTkFrame(build_sub_tab, fg_color="transparent")
        build_input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        build_input_frame.grid_columnconfigure(0, weight=1)
        build_input_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(build_input_frame, text="Строительные блоки", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, pady=(5,10))

        self.build_table_frame = ctk.CTkScrollableFrame(build_input_frame, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        self.build_table_frame.grid(row=1, column=0, sticky="nsew")
        self.build_table_frame.grid_columnconfigure(0, weight=2)
        self.build_table_frame.grid_columnconfigure(1, weight=1)
        self.build_item_entries = {}
        self.total_block_count = 0
        for i, item_name in enumerate(BUILD_COSTS.keys()):
            ctk.CTkLabel(self.build_table_frame, text=item_name, text_color=AppColors.TEXT_COLOR).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = EntryWithContextMenu(self.build_table_frame, width=80, placeholder_text="0",
                                         fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry.bind("<KeyRelease>", self.calculate_total_build_cost)
            self.build_item_entries[item_name] = entry

        build_result_frame = ctk.CTkFrame(build_sub_tab, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        build_result_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        build_result_frame.grid_columnconfigure(0, weight=1)
        
        self.build_cost_label = ctk.CTkLabel(build_result_frame, text="Стоимость постройки: -", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR)
        self.build_cost_label.pack(pady=5, padx=10, anchor="w")
        self.upkeep_cost_label = ctk.CTkLabel(build_result_frame, text="Содержание (24ч): -", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR)
        self.upkeep_cost_label.pack(pady=5, padx=10, anchor="w")

        # --- ВКЛАДКА ПЕРЕРАБОТЧИКА ---
        recycler_sub_tab = calc_notebook.tab("Переработчик")
        recycler_sub_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        recycler_sub_tab.grid_columnconfigure(0, weight=3)
        recycler_sub_tab.grid_columnconfigure(1, weight=2)
        recycler_sub_tab.grid_rowconfigure(1, weight=1)

        recycler_input_frame = ctk.CTkFrame(recycler_sub_tab, fg_color="transparent")
        recycler_input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="new")
        recycler_input_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(recycler_input_frame, text="Режим переработки:", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, padx=(10,5), pady=10, sticky="w")
        self.recycler_mode = ctk.StringVar(value="Обычный")
        self.recycler_mode_switch = ctk.CTkSegmentedButton(recycler_input_frame, values=["Обычный", "Мирная зона"],
                                                     variable=self.recycler_mode, command=self.update_recycler_ui,
                                                     fg_color=AppColors.INPUT_BG_COLOR, selected_color=self.accent_color,
                                                     unselected_color=AppColors.INPUT_BG_COLOR, selected_hover_color=self.accent_color,
                                                     text_color=AppColors.TEXT_COLOR)
        self.recycler_mode_switch.grid(row=0, column=1, padx=(5,10), pady=10, sticky="w")

        recycler_left_frame = ctk.CTkFrame(recycler_sub_tab, fg_color="transparent")
        recycler_left_frame.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="nsew")
        recycler_left_frame.grid_columnconfigure(0, weight=1)
        recycler_left_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(recycler_left_frame, text="Компоненты для переработки", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, pady=(5,10))

        self.recycler_table_frame = ctk.CTkScrollableFrame(recycler_left_frame, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        self.recycler_table_frame.grid(row=1, column=0, sticky="nsew")
        self.recycler_table_frame.grid_columnconfigure(0, weight=2)
        self.recycler_table_frame.grid_columnconfigure(1, weight=1)
        self.recycler_item_entries = {}
        
        recycler_result_frame = ctk.CTkFrame(recycler_sub_tab, fg_color="transparent")
        recycler_result_frame.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="nsew")
        recycler_result_frame.grid_columnconfigure(0, weight=1)
        recycler_result_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(recycler_result_frame, text="Итоговый выход ресурсов", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, pady=(5,10))

        self.recycler_output_frame = ctk.CTkScrollableFrame(recycler_result_frame, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        self.recycler_output_frame.grid(row=1, column=0, sticky="nsew")
        self.recycler_output_frame.grid_columnconfigure(1, weight=1)
        
        self.update_recycler_ui()

    def create_server_manager_tab(self):
        server_tab = self.tab_view.tab("Менеджер серверов")
        server_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        server_tab.grid_columnconfigure(0, weight=1)
        server_tab.grid_rowconfigure(2, weight=1)

        desc_frame = ctk.CTkFrame(server_tab, fg_color="transparent")
        desc_frame.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")
        ctk.CTkLabel(desc_frame, text="Добавляйте серверы в избранное, отслеживайте их онлайн и подключайтесь в один клик.", wraplength=800, justify="left", text_color=AppColors.TEXT_SECONDARY_COLOR).pack(anchor="w")

        add_frame = ctk.CTkFrame(server_tab, fg_color="transparent")
        add_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        add_frame.grid_columnconfigure(0, weight=1)
        self.server_add_entry = EntryWithContextMenu(add_frame, placeholder_text="Введите IP:Порт сервера для добавления в избранное",
                                                     fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
        self.server_add_entry.grid(row=0, column=0, padx=(0,10), sticky="ew")
        self.server_add_button = ctk.CTkButton(add_frame, text="Добавить", width=100, command=self.add_favorite_server,
                                               fg_color=self.accent_color, hover_color=self.accent_color)
        self.server_add_button.grid(row=0, column=1)

        self.server_list_frame = ctk.CTkScrollableFrame(server_tab, label_text="Избранные серверы", fg_color="transparent", label_text_color=AppColors.TEXT_COLOR)
        self.server_list_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.server_list_frame.grid_columnconfigure(0, weight=1)

        self.load_favorite_servers()

    def create_combat_log_tab(self):
        combat_tab = self.tab_view.tab("Анализ боя")
        combat_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        combat_tab.grid_columnconfigure(0, weight=1)
        combat_tab.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(combat_tab, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20,0), sticky="ew")
        ctk.CTkLabel(header_frame, text="Скопируйте текст из консоли игры (F1) после ввода команды 'combatlog' и вставьте в поле ниже для анализа.", wraplength=800, justify="left", text_color=AppColors.TEXT_SECONDARY_COLOR).pack(anchor="w")
        
        ctk.CTkLabel(combat_tab, text="Вставьте сюда ваш combatlog:", font=ctk.CTkFont(size=14, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=1, column=0, padx=20, pady=(10,5), sticky="w")
        
        self.combat_input_textbox = TextboxWithContextMenu(combat_tab, wrap="word", border_width=1, border_color=AppColors.INPUT_BORDER_COLOR,
                                                           fg_color=AppColors.INPUT_BG_COLOR, text_color=AppColors.TEXT_COLOR)
        self.combat_input_textbox.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")

        analyze_button = ctk.CTkButton(combat_tab, text="Анализировать", command=self.analyze_combat_log,
                                       fg_color=self.accent_color, hover_color=self.accent_color)
        analyze_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.combat_output_textbox = TextboxWithContextMenu(combat_tab, state="disabled", wrap="word", border_width=1, border_color=AppColors.FRAME_BORDER_COLOR,
                                                            fg_color=AppColors.FRAME_BG_COLOR, text_color=AppColors.TEXT_COLOR)
        self.combat_output_textbox.grid(row=4, column=0, padx=20, pady=5, sticky="nsew")
        combat_tab.grid_rowconfigure(4, weight=1)

    def create_advanced_tab(self):
        adv_tab = self.tab_view.tab("Доп настройка")
        adv_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        adv_tab.grid_columnconfigure(0, weight=1)
        self.adv_settings_vars = {
            "no_legs": ctk.BooleanVar(value=False), "less_shake": ctk.BooleanVar(value=False),
            "orange_cross": ctk.BooleanVar(value=False), "no_gibs": ctk.BooleanVar(value=False),
            "no_blink": ctk.BooleanVar(value=False), "no_leg_splay": ctk.BooleanVar(value=False),
            "fast_alt_look": ctk.BooleanVar(value=False), "no_strobe": ctk.BooleanVar(value=False),
            "no_safezone": ctk.BooleanVar(value=False),
        }
        self.adv_settings_mapping = {
            "no_legs": "graphics.show_local_player false", "less_shake": "graphics.vm_recoil_scale 0; graphics.vm_bob_scale 0",
            "orange_cross": 'tree.color_decal_on_hit "1 0.5 0 1"', "no_gibs": "effects.gibs false",
            "no_blink": "player.eye_blinking false", "no_leg_splay": "player.leg_splay false",
            "fast_alt_look": "input.autofreeloookduration 0.01", "no_strobe": "effects.strobe 0",
            "no_safezone": "culling.safezone 0",
        }
        settings_labels = [
            ("Отключить отображение ног", "no_legs"), ("Уменьшить тряску камеры", "less_shake"),
            ("Улучшить видимость крестиков на деревьях (оранжевые)", "orange_cross"),
            ("Полностью отключить обломки (gibs)", "no_gibs"), ("Отключить моргание глаз у персонажей", "no_blink"),
            ("Отключить деформацию ног", "no_leg_splay"), ("Ускорить поворот головы через ALT", "fast_alt_look"),
            ("Полностью отключить стробоскопы", "no_strobe"), ("Отключить безопасный механизм отсечения окклюзии", "no_safezone"),
        ]
        adv_frame = ctk.CTkFrame(adv_tab, fg_color="transparent")
        adv_frame.pack(padx=20, pady=20, fill="x", expand=False)
        for i, (text, key) in enumerate(settings_labels):
            switch = ctk.CTkSwitch(adv_frame, text=text, variable=self.adv_settings_vars[key], switch_height=18, switch_width=36, corner_radius=10,
                                   progress_color=self.accent_color, text_color=AppColors.TEXT_COLOR)
            switch.grid(row=i, column=0, padx=20, pady=8, sticky="w")
        
        apply_adv_button = ctk.CTkButton(adv_frame, text="Применить доп. настройки", command=self.start_apply_advanced_thread, height=40, font=("", 14, "bold"),
                                         fg_color=self.accent_color, hover_color=self.accent_color)
        apply_adv_button.grid(row=len(settings_labels), column=0, padx=20, pady=(20,10), sticky="ew")

    def create_about_tab(self):
        about_tab = self.tab_view.tab("О создателе")
        about_tab.configure(fg_color=AppColors.FRAME_BG_COLOR)
        about_tab.grid_columnconfigure(0, weight=1)
        self.load_icons()
        socials = [
            ("youtube", "https://youtube.com/@rustfornew?si=tbFZPm6pgmlawAaU", "YouTube: Rust ForNew"),
            ("discord", "https://discord.gg/MjP85xw4RM", "Discord: Rust ForNew"),
            ("tg", "https://t.me/RustForNew", "ТГК: Rust ForNew"),
            ("tg", "https://t.me/RFNRustLook_bot", "tg bot: RustLook"),
            ("da", "https://www.donationalerts.com/r/rustfornew", "DonationAlerts")
        ]
        
        social_frame = ctk.CTkFrame(about_tab, fg_color="transparent")
        social_frame.pack(padx=20, pady=20, fill="x", expand=False)
        social_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(social_frame, text="Социальные сети и поддержка:", font=ctk.CTkFont(size=16, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        current_row = 1
        for key, url, text in socials:
            if key in self.icons:
                ctk.CTkButton(social_frame, text=text, image=self.icons[key], compound="left", anchor="w", command=lambda u=url: self.open_link(u),
                              fg_color="transparent", text_color=AppColors.TEXT_SECONDARY_COLOR, hover_color=AppColors.BUTTON_HOVER_COLOR).grid(row=current_row, column=0, padx=20, pady=10, sticky="ew")
                current_row += 1

        server_frame = ctk.CTkFrame(about_tab, fg_color="transparent")
        server_frame.pack(padx=20, pady=0, fill="x", expand=False)
        server_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(server_frame, text="Наш сервер Rust:", font=ctk.CTkFont(size=16, weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="w")
        
        server_connect_entry = EntryWithContextMenu(server_frame, fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
        server_connect_entry.insert(0, "connect 78.107.7.197:28016")
        server_connect_entry.configure(state="readonly")
        server_connect_entry.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="ew")

        copy_connect_button = ctk.CTkButton(server_frame, text="📋", width=35, command=lambda: self.copy_to_clipboard(server_connect_entry.get()),
                                            fg_color="transparent", border_width=1, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
        copy_connect_button.grid(row=1, column=1, padx=(0, 20), pady=(5, 15), sticky="w")

    # --- НОВЫЕ ФУНКЦИИ ДЛЯ НАСТРОЕК ---
    def create_settings_button(self):
        # Создаем иконку шестеренки программно
        gear_icon_image = self.create_gear_icon(size=20, color_light="#65676B", color_dark="#B0B3B8")
        self.settings_button = ctk.CTkButton(self, text="", image=gear_icon_image, width=30, height=30,
                                             fg_color="transparent", hover_color=AppColors.BUTTON_HOVER_COLOR,
                                             command=self.open_settings_window)
        self.settings_button.place(relx=1.0, rely=0.0, x=-25, y=15, anchor="ne")

    def create_gear_icon(self, size, color_light, color_dark):
        # Создаем два изображения для светлой и темной тем
        im_light = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw_light = ImageDraw.Draw(im_light)
        im_dark = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw_dark = ImageDraw.Draw(im_dark)

        # Используем системный шрифт для символа шестеренки
        try:
            font = ImageFont.truetype("seguiemj.ttf", size)
        except IOError:
            font = ImageFont.load_default()
        
        # Рисуем символ шестеренки '⚙'
        draw_light.text((0, 0), '⚙', font=font, fill=color_light)
        draw_dark.text((0, 0), '⚙', font=font, fill=color_dark)
        
        return ctk.CTkImage(light_image=im_light, dark_image=im_dark, size=(size, size))

    def open_settings_window(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Настройки")
        self.settings_window.geometry("350x250")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self)
        # FIX: Удален лишний вызов .configure(), который конфликтовал с авто-обновлением темы CTk
        
        settings_frame = ctk.CTkFrame(self.settings_window, fg_color="transparent")
        settings_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Переключение темы
        ctk.CTkLabel(settings_frame, text="Тема оформления", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        theme_switch = ctk.CTkSegmentedButton(settings_frame, values=["Тёмная", "Светлая"], command=self.change_theme,
                                              fg_color=AppColors.INPUT_BG_COLOR, selected_color=self.accent_color,
                                              unselected_color=AppColors.INPUT_BG_COLOR, selected_hover_color=self.accent_color,
                                              text_color=AppColors.TEXT_COLOR)
        theme_switch.set("Тёмная" if ctk.get_appearance_mode() == "Dark" else "Светлая")
        theme_switch.pack(fill="x", pady=(0, 20))

        # Выбор акцентного цвета
        ctk.CTkLabel(settings_frame, text="Акцентный цвет", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        color_button = ctk.CTkButton(settings_frame, text="Выбрать цвет", command=self.choose_accent_color,
                                     fg_color=self.accent_color, hover_color=self.accent_color)
        color_button.pack(fill="x")

    def change_theme(self, theme_str):
        mode = "Dark" if theme_str == "Тёмная" else "Light"
        ctk.set_appearance_mode(mode)
        self.draw_background_pattern() # UI: Перерисовываем фон при смене темы

    def choose_accent_color(self):
        color_code = colorchooser.askcolor(title="Выберите акцентный цвет", initialcolor=self.accent_color, parent=self.settings_window)
        if color_code and color_code[1]:
            self.accent_color = color_code[1]
            self.apply_accent_color()

    def apply_accent_color(self):
        # Применяем новый цвет ко всем элементам, которые его используют
        self.tab_view.configure(segmented_button_selected_color=self.accent_color,
                                segmented_button_selected_hover_color=self.accent_color)
        
        # Обновляем цвет в дочерних табвью (калькуляторы)
        calc_notebook = self.tab_view.tab("Калькуляторы").winfo_children()[0]
        calc_notebook.configure(segmented_button_selected_color=self.accent_color,
                                segmented_button_selected_hover_color=self.accent_color)

        # Обновляем кнопки
        self.apply_button.configure(fg_color=self.accent_color, hover_color=self.accent_color)
        self.apply_binds_button.configure(fg_color=self.accent_color, hover_color=self.accent_color)
        self.server_add_button.configure(fg_color=self.accent_color, hover_color=self.accent_color)
        # FIX: Исправлен индекс с 2 на 3 для корректного выбора кнопки "Анализировать"
        self.tab_view.tab("Анализ боя").winfo_children()[3].configure(fg_color=self.accent_color, hover_color=self.accent_color) # Кнопка "Анализировать"
        self.tab_view.tab("Доп настройка").winfo_children()[0].winfo_children()[-1].configure(fg_color=self.accent_color, hover_color=self.accent_color) # Кнопка "Применить доп. настройки"
        
        # Обновляем переключатели
        self.recycler_mode_switch.configure(selected_color=self.accent_color, selected_hover_color=self.accent_color)
        for switch in self.tab_view.tab("Доп настройка").winfo_children()[0].winfo_children():
            if isinstance(switch, ctk.CTkSwitch):
                switch.configure(progress_color=self.accent_color)
        
        # Обновляем комбо-бокс
        self.profile_combobox.configure(button_color=self.accent_color)

        # Обновляем кнопку в окне настроек, если оно открыто
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.winfo_children()[0].winfo_children()[-1].configure(fg_color=self.accent_color, hover_color=self.accent_color)
            self.settings_window.winfo_children()[0].winfo_children()[1].configure(selected_color=self.accent_color, selected_hover_color=self.accent_color)

    # --- ЛОГИКА НОВЫХ ФУНКЦИЙ ---

    def log(self, message):
        def _perform_log_update():
            now = datetime.now().strftime("%H:%M:%S")
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", f"[{now}] {message}\n")
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")
        self.after(0, _perform_log_update)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.log(f"Текст '{text}' скопирован в буфер обмена.")
        messagebox.showinfo("Скопировано", f"Текст '{text}' скопирован в буфер обмена.")

    def calculate_total_raid_cost(self, event=None):
        for widget in self.raid_cheapest_frame.winfo_children():
            widget.destroy()

        total_raid_plan = {}
        for item_name, entry in self.raid_item_entries.items():
            try:
                quantity = int(entry.get())
                if quantity > 0:
                    total_raid_plan[item_name] = quantity
            except (ValueError, TypeError):
                continue

        if not total_raid_plan:
            ctk.CTkLabel(self.raid_cheapest_frame, text="Введите количество целей.", text_color=AppColors.TEXT_SECONDARY_COLOR).pack(pady=10, padx=10)
            return

        cheapest_explosives_summary = {}
        
        for item_name, quantity in total_raid_plan.items():
            raid_methods = RAID_DATA.get(item_name, [])
            best_method_for_item = None
            min_sulfur_for_item = float('inf')

            for method in raid_methods:
                current_sulfur = 0
                for tool, amount in method["cost"].items():
                    if tool in CRAFT_COSTS and "Сера" in CRAFT_COSTS[tool]:
                        current_sulfur += CRAFT_COSTS[tool]["Сера"] * amount
                
                if current_sulfur < min_sulfur_for_item:
                    min_sulfur_for_item = current_sulfur
                    best_method_for_item = method

            if best_method_for_item:
                for tool, amount in best_method_for_item["cost"].items():
                    cheapest_explosives_summary.setdefault(tool, 0)
                    cheapest_explosives_summary[tool] += amount * quantity
        
        total_craft_cost = {}
        for explosive, total_amount in cheapest_explosives_summary.items():
            if explosive in CRAFT_COSTS:
                for resource, cost_per_one in CRAFT_COSTS[explosive].items():
                    total_craft_cost.setdefault(resource, 0)
                    total_craft_cost[resource] += cost_per_one * total_amount

        ctk.CTkLabel(self.raid_cheapest_frame, text="Необходимая взрывчатка:", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR).pack(anchor="w", padx=10, pady=(10, 5))
        if not cheapest_explosives_summary:
            ctk.CTkLabel(self.raid_cheapest_frame, text="-", text_color=AppColors.TEXT_COLOR).pack(anchor="w", padx=10)
        else:
            for explosive, amount in sorted(cheapest_explosives_summary.items()):
                ctk.CTkLabel(self.raid_cheapest_frame, text=f" • {explosive}: {amount} шт.", text_color=AppColors.TEXT_COLOR).pack(anchor="w", padx=10)

        ctk.CTkLabel(self.raid_cheapest_frame, text="Общие ресурсы для крафта:", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR).pack(anchor="w", padx=10, pady=(15, 5))
        if not total_craft_cost:
            ctk.CTkLabel(self.raid_cheapest_frame, text="-", text_color=AppColors.TEXT_COLOR).pack(anchor="w", padx=10, pady=(0, 10))
        else:
            for resource, amount in sorted(total_craft_cost.items()):
                ctk.CTkLabel(self.raid_cheapest_frame, text=f" • {resource}: {int(amount):,} шт.".replace(",", " "), text_color=AppColors.TEXT_COLOR).pack(anchor="w", padx=10)

    def calculate_total_build_cost(self, event=None):
        total_build_cost = {"Дерево": 0, "Камень": 0, "Металл": 0, "МВК": 0}
        self.total_block_count = 0

        for item_name, entry in self.build_item_entries.items():
            try:
                quantity = int(entry.get())
                if quantity > 0:
                    self.total_block_count += quantity
                    item_build_data = BUILD_COSTS.get(item_name, {})
                    for resource, amount in item_build_data.items():
                        total_build_cost[resource] += quantity * amount
            except (ValueError, TypeError):
                continue

        cost_str = ", ".join([f'{v:,} {k}'.replace(",", " ") for k, v in total_build_cost.items() if v > 0])
        self.build_cost_label.configure(text=f"Стоимость постройки: {cost_str if cost_str else '-'}")
        
        upkeep_multiplier = 0.1 + (0.033 * (self.total_block_count // 10))
        upkeep_multiplier = min(upkeep_multiplier, 0.333)

        upkeep_cost = {res: round(val * upkeep_multiplier) for res, val in total_build_cost.items()}
        upkeep_str = ", ".join([f'{v:,} {k}'.replace(",", " ") for k, v in upkeep_cost.items() if v > 0])
        self.upkeep_cost_label.configure(text=f"Содержание (24ч): {upkeep_str if upkeep_str else '-'}")

    def update_recycler_ui(self, event=None):
        for widget in self.recycler_table_frame.winfo_children():
            widget.destroy()
        self.recycler_item_entries.clear()

        mode = self.recycler_mode.get()
        data_source = RECYCLER_DATA_NORMAL if mode == "Обычный" else RECYCLER_DATA_SAFEZONE

        for i, item_name in enumerate(data_source.keys()):
            ctk.CTkLabel(self.recycler_table_frame, text=item_name, text_color=AppColors.TEXT_COLOR).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = EntryWithContextMenu(self.recycler_table_frame, width=80, placeholder_text="0",
                                         fg_color=AppColors.INPUT_BG_COLOR, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_COLOR)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="e")
            entry.bind("<KeyRelease>", self.calculate_total_recycle_yield)
            self.recycler_item_entries[item_name] = entry
        
        self.calculate_total_recycle_yield()

    def calculate_total_recycle_yield(self, event=None):
        total_yield_processed = {} 
        mode = self.recycler_mode.get()
        data_source = RECYCLER_DATA_NORMAL if mode == "Обычный" else RECYCLER_DATA_SAFEZONE

        aggregated_raw_yield = {}
        for item_name, entry in self.recycler_item_entries.items():
            try:
                quantity = int(entry.get())
                if quantity > 0:
                    item_yield_data = data_source.get(item_name, [])
                    for resource_info in item_yield_data:
                        res_name = resource_info["item"]
                        res_qty_str = str(resource_info["quantity"]) 

                        if res_name not in aggregated_raw_yield:
                            aggregated_raw_yield[res_name] = []
                        aggregated_raw_yield[res_name].append((res_qty_str, quantity))
            except (ValueError, TypeError):
                continue

        for res_name, qty_list in aggregated_raw_yield.items():
            if mode == "Обычный":
                total_amount = sum(int(qty_str) * multiplier for qty_str, multiplier in qty_list)
                total_yield_processed[res_name] = str(total_amount)
            else: 
                min_total = 0.0
                max_total = 0.0
                is_fully_numeric = True

                for qty_str, multiplier in qty_list:
                    if '-' in qty_str:
                        parts = qty_str.split('-')
                        try:
                            min_val = float(parts[0])
                            max_val = float(parts[1])
                            min_total += min_val * multiplier
                            max_total += max_val * multiplier
                        except ValueError:
                            is_fully_numeric = False
                            break
                    else:
                        try:
                            val = float(qty_str)
                            min_total += val * multiplier
                            max_total += val * multiplier
                        except ValueError:
                            is_fully_numeric = False
                            break
                
                if is_fully_numeric:
                    if min_total == max_total:
                        total_yield_processed[res_name] = str(int(min_total)) if min_total.is_integer() else f"{min_total:.1f}"
                    else:
                        min_str = str(int(min_total)) if min_total.is_integer() else f"{min_total:.1f}"
                        max_str = str(int(max_total)) if max_total.is_integer() else f"{max_total:.1f}"
                        total_yield_processed[res_name] = f"{min_str}-{max_str}"
                else:
                    total_yield_processed[res_name] = "Неизвестно"
        
        for widget in self.recycler_output_frame.winfo_children():
            widget.destroy()
            
        if not total_yield_processed:
            ctk.CTkLabel(self.recycler_output_frame, text="Введите количество компонентов.", text_color=AppColors.TEXT_SECONDARY_COLOR).pack(pady=10)
        else:
            i = 0
            for resource, display_text in sorted(total_yield_processed.items()):
                ctk.CTkLabel(self.recycler_output_frame, text=f"{resource}:", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR).grid(row=i, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(self.recycler_output_frame, text=display_text, text_color=AppColors.TEXT_COLOR).grid(row=i, column=1, padx=10, pady=5, sticky="w")
                i += 1

    def extract_weapon_name(self, weapon_path):
        if weapon_path == "N/A":
            return "Неизвестное оружие"
        
        weapon_map = {
            "python": "Python", "pistol_revolver": "Револьвер", "thompson": "Thompson",
            "semi_auto_pistol": "Полуавтоматический пистолет", "pistol_semiauto": "Полуавтоматический пистолет",
            "semi_auto_rifle": "Полуавтоматическая винтовка",
            "pipe shotgun": "Самодельный дробовик", "lr300": "LR-300", "ak47u": "AK47", "smg": "SMG",
            "shotgun_pump": "Помповый дробовик", "shotgun_waterpipe": "Самодельный дробовик", "shotgun_double": "Двуствольный дробовик", "l96": "L96",
            "m249": "M249", "hmlmg": "HMLMG", "crossbow": "Арбалет", "bow": "Лук", "nailgun": "Гвоздемет",
            "eoka_pistol": "Эока", "speargun": "Гарпун", "flamethrower": "Огнемет",
            "grenade_f1": "Граната F1", "rocket_launcher": "Ракетница", "mlrs": "MLRS", "mace": "Булава",
            "longsword": "Длинный меч", "salvaged_sword": "Самодельный меч",
            "salvaged_icepick": "Самодельный ледоруб", "salvaged_axe": "Самодельный топор",
            "salvaged_cleaver": "Самодельный тесак", "stone_axe": "Каменный топор",
            "stone_pickaxe": "Каменная кирка", "hatchet": "Топор", "pickaxe": "Кирка", "torch": "Факел",
            "rock": "Камень", "knife_bone": "Костяной нож", "machete": "Мачете", "sickle": "Серп",

            "jackhammer": "Отбойный молоток", "chainsaw": "Бензопила", "custom_smg": "Самодельный SMG",
            "mp5": "MP5", "m92_pistol": "M92 Пистолет", "spas12": "SPAS-12",
            "waterpipe.entity": "Самодельный дробовик", "waterpipe": "Самодельный дробовик",
            "grenade_beancan": "Самодельная граната", "grenade_smoke": "Дымовая граната",
            "grenade_flashbang": "Светошумовая граната", "landmine": "Мина", "bear_trap": "Капкан",
            "c4": "C4", "rocket_basic": "Ракета", "rocket_hv": "Скоростная ракета",
            "rocket_incendiary": "Зажигательная ракета", "satchel_charge": "Сачель",
            "explosive_ammo": "Взрывные патроны", "incendiary_ammo": "Зажигательные патроны",
            "hv_ammo": "Скоростные патроны", "shotgun_slug": "Дробовой патрон",
            "shotgun_buckshot": "Картечь", "shotgun_incendiary": "Зажигательная картечь",
            "pistol_bullet": "Пистолетный патрон", "rifle_bullet": "Винтовочный патрон",
            "arrow_wooden": "Деревянная стрела", "arrow_hv": "Скоростная стрела",
            "arrow_incendiary": "Зажигательная стрела", "arrow_explosive": "Взрывная стрела",
            "molotov": "Коктейль Молотова", "flame_turret": "Огненная турель",
            "auto_turret": "Автоматическая турель", "shotgun_trap": "Дробовая ловушка", "sam_site": "ЗРК",
            "patrol_helicopter": "Патрульный вертолет", "bradley_apc": "Брэдли БМП",
            "scientist": "Ученый", "mutant_bear": "Медведь-мутант", "mutant_wolf": "Волк-мутант",
            "boar": "Кабан", "bear": "Медведь", "wolf": "Волк", "chicken": "Курица", "stag": "Олень",
            "horse": "Лошадь", "player": "Игрок", "entity": "Сущность",
        }
        
        match = re.search(r'/weapons/([^/]+)/([^/]+)\.entity\.prefab', weapon_path)
        if match:
            prefab_name = match.group(2).lower().replace("_", " ")
            if prefab_name in weapon_map:
                return weapon_map[prefab_name]
            
            folder_name = match.group(1).lower().replace("_", " ")
            if folder_name in weapon_map:
                return weapon_map[folder_name]
            
            return prefab_name.title()

        lower_path = weapon_path.lower()
        for key, value in weapon_map.items():
            if key.replace(" ", "_") in lower_path.replace(" ", "_"):
                return value
        
        return weapon_path

    def analyze_combat_log(self):
        log_text = self.combat_input_textbox.get("1.0", "end")
        if not log_text.strip():
            self.update_combat_output("Поле ввода пустое.")
            return

        total_damage_dealt_by_you = 0.0
        total_damage_taken_by_you = 0.0
        your_shots_fired = 0
        your_hits = 0

        damage_dealt_by_weapon = defaultdict(float)
        damage_dealt_to_target = defaultdict(float)
        damage_taken_by_weapon = defaultdict(float)
        damage_taken_from_attacker = defaultdict(float)

        damage_dealt_by_you_per_weapon_per_target = defaultdict(lambda: defaultdict(float))
        damage_taken_by_you_per_weapon_from_attacker = defaultdict(lambda: defaultdict(float))

        kill_pattern = re.compile(r"you killed (\w+)")
        death_pattern = re.compile(r"(\w+) killed you")
        kills = defaultdict(int)
        deaths = defaultdict(int)

        log_line_pattern = re.compile(
            r'^\d{1,3}\.\d{2}s\s+'                                  # time (e.g., 24.84s)
            r'(?P<attacker>\S+)\s+'                                 # attacker (e.g., you, player_1816149)
            r'(?P<target>\S+)\s+'                                   # target (e.g., player_1816149, you)
            r'(?P<weapon_path>.*?\.entity\.prefab|N/A)\s+'          # weapon_path (non-greedy match until .entity.prefab or N/A)
            r'(?P<ammo>\S+)\s+'                                     # ammo (e.g., shotgunbullet, riflebullet)
            r'(?P<area>\S+)\s+'                                     # hit area (e.g., arm, head, chest)
            r'(?P<distance>\S+)\s+'                                 # distance (e.g., 2.1m)
            r'(?P<old_hp>\d+\.\d+)\s+'                              # old_hp (e.g., 100.0)
            r'(?P<new_hp>\d+\.\d+)'                                 # new_hp (e.g., 88.0)
            r'(?P<trailing_data>.*)$'                               # Everything after new_hp
        )

        for line in log_text.splitlines():
            line = line.strip()
            if not line or "time   attacker" in line or "accessibility.holosightcolour" in line or "Look rotation viewing vector is zero" in line or line.startswith("+"):
                continue
            
            match = log_line_pattern.match(line)

            if match:
                data = match.groupdict()
                attacker = data['attacker']
                target = data['target']
                weapon_path = data['weapon_path']
                old_hp = float(data['old_hp'])
                new_hp = float(data['new_hp'])
                trailing_data = data['trailing_data']

                info = None
                
                trailing_parts = trailing_data.strip().split()
                if trailing_parts:
                    if not re.match(r'^-?\d+(\.\d+)?$', trailing_parts[0]):
                        info = trailing_parts[0]
                
                weapon_name = self.extract_weapon_name(weapon_path)
                
                if attacker == "you":
                    if info != "attack_cooldown":
                        your_shots_fired += 1
                    
                    if new_hp < old_hp:
                        your_hits += 1

                if new_hp < old_hp:
                    damage_amount = old_hp - new_hp
                    
                    if attacker == "you" and target != "you":
                        total_damage_dealt_by_you += damage_amount
                        damage_dealt_by_weapon[weapon_name] += damage_amount
                        if target != "N/A":
                            damage_dealt_to_target[target] += damage_amount
                            damage_dealt_by_you_per_weapon_per_target[weapon_name][target] += damage_amount
                    elif target == "you" and attacker != "you":
                        total_damage_taken_by_you += damage_amount
                        damage_taken_by_weapon[weapon_name] += damage_amount
                        if attacker != "N/A":
                            damage_taken_from_attacker[attacker] += damage_amount
                            damage_taken_by_you_per_weapon_from_attacker[weapon_name][attacker] += damage_amount
            else:
                match_kill = kill_pattern.search(line)
                if match_kill:
                    kills[match_kill.group(1)] += 1
                    continue

                match_death = death_pattern.search(line)
                if match_death:
                    deaths[match_death.group(1)] += 1
                    continue

        hit_percentage = (your_hits / your_shots_fired * 100) if your_shots_fired > 0 else 0.0

        report = "--- АНАЛИЗ БОЯ ---\n\n"

        report += "--- ОБЩАЯ СТАТИСТИКА ---\n"
        report += f"  •  Всего урона нанесено: {total_damage_dealt_by_you:.1f}\n"
        report += f"  •  Всего урона получено: {total_damage_taken_by_you:.1f}\n"
        report += f"  •  Всего выстрелов: {your_shots_fired}\n"
        report += f"  •  Всего попаданий: {your_hits}\n"
        report += f"  •  Процент попаданий: {hit_percentage:.2f}%\n\n"

        report += "--- НАНЕСЕННЫЙ УРОН ---\n"
        if not damage_dealt_by_you_per_weapon_per_target:
            report += "Нет данных.\n"
        else:
            sorted_weapons_dealt = sorted(damage_dealt_by_weapon.items(), key=lambda item: item[1], reverse=True)
            for weapon, total_dmg_from_weapon in sorted_weapons_dealt:
                if total_dmg_from_weapon > 0:
                    report += f"  •  С оружия '{weapon}': {total_dmg_from_weapon:.1f} урона\n"
                    targets_hit_by_this_weapon = sorted(
                        damage_dealt_by_you_per_weapon_per_target[weapon].items(),
                        key=lambda item: item[1], reverse=True
                    )
                    for target, dmg_to_target in targets_hit_by_this_weapon:
                        report += f"      - Кому: {target}, Урон: {dmg_to_target:.1f}\n"
        report += "\n"

        report += "--- ПОЛУЧЕННЫЙ УРОН ---\n"
        if not damage_taken_by_you_per_weapon_from_attacker:
            report += "Нет данных.\n"
        else:
            sorted_weapons_taken = sorted(damage_taken_by_weapon.items(), key=lambda item: item[1], reverse=True)
            for weapon, total_dmg_from_weapon in sorted_weapons_taken:
                 if total_dmg_from_weapon > 0:
                    report += f"  •  От оружия '{weapon}': {total_dmg_from_weapon:.1f} урона\n"
                    attackers_with_this_weapon = sorted(
                        damage_taken_by_you_per_weapon_from_attacker[weapon].items(),
                        key=lambda item: item[1], reverse=True
                    )
                    for attacker, dmg_from_attacker in attackers_with_this_weapon:
                        report += f"      - От кого: {attacker}, Урон: {dmg_from_attacker:.1f}\n"
        report += "\n"

        report += "--- УБИЙСТВА ---\n"
        if not kills: report += "Нет данных.\n"
        else:
            for target, count in sorted(kills.items(), key=lambda item: item[1], reverse=True):
                report += f"  •  {target} (x{count})\n"

        report += "\n--- СМЕРТИ ---\n"
        if not deaths: report += "Нет данных.\n"
        else:
            for killer, count in sorted(deaths.items(), key=lambda item: item[1], reverse=True):
                report += f"  •  От {killer} (x{count})\n"

        self.update_combat_output(report)

    def update_combat_output(self, text):
        self.combat_output_textbox.configure(state="normal")
        self.combat_output_textbox.delete("1.0", "end")
        self.combat_output_textbox.insert("1.0", text)
        self.combat_output_textbox.configure(state="disabled")

    def load_favorite_servers(self):
        for widget in self.server_list_frame.winfo_children():
            widget.destroy()

        try:
            with open("favorites.json", "r") as f:
                self.favorite_servers = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.favorite_servers = []

        if not self.favorite_servers:
            ctk.CTkLabel(self.server_list_frame, text="Нет избранных серверов. Добавьте первый!", text_color=AppColors.TEXT_SECONDARY_COLOR).pack(pady=10)
        else:
            for server_address in self.favorite_servers:
                self.display_server_in_list(server_address)

    def save_favorite_servers(self):
        with open("favorites.json", "w") as f:
            json.dump(self.favorite_servers, f, indent=2)

    def add_favorite_server(self):
        address = self.server_add_entry.get().strip()
        if not address:
            messagebox.showwarning("Пустое поле", "Введите адрес сервера.")
            return
        if address in self.favorite_servers:
            messagebox.showinfo("Уже в списке", "Этот сервер уже есть в избранном.")
            return
        
        self.favorite_servers.append(address)
        self.save_favorite_servers()
        self.load_favorite_servers()
        self.server_add_entry.delete(0, "end")
        self.log(f"Сервер {address} добавлен в избранное.")

    def remove_favorite_server(self, address):
        self.favorite_servers.remove(address)
        self.save_favorite_servers()
        self.load_favorite_servers()
        self.log(f"Сервер {address} удален из избранного.")

    def display_server_in_list(self, address):
        server_frame = ctk.CTkFrame(self.server_list_frame, border_width=1, border_color=AppColors.FRAME_BORDER_COLOR, fg_color=AppColors.FRAME_BG_COLOR)
        server_frame.pack(fill="x", pady=5, padx=5)
        server_frame.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(server_frame, fg_color="transparent")
        top_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,0))
        top_row.grid_columnconfigure(0, weight=1)
        name_label = ctk.CTkLabel(top_row, text=f"Загрузка данных для {address}...", anchor="w", font=ctk.CTkFont(weight="bold"), text_color=AppColors.TEXT_COLOR)
        name_label.grid(row=0, column=0, sticky="w")
        online_label = ctk.CTkLabel(top_row, text="?/?", anchor="e", text_color=AppColors.TEXT_COLOR)
        online_label.grid(row=0, column=1, sticky="e")

        bottom_row = ctk.CTkFrame(server_frame, fg_color="transparent")
        bottom_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,5))
        bottom_row.grid_columnconfigure(0, weight=1)
        map_wipe_label = ctk.CTkLabel(bottom_row, text="Карта: ? | Вайп: ?", anchor="w", text_color=AppColors.TEXT_SECONDARY_COLOR)
        map_wipe_label.grid(row=0, column=0, sticky="w")

        buttons_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")
        connect_button = ctk.CTkButton(buttons_frame, text="Подключиться", width=100, command=lambda a=address: self.connect_to_server(a),
                                       fg_color=self.accent_color, hover_color=self.accent_color)
        connect_button.pack(side="left", padx=(0, 5))
        remove_button = ctk.CTkButton(buttons_frame, text="🗑️", width=30, fg_color="transparent", border_width=1, border_color=AppColors.INPUT_BORDER_COLOR, text_color=AppColors.TEXT_SECONDARY_COLOR, command=lambda a=address: self.remove_favorite_server(a))
        remove_button.pack(side="left")

        threading.Thread(target=self._query_server_bm, args=(address, name_label, online_label, map_wipe_label), daemon=True).start()

    def connect_to_server(self, address):
        command = f"connect {address}"
        self.copy_to_clipboard(command)

    def _query_server_bm(self, address, name_label, online_label, map_wipe_label):
        if BM_API_KEY == "YOUR_API_KEY_HERE":
            self.log("Ошибка: API ключ BattleMetrics не установлен.")
            self.after(0, lambda: name_label.configure(text=f"Ошибка API ключа для {address}"))
            return

        headers = {"Authorization": f"Bearer {BM_API_KEY}"}
        
        try:
            # Проверяем формат адреса, но для запроса используем полный адрес
            req_ip, req_port_str = address.split(":")
            req_port = int(req_port_str)
        except ValueError:
            self.log(f"Неверный формат адреса сервера: {address}")
            self.after(0, lambda: name_label.configure(text=f"Неверный формат: {address}"))
            return

        # FIX: Используем правильный параметр 'filter[search]' вместо 'filter[ip]'
        # Передаем полный адрес для поиска
        params = {"filter[search]": address, "filter[game]": "rust", "page[size]": 5}
        
        try:
            response = requests.get(BM_API_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            found_server = None
            if data.get("data"):
                for server_data in data["data"]:
                    s_attr = server_data["attributes"]
                    # Проверяем совпадение IP, а затем одного из портов (игрового или query)
                    if s_attr.get("ip") == req_ip and (s_attr.get("port") == req_port or s_attr.get("portQuery") == req_port):
                        found_server = s_attr
                        break
            
            if not found_server:
                raise ValueError(f"Сервер {address} не найден в результатах поиска.")

            server_name = found_server['name']
            players = found_server['players']
            max_players = found_server['maxPlayers']
            map_name = found_server['details']['map']
            
            last_wipe_str = found_server['details'].get('rust_last_wipe', 'Неизвестно')
            wipe_date = "Неизвестно"
            if last_wipe_str != 'Неизвестно':
                try:
                    dt_object = datetime.fromisoformat(last_wipe_str.replace('Z', '+00:00'))
                    wipe_date = dt_object.strftime('%d.%m.%Y')
                except ValueError:
                    wipe_date = "Ошибка даты"

            self.after(0, lambda: name_label.configure(text=server_name))
            self.after(0, lambda: online_label.configure(text=f"{players}/{max_players}"))
            self.after(0, lambda: map_wipe_label.configure(text=f"Карта: {map_name} | Вайп: {wipe_date}"))

        except Exception as e:
            self.log(f"Ошибка при запросе к BM для {address}: {e}")
            self.after(0, lambda: name_label.configure(text=f"Ошибка загрузки для {address}"))

    def update_advanced_settings_switches(self):
        client_cfg_path = self.get_client_cfg_path()
        if not client_cfg_path or not client_cfg_path.exists():
            for key in self.adv_settings_vars:
                self.adv_settings_vars[key].set(False)
            return

        try:
            with open(client_cfg_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            for key, cmd_string in self.adv_settings_mapping.items():
                is_active = True
                for cmd in cmd_string.split(';'):
                    cmd_stripped = cmd.strip()
                    if cmd_stripped and cmd_stripped not in content:
                        is_active = False
                        break
                self.adv_settings_vars[key].set(is_active)
            self.log("Состояние доп. настроек обновлено из client.cfg.")
        except Exception as e:
            self.log(f"Ошибка при чтении client.cfg для обновления переключателей: {e}")

    def on_tab_change(self, tab_name=None):
        pass

    def get_keys_cfg_path(self):
        if not self.rust_path: return None
        return self.rust_path / "cfg" / "keys.cfg"

    def get_client_cfg_path(self):
        if not self.rust_path: return None
        return self.rust_path / "cfg" / "client.cfg"

    def _parse_bind_line(self, line):
        line = line.strip()
        if not line.lower().startswith('bind '): return None
        parts_str = line[5:].lstrip()
        key_part, command_part = None, None
        if parts_str.startswith('"'):
            end_quote_idx = parts_str.find('"', 1)
            if end_quote_idx == -1: return None
            key_part = parts_str[1:end_quote_idx]
            remaining_str = parts_str[end_quote_idx+1:].lstrip()
        else:
            space_idx = parts_str.find(' ')
            if space_idx == -1: return None
            key_part = parts_str[:space_idx]
            remaining_str = parts_str[space_idx:].lstrip()
        if remaining_str.startswith('"') and remaining_str.endswith('"'): command_part = remaining_str[1:-1]
        else: command_part = remaining_str
        if key_part and command_part: return key_part, command_part
        return None
    def _normalize_command(self, command_str):
        command_str = command_str.strip().lower()
        command_str = re.sub(r'\s*;\s*', ';', command_str)
        command_str = re.sub(r'\s+', ' ', command_str)
        return command_str
    def parse_keys_cfg(self):
        keys_cfg_path = self.get_keys_cfg_path()
        managed_binds, user_binds = {}, []
        if not keys_cfg_path or not keys_cfg_path.exists():
            self.log(f"Файл keys.cfg не найден по пути: {keys_cfg_path}"); return managed_binds, user_binds
        command_to_internal_key_map = {self._normalize_command(data['command']): key for key, data in self.bind_entries.items()}
        normalized_default_commands = {self._normalize_command(cmd) for cmd in DEFAULT_RUST_COMMANDS}
        try:
            content = None
            for encoding in ['utf-8', 'cp1251', 'latin-1']:
                try:
                    with open(keys_cfg_path, 'r', encoding=encoding) as f: content = f.readlines()
                    break
                except (UnicodeDecodeError, TypeError): continue
            if content is None: self.log("Не удалось прочитать keys.cfg."); return managed_binds, user_binds
            for line in content:
                parsed_data = self._parse_bind_line(line)
                if parsed_data:
                    key_from_cfg, command_from_cfg_raw = parsed_data
                    is_default = False
                    sub_commands = self._normalize_command(command_from_cfg_raw).split(';')
                    for sub_cmd in sub_commands:
                        if sub_cmd in normalized_default_commands: is_default = True; break
                    is_managed = self._normalize_command(command_from_cfg_raw) in command_to_internal_key_map
                    if is_managed:
                        internal_key_id = command_to_internal_key_map[self._normalize_command(command_from_cfg_raw)]
                        managed_binds[internal_key_id] = key_from_cfg
                    elif not is_default: user_binds.append((key_from_cfg, command_from_cfg_raw))
        except Exception as e: self.log(f"Критическая ошибка при разборе keys.cfg: {e}")
        return managed_binds, user_binds
    def populate_binds_from_file(self):
        if not self.rust_path: self.log("Путь к Rust не найден, не могу прочитать бинды."); return
        self.log("Чтение и отображение текущих биндов из keys.cfg в UI...")
        managed_binds, user_binds = self.parse_keys_cfg()
        for internal_key_id, data in self.bind_entries.items():
            entry = data["entry"]
            entry.delete(0, "end")
            if internal_key_id in managed_binds: entry.insert(0, managed_binds[internal_key_id])
        for widget in self.custom_binds_frame.winfo_children(): widget.destroy()
        if not user_binds: ctk.CTkLabel(self.custom_binds_frame, text="Другие пользовательские бинды не найдены.", text_color=AppColors.TEXT_SECONDARY_COLOR).pack(pady=10)
        else:
            self.custom_binds_frame.grid_columnconfigure(0, weight=0, minsize=120)
            self.custom_binds_frame.grid_columnconfigure(1, weight=1)
            for i, (key, command) in enumerate(sorted(user_binds)):
                key_label = ctk.CTkLabel(self.custom_binds_frame, text=key, font=ctk.CTkFont(weight="bold"), anchor="w", text_color=AppColors.TEXT_COLOR)
                key_label.grid(row=i, column=0, padx=(5, 10), pady=3, sticky="w")
                cmd_label = ctk.CTkLabel(self.custom_binds_frame, text=command, anchor="w", wraplength=450, justify="left", text_color=AppColors.TEXT_COLOR)
                cmd_label.grid(row=i, column=1, padx=(0, 5), pady=3, sticky="ew")
        self.log("Отображение биндов завершено.")
        self.update_advanced_settings_switches()

    def start_apply_binds_thread(self):
        self.set_ui_state("disabled"); threading.Thread(target=self.apply_binds_logic, daemon=True).start()
    def apply_binds_logic(self):
        steam_was_running = False
        try:
            keys_cfg_path = self.get_keys_cfg_path()
            if not keys_cfg_path: self.log("Ошибка: Путь к Rust не найден."); self.after(0, lambda: messagebox.showerror("Ошибка", "Путь к Rust не найден.")); return
            steam_was_running = self.is_process_running(STEAM_PROCESS_NAME)
            if steam_was_running:
                if not messagebox.askyesno("Предупреждение", "Для безопасного применения биндов Steam будет полностью закрыт. Продолжить?"): self.log("Пользователь отменил операцию."); return
                if not self.close_steam(): self.log("Не удалось закрыть Steam. Операция отменена."); return
            desired_binds = {}
            for internal_key_id, data in self.bind_entries.items():
                user_input = data["entry"].get().strip().lower()
                eng_key = RUS_TO_ENG_KEY_MAP.get(user_input, user_input)
                desired_binds[data["command"]] = eng_key
            existing_lines = []
            if keys_cfg_path.exists():
                with open(keys_cfg_path, 'r', encoding='utf-8') as f: existing_lines = f.readlines()
            new_lines = []
            managed_commands_normalized = {self._normalize_command(cmd) for cmd in desired_binds.keys()}
            for line in existing_lines:
                parsed_data = self._parse_bind_line(line)
                if parsed_data:
                    _, command_from_cfg_raw = parsed_data
                    normalized_command = self._normalize_command(command_from_cfg_raw)
                    if normalized_command in managed_commands_normalized: continue
                new_lines.append(line.strip())
            new_binds_count = 0
            for command_raw, key_to_bind in desired_binds.items():
                if key_to_bind: new_lines.append(f'bind {key_to_bind} "{command_raw}"'); new_binds_count += 1
            keys_cfg_path.parent.mkdir(parents=True, exist_ok=True)
            with open(keys_cfg_path, 'w', encoding='utf-8') as f: f.write("\n".join(new_lines))
            self.log(f"Изменения успешно записаны в {keys_cfg_path}. Обновлено/добавлено: {new_binds_count} биндов.")
            self.after(0, lambda: messagebox.showinfo("Успех", "Изменения биндов успешно применены!"))
        except Exception as e: self.log(f"Ошибка во время применения биндов: {e}"); self.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка при записи биндов: {e}"))
        finally:
            if steam_was_running: self.log("Возвращаем Steam в исходное состояние..."); self.launch_steam()
            self.after(0, self.populate_binds_from_file); self.after(0, lambda: self.set_ui_state("normal")); self.log("Операция с биндами завершена.")
    
    def load_icons(self):
        icon_folder = Path(resource_path("icons"))
        icon_files = {"youtube": "youtube.png", "discord": "discord.png", "tg": "tg.png", "da": "da.png"}
        if not icon_folder.is_dir(): self.log("Внимание: Встроенная папка 'icons' не найдена."); return
        for key, filename in icon_files.items():
            try:
                path = icon_folder / filename
                if path.exists(): self.icons[key] = ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=(24, 24))
            except Exception as e: self.log(f"Ошибка при загрузке иконки '{filename}': {e}")

    def open_link(self, url): self.log(f"Открытие ссылки: {url}"); webbrowser.open_new_tab(url)
    def set_ui_state(self, state):
        combobox_state = "readonly" if state == "normal" else "disabled"
        self.profile_combobox.configure(state=combobox_state)
        self.apply_button.configure(state=state)
        self.apply_binds_button.configure(state=state)
        for widget in self.tab_view.tab("Доп настройка").winfo_children()[0].winfo_children():
            if isinstance(widget, (ctk.CTkSwitch, ctk.CTkButton)):
                widget.configure(state=state)
        for data in self.bind_entries.values(): data["entry"].configure(state=state)
    def find_steam_path(self):
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            steam_path = winreg.QueryValueEx(hkey, "SteamPath")[0]
            winreg.CloseKey(hkey); return Path(steam_path)
        except Exception: return None
    def find_rust_path(self):
        if not self.steam_path: return None
        library_vdf_path = self.steam_path / "steamapps" / "libraryfolders.vdf"
        if not library_vdf_path.exists(): return None
        library_paths = [self.steam_path]
        try:
            with open(library_vdf_path, "r", encoding="utf-8") as f: data = vdf.load(f)
            folders = data.get('libraryfolders', data.get('LibraryFolders'))
            if folders:
                for key, value in folders.items():
                    if isinstance(value, dict) and 'path' in value: library_paths.append(Path(value['path']))
        except Exception as e: self.log(f"Ошибка при чтении libraryfolders.vdf: {e}")
        rust_appid = "252490"
        for lib_path in library_paths:
            manifest_path = lib_path / "steamapps" / f"appmanifest_{rust_appid}.acf"
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f: manifest_data = vdf.load(f)
                    install_dir = manifest_data.get('AppState', {}).get('installdir')
                    if install_dir:
                        rust_path = lib_path / "steamapps" / "common" / install_dir
                        if rust_path.exists(): return rust_path
                except Exception as e: self.log(f"Ошибка при чтении манифеста Rust: {e}")
        return None
    def initialize_paths(self):
        self.log("Инициализация путей...")
        self.steam_path = self.find_steam_path()
        if self.steam_path:
            self.steam_exe_path = self.steam_path / STEAM_PROCESS_NAME
            self.rust_path = self.find_rust_path()
        if not self.rust_path:
            self.log("КРИТИЧЕСКАЯ ОШИБКА: Не удалось автоматически найти папку с игрой Rust.")
            messagebox.showerror("Ошибка", "Не удалось найти папку с игрой Rust. Убедитесь, что Steam и Rust установлены корректно.")
            self.apply_button.configure(state="disabled")
            self.apply_binds_button.configure(state="disabled")
        else:
            self.log("Все пути успешно определены. Готово к работе.")
            self.populate_binds_from_file()
    def is_process_running(self, process_name):
        return any(proc.info['name'].lower() == process_name.lower() for proc in psutil.process_iter(['name']))
    def close_steam(self):
        self.log("Попытка корректного закрытия Steam...")
        try:
            subprocess.run([str(self.steam_exe_path), "-shutdown"], timeout=15, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            for _ in range(15):
                if not self.is_process_running(STEAM_PROCESS_NAME): self.log("Steam успешно закрыт."); return True
                threading.Event().wait(1)
            self.log("Steam не закрылся штатно, принудительное завершение...")
            subprocess.run(["taskkill", "/F", "/IM", STEAM_PROCESS_NAME], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            threading.Event().wait(2)
            if not self.is_process_running(STEAM_PROCESS_NAME): self.log("Steam принудительно завершен."); return True
            else: self.log("Критическая ошибка: не удалось закрыть Steam."); return False
        except Exception as e: self.log(f"Ошибка при закрытии Steam: {e}"); return not self.is_process_running(STEAM_PROCESS_NAME)
    def launch_steam(self):
        if not self.steam_exe_path or not self.steam_exe_path.exists(): self.log("Ошибка: Не найден steam.exe."); return
        self.log("Запуск Steam...")
        try: subprocess.Popen([str(self.steam_exe_path)], creationflags=subprocess.CREATE_NO_WINDOW); self.log("Команда на запуск Steam отправлена.")
        except Exception as e: self.log(f"Ошибка при запуске Steam: {e}")
    def start_apply_thread(self):
        self.set_ui_state("disabled"); threading.Thread(target=self.apply_settings_logic, daemon=True).start()
    def apply_settings_logic(self):
        steam_was_running = False
        try:
            if not self.rust_path: self.log("Ошибка: Путь к Rust не найден."); return
            rust_cfg_path = self.rust_path / "cfg"; rust_cfg_path.mkdir(exist_ok=True)
            steam_was_running = self.is_process_running(STEAM_PROCESS_NAME)
            if steam_was_running:
                if not messagebox.askyesno("Предупреждение", "Для безопасного применения настроек Steam будет полностью закрыт. Продолжить?"): self.log("Пользователь отменил операцию."); return
                if not self.close_steam(): self.log("Не удалось закрыть Steam. Операция отменена."); return
            if getattr(sys, 'frozen', False): exe_dir = Path(sys.executable).parent
            else: exe_dir = Path(sys.argv[0]).parent
            backup_dir = exe_dir / "backup"
            try:
                backup_subdir = backup_dir / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                if rust_cfg_path.exists():
                    shutil.copytree(rust_cfg_path, backup_subdir, dirs_exist_ok=True)
                    self.log(f"Бэкап успешно создан в: {backup_subdir}")
            except Exception as e: self.log(f"Ошибка при создании бэкапа: {e}")
            selected_profile_name = self.profile_combobox.get()
            config_filename = PROFILES[selected_profile_name]
            source_config_path = Path(resource_path("configs")) / config_filename
            if not source_config_path.exists(): self.log(f"КРИТИЧЕСКАЯ ОШИБКА: Файл настроек {source_config_path} не найден!"); return
            with open(source_config_path, 'r', encoding='utf-8') as f: lines = f.readlines()
            graphics_cmds, client_cmds = [], []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("//"):
                    if line.lower().startswith("graphics."): graphics_cmds.append(line)
                    else: client_cmds.append(line)
            adv_cmds = self.get_advanced_settings_commands()
            client_cmds.extend(adv_cmds)
            with open(rust_cfg_path / "client.cfg", 'w', encoding='utf-8') as f: f.write("\n".join(client_cmds))
            with open(rust_cfg_path / "graphics.cfg", 'w', encoding='utf-8') as f: f.write("\n".join(graphics_cmds))
            self.log("Применение настроек завершено успешно.")
            self.after(0, lambda: messagebox.showinfo("Успех", "Настройки успешно применены!"))
        except Exception as e: self.log(f"Ошибка во время записи файлов конфигурации: {e}")
        finally:
            if steam_was_running: self.launch_steam()
            self.after(0, lambda: self.set_ui_state("normal")); self.log("Операция завершена.")
    
    def start_apply_advanced_thread(self):
        self.set_ui_state("disabled")
        threading.Thread(target=self.apply_advanced_settings_logic, daemon=True).start()

    def apply_advanced_settings_logic(self):
        steam_was_running = False
        try:
            client_cfg_path = self.get_client_cfg_path()
            if not client_cfg_path:
                self.log("Путь к Rust не определен."); return
            
            client_cfg_path.parent.mkdir(exist_ok=True)

            steam_was_running = self.is_process_running(STEAM_PROCESS_NAME)
            if steam_was_running:
                if not messagebox.askyesno("Предупреждение", "Для безопасного применения настроек Steam будет полностью закрыт. Продолжить?"):
                    self.log("Пользователь отменил операцию.")
                    return
                if not self.close_steam():
                    self.log("Не удалось закрыть Steam. Операция отменена.")
                    return

            lines = []
            if client_cfg_path.exists():
                with open(client_cfg_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

            all_possible_adv_cmds = set()
            for cmd_str in self.adv_settings_mapping.values():
                for cmd in cmd_str.split(';'):
                    all_possible_adv_cmds.add(cmd.strip().split(' ')[0].lower())

            new_lines = [line for line in lines if line.strip().split(' ')[0].lower() not in all_possible_adv_cmds]

            new_adv_cmds = self.get_advanced_settings_commands()
            new_lines.extend([f"{cmd}\n" for cmd in new_adv_cmds])

            with open(client_cfg_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            self.log("Дополнительные настройки успешно применены.")
            self.after(0, lambda: messagebox.showinfo("Успех", "Дополнительные настройки успешно применены!"))

        except Exception as e:
            self.log(f"Ошибка во время применения доп. настроек: {e}")
            self.after(0, lambda: messagebox.showerror("Ошибка", f"Произошла ошибка: {e}"))
        finally:
            if steam_was_running:
                self.launch_steam()
            self.after(0, lambda: self.set_ui_state("normal"))
            self.log("Операция с доп. настройками завершена.")

    def get_advanced_settings_commands(self):
        commands = []
        for key, cmd_on in self.adv_settings_mapping.items():
            if self.adv_settings_vars[key].get():
                commands.extend(cmd.strip() for cmd in cmd_on.split(';'))
        return commands
    
    def show_new_instructions(self):
        instructions = """Привет! Данное приложение создано благодаря проекту Rust ForNew.
В RustConfigurator ты можешь удобно настроить графику, 
настроить бинды, 
посчитать кол-во взрывчатки для рейда,
посчитать стоимость содержания и постройки дома,
посмотреть свою статистику из комбатлога
и многое другое!"""
        messagebox.showinfo("Инструкция", instructions)

    def start_update_check_thread(self):
        thread = threading.Thread(target=self.check_for_updates, daemon=True); thread.start()
    
    def check_for_updates(self):
        self.log("Проверка наличия обновлений...")
        try:
            response = requests.get(LATEST_VERSION_FILE_URL, timeout=10)
            response.raise_for_status()
            latest_version_str = response.text.strip()
            
            current_v = version.parse(VERSION)
            latest_v = version.parse(latest_version_str)

            if latest_v > current_v:
                self.log(f"Доступна новая версия: {latest_version_str}. Ваша текущая: {VERSION}")
                self.after(0, lambda: self.show_update_dialog(latest_version_str))
            else:
                self.log(f"Установлена последняя версия ({VERSION}).")
        except requests.exceptions.RequestException as e:
            self.log(f"Ошибка сети при проверке обновлений: {e}")
        except Exception as e:
            self.log(f"Не удалось проверить обновления: {e}")

    def show_update_dialog(self, latest_version):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Доступно обновление")
        dialog.geometry("450x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main_frame, text=f"Доступна новая версия: {latest_version}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        
        link_text = "Скачать с GitHub"
        link_label = ctk.CTkLabel(main_frame, text=link_text, text_color="#60a5fa", cursor="hand2", font=ctk.CTkFont(underline=True))
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: self.open_link(GITHUB_RELEASES_PAGE_URL))
        
        ok_button = ctk.CTkButton(main_frame, text="OK", command=dialog.destroy, width=120)
        ok_button.pack(pady=(20, 0))


if __name__ == "__main__":
    app = RustConfiguratorApp()
    app.mainloop()
