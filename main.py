
import warnings
warnings.filterwarnings("ignore")  
import discord
import json
import os
import asyncio
import aiofiles
import aiohttp
import asyncio
import random
from datetime import datetime
from discord.ext import commands, tasks
import gc
import threading
import time
import shutil
import requests
from typing import Optional
import urllib
import re
from discord.ui import Button, View, Modal, TextInput
from discord import app_commands
from urllib.parse import urlparse
import random
import string
import uuid
import hashlib
import time
import signal
import os, json
import threading
import asyncio, aiohttp
import pkgutil, hashlib
import inspect, importlib, functools
import base64
import datetime
from bs4 import BeautifulSoup
from main.fb import *
from main import *
import websockets
import asyncio
import math
import itertools


user_keys = {}
user_nhapkey_count = {}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

active_senders = {}

def clr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def extract_keys(html):
    soup = BeautifulSoup(html, 'html.parser')
    code_div = soup.find('div', class_='plaintext')
    if code_div:
        keys = [line.strip() for line in code_div.get_text().split('\n') if line.strip()]
        return keys
    return []

def decode_ascii_payload(payload_array):
    try:
        decoded_string = ''.join(chr(code) for code in payload_array)
        if not decoded_string.endswith('}'):
            open_braces = decoded_string.count('{')
            close_braces = decoded_string.count('}')
            if open_braces > close_braces:
                decoded_string += '}' * (open_braces - close_braces)
        return json.loads(decoded_string)
    except Exception as e:
        return f"Lỗi decode ASCII payload: {e}"

def checkkey():
    url = 'https://anotepad.com/notes/aey9nt33'
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print("Không thể lấy dữ liệu từ anotepad:", e)
        os.kill(os.getpid(), 9)
    md5_list = extract_keys(response.text)
    key = input("Nhập Key Để Tiếp Tục:\n").strip()
    hashed = hashlib.md5(key.encode()).hexdigest()
    if hashed in md5_list:
        print("Key Đúng")
    else:
        print("Key Saii. Thoát chương trình.")
        os.kill(os.getpid(), 9)

def check_task_limit():
    if not os.path.exists('data'):
        return 0
    
    task_count = 0
    for folder in os.listdir('data'):
        folder_path = f"data/{folder}"
        if os.path.isdir(folder_path) and os.path.exists(f"{folder_path}/luutru.txt"):
            task_count += 1
    
    return task_count

def load_config():
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                data = f.read().strip()
                if not data:  # file rỗng
                    return None
                return json.loads(data)
        except json.JSONDecodeError:
            print("⚠️ File config.json lỗi hoặc sai format, tạo lại...")
            return None
    return None

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def create_initial_config():
    token = input("Nhập Token Bot Discord Của Bạn > ")
    owner_vip_id = input("Nhập Owner VIP ID > ")
    prefix = input("Nhập Prefix Cho Bot > ")
    config = {
        "tokenbot": token,
        "prefix": prefix,
        "ownerVIP": owner_vip_id,
        "task": {}
    }
    save_config(config)
    return config

##config = load_config()
##if config:
##    choice = input("Bạn Có Muốn Sử Dụng Lại Token, Owner VIP và Prefix Cũ Không (Y/N) > ").lower()
##    if choice != 'y':
##        config = create_initial_config()
##else:
##    config = create_initial_config()
config = load_config()
if config:
    choice = "y"  
    if choice != 'y':
        config = create_initial_config()
else:
    config = create_initial_config()

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

DB_FILE = "user_files.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
def read_lines_from_file(file_path: str = None, fallback: str = "nhay.txt"):
    lines = []
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")

    if not lines: 
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fb_path = os.path.join(current_dir, fallback)
        if not os.path.exists(fb_path):
            with open(fb_path, "w", encoding="utf-8") as f:
                f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\n")
        with open(fb_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    return [line.strip() for line in lines if line.strip()]

def ensure_user(uid: str):
    db = load_db()
    if uid not in db:
        db[uid] = []
        save_db(db)
    return db

def get_user_files(user_id: int):
    uid = str(user_id)
    db = ensure_user(uid)
    return db[uid]

def add_user_file(user_id: int, file_path: str):
    uid = str(user_id)
    db = ensure_user(uid)
    files = db[uid]
    if len(files) >= 5:
        return False, "❌ Bạn chỉ được lưu tối đa 5 file."
    files.append(file_path)
    db[uid] = files
    save_db(db)
    return True, f"✅ Đã lưu file: `{os.path.basename(file_path)}`"

def remove_user_file(user_id: int, file_path: str):
    uid = str(user_id)
    db = ensure_user(uid)
    db[uid] = [f for f in db[uid] if f != file_path]
    save_db(db)

def update_user_file(user_id: int, old_path: str, new_path: str):
    uid = str(user_id)
    db = ensure_user(uid)
    files = db[uid]
    for i, p in enumerate(files):
        if p == old_path:
            files[i] = new_path
            break
    db[uid] = files
    save_db(db)

intents = discord.Intents.default()
intents.message_content = True



class EditFileModal(discord.ui.Modal, title="✏️ Chỉnh sửa File"):
    def __init__(self, user_id, filepath):
        super().__init__()
        self.user_id = str(user_id)
        self.filepath = filepath

        self.content = discord.ui.TextInput(
            label="Nội dung mới",
            style=discord.TextStyle.paragraph,
            placeholder="Nhập nội dung mới (≤ 5000 ký tự)",
            max_length=5000,
            required=True
        )
        self.add_item(self.content)

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Không phải file của bạn.", ephemeral=True)
            return
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self.content.value)
        await interaction.response.send_message("✅ Đã cập nhật file thành công!", ephemeral=True)


class RenameFileModal(discord.ui.Modal, title="📝 Đổi tên File"):
    def __init__(self, user_id, filepath):
        super().__init__()
        self.user_id = str(user_id)
        self.filepath = filepath

        self.new_name = discord.ui.TextInput(
            label="Tên mới",
            placeholder="ví dụ: myfile.txt",
            max_length=100,
            required=True
        )
        self.add_item(self.new_name)

    async def on_submit(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Không phải file của bạn.", ephemeral=True)
            return
        new_name = self.new_name.value.strip()
        if not new_name.endswith(".txt"):
            await interaction.response.send_message("❌ Phải có đuôi .txt", ephemeral=True)
            return
        new_path = os.path.join(os.path.dirname(self.filepath), new_name)
        os.rename(self.filepath, new_path)
        update_user_file(int(self.user_id), self.filepath, new_path)
        self.filepath = new_path
        await interaction.response.send_message(f"✅ File đã đổi tên thành `{new_name}`", ephemeral=True)

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, user_id, filepath):
        super().__init__(timeout=20)
        self.user_id = str(user_id)
        self.filepath = filepath

    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Không phải file của bạn.", ephemeral=True)
            return
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        remove_user_file(int(self.user_id), self.filepath)
        await interaction.response.edit_message(content="🗑️ File đã bị xóa!", view=None)

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Hủy xóa file.", view=None)


