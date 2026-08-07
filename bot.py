import os
import json
import time
import random
import threading
import requests
from datetime import datetime
from flask import Flask, request
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, MessageEntity, InputMediaPhoto

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "8471373583"))
ADMIN_IDS = [OWNER_ID]
PORT = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit(1)

bot = TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ============================================================
# FILES & DATA
# ============================================================
USERS_FILE = "users.json"
GROUPS_FILE = "groups.json"
SETTINGS_FILE = "settings.json"
POSTS_FILE = "posts.json"
PENDING_FILE = "pending.json"
STATS_FILE = "stats.json"

# ============================================================
# STYLISH CHARACTERS - FULL SET
# ============================================================
def stylish_text(text: str) -> str:
    stylish_chars = {
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ', 'G': 'ɢ',
        'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ',
        'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    }
    result = ""
    for char in text:
        result += stylish_chars.get(char, char)
    return result

# ============================================================
# PREMIUM EMOJIS - TERA EMOJI_MAPPING (IDs ke saath)
# ============================================================
EMOJI_MAPPING = {
    "✅": ["6246537187614005254", "6246782404476803545", "6010060634803148161", "6010498532488778300"],
    "✔️": ["6246871001062185760", "6010264538375525668", "6010487760710800947"],
    "☑️": ["6246537187614005254", "6010097953773983121"],
    "👁️": ["6035338338406242050", "6035051267087143217", "6034945975963881533", "6034845323405299835"],
    "👁": ["6035338338406242050", "6035051267087143217"],
    "👀": ["6035225389356290238", "6035081585261287115", "6035243995154616907", "6035173858338672933"],
    "🔥": ["4956222745814762495", "4956606007221421405", "4956429969396859866", "6086954744268460848"],
    "💥": ["6032673796530377389", "4958479549265347295"],
    "⚡": ["5791970059597386804", "6087079590377820415", "6095843123252957701"],
    "❤️": ["5783157259152397008", "5801084710343938087", "6010280773351904888"],
    "💙": ["5780496071645991525", "6104780447684757396"],
    "💚": ["5888789252493283486"],
    "💛": ["5840261097719148872"],
    "🧡": ["5840263144212529797"],
    "💜": ["5840265018655703965"],
    "🖤": ["5840266939932994956"],
    "⭐": ["6244496562752331516", "5904618938578243567", "6010193314932855525"],
    "🌟": ["6010156854955480259", "6086924086791902713"],
    "✨": ["6010338729640596556", "6010086134023985536", "5801044672658805468"],
    "🧛": ["6034871295072539452", "6035251193519805118", "6032673796530377389"],
    "🧛‍♂️": ["6034871295072539452", "6035251193519805118"],
    "👹": ["6034962795055812935"],
    "👺": ["6034962795055812935"],
    "👻": ["6035070298087231243"],
    "👿": ["6035242444671421879", "6032985916098750553"],
    "😈": ["6035136809950778133", "6032695825417638128", "6032739101508113500"],
    "👑": ["5794422335599546668", "6089003761496232797", "6247039939305808563"],
    "💰": ["6089104607328342288", "6086730718774300509", "6086664791026307819"],
    "💵": ["6089140105233044310"],
    "💎": ["6086778246882399112", "5791697221799907788"],
    "👍": ["6089313931149448495", "4958626617535497157", "4956582500865410174"],
    "👎": ["6088789257285988672"],
    "👏": ["6093744967304352336", "4956582500865410174"],
    "😀": ["6093864814071780526", "6093922327978840798"],
    "😁": ["6035060329468137931"],
    "😂": ["5782741660936966676", "5782746664573867142"],
    "😃": ["6035337951859184840"],
    "😄": ["5782942227319756256"],
    "😅": ["5782670102486848559"],
    "😆": ["5782670102486848559"],
    "😉": ["6089024570612781324"],
    "😊": ["5780690182692935276"],
    "😍": ["6010179687001625256"],
    "🥰": ["6044369013952222465", "6044359320211034681"],
    "😘": ["6044373012566774137"],
    "😎": ["6032853480782172520", "6044373012566774137"],
    "😢": ["5780793884678296697"],
    "😭": ["5783024321324651865"],
    "😤": ["6034865170449175739", "6034855438053282213"],
    "😠": ["6035355642829475999", "6034843326245508065"],
    "😡": ["6035355642829475999"],
    "🤔": ["5782756916660802905", "5783034045130610245", "6093666528316625608"],
}

FLAG_MAPPING = {
    "🇺🇸": "5433865586356531140", "🇬🇧": "5433827537241258614", "🇫🇷": "5433636707549331311",
    "🇩🇪": "5433845881046578644", "🇮🇳": "5433601609076586221", "🇯🇵": "5434147542369579483",
    "🇨🇳": "5435996255207567113", "🇷🇺": "5433674924168328689", "🇧🇷": "5433825269498525925",
    "🇮🇹": "5433627189901801019", "🇨🇦": "5433979415874779870", "🇦🇺": "5434067655977874913",
    "🇰🇷": "5434142701941437163", "🇪🇸": "5434026158003862063", "🇲🇽": "5434131139889478358",
    "🇮🇩": "5431739800883312139", "🇳🇱": "5431656358258685474", "🇹🇷": "5433792911214917126",
    "🇸🇦": "5433991338703991663", "🇦🇪": "5434013938821902926", "🇿🇦": "5431489619038320862",
    "🇵🇰": "5434064563601421981", "🇧🇩": "5433854239052935880",
}

PRIMARY_EMOJIS = [
    "6035051267087143217", "6034945975963881533", "6034845323405299835", "6035169816774446606",
    "6035085583875837709", "6032965553658794901", "6035158121578501544", "6035208832257364215",
    "6035067476293718178", "6033130342964007608", "6035179291472302298", "6034986056598688136",
    "6032765485492214347", "6032660275973330342", "6034916516783198293", "6034904439335162652",
    "6034928023000585140", "6035372904303038740", "6035137110598492010", "6035338338406242050",
    "6035225389356290238", "6035081585261287115", "6035243995154616907", "6034865170449175739",
    "6035173858338672933", "6035210301136182368", "6035265083444042235", "6034871295072539452",
    "6035251193519805118", "6035136809950778133", "6032695825417638128", "6032739101508113500",
    "6032985916098750553", "6035374291577475270", "6035355642829475999", "6035337951859184840",
    "6035072209347678547", "6035060329468137931", "6033077437556855182", "6032823763903452409",
    "6034853694296560978", "6035015146412183834", "6035372401791864953", "6034955549445984368",
    "6032673796530377389", "6032916496542339992", "6034855438053282213", "6034962795055812935",
    "6034832094906028632", "6035087164423802534", "6035343380697846690", "6032737138708059114",
    "6035194237958493530", "6035317340311129897", "6035070298087231243", "6035242444671421879",
    "6034957847253487695", "6034925781027656042", "6033067975743902590", "6032975015471747801",
    "6034926000070988470", "6034843326245508065", "6032853480782172520", "6044373012566774137",
    "6044369013952222465", "6044359320211034681", "6044290806892729376", "6044238120528908813",
    "5791970059597386804", "5794422335599546668",
]

def get_random_premium_emoji():
    known = [eid for eid in PRIMARY_EMOJIS if get_fallback_for_id(eid) != "✅"]
    pool = known if known else PRIMARY_EMOJIS
    return random.choice(pool)

def get_fallback_for_id(emoji_id):
    for key, value in EMOJI_MAPPING.items():
        if emoji_id in value:
            return key
    for key, value in FLAG_MAPPING.items():
        if value == emoji_id:
            return key
    return "✅"

# ============================================================
# UTF-16 LENGTH - TELEGRAM ENTITY OFFSETS (EMOJI FIX)
# ============================================================
def utf16_len(text: str) -> int:
    return len(text.encode('utf-16-le')) // 2

# ============================================================
# BUILD MESSAGE - STYLISH + PREMIUM (ALWAYS ON)
# ============================================================
def build_message(text: str):
    text = stylish_text(text)

    lines = text.split('\n')
    result_lines = []
    entities = []
    offset = 0

    for line in lines:
        if line.strip():
            emoji_id = get_random_premium_emoji()
            fallback = get_fallback_for_id(emoji_id)
            new_line = f"{fallback} {line}"
            result_lines.append(new_line)
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=offset,
                length=utf16_len(fallback),
                custom_emoji_id=emoji_id
            ))
            offset += utf16_len(new_line) + 1
        else:
            result_lines.append(line)
            offset += utf16_len(line) + 1

    return '\n'.join(result_lines), entities

