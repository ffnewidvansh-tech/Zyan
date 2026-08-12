import os
import json
import time
import random
import io
import requests
import html as _html
from datetime import datetime
from io import BytesIO
from flask import Flask, request
from telebot import TeleBot, types
from telebot.types import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton

# ============================================================
# ENVIRONMENT
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "8471373583"))
ADMIN_IDS = [OWNER_ID, 8586849798]
PORT = int(os.environ.get("PORT", 10000))

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    exit(1)

bot = TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ============================================================
# FILES
# ============================================================
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
PENDING_FILE = "pending.json"
SETTINGS_FILE = "settings.json"
BANS_FILE = "bans.json"

# ============================================================
# APIS
# ============================================================
PLAYER_API   = "https://info.killersharmabot.online/player-info"
BANCHECK_API = "https://crownx-premium-bancheck.vercel.app/baninfo"
BAN_API      = "https://ffidbanapi.vercel.app/ban-account?access-token={token}&key=ANIXH"
IMAGE_BASE   = "https://ff.garena.com/images"

# ============================================================
# STYLISH TEXT + DIGITS
# ============================================================
def stylish_text(text: str) -> str:
    m = {'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ꜰ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ',
         'K':'ᴋ','L':'ʟ','M':'ᴍ','N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'ꜱ','T':'ᴛ',
         'U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ',
         'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ',
         'k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'ꜱ','t':'ᴛ',
         'u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'}
    return "".join(m.get(ch, ch) for ch in text)

DIGIT_MAP = str.maketrans("0123456789", "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫")
def stylish_digits(n):
    return str(n).translate(DIGIT_MAP)

# ============================================================
# PREMIUM EMOJI (custom emoji IDs - bold entities ke saath)
# ============================================================
EMOJI_MAPPING = {
    "✅": ["6246537187614005254","6246782404476803545","6010060634803148161","6010498532488778300"],
    "✔️": ["6246871001062185760","6010264538375525668","6010487760710800947"],
    "🔥": ["4956222745814762495","4956606007221421405","4956429969396859866","6086954744268460848"],
    "💥": ["6032673796530377389","4958479549265347295"],
    "⚡": ["5791970059597386804","6087079590377820415","6095843123252957701"],
    "❤️": ["5783157259152397008","5801084710343938087","6010280773351904888"],
    "💙": ["5780496071645991525","6104780447684757396"],
    "💚": ["5888789252493283486"],
    "💛": ["5840261097719148872"],
    "🧡": ["5840263144212529797"],
    "💜": ["5840265018655703965"],
    "🖤": ["5840266939932994956"],
    "⭐": ["6244496562752331516","5904618938578243567","6010193314932855525"],
    "🌟": ["6010156854955480259","6086924086791902713"],
    "✨": ["6010338729640596556","6010086134023985536","5801044672658805468"],
    "👑": ["5794422335599546668","6089003761496232797","6247039939305808563"],
    "💰": ["6089104607328342288","6086730718774300509","6086664791026307819"],
    "💵": ["6089140105233044310"],
    "💎": ["6086778246882399112","5791697221799907788"],
    "👍": ["6089313931149448495","4958626617535497157","4956582500865410174"],
    "👎": ["6088789257285988672"],
    "👏": ["6093744967304352336","4956582500865410174"],
    "😀": ["6093864814071780526","6093922327978840798"],
    "😂": ["5782741660936966676","5782746664573867142"],
    "😉": ["6089024570612781324"],
    "😊": ["5780690182692935276"],
    "😍": ["6010179687001625256"],
    "😘": ["6044373012566774137"],
    "😎": ["6032853480782172520","6044373012566774137"],
    "😢": ["5780793884678296697"],
    "😭": ["5783024321324651865"],
    "😠": ["6035355642829475999","6034843326245508065"],
    "😡": ["6035355642829475999"],
    "🤔": ["5782756916660802905","5783034045130610245","6093666528316625608"],
}
FLAG_MAPPING = {
    "🇮🇳": "5433601609076586221","🇺🇸": "5433865586356531140","🇬🇧": "5433827537241258614",
    "🇫🇷": "5433636707549331311","🇩🇪": "5433845881046578644","🇯🇵": "5434147542369579483",
    "🇷🇺": "5433674924168328689","🇧🇷": "5433825269498525925","🇵🇰": "5434064563601421981",
}

def _utf16_len(ch): return len(ch.encode("utf-16-le")) // 2
def _utf16_len_str(s): return len(s.encode("utf-16-le")) // 2

def _build_pe_entities(text):
    entities = []
    off = 0
    total = _utf16_len_str(text)
    if total > 0:
        entities.append(MessageEntity(type="bold", offset=0, length=total))
    i = 0
    while i < len(text):
        ch = text[i]
        cl = _utf16_len(ch)
        if ch in EMOJI_MAPPING:
            entities.append(MessageEntity(type="custom_emoji", offset=off, length=cl,
                                          custom_emoji_id=int(random.choice(EMOJI_MAPPING[ch]))))
        elif ch in FLAG_MAPPING:
            entities.append(MessageEntity(type="custom_emoji", offset=off, length=cl,
                                          custom_emoji_id=int(FLAG_MAPPING[ch])))
        off += cl
        i += 1
    return entities

def _send_pe(chat_id, text, reply_markup=None):
    try:
        return bot.send_message(chat_id, text, entities=_build_pe_entities(text),
                                reply_markup=reply_markup, parse_mode=None)
    except:
        return bot.send_message(chat_id, text, reply_markup=reply_markup)

# ============================================================
# FULLY GREEN BUTTONS (style=success - Bot API 9.4)
# ============================================================
def make_green_button(text, callback=None, url=None):
    label = stylish_text(text)
    if callback:
        return InlineKeyboardButton(text=label, style="success", callback_data=callback)
    if url:
        return InlineKeyboardButton(text=label, style="success", url=url)
    return InlineKeyboardButton(text=label, style="success")

# ============================================================
# DATA HELPERS
# ============================================================
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
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    users = {"8471373583": {"id": 8471373583, "username": "iflexzyan", "name": "ZYAN",
                            "joined": datetime.now().isoformat(), "uses": 0, "unlimited": True,
                            "banned": False, "ban_paid": True},
             "8586849798": {"id": 8586849798, "username": "iflexzyann", "name": "BINAM",
                            "joined": datetime.now().isoformat(), "uses": 0, "unlimited": True,
                            "banned": False, "ban_paid": True}}
    save_data(USERS_FILE, users)
    return users

def save_users(users): save_data(USERS_FILE, users)
def load_orders(): return load_data(ORDERS_FILE)
def save_orders(o): save_data(ORDERS_FILE, o)
def load_pending(): return load_data(PENDING_FILE)
def save_pending(p): save_data(PENDING_FILE, p)

def load_bans():
    d = load_data(BANS_FILE)
    return d if isinstance(d, list) else []

def save_bans(b): save_data(BANS_FILE, b)