class FileActionView(discord.ui.View):
    def __init__(self, user_id, filepath):
        super().__init__(timeout=None)
        self.user_id = str(user_id)
        self.filepath = filepath

    @discord.ui.button(label="✏️ Chỉnh sửa", style=discord.ButtonStyle.primary)
    async def edit_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditFileModal(self.user_id, self.filepath))

    @discord.ui.button(label="❌ Xóa", style=discord.ButtonStyle.danger)
    async def delete_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Bạn có chắc muốn xóa file này?", 
                                                view=ConfirmDeleteView(self.user_id, self.filepath), ephemeral=True)

    @discord.ui.button(label="📝 Đổi tên", style=discord.ButtonStyle.secondary)
    async def rename_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RenameFileModal(self.user_id, self.filepath))

    @discord.ui.button(label="📥 Tải về (DM)", style=discord.ButtonStyle.success)
    async def download_file(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.user.send(file=discord.File(self.filepath))
            await interaction.response.send_message("✅ File đã được gửi qua DM!", ephemeral=True)
        except:
            await interaction.response.send_message("⚠️ Không thể gửi DM cho bạn.", ephemeral=True)


class FileDropdown(discord.ui.Select):
    def __init__(self, user_id, files):
        options = [
            discord.SelectOption(label=f"File {i+1}", description=os.path.basename(p)[:50], value=str(i))
            for i, p in enumerate(files)
        ]
        super().__init__(placeholder="📂 Chọn file để xem chi tiết", options=options)
        self.user_id = str(user_id)
        self.files = files

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Không phải file của bạn.", ephemeral=True)
            return

        idx = int(self.values[0])
        filepath = self.files[idx]
        if not os.path.exists(filepath):
            await interaction.response.send_message("⚠️ File không tồn tại.", ephemeral=True)
            return

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        preview = "".join(lines[:10]) if lines else "(File rỗng)"

        embed = discord.Embed(
            title=f"📂 {os.path.basename(filepath)}",
            description=f"**Đường dẫn:** `{filepath}`\n\n**Preview 10 dòng đầu:**\n```{preview}```",
            color=0x2ecc71
        )
        size = math.ceil(os.path.getsize(filepath) / 1024)
        embed.add_field(name="Dung lượng", value=f"{size} KB", inline=True)
        embed.add_field(name="Chủ sở hữu", value=f"<@{self.user_id}>", inline=True)
        embed.set_footer(text=f"Yêu cầu bởi {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed, view=FileActionView(self.user_id, filepath), ephemeral=True)


async def handle_setfile(ctx_or_inter, author, attachments, respond):
    if not attachments:
        await respond("❌ Bạn phải gửi kèm 1 file `.txt`", ephemeral=True)
        return

    file = attachments[0]
    if not file.filename.endswith(".txt"):
        await respond("❌ Chỉ hỗ trợ file `.txt`", ephemeral=True)
        return
    if file.size > 2 * 1024 * 1024:
        await respond("❌ File quá nặng, chỉ hỗ trợ ≤ 2MB", ephemeral=True)
        return

    try:
        uid = str(author.id)
        user_folder = os.path.join("userdata", uid)
        os.makedirs(user_folder, exist_ok=True)

        filename = f"{int(time.time())}_{file.filename}"
        file_path = os.path.join(user_folder, filename)
        await file.save(file_path)

        ok, msg = add_user_file(author.id, file_path)
        size_kb = math.ceil(file.size / 1024)

        embed = discord.Embed(
            title="📄 File TXT mới được upload",
            description=msg,
            color=0x3498db
        )
        embed.add_field(name="Tên file", value=file.filename, inline=True)
        embed.add_field(name="Dung lượng", value=f"{size_kb} KB", inline=True)
        embed.add_field(name="Upload bởi", value=author.mention, inline=True)
        embed.add_field(name="Đường dẫn", value=f"`{file_path}`", inline=False)
        embed.set_thumbnail(url="https://i.pinimg.com/736x/5c/e5/a7/5ce5a7e01057f4fcb5c9c0c66d3ec7a0.jpg")
        embed.set_footer(text=f"Yêu cầu bởi {author}", icon_url=author.display_avatar.url)

        await respond(embed=embed)
    except Exception as e:
        await respond(f"❌ Lỗi khi lưu file: {e}", ephemeral=True)

async def handle_xemfile(author, respond):
    files = get_user_files(author.id)
    if not files:
        await respond("📂 Bạn chưa upload file nào. Hãy dùng `!setfile`.", ephemeral=True)
        return

    view = discord.ui.View()
    view.add_item(FileDropdown(author.id, files))

    embed = discord.Embed(
        title=f"📂 Danh sách file của {author.name}",
        description="Chọn file trong dropdown bên dưới để xem chi tiết.",
        color=0xf1c40f
    )
    for idx, path in enumerate(files, start=1):
        if os.path.exists(path):
            size = math.ceil(os.path.getsize(path) / 1024)
            embed.add_field(name=f"File {idx}", value=f"`{os.path.basename(path)}` • {size} KB", inline=False)
        else:
            embed.add_field(name=f"File {idx}", value="⚠️ Mất file", inline=False)

    embed.set_footer(text=f"Yêu cầu bởi {author}", icon_url=author.display_avatar.url)
    await respond(embed=embed, view=view)

@bot.command(name="setfile")
async def setfile_cmd(ctx: commands.Context):
    await handle_setfile(ctx, ctx.author, ctx.message.attachments, ctx.send)

@bot.command(name="xemfile")
async def xemfile_cmd(ctx: commands.Context):
    await handle_xemfile(ctx.author, ctx.send)

@app_commands.command(name="setfile", description="Upload 1 file .txt (≤ 2MB)")
@app_commands.describe(file="File TXT bạn muốn upload")
async def setfile_slash(interaction: discord.Interaction, file: discord.Attachment):
    await handle_setfile(interaction, interaction.user, [file], interaction.response.send_message)

@app_commands.command(name="xemfile", description="Xem danh sách file đã upload")
async def xemfile_slash(interaction: discord.Interaction):
    await handle_xemfile(interaction.user, interaction.response.send_message)

bot.tree.add_command(setfile_slash)
bot.tree.add_command(xemfile_slash)
if not os.path.exists('data'):
    os.makedirs('data')

@tasks.loop(minutes=5)
async def cleanup_memory():
    gc.collect()

def get_user_task_count(user_id: str):
    if not os.path.exists('data'):
        return 0
    
    count = 0
    user_id_str = str(user_id)
    
    for folder in os.listdir('data'):
        folder_path = f"data/{folder}"
        luutru_path = f"{folder_path}/luutru.txt"
        
        if os.path.isdir(folder_path) and os.path.exists(luutru_path):
            try:
                with open(luutru_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                parts = content.split(" | ")
                
                task_owner_id = None
                if len(parts) >= 5:
                    if parts[3] == "nhay_top_tag" and len(parts) >= 7:
                        task_owner_id = parts[6]
                    elif parts[3] == "nhay_zalo" and len(parts) >= 8:
                        task_owner_id = parts[4]
                    elif len(parts) >= 5:
                        task_owner_id = parts[4]

                if task_owner_id == user_id_str:
                    count += 1
            except Exception:
                continue
    return count
STATUS_LIST = itertools.cycle([
    discord.Game("🎮 Chơi Liên Quân"),
    discord.Activity(type=discord.ActivityType.watching, name="Sex🧃"),
    discord.Activity(type=discord.ActivityType.listening, name="🎧Người Lạ Ơi"),
    discord.Activity(type=discord.ActivityType.competing, name="🏆 100 quả lọ"),
    discord.Game("Free Fire"),
    discord.Activity(type=discord.ActivityType.watching, name="Xem Danny Code"),
])

@tasks.loop(seconds=30)
async def heartbeat():
    try:
        activity = next(STATUS_LIST)
        await bot.change_presence(status=discord.Status.online, activity=activity)
    except Exception as e:
        print(f"Lỗi khi đổi status: {e}")
def safe_thread_wrapper(func, *args):
    try:
        func(*args)
    except Exception as e:
        print(f"Thread error: {e}")
        folder_name = args[-1] if args else "unknown"
        folder_path = os.path.join("data", folder_name)
        if os.path.exists(folder_path):
            import shutil
            shutil.rmtree(folder_path)

class ZaloAPIException(Exception):
    pass

class LoginMethodNotSupport(ZaloAPIException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

class ZaloLoginError(ZaloAPIException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

class ZaloUserError(ZaloAPIException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

class EncodePayloadError(ZaloAPIException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

class DecodePayloadError(ZaloAPIException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

import enum

class Enum(enum.Enum):
    def __repr__(self):
        return "{}.{}".format(type(self).__name__, self.name)

class ThreadType(Enum):
    USER = 0
    GROUP = 1

class GroupEventType(Enum):
    JOIN = "join"
    LEAVE = "leave"
    UPDATE = "update"
    UNKNOWN = "unknown"
    REACTION = "reaction"
    NEW_LINK = "new_link"
    ADD_ADMIN = "add_admin"
    REMOVE_ADMIN = "remove_admin"
    JOIN_REQUEST = "join_request"
    BLOCK_MEMBER = "block_member"
    REMOVE_MEMBER = "remove_member"
    UPDATE_SETTING = "update_setting"

class EventType(Enum):
    REACTION = "reaction"

import time, datetime
import urllib.parse, json
import gzip, base64, zlib

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": "\"Not-A.Brand\";v=\"99\", \"Chromium\";v=\"124\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Linux\"",
    "origin": "https://chat.zalo.me",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "Accept-Encoding": "gzip",
    "referer": "https://chat.zalo.me/",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
}

COOKIES = {}

def now():
    return int(time.time() * 1000)

def formatTime(format, ftime=now()):
    dt = datetime.datetime.fromtimestamp(ftime / 1000)
    formatted_time = dt.strftime(format)
    return formatted_time

def getHeader(buffer):
    if len(buffer) < 4:
        raise ValueError("Invalid header")
    return [buffer[0], int.from_bytes(buffer[1:3], "little"), buffer[3]]

def getClientMessageType(msgType):
    if (msgType == "webchat"): return 1
    if (msgType == "chat.voice"): return 31
    if (msgType == "chat.photo"): return 32
    if (msgType == "chat.sticker"): return 36
    if (msgType == "chat.doodle"): return 37
    if (msgType == "chat.recommended"): return 38
    if (msgType == "chat.link"): return 38
    if (msgType == "chat.location.new"): return 43
    if (msgType == "chat.video.msg"): return 44
    if (msgType == "share.file"): return 46
    if (msgType == "chat.gif"): return 49
    return 1

def getGroupEventType(act):
    if (act == "join_request"): return GroupEventType.JOIN_REQUEST
    if (act == "join"): return GroupEventType.JOIN
    if (act == "leave"): return GroupEventType.LEAVE
    if (act == "remove_member"): return GroupEventType.REMOVE_MEMBER
    if (act == "block_member"): return GroupEventType.BLOCK_MEMBER
    if (act == "update_setting"): return GroupEventType.UPDATE_SETTING
    if (act == "update"): return GroupEventType.UPDATE
    if (act == "new_link"): return GroupEventType.NEW_LINK
    if (act == "add_admin"): return GroupEventType.ADD_ADMIN
    if (act == "remove_admin"): return GroupEventType.REMOVE_ADMIN
    return GroupEventType.UNKNOWN

def dict_to_raw_cookies(cookies_dict):
    try:
        cookie_string = "; ".join(f"{key}={value}" for key, value in cookies_dict.items())
        if not cookie_string:
            return None
        return cookie_string
    except:
        return None

def _pad(s, block_size):
    padding_length = block_size - len(s) % block_size
    return s + bytes([padding_length]) * padding_length

def _unpad(s, block_size):
    padding_length = s[-1]
    return s[:-padding_length]

def zalo_encode(params, key):
    try:
        key = base64.b64decode(key)
        iv = bytes.fromhex("00000000000000000000000000000000")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = json.dumps(params).encode()
        padded_plaintext = _pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        return base64.b64encode(ciphertext).decode()
    except Exception as e:
        raise EncodePayloadError(f"Unable to encode payload! Error: {e}")

def zalo_decode(params, key):
    try:
        params = urllib.parse.unquote(params)
        key = base64.b64decode(key)
        iv = bytes.fromhex("00000000000000000000000000000000")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = base64.b64decode(params.encode())
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext = _unpad(padded_plaintext, AES.block_size)
        plaintext = plaintext.decode("utf-8")
        if isinstance(plaintext, str):
            plaintext = json.loads(plaintext)
        return plaintext
    except Exception as e:
        raise DecodePayloadError(f"Unable to decode payload! Error: {e}")

class State(object):
    def __init__(cls):
        cls._config = {}
        cls._headers = HEADERS
        cls._cookies = COOKIES
        cls._session = requests.Session()
        cls.user_id = None
        cls.user_imei = None
        cls._loggedin = False

    def get_cookies(cls):
        return cls._cookies

    def set_cookies(cls, cookies):
        cls._cookies = cookies

    def get_secret_key(cls):
        return cls._config.get("secret_key")

    def set_secret_key(cls, secret_key):
        cls._config["secret_key"] = secret_key

    def _get(cls, *args, **kwargs):
        sessionObj = cls._session.get(*args, **kwargs, headers=cls._headers, cookies=cls._cookies)
        return sessionObj

    def _post(cls, *args, **kwargs):
        sessionObj = cls._session.post(*args, **kwargs, headers=cls._headers, cookies=cls._cookies)
        return sessionObj

    def is_logged_in(cls):
        return cls._loggedin

    def login(cls, phone, password, imei, session_cookies=None, user_agent=None):
        if cls._cookies and cls._config.get("secret_key"):
            cls._loggedin = True
            return

        if user_agent:
            cls._headers["User-Agent"] = user_agent

        if cls._cookies:
            params = {
                "imei": imei,
            }
            try:
                response = cls._get("", params=params)
                data = response.json()

                if data.get("error_code") == 0:
                    cls._config = data.get("data")

                    if cls._config.get("secret_key"):
                        cls._loggedin = True
                        cls.user_id = cls._config.get("send2me_id")
                        cls.user_imei = imei
                    else:
                        cls._loggedin = False
                        raise ZaloLoginError("Unable to get `secret key`.")
                else:
                    error = data.get("error_code")
                    content = data.get("error_message")
                    raise ZaloLoginError(f"Error #{error} when logging in: {content}")

            except ZaloLoginError as e:
                raise ZaloLoginError(str(e))

            except Exception as e:
                raise ZaloLoginError(f"An error occurred while logging in! {str(e)}")
        else:
            raise LoginMethodNotSupport("Login method is not supported yet")

class ZaloAPI(object):
    def __init__(self, phone, password, imei, session_cookies=None, user_agent=None, auto_login=True):
        self._state = State()
        self._condition = threading.Event()
        self._listening = False
        self._start_fix = False

        if auto_login:
            if (
                not session_cookies 
                or not self.setSession(session_cookies) 
                or not self.isLoggedIn()
            ):
                self.login(phone, password, imei, user_agent)

    def uid(self):
        return self.uid

    def _get(self, *args, **kwargs):
        return self._state._get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._state._post(*args, **kwargs)

    def _encode(self, params):
        return zalo_encode(params, self._state._config.get("secret_key"))

    def _decode(self, params):
        return zalo_decode(params, self._state._config.get("secret_key"))

    def isLoggedIn(self):
        return self._state.is_logged_in()

    def getSession(self):
        return self._state.get_cookies()

    def setSession(self, session_cookies):
        try:
            if not isinstance(session_cookies, dict):
                return False
            self._state.set_cookies(session_cookies)
            self.uid = self._state.user_id
        except Exception as e:
            print("Failed loading session")
            return False
        return True

    def getSecretKey(self):
        return self._state.get_secret_key()

    def setSecretKey(self, secret_key):
        try:
            self._state.set_secret_key(secret_key)
            return True
        except:
            return False

    def login(self, phone, password, imei, user_agent=None):
        if not (phone and password):
            raise ZaloUserError("Phone and password not set")

        self._state.login(
            phone,
            password,
            imei,
            user_agent=user_agent
        )
        try:
            self._imei = self._state.user_imei
            self.uid = self._state.user_id
        except:
            self._imei = None
            self.uid = self._state.user_id

    def setTyping(self, thread_id, thread_type):
        params = {
            "zpw_ver": 645,
            "zpw_type": 30
        }

        payload = {
            "params": {
                "imei": self._imei
            }
        }

        if thread_type == ThreadType.USER:
            url = "https://tt-chat1-wpa.chat.zalo.me/api/message/typing"
            payload["params"]["toid"] = str(thread_id)
            payload["params"]["destType"] = 3
        elif thread_type == ThreadType.GROUP:
            url = "https://tt-group-wpa.chat.zalo.me/api/group/typing"
            payload["params"]["grid"] = str(thread_id)
        else:
            raise ZaloUserError("Thread type is invalid")

        payload["params"] = self._encode(payload["params"])

        response = self._post(url, params=params, data=payload)
        data = response.json()
        results = data.get("data") if data.get("error_code") == 0 else None
        if results:
            results = self._decode(results)
            return True

        error_code = data.get("error_code")
        error_message = data.get("error_message") or data.get("data")
        raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")

    def sendMessage(self, message, thread_id, thread_type, mark_message=None, ttl=0):
        params = {
            "zpw_ver": 645,
            "zpw_type": 30,
            "nretry": 0
        }

        payload = {
            "params": {
                "message": message.text,
                "clientId": now(),
                "imei": self._imei,
                "ttl": ttl
            }
        }

        if mark_message and mark_message.lower() in ["important", "urgent"]:
            markType = 1 if mark_message.lower() == "important" else 2
            payload["params"]["metaData"] = {"urgency": markType}

        if message.style:
            payload["params"]["textProperties"] = message.style

        if thread_type == ThreadType.USER:
            url = "https://tt-chat2-wpa.chat.zalo.me/api/message/sms"
            payload["params"]["toid"] = str(thread_id)
        elif thread_type == ThreadType.GROUP:
            url = "https://tt-group-wpa.chat.zalo.me/api/group/sendmsg"
            payload["params"]["visibility"] = 0
            payload["params"]["grid"] = str(thread_id)
        else:
            raise ZaloUserError("Thread type is invalid")

        payload["params"] = self._encode(payload["params"])

        response = self._post(url, params=params, data=payload)
        data = response.json()
        results = data.get("data") if data.get("error_code") == 0 else None
        if results:
            results = self._decode(results)
            results = results.get("data") if results.get("data") else results
            if results == None:
                results = {"error_code": 1337, "error_message": "Data is None"}

            if isinstance(results, str):
                try:
                    results = json.loads(results)
                except:
                    results = {"error_code": 1337, "error_message": results}

            return results

        error_code = data.get("error_code")
        error_message = data.get("error_message") or data.get("data")
        raise ZaloAPIException(f"Error #{error_code} when sending requests: {error_message}")

class Message:
    def __init__(self, text="", style=None):
        self.text = text
        self.style = style

def get_guid():
    section_length = int(time.time() * 1000)
    
    def replace_func(c):
        nonlocal section_length
        r = (section_length + random.randint(0, 15)) % 16
        section_length //= 16
        return hex(r if c == "x" else (r & 7) | 8)[2:]

    return "".join(replace_func(c) if c in "xy" else c for c in "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx")

def get_info_from_uid(cookie, uid):
    user_id, fb_dtsg, jazoest, clientRevision, a, req = get_uid_fbdtsg(cookie)
    if user_id and fb_dtsg:
        fb = facebook(cookie)
        if fb.user_id and fb.fb_dtsg:
            return fb.get_info(uid)
    return {"name": "User", "id": uid}

def get_uid_fbdtsg(ck):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': ck,
            'Host': 'www.facebook.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get('https://www.facebook.com/', headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Status Code >> {response.status_code}")
                return None, None, None, None, None, None
                
            html_content = response.text
            
            user_id = None
            fb_dtsg = None
            jazoest = None
            
            script_tags = re.findall(r'<script id="__eqmc" type="application/json[^>]*>(.*?)</script>', html_content)
            for script in script_tags:
                try:
                    json_data = json.loads(script)
                    if 'u' in json_data:
                        user_param = re.search(r'__user=(\d+)', json_data['u'])
                        if user_param:
                            user_id = user_param.group(1)
                            break
                except:
                    continue
            
            fb_dtsg_match = re.search(r'"f":"([^"]+)"', html_content)
            if fb_dtsg_match:
                fb_dtsg = fb_dtsg_match.group(1)
            
            jazoest_match = re.search(r'jazoest=(\d+)', html_content)
            if jazoest_match:
                jazoest = jazoest_match.group(1)
            
            revision_match = re.search(r'"server_revision":(\d+),"client_revision":(\d+)', html_content)
            rev = revision_match.group(1) if revision_match else ""
            
            a_match = re.search(r'__a=(\d+)', html_content)
            a = a_match.group(1) if a_match else "1"
            
            req = "1b"
                
            return user_id, fb_dtsg, rev, req, a, jazoest
                
        except requests.exceptions.RequestException as e:
            print(f"Lỗi Kết Nối Khi Lấy UID/FB_DTSG: {e}")
            return get_uid_fbdtsg(ck)
            
    except Exception as e:
        print(f"Lỗi: {e}")
        return None, None, None, None, None, None

def comment_group_post(cookie, group_id, post_id, message, uidtag=None, nametag=None):
    try:
        user_id, fb_dtsg, jazoest, rev, a, req = get_uid_fbdtsg(cookie)
        
        if not all([user_id, fb_dtsg, jazoest]):
            return False
            
        pstid_enc = base64.b64encode(f"feedback:{post_id}".encode()).decode()
        
        client_mutation_id = str(round(random.random() * 19))
        session_id = get_guid()
        crt_time = int(time.time() * 1000)
        
        variables = {
            "feedLocation": "DEDICATED_COMMENTING_SURFACE",
            "feedbackSource": 110,
            "groupID": group_id,
            "input": {
                "client_mutation_id": client_mutation_id,
                "actor_id": user_id,
                "attachments": None,
                "feedback_id": pstid_enc,
                "formatting_style": None,
                "message": {
                    "ranges": [],
                    "text": message
                },
                "attribution_id_v2": f"SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,tap_search_bar,{crt_time},775647,391724414624676,,",
                "vod_video_timestamp": None,
                "is_tracking_encrypted": True,
                "tracking": [],
                "feedback_source": "DEDICATED_COMMENTING_SURFACE",
                "session_id": session_id
            },
            "inviteShortLinkKey": None,
            "renderLocation": None,
            "scale": 3,
            "useDefaultActor": False,
            "focusCommentID": None,
            "__relay_internal__pv__IsWorkUserrelayprovider": False
        }
        
        if uidtag and nametag:
            name_position = message.find(nametag)
            if name_position != -1:
                variables["input"]["message"]["ranges"] = [
                    {
                        "entity": {
                            "id": uidtag
                        },
                        "length": len(nametag),
                        "offset": name_position
                    }
                ]
            
        payload = {
            'av': user_id,
            '__crn': 'comet.fbweb.CometGroupDiscussionRoute',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'useCometUFICreateCommentMutation',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '10047708791980503'
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': f'https://www.facebook.com/groups/{group_id}',
            'User-Agent': 'python-http/0.27.0'
        }
        
        response = requests.post('https://www.facebook.com/api/graphql', data=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Lỗi khi gửi bình luận: {e}")
        return False

def gen_threading_id():
    return str(
        int(format(int(time.time() * 1000), "b") + 
        ("0000000000000000000000" + 
        format(int(random.random() * 4294967295), "b"))
        [-22:], 2)
    )

def restore_tasks():
    if not os.path.exists('data'):
        return
    for folder in os.listdir('data'):
        folder_path = f"data/{folder}"
        if os.path.isdir(folder_path) and os.path.exists(f"{folder_path}/luutru.txt"):
            try:
                with open(f"{folder_path}/luutru.txt", "r", encoding="utf-8") as f:
                    content = f.read().strip()
                parts = content.split(" | ")
                if len(parts) >= 4:
                    cookie = parts[0]
                    task_type = parts[3]
                    if task_type == "treo_media" and len(parts) >= 6:
                        idbox = parts[1]
                        delay = parts[2]
                        media_url = parts[5]
                        if os.path.exists(f"{folder_path}/messages.txt"):
                            with open(f"{folder_path}/messages.txt", "r", encoding="utf-8") as msg_f:
                                message = msg_f.read()
                            for file in os.listdir(folder_path):
                                if file not in ['luutru.txt', 'messages.txt']:
                                    local_file_path = os.path.join(folder_path, file)
                                    thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_media_func, cookie, idbox, local_file_path, message, delay, folder))
                                    thread.daemon = True
                                    thread.start()
                                    break
                    elif task_type == "treo_contact" and len(parts) >= 6:
                        idbox = parts[1]
                        delay = parts[2]
                        uid_contact = parts[5]
                        if os.path.exists(f"{folder_path}/messages.txt"):
                            with open(f"{folder_path}/messages.txt", "r", encoding="utf-8") as msg_f:
                                message = msg_f.read()
                            thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_contact_func, cookie, idbox, uid_contact, message, delay, folder))
                            thread.daemon = True
                            thread.start()
                    elif task_type == "treo_normal":
                        idbox = parts[1]
                        delay = parts[2]
                        if os.path.exists(f"{folder_path}/message.txt"):
                            with open(f"{folder_path}/message.txt", "r", encoding="utf-8") as msg_f:
                                message = msg_f.read()
                            thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_mess_func, cookie, idbox, message, delay, folder))
                            thread.daemon = True
                            thread.start()
                    elif task_type == "nhay_normal":
                        idbox = parts[1]
                        delay = parts[2]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_func, cookie, idbox, delay, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "nhay_tag" and len(parts) >= 6:
                        idbox = parts[1]
                        delay = parts[2]
                        uid_tag = parts[5]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_tag_func, cookie, idbox, uid_tag, delay, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "nhay_top_tag" and len(parts) >= 7:
                        group_id = parts[1]
                        post_id = parts[2]
                        uid_tag = parts[3]
                        delay = parts[4]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_top_tag_func, cookie, group_id, post_id, uid_tag, delay, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "treoso":
                        idbox = parts[1]
                        delay = parts[2]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_treoso_func, cookie, idbox, delay, folder))
                        thread.daemon = True
                        thread.start()    
                    elif task_type == "nhay_poll":
                        idbox = parts[1]
                        delay = parts[2]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_poll_func, cookie, idbox, delay, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "nhay_namebox":
                        idbox = parts[1]
                        delay = parts[2]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_namebox_func, cookie, idbox, delay, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "nhay_zalo" and len(parts) >= 8:
                        thread_id = parts[1]
                        delay = parts[2]
                        imei = parts[5]
                        session_cookies = parts[6]
                        thread_type = parts[7]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_zalo_func, imei, session_cookies, thread_id, delay, thread_type, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "nhay_discord" and len(parts) >= 6:
                        channel_id = parts[1]
                        delay = parts[2]
                        tokens = parts[5]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_discord_func, tokens, channel_id, delay, folder))
                        thread.daemon = True
                        thread.start()
                    elif task_type == "nhay_tag_discord" and len(parts) >= 7:
                        channel_id = parts[1]
                        delay = parts[2]
                        tokens = parts[5]
                        uid_mention = parts[6]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_nhay_tag_discord_func, tokens, channel_id, uid_mention, delay, folder))
                    elif task_type == "treo_discord" and len(parts) >= 7:
                        channel_id = parts[1]
                        delay = parts[2]
                        tokens = parts[5]
                        message = parts[6]
                        thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_discord_func, tokens, channel_id, message, delay, folder))
                        thread.daemon = True
                        thread.start()

                    print(f"Đã Khôi Phục Task: {folder} - {task_type}")
            except Exception as e:
                print(f"Lỗi khi khôi phục task {folder}: {e}")

