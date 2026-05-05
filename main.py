import asyncio
import json
import os
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import ChatPermissions, Message, User

DATA_FILE = Path("data/users.json")
START_BALANCE = 500
DAILY_BONUS = 250
CASINO_MIN_BET = 10
BOT_NAME = os.environ.get("BOT_NAME", "Eternal")
ROULETTE_COLORS = {"red": "рџ”ґ", "black": "вљ«", "green": "рџџў"}
ADMIN_IDS = {8439166906}
PETER_ONLY_MODE = True
# You can place token directly here.
BOT_TOKEN = "8798997241:AAHa1gXM3B4nW-Z8PUItCEvA8FAsN-ejD5c"
RPS_CHOICES = {"РєР°РјРµРЅСЊ": "rock", "РЅРѕР¶РЅРёС†С‹": "scissors", "Р±СѓРјР°РіР°": "paper", "rock": "rock", "scissors": "scissors", "paper": "paper"}
QUIZ_QUESTIONS = [
    {"q": "РЎРєРѕР»СЊРєРѕ РґРЅРµР№ РІ РІРёСЃРѕРєРѕСЃРЅРѕРј РіРѕРґСѓ?", "a": "366"},
    {"q": "РЎС‚РѕР»РёС†Р° РЇРїРѕРЅРёРё?", "a": "С‚РѕРєРёРѕ"},
    {"q": "2 РІ СЃС‚РµРїРµРЅРё 5 = ?", "a": "32"},
]
MAGIC_ANSWERS = [
    "Р”Р°.",
    "РќРµС‚.",
    "РЎРєРѕСЂРµРµ РІСЃРµРіРѕ РґР°.",
    "РЎРїСЂРѕСЃРё РїРѕР·Р¶Рµ.",
    "РЁР°РЅСЃС‹ С…РѕСЂРѕС€РёРµ.",
    "Р›СѓС‡С€Рµ РЅРµ РЅР°РґРѕ.",
]
PETER_GRIFFIN_IMAGES = [
    "https://media.tenor.com/4P0GZ8Kf4fUAAAAC/peter-griffin-family-guy.gif",
    "https://media.tenor.com/BrYkG8A4oZ0AAAAC/peter-griffin.gif",
    "https://media.tenor.com/8x4VQzQ2R4YAAAAC/family-guy-peter.gif",
    "https://media.tenor.com/CxWHSGSA4mAAAAAC/peter-griffin-dance.gif",
    "https://media.tenor.com/6t2kW4d9vQ0AAAAC/peter-griffin-laugh.gif",
    "https://media.tenor.com/0e6n7mQ6gF8AAAAC/peter-griffin-wow.gif",
    "https://media.tenor.com/vYxw2Fd7sXgAAAAC/peter-griffin-family-guy-dance.gif",
    "https://media.tenor.com/3Q6N8h8h5YwAAAAC/peter-griffin-walk.gif",
    "https://media.tenor.com/h7D7vK8D5jEAAAAC/peter-griffin-funny.gif",
    "https://media.tenor.com/1A8w3r5S6m8AAAAC/peter-griffin-ok.gif",
    "https://media.tenor.com/9GkR4uP7b8cAAAAC/peter-griffin-no.gif",
    "https://media.tenor.com/aQ8P6xR2n5QAAAAC/peter-griffin-yes.gif",
    "https://media.tenor.com/m2sL7cX9w2wAAAAC/family-guy-peter-griffin.gif",
    "https://media.tenor.com/5dV3bK7rP1kAAAAC/peter-griffin-shocked.gif",
    "https://media.tenor.com/x8B1fF9qT6gAAAAC/peter-griffin-clap.gif",
    "https://media.tenor.com/p7R2kJ4nW1wAAAAC/peter-griffin-dancing.gif",
    "https://media.tenor.com/t3Y8nM6vQ4QAAAAC/peter-griffin-family-guy.gif",
    "https://media.tenor.com/r6F2jN8kP3wAAAAC/peter-griffin-meme.gif",
    "https://media.tenor.com/z2D6fH7mS5QAAAAC/peter-griffin-reaction.gif",
    "https://media.tenor.com/q9L3vJ5nR2gAAAAC/peter-griffin-hi.gif",
]
UNI_CARD_POOL = [
    {
        "name": "РћР±С‹С‡РЅР°СЏ РєР°СЂС‚Р° РџРёС‚РµСЂР°",
        "rarity": "common",
        "chance": 0.60,
        "multiplier": 1.3,
    },
    {
        "name": "Р РµРґРєР°СЏ РєР°СЂС‚Р° РџРёС‚РµСЂР°",
        "rarity": "rare",
        "chance": 0.28,
        "multiplier": 2.2,
    },
    {
        "name": "Р­РїРёС‡РµСЃРєР°СЏ РєР°СЂС‚Р° РџРёС‚РµСЂР°",
        "rarity": "epic",
        "chance": 0.10,
        "multiplier": 4.0,
    },
    {
        "name": "Р›Р•Р“Р•РќР”РђР РќРђРЇ РєР°СЂС‚Р° РџРРўР•Р Рђ",
        "rarity": "legendary",
        "chance": 0.02,
        "multiplier": 9.0,
    },
]
DEFAULT_USER = {
    "balance": START_BALANCE,
    "last_daily": None,
    "xp": 0,
    "level": 1,
    "games_played": 0,
    "username": None,
    "display_name": None,
    "tg_id": None,
}


@dataclass
class CasinoResult:
    symbols: list[str]
    multiplier: float
    title: str