def send_pe(chat_id, text, reply_markup=None, parse_mode=None):
    try:
        processed_text, entities = build_message(text)
        if parse_mode:
            return bot.send_message(chat_id, processed_text, reply_markup=reply_markup, parse_mode=parse_mode)
        return bot.send_message(chat_id, processed_text, entities=entities, reply_markup=reply_markup)
    except Exception as e:
        print(f"Send error (premium): {e}")
        try:
            return bot.send_message(chat_id, f"✅ {stylish_text(text)}", reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as e2:
            print(f"Send error (plain): {e2}")
            return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)

# ============================================================
# SEND TO GROUP - MULTIPLE PHOTOS SUPPORT
# ============================================================
def send_to_group(group_id, text, photos=None, dm_username=None):
    try:
        settings = load_settings()
        stats = load_stats()

        stats["total_messages"] = stats.get("total_messages", 0) + 1
        save_stats(stats)

        markup = None
        if dm_username:
            markup = InlineKeyboardMarkup([
                [make_blue_button("DM ME", url=f"https://t.me/{dm_username}")]
            ])

        if photos and len(photos) > 1:
            media_group = []
            for photo in photos:
                media_group.append(InputMediaPhoto(media=photo))
            bot.send_media_group(group_id, media_group)
            send_pe(group_id, text, reply_markup=markup)
        elif photos and len(photos) == 1:
            caption, cap_entities = build_message(text)
            bot.send_photo(
                group_id, photo=photos[0],
                caption=caption, caption_entities=cap_entities,
                reply_markup=markup
            )
        else:
            send_pe(group_id, text, reply_markup=markup)

        return True
    except Exception as e:
        print(f"Send to group error: {e}")
        return False

# ============================================================
# COLORFUL BUTTONS - SAB GREEN (sirf DM ME blue)
# ============================================================
def make_green_button(text, callback=None, url=None):
    final = stylish_text(text)
    try:
        if callback:
            return InlineKeyboardButton(text=final, style="success", callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final, style="success", url=url)
        else:
            return InlineKeyboardButton(text=final, style="success")
    except:
        if callback:
            return InlineKeyboardButton(text=final, callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final, url=url)
        else:
            return InlineKeyboardButton(text=final)

def make_blue_button(text, callback=None, url=None):
    final = stylish_text(text)
    try:
        if callback:
            return InlineKeyboardButton(text=final, style="primary", callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final, style="primary", url=url)
        else:
            return InlineKeyboardButton(text=final, style="primary")
    except:
        if callback:
            return InlineKeyboardButton(text=final, callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final, url=url)
        else:
            return InlineKeyboardButton(text=final)

# ============================================================
# DATA FUNCTIONS
# ============================================================
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_groups():
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_groups(groups):
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=2)

def load_settings():
    default = {
        "upi": "vanshx111@naviaxis",
        "price": 99,
        "send_interval": 6,
        "sending_active": False,
        "welcome_image": "https://iili.io/C8DNTyQ.jpg",
        "welcome_text": "Welcome to Ad Bot!",
        "how_to_use_text": "1. Add me to any group\n2. Click Start Ads\n3. Pay subscription\n4. Ads will run!",
        "how_to_use_video": None,
        "total_messages": 0,
        "dm_username": None,
        "posts_per_cycle": 7,
        "ban_price": 0  # ===== NEW: 0 = FREE =====
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                for key, val in default.items():
                    if key not in data:
                        data[key] = val
                return data
        except:
            return default
    return default

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def load_posts():
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)

def load_pending():
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_pending(pending):
    with open(PENDING_FILE, "w") as f:
        json.dump(pending, f, indent=2)

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"total_messages": 0}
    return {"total_messages": 0}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

# ============================================================
# HELPERS
# ============================================================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def register_user(uid, username=None, name=None):
    users = load_users()
    if str(uid) not in users:
        users[str(uid)] = {
            "id": uid,
            "username": username,
            "name": name or "Unknown",
            "joined": datetime.now().isoformat(),
            "approved": False,
            "banned": False,
            "admin": False,
            "dm_username": None,
            "ban_paid": False
        }
        save_users(users)
        send_pe(OWNER_ID, f"New User Joined!\nID: {uid}\nUsername: @{username or 'N/A'}")
    return users[str(uid)]

def get_user(uid):
    users = load_users()
    return users.get(str(uid))

def update_user(uid, key, val):
    users = load_users()
    if str(uid) in users:
        users[str(uid)][key] = val
        save_users(users)

def get_dm_for_post(post, settings=None):
    if settings is None:
        settings = load_settings()
    owner_id = post.get("user_id") or post.get("added_by")
    if owner_id:
        owner = get_user(owner_id)
        if owner and owner.get("dm_username"):
            return owner["dm_username"]
    return settings.get("dm_username")