DEFAULT_SETTINGS = {
    "price": 19,
    "upi": "vansh111@naviaxis",
    "free_trial": True,
    "bot_name": "FF BAN BOT",
    "developer": "@iflexzyann",
    "support": "@iflexzyann",
    "welcome_image": "AgACAgUAAxkBAAIPa2p20EWYzPwRIu4DLD1hiRORhz6HAAJFEWsbDyKwV6NcNMwHdU3hAQADAgADeAADPQQ",
    "token_text": "https://www.fftools.site/free-fire-token-generator",
    "ban_price": 0,
    "outfit_api": PLAYER_API,
}

def load_settings():
    d = load_data(SETTINGS_FILE)
    for k, v in DEFAULT_SETTINGS.items():
        if k not in d:
            d[k] = v
    return d

def save_settings(s): save_data(SETTINGS_FILE, s)

# ============================================================
# HELPERS
# ============================================================
def is_admin(uid): return uid in ADMIN_IDS

def register_user(user_id, username=None, first_name=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"id": user_id, "username": username, "name": first_name or "Unknown",
                               "joined": datetime.now().isoformat(), "uses": 0, "unlimited": False,
                               "banned": False, "ban_paid": False}
        save_users(users)
        notify_owner(f"✅ ɴᴇᴡ ᴜsᴇʀ!\n👤 ɪᴅ: {user_id}\n👾 @{username or 'N/A'}")
    return users[str(user_id)]

def get_user(user_id):
    return load_users().get(str(user_id))

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
# RED PROCESSING ANIMATION - CHOTE BOXES + STYLISH %
# ============================================================
def show_processing_animation(chat_id):
    steps = [
        ("🟥🟥⬜⬜⬜⬜⬜⬜", "𝟷𝟶%"),
        ("🟥🟥🟥🟥⬜⬜⬜⬜", "𝟹𝟶%"),
        ("🟥🟥🟥🟥🟥🟥⬜⬜", "𝟻𝟶%"),
        ("🟥🟥🟥🟥🟥🟥🟥⬜", "𝟽𝟻%"),
        ("🟥🟥🟥🟥🟥🟥🟥🟥", "𝟷𝟶𝟶%"),
    ]
    msg = bot.send_message(chat_id, f"🟥🟥🟥🟥🟥🟥🟥🟥\n\n🔴 {stylish_digits(0)}%")
    for boxes, percent in steps:
        time.sleep(0.4)
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id,
                                  text=f"{boxes}\n\n🔴 {percent}")
        except:
            pass
    return msg

# ============================================================
# SIRF JSON RESPONSE + .json FILE (koi extra text nahi)
# ============================================================
def send_json_response(chat_id, data, label):
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    if len(json_str) > 3500:
        json_str = json_str[:3500] + "\n...TRUNCATED..."
    json_str = _html.escape(json_str)
    try:
        bot.send_message(chat_id, f"<pre>{json_str}</pre>", parse_mode="HTML")
    except:
        _send_pe(chat_id, f"<code>{json_str}</code>")
    try:
        bio = BytesIO()
        bio.write(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"))
        bio.seek(0)
        bot.send_document(chat_id, bio, visible_file_name=f"{label}.json",
                          caption=f"📄 JSON - {label}")
    except Exception as e:
        print(f"❌ JSON file error: {e}")

# ============================================================
# PLAYER PHOTOS (banner / avatar / pet / outfit)
# ============================================================
def image_candidates(data):
    """API response se image URLs nikalo (graceful - jo mile wo try hoga)"""
    cands = []
    try:
        bi = data.get("basicInfo", {}) if isinstance(data, dict) else {}
        pi = data.get("profileInfo", {}) if isinstance(data, dict) else {}
        pet = data.get("petInfo", {}) if isinstance(data, dict) else {}
        if bi.get("bannerId"):
            cands.append(("🖼 BANNER", f"{IMAGE_BASE}/banner/{bi['bannerId']}.png",
                          bi.get("bannerName", "")))
        if bi.get("headPic"):
            cands.append(("👤 AVATAR", f"{IMAGE_BASE}/head/{bi['headPic']}.png", ""))
        if pi.get("avatarId"):
            cands.append(("👤 AVATAR", f"{IMAGE_BASE}/head/{pi['avatarId']}.png", ""))
        if pet.get("skinId"):
            cands.append(("🐾 PET", f"{IMAGE_BASE}/pet/{pet['skinId']}.png", ""))
        # outfit/suit id dhundho
        for section in [bi, pi, data]:
            if not isinstance(section, dict):
                continue
            for k, v in section.items():
                if ("outfit" in str(k).lower() or "suit" in str(k).lower()) and str(v).isdigit():
                    cands.append(("🎽 OUTFIT", f"{IMAGE_BASE}/outfit/{v}.png", ""))
    except:
        pass
    seen, out = set(), []
    for c in cands:
        if c[1] not in seen:
            seen.add(c[1])
            out.append(c)
    return out

def send_player_photos(chat_id, data):
    sent = 0
    for label, url, name in image_candidates(data):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 1000:
                cap = label + (f": {name}" if name else "")
                bot.send_photo(chat_id, io.BytesIO(r.content), caption=cap)
                sent += 1
        except:
            continue
    if sent == 0:
        try:
            _send_pe(chat_id, "⚠️ ᴘʜᴏᴛᴏ ʟᴏᴀᴅ ɴᴀʜɪ ʜᴜᴀ (ɪᴍᴀɢᴇ ᴄᴅɴ ʙʟᴏᴄᴋᴇᴅ ʜᴀɪ) - ᴊsᴏɴ ᴍᴇ ᴜʀʟ ᴄʜᴇᴄᴋ ᴋᴀʀᴏ")
        except:
            pass
    return sent

# ============================================================
# MENUS - SAB FULLY GREEN INLINE BUTTONS
# ============================================================
def user_menu_markup():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        make_green_button("BAN ACCOUNT", callback="menu_ban"),
        make_green_button("BAN CHECK", callback="menu_bancheck"),
        make_green_button("CHECK OUTFIT", callback="menu_outfit"),
        make_green_button("FREE TRIAL", callback="menu_trial"),
        make_green_button("UNLIMITED", callback="menu_unlimited"),
        make_green_button("HOW TO GET TOKEN", callback="menu_token"),
        make_green_button("SUPPORT", callback="menu_support"),
        make_green_button("HELP", callback="menu_help"),
        make_green_button("ABOUT", callback="menu_about"),
    )
    return kb