class Storage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self) -> Dict[str, dict]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, dict]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _ensure_user_defaults(self, user: dict) -> bool:
        changed = False
        for field, default_value in DEFAULT_USER.items():
            if field not in user:
                user[field] = default_value
                changed = True
        return changed

    def get_or_create_by_telegram(self, tg_user: User) -> tuple[str, dict]:
        data = self._read()
        username = (tg_user.username or "").lower()
        preferred_key = f"u:{username}" if username else f"id:{tg_user.id}"

        existing_key = None
        for key, payload in data.items():
            if payload.get("tg_id") == tg_user.id:
                existing_key = key
                break
        if existing_key is None and username and preferred_key in data:
            existing_key = preferred_key

        if existing_key is None:
            data[preferred_key] = dict(DEFAULT_USER)
            existing_key = preferred_key

        if existing_key != preferred_key and preferred_key not in data:
            data[preferred_key] = data.pop(existing_key)
            existing_key = preferred_key

        user = data[existing_key]
        changed = self._ensure_user_defaults(user)
        if user.get("username") != (username or None):
            user["username"] = username or None
            changed = True
        if user.get("display_name") != tg_user.full_name:
            user["display_name"] = tg_user.full_name
            changed = True
        if user.get("tg_id") != tg_user.id:
            user["tg_id"] = tg_user.id
            changed = True
        if changed:
            data[existing_key] = user
            self._write(data)
        return existing_key, user

    def get_by_username(self, username: str) -> tuple[str, dict] | None:
        data = self._read()
        normalized = username.removeprefix("@").lower()
        key = f"u:{normalized}"
        if key not in data:
            return None
        user = data[key]
        if self._ensure_user_defaults(user):
            data[key] = user
            self._write(data)
        return key, user

    def update_user(self, user_key: str, payload: dict) -> None:
        data = self._read()
        data[user_key] = payload
        self._write(data)

    def all_users(self) -> Dict[str, dict]:
        data = self._read()
        changed = False
        for uid, user in data.items():
            for field, default_value in DEFAULT_USER.items():
                if field not in user:
                    user[field] = default_value
                    changed = True
            data[uid] = user
        if changed:
            self._write(data)
        return data


def spin_slots() -> CasinoResult:
    symbols_pool = ["рџЌ’", "рџЌ‹", "рџЌ‡", "рџ””", "рџ’Ћ", "7пёЏвѓЈ"]
    # Higher win chance: 60% we force at least a pair.
    if random.random() < 0.60:
        main = random.choice(symbols_pool)
        symbols = [main, main, random.choice(symbols_pool)]
        random.shuffle(symbols)
    else:
        symbols = [random.choice(symbols_pool) for _ in range(3)]

    if symbols == ["7пёЏвѓЈ", "7пёЏвѓЈ", "7пёЏвѓЈ"]:
        return CasinoResult(symbols, 10.0, "Р”Р¶РµРєРїРѕС‚!")
    if symbols[0] == symbols[1] == symbols[2]:
        return CasinoResult(symbols, 4.5, "РўСЂРѕР№РЅРѕРµ СЃРѕРІРїР°РґРµРЅРёРµ")
    if len(set(symbols)) == 2:
        return CasinoResult(symbols, 2.0, "РџР°СЂР° СЃРёРјРІРѕР»РѕРІ")
    return CasinoResult(symbols, 0.0, "РњРёРјРѕ")


def parse_bet(text: str) -> int | None:
    parts = text.strip().split()
    if len(parts) != 2:
        return None
    if not parts[1].isdigit():
        return None
    return int(parts[1])


def parse_choice_bet(text: str) -> tuple[str, int] | None:
    parts = text.strip().split()
    if len(parts) != 3:
        return None
    choice = parts[1].lower()
    if not parts[2].isdigit():
        return None
    return choice, int(parts[2])


def parse_admin_balance_cmd(text: str) -> tuple[str, int] | None:
    parts = text.strip().split()
    if len(parts) != 3:
        return None
    username = parts[1].removeprefix("@").lower()
    if not username:
        return None
    try:
        amount = int(parts[2])
    except ValueError:
        return None
    return username, amount


def parse_word_bet(text: str) -> tuple[str, int] | None:
    parts = text.strip().split()
    if len(parts) != 3:
        return None
    if not parts[2].isdigit():
        return None
    return parts[1].lower(), int(parts[2])


def parse_single_word_arg(text: str) -> str | None:
    parts = text.strip().split()
    if len(parts) != 2:
        return None
    return parts[1].lower()


def spin_uni_card() -> dict:
    roll = random.random()
    cumulative = 0.0
    for card in UNI_CARD_POOL:
        cumulative += card["chance"]
        if roll <= cumulative:
            return card
    return UNI_CARD_POOL[-1]