# ============================================================
# FORWARD REPLY TO OWNER
# ============================================================
@bot.message_handler(func=lambda m: m.reply_to_message is not None and m.reply_to_message.from_user.id == bot.get_me().id)
def forward_reply_to_owner(message):
    try:
        original = message.reply_to_message
        replier = message.from_user
        replier_name = replier.first_name or "Unknown"
        replier_username = f"@{replier.username}" if replier.username else "No username"
        replier_id = replier.id
        group_name = message.chat.title or "Unknown Group"
        group_id = message.chat.id

        forward_text = f"""
REPLY RECEIVED
GROUP: {group_name}
GROUP ID: {group_id}
REPLIED BY: {replier_name}
USERNAME: {replier_username}
USER ID: {replier_id}
ORIGINAL: {original.text or '[Media]'}
REPLY: {message.text or '[Media]'}
"""
        send_pe(OWNER_ID, forward_text)

        for uid, data in load_users().items():
            if data.get("approved", False) and int(uid) != OWNER_ID:
                try:
                    send_pe(int(uid), f"""
REPLY TO YOUR AD
GROUP: {group_name}
REPLIED BY: {replier_name}
USERNAME: {replier_username}
REPLY: {message.text or '[Media]'}
""")
                except:
                    pass
    except Exception as e:
        print(f"Forward reply error: {e}")

# ============================================================
# AUTO SENDING
# ============================================================
sending_active = False
sending_thread = None
album_buffers = {}

def auto_send_loop():
    global sending_active
    settings = load_settings()
    posts = load_posts()
    groups = load_groups()
    posts_per_cycle = settings.get("posts_per_cycle", 7)

    if not groups or not posts:
        return

    index = 0
    while sending_active:
        try:
            settings = load_settings()
            posts = load_posts()
            groups = load_groups()
            posts_per_cycle = settings.get("posts_per_cycle", 7)

            if not posts:
                time.sleep(5)
                continue

            for i in range(min(posts_per_cycle, len(posts))):
                current_post = posts[index % len(posts)]
                text = current_post.get("text", "Advertisement")
                photos = current_post.get("photos", [])
                dm_username = get_dm_for_post(current_post, settings)

                for group_id in groups.keys():
                    try:
                        send_to_group(group_id, text, photos, dm_username)
                    except:
                        pass

                index += 1
                time.sleep(settings.get("send_interval", 6))

        except Exception as e:
            print(f"Auto send error: {e}")
            time.sleep(5)

# ============================================================
# USER MENU
# ============================================================
def get_user_menu(uid):
    user = get_user(uid)
    approved = bool(user and user.get("approved", False))

    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton(stylish_text("START ADS")), KeyboardButton(stylish_text("STOP ADS")))
    markup.row(KeyboardButton(stylish_text("BUY SUBSCRIPTION")), KeyboardButton(stylish_text("ADD DM IN ADS")))
    if approved:
        markup.row(KeyboardButton(stylish_text("ADD POST")), KeyboardButton(stylish_text("STATS")))
    markup.row(KeyboardButton(stylish_text("🔍 BAN CHECK")), KeyboardButton(stylish_text("HOW TO USE")))
    markup.row(KeyboardButton(stylish_text("SUPPORT")), KeyboardButton(stylish_text("ABOUT")))
    return markup

def get_admin_menu(uid):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton(stylish_text("ADD GROUP")), KeyboardButton(stylish_text("REMOVE GROUP")))
    markup.row(KeyboardButton(stylish_text("LIST GROUPS")), KeyboardButton(stylish_text("ADD POST")))
    markup.row(KeyboardButton(stylish_text("LIST POSTS")), KeyboardButton(stylish_text("CHECK ALL POSTS")))
    markup.row(KeyboardButton(stylish_text("DELETE POST")), KeyboardButton(stylish_text("START ADS")))
    markup.row(KeyboardButton(stylish_text("STOP ADS")), KeyboardButton(stylish_text("SET INTERVAL")))
    markup.row(KeyboardButton(stylish_text("SET POSTS PER CYCLE")), KeyboardButton(stylish_text("BAN USER")))
    markup.row(KeyboardButton(stylish_text("UNBAN USER")), KeyboardButton(stylish_text("USERS")))
    markup.row(KeyboardButton(stylish_text("DATA")), KeyboardButton(stylish_text("PENDING USERS")))
    markup.row(KeyboardButton(stylish_text("TOTAL MESSAGES")), KeyboardButton(stylish_text("CHANGE UPI")))
    markup.row(KeyboardButton(stylish_text("CHANGE PRICE")), KeyboardButton(stylish_text("SET DM USERNAME")))
    markup.row(KeyboardButton(stylish_text("SET WELCOME")), KeyboardButton(stylish_text("CHANGE WELCOME IMAGE")))
    markup.row(KeyboardButton(stylish_text("SET HOW TO USE")), KeyboardButton(stylish_text("BOT ON")))
    markup.row(KeyboardButton(stylish_text("BOT OFF")), KeyboardButton(stylish_text("STATUS")))
    markup.row(KeyboardButton(stylish_text("SET BAN PRICE")), KeyboardButton(stylish_text("SET BAN FREE")))
    markup.row(KeyboardButton(stylish_text("HELP")), KeyboardButton(stylish_text("ABOUT")))
    return markup

# ============================================================
# BOT COMMANDS
# ============================================================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        uid = message.from_user.id
        username = message.from_user.username
        name = message.from_user.first_name

        user = register_user(uid, username, name)

        if user.get("banned", False):
            send_pe(message.chat.id, "You are banned!")
            return

        settings = load_settings()
        welcome_image = settings.get("welcome_image", "https://iili.io/C8DNTyQ.jpg")

        try:
            bot.send_photo(message.chat.id, photo=welcome_image)
        except:
            pass

        text = f"""
WELCOME TO AD BOT
USER: {name}
ID: {uid}
USERNAME: @{username or 'N/A'}
THIS BOT IS USED FOR RUNNING ADS IN CHEAP RATES
Add me to any group for advertisement!
DEVELOPER: @iflexzyann
"""
        if is_admin(uid):
            markup = get_admin_menu(uid)
        else:
            markup = get_user_menu(uid)

        send_pe(message.chat.id, text, reply_markup=markup)
    except Exception as e:
        print(f"Start error: {e}")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    uid = message.from_user.id
    text = """
HELP
1. START ADS - Start advertising
2. STOP ADS - Stop advertising
3. BUY SUBSCRIPTION - Get access
4. ADD DM IN ADS - Add your username
5. HOW TO USE - Guide
6. STATS - View stats
7. SUPPORT - Contact support
"""
    if is_admin(uid):
        markup = get_admin_menu(uid)
    else:
        markup = get_user_menu(uid)

    send_pe(message.chat.id, text, reply_markup=markup)

