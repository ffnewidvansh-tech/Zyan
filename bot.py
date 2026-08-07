import os
import json
import time
import random
import requests
from datetime import datetime
from flask import Flask, request
from telebot import TeleBot, types
from telebot.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "8471373583"))
ADMIN_IDS = [OWNER_ID]
PORT = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    exit(1)

print("✅ Bot token loaded!")

bot = TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ============================================================
# FILES & DATA
# ============================================================
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
PENDING_FILE = "pending.json"
SETTINGS_FILE = "settings.json"

# Bot state
bot_active = True

# ============================================================
# TERA EMOJI MAPPING
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

# ============================================================
# GET RANDOM EMOJI ID
# ============================================================
def get_random_emoji_id():
    all_ids = []
    for ids in EMOJI_MAPPING.values():
        all_ids.extend(ids)
    for ids in FLAG_MAPPING.values():
        all_ids.append(ids)
    return random.choice(all_ids)

# ============================================================
# STYLISH TEXT
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
# EMOJI HELPERS
# ============================================================
def _utf16_len(ch: str) -> int:
    return len(ch.encode("utf-16-le")) // 2

def _utf16_len_str(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2

def _build_pe_entities(text: str):
    entities = []
    utf16_offset = 0
    total_utf16 = _utf16_len_str(text)
    
    if total_utf16 > 0:
        entities.append(MessageEntity(type="bold", offset=0, length=total_utf16))
    
    i = 0
    while i < len(text):
        ch = text[i]
        ch_len = _utf16_len(ch)
        
        if ch in EMOJI_MAPPING:
            eid = int(random.choice(EMOJI_MAPPING[ch]))
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=utf16_offset,
                length=ch_len,
                custom_emoji_id=eid
            ))
        elif ch in FLAG_MAPPING:
            eid = int(FLAG_MAPPING[ch])
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=utf16_offset,
                length=ch_len,
                custom_emoji_id=eid
            ))
        utf16_offset += ch_len
        i += 1
    
    return entities

def _send_pe(chat_id, text: str, reply_markup=None):
    try:
        entities = _build_pe_entities(text)
        return bot.send_message(chat_id, text, entities=entities, reply_markup=reply_markup, parse_mode=None)
    except:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)

def _send_pe_return(chat_id, text: str, reply_markup=None):
    try:
        entities = _build_pe_entities(text)
        return bot.send_message(chat_id, text, entities=entities, reply_markup=reply_markup, parse_mode=None)
    except:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)

# ============================================================
# SIRF GREEN BUTTONS (Fully Green - Like "I HAVE PAID")
# ============================================================
def make_green_button(text: str, callback: str = None, url: str = None):
    final_text = stylish_text(text)
    try:
        if callback:
            return InlineKeyboardButton(text=final_text, style="success", callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final_text, style="success", url=url)
        else:
            return InlineKeyboardButton(text=final_text, style="success")
    except:
        if callback:
            return InlineKeyboardButton(text=final_text, callback_data=callback)
        elif url:
            return InlineKeyboardButton(text=final_text, url=url)
        else:
            return InlineKeyboardButton(text=final_text)

# ============================================================
# DATA FUNCTIONS
# ============================================================
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    users = {
        "8471373583": {"id": 8471373583, "username": "iflexzyan", "name": "ZYAN", "joined": datetime.now().isoformat(), "uses": 0, "unlimited": True, "banned": False, "ban_paid": True},
    }
    save_users(users)
    return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_orders():
    return load_data(ORDERS_FILE)

def save_orders(orders):
    save_data(ORDERS_FILE, orders)

def load_pending():
    return load_data(PENDING_FILE)

def save_pending(pending):
    save_data(PENDING_FILE, pending)

def load_settings():
    default = {
        "price": 99,
        "upi": "vanshx111@naviaxis",
        "free_trial": True,
        "bot_name": "FF BAN BOT",
        "developer": "@iflexzyan",
        "support": "@iflexzyan",
        "welcome_image": "https://iili.io/C8DNTyQ.jpg",
        "token_text": "1️⃣ Open Free Fire\n2️⃣ Go to Settings\n3️⃣ Click Account\n4️⃣ Find Data Access\n5️⃣ Copy Token",
        "ban_price": 0
    }
    data = load_data(SETTINGS_FILE)
    for key, val in default.items():
        if key not in data:
            data[key] = val
    return data

def save_settings(settings):
    save_data(SETTINGS_FILE, settings)

# ============================================================
# HELPERS
# ============================================================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def register_user(user_id, username=None, first_name=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "id": user_id,
            "username": username,
            "name": first_name or "Unknown",
            "joined": datetime.now().isoformat(),
            "uses": 0,
            "unlimited": False,
            "banned": False,
            "ban_paid": False
        }
        save_users(users)
        notify_owner(f"✅ ɴᴇᴡ ᴜsᴇʀ ᴊᴏɪɴᴇᴅ!\n👤 ɪᴅ: {user_id}\n👾 @{username or 'N/A'}")
    return users[str(user_id)]

def get_user(user_id):
    users = load_users()
    return users.get(str(user_id))

def update_user(user_id, key, value):
    users = load_users()
    if str(user_id) in users:
        users[str(user_id)][key] = value
        save_users(users)

def notify_owner(msg):
    try:
        bot.send_message(OWNER_ID, msg)
    except:
        pass

# ============================================================
# STYLISH QR TEXT
# ============================================================
def get_stylish_qr_text(upi, price):
    stylish_emojis = ["⭐", "✨", "🔥", "💎", "👑", "💰", "💥", "🌟"]
    random_emoji = random.choice(stylish_emojis)
    
    text = f"""
{random_emoji} ═══《 💰 ᴘᴀʏᴍᴇɴᴛ ɪɴꜰᴏ 》═══ {random_emoji}

{random_emoji} 💳 ᴜᴘɪ: {upi}
{random_emoji} 💰 ᴀᴍᴏᴜɴᴛ: ʀs.{price}

{random_emoji} ═══════════════════════ {random_emoji}

{random_emoji} 📱 ꜱᴄᴀɴ Qʀ ᴛᴏ ᴘᴀʏ

{random_emoji} ═══════════════════════ {random_emoji}

`{upi}`

{random_emoji} 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
{random_emoji} ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴄʜᴏᴏꜱɪɴɢ ᴜꜱ! ⭐
"""
    return text