def format_balance(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def xp_for_next_level(level: int) -> int:
    return 120 + (level - 1) * 80


def xp_needed_for_n_levels(start_level: int, levels: int) -> int:
    if levels <= 0:
        return 0
    first = xp_for_next_level(start_level)
    step = 80
    # Sum of arithmetic progression:
    # levels * (2 * first + (levels - 1) * step) / 2
    return levels * (2 * first + (levels - 1) * step) // 2


def add_xp(user: dict, amount: int) -> tuple[int, bool]:
    if amount <= 0:
        return 0, False

    total_xp = user["xp"] + amount
    start_level = user["level"]

    # Fast leveling: binary search how many levels can be bought by XP.
    low, high = 0, 1
    while xp_needed_for_n_levels(start_level, high) <= total_xp:
        high *= 2

    while low < high:
        mid = (low + high + 1) // 2
        if xp_needed_for_n_levels(start_level, mid) <= total_xp:
            low = mid
        else:
            high = mid - 1

    gained_levels = low
    spent_xp = xp_needed_for_n_levels(start_level, gained_levels)
    user["level"] = start_level + gained_levels
    user["xp"] = total_xp - spent_xp
    return gained_levels, gained_levels > 0


def admin_only(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id in ADMIN_IDS)


def resolve_user_label(user_key: str, user_data: dict) -> str:
    username = user_data.get("username")
    full_name = user_data.get("display_name")
    if full_name and username:
        return f"{full_name} (@{username})"
    if username:
        return f"@{username}"
    if full_name:
        return full_name
    return user_key


def build_help() -> str:
    return (
        f"рџЋ® {BOT_NAME} вЂ” РєРѕРјР°РЅРґС‹ Р±РѕС‚Р°:\n"
        "/start вЂ” РЅР°С‡Р°С‚СЊ РёРіСЂСѓ\n"
        "/balance вЂ” РїРѕСЃРјРѕС‚СЂРµС‚СЊ Р±Р°Р»Р°РЅСЃ\n"
        "/profile вЂ” РїСЂРѕС„РёР»СЊ Рё СѓСЂРѕРІРµРЅСЊ\n"
        "/top вЂ” Р»РёРґРµСЂР±РѕСЂРґ\n"
        "/daily вЂ” РµР¶РµРґРЅРµРІРЅС‹Р№ Р±РѕРЅСѓСЃ\n"
        "/casino <СЃС‚Р°РІРєР°> вЂ” СЃС‹РіСЂР°С‚СЊ РІ СЃР»РѕС‚С‹\n"
        "/coin <РѕСЂРµР»|СЂРµС€РєР°> <СЃС‚Р°РІРєР°> вЂ” РјРѕРЅРµС‚РєР°\n"
        "/dice <СЃС‚Р°РІРєР°> вЂ” РєСѓР±РёРє РїСЂРѕС‚РёРІ Р±РѕС‚Р°\n"
        "/roulette <red|black|green> <СЃС‚Р°РІРєР°> вЂ” СЂСѓР»РµС‚РєР°\n"
        "/unicard <СЃС‚Р°РІРєР°> вЂ” РєР°СЂС‚Р° СЃ РџРёС‚РµСЂРѕРј Р“СЂРёС„С„РёРЅРѕРј\n"
        "/rps <РєР°РјРµРЅСЊ|РЅРѕР¶РЅРёС†С‹|Р±СѓРјР°РіР°> вЂ” РєР°РјРµРЅСЊ-РЅРѕР¶РЅРёС†С‹-Р±СѓРјР°РіР°\n"
        "/guess <1-5> вЂ” СѓРіР°РґР°Р№ С‡РёСЃР»Рѕ\n"
        "/quiz <РѕС‚РІРµС‚> вЂ” РјРёРЅРё-РІРёРєС‚РѕСЂРёРЅР°\n"
        "/8ball <РІРѕРїСЂРѕСЃ> вЂ” РјР°РіРёС‡РµСЃРєРёР№ С€Р°СЂ\n"
        "/rate <С‚РµРєСЃС‚> вЂ” РѕС†РµРЅРєР° РѕС‚ 1 РґРѕ 10\n"
        "/admin вЂ” Р°РґРјРёРЅ-РєРѕРјР°РЅРґС‹\n"
        "/help вЂ” СЃРїРёСЃРѕРє РєРѕРјР°РЅРґ\n\n"
        "РџСЂРёРјРµСЂС‹: /casino 50, /rps РєР°РјРµРЅСЊ, /guess 3, /8ball СЏ СЃС‚Р°РЅСѓ Р±РѕРіР°С‚С‹Рј?"
    )


def get_token() -> str:
    token = BOT_TOKEN.strip() or os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "РќРµ РЅР°Р№РґРµРЅ BOT_TOKEN. РЈРєР°Р¶Рё РµРіРѕ РІ РїРµСЂРµРјРµРЅРЅРѕР№ BOT_TOKEN РёР»Рё РІ BOT_TOKEN РІРЅСѓС‚СЂРё bot.py."
        )
    return token