# ============================================================
# BAN CHECK - USER COMMAND
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("🔍 BAN CHECK") in m.text)
def ban_check_start(message):
    uid = message.from_user.id
    user = get_user(uid)

    if not user or user.get("banned", False):
        send_pe(message.chat.id, "🚫 You are banned!")
        return

    settings = load_settings()
    ban_price = settings.get("ban_price", 0)

    if ban_price > 0:
        user_paid = user.get("ban_paid", False)
        if not user_paid:
            text = f"""
🔍 BAN CHECK

💰 Price: Rs.{ban_price}
⚠️ You need to pay to use this feature!

💳 Pay and send screenshot to admin.
Contact: @iflexzyann
"""
            keyboard = [
                [make_green_button("💳 PAY NOW", callback=f"ban_pay_{uid}")],
                [make_green_button("📞 CONTACT", url="https://t.me/iflexzyann")]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            send_pe(message.chat.id, text, reply_markup=markup)
            return

    text = """
🔍 BAN CHECK

Send the UID you want to check:
Example: 5119402525
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_ban_check)


def process_ban_check(message):
    uid_input = message.text.strip()
    user_id = message.from_user.id

    if not uid_input.isdigit():
        send_pe(message.chat.id, "❌ Invalid UID! Send only numbers.")
        return

    try:
        url = f"https://crownx-premium-bancheck.vercel.app/baninfo?uid={uid_input}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            account_id = data.get('account_id', 'N/A')
            nickname = data.get('nickname', 'N/A')
            level = data.get('level', 'N/A')
            region = data.get('region', 'N/A')
            liked = data.get('liked', 'N/A')
            create_at = data.get('create_at', 'N/A')
            last_login = data.get('last_login_at', 'N/A')
            ban_status = data.get('ban_info', {}).get('status', 'unknown')

            if "not banned" in ban_status.lower():
                status_emoji = "✅"
            elif "banned" in ban_status.lower():
                status_emoji = "❌"
            else:
                status_emoji = "⚠️"

            text = f"""
╔══════════════════════════════════╗
║        🔍 BAN CHECK RESULT        ║
╚══════════════════════════════════╝

📌 ACCOUNT INFO
├─ ID: {account_id}
├─ Name: {nickname}
├─ Level: {level}
├─ Region: {region}
├─ Likes: {liked}

📅 TIMESTAMPS
├─ Created: {create_at}
├─ Last Login: {last_login}

🔒 BAN STATUS
├─ {status_emoji} Status: {ban_status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👨‍💻 Developer: @iflexzyann
"""

            send_pe(message.chat.id, text)

        else:
            send_pe(message.chat.id, f"❌ API Error {response.status_code}\nPlease try again later.")

    except requests.exceptions.Timeout:
        send_pe(message.chat.id, "❌ Request timeout! API not responding.")
    except requests.exceptions.ConnectionError:
        send_pe(message.chat.id, "❌ Connection failed! Check your internet.")
    except Exception as e:
        send_pe(message.chat.id, f"❌ Error: {str(e)}")
        print(f"Ban check error: {e}")


# ============================================================
# BAN PAYMENT CALLBACK
# ============================================================

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_pay_"))
def handle_ban_pay(call):
    uid = int(call.data.split("_")[2])
    user_id = call.from_user.id

    if user_id != uid:
        send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    settings = load_settings()
    ban_price = settings.get("ban_price", 0)
    upi = settings.get("upi", "vanshx111@naviaxis")

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={ban_price}&cu=INR"

    text = f"""
💳 PAY FOR BAN CHECK

💰 Amount: Rs.{ban_price}
📱 UPI: {upi}

📸 Scan QR or pay and send screenshot.

After payment, admin will approve.
"""

    keyboard = [
        [make_green_button("✅ I HAVE PAID", callback=f"ban_paid_{uid}")],
        [make_green_button("📞 SUPPORT", url="https://t.me/iflexzyann")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        caption, cap_entities = build_message(text)
        bot.send_photo(call.message.chat.id, photo=qr_url, caption=caption, caption_entities=cap_entities, reply_markup=markup)
    except:
        send_pe(call.message.chat.id, text, reply_markup=markup)

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_paid_"))
def handle_ban_paid(call):
    uid = int(call.data.split("_")[2])
    user_id = call.from_user.id

    if user_id != uid:
        send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    send_pe(call.message.chat.id, "📸 Send payment screenshot to admin!")
    bot.answer_callback_query(call.id)

    admin_text = f"""
🔔 BAN CHECK PAYMENT

👤 User: {call.from_user.first_name}
🆔 ID: {uid}
💰 Amount: Rs.{load_settings().get('ban_price', 0)}
📱 Username: @{call.from_user.username or 'N/A'}
"""
    for admin in ADMIN_IDS:
        send_pe(admin, admin_text)


# ============================================================
# SET BAN PRICE - ADMIN
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("SET BAN PRICE") in m.text)
def set_ban_price_start(message):
    if not is_admin(message.from_user.id):
        return

    text = f"""
SET BAN PRICE
Current: Rs.{load_settings().get('ban_price', 0)}
0 = FREE
Send new price:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_set_ban_price)


def process_set_ban_price(message):
    if not is_admin(message.from_user.id):
        return

    try:
        price = int(message.text.strip())
        if price < 0:
            send_pe(message.chat.id, "Price cannot be negative!")
            return
        settings = load_settings()
        settings["ban_price"] = price
        save_settings(settings)
        send_pe(message.chat.id, f"Ban price set to Rs.{price}")
    except:
        send_pe(message.chat.id, "Invalid number!")


@bot.message_handler(func=lambda m: m.text and stylish_text("SET BAN FREE") in m.text)
def set_ban_free(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()
    settings["ban_price"] = 0
    save_settings(settings)
    send_pe(message.chat.id, "Ban check is now FREE for everyone!")


# ============================================================
# START ADS
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("START ADS") in m.text)
def start_ads_cmd(message):
    uid = message.from_user.id
    user = get_user(uid)

    if not user or user.get("banned", False):
        send_pe(message.chat.id, "You are banned!")
        return

    if not user.get("approved", False) and not is_admin(uid):
        send_pe(message.chat.id, "Buy subscription first!")
        return

    settings = load_settings()
    groups = load_groups()
    posts = load_posts()

    if not groups:
        send_pe(message.chat.id, "No groups added!")
        return

    if not posts:
        send_pe(message.chat.id, "No posts added!")
        return

    global sending_active, sending_thread

    if sending_active:
        send_pe(message.chat.id, "Ads already running!")
        return

    sending_active = True
    settings["sending_active"] = True
    save_settings(settings)

    sending_thread = threading.Thread(target=auto_send_loop, daemon=True)
    sending_thread.start()

    send_pe(message.chat.id, f"Ads started! Interval: {settings.get('send_interval', 6)} seconds")

@bot.message_handler(func=lambda m: m.text and stylish_text("STOP ADS") in m.text)
def stop_ads_cmd(message):
    global sending_active
    uid = message.from_user.id

    if not is_admin(uid):
        user = get_user(uid)
        if not user or not user.get("approved", False):
            send_pe(message.chat.id, "You are not approved!")
            return

    sending_active = False
    settings = load_settings()
    settings["sending_active"] = False
    save_settings(settings)

    send_pe(message.chat.id, "Ads stopped!")

# ============================================================
# ADD POST - MULTIPLE PHOTOS SUPPORT
# ============================================================

def can_add_post(uid):
    if is_admin(uid):
        return True
    user = get_user(uid)
    return bool(user and user.get("approved", False))

def save_album_post(mgid):
    msgs = album_buffers.pop(mgid, [])
    if not msgs:
        return
    photos = [m.photo[-1].file_id for m in msgs if m.photo]
    if not photos:
        return
    caption = next((m.caption for m in msgs if m.caption), None)
    text = caption or "Advertisement"
    uid = msgs[0].from_user.id
    posts = load_posts()
    posts.append({
        "text": text,
        "photos": photos,
        "added_by": uid,
        "user_id": uid,
        "added_at": datetime.now().isoformat()
    })
    save_posts(posts)
    send_pe(msgs[0].chat.id, f"Post added with {len(photos)} photos!")

@bot.message_handler(func=lambda m: m.text and stylish_text("ADD POST") in m.text)
def add_post_start(message):
    if not can_add_post(message.from_user.id):
        return

    text = """
ADD POST
Send text with multiple photos (up to 10)
Or send photo(s) with caption
Or send text only
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_add_post)

def process_add_post(message):
    if not can_add_post(message.from_user.id):
        return

    if message.media_group_id:
        mgid = message.media_group_id
        album_buffers.setdefault(mgid, []).append(message)
        if len(album_buffers[mgid]) == 1:
            threading.Timer(3.0, save_album_post, args=(mgid,)).start()
        return

    photos = []
    if message.photo:
        photos.append(message.photo[-1].file_id)

    text = message.caption or message.text or "Advertisement"

    posts = load_posts()
    posts.append({
        "text": text,
        "photos": photos,
        "added_by": message.from_user.id,
        "user_id": message.from_user.id,
        "added_at": datetime.now().isoformat()
    })
    save_posts(posts)

    send_pe(message.chat.id, f"Post added with {len(photos)} photos!")

# ============================================================
# DELETE POST
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("DELETE POST") in m.text)
def delete_post_start(message):
    if not is_admin(message.from_user.id):
        return

    posts = load_posts()
    if not posts:
        send_pe(message.chat.id, "No posts to delete!")
        return

    text = "DELETE POST\nSend post number to delete:\n\n"
    for i, post in enumerate(posts, 1):
        text += f"{i}. {post.get('text', '')[:50]}...\n"

    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_delete_post)

def process_delete_post(message):
    if not is_admin(message.from_user.id):
        return

    try:
        num = int(message.text.strip())
        posts = load_posts()
        if num < 1 or num > len(posts):
            send_pe(message.chat.id, "Invalid number!")
            return
        deleted = posts.pop(num - 1)
        save_posts(posts)
        send_pe(message.chat.id, f"Post {num} deleted!")
    except:
        send_pe(message.chat.id, "Invalid input!")

# ============================================================
# LIST POSTS
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("LIST POSTS") in m.text)
def list_posts(message):
    if not is_admin(message.from_user.id):
        return

    posts = load_posts()
    if not posts:
        send_pe(message.chat.id, "No posts!")
        return

    text = "POSTS\n"
    for i, post in enumerate(posts, 1):
        text += f"{i}. {post.get('text', '')[:50]}...\n"
        if post.get('photos'):
            text += f"   📷 {len(post.get('photos'))} photos\n"
        text += "\n"

    text += f"TOTAL: {len(posts)}"
    send_pe(message.chat.id, text)

# ============================================================
# CHECK ALL POSTS
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("CHECK ALL POSTS") in m.text)
def check_all_posts(message):
    if not is_admin(message.from_user.id):
        return

    posts = load_posts()
    if not posts:
        send_pe(message.chat.id, "No posts!")
        return

    text = "ALL POSTS\n"
    for i, post in enumerate(posts, 1):
        text += f"{i}. {post.get('text', '')[:50]}...\n"
        if post.get('photos'):
            text += f"   📷 {len(post.get('photos'))} photos\n"
        text += "\n"

    text += f"TOTAL: {len(posts)}"
    send_pe(message.chat.id, text)

# ============================================================
# BAN/UNBAN USER
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("BAN USER") in m.text)
def ban_user_start(message):
    if not is_admin(message.from_user.id):
        return

    text = """
BAN USER
Send USER ID to ban:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_ban_user)