# ============================================================
# USER MENU - FULLY GREEN BUTTONS
# ============================================================
def get_user_menu(user_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton("🟢 BAN ACCOUNT"))
    markup.row(KeyboardButton("🟢 FREE TRIAL"), KeyboardButton("🟢 UNLIMITED"))
    markup.row(KeyboardButton("🟢 BAN CHECK"), KeyboardButton("🟢 HOW TO GET TOKEN"))
    markup.row(KeyboardButton("🟢 SUPPORT"), KeyboardButton("🟢 HELP"))
    markup.row(KeyboardButton("🟢 ABOUT"))
    return markup

# ============================================================
# ADMIN MENU - FULLY GREEN BUTTONS
# ============================================================
def get_admin_menu(user_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(KeyboardButton("🟢 BOT OFF"), KeyboardButton("🟢 BOT ON"))
    markup.row(KeyboardButton("🟢 ADMIN PANEL"), KeyboardButton("🟢 STATS"))
    markup.row(KeyboardButton("🟢 USERS"), KeyboardButton("🟢 DATA"))
    markup.row(KeyboardButton("🟢 CHECK ALL"), KeyboardButton("🟢 TOTAL ADMINS"))
    markup.row(KeyboardButton("🟢 PRICE"), KeyboardButton("🟢 UPI"))
    markup.row(KeyboardButton("🟢 ADD ADMIN"), KeyboardButton("🟢 ALL COMMANDS"))
    markup.row(KeyboardButton("🟢 HOW TO GET TOKEN"), KeyboardButton("🟢 BROADCAST"))
    markup.row(KeyboardButton("🟢 ALL BROADCAST"), KeyboardButton("🟢 SET WELCOME IMAGE"))
    markup.row(KeyboardButton("🟢 SET TOKEN TEXT"), KeyboardButton("🟢 ADD TOKEN VIDEO"))
    markup.row(KeyboardButton("🟢 SET BAN PRICE"), KeyboardButton("🟢 SET BAN FREE"))
    return markup

# ============================================================
# START COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        settings = load_settings()
        price = settings.get("price", 99)
        developer = settings.get("developer", "@iflexzyan")
        welcome_image = settings.get("welcome_image", "https://iili.io/C8DNTyQ.jpg")
        
        user = register_user(user_id, username, first_name)
        
        if user.get("banned", False):
            _send_pe(message.chat.id, f"❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return
        
        try:
            if welcome_image.startswith("http"):
                bot.send_photo(message.chat.id, photo=welcome_image)
            else:
                bot.send_photo(message.chat.id, photo=welcome_image)
        except:
            pass
        
        welcome_text = f"""
⭐ ═══《 🔥 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ғғ ʙᴀɴ ʙᴏᴛ 》═══ ⭐

⭐ 👤 ᴜsᴇʀ: {first_name}
⭐ 🆔 ɪᴅ: {user_id}
⭐ 👾 ᴜsᴇʀɴᴀᴍᴇ: @{username or 'N/A'}

⭐ ═══════════════════════ ⭐

⭐ 🎯 𝟷 ғʀᴇᴇ ᴛʀɪᴀʟ - ʙᴀɴ 𝟷 ᴀᴄᴄᴏᴜɴᴛ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss - ʀs.{price}
⭐ 🔍 BAN CHECK - Check UID status

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: {developer}

⭐ ═══════════════════════ ⭐
"""
        
        if is_admin(user_id):
            markup = get_admin_menu(user_id)
        else:
            markup = get_user_menu(user_id)
        
        _send_pe(message.chat.id, welcome_text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Start error: {e}")

# ============================================================
# BAN ACCOUNT - FULL
# ============================================================
user_tokens = {}

@bot.message_handler(func=lambda m: m.text == "🟢 BAN ACCOUNT" or stylish_text("🟢 BAN ACCOUNT") in m.text)
def ban_account_start(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if not user or user.get("banned", False):
            _send_pe(message.chat.id, f"❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return
        
        if not user.get("unlimited", False):
            uses = user.get("uses", 0)
            if uses >= 1:
                _send_pe(message.chat.id, f"⚠️ ғʀᴇᴇ ᴛʀɪᴀʟ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 99)}")
                send_payment_qr(message.chat.id)
                return
        
        _send_pe(message.chat.id, f"🔑 sᴇɴᴅ ᴛʜᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ:")
        bot.register_next_step_handler(message, get_ban_token)
    except Exception as e:
        print(f"❌ Ban start error: {e}")

def get_ban_token(message):
    try:
        user_id = message.from_user.id
        token = message.text.strip()
        
        if len(token) < 30:
            _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ!")
            return
        
        user_tokens[user_id] = token
        
        keyboard = [
            [make_green_button("YES, I AM 100% SURE", callback=f"confirm_ban_{user_id}")],
            [make_green_button("NO, CANCEL", callback="cancel_ban")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        _send_pe(message.chat.id, f"""
⚠️ ═══《 ⚠️ ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ 》═══ ⚠️

⚠️ ᴀʀᴇ ʏᴏᴜ 𝟷𝟶𝟶% sᴜʀᴇ?

⚠️ ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!

⚠️ ═══════════════════════ ⚠️
""", reply_markup=markup)
    except Exception as e:
        print(f"❌ Get token error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("confirm_ban_"))
def confirm_ban_callback(call):
    try:
        user_id = int(call.data.split("_")[2])
        if call.from_user.id != user_id:
            _send_pe(call.message.chat.id, f"❌ ɴᴏᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ!")
            bot.answer_callback_query(call.id)
            return
        
        token = user_tokens.get(user_id)
        if not token:
            _send_pe(call.message.chat.id, f"❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        msg = _send_pe_return(call.message.chat.id, f"⏳ ʙᴀɴɴɪɴɢ...")
        
        try:
            url = f"https://ffidbanapi.vercel.app/ban-account?access-token={token}&key=ANIXH"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            account_id = data.get('id', 'N/A')
            account_name = data.get('name', 'N/A')
            account_uid = data.get('uid', 'N/A')
            status = data.get('status', 'UNKNOWN')
            
            is_banned = "BANNED" in str(status).upper()
            
            bot.delete_message(call.message.chat.id, msg.message_id)
            
            if is_banned:
                user = get_user(user_id)
                if user:
                    uses = user.get("uses", 0) + 1
                    update_user(user_id, "uses", uses)
                
                result_text = f"""
⭐ ═══《 ✅ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴɴᴇᴅ 》═══ ⭐

⭐ 🎯 ʙᴀɴ sᴜᴄᴄᴇssғᴜʟ!

⭐ ═══════════════════════ ⭐

⭐ 🆔 ɪᴅ: {account_id}
⭐ 👤 ɴᴀᴍᴇ: {account_name}
⭐ 🔢 ᴜɪᴅ: {account_uid}

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
                keyboard = [
                    [make_green_button("BAN ANOTHER", callback="ban_another")],
                    [make_green_button("GET UNLIMITED", callback="get_unlimited")]
                ]
                markup = InlineKeyboardMarkup(keyboard)
                _send_pe(call.message.chat.id, result_text, reply_markup=markup)
                notify_owner(f"✅ ʙᴀɴɴᴇᴅ!\n👤 {user_id}\n🔢 {account_uid}")
            else:
                result_text = f"""
⭐ ═══《 ❌ ʙᴀɴ ғᴀɪʟᴇᴅ 》═══ ⭐

⭐ ❌ ɴᴏᴛ ʙᴀɴɴᴇᴅ!

⭐ 🆔 ɪᴅ: {account_id}
⭐ 👤 ɴᴀᴍᴇ: {account_name}
⭐ 🔢 ᴜɪᴅ: {account_uid}
⭐ 📌 sᴛᴀᴛᴜs: {status}

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
"""
                _send_pe(call.message.chat.id, result_text)
        except Exception as e:
            bot.delete_message(call.message.chat.id, msg.message_id)
            _send_pe(call.message.chat.id, f"❌ ᴇʀʀᴏʀ: {str(e)}")
        
        user_tokens.pop(user_id, None)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Confirm ban error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_ban")
def cancel_ban_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    _send_pe(call.message.chat.id, f"✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
    user_tokens.pop(call.from_user.id, None)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "ban_another")
def ban_another_callback(call):
    try:
        user_id = call.from_user.id
        user = get_user(user_id)
        if not user or user.get("banned", False):
            _send_pe(call.message.chat.id, f"❌ ʙᴀɴɴᴇᴅ!")
            return
        if not user.get("unlimited", False):
            uses = user.get("uses", 0)
            if uses >= 1:
                _send_pe(call.message.chat.id, f"⚠️ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 99)}")
                send_payment_qr(call.message.chat.id)
                bot.answer_callback_query(call.id)
                return
        _send_pe(call.message.chat.id, f"🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ:")
        bot.register_next_step_handler(call.message, get_ban_token)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Ban another error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "get_unlimited")
def get_unlimited_callback(call):
    try:
        send_payment_qr(call.message.chat.id)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Get unlimited error: {e}")

# ============================================================
# BAN CHECK - FULL DATA (A to Z)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🟢 BAN CHECK" or stylish_text("🟢 BAN CHECK") in m.text)
def ban_check_start(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not user or user.get("banned", False):
        _send_pe(message.chat.id, f"❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
        return

    settings = load_settings()
    ban_price = settings.get("ban_price", 0)

    if ban_price > 0:
        user_paid = user.get("ban_paid", False)
        if not user_paid:
            text = f"""
⭐ ═══《 🔍 BAN CHECK 》═══ ⭐

⭐ 💰 Price: Rs.{ban_price}
⭐ ⚠️ You need to pay to use this!

⭐ 💳 Pay & send screenshot to admin.
⭐ 👨‍💻 @iflexzyan
"""
            keyboard = [
                [make_green_button("💳 PAY NOW", callback=f"ban_pay_{user_id}")],
                [make_green_button("📞 CONTACT", url="https://t.me/iflexzyan")]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            _send_pe(message.chat.id, text, reply_markup=markup)
            return

    text = """
⭐ ═══《 🔍 BAN CHECK 》═══ ⭐

⭐ Send the UID you want to check:
⭐ Example: 5119402525

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)
    bot.register_next_step_handler(message, process_ban_check)

def process_ban_check(message):
    uid_input = message.text.strip()
    user_id = message.from_user.id

    if not uid_input.isdigit():
        _send_pe(message.chat.id, f"❌ Invalid UID! Send only numbers.")
        return

    try:
        url = f"https://crownx-premium-bancheck.vercel.app/baninfo?uid={uid_input}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Agar list hai toh pehla element lo
            if isinstance(data, list):
                if len(data) > 0:
                    data = data[0]
                else:
                    _send_pe(message.chat.id, f"❌ No data found!")
                    return

            # ===== SABA DATA EXTRACT KARO (A to Z) =====
            account_id = data.get('account_id', 'N/A')
            account_type = data.get('account_type', 'N/A')
            nickname = data.get('nickname', 'N/A')
            region = data.get('region', 'N/A')
            level = data.get('level', 'N/A')
            liked = data.get('liked', 'N/A')
            create_at = data.get('create_at', 'N/A')
            last_login_at = data.get('last_login_at', 'N/A')
            release_version = data.get('release_version', 'N/A')
            prime_level = data.get('prime_level', 'N/A')
            is_pc_player = data.get('is_pc_player', 'N/A')
            
            # Ban info
            ban_info = data.get('ban_info', {})
            if isinstance(ban_info, dict):
                ban_status = ban_info.get('status', 'unknown')
                ban_reason = ban_info.get('reason', 'N/A')
                ban_time = ban_info.get('ban_time', 'N/A')
                ban_duration = ban_info.get('duration', 'N/A')
            else:
                ban_status = str(ban_info) if ban_info else 'unknown'
                ban_reason = 'N/A'
                ban_time = 'N/A'
                ban_duration = 'N/A'

            # Extra data jo bhi ho
            extra_keys = []
            for key in data.keys():
                if key not in ['account_id', 'account_type', 'nickname', 'region', 'level', 'liked', 'create_at', 'last_login_at', 'release_version', 'prime_level', 'is_pc_player', 'ban_info']:
                    extra_keys.append(f"⭐ ├─ {key}: {data[key]}")

            if "not banned" in ban_status.lower():
                status_emoji = "✅"
            elif "banned" in ban_status.lower():
                status_emoji = "❌"
            else:
                status_emoji = "⚠️"

            # ===== BUILD RESPONSE =====
            text = f"""
⭐ ═══《 🔍 BAN CHECK RESULT 》═══ ⭐

⭐ 📌 ACCOUNT INFO
⭐ ├─ ID: {account_id}
⭐ ├─ Type: {account_type}
⭐ ├─ Name: {nickname}
⭐ ├─ Region: {region}
⭐ ├─ Level: {level}
⭐ ├─ Likes: {liked}

⭐ 📅 TIMESTAMPS
⭐ ├─ Created: {create_at}
⭐ ├─ Last Login: {last_login_at}

⭐ ⚙️ OTHER INFO
⭐ ├─ Release Version: {release_version}
⭐ ├─ Prime Level: {prime_level}
⭐ ├─ PC Player: {is_pc_player}
"""

            # Extra keys
            if extra_keys:
                text += f"\n⭐ 📌 EXTRA DATA\n"
                for extra in extra_keys:
                    text += f"{extra}\n"

            text += f"""
⭐ 🔒 BAN STATUS
⭐ ├─ {status_emoji} Status: {ban_status}
⭐ ├─ Reason: {ban_reason}
⭐ ├─ Ban Time: {ban_time}
⭐ ├─ Duration: {ban_duration}

⭐ ═══════════════════════ ⭐
⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
            _send_pe(message.chat.id, text)
        else:
            _send_pe(message.chat.id, f"❌ API Error {response.status_code}")
    except Exception as e:
        _send_pe(message.chat.id, f"❌ Error: {str(e)}")

# ============================================================
# BAN CHECK PAYMENT
# ============================================================

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_pay_"))
def handle_ban_pay(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, f"❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    settings = load_settings()
    ban_price = settings.get("ban_price", 0)
    upi = settings.get("upi", "vanshx111@naviaxis")

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={ban_price}&cu=INR"

    text = get_stylish_qr_text(upi, ban_price)

    keyboard = [
        [make_green_button("✅ I HAVE PAID", callback=f"ban_paid_{user_id}")],
        [make_green_button("📞 SUPPORT", url="https://t.me/iflexzyan")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        bot.send_photo(call.message.chat.id, photo=qr_url, caption=text, reply_markup=markup)
    except:
        _send_pe(call.message.chat.id, text, reply_markup=markup)

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_paid_"))
def handle_ban_paid(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, f"❌ Not your request!")
        bot.answer_callback_query(call.id)
        return

    _send_pe(call.message.chat.id, f"📸 Send payment screenshot to admin!")
    bot.answer_callback_query(call.id)

    admin_text = f"""
⭐ ═══《 🔔 BAN CHECK PAYMENT 》═══ ⭐

⭐ 👤 User: {call.from_user.first_name}
⭐ 🆔 ID: {user_id}
⭐ 💰 Amount: Rs.{load_settings().get('ban_price', 0)}
⭐ 📱 Username: @{call.from_user.username or 'N/A'}

⭐ ═══════════════════════ ⭐
"""
    for admin in ADMIN_IDS:
        _send_pe(admin, admin_text)

# ============================================================
# SET BAN PRICE & FREE - ADMIN
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🟢 SET BAN PRICE" or stylish_text("🟢 SET BAN PRICE") in m.text)
def set_ban_price_start(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"💰 Send new ban price (0 = FREE):")
    bot.register_next_step_handler(message, process_set_ban_price)

def process_set_ban_price(message):
    if not is_admin(message.from_user.id):
        return
    try:
        price = int(message.text.strip())
        if price < 0:
            _send_pe(message.chat.id, f"❌ Price cannot be negative!")
            return
        settings = load_settings()
        settings["ban_price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ Ban price set to Rs.{price}")
    except:
        _send_pe(message.chat.id, f"❌ Invalid number!")

@bot.message_handler(func=lambda m: m.text == "🟢 SET BAN FREE" or stylish_text("🟢 SET BAN FREE") in m.text)
def set_ban_free(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    settings["ban_price"] = 0
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ Ban check is now FREE for everyone! 🎉")

# ============================================================
# PAYMENT SYSTEM
# ============================================================

def send_payment_qr(chat_id):
    try:
        settings = load_settings()
        upi = settings.get("upi", "vanshx111@naviaxis")
        price = settings.get("price", 99)
        
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={price}&cu=INR"
        
        text = get_stylish_qr_text(upi, price)
        
        keyboard = [
            [make_green_button("I HAVE PAID", callback=f"paid_{chat_id}")],
            [make_green_button("CANCEL", callback="cancel_payment")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        try:
            bot.send_photo(chat_id, photo=qr_url, caption=text, reply_markup=markup)
        except:
            _send_pe(chat_id, text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Payment QR error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("paid_"))
def handle_paid(call):
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        
        pending = load_pending()
        pending[str(user_id)] = {
            "user_id": user_id,
            "username": call.from_user.username,
            "name": call.from_user.first_name,
            "status": "pending",
            "requested": datetime.now().isoformat()
        }
        save_pending(pending)
        
        _send_pe(chat_id, f"📸 sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ!")
        bot.register_next_step_handler(call.message, receive_payment_screenshot)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Paid callback error: {e}")

def receive_payment_screenshot(message):
    try:
        user_id = message.from_user.id
        
        if message.photo:
            file_id = message.photo[-1].file_id
            pending = load_pending()
            if str(user_id) in pending:
                pending[str(user_id)]["screenshot"] = file_id
                pending[str(user_id)]["status"] = "pending"
                save_pending(pending)
            
            _send_pe(message.chat.id, f"✅ ʀᴇᴄᴇɪᴠᴇᴅ!\n⏳ ᴡᴀɪᴛ ғᴏʀ ᴀᴅᴍɪɴ")
            
            admin_text = f"""
⭐ ═══《 💰 ɴᴇᴡ ᴘᴀʏᴍᴇɴᴛ 》═══ ⭐

⭐ 👤 {message.from_user.first_name}
⭐ 🆔 {user_id}
⭐ 👾 @{message.from_user.username or 'N/A'}

⭐ ═══════════════════════ ⭐
"""
            keyboard = [
                [make_green_button("✅ ᴀᴘᴘʀᴏᴠᴇ", callback=f"admin_approve_{user_id}")],
                [make_green_button("❌ ᴅɪsᴀᴘᴘʀᴏᴠᴇ", callback=f"admin_disapprove_{user_id}")]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            
            for admin in ADMIN_IDS:
                try:
                    bot.send_photo(admin, photo=file_id, caption=admin_text, reply_markup=markup)
                except:
                    bot.send_message(admin, admin_text, reply_markup=markup)
        else:
            _send_pe(message.chat.id, f"❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ!")
    except Exception as e:
        print(f"❌ Screenshot receive error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_approve_"))
def admin_approve_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, f"❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        
        user_id = int(call.data.split("_")[2])
        
        update_user(user_id, "unlimited", True)
        update_user(user_id, "uses", 0)
        update_user(user_id, "ban_paid", True)
        
        pending = load_pending()
        if str(user_id) in pending:
            del pending[str(user_id)]
            save_pending(pending)
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        _send_pe(call.message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴀᴘᴘʀᴏᴠᴇᴅ!")
        
        try:
            bot.send_message(user_id, f"""
🎉 ᴄᴏɴɢʀᴀᴛs! ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss! 🎉

⭐ ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ʙᴀɴ ᴀɴʏ ᴀᴄᴄᴏᴜɴᴛ!
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴄʜᴏᴏꜱɪɴɢ ᴜꜱ!

⭐ @ɪꜰʟᴇxᴢʏᴀɴ ⭐
""")
        except:
            pass
        
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin approve error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_disapprove_"))
def admin_disapprove_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, f"❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        
        user_id = int(call.data.split("_")[2])
        
        pending = load_pending()
        if str(user_id) in pending:
            del pending[str(user_id)]
            save_pending(pending)
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        _send_pe(call.message.chat.id, f"❌ ᴜsᴇʀ {user_id} ʀᴇᴊᴇᴄᴛᴇᴅ!")
        
        try:
            bot.send_message(user_id, f"❌ ᴘᴀʏᴍᴇɴᴛ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.")
        except:
            pass
        
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin disapprove error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_payment")
def cancel_payment_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    _send_pe(call.message.chat.id, f"✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
    bot.answer_callback_query(call.id)

# ============================================================
# OTHER USER COMMANDS
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🟢 FREE TRIAL" or stylish_text("🟢 FREE TRIAL") in m.text)
def free_trial_cmd(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if not user:
            _send_pe(message.chat.id, f"❌ /start ғɪʀsᴛ!")
            return
        
        if user.get("unlimited", False):
            _send_pe(message.chat.id, f"✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!")
            return
        
        uses = user.get("uses", 0)
        if uses >= 1:
            _send_pe(message.chat.id, f"⚠️ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 99)}")
            send_payment_qr(message.chat.id)
            return
        
        _send_pe(message.chat.id, f"""
🆓 ғʀᴇᴇ ᴛʀɪᴀʟ ᴀᴄᴛɪᴠᴀᴛᴇᴅ! 🎯

🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ ᴛᴏ ʙᴀɴ:
1️⃣ ᴄʟɪᴄᴋ "BAN ACCOUNT"
2️⃣ sᴇɴᴅ ᴛᴏᴋᴇɴ
3️⃣ ᴄᴏɴғɪʀᴍ

⭐ @ɪꜰʟᴇxᴢʏᴀɴ ⭐
""")
    except Exception as e:
        print(f"❌ Free trial error: {e}")

@bot.message_handler(func=lambda m: m.text == "🟢 UNLIMITED" or stylish_text("🟢 UNLIMITED") in m.text)
def unlimited_cmd(message):
    try:
        user_id = message.from_user.id
        user = get_user(user_id)
        
        if user and user.get("unlimited", False):
            _send_pe(message.chat.id, f"✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!")
            return
        
        send_payment_qr(message.chat.id)
    except Exception as e:
        print(f"❌ Unlimited error: {e}")

@bot.message_handler(func=lambda m: m.text == "🟢 HOW TO GET TOKEN" or stylish_text("🟢 HOW TO GET TOKEN") in m.text)
def how_to_get_token(message):
    try:
        settings = load_settings()
        token_text = settings.get("token_text", "1️⃣ Open Free Fire\n2️⃣ Go to Settings\n3️⃣ Click Account\n4️⃣ Find Data Access\n5️⃣ Copy Token")
        
        _send_pe(message.chat.id, f"""
⭐ ═══《 🔑 ʜᴏᴡ ᴛᴏ ɢᴇᴛ ᴛᴏᴋᴇɴ 》═══ ⭐

⭐ {token_text}

⭐ ═══════════════════════ ⭐
""")
        
        if os.path.exists("token_video.mp4"):
            with open("token_video.mp4", "rb") as f:
                bot.send_video(message.chat.id, f, caption=f"⭐ ᴠɪᴅᴇᴏ ɢᴜɪᴅᴇ")
    except Exception as e:
        print(f"❌ How to get token error: {e}")

@bot.message_handler(func=lambda m: m.text == "🟢 SUPPORT" or stylish_text("🟢 SUPPORT") in m.text)
def support_cmd(message):
    try:
        settings = load_settings()
        support = settings.get("support", "@iflexzyan")
        
        text = f"""
⭐ ═══《 📞 sᴜᴘᴘᴏʀᴛ 》═══ ⭐

⭐ 👨‍💻 {support}

⭐ ғᴏʀ ᴀɴʏ ɪssᴜᴇ:
⭐ 📱 {support}

⭐ ═══════════════════════ ⭐
"""
        markup = InlineKeyboardMarkup([
            [make_green_button("CONTACT", url=f"https://t.me/{support.replace('@', '')}")]
        ])
        _send_pe(message.chat.id, text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Support error: {e}")

@bot.message_handler(func=lambda m: m.text == "🟢 HELP" or stylish_text("🟢 HELP") in m.text)
def help_cmd(message):
    try:
        user_id = message.from_user.id
        if is_admin(user_id):
            markup = get_admin_menu(user_id)
        else:
            markup = get_user_menu(user_id)
        
        help_text = f"""
⭐ ═══《 ❓ ʜᴇʟᴘ 》═══ ⭐

⭐ ʜᴏᴡ ᴛᴏ ᴜsᴇ:

⭐ 𝟷️⃣ ᴄʟɪᴄᴋ BAN ACCOUNT
⭐ 𝟸️⃣ sᴇɴᴅ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ
⭐ 𝟹️⃣ ᴄᴏɴғɪʀᴍ ʏᴇs
⭐ 𝟺️⃣ ᴀᴄᴄᴏᴜɴᴛ ɢᴇᴛs ʙᴀɴɴᴇᴅ!

⭐ ═══════════════════ ⭐

⭐ 🆓 ғʀᴇᴇ ᴛʀɪᴀʟ: 𝟷 ʙᴀɴ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ: ᴘᴀʏ & ɢᴇᴛ
⭐ 🔍 BAN CHECK: Check UID status

⭐ ═══════════════════ ⭐

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴ
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
        _send_pe(message.chat.id, help_text, reply_markup=markup)
    except Exception as e:
        print(f"❌ Help error: {e}")

@bot.message_handler(func=lambda m: m.text == "🟢 ABOUT" or stylish_text("🟢 ABOUT") in m.text)
def about_cmd(message):
    try:
        settings = load_settings()
        developer = settings.get("developer", "@iflexzyan")
        
        text = f"""
⭐ ═══《 ℹ️ ᴀʙᴏᴜᴛ 》═══ ⭐

⭐ 🤖 ғғ ʙᴀɴ ʙᴏᴛ

⭐ 🔫 ʙᴀɴ ғʀᴇᴇ ғɪʀᴇ ᴀᴄᴄᴏᴜɴᴛs
⭐ 🔍 BAN CHECK - UID status check
⭐ 💰 ᴘᴀʏ & ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ
⭐ 🆓 𝟷 ғʀᴇᴇ ᴛʀɪᴀʟ

⭐ 👨‍💻 {developer}
⭐ ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜꜱɪɴɢ ᴏᴜʀ ʙᴏᴛ! ⭐
"""
        _send_pe(message.chat.id, text)
    except Exception as e:
        print(f"❌ About error: {e}")

# ============================================================
# ADMIN COMMANDS (Buttons + Commands)
# ============================================================

@bot.message_handler(func=lambda m: m.text == "🟢 ADMIN PANEL" or stylish_text("🟢 ADMIN PANEL") in m.text)
def admin_panel_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = f"""
⭐ ═══《 👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ 》═══ ⭐

⭐ /approve ID - APPROVE
⭐ /disapprove ID - REJECT
⭐ /ban ID - BAN
⭐ /unban ID - UNBAN
⭐ /users - ALL USERS
⭐ /data - DOWNLOAD
⭐ /checkall - CHECK ALL
⭐ /totaladmins - ADMINS
⭐ /price <AMT> - CHANGE
⭐ /upi <UPI> - CHANGE
⭐ /developer <@> - CHANGE
⭐ /addadmin ID - ADD
⭐ /broadcastuser ID MSG - SEND
⭐ /allbroadcast MSG - ALL

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🟢 STATS" or stylish_text("🟢 STATS") in m.text)
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    orders = load_orders()
    pending = load_pending()
    settings = load_settings()
    text = f"""
⭐ ═══《 📊 sᴛᴀᴛs 》═══ ⭐

⭐ 👥 ᴜsᴇʀs: {len(users)}
⭐ 🔫 ʙᴀɴs: {len(orders)}
⭐ 💰 ᴘᴇɴᴅɪɴɢ: {len(pending)}
⭐ 💎 ᴜɴʟɪᴍɪᴛᴇᴅ: {sum(1 for u in users.values() if u.get('unlimited', False))}
⭐ 👑 ᴀᴅᴍɪɴs: {len(ADMIN_IDS)}
⭐ 💳 ᴘʀɪᴄᴇ: ʀs.{settings.get('price', 99)}
⭐ 🏦 ᴜᴘɪ: {settings.get('upi', 'vanshx111@naviaxis')}
⭐ 👨‍💻 {settings.get('developer', '@iflexzyan')}

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🟢 BOT ON" or stylish_text("🟢 BOT ON") in m.text)
def bot_on_btn(message):
    if not is_admin(message.from_user.id):
        return
    global bot_active
    bot_active = True
    _send_pe(message.chat.id, f"✅ 🟢 ʙᴏᴛ ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ!")

@bot.message_handler(func=lambda m: m.text == "🟢 BOT OFF" or stylish_text("🟢 BOT OFF") in m.text)
def bot_off_btn(message):
    if not is_admin(message.from_user.id):
        return
    global bot_active
    bot_active = False
    _send_pe(message.chat.id, f"✅ 🔴 ʙᴏᴛ ɪs ɴᴏᴡ ᴏғғʟɪɴᴇ!")

@bot.message_handler(func=lambda m: m.text == "🟢 USERS" or stylish_text("🟢 USERS") in m.text)
def users_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    text = f"⭐ ═══《 👥 ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🟢 DATA" or stylish_text("🟢 DATA") in m.text)
def data_cmd(message):
    if not is_admin(message.from_user.id):
        return
    data = {
        "users": load_users(),
        "orders": load_orders(),
        "pending": load_pending(),
        "settings": load_settings(),
        "admins": ADMIN_IDS,
        "generated": datetime.now().isoformat()
    }
    file_path = "bot_data.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    with open(file_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=f"⭐ 📥 ᴅᴀᴛᴀ ᴇxᴘᴏʀᴛ")

@bot.message_handler(func=lambda m: m.text == "🟢 CHECK ALL" or stylish_text("🟢 CHECK ALL") in m.text)
def check_all_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    if not users:
        _send_pe(message.chat.id, f"⭐ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ!")
        return
    text = f"⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🟢 TOTAL ADMINS" or stylish_text("🟢 TOTAL ADMINS") in m.text)
def total_admins_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = f"⭐ ═══《 👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs 》═══ ⭐\n\n"
    for admin_id in ADMIN_IDS:
        user = get_user(admin_id)
        if user:
            text += f"⭐ • {user.get('name', 'Unknown')} (@{user.get('username', 'N/A')}) - 🆔 {admin_id}\n"
        else:
            text += f"⭐ • 🆔 {admin_id}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(ADMIN_IDS)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🟢 PRICE" or stylish_text("🟢 PRICE") in m.text)
def price_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ 💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{load_settings().get('price', 99)}\n⭐ /price <ᴀᴍᴛ>")

@bot.message_handler(func=lambda m: m.text == "🟢 UPI" or stylish_text("🟢 UPI") in m.text)
def upi_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ 🏦 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('upi', 'vanshx111@naviaxis')}\n⭐ /upi <ɴᴇᴡ>")

@bot.message_handler(func=lambda m: m.text == "🟢 ADD ADMIN" or stylish_text("🟢 ADD ADMIN") in m.text)
def add_admin_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ /addadmin ɪᴅ")

@bot.message_handler(func=lambda m: m.text == "🟢 ALL COMMANDS" or stylish_text("🟢 ALL COMMANDS") in m.text)
def all_commands_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = f"""
⭐ ═══《 📋 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs 》═══ ⭐

⭐ /start - sᴛᴀʀᴛ ʙᴏᴛ
⭐ /help - ʜᴇʟᴘ ɢᴜɪᴅᴇ
⭐ /approve ID - ᴀᴘᴘʀᴏᴠᴇ
⭐ /disapprove ID - ʀᴇᴊᴇᴄᴛ
⭐ /ban ID - ʙᴀɴ
⭐ /unban ID - ᴜɴʙᴀɴ
⭐ /users - ᴀʟʟ ᴜsᴇʀs
⭐ /data - ᴅᴏᴡɴʟᴏᴀᴅ
⭐ /checkall - ᴄʜᴇᴄᴋ ᴀʟʟ
⭐ /totaladmins - ᴀᴅᴍɪɴs
⭐ /price <AMT> - ᴄʜᴀɴɢᴇ
⭐ /upi <UPI> - ᴄʜᴀɴɢᴇ
⭐ /developer <@> - ᴄʜᴀɴɢᴇ
⭐ /addadmin ID - ᴀᴅᴅ
⭐ /broadcastuser ID MSG - SEND
⭐ /allbroadcast MSG - ALL

⭐ ═══════════════════════ ⭐
"""
    _send_pe(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🟢 BROADCAST" or stylish_text("🟢 BROADCAST") in m.text)
def broadcast_btn_msg(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ /broadcastuser ɪᴅ ᴍsɢ")

@bot.message_handler(func=lambda m: m.text == "🟢 ALL BROADCAST" or stylish_text("🟢 ALL BROADCAST") in m.text)
def all_broadcast_btn_msg(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ /allbroadcast ᴍsɢ")

@bot.message_handler(func=lambda m: m.text == "🟢 SET WELCOME IMAGE" or stylish_text("🟢 SET WELCOME IMAGE") in m.text)
def set_welcome_image_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ɪᴍᴀɢᴇ ᴜʀʟ")
    bot.register_next_step_handler(message, save_welcome_image)

def save_welcome_image(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    if message.photo:
        settings["welcome_image"] = message.photo[-1].file_id
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ!")
    elif message.text and message.text.startswith("http"):
        settings["welcome_image"] = message.text.strip()
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜʀʟ ᴜᴘᴅᴀᴛᴇᴅ!")
    else:
        _send_pe(message.chat.id, f"❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴠᴀʟɪᴅ ᴜʀʟ!")

@bot.message_handler(func=lambda m: m.text == "🟢 SET TOKEN TEXT" or stylish_text("🟢 SET TOKEN TEXT") in m.text)
def set_token_text_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"⭐ sᴇɴᴅ ɴᴇᴡ ᴛᴏᴋᴇɴ ᴛᴇxᴛ")
    bot.register_next_step_handler(message, save_token_text)

def save_token_text(message):
    if not is_admin(message.from_user.id):
        return
    settings = load_settings()
    settings["token_text"] = message.text.strip()
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴛᴏᴋᴇɴ ᴛᴇxᴛ ᴜᴘᴅᴀᴛᴇᴅ!")

@bot.message_handler(func=lambda m: m.text == "🟢 ADD TOKEN VIDEO" or stylish_text("🟢 ADD TOKEN VIDEO") in m.text)
def add_token_video_btn(message):
    if not is_admin(message.from_user.id):
        return
    _send_pe(message.chat.id, f"📤 sᴇɴᴅ ᴠɪᴅᴇᴏ")
    bot.register_next_step_handler(message, save_token_video)

def save_token_video(message):
    if message.video:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("token_video.mp4", "wb") as f:
            f.write(downloaded_file)
        _send_pe(message.chat.id, f"✅ ᴠɪᴅᴇᴏ sᴀᴠᴇᴅ!")
    else:
        _send_pe(message.chat.id, f"❌ sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ!")

# ============================================================
# COMMAND HANDLERS (Admin Commands)
# ============================================================

@bot.message_handler(commands=['approve'])
def approve_user(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, f"❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"❌ /approve ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    update_user(user_id, "unlimited", True)
    update_user(user_id, "uses", 0)
    update_user(user_id, "ban_paid", True)
    pending = load_pending()
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_pending(pending)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴀᴘᴘʀᴏᴠᴇᴅ!")
    try:
        bot.send_message(user_id, f"🎉 ᴄᴏɴɢʀᴀᴛs! ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss!")
    except:
        pass

@bot.message_handler(commands=['disapprove'])
def disapprove_user(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, f"❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"❌ /disapprove ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    pending = load_pending()
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_pending(pending)
    _send_pe(message.chat.id, f"❌ ᴜsᴇʀ {user_id} ʀᴇᴊᴇᴄᴛᴇᴅ!")

@bot.message_handler(commands=['ban'])
def ban_user_cmd(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, f"❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"❌ /ban ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    update_user(user_id, "banned", True)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=['unban'])
def unban_user_cmd(message):
    if not is_admin(message.from_user.id):
        _send_pe(message.chat.id, f"❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"❌ /unban ID")
        return
    try:
        user_id = int(parts[1])
    except:
        _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
        return
    update_user(user_id, "banned", False)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴜɴʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=['users'])
def users_cmd_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    text = f"⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(commands=['data'])
def data_cmd_cmd(message):
    if not is_admin(message.from_user.id):
        return
    data = {
        "users": load_users(),
        "orders": load_orders(),
        "pending": load_pending(),
        "settings": load_settings(),
        "admins": ADMIN_IDS,
        "generated": datetime.now().isoformat()
    }
    file_path = "bot_data.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    with open(file_path, "rb") as f:
        bot.send_document(message.chat.id, f, caption=f"⭐ 📥 ᴅᴀᴛᴀ ᴇxᴘᴏʀᴛ")

@bot.message_handler(commands=['checkall'])
def checkall_cmd(message):
    if not is_admin(message.from_user.id):
        return
    users = load_users()
    if not users:
        _send_pe(message.chat.id, f"⭐ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ!")
        return
    text = f"⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for uid, data in users.items():
        status = "💎" if data.get("unlimited", False) else "🆓"
        banned = "🚫" if data.get("banned", False) else "✅"
        admin = "👑" if int(uid) in ADMIN_IDS else ""
        text += f"⭐ • {data.get('name', 'Unknown')} (@{data.get('username', 'N/A')}) - {status} {banned} {admin}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(commands=['totaladmins'])
def totaladmins_cmd(message):
    if not is_admin(message.from_user.id):
        return
    text = f"⭐ ═══《 👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs 》═══ ⭐\n\n"
    for admin_id in ADMIN_IDS:
        user = get_user(admin_id)
        if user:
            text += f"⭐ • {user.get('name', 'Unknown')} (@{user.get('username', 'N/A')}) - 🆔 {admin_id}\n"
        else:
            text += f"⭐ • 🆔 {admin_id}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(ADMIN_IDS)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(commands=['price'])
def price_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"⭐ 💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{load_settings().get('price', 99)}\n⭐ /price <AMT>")
        return
    try:
        price = int(parts[1])
        settings = load_settings()
        settings["price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ ᴘʀɪᴄᴇ sᴇᴛ ᴛᴏ ʀs.{price}")
    except:
        _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ!")

@bot.message_handler(commands=['upi'])
def upi_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"⭐ 🏦 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('upi', 'vanshx111@naviaxis')}\n⭐ /upi <NEW>")
        return
    upi = parts[1]
    settings = load_settings()
    settings["upi"] = upi
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴜᴘɪ sᴇᴛ ᴛᴏ {upi}")

@bot.message_handler(commands=['developer'])
def developer_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"⭐ 👨‍💻 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('developer', '@iflexzyan')}\n⭐ /developer <@>")
        return
    developer = parts[1]
    settings = load_settings()
    settings["developer"] = developer
    settings["support"] = developer
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴅᴇᴠᴇʟᴏᴘᴇʀ sᴇᴛ ᴛᴏ {developer}")

@bot.message_handler(commands=['addadmin'])
def add_admin_cmd(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        _send_pe(message.chat.id, f"❌ /addadmin ID")
        return
    try:
        user_id = int(parts[1])
        if user_id not in ADMIN_IDS:
            ADMIN_IDS.append(user_id)
            _send_pe(message.chat.id, f"✅ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ!")
        else:
            _send_pe(message.chat.id, f"⚠️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ!")
    except:
        _send_pe(message.chat.id, f"❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")

@bot.message_handler(commands=['broadcastuser'])
def broadcast_user(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        _send_pe(message.chat.id, f"❌ /broadcastuser ID MSG")
        return
    try:
        user_id = int(parts[1])
        msg = parts[2]
        bot.send_message(user_id, f"📢 {msg}")
        _send_pe(message.chat.id, f"✅ sᴇɴᴛ ᴛᴏ {user_id}!")
    except:
        _send_pe(message.chat.id, f"❌ ғᴀɪʟᴇᴅ!")

@bot.message_handler(commands=['allbroadcast'])
def all_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        _send_pe(message.chat.id, f"❌ /allbroadcast MSG")
        return
    msg = parts[1]
    users = load_users()
    sent = 0
    failed = 0
    _send_pe(message.chat.id, f"⏳ sᴇɴᴅɪɴɢ ᴛᴏ {len(users)} ᴜsᴇʀs...")
    for user_id in users.keys():
        try:
            bot.send_message(int(user_id), f"📢 {msg}")
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    _send_pe(message.chat.id, f"⭐ ᴄᴏᴍᴘʟᴇᴛᴇ!\n⭐ ᴛᴏᴛᴀʟ: {len(users)}\n⭐ sᴇɴᴛ: {sent}\n⭐ ғᴀɪʟᴇᴅ: {failed}")

# ============================================================
# FLASK WEBHOOK
# ============================================================

@app.route('/', methods=['GET'])
def index():
    return "✅ FF BAN BOT is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    return '', 403

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("✅ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ!")
    print(f"✅ ᴏᴡɴᴇʀ: {OWNER_ID}")
    print(f"✅ ᴜsᴇʀs: {len(load_users())}")
    print(f"✅ ᴀᴅᴍɪɴs: {len(ADMIN_IDS)}")
    
    try:
        bot.remove_webhook()
        print("✅ ᴡᴇʙʜᴏᴏᴋ ʀᴇᴍᴏᴠᴇᴅ!")
    except Exception as e:
        print(f"⚠️ {e}")
    
    try:
        hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        if hostname:
            webhook_url = f"https://{hostname}/{BOT_TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"✅ ᴡᴇʙʜᴏᴏᴋ sᴇᴛ: {webhook_url}")
        else:
            print("⚠️ ɴᴏ ʜᴏsᴛɴᴀᴍᴇ, ᴜsɪɴɢ ᴘᴏʟʟɪɴɢ")
            bot.infinity_polling()
            exit()
    except Exception as e:
        print(f"⚠️ {e}, ғᴀʟʟɪɴɢ ʙᴀᴄᴋ ᴛᴏ ᴘᴏʟʟɪɴɢ")
        bot.infinity_polling()
        exit()
    
    app.run(host='0.0.0.0', port=PORT)