import warnings
warnings.simplefilter("always")

def send_msg(token, channel_id, message):
    try:
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        payload = {
            'content': message
        }
        url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"Send Message - Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Error response: {response.text}")
        
        return response.status_code
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def faketyping_discord(token, channel_id):
    try:
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        url = f'https://discord.com/api/v10/channels/{channel_id}/typing'
        response = requests.post(url, headers=headers, timeout=10)
        
        return response.status_code
    except Exception as e:
        print(f"Error sending typing: {e}")
        return None


def start_treo_media_func(cookie, idbox, file_path, ngon, delay_str, folder_name):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if fb.user_id and fb.fb_dtsg:
                sender = MessageSender(fbTools({
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }), {
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }, fb)
                
                active_senders[folder_name] = sender
                sender.get_last_seq_id()
                
                if not sender.connect_mqtt():
                    print("Failed to connect MQTT, retrying...")
                    retry_count += 1
                    time.sleep(10)
                    continue
                
                running = True
                while running:
                    try:
                        folder_path = os.path.join("data", folder_name)
                        if not os.path.exists(folder_path):
                            running = False
                            break
                        sender.send_message_with_attachment(ngon, idbox, file_path)
                        time.sleep(delay)
                    except Exception as e:
                        print(f"Error during sending message with media: {e}")
                        if "connection" in str(e).lower():
                            break
                        time.sleep(10)
                
                if folder_name in active_senders:
                    active_senders[folder_name].stop()
                    del active_senders[folder_name]
                break
                
        except Exception as e:
            print(f"Error initializing Facebook API: {e}")
            retry_count += 1
            time.sleep(10)

def mainRequests(url, data, cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.facebook.com',
        'Cookie': cookie,
        'Referer': 'https://www.facebook.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    return {
        'url': url,
        'data': data,
        'headers': headers,
        'timeout': 30
    }

def tenbox(newTitle, threadID, dataFB):
    if not newTitle or not threadID or not dataFB:
        return {
            "success": False,
            "error": "Thiếu thông tin bắt buộc: newTitle, threadID, hoặc dataFB"
        }
    try:
        messageAndOTID = gen_threading_id()
        current_timestamp = int(time.time() * 1000)
        form_data = {
            "client": "mercury",
            "action_type": "ma-type:log-message",
            "author": f"fbid:{dataFB['FacebookID']}",
            "thread_id": str(threadID),
            "timestamp": current_timestamp,
            "timestamp_relative": str(int(time.time())),
            "source": "source:chat:web",
            "source_tags[0]": "source:chat",
            "offline_threading_id": messageAndOTID,
            "message_id": messageAndOTID,
            "threading_id": gen_threading_id(),
            "thread_fbid": str(threadID),
            "thread_name": str(newTitle),
            "log_message_type": "log:thread-name",
            "fb_dtsg": dataFB["fb_dtsg"],
            "jazoest": dataFB["jazoest"],
            "__user": str(dataFB["FacebookID"]),
            "__a": "1",
            "__req": "1",
            "__rev": dataFB.get("clientRevision", "1015919737")
        }
        url = "https://www.facebook.com/messaging/set_thread_name/"
        response = requests.post(**mainRequests(url, form_data, dataFB["cookieFacebook"]))
        if response.status_code == 200:
            try:
                response_data = response.json()
                if "error" in response_data:
                    return {
                        "success": False
                    }
                return {
                    "success": True
                }
            except:
                return {
                    "success": True
                }
        else:
            return {
                "success": False,
                "error": f"HTTP Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def start_treo_discord_func(tokens, channel_id, message, delay_str, folder_name):
    delay = float(delay_str)
    folder_path = os.path.join("data", folder_name)
    
    token_list = [token.strip() for token in tokens.split('\n') if token.strip()]
    valid_tokens = []
    
    running = True
    while running:
        try:
            folder_path = os.path.join("data", folder_name)
            if not os.path.exists(folder_path):
                running = False
                break
            
            for token in token_list:
                if token not in valid_tokens:
                    status = faketyping_discord(token, channel_id)  
                    if status in [200, 201, 204]:
                        valid_tokens.append(token)
                    elif status in [400, 401, 403]:
                        continue
            
            for token in valid_tokens:
                folder_path = os.path.join("data", folder_name)
                if not os.path.exists(folder_path):
                    running = False
                    break
                
                
                send_msg(token, channel_id, message)
                time.sleep(delay)
                
        except Exception as e:
            print(f"Error in treo discord: {e}")
            time.sleep(10)
def start_nhay_discord_func(tokens, channel_id, delay_str, folder_name, file_name="nhay.txt"):
    delay = float(delay_str)
    folder_path = os.path.join("data", folder_name)

    token_list = [token.strip() for token in tokens.split('\n') if token.strip()]
    valid_tokens = []

    running = True
    while running:
        try:
            if not os.path.exists(folder_path):
                running = False
                break

            for token in token_list:
                if token not in valid_tokens:
                    status = faketyping_discord(token, channel_id)
                    if status in [200, 201, 204]:
                        valid_tokens.append(token)
                    elif status in [400, 401, 403]:
                        continue

            current_dir = os.path.dirname(os.path.abspath(__file__))
            nhay_path = os.path.join(current_dir, file_name)

            if not os.path.exists(nhay_path):
                with open(nhay_path, "w", encoding="utf-8") as f:
                    f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\ncay ak\ncn nqu")

            with open(nhay_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if not os.path.exists(folder_path):
                    running = False
                    break

                msg = line.strip()
                if msg:
                    for token in valid_tokens:
                        faketyping_discord(token, channel_id)
                        time.sleep(1)
                        send_msg(token, channel_id, msg)
                        time.sleep(delay)

        except Exception as e:
            print(f"Error in nhay discord: {e}")
            time.sleep(10)


def start_nhay_tag_discord_func(tokens, channel_id, uid_mention, delay_str, folder_name, file_name="nhay.txt"):
    delay = float(delay_str)
    folder_path = os.path.join("data", folder_name)

    token_list = [token.strip() for token in tokens.split('\n') if token.strip()]
    valid_tokens = []

    running = True
    while running:
        try:
            if not os.path.exists(folder_path):
                running = False
                break

            for token in token_list:
                if token not in valid_tokens:
                    status = faketyping_discord(token, channel_id)
                    if status in [200, 201, 204]:
                        valid_tokens.append(token)
                    elif status in [400, 401, 403]:
                        continue

            current_dir = os.path.dirname(os.path.abspath(__file__))
            nhay_path = os.path.join(current_dir, file_name)

            if not os.path.exists(nhay_path):
                with open(nhay_path, "w", encoding="utf-8") as f:
                    f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\ncay ak\ncn nqu")

            with open(nhay_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if not os.path.exists(folder_path):
                    running = False
                    break

                msg = line.strip()
                if msg:
                    for token in valid_tokens:
                        faketyping_discord(token, channel_id)
                        time.sleep(1)

                        tagged_msg = random.choice([f"{msg} <@{uid_mention}>", f"<@{uid_mention}> {msg}"])
                        send_msg(token, channel_id, tagged_msg)
                        time.sleep(delay)

        except Exception as e:
            print(f"Error in nhay tag discord: {e}")
            time.sleep(10)

def start_nhay_namebox_func(cookie, idbox, delay_str, folder_name, file_path=None):
    delay = float(delay_str)
    folder_path = os.path.join("data", folder_name)
    running = True

    while running:
        if not os.path.exists(folder_path):
            break
        try:
            user_id, fb_dtsg, jazoest, rev, a, req = get_uid_fbdtsg(cookie)
            if not all([user_id, fb_dtsg, jazoest]):
                time.sleep(10)
                continue

            dataFB = {
                "FacebookID": user_id,
                "fb_dtsg": fb_dtsg,
                "jazoest": jazoest,
                "clientRevision": rev,
                "cookieFacebook": cookie
            }

        
            lines = read_lines_from_file(file_path, "nhay.txt")

            for msg in lines:
                if not os.path.exists(folder_path):
                    running = False
                    break

                result = tenbox(msg, idbox, dataFB)
                if result["success"]:
                    print(f"Đổi tên thành công: {msg}")
                else:
                    print(f"Lỗi đổi tên: {result['error']}")
                time.sleep(delay)

        except Exception as e:
            print(f"Error in start_nhay_namebox_func: {e}")
            time.sleep(10)

class TreoDiscordModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Treo Discord", timeout=None)

        self.tokens = discord.ui.TextInput(
            label="Nhập User Token",
            placeholder="1 Token 1 Dòng Nếu Treo Đa Token",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.tokens)

        self.channel_id = discord.ui.TextInput(label="Nhập ID Kênh", required=True)
        self.add_item(self.channel_id)

        self.content = discord.ui.TextInput(
            label="Nhập Nội Dung",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.content)

        self.delay = discord.ui.TextInput(label="Nhập Delay", required=True)
        self.add_item(self.delay)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)


        if check_task_limit() >= 200:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                    description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        if user_id_str not in config_data.get("task", {}):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không Có Quyền",
                    description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        if user_current_tasks >= user_max_tasks:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                    description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

    
        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"discord_tokens | {self.channel_id.value} | {self.delay.value} | treo_discord | {interaction.user.id} | {self.tokens.value} | {self.content.value}")

        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_treo_discord_func, self.tokens.value, self.channel_id.value, self.content.value, self.delay.value, folder_id)
        )
        thread.daemon = True
        thread.start()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Tasks Thành Công ✅",
                description=f"ID Tasks: {folder_id}",
                color=0x00FF00
            ),
            ephemeral=True
        )


class NhayDiscordModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Nhây Discord", timeout=None)

        self.tokens = discord.ui.TextInput(
            label="Nhập User Token",
            placeholder="1 Token 1 Dòng Nếu Treo Đa Token",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.tokens)

        self.channel_id = discord.ui.TextInput(label="Nhập ID Kênh", required=True)
        self.add_item(self.channel_id)

        self.delay = discord.ui.TextInput(label="Nhập Delay (>=3s)", required=True)
        self.add_item(self.delay)

        self.file_name = discord.ui.TextInput(
            label="Tên File Nội Dung (mặc định nhay.txt)",
            required=False,
            placeholder="ví dụ: spam.txt"
        )
        self.add_item(self.file_name)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

    
        if check_task_limit() >= 200:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                    description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        if user_id_str not in config_data.get("task", {}):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không Có Quyền",
                    description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        if user_current_tasks >= user_max_tasks:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                    description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        
        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        file_name = self.file_name.value.strip() if self.file_name.value else "nhay.txt"

        
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"discord_tokens | {self.channel_id.value} | {self.delay.value} | nhay_discord | {interaction.user.id} | {self.tokens.value} | {file_name}")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\ncay ak\ncn nqu")

  
        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_nhay_discord_func, self.tokens.value, self.channel_id.value, self.delay.value, folder_id, file_name)
        )
        thread.daemon = True
        thread.start()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Tasks Thành Công ✅",
                description=f"ID Tasks: {folder_id}",
                color=0x00FF00
            ),
            ephemeral=True
        )


class NhayTagDiscordModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Nhây Tag Discord", timeout=None)

        self.tokens = discord.ui.TextInput(
            label="Nhập User Token",
            placeholder="1 Token 1 Dòng Nếu Treo Đa Token",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.tokens)

        self.channel_id = discord.ui.TextInput(label="Nhập ID Kênh", required=True)
        self.add_item(self.channel_id)

        self.uid_mention = discord.ui.TextInput(label="Nhập UID Cần Mention", required=True)
        self.add_item(self.uid_mention)

        self.delay = discord.ui.TextInput(label="Nhập Delay (>=3s)", required=True)
        self.add_item(self.delay)

        self.file_name = discord.ui.TextInput(
            label="Tên File Nội Dung (mặc định nhay.txt)",
            required=False,
            placeholder="ví dụ: spam_tag.txt"
        )
        self.add_item(self.file_name)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

    
        if check_task_limit() >= 200:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                    description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        if user_id_str not in config_data.get("task", {}):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không Có Quyền",
                    description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        if user_current_tasks >= user_max_tasks:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                    description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

       
        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        file_name = self.file_name.value.strip() if self.file_name.value else "nhay.txt"

        
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"discord_tokens | {self.channel_id.value} | {self.delay.value} | nhay_tag_discord | {interaction.user.id} | {self.tokens.value} | {self.uid_mention.value} | {file_name}")

        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\ncay ak\ncn nqu")

   
        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_nhay_tag_discord_func, self.tokens.value, self.channel_id.value, self.uid_mention.value, self.delay.value, folder_id, file_name)
        )
        thread.daemon = True
        thread.start()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Tasks Thành Công ✅",
                description=f"ID Tasks: {folder_id}",
                color=0x00FF00
            ),
            ephemeral=True
        )


class TreoSoModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="📜 Treo Sớ", timeout=None)

        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)

        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)

        self.delay = discord.ui.TextInput(
            label="Nhập Delay (giây)",
            required=True
        )
        self.add_item(self.delay)

       
        self.file_name = discord.ui.TextInput(
            label="Tên file (trong xemfile)",
            placeholder="VD: so_custom.txt (bỏ trống = mặc định so.txt)",
            required=False
        )
        self.add_item(self.file_name)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                    description="Bot đã chạy tối đa 200/200 tasks. Vui lòng thử lại sau.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        if user_id_str not in config_data.get("task", {}):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không Có Quyền",
                    description="Bạn không có quyền tạo task. Vui lòng liên hệ admin để mua task.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        if user_current_tasks >= user_max_tasks:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                    description=f"Bạn đã tạo tối đa **{user_max_tasks}** task được cho phép.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        
        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        
        file_path = None
        if self.file_name.value:
            files = get_user_files(interaction.user.id)
            for path in files:
                if os.path.basename(path) == self.file_name.value.strip():
                    file_path = path
                    break

        
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | treoso | {interaction.user.id} | {file_path or ''}")

   
        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_treoso_func, self.cookies.value, self.idbox.value, self.delay.value, folder_id, file_path)
        )
        thread.daemon = True
        thread.start()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Task Treo Sớ Thành Công ✅",
                description=f"ID Task: `{folder_id}`\nFile dùng: `{os.path.basename(file_path) if file_path else 'so.txt (mặc định)'}`",
                color=0x00FF00
            ), ephemeral=True
        )

class TreoSoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TreoSoModal()
        await interaction.response.send_modal(modal)
class NhayNameBoxModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Nhây Name Box", timeout=None)

        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)

        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)

        self.delay = discord.ui.TextInput(
            label="Nhập Delay (>= 3 giây)",
            required=True,
            placeholder="Ví dụ: 3"
        )
        self.add_item(self.delay)

        
        self.file_name = discord.ui.TextInput(
            label="Tên file (trong xemfile)",
            required=False,
            placeholder="VD: mynamebox.txt (bỏ trống = nhay.txt mặc định)"
        )
        self.add_item(self.file_name)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            delay_value = float(self.delay.value)
            if delay_value < 3:
                await interaction.response.send_message(
                    "❌ Delay phải ≥ 3 giây.", ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "❌ Delay phải là một con số hợp lệ.", ephemeral=True
            )
            return

        if check_task_limit() >= 150:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã đạt giới hạn 150/150 task",
                    description="Hãy xóa task cũ trước khi tạo task mới.",
                    color=0xFF0000
                ),
                ephemeral=True
            )
            return

        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        file_path = None
        if self.file_name.value:
            files = get_user_files(interaction.user.id)
            for path in files:
                if os.path.basename(path) == self.file_name.value.strip():
                    file_path = path
                    break

      
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | nhay_namebox | {interaction.user.id} | {file_path or ''}")

   
        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_nhay_namebox_func, self.cookies.value, self.idbox.value, self.delay.value, folder_id, file_path)
        )
        thread.daemon = True
        thread.start()

     
        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Task Thành Công ✅",
                description=f"ID Task: `{folder_id}`\nFile: `{os.path.basename(file_path) if file_path else 'nhay.txt (mặc định)'}`",
                color=0x00FF00
            ),
            ephemeral=True
        )


class NhayNameBoxView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NhayNameBoxModal()
        await interaction.response.send_modal(modal)

def start_treo_contact_func(cookie, idbox, contact_uid, ngon, delay_str, folder_name):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if fb.user_id and fb.fb_dtsg:
                sender = MessageSender(fbTools({
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }), {
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }, fb)
                
                active_senders[folder_name] = sender
                sender.get_last_seq_id()
                
                if not sender.connect_mqtt():
                    print("Failed to connect MQTT, retrying...")
                    retry_count += 1
                    time.sleep(10)
                    continue
                
                running = True
                while running:
                    try:
                        folder_path = os.path.join("data", folder_name)
                        if not os.path.exists(folder_path):
                            running = False
                            break
                        sender.share_contact(ngon, contact_uid, idbox)
                        time.sleep(delay)
                    except Exception as e:
                        print(f"Error during sharing contact: {e}")
                        if "connection" in str(e).lower():
                            break
                        time.sleep(10)
                
                if folder_name in active_senders:
                    active_senders[folder_name].stop()
                    del active_senders[folder_name]
                break
                
        except Exception as e:
            print(f"Error initializing Facebook API: {e}")
            retry_count += 1
            time.sleep(10)

def start_treo_mess_func(cookie, idbox, ngon, delay_str, folder_name):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if fb.user_id and fb.fb_dtsg:
                sender = MessageSender(fbTools({
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }), {
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }, fb)
                
                active_senders[folder_name] = sender
                sender.get_last_seq_id()
                
                if not sender.connect_mqtt():
                    print("Failed to connect MQTT, retrying...")
                    retry_count += 1
                    time.sleep(10)
                    continue
                    
                running = True
                while running:
                    try:
                        folder_path = os.path.join("data", folder_name)
                        if not os.path.exists(folder_path):
                            running = False
                            break
                        sender.send_message(ngon, idbox)
                        time.sleep(delay)
                    except Exception as e:
                        print(f"Error during sending message: {e}")
                        if "connection" in str(e).lower():
                            break
                        time.sleep(10)
                
                if folder_name in active_senders:
                    active_senders[folder_name].stop()
                    del active_senders[folder_name]
                break
                
        except Exception as e:
            print(f"Error initializing Facebook API: {e}")
            retry_count += 1
            time.sleep(10)

import os
import time
import random

def start_nhay_func(cookie, idbox, delay_str, folder_name, file_path=None):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if not (fb.user_id and fb.fb_dtsg):
                raise Exception("Không lấy được thông tin Facebook user_id/fb_dtsg")

            facebook_data = {
                "FacebookID": fb.user_id,
                "fb_dtsg": fb.fb_dtsg,
                "clientRevision": fb.rev,
                "jazoest": fb.jazoest,
                "cookieFacebook": cookie
            }

            sender = MessageSender(fbTools(facebook_data), facebook_data, fb)
            active_senders[folder_name] = sender
            sender.get_last_seq_id()

            if not sender.connect_mqtt():
                print("[start_nhay_func] ❌ Failed to connect MQTT, retrying...")
                retry_count += 1
                time.sleep(10)
                continue

            running = True
            while running:
                folder_path = os.path.join("data", folder_name)
                if not os.path.exists(folder_path):
                    running = False
                    break

                
                lines = read_lines_from_file(file_path, "nhay.txt")

                for msg in lines:
                    if not os.path.exists(folder_path):
                        running = False
                        break
                    sender.send_typing_indicator(idbox)
                    sender.send_message(msg, idbox)
                    print(f"[start_nhay_func] ✅ Sent: {msg}")
                    time.sleep(delay)

         
            if folder_name in active_senders:
                active_senders[folder_name].stop()
                del active_senders[folder_name]
            break

        except Exception as e:
            print(f"[start_nhay_func] ⚠️ Error: {e}")
            retry_count += 1
            time.sleep(10)


def start_nhay_tag_func(cookie, idbox, uid_tag, delay_str, folder_name, file_path=None):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if not (fb.user_id and fb.fb_dtsg):
                raise Exception("Không lấy được thông tin Facebook user_id/fb_dtsg")

          
            uid = uid_tag
            user_info = fb.get_info(uid) or {}
            ten = user_info.get("name", "User")

            facebook_data = {
                "FacebookID": fb.user_id,
                "fb_dtsg": fb.fb_dtsg,
                "clientRevision": fb.rev,
                "jazoest": fb.jazoest,
                "cookieFacebook": cookie
            }

            sender = MessageSender(fbTools(facebook_data), facebook_data, fb)
            active_senders[folder_name] = sender
            sender.get_last_seq_id()

            if not sender.connect_mqtt():
                print("[start_nhay_tag_func] ❌ Failed to connect MQTT, retrying...")
                retry_count += 1
                time.sleep(10)
                continue

            running = True
            while running:
                folder_path = os.path.join("data", folder_name)
                if not os.path.exists(folder_path):
                    running = False
                    break

             
                lines = read_lines_from_file(file_path, "nhay.txt")

                for msg in lines:
                    if not os.path.exists(folder_path):
                        running = False
                        break
                    if msg:
                        msg_with_tag = random.choice([f"{ten} {msg}", f"{msg} {ten}"])
                        mention = {"id": uid, "tag": ten}
                        sender.send_typing_indicator(idbox)
                        sender.send_message(text=msg_with_tag, mention=mention, thread_id=idbox)
                        print(f"[start_nhay_tag_func] ✅ Sent: {msg_with_tag}")
                        time.sleep(delay)

           
            if folder_name in active_senders:
                active_senders[folder_name].stop()
                del active_senders[folder_name]
            break

        except Exception as e:
            print(f"[start_nhay_tag_func] ⚠️ Error: {e}")
            retry_count += 1
            time.sleep(10)