def process_ban_user(message):
    if not is_admin(message.from_user.id):
        return

    try:
        uid = int(message.text.strip())
        user = get_user(uid)
        if not user:
            send_pe(message.chat.id, "User not found!")
            return
        update_user(uid, "banned", True)
        send_pe(message.chat.id, f"User {uid} banned!")
        try:
            send_pe(uid, "You have been banned!")
        except:
            pass
    except:
        send_pe(message.chat.id, "Invalid ID!")

@bot.message_handler(func=lambda m: m.text and stylish_text("UNBAN USER") in m.text)
def unban_user_start(message):
    if not is_admin(message.from_user.id):
        return

    text = """
UNBAN USER
Send USER ID to unban:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_unban_user)

def process_unban_user(message):
    if not is_admin(message.from_user.id):
        return

    try:
        uid = int(message.text.strip())
        user = get_user(uid)
        if not user:
            send_pe(message.chat.id, "User not found!")
            return
        update_user(uid, "banned", False)
        send_pe(message.chat.id, f"User {uid} unbanned!")
        try:
            send_pe(uid, "You have been unbanned!")
        except:
            pass
    except:
        send_pe(message.chat.id, "Invalid ID!")

# ============================================================
# BUY SUBSCRIPTION
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("BUY SUBSCRIPTION") in m.text)
def buy_subscription(message):
    uid = message.from_user.id
    user = get_user(uid)

    if user and user.get("approved", False):
        send_pe(message.chat.id, "You already have access!")
        return

    settings = load_settings()
    upi = settings.get("upi", "vanshx111@naviaxis")
    price = settings.get("price", 99)

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={price}&cu=INR"

    text = f"""
