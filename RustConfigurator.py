# -*- coding: utf-8 -*-

# RustConfigurator
# ВНИМАНИЕ: Эта программа изменяет конфигурационные файлы игры Rust.
# Используйте на свой страх и риск. Автор и разработчик не несут
# ответственности за возможные последствия, включая, но не ограничиваясь,
# блокировкой игрового аккаунта. Политика Facepunch в отношении
# изменения файлов может меняться.

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
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
from datetime import datetime
from PIL import Image
import requests # ИЗМЕНЕНИЕ: Добавляем для выполнения HTTP-запросов
from packaging import version # ИЗМЕНЕНИЕ: Добавляем для надежного сравнения версий

def resource_path(relative_path):
    """ 
    Получаем абсолютный путь к ресурсу для совместимости с PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- КОНФИГУРАЦИЯ ---
APP_NAME = "RustConfigurator"
VERSION = "1.0.0" # ИЗМЕНЕНИЕ: Укажите текущую версию вашего приложения. Обновляйте ее при каждом новом релизе.
WINDOW_SIZE = "800x750"

PROFILES = {
    "🔫 Combat": "Комбат.cfg",
    "🎨 Красивая картинка": "Топ графика.cfg",
    "⚖️ Средние настройки": "Баланс.cfg",
    "🖥️ Слабый ПК": "Макс производительность.cfg"
}
STEAM_PROCESS_NAME = "steam.exe"

# ИЗМЕНЕНИЕ: Настройки для проверки обновлений на GitHub
GITHUB_REPO_OWNER = "RustForNew" # Замените на ваш никнейм на GitHub
GITHUB_REPO_NAME = "RustConfigurator" # Замените на имя вашего репозитория
LATEST_VERSION_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/main/latest_version.txt"
GITHUB_RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases"


RUS_TO_ENG_KEY_MAP = {
    'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p',
    'х': '[', 'ъ': ']', 'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k',
    'д': 'l', 'ж': ';', 'э': "'", 'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n', 'ь': 'm',
    'б': ',', 'ю': '.', '.': '/', 'ё': '`'
}

DEFAULT_RUST_COMMANDS = {
    'consoletoggle', '+forward', '+backward', '+left', '+right', '+attack', '+attack2', '+attack3', '+ping',
    '+slot1', '+slot2', '+slot3', '+slot4', '+slot5', '+slot6', '+holsteritem', '+sprint', '+altlook',
    '+reload', '+jump', '+duck', '+use', '+voice', '+map', 'chat.open', '+invnext', '+invprev',
    'inventory.toggle', 'inventory.togglecrafting', 'lighttoggle', 'inventory.examineheld', '+compass',
    '+hoverloot', '+gestures', '+pets', '+firemode', 'clan.toggleclan', '+prevskin', '+nextskin',
    '+focusmap', '+notec', '+noted', '+notee', '+notef', '+noteg', '+notea', '+noteb',
    '+notesharpmod', '+noteoctaveupmod', '+zoomincrease', '+zoomdecrease', '+opentutorialhelp',
    'swapseats', 'swaptoseat 0', 'swaptoseat 1', 'swaptoseat 2', 'swaptoseat 3', 'swaptoseat 4',
    'swaptoseat 5', 'swaptoseat 6', 'swaptoseat 7', '+wireslackup', '+wireslackdown', 'kill'
}

class RustConfiguratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.resizable(True, True) 
        self.minsize(800, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.steam_path = None
        self.rust_path = None
        self.steam_exe_path = None
        self.icons = {}
        self.bind_entries = {}

        self.tab_view = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.tab_view.add("Основные настройки")
        self.tab_view.add("Бинды")
        self.tab_view.add("Доп настройка")
        self.tab_view.add("О создателе")
        self.tab_view.set("Основные настройки")

        self.create_main_tab()
        self.create_binds_tab()
        self.create_advanced_tab()
        self.create_about_tab()
        
        self.log_textbox = ctk.CTkTextbox(self, state="disabled", wrap="word", font=("Consolas", 11))
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.log("Приложение запущено.")
        self.initialize_paths()
        self.after(100, self.show_new_instructions)
        self.after(200, self.start_update_check_thread) # ИЗМЕНЕНИЕ: Запускаем проверку обновлений через короткое время после старта

    def create_main_tab(self):
        main_tab = self.tab_view.tab("Основные настройки")
        main_tab.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(main_tab, text="Выберите профиль настроек:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.profile_combobox = ctk.CTkComboBox(main_tab, values=list(PROFILES.keys()), state="readonly")
        self.profile_combobox.set(list(PROFILES.keys())[0])
        self.profile_combobox.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.apply_button = ctk.CTkButton(main_tab, text="Применить настройки", command=self.start_apply_thread)
        self.apply_button.grid(row=2, column=0, padx=10, pady=20, sticky="ew")

    def create_advanced_tab(self):
        adv_tab = self.tab_view.tab("Доп настройка")
        adv_tab.grid_columnconfigure(0, weight=1)
        self.adv_settings_vars = {
            "no_legs": ctk.BooleanVar(value=False), "less_shake": ctk.BooleanVar(value=False),
            "orange_cross": ctk.BooleanVar(value=False), "no_gibs": ctk.BooleanVar(value=False),
            "no_blink": ctk.BooleanVar(value=False), "no_leg_splay": ctk.BooleanVar(value=False),
            "fast_alt_look": ctk.BooleanVar(value=False), "no_strobe": ctk.BooleanVar(value=False),
            "no_safezone": ctk.BooleanVar(value=False),
        }
        settings_labels = [
            ("Отключить отображение ног", "no_legs"), ("Уменьшить тряску камеры", "less_shake"),
            ("Улучшить видимость крестиков на деревьях (оранжевые)", "orange_cross"),
            ("Полностью отключить обломки (gibs)", "no_gibs"), ("Отключить моргание глаз у персонажей", "no_blink"),
            ("Отключить деформацию ног", "no_leg_splay"), ("Ускорить поворот головы через ALT", "fast_alt_look"),
            ("Полностью отключить стробоскопы", "no_strobe"), ("Отключить безопасный механизм отсечения окклюзии", "no_safezone"),
        ]
        for i, (text, key) in enumerate(settings_labels):
            ctk.CTkSwitch(adv_tab, text=text, variable=self.adv_settings_vars[key]).grid(row=i, column=0, padx=20, pady=8, sticky="w")

    def create_about_tab(self):
        about_tab = self.tab_view.tab("О создателе")
        about_tab.grid_columnconfigure(0, weight=1)
        self.load_icons()
        
        socials = [
            ("youtube", "https://youtube.com/@rustfornew?si=tbFZPm6pgmlawAaU", "YouTube: Rust ForNew"),
            ("discord", "https://discord.gg/MjP85xw4RM", "Discord: Rust ForNew"),
            ("tg", "https://t.me/RustForNew", "ТГК: Rust ForNew"),
            ("tg", "https://t.me/RFNRustLook_bot", "tg bot: RustLook")
        ]
        
        current_row = 0
        for key, url, text in socials:
            if key in self.icons:
                ctk.CTkButton(about_tab, text=text, image=self.icons[key], compound="left", anchor="w", command=lambda u=url: self.open_link(u)).grid(row=current_row, column=0, padx=20, pady=10, sticky="ew")
                current_row += 1
        
        ctk.CTkLabel(about_tab, text="Наш сервер Rust:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=current_row, column=0, padx=20, pady=(20, 5), sticky="w")
        current_row += 1
        server_connect = ctk.CTkEntry(about_tab)
        server_connect.insert(0, "connect 78.107.7.197:28016")
        server_connect.configure(state="readonly")
        server_connect.grid(row=current_row, column=0, padx=20, pady=5, sticky="ew")

    def create_binds_tab(self):
        self.binds_tab = self.tab_view.tab("Бинды")
        self.binds_tab.grid_columnconfigure(0, weight=1)
        self.binds_tab.grid_rowconfigure(1, weight=1)

        self.managed_binds_definitions = [
            ("auto_run", 'Автобег (отключается кнопкой движения вперед)', 'forward;sprint'),
            ("quick_loot", 'Быстрый сбор (удерживать)', '+use'),
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
            ("suicide", 'Суицид', 'kill') # ИЗМЕНЕНИЕ: Добавлен бинд "Суицид"
        ]

        managed_frame = ctk.CTkFrame(self.binds_tab)
        managed_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        managed_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(managed_frame, text="Управляемые бинды (оставьте поле пустым для удаления):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 15), sticky="w")

        for i, (key, description, command) in enumerate(self.managed_binds_definitions):
            ctk.CTkLabel(managed_frame, text=description, anchor="w").grid(row=i + 1, column=0, padx=(10, 5), pady=5, sticky="w")
            entry = ctk.CTkEntry(managed_frame, placeholder_text="Клавиша")
            entry.grid(row=i + 1, column=1, padx=(5, 10), pady=5, sticky="ew")
            self.bind_entries[key] = {"entry": entry, "command": command}
        
        self.apply_binds_button = ctk.CTkButton(managed_frame, text="Применить изменения биндов", command=self.start_apply_binds_thread)
        self.apply_binds_button.grid(row=len(self.managed_binds_definitions) + 1, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        custom_frame = ctk.CTkFrame(self.binds_tab)
        custom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        custom_frame.grid_columnconfigure(0, weight=1)
        custom_frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header_frame, text="Ваши остальные бинды (кроме стандартных):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header_frame, text="🔄", width=30, command=self.populate_binds_from_file).grid(row=0, column=1, sticky="e")

        self.custom_binds_frame = ctk.CTkScrollableFrame(custom_frame, label_text="")
        self.custom_binds_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.custom_binds_frame.grid_columnconfigure(1, weight=1)

    def on_tab_change(self):
        if self.tab_view.get() == "Бинды":
            self.populate_binds_from_file()

    def get_keys_cfg_path(self):
        if not self.rust_path:
            return None
        return self.rust_path / "cfg" / "keys.cfg"

    def _parse_bind_line(self, line):
        line = line.strip()
        if not line.lower().startswith('bind '):
            return None

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

        if remaining_str.startswith('"') and remaining_str.endswith('"'):
            command_part = remaining_str[1:-1]
        else:
            command_part = remaining_str

        if key_part and command_part:
            return key_part, command_part
        
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
            self.log(f"Файл keys.cfg не найден по пути: {keys_cfg_path}")
            return managed_binds, user_binds

        command_to_internal_key_map = {
            self._normalize_command(data['command']): key 
            for key, data in self.bind_entries.items()
        }
        normalized_default_commands = {self._normalize_command(cmd) for cmd in DEFAULT_RUST_COMMANDS}

        try:
            content = None
            for encoding in ['utf-8', 'cp1251', 'latin-1']:
                try:
                    with open(keys_cfg_path, 'r', encoding=encoding) as f:
                        content = f.readlines()
                    break
                except (UnicodeDecodeError, TypeError):
                    continue
            
            if content is None:
                self.log("Не удалось прочитать keys.cfg ни в одной из стандартных кодировок.")
                return managed_binds, user_binds

            for line in content:
                parsed_data = self._parse_bind_line(line)
                if parsed_data:
                    key_from_cfg, command_from_cfg_raw = parsed_data
                    
                    is_default = False
                    sub_commands = self._normalize_command(command_from_cfg_raw).split(';')
                    for sub_cmd in sub_commands:
                        if sub_cmd in normalized_default_commands:
                            is_default = True
                            break
                    
                    is_managed = self._normalize_command(command_from_cfg_raw) in command_to_internal_key_map

                    if is_managed:
                        internal_key_id = command_to_internal_key_map[self._normalize_command(command_from_cfg_raw)]
                        managed_binds[internal_key_id] = key_from_cfg
                    elif not is_default:
                        user_binds.append((key_from_cfg, command_from_cfg_raw))

        except Exception as e:
            self.log(f"Критическая ошибка при разборе keys.cfg: {e}")

        return managed_binds, user_binds

    def populate_binds_from_file(self):
        if not self.rust_path:
            self.log("Путь к Rust не найден, не могу прочитать бинды.")
            return

        self.log("Чтение и отображение текущих биндов из keys.cfg в UI...")
        managed_binds, user_binds = self.parse_keys_cfg()

        for internal_key_id, data in self.bind_entries.items():
            entry = data["entry"]
            entry.delete(0, "end")
            if internal_key_id in managed_binds:
                entry.insert(0, managed_binds[internal_key_id])

        for widget in self.custom_binds_frame.winfo_children():
            widget.destroy()

        if not user_binds:
            ctk.CTkLabel(self.custom_binds_frame, text="Другие пользовательские бинды не найдены.").pack(pady=10)
        else:
            self.custom_binds_frame.grid_columnconfigure(0, weight=0, minsize=120)
            self.custom_binds_frame.grid_columnconfigure(1, weight=1)
            
            for i, (key, command) in enumerate(sorted(user_binds)):
                key_label = ctk.CTkLabel(self.custom_binds_frame, text=key, font=ctk.CTkFont(weight="bold"), anchor="w")
                key_label.grid(row=i, column=0, padx=(5, 10), pady=3, sticky="w")
                
                cmd_label = ctk.CTkLabel(self.custom_binds_frame, text=command, anchor="w", wraplength=450, justify="left")
                cmd_label.grid(row=i, column=1, padx=(0, 5), pady=3, sticky="ew")
        self.log("Отображение биндов завершено.")

    def start_apply_binds_thread(self):
        self.set_ui_state("disabled")
        threading.Thread(target=self.apply_binds_logic, daemon=True).start()

    def apply_binds_logic(self):
        steam_was_running = False
        try:
            keys_cfg_path = self.get_keys_cfg_path()
            if not keys_cfg_path:
                self.log("Ошибка: Путь к Rust не найден."); messagebox.showerror("Ошибка", "Путь к Rust не найден."); return

            steam_was_running = self.is_process_running(STEAM_PROCESS_NAME)
            if steam_was_running:
                if not messagebox.askyesno("Предупреждение", "Для безопасного применения биндов Steam будет полностью закрыт. Продолжить?"):
                    self.log("Пользователь отменил операцию."); return
                if not self.close_steam():
                    self.log("Не удалось закрыть Steam. Операция отменена."); return
            
            desired_binds = {}
            for internal_key_id, data in self.bind_entries.items():
                user_input = data["entry"].get().strip().lower()
                eng_key = RUS_TO_ENG_KEY_MAP.get(user_input, user_input)
                desired_binds[data["command"]] = eng_key
            
            existing_lines = []
            if keys_cfg_path.exists():
                with open(keys_cfg_path, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()

            new_lines = []
            managed_commands_normalized = {self._normalize_command(cmd) for cmd in desired_binds.keys()}

            for line in existing_lines:
                parsed_data = self._parse_bind_line(line)
                if parsed_data:
                    _, command_from_cfg_raw = parsed_data
                    normalized_command = self._normalize_command(command_from_cfg_raw)
                    if normalized_command in managed_commands_normalized:
                        continue
                new_lines.append(line.strip())

            new_binds_count = 0
            for command_raw, key_to_bind in desired_binds.items():
                if key_to_bind:
                    new_lines.append(f'bind {key_to_bind} "{command_raw}"')
                    new_binds_count += 1
            
            keys_cfg_path.parent.mkdir(parents=True, exist_ok=True)
            with open(keys_cfg_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(new_lines))
            
            self.log(f"Изменения успешно записаны в {keys_cfg_path}. Обновлено/добавлено: {new_binds_count} биндов.")
            messagebox.showinfo("Успех", "Изменения биндов успешно применены!")

        except Exception as e:
            self.log(f"Ошибка во время применения биндов: {e}")
            messagebox.showerror("Ошибка", f"Произошла ошибка при записи биндов: {e}")
        finally:
            if steam_was_running:
                self.log("Возвращаем Steam в исходное состояние..."); self.launch_steam()
            self.after(0, self.populate_binds_from_file)
            self.after(0, lambda: self.set_ui_state("normal"))
            self.log("Операция с биндами завершена.")

    def load_icons(self):
        icon_folder = Path(resource_path("icons"))
        icon_files = {"youtube": "youtube.png", "discord": "discord.png", "tg": "tg.png"}
        if not icon_folder.is_dir():
            self.log("Внимание: Встроенная папка 'icons' не найдена."); return
        for key, filename in icon_files.items():
            try:
                path = icon_folder / filename
                if path.exists():
                    self.icons[key] = ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=(24, 24))
            except Exception as e:
                self.log(f"Ошибка при загрузке иконки '{filename}': {e}")

    def open_link(self, url):
        self.log(f"Открытие ссылки: {url}"); webbrowser.open_new_tab(url)

    def log(self, message):
        def _log():
            now = datetime.now().strftime("%H:%M:%S")
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", f"[{now}] {message}\n")
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")
        self.after(0, _log)

    def set_ui_state(self, state):
        combobox_state = "readonly" if state == "normal" else "disabled"
        self.profile_combobox.configure(state=combobox_state)
        self.apply_button.configure(state=state)
        self.apply_binds_button.configure(state=state)
        for switch in self.tab_view.tab("Доп настройка").winfo_children():
            if isinstance(switch, ctk.CTkSwitch):
                switch.configure(state=state)
        for data in self.bind_entries.values():
            data["entry"].configure(state=state)

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
                    if isinstance(value, dict) and 'path' in value:
                        library_paths.append(Path(value['path']))
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
        except Exception as e:
            self.log(f"Ошибка при закрытии Steam: {e}"); return not self.is_process_running(STEAM_PROCESS_NAME)

    def launch_steam(self):
        if not self.steam_exe_path or not self.steam_exe_path.exists(): self.log("Ошибка: Не найден steam.exe."); return
        self.log("Запуск Steam...")
        try:
            subprocess.Popen([str(self.steam_exe_path)], creationflags=subprocess.CREATE_NO_WINDOW)
            self.log("Команда на запуск Steam отправлена.")
        except Exception as e: self.log(f"Ошибка при запуске Steam: {e}")

    def start_apply_thread(self):
        self.set_ui_state("disabled")
        threading.Thread(target=self.apply_settings_logic, daemon=True).start()

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
                backup_dir.mkdir(exist_ok=True)
                backup_subdir = backup_dir / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
            messagebox.showinfo("Успех", "Настройки успешно применены!")
        except Exception as e:
            self.log(f"Ошибка во время записи файлов конфигурации: {e}")
        finally:
            if steam_was_running: self.launch_steam()
            self.after(0, lambda: self.set_ui_state("normal"))
            self.log("Операция завершена.")

    def get_advanced_settings_commands(self):
        commands = []
        mapping = {
            "no_legs": "graphics.show_local_player false", "less_shake": "graphics.vm_recoil_scale 0; graphics.vm_bob_scale 0",
            "orange_cross": 'tree.color_decal_on_hit "1 0.5 0 1"', "no_gibs": "effects.gibs false",
            "no_blink": "player.eye_blinking false", "no_leg_splay": "player.leg_splay false",
            "fast_alt_look": "input.autofreeloookduration 0.01", "no_strobe": "effects.strobe 0",
            "no_safezone": "culling.safezone 0",
        }
        for key, cmd_on in mapping.items():
            if self.adv_settings_vars[key].get():
                commands.extend(cmd_on.split('; '))
        return commands

    def show_new_instructions(self):
        instructions = """