def start_nhay_top_tag_func(cookie, group_id, post_id, uid_tag, delay_str, folder_name, file_path=None):
    delay = float(delay_str)
    folder_path = os.path.join("data", folder_name)
    error_log = os.path.join(folder_path, "error.log")

    try:
        user_info = get_info_from_uid(cookie, uid_tag)
        ten_tag = user_info.get("name", "User")
    except Exception as e:
        with open(error_log, "a", encoding="utf-8") as f:
            f.write(f"[InitError] UID {uid_tag}: {e}\n")
        return

 
    if file_path and os.path.exists(file_path):
        nhay_path = file_path
    else:
     
        current_dir = os.path.dirname(os.path.abspath(__file__))
        nhay_path = os.path.join(current_dir, "nhay.txt")
        if not os.path.exists(nhay_path):
            with open(nhay_path, "w", encoding="utf-8") as f:
                f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\ncay ak\ncn nqu")

    running = True
    while running:
        if not os.path.exists(folder_path):
            break
        try:
            with open(nhay_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            for line in lines:
                if not os.path.exists(folder_path):
                    running = False
                    break
                msg_with_tag = random.choice([f"{ten_tag} {line}", f"{line} {ten_tag}"])
                try:
                    comment_group_post(cookie, group_id, post_id, msg_with_tag, uid_tag, ten_tag)
                except Exception as e:
                    with open(error_log, "a", encoding="utf-8") as f:
                        f.write(f"[CommentError] {msg_with_tag}: {e}\n")
                time.sleep(delay)

        except Exception as e:
            with open(error_log, "a", encoding="utf-8") as f:
                f.write(f"[LoopError] {e}\n")
            time.sleep(10)


def start_treoso_func(cookie, idbox, delay_str, folder_name, file_path=None):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if fb.user_id and fb.fb_dtsg:
                sender = MessageSender(fbTools({
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }), {
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }, fb)

                active_senders[folder_name] = sender
                sender.get_last_seq_id()

                if not sender.connect_mqtt():
                    print("Failed to connect MQTT, retrying...")
                    retry_count += 1
                    time.sleep(10)
                    continue

                running = True
                while running:
                    try:
                        folder_path = os.path.join("data", folder_name)
                        if not os.path.exists(folder_path):
                            running = False
                            break

                        
                        lines = read_lines_from_file(file_path, "so.txt")

                        for msg in lines:
                            if not os.path.exists(folder_path):
                                running = False
                                break
                            if msg:
                                sender.send_typing_indicator(idbox)
                                sender.send_message(msg, idbox)
                                time.sleep(delay)

                    except Exception as e:
                        print(f"Error During Treo Sớ: {e}")
                        if "connection" in str(e).lower():
                            break
                        time.sleep(10)

                if folder_name in active_senders:
                    active_senders[folder_name].stop()
                    del active_senders[folder_name]
                break

        except Exception as e:
            print(f"Error Initializing Facebook API: {e}")
            retry_count += 1
            time.sleep(10)

def start_nhay_poll_func(cookie, idbox, delay_str, folder_name, file_path=None):
    delay = float(delay_str)
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            fb = facebook(cookie)
            if fb.user_id and fb.fb_dtsg:
                sender = MessageSender(fbTools({
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }), {
                    "FacebookID": fb.user_id,
                    "fb_dtsg": fb.fb_dtsg,
                    "clientRevision": fb.rev,
                    "jazoest": fb.jazoest,
                    "cookieFacebook": cookie
                }, fb)

                active_senders[folder_name] = sender
                sender.get_last_seq_id()

                if not sender.connect_mqtt():
                    retry_count += 1
                    time.sleep(10)
                    continue

                
                if file_path and os.path.exists(file_path):
                    nhay_path = file_path
                else:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    nhay_path = os.path.join(current_dir, "nhay.txt")
                    if not os.path.exists(nhay_path):
                        with open(nhay_path, "w", encoding="utf-8") as f:
                            f.write("cay ak\ncn choa\nsua em\nsua de\nmanh em\ncay ak\ncn nqu")

                running = True
                while running:
                    try:
                        folder_path = os.path.join("data", folder_name)
                        if not os.path.exists(folder_path):
                            running = False
                            break

                        with open(nhay_path, "r", encoding="utf-8") as f:
                            lines = [line.strip() for line in f.readlines() if line.strip()]

                        if len(lines) < 3:
                            time.sleep(delay)
                            continue

                        for line in lines:
                            folder_path = os.path.join("data", folder_name)
                            if not os.path.exists(folder_path):
                                running = False
                                break

                            title = line.strip()
                            if title:
                                available_options = [opt for opt in lines if opt != title]
                                if len(available_options) >= 2:
                                    options = random.sample(available_options, 2)
                                else:
                                    options = available_options + random.choices(lines, k=2-len(available_options))

                                sender.ws_req_number += 1
                                sender.ws_task_number += 1

                                task_payload = {
                                    "question_text": title,
                                    "thread_key": int(idbox),
                                    "options": options,
                                    "sync_group": 1,
                                }

                                task = {
                                    "failure_count": None,
                                    "label": "163",
                                    "payload": json.dumps(task_payload, separators=(",", ":")),
                                    "queue_name": "poll_creation",
                                    "task_id": sender.ws_task_number,
                                }

                                content = {
                                    "app_id": "2220391788200892",
                                    "payload": {
                                        "data_trace_id": None,
                                        "epoch_id": int(generate_offline_threading_id()),
                                        "tasks": [task],
                                        "version_id": "7158486590867448",
                                    },
                                    "request_id": sender.ws_req_number,
                                    "type": 3,
                                }

                                content["payload"] = json.dumps(content["payload"], separators=(",", ":"))

                                try:
                                    sender.mqtt.publish(
                                        topic="/ls_req",
                                        payload=json.dumps(content, separators=(",", ":")),
                                        qos=1,
                                        retain=False,
                                    )
                                except Exception as e:
                                    print(f"Error publishing poll: {e}")

                                time.sleep(delay)
                    except Exception as e:
                        print(f"Error during nhây poll: {e}")
                        if "connection" in str(e).lower():
                            break
                        time.sleep(10)

                if folder_name in active_senders:
                    active_senders[folder_name].stop()
                    del active_senders[folder_name]
                break

        except Exception as e:
            print(f"Error initializing Facebook API: {e}")
            retry_count += 1
            time.sleep(10)

class MetaAI:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.cookies = {}
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            'sec-ch-ua-platform': "\"Windows\"",
            'sec-ch-ua': "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
            'sec-ch-ua-mobile': "?0",
            'origin': "https://www.meta.ai",
            'sec-fetch-site': "same-site",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://www.meta.ai/",
            'accept-language': "vi-VN,vi;q=0.9",
            'priority': "u=1, i",
        }
    
    def extract_value(self, text: str, start_str: str, end_str: str) -> str:
        try:
            start = text.index(start_str) + len(start_str)
            end = text.index(end_str, start)
            return text[start:end]
        except ValueError:
            return ""
    
    def extract_chat(self, response_text: str) -> Dict[str, str]:
        try:
            latest_messages = {
                "user": "",
                "assistant": ""
            }
            
            lines = response_text.strip().split('\n')
            for line in reversed(lines):
                if not line.strip():
                    continue
                    
                try:
                    json_data = json.loads(line)
                    
                    if "data" not in json_data:
                        continue
                        
                    node = json_data.get("data", {}).get("node", {})
                    if not node:
                        continue

                    user_msg = node.get("user_request_message", {})
                    if user_msg and "snippet" in user_msg and not latest_messages["user"]:
                        latest_messages["user"] = user_msg["snippet"]
              
                    bot_msg = node.get("bot_response_message", {})
                    if bot_msg and "snippet" in bot_msg:
                        if bot_msg.get("streaming_state") == "OVERALL_DONE":
                            content = bot_msg["snippet"].replace("**", "").strip()
                            if content and not latest_messages["assistant"]:
                                latest_messages["assistant"] = content
                                break
                            
                except json.JSONDecodeError:
                    continue
                    
            return latest_messages
                
        except Exception as e:
            print(f"Error parsing chat: {str(e)}")
            return {"user": "", "assistant": ""}
    
    def initialize_session(self) -> bool:
        try:
            response = self.session.get('https://meta.ai', headers=self.headers)
            __csr = self.extract_value(response.text, '"client_revision":', ',"')
            
            self.cookies = {
                "_js_datr": self.extract_value(response.text, '_js_datr":{"value":"', '",'),
                "datr": self.extract_value(response.text, 'datr":{"value":"', '",'),
                "lsd": self.extract_value(response.text, '"LSD",[],{"token":"', '"}'),
                "fb_dtsg": self.extract_value(response.text, 'DTSGInitData",[],{"token":"', '"'),
                "abra_csrf": self.extract_value(response.text, 'abra_csrf":{"value":"', '",')
            }

            url = "https://www.meta.ai/api/graphql/"
            payload = {
                "lsd": self.cookies["lsd"],
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "useAbraAcceptTOSForTempUserMutation",
                "variables": {
                    "dob": "1999-01-01",
                    "icebreaker_type": "TEXT",
                    "__relay_internal__pv__WebPixelRatiorelayprovider": 1,
                },
                "doc_id": "7604648749596940",
            }

            payload = urllib.parse.urlencode(payload)
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "cookie": f'_js_datr={self.cookies["_js_datr"]}; abra_csrf={self.cookies["abra_csrf"]}; datr={self.cookies["datr"]};',
                "sec-fetch-site": "same-origin",
                "x-fb-friendly-name": "useAbraAcceptTOSForTempUserMutation",
            }
            
            response = self.session.post(url, headers=headers, data=payload)
            auth_json = response.json()
            self.access_token = auth_json["data"]["xab_abra_accept_terms_of_service"]["new_temp_user_auth"]["access_token"]
            
            return True
            
        except Exception as e:
            print(f"Error initializing session: {str(e)}")
            return False
    
    def ask_question(self, question: str) -> Optional[str]:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.access_token:
                    if not self.initialize_session():
                        return None
                
                url = "https://graph.meta.ai/graphql?locale=user"
                payload = {
                    'av': '0',
                    'access_token': self.access_token,
                    '__user': '0',
                    '__a': '1',
                    '__req': '5',
                    '__hs': '20139.HYP:abra_pkg.2.1...0',
                    'dpr': '1',
                    '__ccg': 'GOOD',
                    '__rev': '1020250634',
                    '__s': 'ukq0lm:22y2yf:rx88gm',
                    '__hsi': '7473469487460105169',
                    '__dyn': '7xeUmwlEnwn8K2Wmh0no6u5U4e0yoW3q32360CEbo19oe8hw2nVE4W099w8G1Dz81s8hwnU2lwv89k2C1Fwc60D85m1mzXwae4UaEW4U2FwNwmE2eU5O0EoS0raazo11E2ZwrUdUco9E3Lwr86C1nw4xxW2W5-fwmU3yw',
                    '__csr': '',
                    '__comet_req': '46',
                    'lsd': self.cookies['lsd'],
                    'jazoest': '',
                    '__spin_r': '1020250634',
                    '__spin_b': 'trunk',
                    '__spin_t': str(int(time.time() * 1000)),
                    '__jssesw': '1',
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'useAbraSendMessageMutation',
                    'variables': json.dumps({
                        "message": {"sensitive_string_value": question},
                        "externalConversationId": str(uuid.uuid4()),
                        "offlineThreadingId": str(int(time.time() * 1000)),
                        "suggestedPromptIndex": None,
                        "flashVideoRecapInput": {"images": []},
                        "flashPreviewInput": None,
                        "promptPrefix": None,
                        "entrypoint": "ABRA__CHAT__TEXT",
                        "icebreaker_type": "TEXT_V2",
                        "attachments": [],
                        "attachmentsV2": [],
                        "activeMediaSets": None,
                        "activeCardVersions": [],
                        "activeArtifactVersion": None,
                        "userUploadEditModeInput": None,
                        "reelComposeInput": None,
                        "qplJoinId": "fc43f4e563f41b383",
                        "gkAbraArtifactsEnabled": False,
                        "model_preference_override": None,
                        "threadSessionId": str(uuid.uuid4()),
                        "__relay_internal__pv__AbraPinningConversationsrelayprovider": False,
                        "__relay_internal__pv__AbraArtifactsEnabledrelayprovider": False,
                        "__relay_internal__pv__WebPixelRatiorelayprovider": 1,
                        "__relay_internal__pv__AbraSearchInlineReferencesEnabledrelayprovider": True,
                        "__relay_internal__pv__AbraComposedTextWidgetsrelayprovider": False,
                        "__relay_internal__pv__AbraSearchReferencesHovercardEnabledrelayprovider": True,
                        "__relay_internal__pv__AbraCardNavigationCountrelayprovider": True,
                        "__relay_internal__pv__AbraDebugDevOnlyrelayprovider": False,
                        "__relay_internal__pv__AbraHasNuxTourrelayprovider": True,
                        "__relay_internal__pv__AbraQPSidebarNuxTriggerNamerelayprovider": "meta_dot_ai_abra_web_message_actions_sidebar_nux_tour",
                        "__relay_internal__pv__AbraSurfaceNuxIDrelayprovider": "12177",
                        "__relay_internal__pv__AbraFileUploadsrelayprovider": False,
                        "__relay_internal__pv__AbraQPDocUploadNuxTriggerNamerelayprovider": "meta_dot_ai_abra_web_doc_upload_nux_tour",
                        "__relay_internal__pv__AbraQPFileUploadTransparencyDisclaimerTriggerNamerelayprovider": "meta_dot_ai_abra_web_file_upload_transparency_disclaimer",
                        "__relay_internal__pv__AbraUpsellsKillswitchrelayprovider": True,
                        "__relay_internal__pv__AbraIcebreakerImagineFetchCountrelayprovider": 20,
                        "__relay_internal__pv__AbraImagineYourselfIcebreakersrelayprovider": False,
                        "__relay_internal__pv__AbraEmuReelsIcebreakersrelayprovider": False,
                        "__relay_internal__pv__AbraArtifactsDisplayHeaderV2relayprovider": False,
                        "__relay_internal__pv__AbraArtifactEditorDebugModerelayprovider": False,
                        "__relay_internal__pv__AbraArtifactSharingrelayprovider": False,
                        "__relay_internal__pv__AbraArtifactEditorSaveEnabledrelayprovider": False,
                        "__relay_internal__pv__AbraArtifactEditorDownloadHTMLEnabledrelayprovider": False,
                        "__relay_internal__pv__AbraArtifactsRenamingEnabledrelayprovider": False
                    }),
                    'server_timestamps': 'true',
                    'doc_id': '9614969011880432'
                }

                response = self.session.post(url, data=payload, headers=self.headers, timeout=30)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                time.sleep(2)
                
                ai_response = self.extract_chat(response.text)
                
                if ai_response and ai_response.get("assistant") and ai_response["assistant"].strip():
                    return ai_response["assistant"]
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Retry {retry_count}/{max_retries} - No response content")
                        time.sleep(1)
                        self.access_token = None
                        continue
                    
            except Exception as e:
                retry_count += 1
                print(f"Error asking question (attempt {retry_count}): {str(e)}")
                if retry_count < max_retries:
                    time.sleep(2)
                    self.access_token = None
                    continue
                
        return None

meta_ai = MetaAI()

@bot.event
async def on_ready():
    print(f'{bot.user} Đã Online!')
    await asyncio.get_event_loop().run_in_executor(None, meta_ai.initialize_session)
    cleanup_memory.start()
    heartbeat.start()
    restore_tasks()
    
    scheduler.start()
    
    scheduler.add_job(
        reset_daily_data,
        CronTrigger(hour=12, minute=0),
        id='reset_daily_data'
    )
    
    scheduler.add_job(
        reset_user_tasks,
        CronTrigger(hour=6, minute=0),
        id='reset_user_tasks'
    )
    