async def main() -> None:
    storage = Storage(DATA_FILE)
    bot = Bot(token=get_token())
    dp = Dispatcher()

    def current_user(message: Message) -> tuple[str, dict]:
        return storage.get_or_create_by_telegram(message.from_user)

    async def send_with_peter(message: Message, text: str) -> None:
        if not PETER_ONLY_MODE:
            await message.answer(text)
            return
        try:
            await message.answer_animation(animation=random.choice(PETER_GRIFFIN_IMAGES), caption=text)
        except Exception:
            await message.answer(text)

    @dp.message(Command("start"))
    async def start_handler(message: Message) -> None:
        _, user = current_user(message)
        await message.answer(
            f"Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ РІ {BOT_NAME} Casino Bot!\n"
            f"РўРІРѕР№ СЃС‚Р°СЂС‚РѕРІС‹Р№ Р±Р°Р»Р°РЅСЃ: {format_balance(user['balance'])} РјРѕРЅРµС‚.\n\n"
            + build_help()
        )

    @dp.message(Command("help"))
    async def help_handler(message: Message) -> None:
        await message.answer(build_help())

    @dp.message(Command("balance"))
    async def balance_handler(message: Message) -> None:
        _, user = current_user(message)
        await message.answer(f"рџ’° РўРІРѕР№ Р±Р°Р»Р°РЅСЃ: {format_balance(user['balance'])} РјРѕРЅРµС‚.")

    @dp.message(Command("profile"))
    async def profile_handler(message: Message) -> None:
        _, user = current_user(message)
        next_need = xp_for_next_level(user["level"])
        await message.answer(
            f"рџ‘¤ РџСЂРѕС„РёР»СЊ\n"
            f"РЈСЂРѕРІРµРЅСЊ: {user['level']}\n"
            f"XP: {user['xp']} / {next_need}\n"
            f"РЎС‹РіСЂР°РЅРѕ РёРіСЂ: {user['games_played']}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )

    @dp.message(Command("top"))
    async def top_handler(message: Message) -> None:
        users = storage.all_users()
        if not users:
            await message.answer("Р›РёРґРµСЂР±РѕСЂРґ РїРѕРєР° РїСѓСЃС‚.")
            return

        ranked = sorted(
            users.items(),
            key=lambda item: (item[1].get("balance", 0), item[1].get("level", 1)),
            reverse=True,
        )[:10]
        lines = ["рџЏ† РўРѕРї РёРіСЂРѕРєРѕРІ РїРѕ Р±Р°Р»Р°РЅСЃСѓ:"]
        for idx, (uid, udata) in enumerate(ranked, start=1):
            label = resolve_user_label(uid, udata)
            lines.append(
                f"{idx}. {label} вЂ” {format_balance(udata.get('balance', 0))} | "
                f"LVL {udata.get('level', 1)}"
            )
        await message.answer("\n".join(lines))

    @dp.message(Command("daily"))
    async def daily_handler(message: Message) -> None:
        user_key, user = current_user(message)
        today = date.today().isoformat()
        if user["last_daily"] == today:
            await message.answer("РЎРµРіРѕРґРЅСЏ Р±РѕРЅСѓСЃ СѓР¶Рµ Р·Р°Р±СЂР°РЅ. Р’РѕР·РІСЂР°С‰Р°Р№СЃСЏ Р·Р°РІС‚СЂР°.")
            return

        user["balance"] += DAILY_BONUS
        user["last_daily"] = today
        add_xp(user, 15)
        storage.update_user(user_key, user)
        await message.answer(
            f"рџЋЃ РўС‹ РїРѕР»СѓС‡РёР» РµР¶РµРґРЅРµРІРЅС‹Р№ Р±РѕРЅСѓСЃ: +{DAILY_BONUS} РјРѕРЅРµС‚.\n"
            f"РўРµРєСѓС‰РёР№ Р±Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )

    @dp.message(Command("casino"))
    async def casino_handler(message: Message) -> None:
        bet = parse_bet(message.text or "")
        if bet is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /casino <СЃС‚Р°РІРєР°>\nРџСЂРёРјРµСЂ: /casino 100")
            return

        if bet < CASINO_MIN_BET:
            await message.answer(f"РњРёРЅРёРјР°Р»СЊРЅР°СЏ СЃС‚Р°РІРєР°: {CASINO_MIN_BET} РјРѕРЅРµС‚.")
            return

        user_key, user = current_user(message)
        if bet > user["balance"]:
            await message.answer("РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РјРѕРЅРµС‚ РґР»СЏ С‚Р°РєРѕР№ СЃС‚Р°РІРєРё.")
            return

        result = spin_slots()
        win_amount = int(bet * result.multiplier)
        user["balance"] = user["balance"] - bet + win_amount
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, 20)
        storage.update_user(user_key, user)

        reply = (
            f"рџЋ° {' | '.join(result.symbols)}\n"
            f"{result.title}\n"
            f"РЎС‚Р°РІРєР°: {format_balance(bet)}\n"
            f"Р’С‹РёРіСЂС‹С€: {format_balance(win_amount)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("coin"))
    async def coin_handler(message: Message) -> None:
        parsed = parse_choice_bet(message.text or "")
        if parsed is None:
            await message.answer(
                "РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /coin <РѕСЂРµР»|СЂРµС€РєР°> <СЃС‚Р°РІРєР°>\nРџСЂРёРјРµСЂ: /coin РѕСЂРµР» 50"
            )
            return

        choice_raw, bet = parsed
        choice_map = {"РѕСЂРµР»": "heads", "СЂРµС€РєР°": "tails", "heads": "heads", "tails": "tails"}
        choice = choice_map.get(choice_raw)
        if choice is None:
            await message.answer("Р’С‹Р±РµСЂРё СЃС‚РѕСЂРѕРЅСѓ: РѕСЂРµР» РёР»Рё СЂРµС€РєР°.")
            return
        if bet < CASINO_MIN_BET:
            await message.answer(f"РњРёРЅРёРјР°Р»СЊРЅР°СЏ СЃС‚Р°РІРєР°: {CASINO_MIN_BET} РјРѕРЅРµС‚.")
            return

        user_key, user = current_user(message)
        if bet > user["balance"]:
            await message.answer("РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РјРѕРЅРµС‚ РґР»СЏ С‚Р°РєРѕР№ СЃС‚Р°РІРєРё.")
            return

        # 60% chance to land on player's choice.
        result = choice if random.random() < 0.60 else random.choice(["heads", "tails"])
        won = result == choice
        win_amount = bet * 2 if won else 0
        user["balance"] = user["balance"] - bet + win_amount
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, 12)
        storage.update_user(user_key, user)

        result_ru = "РѕСЂРµР»" if result == "heads" else "СЂРµС€РєР°"
        reply = (
            f"рџЄ™ Р’С‹РїР°Р»Рѕ: {result_ru}\n"
            f"{'РџРѕР±РµРґР°!' if won else 'РџСЂРѕРёРіСЂС‹С€'}\n"
            f"РЎС‚Р°РІРєР°: {format_balance(bet)}\n"
            f"Р’С‹РёРіСЂС‹С€: {format_balance(win_amount)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("dice"))
    async def dice_handler(message: Message) -> None:
        bet = parse_bet(message.text or "")
        if bet is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /dice <СЃС‚Р°РІРєР°>\nРџСЂРёРјРµСЂ: /dice 80")
            return
        if bet < CASINO_MIN_BET:
            await message.answer(f"РњРёРЅРёРјР°Р»СЊРЅР°СЏ СЃС‚Р°РІРєР°: {CASINO_MIN_BET} РјРѕРЅРµС‚.")
            return

        user_key, user = current_user(message)
        if bet > user["balance"]:
            await message.answer("РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РјРѕРЅРµС‚ РґР»СЏ С‚Р°РєРѕР№ СЃС‚Р°РІРєРё.")
            return

        # Bias in player's favor.
        player_roll = random.randint(2, 6)
        bot_roll = random.randint(1, 5)
        if player_roll > bot_roll:
            win_amount = int(bet * 1.9)
            title = "РўС‹ РїРѕР±РµРґРёР» Р±РѕС‚Р°!"
        elif player_roll == bot_roll:
            win_amount = bet
            title = "РќРёС‡СЊСЏ"
        else:
            win_amount = 0
            title = "Р‘РѕС‚ РїРѕР±РµРґРёР»"

        user["balance"] = user["balance"] - bet + win_amount
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, 16)
        storage.update_user(user_key, user)
        reply = (
            f"рџЋІ РўС‹: {player_roll} | Р‘РѕС‚: {bot_roll}\n"
            f"{title}\n"
            f"РЎС‚Р°РІРєР°: {format_balance(bet)}\n"
            f"Р’С‹РёРіСЂС‹С€: {format_balance(win_amount)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("roulette"))
    async def roulette_handler(message: Message) -> None:
        parsed = parse_choice_bet(message.text or "")
        if parsed is None:
            await message.answer(
                "РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /roulette <red|black|green> <СЃС‚Р°РІРєР°>\n"
                "РџСЂРёРјРµСЂ: /roulette red 100"
            )
            return

        color, bet = parsed
        if color not in ROULETTE_COLORS:
            await message.answer("Р’С‹Р±РµСЂРё С†РІРµС‚: red, black РёР»Рё green.")
            return
        if bet < CASINO_MIN_BET:
            await message.answer(f"РњРёРЅРёРјР°Р»СЊРЅР°СЏ СЃС‚Р°РІРєР°: {CASINO_MIN_BET} РјРѕРЅРµС‚.")
            return

        user_key, user = current_user(message)
        if bet > user["balance"]:
            await message.answer("РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РјРѕРЅРµС‚ РґР»СЏ С‚Р°РєРѕР№ СЃС‚Р°РІРєРё.")
            return

        # 60% chance roulette lands on selected color.
        if random.random() < 0.60:
            result_color = color
        else:
            roll = random.randint(1, 37)
            if roll == 37:
                result_color = "green"
            elif roll % 2 == 0:
                result_color = "red"
            else:
                result_color = "black"

        multipliers = {"red": 2, "black": 2, "green": 14}
        won = result_color == color
        win_amount = bet * multipliers[color] if won else 0
        user["balance"] = user["balance"] - bet + win_amount
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, 18)
        storage.update_user(user_key, user)

        reply = (
            f"рџЋЎ Р’С‹РїР°Р»Рѕ: {ROULETTE_COLORS[result_color]} {result_color}\n"
            f"{'РџРѕР±РµРґР°!' if won else 'РњРёРјРѕ'}\n"
            f"РЎС‚Р°РІРєР°: {format_balance(bet)}\n"
            f"Р’С‹РёРіСЂС‹С€: {format_balance(win_amount)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("rps"))
    async def rps_handler(message: Message) -> None:
        pick_raw = parse_single_word_arg(message.text or "")
        if pick_raw is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /rps <РєР°РјРµРЅСЊ|РЅРѕР¶РЅРёС†С‹|Р±СѓРјР°РіР°>")
            return
        player = RPS_CHOICES.get(pick_raw)
        if player is None:
            await message.answer("Р’С‹Р±РѕСЂ: РєР°РјРµРЅСЊ, РЅРѕР¶РЅРёС†С‹ РёР»Рё Р±СѓРјР°РіР°.")
            return

        # 55% chance player wins, 20% draw, rest loses.
        wins_map = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
        loses_map = {"rock": "paper", "scissors": "rock", "paper": "scissors"}
        luck = random.random()
        if luck < 0.55:
            bot_pick = wins_map[player]
        elif luck < 0.75:
            bot_pick = player
        else:
            bot_pick = loses_map[player]
        labels = {"rock": "РєР°РјРµРЅСЊ", "scissors": "РЅРѕР¶РЅРёС†С‹", "paper": "Р±СѓРјР°РіР°"}
        wins = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}

        user_key, user = current_user(message)
        if player == bot_pick:
            title = "РќРёС‡СЊСЏ"
            bonus = 20
            xp_gain = 8
        elif (player, bot_pick) in wins:
            title = "РўС‹ РїРѕР±РµРґРёР»!"
            bonus = 60
            xp_gain = 18
        else:
            title = "Р‘РѕС‚ РїРѕР±РµРґРёР»"
            bonus = 0
            xp_gain = 6

        user["balance"] += bonus
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, xp_gain)
        storage.update_user(user_key, user)
        reply = (
            f"рџЄЁвњ‚пёЏрџ“„ РўС‹: {labels[player]} | Р‘РѕС‚: {labels[bot_pick]}\n"
            f"{title}\n"
            f"РќР°РіСЂР°РґР°: {format_balance(bonus)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("unicard"))
    async def unicard_handler(message: Message) -> None:
        bet = parse_bet(message.text or "")
        if bet is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /unicard <СЃС‚Р°РІРєР°>\nРџСЂРёРјРµСЂ: /unicard 100")
            return
        if bet < CASINO_MIN_BET:
            await message.answer(f"РњРёРЅРёРјР°Р»СЊРЅР°СЏ СЃС‚Р°РІРєР°: {CASINO_MIN_BET} РјРѕРЅРµС‚.")
            return

        user_key, user = current_user(message)
        if bet > user["balance"]:
            await message.answer("РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РјРѕРЅРµС‚ РґР»СЏ С‚Р°РєРѕР№ СЃС‚Р°РІРєРё.")
            return

        card = spin_uni_card()
        win_amount = int(bet * card["multiplier"])
        user["balance"] = user["balance"] - bet + win_amount
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, 24)
        storage.update_user(user_key, user)

        caption = (
            f"рџѓЏ РўРµР±Рµ РІС‹РїР°Р»Р°: {card['name']}\n"
            f"Р РµРґРєРѕСЃС‚СЊ: {card['rarity']}\n"
            f"РЎС‚Р°РІРєР°: {format_balance(bet)}\n"
            f"Р’С‹РёРіСЂС‹С€: {format_balance(win_amount)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            caption += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"

        try:
            await message.answer_animation(animation=random.choice(PETER_GRIFFIN_IMAGES), caption=caption)
        except Exception:
            await message.answer(caption + "\n\n(РљР°СЂС‚РёРЅРєР° РІСЂРµРјРµРЅРЅРѕ РЅРµРґРѕСЃС‚СѓРїРЅР°)")

    @dp.message(Command("guess"))
    async def guess_handler(message: Message) -> None:
        parts = (message.text or "").strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /guess <1-5>\nРџСЂРёРјРµСЂ: /guess 4")
            return
        guessed = int(parts[1])
        if guessed < 1 or guessed > 5:
            await message.answer("Р§РёСЃР»Рѕ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ РѕС‚ 1 РґРѕ 5.")
            return

        # Give better odds in guess game.
        answer = guessed if random.random() < 0.50 else random.randint(1, 5)
        user_key, user = current_user(message)
        if guessed == answer:
            reward = 120
            xp_gain = 20
            title = "РџРѕРїР°Р» РІ С‚РѕС‡РєСѓ!"
        else:
            reward = 10
            xp_gain = 7
            title = "РџРѕС‡С‚Рё, РЅРѕ РјРёРјРѕ."
        user["balance"] += reward
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, xp_gain)
        storage.update_user(user_key, user)
        reply = (
            f"рџ”ў Р‘С‹Р»Рѕ С‡РёСЃР»Рѕ: {answer}\n"
            f"{title}\n"
            f"РќР°РіСЂР°РґР°: {format_balance(reward)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("quiz"))
    async def quiz_handler(message: Message) -> None:
        parts = (message.text or "").strip().split(maxsplit=1)
        if len(parts) != 2:
            q = random.choice(QUIZ_QUESTIONS)
            await message.answer(
                f"вќ“ Р’РѕРїСЂРѕСЃ: {q['q']}\n"
                "РћС‚РІРµС‚СЊ РєРѕРјР°РЅРґРѕР№: /quiz <С‚РІРѕР№_РѕС‚РІРµС‚>"
            )
            return

        answer = parts[1].strip().lower()
        q = random.choice(QUIZ_QUESTIONS)
        correct = answer == q["a"]
        user_key, user = current_user(message)
        reward = 140 if correct else 0
        xp_gain = 22 if correct else 5
        user["balance"] += reward
        user["games_played"] += 1
        gained_levels, level_up = add_xp(user, xp_gain)
        storage.update_user(user_key, user)
        reply = (
            f"вќ“ Р’РѕРїСЂРѕСЃ: {q['q']}\n"
            f"РўРІРѕР№ РѕС‚РІРµС‚: {answer}\n"
            f"{'Р’РµСЂРЅРѕ!' if correct else 'РќРµРІРµСЂРЅРѕ. РџСЂР°РІРёР»СЊРЅС‹Р№ РѕС‚РІРµС‚: ' + q['a']}\n"
            f"РќР°РіСЂР°РґР°: {format_balance(reward)}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(user['balance'])}"
        )
        if level_up:
            reply += f"\nв¬†пёЏ РќРѕРІС‹Р№ СѓСЂРѕРІРµРЅСЊ! +{gained_levels} (С‚РµРєСѓС‰РёР№: {user['level']})"
        await message.answer(reply)

    @dp.message(Command("8ball"))
    async def ball_handler(message: Message) -> None:
        parts = (message.text or "").strip().split(maxsplit=1)
        if len(parts) != 2:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /8ball <РІРѕРїСЂРѕСЃ>")
            return
        user_key, user = current_user(message)
        user["games_played"] += 1
        add_xp(user, 4)
        storage.update_user(user_key, user)
        await send_with_peter(message, f"рџЋ± {random.choice(MAGIC_ANSWERS)}")

    @dp.message(Command("rate"))
    async def rate_handler(message: Message) -> None:
        parts = (message.text or "").strip().split(maxsplit=1)
        if len(parts) != 2:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /rate <С‡С‚Рѕ_РѕС†РµРЅРёС‚СЊ>")
            return
        user_key, user = current_user(message)
        user["games_played"] += 1
        add_xp(user, 6)
        storage.update_user(user_key, user)
        await send_with_peter(message, f"рџ“Љ РћС†РµРЅРєР°: {random.randint(1, 10)}/10")

    @dp.message(Command("admin"))
    async def admin_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        await message.answer(
            "рџ›  РђРґРјРёРЅ-РїР°РЅРµР»СЊ:\n"
            "/admin_add <@username> <amount> вЂ” РЅР°РєСЂСѓС‚РёС‚СЊ Р±Р°Р»Р°РЅСЃ\n"
            "/admin_set <@username> <amount> вЂ” СѓСЃС‚Р°РЅРѕРІРёС‚СЊ Р±Р°Р»Р°РЅСЃ\n"
            "/admin_take <@username> <amount> вЂ” СЃРЅСЏС‚СЊ Р±Р°Р»Р°РЅСЃ\n"
            "/admin_addxp <@username> <amount> вЂ” РІС‹РґР°С‚СЊ XP\n"
            "/admin_reset_money <@username> вЂ” РѕР±РЅСѓР»РёС‚СЊ Р±Р°Р»Р°РЅСЃ РёРіСЂРѕРєСѓ\n"
            "/admin_reset_xp <@username> вЂ” РѕР±РЅСѓР»РёС‚СЊ XP/СѓСЂРѕРІРµРЅСЊ РёРіСЂРѕРєСѓ\n"
            "/admin_all_money <amount> вЂ” РІС‹РґР°С‚СЊ РІСЃРµРј РёРіСЂРѕРєР°Рј РјРѕРЅРµС‚С‹\n"
            "/admin_all_level <levels> вЂ” РІС‹РґР°С‚СЊ РІСЃРµРј РёРіСЂРѕРєР°Рј СѓСЂРѕРІРЅРё\n"
            "/admin_all_reset_money вЂ” РѕР±РЅСѓР»РёС‚СЊ Р±Р°Р»Р°РЅСЃ РІСЃРµРј\n"
            "/admin_all_reset_xp вЂ” РѕР±РЅСѓР»РёС‚СЊ XP/СѓСЂРѕРІРЅРё РІСЃРµРј\n"
            "/admin_gamegift <@username> <coins> <xp> вЂ” РЅР°РіСЂР°РґР° Р·Р° РёРІРµРЅС‚\n"
            "/mute <РјРёРЅСѓС‚С‹> (reply) вЂ” Р·Р°РјСѓС‚РёС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ\n"
            "/unmute (reply) вЂ” СЂР°Р·РјСѓС‚РёС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ\n"
            "/slowmode <СЃРµРєСѓРЅРґС‹> вЂ” РєРґ С‡Р°С‚Р° 0..3600\n"
            "/admin_stats вЂ” РѕР±С‰Р°СЏ СЃС‚Р°С‚РёСЃС‚РёРєР°"
        )

    @dp.message(Command("admin_add"))
    async def admin_add_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parsed = parse_admin_balance_cmd(message.text or "")
        if parsed is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_add <@username> <amount>")
            return
        target_username, amount = parsed
        if amount <= 0:
            await message.answer("РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ Р±РѕР»СЊС€Рµ 0.")
            return
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        target["balance"] += amount
        storage.update_user(target_key, target)
        await message.answer(
            f"Р“РѕС‚РѕРІРѕ. @{target_username} РїРѕР»СѓС‡РёР» +{format_balance(amount)}. "
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(target['balance'])}"
        )

    @dp.message(Command("admin_set"))
    async def admin_set_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parsed = parse_admin_balance_cmd(message.text or "")
        if parsed is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_set <@username> <amount>")
            return
        target_username, amount = parsed
        if amount < 0:
            await message.answer("Р‘Р°Р»Р°РЅСЃ РЅРµ РјРѕР¶РµС‚ Р±С‹С‚СЊ РѕС‚СЂРёС†Р°С‚РµР»СЊРЅС‹Рј.")
            return
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        target["balance"] = amount
        storage.update_user(target_key, target)
        await message.answer(
            f"Р“РѕС‚РѕРІРѕ. @{target_username} С‚РµРїРµСЂСЊ РёРјРµРµС‚ {format_balance(target['balance'])} РјРѕРЅРµС‚."
        )

    @dp.message(Command("admin_take"))
    async def admin_take_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parsed = parse_admin_balance_cmd(message.text or "")
        if parsed is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_take <@username> <amount>")
            return
        target_username, amount = parsed
        if amount <= 0:
            await message.answer("РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ Р±РѕР»СЊС€Рµ 0.")
            return
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        target["balance"] = max(0, target["balance"] - amount)
        storage.update_user(target_key, target)
        await message.answer(
            f"Р“РѕС‚РѕРІРѕ. РЈ @{target_username} СЃРїРёСЃР°РЅРѕ {format_balance(amount)}. "
            f"Р‘Р°Р»Р°РЅСЃ: {format_balance(target['balance'])}"
        )

    @dp.message(Command("admin_addxp"))
    async def admin_addxp_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parsed = parse_admin_balance_cmd(message.text or "")
        if parsed is None:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_addxp <@username> <amount>")
            return
        target_username, amount = parsed
        if amount <= 0:
            await message.answer("XP РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ Р±РѕР»СЊС€Рµ 0.")
            return
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        gained_levels, _ = add_xp(target, amount)
        storage.update_user(target_key, target)
        await message.answer(
            f"Р’С‹РґР°РЅРѕ {amount} XP РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ @{target_username}. "
            f"РЈСЂРѕРІРµРЅСЊ: {target['level']} (+{gained_levels}), XP: {target['xp']}"
        )

    @dp.message(Command("admin_all_money"))
    async def admin_all_money_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 2:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_all_money <amount>")
            return
        try:
            amount = int(parts[1])
        except ValueError:
            await message.answer("РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ С‡РёСЃР»РѕРј.")
            return
        if amount <= 0:
            await message.answer("РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ Р±РѕР»СЊС€Рµ 0.")
            return

        users = storage.all_users()
        for uid, user in users.items():
            user["balance"] = user.get("balance", 0) + amount
            users[uid] = user
        storage._write(users)
        await message.answer(
            f"Р’С‹РґР°Р» РІСЃРµРј РёРіСЂРѕРєР°Рј РїРѕ {format_balance(amount)} РјРѕРЅРµС‚.\n"
            f"Р—Р°С‚СЂРѕРЅСѓС‚Рѕ Р°РєРєР°СѓРЅС‚РѕРІ: {len(users)}"
        )

    @dp.message(Command("admin_all_level"))
    async def admin_all_level_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 2:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_all_level <levels>")
            return
        try:
            levels = int(parts[1])
        except ValueError:
            await message.answer("РљРѕР»РёС‡РµСЃС‚РІРѕ СѓСЂРѕРІРЅРµР№ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ С‡РёСЃР»РѕРј.")
            return
        if levels <= 0:
            await message.answer("РљРѕР»РёС‡РµСЃС‚РІРѕ СѓСЂРѕРІРЅРµР№ РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ Р±РѕР»СЊС€Рµ 0.")
            return

        users = storage.all_users()
        for uid, user in users.items():
            current_level = user.get("level", 1)
            user["level"] = current_level + levels
            users[uid] = user
        storage._write(users)
        await message.answer(
            f"Р’С‹РґР°Р» РІСЃРµРј РёРіСЂРѕРєР°Рј +{levels} СѓСЂРѕРІРЅРµР№.\n"
            f"Р—Р°С‚СЂРѕРЅСѓС‚Рѕ Р°РєРєР°СѓРЅС‚РѕРІ: {len(users)}"
        )

    @dp.message(Command("admin_reset_money"))
    async def admin_reset_money_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 2:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_reset_money <@username>")
            return
        target_username = parts[1].removeprefix("@").lower()
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        target["balance"] = 0
        storage.update_user(target_key, target)
        await message.answer(f"Р‘Р°Р»Р°РЅСЃ @{target_username} РѕР±РЅСѓР»РµРЅ.")

    @dp.message(Command("admin_reset_xp"))
    async def admin_reset_xp_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 2:
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_reset_xp <@username>")
            return
        target_username = parts[1].removeprefix("@").lower()
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        target["xp"] = 0
        target["level"] = 1
        storage.update_user(target_key, target)
        await message.answer(f"XP Рё СѓСЂРѕРІРµРЅСЊ @{target_username} РѕР±РЅСѓР»РµРЅС‹.")

    @dp.message(Command("admin_all_reset_money"))
    async def admin_all_reset_money_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        users = storage.all_users()
        for uid, user in users.items():
            user["balance"] = 0
            users[uid] = user
        storage._write(users)
        await message.answer(f"РћР±РЅСѓР»РёР» Р±Р°Р»Р°РЅСЃ РІСЃРµРј РёРіСЂРѕРєР°Рј. Р—Р°С‚СЂРѕРЅСѓС‚Рѕ: {len(users)}")

    @dp.message(Command("admin_all_reset_xp"))
    async def admin_all_reset_xp_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        users = storage.all_users()
        for uid, user in users.items():
            user["xp"] = 0
            user["level"] = 1
            users[uid] = user
        storage._write(users)
        await message.answer(f"РћР±РЅСѓР»РёР» XP Рё СѓСЂРѕРІРЅРё РІСЃРµРј РёРіСЂРѕРєР°Рј. Р—Р°С‚СЂРѕРЅСѓС‚Рѕ: {len(users)}")

    @dp.message(Command("admin_stats"))
    async def admin_stats_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        users = storage.all_users()
        total_users = len(users)
        total_balance = sum(u.get("balance", 0) for u in users.values())
        total_games = sum(u.get("games_played", 0) for u in users.values())
        await message.answer(
            f"рџ“Љ РЎС‚Р°С‚РёСЃС‚РёРєР°:\n"
            f"РџРѕР»СЊР·РѕРІР°С‚РµР»РµР№: {total_users}\n"
            f"Р’СЃРµРіРѕ РјРѕРЅРµС‚ РІ СЃРёСЃС‚РµРјРµ: {format_balance(total_balance)}\n"
            f"Р’СЃРµРіРѕ СЃС‹РіСЂР°РЅРѕ РёРіСЂ: {total_games}"
        )

    @dp.message(Command("admin_gamegift"))
    async def admin_gamegift_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 4 or not parts[2].isdigit() or not parts[3].isdigit():
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /admin_gamegift <@username> <coins> <xp>")
            return
        target_username = parts[1].removeprefix("@").lower()
        coins = int(parts[2])
        xp_value = int(parts[3])
        target_pair = storage.get_by_username(target_username)
        if target_pair is None:
            await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅРµ РЅР°Р№РґРµРЅ. РћРЅ РґРѕР»Р¶РµРЅ С…РѕС‚СЏ Р±С‹ СЂР°Р· РЅР°РїРёСЃР°С‚СЊ Р±РѕС‚Сѓ.")
            return
        target_key, target = target_pair
        target["balance"] += coins
        gained_levels, _ = add_xp(target, xp_value)
        storage.update_user(target_key, target)
        await message.answer(
            f"РРІРµРЅС‚-РЅР°РіСЂР°РґР° РІС‹РґР°РЅР° @{target_username}: +{format_balance(coins)} РјРѕРЅРµС‚, +{xp_value} XP. "
            f"LVL +{gained_levels}, Р±Р°Р»Р°РЅСЃ: {format_balance(target['balance'])}."
        )

    @dp.message(Command("mute"))
    async def mute_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        if message.chat.type == "private":
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° СЂР°Р±РѕС‚Р°РµС‚ С‚РѕР»СЊРєРѕ РІ РіСЂСѓРїРїРµ.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.answer("РћС‚РІРµС‚СЊ РЅР° СЃРѕРѕР±С‰РµРЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ: /mute <РјРёРЅСѓС‚С‹>")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /mute <РјРёРЅСѓС‚С‹> (reply)")
            return
        minutes = max(1, min(1440, int(parts[1])))
        target_id = message.reply_to_message.from_user.id
        until_date = message.date + timedelta(minutes=minutes)
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
        await message.answer(f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ Р·Р°РјСѓС‡РµРЅ РЅР° {minutes} РјРёРЅ.")

    @dp.message(Command("unmute"))
    async def unmute_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        if message.chat.type == "private":
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° СЂР°Р±РѕС‚Р°РµС‚ С‚РѕР»СЊРєРѕ РІ РіСЂСѓРїРїРµ.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.answer("РћС‚РІРµС‚СЊ РЅР° СЃРѕРѕР±С‰РµРЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ: /unmute")
            return
        target_id = message.reply_to_message.from_user.id
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False,
                can_manage_topics=False,
            ),
        )
        await message.answer("РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЂР°Р·РјСѓС‡РµРЅ.")

    @dp.message(Command("slowmode"))
    async def slowmode_handler(message: Message) -> None:
        if not admin_only(message):
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° С‚РѕР»СЊРєРѕ РґР»СЏ Р°РґРјРёРЅР°.")
            return
        if message.chat.type == "private":
            await message.answer("Р­С‚Р° РєРѕРјР°РЅРґР° СЂР°Р±РѕС‚Р°РµС‚ С‚РѕР»СЊРєРѕ РІ РіСЂСѓРїРїРµ.")
            return
        parts = (message.text or "").strip().split()
        if len(parts) != 2 or not parts[1].isdigit():
            await message.answer("РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ: /slowmode <СЃРµРєСѓРЅРґС‹>\nРџСЂРёРјРµСЂ: /slowmode 10")
            return
        seconds = max(0, min(3600, int(parts[1])))
        await bot.set_chat_slow_mode_delay(chat_id=message.chat.id, slow_mode_delay=seconds)
        await message.answer(f"РљР” С‡Р°С‚Р° СѓСЃС‚Р°РЅРѕРІР»РµРЅ: {seconds} СЃРµРє.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