BUY SUBSCRIPTION
UPI: {upi}
AMOUNT: Rs.{price}
Scan QR to Pay
"""

    keyboard = [
        [make_green_button("I HAVE PAID", callback=f"paid_{uid}")],
        [make_green_button("SUPPORT", url="https://t.me/iflexzyann")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        caption, cap_entities = build_message(text)
        bot.send_photo(message.chat.id, photo=qr_url, caption=caption, caption_entities=cap_entities, reply_markup=markup)
    except:
        send_pe(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("paid_"))
def handle_paid(call):
    uid = int(call.data.split("_")[1])
    user_id = call.from_user.id

    if user_id != uid:
        send_pe(call.message.chat.id, "Not your request!")
        bot.answer_callback_query(call.id)
        return

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    pending = load_pending()
    pending[str(uid)] = {
        "user_id": uid,
        "username": call.from_user.username,
        "name": call.from_user.first_name,
        "status": "pending",
        "requested": datetime.now().isoformat()
    }
    save_pending(pending)

    send_pe(call.message.chat.id, "Send payment screenshot!")
    bot.register_next_step_handler(call.message, receive_payment_screenshot)
    bot.answer_callback_query(call.id)

def receive_payment_screenshot(message):
    uid = message.from_user.id

    if message.photo:
        file_id = message.photo[-1].file_id
        pending = load_pending()
        if str(uid) in pending:
            pending[str(uid)]["screenshot"] = file_id
            pending[str(uid)]["status"] = "pending"
            save_pending(pending)

        send_pe(message.chat.id, "Received! Waiting for admin.")

        admin_text = f"""
NEW PAYMENT
USER: {message.from_user.first_name}
ID: {uid}
USERNAME: @{message.from_user.username or 'N/A'}
"""
        keyboard = [
            [make_green_button("APPROVE", callback=f"admin_approve_{uid}")],
            [make_green_button("REJECT", callback=f"admin_reject_{uid}")]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        for admin in ADMIN_IDS:
            try:
                caption, cap_entities = build_message(admin_text)
                bot.send_photo(admin, photo=file_id, caption=caption, caption_entities=cap_entities, reply_markup=markup)
            except:
                send_pe(admin, admin_text, reply_markup=markup)
    else:
        send_pe(message.chat.id, "Send a photo!")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_approve_"))
def admin_approve(call):
    if not is_admin(call.from_user.id):
        send_pe(call.message.chat.id, "Unauthorized!")
        bot.answer_callback_query(call.id)
        return

    uid = int(call.data.split("_")[2])
    update_user(uid, "approved", True)
    pending = load_pending()
    if str(uid) in pending:
        del pending[str(uid)]
        save_pending(pending)

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    send_pe(call.message.chat.id, f"User {uid} approved!")
    try:
        send_pe(uid, "You now have access!")
    except:
        pass
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_reject_"))
def admin_reject(call):
    if not is_admin(call.from_user.id):
        send_pe(call.message.chat.id, "Unauthorized!")
        bot.answer_callback_query(call.id)
        return

    uid = int(call.data.split("_")[2])
    pending = load_pending()
    if str(uid) in pending:
        del pending[str(uid)]
        save_pending(pending)

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    send_pe(call.message.chat.id, f"User {uid} rejected!")
    try:
        send_pe(uid, "Payment not approved.")
    except:
        pass
    bot.answer_callback_query(call.id)

# ============================================================
# ADD DM IN ADS - PER-USER DM
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("ADD DM IN ADS") in m.text)
def add_dm_start(message):
    uid = message.from_user.id
    user = get_user(uid)

    if not user or user.get("banned", False):
        send_pe(message.chat.id, "You are banned!")
        return

    if not user.get("approved", False) and not is_admin(uid):
        send_pe(message.chat.id, "You are not approved!")
        return

    current = user.get("dm_username")
    text = f"""
ADD DM IN ADS
Current: @{current or 'Not Set'}
Send your Telegram username (without @):
Example: iflexzyann
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_add_dm)

def process_add_dm(message):
    uid = message.from_user.id
    username = message.text.strip().replace('@', '')

    update_user(uid, "dm_username", username)

    send_pe(message.chat.id, f"DM set to @{username}")

# ============================================================
# OTHER COMMANDS
# ============================================================

@bot.message_handler(func=lambda m: m.text and stylish_text("SET INTERVAL") in m.text)
def set_interval_start(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()
    text = f"""
SET INTERVAL
Current: {settings.get('send_interval', 6)} seconds
Min: 2 | Max: 600
Send new interval:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_set_interval)

def process_set_interval(message):
    if not is_admin(message.from_user.id):
        return

    try:
        interval = int(message.text.strip())
        if interval < 2 or interval > 600:
            send_pe(message.chat.id, "Min: 2 | Max: 600")
            return
        settings = load_settings()
        settings["send_interval"] = interval
        save_settings(settings)
        send_pe(message.chat.id, f"Interval set to {interval}s!")
    except:
        send_pe(message.chat.id, "Invalid number!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET POSTS PER CYCLE") in m.text)
def set_posts_per_cycle_start(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()
    text = f"""
SET POSTS PER CYCLE
Current: {settings.get('posts_per_cycle', 7)} posts
Min: 5 | Max: 15
Send new number:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_set_posts_per_cycle)

def process_set_posts_per_cycle(message):
    if not is_admin(message.from_user.id):
        return

    try:
        num = int(message.text.strip())
        if num < 5 or num > 15:
            send_pe(message.chat.id, "Min: 5 | Max: 15")
            return
        settings = load_settings()
        settings["posts_per_cycle"] = num
        save_settings(settings)
        send_pe(message.chat.id, f"Posts per cycle set to {num}!")
    except:
        send_pe(message.chat.id, "Invalid number!")