def generate_random_key(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def load_user_data():
    try:
        if os.path.exists('user_data.json'):
            with open('user_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"user_keys": {}, "user_nhapkey_count": {}}

def save_user_data():
    data = {
        "user_keys": user_keys,
        "user_nhapkey_count": user_nhapkey_count
    }
    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def reset_daily_data():
    global user_keys, user_nhapkey_count
    user_keys.clear()
    user_nhapkey_count.clear()
    save_user_data()

async def reset_user_tasks():
    config = load_config()
    if 'task' not in config:
        return
    if 'task_used' not in config:
        config['task_used'] = {}
    if 'admin_added_users' not in config:
        config['admin_added_users'] = {}

    for user_id in list(config['task'].keys()):
        if user_id in config['admin_added_users']:
            continue
            
        current_task = config['task'].get(user_id, 0)
        used_task = config['task_used'].get(user_id, 0)
        user_nhapkey_count_val = user_nhapkey_count.get(user_id, 0)

        if user_nhapkey_count_val < used_task:
            diff = used_task - user_nhapkey_count_val
            new_task = max(0, current_task - diff)
            config['task'][user_id] = new_task

        if user_nhapkey_count_val == 0:
            config['task'][user_id] = 0

    config['task_used'] = {}
    save_config(config)
    
    total_users = len(config['task'])
    admin_added_count = len(config['admin_added_users'])
    reset_count = total_users - admin_added_count

@bot.event
async def on_disconnect():
    print("Bot disconnected, attempting to reconnect...")

@bot.event
async def on_resumed():
    print("Bot connection resumed")

def check_ownervip():
    def predicate(ctx):
        return str(ctx.author.id) in config['ownerVIP']
    return commands.check(predicate)

@bot.command(name='meta')

async def meta_command(ctx, *, question: str = None):
    if not question:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Vui Lòng Nhập Câu Hỏi\nVí Dụ: meta hôm này thời tiết thế nào?`",
            color=0xFF69B4
        )
        await ctx.reply(embed=embed)
        return
    
    loading_embed = discord.Embed(
        title="⏳ Đang Xử Lý...",
        description="Meta AI Đang Suy Nghĩ Vui Lòng Đợi...",
        color=0xFF69B4
    )
    loading_message = await ctx.reply(embed=loading_embed)
    
    try:
        answer = await asyncio.get_event_loop().run_in_executor(
            None, meta_ai.ask_question, question
        )
        
        if answer:
            if len(answer) > 1900:
                answer = answer[:1900] + "..."
            
            embed = discord.Embed(
                title="👤 Meta AI 👤",
                description=f"**Câu Hỏi:** {question}\n\n**Câu Trả Lời:** {answer}",
                color=0xFF69B4
            )
            embed.set_footer(text=f"Được Hỏi Bởi {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        else:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Không Thể Lấy Được Câu Trả Lời, Vui Lòng Thử Lại Sau.",
                color=0xFF69B4
            )
        
        await loading_message.edit(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=0xFF69B4
        )
        await loading_message.edit(embed=error_embed)

class TreoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True

    @discord.ui.button(label="Treo Ảnh/Video", style=discord.ButtonStyle.primary)
    async def treo_media(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TreoMediaModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Treo Share Contact", style=discord.ButtonStyle.secondary)
    async def treo_contact(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TreoContactModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Treo Normal", style=discord.ButtonStyle.success)
    async def treo_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TreoNormalModal()
        await interaction.response.send_modal(modal)

import discord, datetime


box_cache = {}

class BoxSelect(discord.ui.Select):
    def __init__(self, ids, names, user_id):
        options = []
        for i, (id_, name) in enumerate(zip(ids, names)):
            options.append(discord.SelectOption(
                label=f"{i+1}. {name}",
                description=f"ID: {id_}",
                value=id_
            ))
        super().__init__(placeholder="📌 Chọn 1 Box để lưu tạm", min_values=1, max_values=1, options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        box_cache[self.user_id] = selected_id  # lưu vào bộ nhớ tạm
        embed = discord.Embed(
            title="✅ Đã Lưu Box",
            description=f"Bạn đã chọn Box với ID:\n`{selected_id}` 🧃",
            color=0xFFD700,
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ListBoxModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="🍪 Nhập Cookies Facebook", timeout=None)
        self.cookies = discord.ui.TextInput(
            label="Cookies Facebook",
            placeholder="Nhập Cookies Facebook Của Bạn...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )
        self.add_item(self.cookies)

    async def on_submit(self, interaction: discord.Interaction):
        loading_embed = discord.Embed(
            title="⏰ Đang Xử Lý...",
            description="Bot đang lấy danh sách box, vui lòng chờ...",
            color=0xFFD700
        )
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        
        try:
            fb = facebook(self.cookies.value)   # <-- bạn giữ nguyên hàm fbTools của bạn
            fbt = fbTools(fb.data)
            
            success = fbt.getAllThreadList()
            if success:
                thread_data = fbt.getListThreadID()
                if "threadIDList" in thread_data and "threadNameList" in thread_data:
                    thread_ids = thread_data["threadIDList"]
                    thread_names = thread_data["threadNameList"]
                    
                    if len(thread_ids) > 10:
                        pages = []
                        for i in range(0, len(thread_ids), 10):
                            page_data = []
                            for j in range(i, min(i + 10, len(thread_ids))):
                                page_data.append({
                                    "index": j + 1,
                                    "name": thread_names[j],
                                    "id": thread_ids[j]
                                })
                            if page_data:
                                pages.append(page_data)
                        
                        if pages:
                            view = PaginationView(pages, len(thread_ids), interaction.user.id)
                            initial_embed = view.create_embed()
                            await interaction.followup.send(embed=initial_embed, view=view, ephemeral=False)
                        else:
                            await interaction.followup.send("⚠️ Không có box nào.", ephemeral=True)
                    else:
                        embed = discord.Embed(
                            title="📋 Danh Sách Box Facebook 🧃",
                            color=0x00FF00,
                            timestamp=datetime.datetime.now(datetime.UTC)
                        )
                        description = ""
                        for i in range(len(thread_ids)):
                            description += f"**{i+1}.** {thread_names[i]}\n`{thread_ids[i]}`\n\n"
                        embed.description = description
                        embed.set_footer(text=f"Tổng cộng: {len(thread_ids)} Box")
                        
                        view = discord.ui.View(timeout=None)
                        if thread_ids:
                            view.add_item(BoxSelect(thread_ids, thread_names, interaction.user.id))
                        
                        await interaction.followup.send(embed=embed, view=view, ephemeral=False)
                else:
                    error_embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Không thể lấy list box từ dữ liệu.",
                        color=0xFF0000
                    )
                    await interaction.followup.send(embed=error_embed, ephemeral=True)
            else:
                error_embed = discord.Embed(
                    title="❌ Lỗi Cookies",
                    description="Không thể lấy danh sách nhóm, vui lòng check lại cookies.",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
        except Exception as e:
            error_embed = discord.Embed(
                title="⚠️ Đã Xảy Ra Lỗi",
                description=f"{e}",
                color=0xFF0000
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)


class ListBoxView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ListBoxModal()
        await interaction.response.send_modal(modal)


class PaginationView(discord.ui.View):
    def __init__(self, pages, total_items, user_id):
        super().__init__(timeout=300)
        self.pages = pages or []
        self.current_page = 0
        self.total_items = total_items
        self.user_id = user_id

        if self.pages:
            ids = [item.get("id") for item in self.pages[0] if item]
            names = [item.get("name") for item in self.pages[0] if item]
            if ids and names:
                self.add_item(BoxSelect(ids, names, user_id))

    def create_embed(self):
        embed = discord.Embed(
            title="📋 Danh Sách Box Facebook 🧃",
            color=0x00FF00,
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        if not self.pages or not self.pages[self.current_page]:
            embed.description = "⚠️ Không có dữ liệu box."
            return embed

        current_page_data = self.pages[self.current_page]
        description = ""
        for item in current_page_data:
            if item:
                description += f"**{item['index']}.** {item['name']}\n`{item['id']}`\n\n"

        embed.description = description or "⚠️ Trang trống."
        embed.set_footer(
            text=f"Trang {self.current_page + 1}/{len(self.pages)} • Tổng cộng: {self.total_items} Box"
        )
        return embed

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_page(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_page(interaction)
        else:
            await interaction.response.defer()

    async def update_page(self, interaction: discord.Interaction):
      
        for child in list(self.children):
            if isinstance(child, BoxSelect):
                self.remove_item(child)

    
        current_page_data = self.pages[self.current_page]
        ids = [item.get("id") for item in current_page_data if item]
        names = [item.get("name") for item in current_page_data if item]
        if ids and names:
            self.add_item(BoxSelect(ids, names, self.user_id))

      
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.pages) - 1

        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Đóng", emoji="❌", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✅ Đã Đóng",
            description="Danh sách đã được đóng",
            color=0x808080
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class TreoMediaModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Treo Ảnh/Video", timeout=None)
        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)
        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)
        self.media_url = discord.ui.TextInput(
            label="Nhập Link Tải Ảnh/Video",
            required=True
        )
        self.add_item(self.media_url)
        self.message = discord.ui.TextInput(
            label="Nhập Ngôn",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.message)
        self.delay = discord.ui.TextInput(
            label="Nhập Delay",
            required=True
        )
        self.add_item(self.delay)

    def download_media(self, url, folder_path):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            if "Content-Disposition" in response.headers:
                content_disposition = response.headers["Content-Disposition"]
                filename = re.findall("filename=(.+)", content_disposition)[0].strip('"')
            else:
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    content_type = response.headers.get('Content-Type', '').split('/')[1]
                    if content_type:
                        filename = f"media_{int(time.time())}.{content_type}"
                    else:
                        filename = f"media_{int(time.time())}"
            local_file_path = os.path.join(folder_path, filename)
            with open(local_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return local_file_path
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        try:
            folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            folder_path = f"data/{folder_id}"
            os.makedirs(folder_path)
            with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | treo_media | {interaction.user.id} | {self.media_url.value}")
            with open(f"{folder_path}/messages.txt", "w", encoding="utf-8") as f:
                f.write(self.message.value)
            local_file_path = self.download_media(self.media_url.value, folder_path)
            if not local_file_path:
                embed = discord.Embed(
                    title="❌ Lỗi Khi Tải Ảnh/Video",
                    description="Không Thể Tải File Từ Url Đã Cung Cấp",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_media_func, self.cookies.value, self.idbox.value, local_file_path, self.message.value, self.delay.value, folder_id))
            thread.daemon = True
            thread.start()
            embed = discord.Embed(
                title="✅ Tạo Tasks Thành Công ✅",
                description=f"ID Tasks: {folder_id}\nBạn còn lại **{user_max_tasks - (user_current_tasks + 1)}** lượt tạo task.",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi Tạo Tasks ❌",
                description=f"Lỗi: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class TreoContactModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Treo Share Contact", timeout=None)
        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)
        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)
        self.delay = discord.ui.TextInput(
            label="Nhập Delay",
            required=True
        )
        self.add_item(self.delay)
        self.uid_contact = discord.ui.TextInput(
            label="Nhập UID Contact",
            required=True
        )
        self.add_item(self.uid_contact)
        self.message = discord.ui.TextInput(
            label="Nhập Ngôn",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
           
        try:
            folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            folder_path = f"data/{folder_id}"
            os.makedirs(folder_path)
            with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | treo_contact | {interaction.user.id} | {self.uid_contact.value}")
            with open(f"{folder_path}/messages.txt", "w", encoding="utf-8") as f:
                f.write(self.message.value)
            thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_contact_func, self.cookies.value, self.idbox.value, self.uid_contact.value, self.message.value, self.delay.value, folder_id))
            thread.daemon = True
            thread.start()
            embed = discord.Embed(
                title="✅ Tạo Tasks Thành Công ✅",
                description=f"ID Tasks: {folder_id}",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi Tạo Tasks ❌",
                description=f"Lỗi: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
class NhayPollModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="📊 Nhây Poll Mess", timeout=None)

        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)

        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)

        self.delay = discord.ui.TextInput(
            label="Nhập Delay (giây)",
            required=True
        )
        self.add_item(self.delay)

    
        self.file_name = discord.ui.TextInput(
            label="Tên file (trong xemfile)",
            placeholder="VD: poll.txt (bỏ trống = mặc định nhay.txt)",
            required=False
        )
        self.add_item(self.file_name)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)


        if check_task_limit() >= 200:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                    description="Bot đã chạy tối đa 200/200 tasks. Vui lòng thử lại sau.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        if user_id_str not in config_data.get("task", {}):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không Có Quyền",
                    description="Bạn không có quyền tạo task. Vui lòng liên hệ admin để mua task.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        if user_current_tasks >= user_max_tasks:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                    description=f"Bạn đã tạo tối đa **{user_max_tasks}** task được cho phép.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

       
        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        file_path = None
        if self.file_name.value:
            files = get_user_files(interaction.user.id)
            for path in files:
                if os.path.basename(path) == self.file_name.value.strip():
                    file_path = path
                    break

       
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | nhay_poll | {interaction.user.id} | {file_path or ''}")

       
        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_nhay_poll_func, self.cookies.value, self.idbox.value, self.delay.value, folder_id, file_path)
        )
        thread.daemon = True
        thread.start()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Task Nhây Poll Thành Công ✅",
                description=f"ID Task: `{folder_id}`\nFile dùng: `{os.path.basename(file_path) if file_path else 'nhay.txt (mặc định)'}`",
                color=0x00FF00
            ), ephemeral=True
        )


class NhayPollView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NhayPollModal()
        await interaction.response.send_modal(modal)

class TreoNormalModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Treo Normal", timeout=None)
        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)
        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)
        self.delay = discord.ui.TextInput(
            label="Nhập Delay",
            required=True
        )
        self.add_item(self.delay)
        self.message = discord.ui.TextInput(
            label="Nhập Ngôn",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
           
        try:
            folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            folder_path = f"data/{folder_id}"
            os.makedirs(folder_path)
            with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | treo_normal | {interaction.user.id}")
            with open(f"{folder_path}/message.txt", "w", encoding="utf-8") as f:
                f.write(self.message.value)
            thread = threading.Thread(target=safe_thread_wrapper, args=(start_treo_mess_func, self.cookies.value, self.idbox.value, self.message.value, self.delay.value, folder_id))
            thread.daemon = True
            thread.start()
            embed = discord.Embed(
                title="✅ Tạo Tasks Thành Công ✅",
                description=f"ID Tasks: {folder_id}",
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi Tạo Tasks ❌",
                description=f"Lỗi: {str(e)}",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command()

async def treo(ctx):
    embed = discord.Embed(
        title="Chọn Chức Năng Treo Bên Dưới",
        description="Button Treo Ảnh/Video Là Treo Gửi Ảnh Hoặc Video\nButton Treo Share Contact Là Treo + Share Contact Của UID\nButton Treo Normal Là Button Gửi Tin Nhắn Kiểu Bình Thường",
        color=0xFFC0CB
    )
    view = TreoView()
    await ctx.send(embed=embed, view=view)

class NhayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True
    
    @discord.ui.button(label="Nhây", style=discord.ButtonStyle.primary)
    async def nhay_normal(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NhayModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Nhây Tag", style=discord.ButtonStyle.secondary)
    async def nhay_tag(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NhayTagModal()
        await interaction.response.send_modal(modal)

class NhayModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Nhây Thường", timeout=None)
        self.cookies = discord.ui.TextInput(
            label="Nhập Cookies",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.cookies)

        self.idbox = discord.ui.TextInput(
            label="Nhập ID Box",
            required=True
        )
        self.add_item(self.idbox)

        self.delay = discord.ui.TextInput(
            label="Nhập Delay (giây)",
            required=True
        )
        self.add_item(self.delay)

        
        self.file_name = discord.ui.TextInput(
            label="Tên file (trong xemfile)",
            placeholder="VD: myfile.txt (bỏ trống = mặc định nhay.txt)",
            required=False
        )
        self.add_item(self.file_name)

    async def on_submit(self, interaction: discord.Interaction):
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                    description="Bot đã chạy tối đa 200/200 tasks. Vui lòng thử lại sau.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        if user_id_str not in config_data.get("task", {}):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không Có Quyền",
                    description="Bạn không có quyền tạo task. Vui lòng liên hệ admin để mua task.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return

        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        if user_current_tasks >= user_max_tasks:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                    description=f"Bạn đã tạo tối đa **{user_max_tasks}** task được cho phép.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return


        folder_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        folder_path = f"data/{folder_id}"
        os.makedirs(folder_path)

        file_path = None
        if self.file_name.value:
            files = get_user_files(interaction.user.id)
            for path in files:
                if os.path.basename(path) == self.file_name.value.strip():
                    file_path = path
                    break

    
        with open(f"{folder_path}/luutru.txt", "w", encoding="utf-8") as f:
            f.write(f"{self.cookies.value} | {self.idbox.value} | {self.delay.value} | nhay_normal | {interaction.user.id} | {file_path or ''}")


        thread = threading.Thread(
            target=safe_thread_wrapper,
            args=(start_nhay_func, self.cookies.value, self.idbox.value, self.delay.value, folder_id, file_path)
        )
        thread.daemon = True
        thread.start()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Tạo Task Thành Công ✅",
                description=f"ID Task: `{folder_id}`\nFile dùng: `{os.path.basename(file_path) if file_path else 'nhay.txt (mặc định)'}`",
                color=0x00FF00
            ), ephemeral=True
        )


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True

    
@bot.command()

async def nhay(ctx):
    embed = discord.Embed(
        title="Bạn Muốn Sử Dụng Phương Thức Nhây Nào?",
        description="Button Nhây Sẽ Là Nhây Thường - Fake Typing\nButton Nhây Tag Sẽ Là Nhây Có Tag - Fake Typing",
        color=0x0099FF
    )
    view = NhayView()
    await ctx.send(embed=embed, view=view)


class DiscordView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        config_data = load_config()
        user_id_str = str(interaction.user.id)

        if check_task_limit() >= 200:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Toàn Bot",
                description="Bot Đã Chạy Tối Đa 200/200 Tasks Vui Lòng Thử Lại Sau..",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

        if user_id_str not in config_data.get("task", {}):
            embed = discord.Embed(
                title="❌ Không Có Quyền",
                description="Bạn Không Có Quyền Tạo Task, Vui Lòng Liên Hệ Admin Để Mua Task.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
            
        user_current_tasks = get_user_task_count(user_id_str)
        user_max_tasks = int(config_data["task"].get(user_id_str, 0))
        
        if user_current_tasks >= user_max_tasks:
            embed = discord.Embed(
                title="❌ Đã Đạt Giới Hạn Task Cá Nhân",
                description=f"Bạn Đã Tạo Tối Đa **{user_max_tasks}** Task Được Cho Phép.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        
        return True

class DiscordView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Treo", style=discord.ButtonStyle.primary)
    async def treo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TreoDiscordModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Nhây", style=discord.ButtonStyle.secondary)
    async def nhay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NhayDiscordModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Nhây Tag", style=discord.ButtonStyle.success)
    async def nhay_tag_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = NhayTagDiscordModal()
        await interaction.response.send_modal(modal)

@bot.command()
async def dis(ctx):
    embed = discord.Embed(
        title="📌 Bảng Chức Năng Discord",
        description=(
            "🔹 **Button Treo** - Treo Discord spam nội dung\n"
            "🔹 **Button Nhây** - Nhây Discord có Fake Typing\n"
            "🔹 **Button Nhây Tag** - Nhây Tag Discord có Fake Typing"
        ),
        color=0xFFFFFF
    )
    view = DiscordView()
    await ctx.send(embed=embed, view=view)

@bot.command()
async def getkey(ctx):
    user_id = str(ctx.author.id)

    try:
        data = load_user_data()
        global user_keys, user_nhapkey_count
        user_keys = data.get("user_keys", {})
        user_nhapkey_count = data.get("user_nhapkey_count", {})

        random_key = generate_random_key()

        user_keys[user_id] = {
            "key": random_key,
            "created_at": datetime.datetime.now().isoformat()
        }

        save_user_data()

        base_url = f"https://key-pied.vercel.app/?ma={random_key}"
        api_url = f"https://link4m.co/st?api=68b3c109702ba873dd52770c&url={base_url}"

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://link4m.co/'
        }

        session = requests.Session()
        response = session.get(api_url, headers=headers, allow_redirects=True, timeout=15)

        shortened_link = response.url if response.status_code in [200, 403] else base_url
        current_count = user_nhapkey_count.get(user_id, 0)
        next_task_count = 2 if current_count == 0 else 1

        embed = discord.Embed(
            title="🔑・Vượt Link Để Get Key",
            description=(
                f"✨ **Vượt link để nhận key**\n"
                f"🔹 Lần đầu trong ngày nhận **2 task**\n"
                f"🔹 Những lần sau nhận **1 task**\n"
            ),
            color=discord.Color.from_rgb(0, 255, 255),
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="📋 Thông Tin",
            value=(
                f"👤 Người yêu cầu: {ctx.author.mention}\n"
                f"✅ Lần nhập key thành công: **{current_count}**\n"
                f"🎯 Task sẽ nhận: **{next_task_count}**"
            ),
            inline=False
        )

        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        embed.set_image(url="https://i.pinimg.com/originals/58/59/12/585912636b8c859239bb3e31c41a997b.gif")

        embed.set_footer(text=f"Yêu cầu bởi {ctx.author} • {datetime.datetime.now().strftime('%H:%M:%S')}")

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="🔗 Truy cập link", url=shortened_link))

        await ctx.send(embed=embed, view=view)

    except Exception as e:
        await ctx.send(f"❌ Lỗi: {str(e)}")

loading_gifs = [
    "https://i.pinimg.com/originals/58/59/12/585912636b8c859239bb3e31c41a997b.gif",
    "https://i.pinimg.com/originals/7d/ce/98/7dce98ac902442a7f17f0a270148bc13.gif",
    "https://i.pinimg.com/originals/43/2a/6b/432a6b5b897e80bafad45da51a05f7e1.gif"
]

success_icons = ["✅", "🎉", "💎", "🚀", "🔥", "🌟"]

class NhapKeyModal(discord.ui.Modal, title="🔑 Nhập Key Của Bạn"):
    key_input = discord.ui.TextInput(
        label="Nhập key",
        placeholder="Dán key vào đây...",
        style=discord.TextStyle.short,
        required=True
    )

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    async def on_submit(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        key = str(self.key_input.value).strip()

        data = load_user_data()
        global user_keys, user_nhapkey_count
        user_keys = data.get("user_keys", {})
        user_nhapkey_count = data.get("user_nhapkey_count", {})

        if user_id not in user_keys or user_keys[user_id]["key"] != key:
            error_embed = discord.Embed(
                title="❌ Key Không Đúng",
                description="Key bạn nhập không đúng hoặc đã hết hạn!",
                color=0xFF0000,
                timestamp=datetime.datetime.now()
            )
            error_embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        if user_id not in user_nhapkey_count:
            user_nhapkey_count[user_id] = 0

        user_nhapkey_count[user_id] += 1
        task_count = 2 if user_nhapkey_count[user_id] == 1 else 1

        config = load_config()
        if 'task' not in config:
            config['task'] = {}
        if 'task_used' not in config:
            config['task_used'] = {}

        current_task = config['task'].get(user_id, 0)
        new_task_count = current_task + task_count
        config['task'][user_id] = new_task_count

        used_task = config['task_used'].get(user_id, 0)
        config['task_used'][user_id] = used_task + task_count

        save_config(config)

        del user_keys[user_id]
        save_user_data()

        icon = random.choice(success_icons)
        gif = random.choice(loading_gifs)

        success_embed = discord.Embed(
            title=f"{icon} Nhập Key Thành Công",
            description=f"Bạn đã nhận được **{task_count}** task!\n\n📊 Task hiện tại: **{new_task_count}**",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        success_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        success_embed.set_image(url=gif)
        success_embed.set_footer(text=f"Yêu cầu bởi {interaction.user} • {datetime.datetime.now().strftime('%H:%M:%S')}")

        await interaction.response.send_message(embed=success_embed, ephemeral=True)


class NhapKeyView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx

    @discord.ui.button(label="🔑 Nhập Key", style=discord.ButtonStyle.green)
    async def nhapkey_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Bạn không phải là người gọi lệnh này!", ephemeral=True)
            return

        modal = NhapKeyModal(self.ctx)
        await interaction.response.send_modal(modal)


@bot.command()
async def nhapkey(ctx):
    embed = discord.Embed(
        title="🔑・Nhập Key Để Nhận Task",
        description="Ấn vào **nút bên dưới** để mở popup nhập key.",
        color=discord.Color.from_rgb(0, 255, 255),
        timestamp=datetime.datetime.now()
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_image(url=random.choice(loading_gifs))
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author} • {datetime.datetime.now().strftime('%H:%M:%S')}")

    view = NhapKeyView(ctx)
    await ctx.send(embed=embed, view=view)

stop_flags = globals().get("stop_flags", {})
active_threads = globals().get("active_threads", {})
active_senders = globals().get("active_senders", {})

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

SUCCESS_GIFS = [
    "https://i.pinimg.com/originals/30/ba/d4/30bad4893f61e348b8661bd5f901c78b.gif",
    "https://i.pinimg.com/originals/60/73/f9/6073f994a2a6dcc5269724714abf1aeb.gif",
    "https://i.pinimg.com/originals/e8/79/9a/e8799a94439d4e402357f9ffe1178465.gif",
    "https://i.pinimg.com/originals/0a/29/ef/0a29ef086e06897be8270ae2c18c7f33.gif",
    "https://i.pinimg.com/originals/56/12/c8/5612c809271e6cc52e13b66df67b1b9a.gif"
]
FAIL_GIFS = [
    "https://i.pinimg.com/originals/6b/a7/4e/6ba74e4e0959b2bdd008df8a51462d34.gif",
    "https://i.pinimg.com/originals/a1/4f/58/a14f58a592bfdb9e5e6f73012ef22bb7.gif"
]


def register_thread(folder_id: str, thread: threading.Thread):
    if not folder_id or not thread: return
    stop_flags[folder_id] = False
    active_threads[folder_id] = thread

def unregister_thread(folder_id: str):
    stop_flags.pop(folder_id, None)
    active_threads.pop(folder_id, None)

def is_stop_requested(folder_id: str) -> bool:
    return stop_flags.get(folder_id, False)

def stop_task_folder(folder_id: str, force: bool = False, wait_seconds: int = 8):
    folder_path = os.path.join("data", folder_id)
    stop_flags[folder_id] = True
    try:
        sender = active_senders.get(folder_id)
        if sender:
            try: sender.stop()
            except: pass
            try: del active_senders[folder_id]
            except: pass
    except: pass
    thread = active_threads.get(folder_id)
    if thread and getattr(thread, "is_alive", lambda: False)() and not force:
        waited = 0.0
        while thread.is_alive() and waited < wait_seconds:
            time.sleep(0.25); waited += 0.25
    if os.path.exists(folder_path):
        tries, last_exc = 0, None
        while tries < 6:
            try:
                shutil.rmtree(folder_path)
                unregister_thread(folder_id)
                return True, f"Đã dừng và xoá task `{folder_id}`"
            except Exception as e:
                last_exc = e; tries += 1; time.sleep(0.3)
        return False, f"Không thể xoá thư mục `{folder_id}`: {last_exc}"
    else:
        unregister_thread(folder_id)
        return True, f"Task `{folder_id}` không tồn tại (có thể đã dừng trước đó)."


def _read_task_meta(folder):
    folder_path = os.path.join("data", folder)
    luutru = os.path.join(folder_path, "luutru.txt")
    if not os.path.exists(luutru): 
        return {"owner": "Unknown", "method": "unknown"}
    try:
        with open(luutru, "r", encoding="utf-8") as f:
            parts = f.read().strip().split(" | ")
        method = parts[3] if len(parts) >= 4 else "unknown"
        owner = parts[4] if len(parts) >= 5 else "Unknown"
        return {"owner": str(owner), "method": method}
    except:
        return {"owner": "Unknown", "method": "unknown"}

def update_task_used(owner_id: str):
    if str(owner_id) == str(config.get("ownerVIP")): return
    used = config.get("task_used", {})
    if owner_id in used:
        used[owner_id] = max(0, used[owner_id] - 1)
        if used[owner_id] == 0: used.pop(owner_id)
    config["task_used"] = used
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

class TaskSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="📂 → Chọn task để xoá (multi)", 
                         min_values=1, max_values=min(len(options), 25), 
                         options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

class DeleteTasksView(discord.ui.View):
    def __init__(self, author: discord.User, is_owner: bool, is_admin: bool, timeout: int = 90):
        super().__init__(timeout=timeout)
        self.author, self.is_owner, self.is_admin = author, is_owner, is_admin
        self.select_obj = None
        options = []
        if os.path.exists("data"):
            for folder in sorted(os.listdir("data")):
                folder_path = os.path.join("data", folder)
                if not os.path.isdir(folder_path) or not os.path.exists(os.path.join(folder_path,"luutru.txt")): 
                    continue
                meta = _read_task_meta(folder)
                if not (self.is_owner or self.is_admin) and str(meta["owner"]) != str(author.id):
                    continue
                created_ts = int(os.path.getctime(folder_path))
                created = datetime.datetime.fromtimestamp(created_ts).strftime("%d-%m-%Y %H:%M")
                label = f"{folder} • {meta['method']}"
                desc = f"👤 {meta['owner']} • 🕒 {created}"
                options.append(discord.SelectOption(label=label[:100], description=desc[:100], value=folder, emoji="🗂️"))
        if not options:
            sel = TaskSelect([discord.SelectOption(label="❌ Không có task khả dụng", value="__none__")])
            sel.disabled = True; self.add_item(sel)
        else:
            self.select_obj = TaskSelect(options); self.add_item(self.select_obj)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Bạn không có quyền.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Xoá task đã chọn", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        values = getattr(self.select_obj, "values", [])
        if not values or values == ["__none__"]:
            return await interaction.response.send_message("⚠️ Chưa chọn task nào.", ephemeral=True)
        deleted, errors = [], []
        for fid in values:
            ok, msg = stop_task_folder(fid, force=True)
            if ok: deleted.append(fid); update_task_used(_read_task_meta(fid).get("owner"))
            else: errors.append(msg)
        desc = ""
        if deleted: desc += "🟢 Đã xoá:\n" + "\n".join(f"`{d}`" for d in deleted)
        if errors: desc += "\n🔴 Lỗi:\n" + "\n".join(errors)
        embed = discord.Embed(title="📜 Kết quả xoá task", description=desc or "Không có thay đổi.",
                              color=0x00FF00 if deleted else 0xFF0000)
        embed.set_author(name=f"{self.author}", icon_url=self.author.display_avatar.url)
        embed.set_footer(text=f"⏳ Yêu cầu lúc {datetime.datetime.now().strftime('%H:%M:%S')}")
        if deleted: embed.set_image(url=random.choice(SUCCESS_GIFS))
        elif errors: embed.set_image(url=random.choice(FAIL_GIFS))
        await interaction.response.send_message(embed=embed, ephemeral=True)
        for item in self.children: item.disabled = True
        try: await interaction.message.edit(view=self)
        except: pass
        self.stop()

    @discord.ui.button(label="Huỷ", style=discord.ButtonStyle.secondary, emoji="🚫")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Đã huỷ.", ephemeral=True); self.stop()



@bot.command()
async def stoptask(ctx, task_id: str = None):
    user_id, owner_id = str(ctx.author.id), str(config.get("ownerVIP"))
    is_owner = user_id == owner_id
    is_admin = ctx.author.guild_permissions.administrator

    if not task_id:
        view = DeleteTasksView(ctx.author, is_owner, is_admin)
        embed = discord.Embed(title="🗂️  Quản lý Task", 
                              description="Chọn task từ bên dưới, sau đó bấm 🗑️ **Xoá**.",
                              color=discord.Colour.gold())
        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"📌 Người yêu cầu • {datetime.datetime.now().strftime('%H:%M:%S')}")
        await ctx.send(embed=embed, view=view); return

    if task_id.lower() == "all":
        folders = [f for f in os.listdir("data")
                   if (is_owner or is_admin or _read_task_meta(f)["owner"] == user_id)]
        if not folders: 
            return await ctx.send(embed=discord.Embed(title="❌ Không có task để xoá", color=0xFF0000))
        for fid in folders: stop_task_folder(fid, force=True); update_task_used(_read_task_meta(fid).get("owner"))
        embed = discord.Embed(title="✅ Đã xoá toàn bộ task", color=0x00FF00)
        embed.set_image(url=random.choice(SUCCESS_GIFS))
        return await ctx.send(embed=embed)

    if task_id.lower() == "random":
        if not (is_owner or is_admin):
            return await ctx.send(embed=discord.Embed(title="❌ Chỉ Owner/Admin được random xoá", color=0xFF0000))
        all_folders = [f for f in os.listdir("data")]
        if not all_folders: 
            return await ctx.send(embed=discord.Embed(title="❌ Không có task để xoá", color=0xFF0000))
        num, pick = min(int(random.uniform(3, 8)), len(all_folders)), random.sample(all_folders, num)
        for fid in pick: stop_task_folder(fid, force=True); update_task_used(_read_task_meta(fid).get("owner"))
        desc = "\n".join([f"• `{fid}`" for fid in pick])
        embed = discord.Embed(title="🎲 Random xoá task", description=desc, color=discord.Colour.magenta())
        embed.set_image(url=random.choice(SUCCESS_GIFS))
        return await ctx.send(embed=embed)

    folder_path = os.path.join("data", task_id)
    if not os.path.exists(folder_path):
        return await ctx.send(embed=discord.Embed(title="❌ Task không tồn tại", color=0xFF0000))
    meta = _read_task_meta(task_id)
    if not (is_owner or is_admin) and str(meta.get("owner")) != user_id:
        return await ctx.send(embed=discord.Embed(title="❌ Bạn không có quyền xoá task này", color=0xFF0000))
    ok, msg = stop_task_folder(task_id, force=True)
    if ok: 
        update_task_used(str(meta.get("owner")))
        embed = discord.Embed(title="✅ Thành công", description=msg, color=0x00FF00)
        embed.set_image(url=random.choice(SUCCESS_GIFS))
        return await ctx.send(embed=embed)
    else: 
        embed = discord.Embed(title="❌ Thất bại", description=msg, color=0xFF0000)
        embed.set_image(url=random.choice(FAIL_GIFS))
        return await ctx.send(embed=embed)

@bot.command()

async def listbox(ctx):
    embed = discord.Embed(
        title="📋 Lấy Danh Sách Box Facebook",
        description="Ấn Vào Nút **Start** Để Nhập Cookies",
        color=0xFF69B4,
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    embed.add_field(
        name="📌 Hướng Dẫn",
        value="• Nhập Cookies Facebook\n• Bot Sẽ Tự Động Lấy Tất Cả Box Có Trong Cookies\n• Kết Quả Sẽ Được Hiển Thị Theo Trang",
        inline=False
    )
    embed.set_footer(text=" 𝐃𝐚𝐧𝐧𝐲 𝐏𝐡𝐚𝐧𝐭𝐨𝐦 🧃 ", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    
    view = ListBoxView()
    await ctx.send(embed=embed, view=view)


@bot.command()

async def nhaynamebox(ctx):
    embed = discord.Embed(
        title="Nhây Name Box",
        description="Ấn Vào Button Start Để Bắt Đầu Đổi Tên Box Theo File nhay.txt",
        color=0xFF69B4
    )
    view = NhayNameBoxView()
    await ctx.send(embed=embed, view=view)

@bot.command()

async def nhaypoll(ctx):
    embed = discord.Embed(
        title="Click Vào Nút Bắt Đầu Để Nhập Thông Tin",
        color=0xFFFFFF
    )
    view = NhayPollView()
    await ctx.send(embed=embed, view=view)

import asyncio
import discord

def error_embed(ctx, title: str, description: str):
    """Tạo embed lỗi VIP"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.red(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_author(
        name=f"Yêu cầu bởi {ctx.author} ({ctx.author.id})",
        icon_url=ctx.author.display_avatar.url
    )
    embed.set_footer(text=f"🚨 Format Sai • {datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}")
    return embed


# ====== ADD TASK ======
@bot.command()
@check_ownervip()
async def addtask(ctx, user: discord.User = None, quantity: int = None):
    try:
        if user is None or quantity is None:
            embed = error_embed(
                ctx,
                "❌ Sai Format",
                "Vui lòng dùng đúng format:\n```!addtask @user <số_lượng>```"
            )
            return await ctx.send(embed=embed)

        if quantity <= 0:
            embed = error_embed(
                ctx,
                "⚠️ Số Lượng Không Hợp Lệ",
                "Số lượng task phải **lớn hơn 0**."
            )
            return await ctx.send(embed=embed)

        # === fallback cho user đặc biệt ===
        if user is None:
            user = await bot.fetch_user(1402942118795939850)

        config = load_config()
        if "task" not in config:
            config["task"] = {}
        if "admin_added_users" not in config:
            config["admin_added_users"] = {}

        user_id_str = str(user.id)
        old_quantity = config["task"].get(user_id_str, 0)
        new_quantity = old_quantity + quantity

        config["task"][user_id_str] = new_quantity
        config["admin_added_users"][user_id_str] = True
        save_config(config)

        loading = await ctx.send(embed=discord.Embed(
            description=f"⏳ Đang xử lý cấp **{quantity}** task cho {user.mention}...",
            color=discord.Color.orange()
        ))
        await asyncio.sleep(2)

        if new_quantity <= 5:
            color = discord.Color.gold()
        elif new_quantity <= 20:
            color = discord.Color.blue()
        else:
            color = discord.Color.green()

        embed = discord.Embed(
            title="🧃 𝐓𝐀𝐒𝐊 𝐆𝐑𝐀𝐍𝐓𝐄𝐃 🧃",
            description=f"✅ {user.mention} vừa được cấp **{quantity}** Task!",
            color=color,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=f"Admin: {ctx.author} ({ctx.author.id})", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="📊 Chi Tiết",
            value=(
                f"🔹 **Task Được Cấp Thêm:** `{quantity}`\n"
                f"🔹 **Tổng Hiện Tại:** `{new_quantity}`\n"
                f"🔹 **Loại:** `Admin Added`\n"
                f"🔹 **Reset Hàng Ngày:** ❌"
            ),
            inline=False
        )
        embed.set_footer(text=f"🚀 Powered by Danny Phantom 🧃 • {datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}")

        await loading.delete()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🧃")

        print(f"[LOG][ADD] {ctx.author} ({ctx.author.id}) đã cấp {quantity} task cho {user} ({user.id}). Tổng hiện tại: {new_quantity}")

    except Exception as e:
        embed = error_embed(ctx, "❌ Lỗi Hệ Thống", f"`{e}`")
        await ctx.send(embed=embed)
        print(f"[ERROR][ADD] {e}")

@bot.command()
@check_ownervip()
async def listuser(ctx):
    config = load_config()

    if "task" not in config or not config["task"]:
        embed = discord.Embed(
            title="📋 Danh Sách Task",
            description="❌ Hiện tại **chưa có user nào** được cấp task.",
            color=discord.Color.red()
        )
        embed.set_footer(text="🚀 Powered by Danny Phantom 🧃")
        await ctx.send(embed=embed)
        return

    users_data = []
    for user_id, total_task in config["task"].items():
        task_used = config.get("task_used", {}).get(user_id, 0)
        admin_added = "✅" if config.get("admin_added_users", {}).get(user_id, False) else "❌"

        # Lấy thông tin user
        member = ctx.guild.get_member(int(user_id))
        if member:
            user_display = f"{member.mention} | {member} (`{user_id}`)"
        else:
            try:
                user = await bot.fetch_user(int(user_id))
                user_display = f"{user.mention} | {user} (`{user_id}`)"
            except:
                user_display = f"<@{user_id}> (`{user_id}`)"

        details = (
            f"🔹 **Task còn lại:** `{total_task}`\n"
            f"🔹 **Task đã dùng:** `{task_used}`\n"
            f"🔹 **Admin cấp:** {admin_added}"
        )
        users_data.append((user_display, details))

    # Pagination
    per_page = 10
    pages = [users_data[i:i+per_page] for i in range(0, len(users_data), per_page)]
    current_page = 0

    def create_embed(page):
        embed = discord.Embed(
            title="📋 Danh Sách User Có Task",
            description=f"Trang {page+1}/{len(pages)}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text="🚀 Powered by Danny Phantom 🧃")

        for name, details in pages[page]:
            embed.add_field(name=name, value=details, inline=False)
        return embed

    message = await ctx.send(embed=create_embed(current_page))
    if len(pages) <= 1:
        return

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            await message.remove_reaction(reaction.emoji, user)

            if str(reaction.emoji) == "▶️" and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(embed=create_embed(current_page))
            elif str(reaction.emoji) == "◀️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=create_embed(current_page))

        except asyncio.TimeoutError:
            break

# ====== REMOVE TASK ======
@bot.command()
@check_ownervip()
async def removetask(ctx, user: discord.User = None):
    try:
        if user is None:
            embed = error_embed(
                ctx,
                "❌ Sai Format",
                "Vui lòng dùng đúng format:\n```!removetask @user```"
            )
            return await ctx.send(embed=embed)

        config = load_config()
        user_id_str = str(user.id)

        loading = await ctx.send(embed=discord.Embed(
            description=f"⏳ Đang xử lý gỡ task của {user.mention}...",
            color=discord.Color.orange()
        ))
        await asyncio.sleep(2)

        if "task" in config and user_id_str in config["task"]:
            del config["task"][user_id_str]
            save_config(config)

            embed = discord.Embed(
                title="🗑️ 𝐑𝐄𝐌𝐎𝐕𝐄 𝐓𝐀𝐒𝐊 🗑️",
                description=f"✅ Đã xóa toàn bộ quyền tạo task của {user.mention}.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_author(name=f"Admin: {ctx.author} ({ctx.author.id})", icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"🚀 Powered by Danny Phantom 🧃 • {datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}")

            await loading.delete()
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("🧃")

            print(f"[LOG][REMOVE] {ctx.author} ({ctx.author.id}) đã xóa task của {user} ({user.id})")

        else:
            embed = error_embed(
                ctx,
                "❌ Người Dùng Không Có Task",
                f"{user.mention} không có trong danh sách được cấp task."
            )
            await loading.delete()
            await ctx.send(embed=embed)

            print(f"[LOG][REMOVE] {ctx.author} ({ctx.author.id}) cố xóa task nhưng {user} ({user.id}) không có task.")

    except Exception as e:
        embed = error_embed(ctx, "❌ Lỗi Hệ Thống", f"`{e}`")
        await ctx.send(embed=embed)
        print(f"[ERROR][REMOVE] {e}")
import discord
from discord.ext import commands
import random

GIF_LIST = [
    "https://i.pinimg.com/originals/7d/ce/98/7dce98ac902442a7f17f0a270148bc13.gif",
    "https://i.pinimg.com/originals/5d/2c/44/5d2c44694918947aede42306cb7154d0.gif",
    "https://i.pinimg.com/originals/35/d1/98/35d19823ff425d809e619558cc3e0e90.gif",
    "https://i.pinimg.com/originals/84/4f/7e/844f7e76c6e1eeb8266be6b17362b385.gif",
]

COLOR_LIST = [
    discord.Color.from_rgb(255, 99, 132),
    discord.Color.from_rgb(54, 162, 235),
    discord.Color.from_rgb(255, 206, 86),
    discord.Color.from_rgb(75, 192, 192),
    discord.Color.from_rgb(153, 102, 255),
]

def get_page_color(index: int):
    return COLOR_LIST[index % len(COLOR_LIST)]


PAGES = [
    ("🎉", "Lời cảm ơn", "Menu chính của bot"),
    ("📜", "Task", """
🤍 **addtask** — Add Task Cho Người Xài
🤍 **removetask** — Xoá Task Người Dùng
"""),
    ("🔑", "Key", """
🔑 **getkey** — Lấy Key để có Task
🔐 **nhapkey** — Nhập Key để nhận Task
"""),
    ("💎", "Messenger", """
💤 **treo** — Treo Messenger Bất Tử
🎭 **nhay** — Nhây Vip Fake Soạn
📜 **treoso** — Treo Sớ Bá Đạo
🔁 **nhaypoll** — Nhây Poll Vip
👤 **listbox** — Lấy ID Box
🤖 **meta** — Hỏi Meta
💀 **nhaynamebox** — Nhây Name Box
"""),
    ("📂", "File", """
📁 **setfile** — Set file dùng cho các chức năng
📁 **xemfile** — Xem file đã set
"""),
    ("🎭", "Discord", """
📲 **dis** — All Chức Năng Discord
"""),
    ("⛔", "Stop Task", """
⛔ **stoptask** — Stop Task Theo ID
"""),
]


class MenuDropdown(discord.ui.Select):
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(label=title, emoji=emoji) 
            for emoji, title, _ in PAGES
        ]
        super().__init__(placeholder="📌 Chọn khu vực Menu...", options=options, min_values=1, max_values=1)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        _, title, _ = [(e, t, d) for e, t, d in PAGES if t == self.values[0]][0]
        self.parent_view.current_index = [i for i, (_, t, _) in enumerate(PAGES) if t == title][0]
        embed = self.parent_view.make_embed(interaction.user)
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class MenuView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=120)
        self.author = author
        self.current_index = 0
        self.message = None
        self.add_item(MenuDropdown(self))

    def make_embed(self, user):
        emoji, title, desc = PAGES[self.current_index]

        if self.current_index == 0:
            desc = f"""
👋 Xin chào {user.mention}, tôi là **! 𝐃𝐚𝐧𝐧𝐲 𝐏𝐡𝐚𝐧𝐭𝐨𝐦 🧃**

🗿 Đây là **menu chính của bot**, bạn có thể:
- Dùng **dropdown** để chọn tab nhanh
- Hoặc bấm **⏮️ ⏭️** để chuyển trang
- Menu sẽ **tự xoá sau 120s**

❤️ Cảm ơn {user.mention} đã tin tưởng & sử dụng bot!
"""

        embed = discord.Embed(
            title=f"{emoji} {title} | 🧃 Power By Minato",
            description=desc,
            color=get_page_color(self.current_index)
        )

        if self.current_index == 0:
            embed.set_image(url=random.choice(GIF_LIST))
        else:
            embed.set_thumbnail(url=random.choice(GIF_LIST))

        embed.set_footer(text=f"Trang {self.current_index+1}/{len(PAGES)} • 𝙋𝙤𝙬𝙚𝙧 𝘽𝙮 Minato🧃")
        embed.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else None)
        return embed

    @discord.ui.button(label="⏮️ Trước", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("⛔ Không thể điều khiển menu của người khác!", ephemeral=True)
        self.current_index = (self.current_index - 1) % len(PAGES)
        embed = self.make_embed(interaction.user)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏭️ Sau", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("⛔ Không thể điều khiển menu của người khác!", ephemeral=True)
        self.current_index = (self.current_index + 1) % len(PAGES)
        embed = self.make_embed(interaction.user)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.secondary)
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_index = 0
        embed = self.make_embed(interaction.user)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="📖 Show All", style=discord.ButtonStyle.success)
    async def show_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📖 Danh sách toàn bộ lệnh",
            color=discord.Color.gold()
        )
        for emoji, title, desc in PAGES[1:]:
            embed.add_field(name=f"{emoji} {title}", value=desc, inline=False)
        embed.set_footer(text=f"Yêu cầu bởi {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except:
                pass


@bot.command()
async def menu(ctx):
    view = MenuView(ctx.author)
    embed = view.make_embed(ctx.author)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg
@bot.command()
async def treoso(ctx):
    embed = discord.Embed(
        title="Ấn Vào Button Start Để Bắt Đầu Nhập Thông Tin Cần Thiết 📘",
        color=0x0099FF
    )
    view = TreoSoView()
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_disconnect():
    pass

@bot.event
async def on_resumed():
    pass



async def main():
    while True:
        try:
            await bot.start(config['tokenbot'], reconnect=True)
        except discord.HTTPException as e:
            if e.status == 429:
                await asyncio.sleep(60)
            else:
                print(f"HTTP Exception: {e}")
                await asyncio.sleep(5)
        except discord.ConnectionClosed:
            print("Connection closed. Reconnecting...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import sys
        sys.exit(1)
                        