def admin_menu_markup():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        make_green_button("ADMIN PANEL", callback="adm_panel"),
        make_green_button("STATS", callback="adm_stats"),
        make_green_button("USERS", callback="adm_users"),
        make_green_button("DATA", callback="adm_data"),
        make_green_button("CHECK ALL", callback="adm_checkall"),
        make_green_button("TOTAL ADMINS", callback="adm_totaladmins"),
        make_green_button("TOTAL BANNED", callback="adm_totalbanned"),
        make_green_button("CHECK ALL BANNED", callback="adm_checkbanned"),
        make_green_button("PRICE", callback="adm_price"),
        make_green_button("UPI", callback="adm_upi"),
        make_green_button("ADD ADMIN", callback="adm_addadmin"),
        make_green_button("ALL COMMANDS", callback="adm_commands"),
        make_green_button("BROADCAST", callback="adm_broadcast"),
        make_green_button("ALL BROADCAST", callback="adm_allbroadcast"),
        make_green_button("SET WELCOME IMAGE", callback="adm_welimg"),
        make_green_button("SET TOKEN TEXT", callback="adm_tokentext"),
        make_green_button("ADD TOKEN VIDEO", callback="adm_tokenvideo"),
        make_green_button("SET BAN PRICE", callback="adm_banprice"),
        make_green_button("SET BAN FREE", callback="adm_banfree"),
        make_green_button("SET OUTFIT API", callback="adm_outfitapi"),
    )
    return kb

def show_menu(chat_id, user_id):
    kb = admin_menu_markup() if is_admin(user_id) else user_menu_markup()
    try:
        bot.send_message(chat_id, stylish_text("─── ⋆⋅☆⋅⋆ ───\nᴍᴀɪɴ ᴍᴇɴᴜ\n─── ⋆⋅☆⋅⋆ ───"), reply_markup=kb)
    except:
        bot.send_message(chat_id, "ᴍᴀɪɴ ᴍᴇɴᴜ", reply_markup=kb)