@bot.message_handler(func=lambda m: m.text and stylish_text("CHANGE WELCOME IMAGE") in m.text)
def change_welcome_image_start(message):
    if not is_admin(message.from_user.id):
        return

    text = """
CHANGE WELCOME IMAGE
Send a PHOTO or IMAGE URL
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_change_welcome_image)

def process_change_welcome_image(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()

    if message.photo:
        settings["welcome_image"] = message.photo[-1].file_id
        save_settings(settings)
        send_pe(message.chat.id, "Welcome image updated!")
    elif message.text and message.text.startswith("http"):
        settings["welcome_image"] = message.text.strip()
        save_settings(settings)
        send_pe(message.chat.id, "Welcome image URL updated!")
    else:
        send_pe(message.chat.id, "Send a photo or URL!")

@bot.message_handler(func=lambda m: m.text and stylish_text("DATA") in m.text)
def data_cmd(message):
    if not is_admin(message.from_user.id):
        return

    users = load_users()
    groups = load_groups()
    posts = load_posts()
    pending = load_pending()
    settings = load_settings()
    stats = load_stats()

    data = {
        "users": users,
        "groups": groups,
        "posts": posts,
        "pending": pending,
        "settings": settings,
        "stats": stats,
        "admins": ADMIN_IDS,
        "total_users": len(users),
        "total_groups": len(groups),
        "total_posts": len(posts),
        "total_messages": stats.get("total_messages", 0),
        "pending_users": len(pending),
        "total_admins": len(ADMIN_IDS),
        "generated": datetime.now().isoformat()
    }

    file_path = "bot_data.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    caption, cap_entities = build_message("Data Export")
    with open(file_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=caption, caption_entities=cap_entities)

@bot.message_handler(func=lambda m: m.text and stylish_text("USERS") in m.text)
def users_cmd(message):
    if not is_admin(message.from_user.id):
        return

    users = load_users()
    if not users:
        send_pe(message.chat.id, "No users!")
        return

    text = "USERS\n"
    for uid, data in users.items():
        status = "✅" if data.get("approved", False) else "⏳"
        banned = "🚫" if data.get("banned", False) else ""
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"• {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"

    text += f"TOTAL: {len(users)}"
    send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("PENDING USERS") in m.text)
def pending_users(message):
    if not is_admin(message.from_user.id):
        return

    pending = load_pending()
    if not pending:
        send_pe(message.chat.id, "No pending users!")
        return

    text = "PENDING USERS\n"
    for uid, data in pending.items():
        text += f"• {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')})\n"

    text += f"TOTAL: {len(pending)}"
    send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("TOTAL MESSAGES") in m.text)
def total_messages_cmd(message):
    if not is_admin(message.from_user.id):
        return

    stats = load_stats()
    send_pe(message.chat.id, f"Total Messages: {stats.get('total_messages', 0)}")

@bot.message_handler(func=lambda m: m.text and stylish_text("CHANGE UPI") in m.text)
def change_upi_start(message):
    if not is_admin(message.from_user.id):
        return

    text = f"""
CHANGE UPI
Current: {load_settings().get('upi', 'vanshx111@naviaxis')}
Send new UPI:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_change_upi)

def process_change_upi(message):
    if not is_admin(message.from_user.id):
        return

    upi = message.text.strip()
    settings = load_settings()
    settings["upi"] = upi
    save_settings(settings)
    send_pe(message.chat.id, f"UPI updated to {upi}!")

@bot.message_handler(func=lambda m: m.text and stylish_text("CHANGE PRICE") in m.text)
def change_price_start(message):
    if not is_admin(message.from_user.id):
        return

    text = f"""
CHANGE PRICE
Current: Rs.{load_settings().get('price', 99)}
Send new price:
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_change_price)

def process_change_price(message):
    if not is_admin(message.from_user.id):
        return

    try:
        price = int(message.text.strip())
        if price <= 0:
            send_pe(message.chat.id, "Price must be > 0!")
            return
        settings = load_settings()
        settings["price"] = price
        save_settings(settings)
        send_pe(message.chat.id, f"Price updated to Rs.{price}!")
    except:
        send_pe(message.chat.id, "Invalid number!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET DM USERNAME") in m.text)
def set_dm_start(message):
    if not is_admin(message.from_user.id):
        return

    text = f"""
SET DM USERNAME
Current: @{load_settings().get('dm_username', 'Not Set')}
Send new username (without @):
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_set_dm)

def process_set_dm(message):
    if not is_admin(message.from_user.id):
        return

    username = message.text.strip().replace('@', '')
    settings = load_settings()
    settings["dm_username"] = username
    save_settings(settings)
    send_pe(message.chat.id, f"DM set to @{username}!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET WELCOME") in m.text)
def set_welcome_start(message):
    if not is_admin(message.from_user.id):
        return

    text = """
SET WELCOME
Send PHOTO or TEXT for welcome
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_set_welcome)

def process_set_welcome(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()
    if message.photo:
        settings["welcome_image"] = message.photo[-1].file_id
        save_settings(settings)
        send_pe(message.chat.id, "Welcome image updated!")
    elif message.text:
        settings["welcome_text"] = message.text.strip()
        save_settings(settings)
        send_pe(message.chat.id, "Welcome text updated!")

@bot.message_handler(func=lambda m: m.text and stylish_text("SET HOW TO USE") in m.text)
def set_how_to_use_start(message):
    if not is_admin(message.from_user.id):
        return

    text = """
SET HOW TO USE
Send TEXT or VIDEO
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_set_how_to_use)

def process_set_how_to_use(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()
    if message.video:
        settings["how_to_use_video"] = message.video.file_id
        settings["how_to_use_text"] = message.caption or "Video Guide"
        save_settings(settings)
        send_pe(message.chat.id, "How to use video updated!")
    elif message.text:
        settings["how_to_use_text"] = message.text.strip()
        settings["how_to_use_video"] = None
        save_settings(settings)
        send_pe(message.chat.id, "How to use text updated!")

@bot.message_handler(func=lambda m: m.text and stylish_text("HOW TO USE") in m.text)
def how_to_use(message):
    settings = load_settings()
    video = settings.get("how_to_use_video", None)
    text = settings.get("how_to_use_text", "1. Add me to any group\n2. Click Start Ads\n3. Pay subscription\n4. Ads will run!")

    if video:
        try:
            caption, cap_entities = build_message(text)
            bot.send_video(message.chat.id, video=video, caption=caption, caption_entities=cap_entities)
        except:
            send_pe(message.chat.id, text)
    else:
        send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("STATS") in m.text)
def stats_cmd(message):
    uid = message.from_user.id
    user = get_user(uid)

    if user and user.get("banned", False):
        send_pe(message.chat.id, "You are banned!")
        return

    settings = load_settings()
    stats = load_stats()

    if is_admin(uid):
        text = f"""
STATS
GROUPS: {len(load_groups())}
POSTS: {len(load_posts())}
MESSAGES: {stats.get('total_messages', 0)}
INTERVAL: {settings.get('send_interval', 6)} sec
SENDING: {'ACTIVE' if settings.get('sending_active', False) else 'INACTIVE'}
DM: @{settings.get('dm_username', 'Not Set')}
"""
        send_pe(message.chat.id, text)
    else:
        text = f"""
STATS
MESSAGES: {stats.get('total_messages', 0)}
SENDING: {'ACTIVE' if settings.get('sending_active', False) else 'INACTIVE'}
"""
        send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("SUPPORT") in m.text)
def support_cmd(message):
    text = """
SUPPORT
DEVELOPER: @iflexzyann
Contact: @iflexzyann
"""
    markup = InlineKeyboardMarkup([
        [make_green_button("CONTACT SUPPORT", url="https://t.me/iflexzyann")]
    ])
    send_pe(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and stylish_text("ABOUT") in m.text)