Добро пожаловать в RustConfigurator, данная программа выпущена командой Rust ForNew.

Как использовать программу: просто выбираете нужный вам конфиг и программа автоматически поставит нужные настройки, в которых отключены все мусорные функции графики и включены полезные.

Наслаждайтесь использованием ;)

Ну а поиграть в раст и получить за это деньги и скины можно на Rust ForNew
        """
        messagebox.showinfo("Инструкция", instructions)

    # ИЗМЕНЕНИЕ: Новые методы для проверки обновлений
    def start_update_check_thread(self):
        """Запускает проверку обновлений в отдельном потоке, чтобы не блокировать интерфейс."""
        thread = threading.Thread(target=self.check_for_updates, daemon=True)
        thread.start()

    def check_for_updates(self):
        """Проверяет наличие новой версии приложения на GitHub."""
        self.log("Проверка наличия обновлений...")
        try:
            # Получаем последнюю версию из файла на GitHub
            response = requests.get(LATEST_VERSION_FILE_URL, timeout=5)
            response.raise_for_status() # Вызывает исключение для ошибок HTTP (4xx или 5xx)
            latest_version_str = response.text.strip()

            # Парсим и сравниваем версии
            current_version = version.parse(VERSION)
            latest_version = version.parse(latest_version_str)

            if latest_version > current_version:
                self.log(f"Доступна новая версия: {latest_version_str}. Ваша текущая: {VERSION}")
                if messagebox.askyesno(
                    "Доступно обновление",
                    f"Доступна новая версия RustConfigurator: {latest_version_str} (Ваша текущая: {VERSION}).\n"
                    "Хотите перейти на страницу загрузки?"
                ):
                    webbrowser.open_new_tab(GITHUB_RELEASES_PAGE_URL)
            else:
                self.log(f"У вас установлена последняя версия ({VERSION}).")

        except requests.exceptions.RequestException as e:
            self.log(f"Ошибка при проверке обновлений (нет сети или GitHub недоступен): {e}")
        except version.InvalidVersion as e:
            self.log(f"Ошибка при парсинге версии: {e}. Убедитесь, что файл latest_version.txt содержит корректный номер версии (например, 1.0.0).")
        except Exception as e:
            self.log(f"Непредвиденная ошибка при проверке обновлений: {e}")

if __name__ == "__main__":
    app = RustConfiguratorApp()
    app.mainloop()