# ============================================================
# START
# ============================================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    try:
        user_id = message.from_user.id
        settings = load_settings()
        price = settings.get("price", 19)
        developer = settings.get("developer", "@iflexzyann")
        welcome_image = settings.get("welcome_image")
        user = register_user(user_id, message.from_user.username, message.from_user.first_name)
        if user.get("banned", False):
            _send_pe(message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
            return
        try:
            if welcome_image:
                bot.send_photo(message.chat.id, photo=welcome_image)
        except:
            pass
        welcome_text = f"""
⭐ ═══《 🔥 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ғғ ʙᴀɴ ʙᴏᴛ 》═══ ⭐

⭐ 👤 ᴜsᴇʀ: {message.from_user.first_name}
⭐ 🆔 ɪᴅ: {user_id}
⭐ 👾 ᴜsᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'N/A'}

⭐ ═══════════════════════ ⭐

⭐ 🎯 𝟷 ғʀᴇᴇ ᴛʀɪᴀʟ - ʙᴀɴ 𝟷 ᴀᴄᴄᴏᴜɴᴛ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss - ʀs.{price}
⭐ 🔍 BAN CHECK - Check UID status
⭐ 🎽 CHECK OUTFIT - Outfit info + photos

⭐ ═══════════════════════ ⭐

⭐ 👨‍💻 {developer}

⭐ ═══════════════════════ ⭐
"""
        _send_pe(message.chat.id, welcome_text)
        show_menu(message.chat.id, user_id)
    except Exception as e:
        print(f"❌ Start error: {e}")

# ============================================================
# USER CALLBACKS
# ============================================================
@bot.callback_query_handler(func=lambda c: c.data == "menu_ban")
def cb_ban(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user or user.get("banned", False):
        _send_pe(call.message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
        bot.answer_callback_query(call.id)
        return
    if not user.get("unlimited", False) and user.get("uses", 0) >= 1:
        _send_pe(call.message.chat.id, f"⚠️ ғʀᴇᴇ ᴛʀɪᴀʟ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 19)}")
        send_payment_qr(call.message.chat.id)
        bot.answer_callback_query(call.id)
        return
    _send_pe(call.message.chat.id, "🔑 sᴇɴᴅ ᴛʜᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ:")
    bot.register_next_step_handler(call.message, get_ban_token)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_bancheck")
def cb_bancheck(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user or user.get("banned", False):
        _send_pe(call.message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
        bot.answer_callback_query(call.id)
        return
    settings = load_settings()
    if settings.get("ban_price", 0) > 0 and not user.get("ban_paid", False):
        kb = InlineKeyboardMarkup([
            [make_green_button("PAY NOW", callback=f"ban_pay_{user_id}")],
            [make_green_button("CONTACT", url=f"https://t.me/iflexzyann")]
        ])
        _send_pe(call.message.chat.id, f"""
⭐ ═══《 🔍 BAN CHECK 》═══ ⭐

⭐ 💰 Price: Rs.{settings.get('ban_price', 0)}
⭐ ⚠️ Pay karke use karo!

⭐ 💳 Pay & send screenshot to admin.
⭐ 👨‍💻 {settings.get('support', '@iflexzyann')}
""", reply_markup=kb)
        bot.answer_callback_query(call.id)
        return
    _send_pe(call.message.chat.id, """
⭐ ═══《 🔍 BAN CHECK 》═══ ⭐

⭐ Send the UID you want to check:
⭐ Example: 5119402525

⭐ ═══════════════════════ ⭐
""")
    bot.register_next_step_handler(call.message, process_ban_check)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_outfit")
def cb_outfit(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user or user.get("banned", False):
        _send_pe(call.message.chat.id, "❌ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ!")
        bot.answer_callback_query(call.id)
        return
    _send_pe(call.message.chat.id, """
⭐ ═══《 🎽 ᴄʜᴇᴄᴋ ᴏᴜᴛғɪᴛ 》═══ ⭐

⭐ Send the UID you want to check:
⭐ Example: 1972629696

⭐ 🖼 Banner + outfit photos bhi aayenge

⭐ ═══════════════════════ ⭐
""")
    bot.register_next_step_handler(call.message, process_outfit_check)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_trial")
def cb_trial(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    if not user:
        _send_pe(call.message.chat.id, "❌ /start ғɪʀsᴛ!")
        bot.answer_callback_query(call.id)
        return
    if user.get("unlimited", False):
        _send_pe(call.message.chat.id, "✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!")
        bot.answer_callback_query(call.id)
        return
    if user.get("uses", 0) >= 1:
        _send_pe(call.message.chat.id, f"⚠️ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 19)}")
        send_payment_qr(call.message.chat.id)
        bot.answer_callback_query(call.id)
        return
    _send_pe(call.message.chat.id, """
🆓 ғʀᴇᴇ ᴛʀɪᴀʟ ᴀᴄᴛɪᴠᴀᴛᴇᴅ! 🎯

🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ ᴛᴏ ʙᴀɴ:
1️⃣ ᴄʟɪᴄᴋ BAN ACCOUNT
2️⃣ sᴇɴᴅ ᴛᴏᴋᴇɴ
3️⃣ ᴄᴏɴғɪʀᴍ

⭐ @ɪꜰʟᴇxᴢʏᴀɴɴ ⭐
""")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_unlimited")
def cb_unlimited(call):
    user = get_user(call.from_user.id)
    if user and user.get("unlimited", False):
        _send_pe(call.message.chat.id, "✅ ᴀʟʀᴇᴀᴅʏ ᴜɴʟɪᴍɪᴛᴇᴅ!")
        bot.answer_callback_query(call.id)
        return
    send_payment_qr(call.message.chat.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_token")
def cb_token(call):
    settings = load_settings()
    _send_pe(call.message.chat.id, f"""
⭐ ═══《 🔑 ʜᴏᴡ ᴛᴏ ɢᴇᴛ ᴛᴏᴋᴇɴ 》═══ ⭐

⭐ {settings.get('token_text')}

⭐ ═══════════════════════ ⭐
""")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_support")
def cb_support(call):
    settings = load_settings()
    support = settings.get("support", "@iflexzyann")
    kb = InlineKeyboardMarkup([[make_green_button("CONTACT", url=f"https://t.me/{support.replace('@', '')}")]])
    _send_pe(call.message.chat.id, f"""
⭐ ═══《 📞 sᴜᴘᴘᴏʀᴛ 》═══ ⭐

⭐ 👨‍💻 {support}

⭐ ғᴏʀ ᴀɴʏ ɪssᴜᴇ:
⭐ 📱 {support}

⭐ ═══════════════════════ ⭐
""", reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_help")
def cb_help(call):
    _send_pe(call.message.chat.id, """
⭐ ═══《 ❓ ʜᴇʟᴘ 》═══ ⭐

⭐ 𝟷️⃣ ᴄʟɪᴄᴋ BAN ACCOUNT
⭐ 𝟸️⃣ sᴇɴᴅ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ
⭐ 𝟹️⃣ ᴄᴏɴғɪʀᴍ ʏᴇs
⭐ 𝟺️⃣ ᴀᴄᴄᴏᴜɴᴛ ɢᴇᴛs ʙᴀɴɴᴇᴅ!

⭐ 🆓 ғʀᴇᴇ ᴛʀɪᴀʟ: 𝟷 ʙᴀɴ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ: ᴘᴀʏ & ɢᴇᴛ
⭐ 🔍 BAN CHECK: Check UID status
⭐ 🎽 CHECK OUTFIT: Outfit + photos

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴɴ
""")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "menu_about")
def cb_about(call):
    settings = load_settings()
    _send_pe(call.message.chat.id, f"""
⭐ ═══《 ℹ️ ᴀʙᴏᴜᴛ 》═══ ⭐

⭐ 🤖 ғғ ʙᴀɴ ʙᴏᴛ

⭐ 🔫 ʙᴀɴ ғʀᴇᴇ ғɪʀᴇ ᴀᴄᴄᴏᴜɴᴛs
⭐ 🔍 BAN CHECK - UID status check
⭐ 🎽 CHECK OUTFIT - Outfit info + photos
⭐ 💰 ᴘᴀʏ & ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ
⭐ 🆓 𝟷 ғʀᴇᴇ ᴛʀɪᴀʟ

⭐ 👨‍💻 {settings.get('developer', '@iflexzyann')}
""")
    bot.answer_callback_query(call.id)

# ============================================================
# BAN ACCOUNT FLOW (SAB GREEN BUTTONS)
# ============================================================
user_tokens = {}

def get_ban_token(message):
    try:
        token = message.text.strip()
        if len(token) < 30:
            _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ!")
            return
        user_tokens[message.from_user.id] = token
        kb = InlineKeyboardMarkup([
            [make_green_button("YES, I AM 100% SURE", callback=f"confirm_ban_{message.from_user.id}")],
            [make_green_button("NO, CANCEL", callback="cancel_ban")]
        ])
        _send_pe(message.chat.id, """
⚠️ ═══《 ⚠️ ᴄᴏɴғɪʀᴍᴀᴛɪᴏɴ 》═══ ⚠️

⚠️ ᴀʀᴇ ʏᴏᴜ 𝟷𝟶𝟶% sᴜʀᴇ?

⚠️ ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ!

⚠️ ═══════════════════════ ⚠️
""", reply_markup=kb)
    except Exception as e:
        print(f"❌ Get token error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("confirm_ban_"))
def confirm_ban_callback(call):
    try:
        user_id = int(call.data.split("_")[2])
        if call.from_user.id != user_id:
            _send_pe(call.message.chat.id, "❌ ɴᴏᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ!")
            bot.answer_callback_query(call.id)
            return
        token = user_tokens.get(user_id)
        if not token:
            _send_pe(call.message.chat.id, "❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        anim = show_processing_animation(call.message.chat.id)
        try:
            r = requests.get(BAN_API.format(token=token), timeout=30)
            data = r.json()
            account_id = data.get('id', 'N/A')
            account_name = data.get('name', 'N/A')
            account_uid = data.get('uid', 'N/A')
            status = data.get('status', 'UNKNOWN')
            is_banned = "BANNED" in str(status).upper()
            try:
                bot.delete_message(call.message.chat.id, anim.message_id)
            except:
                pass
            if is_banned:
                user = get_user(user_id)
                if user:
                    update_user(user_id, "uses", user.get("uses", 0) + 1)
                bans = load_bans()
                bans.append({"uid": account_uid, "name": account_name, "account_id": account_id,
                             "status": status, "by_user": user_id, "time": datetime.now().isoformat()})
                save_bans(bans)
                kb = InlineKeyboardMarkup([
                    [make_green_button("BAN ANOTHER", callback="ban_another")],
                    [make_green_button("GET UNLIMITED", callback="get_unlimited")]
                ])
                _send_pe(call.message.chat.id, f"""
⭐ ═══《 ✅ ᴀᴄᴄᴏᴜɴᴛ ʙᴀɴɴᴇᴅ 》═══ ⭐

⭐ 🎯 ʙᴀɴ sᴜᴄᴄᴇssғᴜʟ!

⭐ 🆔 ɪᴅ: {account_id}
⭐ 👤 ɴᴀᴍᴇ: {account_name}
⭐ 🔢 ᴜɪᴅ: {account_uid}

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴɴ
""", reply_markup=kb)
                notify_owner(f"✅ ʙᴀɴɴᴇᴅ!\n👤 {user_id}\n🔢 {account_uid}")
            else:
                _send_pe(call.message.chat.id, f"""
⭐ ═══《 ❌ ʙᴀɴ ғᴀɪʟᴇᴅ 》═══ ⭐

⭐ ❌ ɴᴏᴛ ʙᴀɴɴᴇᴅ!

⭐ 🆔 ɪᴅ: {account_id}
⭐ 👤 ɴᴀᴍᴇ: {account_name}
⭐ 🔢 ᴜɪᴅ: {account_uid}
⭐ 📌 sᴛᴀᴛᴜs: {status}

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴɴ
""")
        except Exception as e:
            try:
                bot.delete_message(call.message.chat.id, anim.message_id)
            except:
                pass
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
    _send_pe(call.message.chat.id, "✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
    user_tokens.pop(call.from_user.id, None)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "ban_another")
def ban_another_callback(call):
    try:
        user_id = call.from_user.id
        user = get_user(user_id)
        if not user or user.get("banned", False):
            _send_pe(call.message.chat.id, "❌ ʙᴀɴɴᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        if not user.get("unlimited", False) and user.get("uses", 0) >= 1:
            _send_pe(call.message.chat.id, f"⚠️ ᴜsᴇᴅ!\n💰 ᴘᴀʏ ʀs.{load_settings().get('price', 19)}")
            send_payment_qr(call.message.chat.id)
            bot.answer_callback_query(call.id)
            return
        _send_pe(call.message.chat.id, "🔑 sᴇɴᴅ ᴛᴏᴋᴇɴ:")
        bot.register_next_step_handler(call.message, get_ban_token)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Ban another error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "get_unlimited")
def get_unlimited_callback(call):
    send_payment_qr(call.message.chat.id)
    bot.answer_callback_query(call.id)

# ============================================================
# BAN CHECK FLOW (SIRF JSON)
# ============================================================
def process_ban_check(message):
    uid_input = message.text.strip()
    if not uid_input.isdigit():
        _send_pe(message.chat.id, "❌ Invalid UID! Send only numbers.")
        return
    anim = show_processing_animation(message.chat.id)
    try:
        r = requests.get(f"{BANCHECK_API}?uid={uid_input}", timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                data = data[0] if len(data) > 0 else {"error": "No data"}
            try:
                bot.delete_message(message.chat.id, anim.message_id)
            except:
                pass
            send_json_response(message.chat.id, data, f"ban_check_{uid_input}")
        else:
            try:
                bot.delete_message(message.chat.id, anim.message_id)
            except:
                pass
            _send_pe(message.chat.id, f"❌ API Error {r.status_code}")
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, anim.message_id)
        except:
            pass
        _send_pe(message.chat.id, f"❌ Error: {str(e)}")

# ============================================================
# CHECK OUTFIT FLOW - JSON + BANNER/OUTFIT PHOTOS
# ============================================================
def build_api_url(api, uid):
    if "{uid}" in api:
        return api.replace("{uid}", uid)
    sep = "&" if "?" in api else "?"
    return f"{api}{sep}uid={uid}"

def process_outfit_check(message):
    uid_input = message.text.strip()
    if not uid_input.isdigit():
        _send_pe(message.chat.id, "❌ Invalid UID! Send only numbers.")
        return
    anim = show_processing_animation(message.chat.id)
    try:
        settings = load_settings()
        api = settings.get("outfit_api") or PLAYER_API
        r = requests.get(build_api_url(api, uid_input), timeout=15)
        if r.status_code == 200:
            data = r.json()
            # nested "data" normalize
            if isinstance(data, dict) and isinstance(data.get("data"), dict) and \
               ("basicInfo" in data["data"] or "profileInfo" in data["data"]):
                data = data["data"]
            if isinstance(data, list):
                data = data[0] if len(data) > 0 else {"error": "No data"}
            try:
                bot.delete_message(message.chat.id, anim.message_id)
            except:
                pass
            send_json_response(message.chat.id, data, f"outfit_{uid_input}")
            send_player_photos(message.chat.id, data)
        else:
            try:
                bot.delete_message(message.chat.id, anim.message_id)
            except:
                pass
            _send_pe(message.chat.id, f"❌ API Error {r.status_code}")
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, anim.message_id)
        except:
            pass
        _send_pe(message.chat.id, f"❌ Error: {str(e)}")

# ============================================================
# PAYMENT SYSTEM
# ============================================================
def get_stylish_qr_text(upi, price):
    e = random.choice(["⭐", "✨", "🔥", "💎", "👑", "💰", "💥"])
    return f"""
{e} ═══《 💰 ᴘᴀʏᴍᴇɴᴛ ɪɴꜰᴏ 》═══ {e}

{e} 💳 ᴜᴘɪ: {upi}
{e} 💰 ᴀᴍᴏᴜɴᴛ: ʀs.{price}

{e} 📱 ꜱᴄᴀɴ Qʀ ᴛᴏ ᴘᴀʏ

`{upi}`

{e} 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴɴ
{e} ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴄʜᴏᴏꜱɪɴɢ ᴜꜱ! ⭐
"""

def send_payment_qr(chat_id):
    try:
        settings = load_settings()
        upi = settings.get("upi", "vansh111@naviaxis")
        price = settings.get("price", 19)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={price}&cu=INR"
        kb = InlineKeyboardMarkup([
            [make_green_button("I HAVE PAID", callback=f"paid_{chat_id}")],
            [make_green_button("CANCEL", callback="cancel_payment")]
        ])
        try:
            bot.send_photo(chat_id, photo=qr_url, caption=get_stylish_qr_text(upi, price), reply_markup=kb)
        except:
            _send_pe(chat_id, get_stylish_qr_text(upi, price), reply_markup=kb)
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
        pending[str(user_id)] = {"user_id": user_id, "username": call.from_user.username,
                                 "name": call.from_user.first_name, "status": "pending",
                                 "requested": datetime.now().isoformat()}
        save_pending(pending)
        _send_pe(chat_id, "📸 sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ!")
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
                save_pending(pending)
            _send_pe(message.chat.id, "✅ ʀᴇᴄᴇɪᴠᴇᴅ!\n⏳ ᴡᴀɪᴛ ғᴏʀ ᴀᴅᴍɪɴ")
            kb = InlineKeyboardMarkup([
                [make_green_button("APPROVE", callback=f"admin_approve_{user_id}")],
                [make_green_button("DISAPPROVE", callback=f"admin_disapprove_{user_id}")]
            ])
            admin_text = f"""
⭐ ═══《 💰 ɴᴇᴡ ᴘᴀʏᴍᴇɴᴛ 》═══ ⭐

⭐ 👤 {message.from_user.first_name}
⭐ 🆔 {user_id}
⭐ 👾 @{message.from_user.username or 'N/A'}
"""
            for admin in ADMIN_IDS:
                try:
                    bot.send_photo(admin, photo=file_id, caption=admin_text, reply_markup=kb)
                except:
                    bot.send_message(admin, admin_text, reply_markup=kb)
        else:
            _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ!")
    except Exception as e:
        print(f"❌ Screenshot receive error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_approve_"))
def admin_approve_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
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
            bot.send_message(user_id, "🎉 ᴄᴏɴɢʀᴀᴛs! ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss! 🎉\n\n⭐ @ɪꜰʟᴇxᴢʏᴀɴɴ ⭐")
        except:
            pass
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin approve error: {e}")

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("admin_disapprove_"))
def admin_disapprove_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
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
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin disapprove error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "cancel_payment")
def cancel_payment_callback(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    _send_pe(call.message.chat.id, "✅ ᴄᴀɴᴄᴇʟʟᴇᴅ!")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_pay_"))
def handle_ban_pay(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return
    settings = load_settings()
    price = settings.get("ban_price", 0)
    upi = settings.get("upi", "vansh111@naviaxis")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={upi}&am={price}&cu=INR"
    kb = InlineKeyboardMarkup([
        [make_green_button("I HAVE PAID", callback=f"ban_paid_{user_id}")],
        [make_green_button("CONTACT", url="https://t.me/iflexzyann")]
    ])
    try:
        bot.send_photo(call.message.chat.id, photo=qr_url, caption=get_stylish_qr_text(upi, price), reply_markup=kb)
    except:
        _send_pe(call.message.chat.id, get_stylish_qr_text(upi, price), reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("ban_paid_"))
def handle_ban_paid(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        _send_pe(call.message.chat.id, "❌ Not your request!")
        bot.answer_callback_query(call.id)
        return
    _send_pe(call.message.chat.id, "📸 Send payment screenshot to admin!")
    bot.answer_callback_query(call.id)
    for admin in ADMIN_IDS:
        _send_pe(admin, f"""
⭐ ═══《 🔔 BAN CHECK PAYMENT 》═══ ⭐

⭐ 👤 {call.from_user.first_name}
⭐ 🆔 {user_id}
⭐ 💰 Rs.{load_settings().get('ban_price', 0)}
⭐ 📱 @{call.from_user.username or 'N/A'}
""")

# ============================================================
# ADMIN CALLBACKS (SAB FULLY GREEN)
# ============================================================
@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def admin_callback(call):
    try:
        if not is_admin(call.from_user.id):
            _send_pe(call.message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
            bot.answer_callback_query(call.id)
            return
        action = call.data
        chat = call.message.chat.id
        settings = load_settings()
        users = load_users()

        if action == "adm_panel":
            _send_pe(chat, f"""
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
⭐ /setoutfitapi URL - OUTFIT API
⭐ /broadcastuser ID MSG - SEND
⭐ /allbroadcast MSG - ALL
""")
        elif action == "adm_stats":
            pending = load_pending()
            bans = load_bans()
            _send_pe(chat, f"""
⭐ ═══《 📊 sᴛᴀᴛs 》═══ ⭐

⭐ 👥 ᴜsᴇʀs: {len(users)}
⭐ 🔫 ʙᴀɴɴᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {len(bans)}
⭐ 💰 ᴘᴇɴᴅɪɴɢ: {len(pending)}
⭐ 💎 ᴜɴʟɪᴍɪᴛᴇᴅ: {sum(1 for u in users.values() if u.get('unlimited', False))}
⭐ 👑 ᴀᴅᴍɪɴs: {len(ADMIN_IDS)}
⭐ 💳 ᴘʀɪᴄᴇ: ʀs.{settings.get('price', 19)}
⭐ 🏦 ᴜᴘɪ: {settings.get('upi', 'vansh111@naviaxis')}
⭐ 🎽 OUTFIT API: {'✅' if settings.get('outfit_api') else '❌'}
⭐ 👨‍💻 {settings.get('developer', '@iflexzyann')}
""")
        elif action in ("adm_users", "adm_checkall"):
            if not users:
                _send_pe(chat, "⭐ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ!")
            else:
                text = f"⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
                for _uid, d in users.items():
                    st = "💎" if d.get("unlimited", False) else "🆓"
                    bn = "🚫" if d.get("banned", False) else "✅"
                    ad = "👑" if int(_uid) in ADMIN_IDS else ""
                    text += f"⭐ • {d.get('name', 'Unknown')} (@{d.get('username', 'N/A')}) - {st} {bn} {ad}\n"
                text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
                _send_pe(chat, text)
        elif action == "adm_data":
            with open("bot_data.json", "w") as f:
                json.dump({"users": users, "orders": load_orders(), "pending": load_pending(),
                           "bans": load_bans(), "settings": settings, "admins": ADMIN_IDS,
                           "generated": datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
            with open("bot_data.json", "rb") as f:
                bot.send_document(chat, f, caption="⭐ 📥 ᴅᴀᴛᴀ ᴇxᴘᴏʀᴛ")
        elif action == "adm_totaladmins":
            text = f"⭐ ═══《 👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs 》═══ ⭐\n\n"
            for admin_id in ADMIN_IDS:
                u = get_user(admin_id)
                text += f"⭐ • {u.get('name', 'Unknown')} (@{u.get('username', 'N/A')}) - 🆔 {admin_id}\n" if u else f"⭐ • 🆔 {admin_id}\n"
            text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(ADMIN_IDS)}"
            _send_pe(chat, text)
        elif action == "adm_totalbanned":
            bans = load_bans()
            text = f"⭐ ═══《 🔫 ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ 》═══ ⭐\n\n⭐ Total Accounts: {len(bans)}\n\n"
            for b in bans[-20:]:
                text += f"⭐ • {b.get('name', '?')} (UID: {b.get('uid', '?')}) - {str(b.get('time', ''))[:16]}\n"
            if not bans:
                text += "⭐ Abhi koi ban record nahi."
            _send_pe(chat, text)
        elif action == "adm_checkbanned":
            bans = load_bans()
            if not bans:
                _send_pe(chat, "⭐ Abhi koi ban record nahi!")
            else:
                anim = show_processing_animation(chat)
                results = {}
                for b in bans[-20:]:
                    try:
                        rr = requests.get(f"{BANCHECK_API}?uid={b['uid']}", timeout=10)
                        d = rr.json() if rr.status_code == 200 else {"error": f"HTTP {rr.status_code}"}
                        results[b['uid']] = d[0] if isinstance(d, list) and d else d
                    except Exception as e:
                        results[b['uid']] = {"error": str(e)}
                try:
                    bot.delete_message(chat, anim.message_id)
                except:
                    pass
                send_json_response(chat, {"total": len(results), "results": results}, "all_banned")
        elif action == "adm_price":
            _send_pe(chat, f"⭐ 💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{settings.get('price', 19)}\n⭐ /price <ᴀᴍᴛ>")
        elif action == "adm_upi":
            _send_pe(chat, f"⭐ 🏦 ᴄᴜʀʀᴇɴᴛ: {settings.get('upi', 'vansh111@naviaxis')}\n⭐ /upi <ɴᴇᴡ>")
        elif action == "adm_addadmin":
            _send_pe(chat, "⭐ /addadmin ɪᴅ")
        elif action == "adm_commands":
            _send_pe(chat, """
⭐ ═══《 📋 ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs 》═══ ⭐

⭐ /start - sᴛᴀʀᴛ ʙᴏᴛ
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
⭐ /setoutfitapi URL - sᴇᴛ ᴏᴜᴛғɪᴛ ᴀᴘɪ
⭐ /broadcastuser ID MSG - SEND
⭐ /allbroadcast MSG - ALL
""")
        elif action == "adm_broadcast":
            _send_pe(chat, "⭐ /broadcastuser ɪᴅ ᴍsɢ")
        elif action == "adm_allbroadcast":
            _send_pe(chat, "⭐ /allbroadcast ᴍsɢ")
        elif action == "adm_welimg":
            _send_pe(chat, "⭐ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ɪᴍᴀɢᴇ ᴜʀʟ")
            bot.register_next_step_handler(call.message, save_welcome_image)
        elif action == "adm_tokentext":
            _send_pe(chat, "⭐ sᴇɴᴅ ɴᴇᴡ ᴛᴏᴋᴇɴ ᴛᴇxᴛ")
            bot.register_next_step_handler(call.message, save_token_text)
        elif action == "adm_tokenvideo":
            _send_pe(chat, "📤 sᴇɴᴅ ᴠɪᴅᴇᴏ")
            bot.register_next_step_handler(call.message, save_token_video)
        elif action == "adm_banprice":
            _send_pe(chat, "💰 Send new ban price (0 = FREE):")
            bot.register_next_step_handler(call.message, process_set_ban_price)
        elif action == "adm_banfree":
            settings["ban_price"] = 0
            save_settings(settings)
            _send_pe(chat, "✅ Ban check is now FREE for everyone! 🎉")
        elif action == "adm_outfitapi":
            _send_pe(chat, "🔗 sᴇɴᴅ ᴏᴜᴛғɪᴛ ᴀᴘɪ ᴜʀʟ\n\n✅ Use {uid} ya ?uid= format\n⭐ Example: https://info.killersharmabot.online/player-info?uid={uid}")
            bot.register_next_step_handler(call.message, save_outfit_api)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"❌ Admin callback error: {e}")

# ============================================================
# ADMIN SETTERS
# ============================================================
def save_welcome_image(message):
    if not is_admin(message.from_user.id): return
    settings = load_settings()
    if message.photo:
        settings["welcome_image"] = message.photo[-1].file_id
        save_settings(settings)
        _send_pe(message.chat.id, "✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ!")
    elif message.text and message.text.startswith("http"):
        settings["welcome_image"] = message.text.strip()
        save_settings(settings)
        _send_pe(message.chat.id, "✅ ᴡᴇʟᴄᴏᴍᴇ ɪᴍᴀɢᴇ ᴜʀʟ ᴜᴘᴅᴀᴛᴇᴅ!")
    else:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ᴠᴀʟɪᴅ ᴜʀʟ!")

def save_token_text(message):
    if not is_admin(message.from_user.id): return
    settings = load_settings()
    settings["token_text"] = message.text.strip()
    save_settings(settings)
    _send_pe(message.chat.id, "✅ ᴛᴏᴋᴇɴ ᴛᴇxᴛ ᴜᴘᴅᴀᴛᴇᴅ!")

def save_token_video(message):
    if message.video:
        file_info = bot.get_file(message.video.file_id)
        bot.download_file(file_info.file_path, "token_video.mp4")
        _send_pe(message.chat.id, "✅ ᴠɪᴅᴇᴏ sᴀᴠᴇᴅ!")
    else:
        _send_pe(message.chat.id, "❌ sᴇɴᴅ ᴀ ᴠɪᴅᴇᴏ!")

def process_set_ban_price(message):
    if not is_admin(message.from_user.id): return
    try:
        price = int(message.text.strip())
        if price < 0:
            _send_pe(message.chat.id, "❌ Price cannot be negative!")
            return
        settings = load_settings()
        settings["ban_price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ Ban price set to Rs.{price}")
    except:
        _send_pe(message.chat.id, "❌ Invalid number!")

def save_outfit_api(message):
    if not is_admin(message.from_user.id): return
    api = message.text.strip()
    if not api.startswith("http"):
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜʀʟ!")
        return
    settings = load_settings()
    settings["outfit_api"] = api
    save_settings(settings)
    _send_pe(message.chat.id, "✅ ᴏᴜᴛғɪᴛ ᴀᴘɪ sᴀᴠᴇᴅ!")

# ============================================================
# SLASH COMMANDS (ADMIN)
# ============================================================
@bot.message_handler(commands=['approve'])
def approve_user(message):
    if not is_admin(message.from_user.id): return _send_pe(message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /approve ID")
    try: user_id = int(p[1])
    except: return _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
    update_user(user_id, "unlimited", True)
    update_user(user_id, "uses", 0)
    update_user(user_id, "ban_paid", True)
    pending = load_pending()
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_pending(pending)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴀᴘᴘʀᴏᴠᴇᴅ!")
    try: bot.send_message(user_id, "🎉 ᴄᴏɴɢʀᴀᴛs! ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss!")
    except: pass

@bot.message_handler(commands=['disapprove'])
def disapprove_user(message):
    if not is_admin(message.from_user.id): return _send_pe(message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /disapprove ID")
    try: user_id = int(p[1])
    except: return _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
    pending = load_pending()
    if str(user_id) in pending:
        del pending[str(user_id)]
        save_pending(pending)
    _send_pe(message.chat.id, f"❌ ᴜsᴇʀ {user_id} ʀᴇᴊᴇᴄᴛᴇᴅ!")

@bot.message_handler(commands=['ban'])
def ban_user_cmd(message):
    if not is_admin(message.from_user.id): return _send_pe(message.chat.id, "❌ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ!")
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /ban ID")
    try: user_id = int(p[1])
    except: return _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
    update_user(user_id, "banned", True)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=['unban'])
def unban_user_cmd(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /unban ID")
    try: user_id = int(p[1])
    except: return _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")
    update_user(user_id, "banned", False)
    _send_pe(message.chat.id, f"✅ ᴜsᴇʀ {user_id} ᴜɴʙᴀɴɴᴇᴅ!")

@bot.message_handler(commands=['users', 'checkall'])
def users_cmd_cmd(message):
    if not is_admin(message.from_user.id): return
    users = load_users()
    if not users: return _send_pe(message.chat.id, "⭐ ɴᴏ ᴜsᴇʀs ғᴏᴜɴᴅ!")
    text = f"⭐ ═══《 👥 ᴀʟʟ ᴜsᴇʀs 》═══ ⭐\n\n"
    for _uid, d in users.items():
        st = "💎" if d.get("unlimited", False) else "🆓"
        bn = "🚫" if d.get("banned", False) else "✅"
        ad = "👑" if int(_uid) in ADMIN_IDS else ""
        text += f"⭐ • {d.get('name', 'Unknown')} (@{d.get('username', 'N/A')}) - {st} {bn} {ad}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(users)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(commands=['data'])
def data_cmd_cmd(message):
    if not is_admin(message.from_user.id): return
    with open("bot_data.json", "w") as f:
        json.dump({"users": load_users(), "orders": load_orders(), "pending": load_pending(),
                   "bans": load_bans(), "settings": load_settings(), "admins": ADMIN_IDS,
                   "generated": datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
    with open("bot_data.json", "rb") as f:
        bot.send_document(message.chat.id, f, caption="⭐ 📥 ᴅᴀᴛᴀ ᴇxᴘᴏʀᴛ")

@bot.message_handler(commands=['totaladmins'])
def totaladmins_cmd(message):
    if not is_admin(message.from_user.id): return
    text = f"⭐ ═══《 👑 ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs 》═══ ⭐\n\n"
    for admin_id in ADMIN_IDS:
        u = get_user(admin_id)
        text += f"⭐ • {u.get('name', 'Unknown')} (@{u.get('username', 'N/A')}) - 🆔 {admin_id}\n" if u else f"⭐ • 🆔 {admin_id}\n"
    text += f"\n⭐ ᴛᴏᴛᴀʟ: {len(ADMIN_IDS)}"
    _send_pe(message.chat.id, text)

@bot.message_handler(commands=['price'])
def price_cmd(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, f"⭐ 💰 ᴄᴜʀʀᴇɴᴛ: ʀs.{load_settings().get('price', 19)}\n⭐ /price <AMT>")
    try:
        price = int(p[1])
        settings = load_settings()
        settings["price"] = price
        save_settings(settings)
        _send_pe(message.chat.id, f"✅ ᴘʀɪᴄᴇ sᴇᴛ ᴛᴏ ʀs.{price}")
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ!")

@bot.message_handler(commands=['upi'])
def upi_cmd(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, f"⭐ 🏦 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('upi', 'vansh111@naviaxis')}\n⭐ /upi <NEW>")
    settings = load_settings()
    settings["upi"] = p[1]
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴜᴘɪ sᴇᴛ ᴛᴏ {p[1]}")

@bot.message_handler(commands=['developer'])
def developer_cmd(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, f"⭐ 👨‍💻 ᴄᴜʀʀᴇɴᴛ: {load_settings().get('developer', '@iflexzyann')}\n⭐ /developer <@>")
    settings = load_settings()
    settings["developer"] = p[1]
    settings["support"] = p[1]
    save_settings(settings)
    _send_pe(message.chat.id, f"✅ ᴅᴇᴠᴇʟᴏᴘᴇʀ sᴇᴛ ᴛᴏ {p[1]}")

@bot.message_handler(commands=['addadmin'])
def add_admin_cmd(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /addadmin ID")
    try:
        user_id = int(p[1])
        if user_id not in ADMIN_IDS:
            ADMIN_IDS.append(user_id)
            _send_pe(message.chat.id, "✅ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ!")
        else:
            _send_pe(message.chat.id, "⚠️ ᴀʟʀᴇᴀᴅʏ ᴀᴅᴍɪɴ!")
    except:
        _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ɪᴅ!")

@bot.message_handler(commands=['setoutfitapi'])
def set_outfit_api_cmd(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split()
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /setoutfitapi URL\n⭐ Example: /setoutfitapi https://info.killersharmabot.online/player-info?uid={uid}")
    api = p[1].strip()
    if not api.startswith("http"): return _send_pe(message.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜʀʟ!")
    settings = load_settings()
    settings["outfit_api"] = api
    save_settings(settings)
    _send_pe(message.chat.id, "✅ ᴏᴜᴛғɪᴛ ᴀᴘɪ sᴀᴠᴇᴅ!")

@bot.message_handler(commands=['broadcastuser'])
def broadcast_user(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split(maxsplit=2)
    if len(p) < 3: return _send_pe(message.chat.id, "❌ /broadcastuser ID MSG")
    try:
        bot.send_message(int(p[1]), f"📢 {p[2]}")
        _send_pe(message.chat.id, f"✅ sᴇɴᴛ ᴛᴏ {p[1]}!")
    except:
        _send_pe(message.chat.id, "❌ ғᴀɪʟᴇᴅ!")

@bot.message_handler(commands=['allbroadcast'])
def all_broadcast(message):
    if not is_admin(message.from_user.id): return
    p = message.text.split(maxsplit=1)
    if len(p) < 2: return _send_pe(message.chat.id, "❌ /allbroadcast MSG")
    users = load_users()
    sent = failed = 0
    _send_pe(message.chat.id, f"⏳ sᴇɴᴅɪɴɢ ᴛᴏ {len(users)} ᴜsᴇʀs...")
    for user_id in users.keys():
        try:
            bot.send_message(int(user_id), f"📢 {p[1]}")
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    _send_pe(message.chat.id, f"⭐ ᴄᴏᴍᴘʟᴇᴛᴇ!\n⭐ ᴛᴏᴛᴀʟ: {len(users)}\n⭐ sᴇɴᴛ: {sent}\n⭐ ғᴀɪʟᴇᴅ: {failed}")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    _send_pe(message.chat.id, """
⭐ ═══《 ❓ ʜᴇʟᴘ 》═══ ⭐

⭐ 𝟷️⃣ ᴄʟɪᴄᴋ BAN ACCOUNT
⭐ 𝟸️⃣ sᴇɴᴅ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ
⭐ 𝟹️⃣ ᴄᴏɴғɪʀᴍ ʏᴇs
⭐ 𝟺️⃣ ᴀᴄᴄᴏᴜɴᴛ ɢᴇᴛs ʙᴀɴɴᴇᴅ!

⭐ 🆓 ғʀᴇᴇ ᴛʀɪᴀʟ: 𝟷 ʙᴀɴ
⭐ 💰 ᴜɴʟɪᴍɪᴛᴇᴅ: ᴘᴀʏ & ɢᴇᴛ
⭐ 🔍 BAN CHECK: Check UID status
⭐ 🎽 CHECK OUTFIT: Outfit + photos

⭐ 👨‍💻 @ɪꜰʟᴇxᴢʏᴀɴɴ
""")
    show_menu(message.chat.id, message.from_user.id)

# ============================================================
# WEBHOOK
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
# MAIN - FIXED (Flask hamesha chalega, polling thread me)
# ============================================================
if __name__ == "__main__":
    print("✅ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ!")
    print(f"✅ ᴏᴡɴᴇʀ: {OWNER_ID}")

    hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

    if hostname:
        try:
            bot.remove_webhook()
            bot.set_webhook(url=f"https://{hostname}/{BOT_TOKEN}")
            print("✅ ᴡᴇʙʜᴏᴏᴋ sᴇᴛ")
        except Exception as e:
            print(f"⚠️ webhook fail: {e}, ᴘᴏʟʟɪɴɢ ᴛʜʀᴇᴀᴅ sᴛᴀʀᴛ")
            import threading
            threading.Thread(target=bot.infinity_polling, daemon=True).start()
    else:
        print("⚠️ ɴᴏ ʜᴏsᴛɴᴀᴍᴇ, ᴘᴏʟʟɪɴɢ ɪɴ ᴛʜʀᴇᴀᴅ")
        import threading
        try:
            bot.remove_webhook()
        except Exception:
            pass
        threading.Thread(target=bot.infinity_polling, daemon=True).start()

    # Flask hamesha port par chalega - Render ka health check pass hoga
    app.run(host='0.0.0.0', port=PORT)