def about_cmd(message):
    text = """
ABOUT
AD BOT
Run ads in groups easily!
DEVELOPER: @iflexzyann
"""
    send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("BOT ON") in m.text)
def bot_on_cmd(message):
    if not is_admin(message.from_user.id):
        return

    global sending_active
    settings = load_settings()
    if settings.get("sending_active", False):
        sending_active = True
        thread = threading.Thread(target=auto_send_loop, daemon=True)
        thread.start()
    send_pe(message.chat.id, "Bot is ONLINE!")

@bot.message_handler(func=lambda m: m.text and stylish_text("BOT OFF") in m.text)
def bot_off_cmd(message):
    if not is_admin(message.from_user.id):
        return

    global sending_active
    sending_active = False
    settings = load_settings()
    settings["sending_active"] = False
    save_settings(settings)
    send_pe(message.chat.id, "Bot is OFFLINE!")

@bot.message_handler(func=lambda m: m.text and stylish_text("STATUS") in m.text)
def status_admin(message):
    if not is_admin(message.from_user.id):
        return

    settings = load_settings()
    stats = load_stats()
    groups = load_groups()
    posts = load_posts()
    users = load_users()

    text = f"""
STATUS
BOT: {'ONLINE' if settings.get('sending_active', False) else 'OFFLINE'}
SENDING: {'ACTIVE' if settings.get('sending_active', False) else 'INACTIVE'}
INTERVAL: {settings.get('send_interval', 6)} sec
GROUPS: {len(groups)}
POSTS: {len(posts)}
USERS: {len(users)}
MESSAGES: {stats.get('total_messages', 0)}
DM: @{settings.get('dm_username', 'Not Set')}
UPI: {settings.get('upi', 'vanshx111@naviaxis')}
PRICE: Rs.{settings.get('price', 99)}
ADMINS: {len(ADMIN_IDS)}
"""
    send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("LIST GROUPS") in m.text)
def list_groups(message):
    if not is_admin(message.from_user.id):
        return

    groups = load_groups()
    if not groups:
        send_pe(message.chat.id, "No groups!")
        return

    text = "GROUPS\n"
    for gid in groups.keys():
        name = groups[gid].get("name", "Unknown")
        text += f"• {gid} ({name})\n"

    text += f"TOTAL: {len(groups)}"
    send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and stylish_text("ADD GROUP") in m.text)
def add_group_start(message):
    if not is_admin(message.from_user.id):
        return

    text = """
ADD GROUP
Send GROUP ID or add me to group
"""
    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_add_group)

def process_add_group(message):
    if not is_admin(message.from_user.id):
        return

    group_id = message.text.strip()
    if not group_id.startswith('-') and not group_id.startswith('@'):
        try:
            group_id = str(int(group_id))
        except:
            send_pe(message.chat.id, "Invalid group ID!")
            return

    groups = load_groups()
    if group_id in groups:
        send_pe(message.chat.id, "Group already added!")
        return

    groups[group_id] = {
        "added_by": message.from_user.id,
        "added_at": datetime.now().isoformat()
    }
    save_groups(groups)
    send_pe(message.chat.id, f"Group added: {group_id}")

@bot.message_handler(commands=['addgroup'])
def addgroup_cmd(message):
    if not is_admin(message.from_user.id):
        return

    if message.chat.type in ['group', 'supergroup']:
        group_id = str(message.chat.id)
        groups = load_groups()
        if group_id not in groups:
            groups[group_id] = {
                "added_by": message.from_user.id,
                "added_at": datetime.now().isoformat(),
                "name": message.chat.title
            }
            save_groups(groups)
            send_pe(message.chat.id, f"Group added!\nID: {group_id}")
        else:
            send_pe(message.chat.id, "Group already added!")
    else:
        send_pe(message.chat.id, "Only works in groups!")

@bot.message_handler(func=lambda m: m.text and stylish_text("REMOVE GROUP") in m.text)
def remove_group_start(message):
    if not is_admin(message.from_user.id):
        return

    groups = load_groups()
    if not groups:
        send_pe(message.chat.id, "No groups!")
        return

    text = "REMOVE GROUP\nSend GROUP ID:\n\n"
    for gid in groups.keys():
        text += f"• {gid}\n"

    send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_remove_group)

def process_remove_group(message):
    if not is_admin(message.from_user.id):
        return

    group_id = message.text.strip()
    groups = load_groups()
    if group_id not in groups:
        send_pe(message.chat.id, "Group not found!")
        return

    del groups[group_id]
    save_groups(groups)
    send_pe(message.chat.id, "Group removed!")

# ============================================================
# WELCOME NEW MEMBERS
# ============================================================

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    try:
        for member in message.new_chat_members:
            if member.id == bot.get_me().id:
                group_id = str(message.chat.id)
                groups = load_groups()
                if group_id not in groups:
                    groups[group_id] = {
                        "added_by": "BOT_ADDED",
                        "added_at": datetime.now().isoformat(),
                        "name": message.chat.title
                    }
                    save_groups(groups)

                    settings = load_settings()
                    welcome_image = settings.get("welcome_image", None)
                    welcome_text = f"""
Bot added to group!
GROUP: {message.chat.title}
ID: {group_id}
Add me to any group for advertisement!
Contact: @iflexzyann
"""
                    if welcome_image:
                        try:
                            caption, cap_entities = build_message(welcome_text)
                            bot.send_photo(message.chat.id, photo=welcome_image, caption=caption, caption_entities=cap_entities)
                        except:
                            send_pe(message.chat.id, welcome_text)
                    else:
                        send_pe(message.chat.id, welcome_text)
                return
    except Exception as e:
        print(f"Welcome error: {e}")

# ============================================================
# FLASK WEBHOOK
# ============================================================

@app.route('/', methods=['GET'])
def index():
    return "AD BOT is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
    except Exception as e:
        print(f"Webhook error: {e}")
    return '', 403

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("AD BOT Started!")
    print(f"Owner: {OWNER_ID}")
    print(f"Admins: {len(ADMIN_IDS)}")
    print(f"Users: {len(load_users())}")

    try:
        bot.remove_webhook()
        print("Webhook removed!")
    except Exception as e:
        print(f"Webhook remove error: {e}")

    try:
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if hostname:
            webhook_url = f"https://{hostname}/{BOT_TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"Webhook set: {webhook_url}")
        else:
            print("No hostname, using polling")
            bot.infinity_polling()
            exit()
    except Exception as e:
        print(f"Webhook error: {e}, falling back to polling")
        bot.infinity_polling()
        exit()

    app.run(host='0.0.0.0', port=PORT)