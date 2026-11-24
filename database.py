import json
import aiosqlite
import pytz
from datetime import datetime, timedelta
import random
import os
import re
import jdatetime
async def reply(message, text, is_deleted_timer, delet_timer):
    if is_deleted_timer:
        return await message.reply(text, delete_after=delet_timer)
    else:
        return await message.reply(text)
async def MPro(text: str, chat_id=None):
    mode = await get_group_model(chat_id)
    a = await get_group_sticker_emoji(chat_id)
    symbols = ["❖  ", "»  ", "•  ", "◄  ", " "]
    def broken_text(s: str) -> str:
        return "\u200c".join(list(s))
    def spaced_text(s: str) -> str:
        return " ".join(list(s))
    def reversed_text(s: str) -> str:
        return s[::-1]
    def timestamp_prefix(s: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"[{now}] {s} {a}"
    def boxed_text(s: str) -> str:
        line = "═" * (len(s) + 2)
        return f"╔{line}╗\n║ {s} {a} ║\n╚{line}╝"
    def code_block_format(s: str) -> str:
        safe_text = s.replace("```", "").strip()
        if "\n" in safe_text:
            lines = safe_text.splitlines()
            formatted_lines = "\n".join(
                [f"```{line} {a}```" for line in lines if line.strip()]
            )
            return f"{symbols[4]}{formatted_lines} {a}\n"
        else:
            return f"{symbols[4]}```{safe_text} {a}```\n"
    def inline_code_format(s: str) -> str:
        safe_text = s.replace("`", "ˋ").strip()
        if "\n" in safe_text:
            lines = safe_text.splitlines()
            formatted_lines = "\n".join([f"`{line}`" for line in lines if line.strip()])
            return f"{symbols[4]}{formatted_lines} {a}\n"
        else:
            return f"{symbols[4]}`{safe_text} {a}`\n"
    formatters = {
        1: lambda s: f"{symbols[0]}{s} {a}\n",
        2: lambda s: f"{symbols[1]}{s} {a}\n",
        3: lambda s: f"{symbols[2]}{s} {a}\n",
        4: lambda s: f"{symbols[3]}{s} {a}\n",
        5: lambda s: code_block_format(s),
        6: lambda s: f"{symbols[4]}||{s} {a}||\n",
        7: lambda s: f"{symbols[4]}**{s} {a}**\n",
        8: lambda s: f"{symbols[4]}__{s} {a}__\n",
        9: lambda s: f"{symbols[4]}--{s} {a}--\n",
        10: lambda s: inline_code_format(s),
        11: lambda s: f"{symbols[4]}~~{s} {a}~~\n",
        12: lambda s: f"{symbols[4]}{broken_text(s)} {a}\n",
        13: lambda s: f"{symbols[4]}{spaced_text(s)} {a}\n",
        14: lambda s: f"{symbols[4]}{reversed_text(s)} {a}\n",
        15: lambda s: f"{symbols[4]}{timestamp_prefix(s)}\n",
        16: lambda s: f"{boxed_text(s)}\n",
    }
    formatter = formatters.get(mode)
    return formatter(text) if formatter else text
MAIN_DB = "bot_data.db"
_db_conn = None
model = 1
async def get_db_conn():
    global _db_conn
    if _db_conn is None:
        _db_conn = await aiosqlite.connect(MAIN_DB)
        await _db_conn.execute("PRAGMA journal_mode = WAL")
        await _db_conn.execute("PRAGMA synchronous = NORMAL")
        await _db_conn.execute("PRAGMA foreign_keys = ON")
        await _db_conn.execute("PRAGMA cache_size = -2000")
        await _db_conn.execute("PRAGMA temp_store = MEMORY")
    return _db_conn
async def reconnect_if_needed():
    global _db_conn
    if _db_conn is None:
        return await get_db_conn()
    try:
        await _db_conn.execute("SELECT 1")
        return _db_conn
    except Exception:
        try:
            await _db_conn.close()
        except:
            pass
        _db_conn = None
        return await get_db_conn()
async def close_connection():
    global _db_conn
    if _db_conn:
        await _db_conn.close()
        _db_conn = None
async def setup_all_tables():
    conn = await get_db_conn()
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS main_settings (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            chat_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            active BOOLEAN NOT NULL,
            bot_name TEXT DEFAULT 'دراگون',
            delet_timer INTEGER DEFAULT 16
            
        )
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS group_members (
            chat_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('owner', 'admin', 'vip', 'member')),
            messages INTEGER DEFAULT 0,
            id INTEGER DEFAULT 0,
            links INTEGER DEFAULT 0,
            media INTEGER DEFAULT 0,
            photos INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            documents INTEGER DEFAULT 0,
            polls INTEGER DEFAULT 0,
            location INTEGER DEFAULT 0,
            voice INTEGER DEFAULT 0,
            sticker INTEGER DEFAULT 0,
            forward INTEGER DEFAULT 0,
            hashtag INTEGER DEFAULT 0,
            english INTEGER DEFAULT 0,
            persian INTEGER DEFAULT 0,
            FOREIGN KEY (chat_id) REFERENCES groups(chat_id),
            UNIQUE(chat_id, user_id)
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lang TEXT DEFAULT NULL,
            join_time TEXT NOT NULL,
            joined BOOLEAN DEFAULT 0
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stats (
            chat_id TEXT PRIMARY KEY,
            messages_count INTEGER DEFAULT 0,
            tickets_count INTEGER DEFAULT 0
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            chat_id TEXT NOT NULL,
            ticket_id TEXT NOT NULL,
            name TEXT,
            text TEXT,
            time TEXT,
            PRIMARY KEY (chat_id, ticket_id)
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blocked_users (
            chat_id TEXT PRIMARY KEY
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_languages (
            chat_id TEXT PRIMARY KEY,
            lang TEXT DEFAULT 'fa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS broadcast_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT,
            sender_chat_id TEXT,
            message_text TEXT,
            target_lang TEXT,
            sent_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dashboard (
            chat_id TEXT NOT NULL,
            dashboard_type TEXT NOT NULL,
            is_locked BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (chat_id, dashboard_type)
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS locks (
            chat_id TEXT NOT NULL,
            lock_type TEXT NOT NULL,
            is_locked BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (chat_id, lock_type)
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            chat_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            is_exempt BOOLEAN DEFAULT FALSE,
            original TEXT,
            nickname TEXT,
            sokot BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (chat_id, sender_id)
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS group_model (
            chat_id TEXT PRIMARY KEY,
            model INTEGER DEFAULT 0,
            sticker_emoji TEXT DEFAULT '🐉'
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS group_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            text TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS group_timers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            text TEXT NOT NULL,
            run_time TEXT NOT NULL
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sargarmi_lock (
            chat_id TEXT NOT NULL,
            lock_type TEXT NOT NULL,
            is_locked BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (chat_id, lock_type)
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS warnings (
            chat_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            warnings_count INTEGER DEFAULT 0,
            last_warning_time TEXT,
            max_warnings INTEGER DEFAULT 3,
            PRIMARY KEY (chat_id, user_id)
        )
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id TEXT PRIMARY KEY,
            max_warnings INTEGER DEFAULT 3,
            penalty_type TEXT DEFAULT 'ban'
        )
        """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS group_charges (
            chat_id TEXT PRIMARY KEY,
            is_active BOOLEAN DEFAULT 0,
            total_days INTEGER DEFAULT 0,          -- کل روزهای خریداری شده
            used_days INTEGER DEFAULT 0,           -- روزهای استفاده شده
            remaining_days INTEGER DEFAULT 0,       -- روزهای باقیمانده
            start_time TEXT,                       -- زمان شروع آخرین شارژ
            end_time TEXT,                         -- زمان پایان
            last_warning_day INTEGER DEFAULT 0,    -- آخرین روز اخطار داده شده
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    await conn.executescript(
        """
        -- ایندکس برای جستجوی سریع در group_members
        CREATE INDEX IF NOT EXISTS idx_group_members_chat_user 
        ON group_members(chat_id, user_id);
        
        CREATE INDEX IF NOT EXISTS idx_group_members_role 
        ON group_members(chat_id, role);
        
        -- ایندکس برای آمار پیام‌ها
        CREATE INDEX IF NOT EXISTS idx_group_members_messages 
        ON group_members(chat_id, messages DESC);
        
        -- ایندکس برای کاربران
        CREATE INDEX IF NOT EXISTS idx_users_chat_id 
        ON users(chat_id);
        
        -- ایندکس برای تیکت‌ها
        CREATE INDEX IF NOT EXISTS idx_tickets_chat_time 
        ON tickets(chat_id, time DESC);
        
        -- ایندکس برای لاک‌ها
        CREATE INDEX IF NOT EXISTS idx_locks_chat_type 
        ON locks(chat_id, lock_type);
        
        -- ایندکس برای اعضا
        CREATE INDEX IF NOT EXISTS idx_members_chat_sender 
        ON members(chat_id, sender_id);
        
        -- ایندکس برای داشبورد
        CREATE INDEX IF NOT EXISTS idx_dashboard_chat_type 
        ON dashboard(chat_id, dashboard_type);
        
        -- ایندکس برای warnings
        CREATE INDEX IF NOT EXISTS idx_warnings_chat_user 
        ON warnings(chat_id, user_id);
        
        -- ایندکس برای group_charges
        CREATE INDEX IF NOT EXISTS idx_group_charges_chat 
        ON group_charges(chat_id);
        
        CREATE INDEX IF NOT EXISTS idx_group_charges_end_time 
        ON group_charges(end_time) WHERE is_active = 1;
    """
    )
    async with conn.execute("SELECT COUNT(*) FROM main_settings") as cursor:
        row = await cursor.fetchone()
        if row[0] == 0:
            initial_data = {"owners": [], "channels": []}
            await conn.execute(
                "INSERT INTO main_settings (id, data) VALUES (?, ?)",
                (1, json.dumps(initial_data)),
            )
    await conn.commit()
async def get_data():
    conn = await get_db_conn()
    async with conn.execute("SELECT data FROM main_settings WHERE id = 1") as cursor:
        row = await cursor.fetchone()
        return json.loads(row[0]) if row else {"owners": [], "channels": []}
async def save_data(data):
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE main_settings SET data = ? WHERE id = 1", (json.dumps(data),)
    )
    await conn.commit()
async def add_owner(name: str, guid: str):
    data = await get_data()
    if not any(o["guid"] == guid for o in data["owners"]):
        data["owners"].append({"name": name, "guid": guid})
        await save_data(data)
async def remove_owner(guid: str):
    data = await get_data()
    data["owners"] = [o for o in data["owners"] if o["guid"] != guid]
    await save_data(data)
async def list_owners():
    data = await get_data()
    return data["owners"]
async def owner_exists(guid: str) -> bool:
    data = await get_data()
    return any(o["guid"] == guid for o in data["owners"])
async def count_owners() -> int:
    data = await get_data()
    return len(data["owners"])
async def add_channel(name: str, link: str):
    data = await get_data()
    if not any(c["link"] == link for c in data["channels"]):
        data["channels"].append({"name": name, "link": link})
        await save_data(data)
async def remove_channel(link: str):
    data = await get_data()
    data["channels"] = [c for c in data["channels"] if c["link"] != link]
    await save_data(data)
async def list_channels():
    data = await get_data()
    channels = data["channels"]
    if not channels:
        return "📭 هیچ کانالی ثبت نشده است."
    text = ""
    for ch in channels:
        text += f"{ch['link']}\n"
    return text
async def channel_exists(link: str) -> bool:
    data = await get_data()
    return any(c["link"] == link for c in data["channels"])
async def count_channels() -> int:
    data = await get_data()
    return len(data["channels"])
async def has_owner() -> bool:
    data = await get_data()
    return len(data["owners"]) > 0
async def get_owner_ids() -> list[str]:
    data = await get_data()
    return [o["guid"] for o in data["owners"]]
async def handle_add_admin(msg, bot, lang="fa"):
    text = msg.text.strip()
    parts = text.split()
    if len(parts) != 2:
        await msg.reply("❌ فرمت صحیح: /addadmin <chat_id>")
        return
    if not await owner_exists(str(msg.chat_id)):
        await msg.reply("⛔ فقط مالک ربات اجازه استفاده از این دستور را دارد.")
        return
    chat_id = parts[1].strip()
    try:
        name = await bot.get_name(chat_id=chat_id)
    except Exception:
        name = "Unknown"
    await add_owner(name=name, guid=chat_id)
    await msg.reply(f"✅ کاربر {name} ({chat_id}) به عنوان ادمین اضافه شد.")
    try:
        await bot.send_message(chat_id, "✅ شما به عنوان ادمین ربات اضافه شدید.")
    except Exception:
        pass
async def handle_remove_admin(msg, bot):
    chat_id = str(msg.chat_id)
    if not await owner_exists(chat_id):
        await msg.reply("⛔ فقط مالک ربات اجازه استفاده از این دستور را دارد.")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.reply("❌ لطفاً GUID کاربر را وارد کنید. مثال: /deladmin <guid>")
        return
    guid = parts[1]
    if not await owner_exists(guid):
        await msg.reply(f"⚠️ کاربر {guid} ادمین نیست.")
        return
    await remove_owner(guid)
    await msg.reply(f"✅ کاربر {guid} از لیست ادمین‌ها حذف شد.")
async def activate_group(chat_id: str):
    conn = await get_db_conn()
    await conn.execute("UPDATE groups SET active = 1 WHERE chat_id = ?", (chat_id,))
    await conn.commit()
async def deactivate_group(chat_id: str):
    conn = await get_db_conn()
    await conn.execute("UPDATE groups SET active = 0 WHERE chat_id = ?", (chat_id,))
    await conn.commit()
async def is_group_active(chat_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT active FROM groups WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row and row[0] == 1
async def get_time_deleter(chat_id):
    conn = await get_db_conn()
    try:
        async with conn.execute(
            "SELECT delet_timer FROM groups WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
        if row and row[0] is not None:
            return int(row[0])
        else:
            return 8
    except Exception as e:
        return 8
async def group_exists(chat_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT 1 FROM groups WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
    return row is not None
async def add_group(chat_id: str, name: str, active: bool = True):
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR REPLACE INTO groups (chat_id, name, active) VALUES (?, ?, ?)",
        (chat_id, name, int(active)),
    )
    await conn.commit()
async def remove_group(chat_id: str):
    conn = await get_db_conn()
    try:
        await conn.execute("DELETE FROM group_members WHERE chat_id = ?", (chat_id,))
        await conn.execute("DELETE FROM groups WHERE chat_id = ?", (chat_id,))
        await conn.commit()
    except Exception as e:
        await conn.rollback()
async def add_bot_name(chat_id, bot_name):
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE groups SET bot_name = ? WHERE chat_id = ?",
        (bot_name, chat_id),
    )
    await conn.commit()
    return True
async def get_bot_name(chat_id):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT bot_name FROM groups WHERE chat_id = ?",
        (chat_id,),
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else None
async def list_groups():
    conn = await get_db_conn()
    async with conn.execute("SELECT chat_id, name, active FROM groups") as cursor:
        rows = await cursor.fetchall()
    return [{"chat_id": r[0], "name": r[1], "active": bool(r[2])} for r in rows]
async def count_groups():
    conn = await get_db_conn()
    async with conn.execute("SELECT COUNT(*) FROM groups") as cursor:
        row = await cursor.fetchone()
    return row[0] if row else 0
async def add_member(chat_id: str, user_id: str, role: str) -> bool:
    conn = await get_db_conn()
    try:
        limits = {"owner": 1, "admin": 10000, "vip": 10000, "member": 99999999999999}
        async with conn.execute(
            "SELECT 1 FROM groups WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            group_row = await cursor.fetchone()
        if not group_row:
            return False
        async with conn.execute(
            "SELECT 1 FROM group_members WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ) as cursor:
            row = await cursor.fetchone()
        if row:
            return False
        async with conn.execute(
            "SELECT COUNT(*) FROM group_members WHERE chat_id = ? AND role = ?",
            (chat_id, role),
        ) as cursor:
            count_row = await cursor.fetchone()
        if count_row[0] >= limits[role]:
            return False
        await conn.execute(
            "INSERT INTO group_members (chat_id, user_id, role) VALUES (?, ?, ?)",
            (chat_id, user_id, role),
        )
        await conn.commit()
        return True
    except Exception as e:
        await conn.rollback()
        return False
async def list_group_admins(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT user_id FROM group_members WHERE chat_id = ? AND role = 'admin'",
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
async def list_group_vips(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT user_id FROM group_members WHERE chat_id = ? AND role = 'vip'",
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
async def list_group_ow(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT user_id FROM group_members WHERE chat_id = ? AND role = 'owner'",
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
async def get_all_groups():
    conn = await get_db_conn()
    async with conn.execute("SELECT chat_id FROM groups WHERE active = 1") as cursor:
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
async def send_groups_list(message, bot):
    try:
        conn = await get_db_conn()
        async with conn.execute("SELECT chat_id, name, active FROM groups") as cursor:
            rows = await cursor.fetchall()
        if not rows:
            await message.reply("⚠️ هیچ گروهی در دیتابیس یافت نشد.")
            return
        groups = [
            {
                "chat_id": row[0],
                "name": row[1] if row[1] else "نام ثبت نشده",
                "active": bool(row[2]),
            }
            for row in rows
        ]
        total = len(groups)
        if total <= 30:
            text = "📊 **لیست گروه‌ها:**\n\n"
            for idx, g in enumerate(groups, 1):
                status = "✅ فعال" if g["active"] else "❌ غیرفعال"
                text += (
                    f"{idx}. **{g['name']}**\n"
                    f"🆔 `{g['chat_id']}`\n"
                    f"📦 وضعیت: {status}\n\n"
                )
            await message.reply(text)
        else:
            file_name = "groups_list.json"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)
            await message.reply(
                f"📦 تعداد گروه‌ها زیاد بود ({total} عدد)، فایل JSON ارسال شد 👇"
            )
            if os.path.exists("groups_list.json"):
                await bot.send_document(
                    chat_id=message.chat_id, path="groups_list.json"
                )
            import time
            try:
                time.sleep(10)
                os.remove(file_path)
            except Exception as err:
                print(f"⚠️ Error removing temp file: {err}")
    except Exception as e:
        await message.reply(f"❌ خطا در دریافت لیست گروه‌ها:\n`{e}`")
async def edit_member(chat_id: str, user_id: str, new_role: str) -> bool:
    VALID_ROLES = ["owner", "admin", "vip", "member"]
    if new_role not in VALID_ROLES:
        return False
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE group_members SET role = ? WHERE chat_id = ? AND user_id = ?",
        (new_role, chat_id, user_id),
    )
    await conn.commit()
    return True
async def remove_member(chat_id: str, user_id: str):
    conn = await get_db_conn()
    await conn.execute(
        "DELETE FROM group_members WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    await conn.commit()
async def list_members(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        """
        SELECT user_id, role, messages, id, links, media, photos, videos,
        documents, polls, location, voice, sticker, forward, hashtag,
        english, persian
        FROM group_members
        WHERE chat_id = ?
        """,
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        {
            "user_id": r[0],
            "role": r[1],
            "messages": r[2],
            "id": r[3],
            "links": r[4],
            "media": r[5],
            "photos": r[6],
            "videos": r[7],
            "documents": r[8],
            "polls": r[9],
            "location": r[10],
            "voice": r[11],
            "sticker": r[12],
            "forward": r[13],
            "hashtag": r[14],
            "english": r[15],
            "persian": r[16],
        }
        for r in rows
    ]
VALID_STATS = [
    "messages",
    "id",
    "links",
    "media",
    "photos",
    "videos",
    "documents",
    "polls",
    "location",
    "voice",
    "sticker",
    "forward",
    "hashtag",
    "english",
    "persian",
]
async def increment_stat(chat_id: str, user_id: str, stat: str):
    if stat not in VALID_STATS:
        raise ValueError(f"Invalid stat type: {stat}")
    conn = await get_db_conn()
    await conn.execute(
        f"UPDATE group_members SET {stat} = {stat} + 1 WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    await conn.commit()
async def get_member(chat_id: str, user_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        """
        SELECT role, messages, id, links, media, photos, videos, documents, polls,
               location, voice, sticker, forward, hashtag, english, persian
        FROM group_members
        WHERE chat_id = ? AND user_id = ?
        """,
        (chat_id, user_id),
    ) as cursor:
        row = await cursor.fetchone()
    if row:
        return {
            "role": row[0],
            "messages": row[1],
            "id": row[2],
            "links": row[3],
            "media": row[4],
            "photos": row[5],
            "videos": row[6],
            "documents": row[7],
            "polls": row[8],
            "location": row[9],
            "voice": row[10],
            "sticker": row[11],
            "forward": row[12],
            "hashtag": row[13],
            "english": row[14],
            "persian": row[15],
        }
    return False
async def get_user_role(chat_id: str, user_id: str) -> str | None:
    member = await get_member(chat_id, user_id)
    return member["role"] if member else None
async def check_role(chat_id: str, user_id: str, roles: list[str]) -> bool:
    role = await get_user_role(chat_id, user_id)
    return role in roles if role else False
async def has_ownerr(user_id: str, chat_id: str = None) -> bool:
    if chat_id is None:
        return False
    return await check_role(chat_id, user_id, ["owner"])
async def reset_vips(chat_id: str) -> int:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT COUNT(*) FROM group_members WHERE chat_id = ? AND role = 'vip'",
        (chat_id,),
    ) as cursor:
        row = await cursor.fetchone()
        count = row[0] if row else 0
    await conn.execute(
        "UPDATE group_members SET role = 'member' WHERE chat_id = ? AND role = 'vip'",
        (chat_id,),
    )
    await conn.commit()
    return count
async def reset_admins(chat_id: str) -> int:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT COUNT(*) FROM group_members WHERE chat_id = ? AND role = 'admin'",
        (chat_id,),
    ) as cursor:
        row = await cursor.fetchone()
        count = row[0] if row else 0
    await conn.execute(
        "UPDATE group_members SET role = 'member' WHERE chat_id = ? AND role = 'admin'",
        (chat_id,),
    )
    await conn.commit()
    return count
async def add_user(
    chat_id: str, name: str, join_time: str = None, joined: bool = False
):
    if join_time is None:
        join_time = datetime.now(pytz.timezone("Asia/Tehran")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR REPLACE INTO users (chat_id, name, join_time, joined) VALUES (?, ?, ?, ?)",
        (chat_id, name, join_time, int(joined)),
    )
    await conn.commit()
async def get_user_lang_from_users(chat_id: str) -> str:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT lang FROM users WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if row and row[0]:
            return row[0]
        return "fa"
async def set_user_lang_in_users(chat_id: str, lang: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT 1 FROM users WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        exists = await cursor.fetchone()
    if exists:
        await conn.execute(
            "UPDATE users SET lang = ? WHERE chat_id = ?", (lang, chat_id)
        )
    else:
        await conn.execute(
            "INSERT INTO users (chat_id, name, lang, join_time, joined) VALUES (?, ?, ?, ?, ?)",
            (
                chat_id,
                "Unknown",
                lang,
                datetime.now(pytz.timezone("Asia/Tehran")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                0,
            ),
        )
    await conn.commit()
async def user_exists(chat_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT 1 FROM users WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row is not None
async def set_user_joined(chat_id: str, joined: bool = True):
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE users SET joined = ? WHERE chat_id = ?", (int(joined), chat_id)
    )
    await conn.commit()
async def list_users():
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT chat_id, name, join_time, joined FROM users"
    ) as cursor:
        rows = await cursor.fetchall()
        return [
            {"chat_id": r[0], "name": r[1], "join_time": r[2], "joined": bool(r[3])}
            for r in rows
        ]
async def list_user_ids():
    conn = await get_db_conn()
    async with conn.execute("SELECT chat_id FROM users") as cursor:
        rows = await cursor.fetchall()
        return [r[0] for r in rows]
async def count_users():
    conn = await get_db_conn()
    async with conn.execute("SELECT COUNT(*) FROM users") as cursor:
        result = await cursor.fetchone()
        return result[0] if result else 0
async def has_selected_lang(chat_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT lang FROM users WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row and row[0])
async def has_joined(chat_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT joined FROM users WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row and row[0])
async def ensure_user_exists_stats(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT chat_id FROM stats WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        result = await cursor.fetchone()
        if not result:
            await conn.execute(
                "INSERT INTO stats (chat_id, messages_count, tickets_count) VALUES (?, ?, ?)",
                (chat_id, 0, 0),
            )
            await conn.commit()
async def increase_messages(chat_id: str, amount: int = 1):
    await ensure_user_exists_stats(chat_id)
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE stats SET messages_count = messages_count + ? WHERE chat_id = ?",
        (amount, chat_id),
    )
    await conn.commit()
async def increase_tickets(chat_id: str, amount: int = 1):
    await ensure_user_exists_stats(chat_id)
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE stats SET tickets_count = tickets_count + ? WHERE chat_id = ?",
        (amount, chat_id),
    )
    await conn.commit()
async def get_messages_count(chat_id: str) -> int:
    await ensure_user_exists_stats(chat_id)
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT messages_count FROM stats WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 0
async def get_tickets_count(chat_id: str) -> int:
    await ensure_user_exists_stats(chat_id)
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT tickets_count FROM stats WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 0
async def list_all_stats():
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT chat_id, messages_count, tickets_count FROM stats"
    ) as cursor:
        rows = await cursor.fetchall()
        return [{"chat_id": r[0], "messages": r[1], "tickets": r[2]} for r in rows]
async def generate_ticket_id() -> str:
    return str(random.randint(100000000, 999999999))
async def add_ticket(chat_id: str, name: str, text: str):
    ticket_id = await generate_ticket_id()
    tehran_time = datetime.now(pytz.timezone("Asia/Tehran")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    conn = await get_db_conn()
    await conn.execute(
        "INSERT INTO tickets (chat_id, ticket_id, name, text, time) VALUES (?, ?, ?, ?, ?)",
        (chat_id, ticket_id, name, text, tehran_time),
    )
    await conn.commit()
    return ticket_id
async def get_ticket(chat_id: str, ticket_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT name, text, time FROM tickets WHERE chat_id = ? AND ticket_id = ?",
        (chat_id, ticket_id),
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return {
            "chat_id": chat_id,
            "ticket_id": ticket_id,
            "name": row[0],
            "text": row[1],
            "time": row[2],
        }
async def get_tickets_by_chat(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT ticket_id, name, text, time FROM tickets WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        return [
            {
                "chat_id": chat_id,
                "ticket_id": r[0],
                "name": r[1],
                "text": r[2],
                "time": r[3],
            }
            for r in rows
        ]
async def count_tickets(chat_id: str) -> int:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 0
async def remove_ticket(chat_id: str, ticket_id: str):
    conn = await get_db_conn()
    await conn.execute(
        "DELETE FROM tickets WHERE chat_id = ? AND ticket_id = ?", (chat_id, ticket_id)
    )
    await conn.commit()
async def remove_all_tickets(chat_id: str):
    conn = await get_db_conn()
    await conn.execute("DELETE FROM tickets WHERE chat_id = ?", (chat_id,))
    await conn.commit()
async def list_all_tickets(limit: int = 50):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT chat_id, ticket_id, name, text, time FROM tickets ORDER BY time DESC LIMIT ?",
        (limit,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [
            {
                "chat_id": r[0],
                "ticket_id": r[1],
                "name": r[2],
                "text": r[3],
                "time": r[4],
            }
            for r in rows
        ]
BLOCKED_TEXTS = {
    "fa": {
        "format_error": "❌ فرمت صحیح: {cmd} <chat_id>",
        "blocked_success": "✅ کاربر {chat_id} مسدود شد.",
        "blocked_notice": "⚠️ شما توسط ادمین مسدود شدید و نمی‌توانید از ربات استفاده کنید.",
        "already_blocked": "⚠️ کاربر {chat_id} قبلا مسدود شده بود.",
        "unblocked_success": "✅ کاربر {chat_id} از مسدودیت خارج شد.",
        "unblocked_notice": "✅ شما از مسدودیت ربات خارج شدید. حالا می‌توانید از ربات استفاده کنید.",
        "not_blocked": "⚠️ کاربر {chat_id} در لیست مسدودها نبود.",
        "list_title": "📜 لیست کاربران مسدود شده:\n",
        "list_empty": "⚠️ هیچ کاربری مسدود نشده است.",
        "reset": "✅ لیست مسدودها پاک شد.",
    }
}
def t(lang, key, **kwargs):
    return BLOCKED_TEXTS.get(lang, BLOCKED_TEXTS["fa"]).get(key, key).format(**kwargs)
async def load_blocked():
    conn = await get_db_conn()
    async with conn.execute("SELECT chat_id FROM blocked_users") as cursor:
        rows = await cursor.fetchall()
    return [row[0] for row in rows]
async def add_block(chat_id):
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR IGNORE INTO blocked_users(chat_id) VALUES(?)", (str(chat_id),)
    )
    await conn.commit()
async def remove_block(chat_id):
    conn = await get_db_conn()
    await conn.execute("DELETE FROM blocked_users WHERE chat_id = ?", (str(chat_id),))
    await conn.commit()
async def reset_blocked():
    conn = await get_db_conn()
    await conn.execute("DELETE FROM blocked_users")
    await conn.commit()
async def is_blocked(chat_id):
    blocked = await load_blocked()
    return str(chat_id) in blocked
async def handle_bloke_command(msg, bot, lang="fa"):
    parts = msg.text.split()
    if len(parts) != 2:
        await msg.reply(t(lang, "format_error", cmd="/bloke"))
        return
    chat_id = parts[1]
    if not await is_blocked(chat_id):
        await add_block(chat_id)
        await msg.reply(t(lang, "blocked_success", chat_id=chat_id))
        try:
            await bot.send_message(chat_id, t(lang, "blocked_notice"))
        except:
            pass
    else:
        await msg.reply(t(lang, "already_blocked", chat_id=chat_id))
async def handle_unbloke_command(msg, bot, lang="fa"):
    parts = msg.text.split()
    if len(parts) != 2:
        await msg.reply(t(lang, "format_error", cmd="/unbloke"))
        return
    chat_id = parts[1]
    if await is_blocked(chat_id):
        await remove_block(chat_id)
        await msg.reply(t(lang, "unblocked_success", chat_id=chat_id))
        try:
            await bot.send_message(chat_id, t(lang, "unblocked_notice"))
        except:
            pass
    else:
        await msg.reply(t(lang, "not_blocked", chat_id=chat_id))
async def handle_reset_blocked(msg, lang="fa"):
    await reset_blocked()
    await msg.reply(t(lang, "reset"))
async def handle_list_blocked(msg, lang="fa"):
    blocked = await load_blocked()
    if blocked:
        text = t(lang, "list_title") + "\n".join(blocked)
    else:
        text = t(lang, "list_empty")
    await msg.reply(text)
async def set_user_lang(chat_id: str, lang: str):
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR REPLACE INTO user_languages (chat_id, lang) VALUES (?, ?)",
        (chat_id, lang),
    )
    await conn.commit()
async def get_user_lang(chat_id: str) -> str:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT lang FROM user_languages WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else "fa"
async def save_broadcast_message(
    sender_id: str, sender_chat_id: str, message_text: str, target_lang: str = "all"
):
    conn = await get_db_conn()
    cursor = await conn.execute(
        "INSERT INTO broadcast_messages (sender_id, sender_chat_id, message_text, target_lang) VALUES (?, ?, ?, ?)",
        (sender_id, sender_chat_id, message_text, target_lang),
    )
    await conn.commit()
    return cursor.lastrowid
async def get_broadcast_stats(broadcast_id: int):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT sent_count, failed_count FROM broadcast_messages WHERE id = ?",
        (broadcast_id,),
    ) as cursor:
        return await cursor.fetchone()
async def update_broadcast_stats(broadcast_id: int, sent: int, failed: int):
    conn = await get_db_conn()
    await conn.execute(
        "UPDATE broadcast_messages SET sent_count = ?, failed_count = ? WHERE id = ?",
        (sent, failed, broadcast_id),
    )
    await conn.commit()
DASHBOARD_TYPES = ["speak", "speak_bad", "speak_vip", "delet_timer", "calculator"]
DASHBOARD_TRANSLATIONS = {
    "delet_timer": "حذف خودکار",
    "speak": "سخنگو بی ادب",
    "speak_bad": "سخنگو بی ادب",
    "speak_vip": "سخنگو شخصی",
    "calculator": "ماشین حساب",
}
async def set_dashboard(chat_id: str, dashboard_type: str, is_locked: bool = True):
    if dashboard_type not in DASHBOARD_TYPES:
        raise ValueError(f"Invalid dashboard type: {dashboard_type}")
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR REPLACE INTO dashboard (chat_id, dashboard_type, is_locked) VALUES (?, ?, ?)",
        (chat_id, dashboard_type, int(is_locked)),
    )
    await conn.commit()
async def get_dashboard_status(chat_id: str, dashboard_type: str) -> bool:
    if dashboard_type not in DASHBOARD_TYPES:
        return False
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT is_locked FROM dashboard WHERE chat_id = ? AND dashboard_type = ?",
        (chat_id, dashboard_type),
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            await conn.execute(
                "INSERT INTO dashboard (chat_id, dashboard_type, is_locked) VALUES (?, ?, 0)",
                (chat_id, dashboard_type),
            )
            await conn.commit()
            return False
        return bool(row[0])
async def toggle_dashboard(chat_id: str, dashboard_type: str) -> bool:
    current_status = await get_dashboard_status(chat_id, dashboard_type)
    new_status = not current_status
    await set_dashboard(chat_id, dashboard_type, new_status)
    return new_status
async def get_all_dashboards(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT dashboard_type, is_locked FROM dashboard WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        dashboards = {row[0]: bool(row[1]) for row in rows}
    async with conn.execute(
        "SELECT model, sticker_emoji FROM group_model WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        mode_row = await cursor.fetchone()
        if mode_row:
            text_mode = mode_row[0]
            sticker_emoji = mode_row[1] if mode_row[1] else "😊"
        else:
            text_mode = 1
            sticker_emoji = "😊"
    dashboards["text_mode"] = text_mode
    dashboards["sticker_emoji"] = sticker_emoji
    return dashboards
async def reset_dashboards(chat_id: str):
    conn = await get_db_conn()
    await conn.execute("DELETE FROM dashboard WHERE chat_id = ?", (chat_id,))
    await conn.commit()
async def dashboard_delet_timer(chat_id: str):
    await set_dashboard(chat_id, "delet_timer", True)
async def undashboard_delet_timer(chat_id: str):
    await set_dashboard(chat_id, "delet_timer", False)
async def are_delet_timer_dashboard(chat_id: str) -> bool:
    return await get_dashboard_status(chat_id, "delet_timer")
async def toggle_delet_timer_dashboard(chat_id: str) -> bool:
    return await toggle_dashboard(chat_id, "delet_timer")
async def dashboard_speak_vip(chat_id: str):
    await set_dashboard(chat_id, "speak_vip", True)
async def undashboard_speak_vip(chat_id: str):
    await set_dashboard(chat_id, "speak_vip", False)
async def are_speak_vip_dashboard(chat_id: str) -> bool:
    return await get_dashboard_status(chat_id, "speak_vip")
async def toggle_speak_vip_dashboard(chat_id: str) -> bool:
    return await toggle_dashboard(chat_id, "speak_vip")
async def dashboard_speak(chat_id: str):
    await set_dashboard(chat_id, "speak", True)
async def undashboard_speak(chat_id: str):
    await set_dashboard(chat_id, "speak", False)
async def are_speak_dashboard(chat_id: str) -> bool:
    return await get_dashboard_status(chat_id, "speak")
async def toggle_speak_dashboard(chat_id: str) -> bool:
    return await toggle_dashboard(chat_id, "speak")
async def dashboard_speak_bad(chat_id: str):
    await set_dashboard(chat_id, "speak_bad", True)
async def undashboard_speak_bad(chat_id: str):
    await set_dashboard(chat_id, "speak_bad", False)
async def are_speak_bad_dashboard(chat_id: str) -> bool:
    return await get_dashboard_status(chat_id, "speak_bad")
async def toggle_speak_bad_dashboard(chat_id: str) -> bool:
    return await toggle_dashboard(chat_id, "speak_bad")
async def dashboard_calculator(chat_id: str):
    await set_dashboard(chat_id, "calculator", True)
async def undashboard_calculator(chat_id: str):
    await set_dashboard(chat_id, "calculator", False)
async def are_calculator_dashboard(chat_id: str) -> bool:
    return await get_dashboard_status(chat_id, "calculator")
async def toggle_calculator_dashboard(chat_id: str) -> bool:
    return await toggle_dashboard(chat_id, "calculator")
LOCK_TYPES = [
    "links",
    "media",
    "photos",
    "videos",
    "documents",
    "polls",
    "location",
    "voice",
    "sticker",
    "forward",
    "mention",
    "hashtag",
    "spoiler",
    "english",
    "persian",
    "id",
    "Quote",
    "Bold",
    "Italic",
    "Mono",
    "Strike",
    "Underline",
    "bad",
    "spam",
    "long_text",
    "filter",
]
LOCK_TRANSLATIONS = {
    "links": "لینک‌ها",
    "media": "رسانه",
    "photos": "عکس",
    "videos": "ویدیو",
    "documents": "فایل",
    "polls": "نظرسنجی",
    "location": "موقعیت",
    "voice": "ویس",
    "sticker": "استیکر",
    "forward": "فوروارد",
    "mention": "منشن",
    "hashtag": "هشتگ",
    "spoiler": "اسپویلر",
    "english": "متن انگلیسی",
    "persian": "متن فارسی",
    "id": "ایدی",
    "Quote": "نقل قول",
    "Bold": "برجسته",
    "Italic": "کج",
    "Mono": "تکی",
    "Strike": "خط خورده",
    "Underline": "زیر خط",
    "bad": "متن نامناسب",
    "spam": "اسپم",
    "long_text": "متن بلند",
    "filter": "کد هنگی",
}
async def set_lock(chat_id: str, lock_type: str, is_locked: bool = True):
    if lock_type not in LOCK_TYPES:
        raise ValueError(f"Invalid lock type: {lock_type}")
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR REPLACE INTO locks (chat_id, lock_type, is_locked) VALUES (?, ?, ?)",
        (chat_id, lock_type, int(is_locked)),
    )
    await conn.commit()
async def get_lock_status(chat_id: str, lock_type: str) -> bool:
    if lock_type not in LOCK_TYPES:
        return False
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT is_locked FROM locks WHERE chat_id = ? AND lock_type = ?",
        (chat_id, lock_type),
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row[0]) if row else False
async def toggle_lock(chat_id: str, lock_type: str) -> bool:
    current_status = await get_lock_status(chat_id, lock_type)
    new_status = not current_status
    await set_lock(chat_id, lock_type, new_status)
    return new_status
async def get_all_locks(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT lock_type, is_locked FROM locks WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        return {row[0]: bool(row[1]) for row in rows}
async def reset_locks(chat_id: str):
    conn = await get_db_conn()
    await conn.execute("DELETE FROM locks WHERE chat_id = ?", (chat_id,))
    await conn.commit()
async def handle_lock_command(msg, lang="fa"):
    chat_id = str(msg.chat_id)
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.reply("❌ فرمت صحیح: /lock <نوع>\nمثال: /lock links")
        return
    lock_type = parts[1].lower()
    if lock_type not in LOCK_TYPES:
        await msg.reply(
            f"❌ نوع قفل نامعتبر!\nانواع معتبر: {', '.join(LOCK_TYPES[:5])}..."
        )
        return
    new_status = await toggle_lock(chat_id, lock_type)
    persian_name = LOCK_TRANSLATIONS.get(lock_type, lock_type)
    if new_status:
        await msg.reply(f"🔒 {persian_name} قفل شد")
    else:
        await msg.reply(f"🔓 قفل {persian_name} باز شد")
async def handle_lock_status(
    msg, bot, lang="fa", is_deleted_timer=False, delet_timer=10
):
    chat_id = str(msg.chat_id)
    locks = await get_all_locks(chat_id)
    active_locks = []
    inactive_locks = []
    for lock_type in LOCK_TYPES:
        status = locks.get(lock_type, False)
        persian_name = LOCK_TRANSLATIONS.get(lock_type, lock_type)
        if status:
            active_locks.append(f"🔒 {persian_name}")
        else:
            inactive_locks.append(f"🔓 {persian_name} ")
    text = "🔐 **وضعیت قفل‌های گروه**\n\n"
    if active_locks:
        text += "**قفل‌های فعال:**\n" + "\n".join(active_locks) + "\n\n"
    else:
        text += "**قفل‌های فعال:** ❌\n\n"
    if inactive_locks:
        text += "**قفل‌های غیرفعال:**\n" + "\n".join(inactive_locks[:500])
        if len(inactive_locks) > 500:
            text += f"\n... و {len(inactive_locks) - 10} مورد دیگر"
    await reply(msg, await MPro(text, chat_id), is_deleted_timer, delet_timer)
async def handle_lock_all(msg, lang="fa", is_deleted_timer=False, delet_timer=10):
    chat_id = str(msg.chat_id)
    for lock_type in LOCK_TYPES:
        await set_lock(chat_id, lock_type, True)
    await reply(msg, "🔒 تمام قفل‌ها فعال شدند", is_deleted_timer, delet_timer)
async def handle_unlock_all(msg, lang="fa"):
    chat_id = str(msg.chat_id)
    user_role = await get_user_role(chat_id, str(msg.sender_id))
    if user_role not in ["owner", "admin"]:
        await msg.reply("❌ فقط ادمین‌ها می‌توانند قفل تنظیم کنند")
        return
    await reset_locks(chat_id)
    await msg.reply("🔓 تمام قفل‌ها غیرفعال شدند")
async def lock_spam(chat_id: str):
    await set_lock(chat_id, "spam", True)
async def unlock_spam(chat_id: str):
    await set_lock(chat_id, "spam", False)
async def are_spam_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "spam")
async def toggle_spam_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "spam")
async def lock_long_text(chat_id: str):
    await set_lock(chat_id, "long_text", True)
async def unlock_long_text(chat_id: str):
    await set_lock(chat_id, "long_text", False)
async def are_long_text_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "long_text")
async def toggle_long_text_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "long_text")
async def lock_filter(chat_id: str):
    await set_lock(chat_id, "filter", True)
async def unlock_filter(chat_id: str):
    await set_lock(chat_id, "filter", False)
async def are_filter_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "filter")
async def toggle_filter_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "filter")
async def lock_links(chat_id: str):
    await set_lock(chat_id, "links", True)
async def unlock_links(chat_id: str):
    await set_lock(chat_id, "links", False)
async def are_links_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "links")
async def toggle_links_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "links")
async def lock_bad(chat_id: str):
    await set_lock(chat_id, "bad", True)
async def unlock_bad(chat_id: str):
    await set_lock(chat_id, "bad", False)
async def are_bad_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "bad")
async def toggle_bad_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "bad")
async def lock_Quote(chat_id: str):
    await set_lock(chat_id, "Quote", True)
async def unlock_Quote(chat_id: str):
    await set_lock(chat_id, "Quote", False)
async def is_Quote_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "Quote")
async def toggle_Quote_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "Quote")
async def lock_Bold(chat_id: str):
    await set_lock(chat_id, "Bold", True)
async def unlock_Bold(chat_id: str):
    await set_lock(chat_id, "Bold", False)
async def is_Bold_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "Bold")
async def toggle_Bold_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "Bold")
async def lock_Italic(chat_id: str):
    await set_lock(chat_id, "Italic", True)
async def unlock_Italic(chat_id: str):
    await set_lock(chat_id, "Italic", False)
async def is_Italic_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "Italic")
async def toggle_Italic_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "Italic")
async def lock_Mono(chat_id: str):
    await set_lock(chat_id, "Mono", True)
async def unlock_Mono(chat_id: str):
    await set_lock(chat_id, "Mono", False)
async def is_Mono_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "Mono")
async def toggle_Mono_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "Mono")
async def lock_Strike(chat_id: str):
    await set_lock(chat_id, "Strike", True)
async def unlock_Strike(chat_id: str):
    await set_lock(chat_id, "Strike", False)
async def is_Strike_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "Strike")
async def toggle_Strike_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "Strike")
async def lock_Underline(chat_id: str):
    await set_lock(chat_id, "Underline", True)
async def unlock_Underline(chat_id: str):
    await set_lock(chat_id, "Underline", False)
async def is_Underline_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "Underline")
async def toggle_Underline_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "Underline")
async def lock_media(chat_id: str):
    await set_lock(chat_id, "media", True)
async def unlock_media(chat_id: str):
    await set_lock(chat_id, "media", False)
async def is_media_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "media")
async def toggle_media_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "media")
async def lock_ids(chat_id: str):
    await set_lock(chat_id, "id", True)
async def unlock_ids(chat_id: str):
    await set_lock(chat_id, "id", False)
async def are_ids_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "id")
async def toggle_ids_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "id")
async def lock_photos(chat_id: str):
    await set_lock(chat_id, "photos", True)
async def unlock_photos(chat_id: str):
    await set_lock(chat_id, "photos", False)
async def are_photos_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "photos")
async def toggle_photos_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "photos")
async def lock_videos(chat_id: str):
    await set_lock(chat_id, "videos", True)
async def unlock_videos(chat_id: str):
    await set_lock(chat_id, "videos", False)
async def are_videos_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "videos")
async def toggle_videos_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "videos")
async def lock_documents(chat_id: str):
    await set_lock(chat_id, "documents", True)
async def unlock_documents(chat_id: str):
    await set_lock(chat_id, "documents", False)
async def are_documents_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "documents")
async def toggle_documents_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "documents")
async def lock_polls(chat_id: str):
    await set_lock(chat_id, "polls", True)
async def unlock_polls(chat_id: str):
    await set_lock(chat_id, "polls", False)
async def are_polls_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "polls")
async def toggle_polls_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "polls")
async def lock_contacts(chat_id: str):
    await set_lock(chat_id, "contacts", True)
async def unlock_contacts(chat_id: str):
    await set_lock(chat_id, "contacts", False)
async def are_contacts_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "contacts")
async def toggle_contacts_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "contacts")
async def lock_location(chat_id: str):
    await set_lock(chat_id, "location", True)
async def unlock_location(chat_id: str):
    await set_lock(chat_id, "location", False)
async def is_location_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "location")
async def toggle_location_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "location")
async def lock_voice(chat_id: str):
    await set_lock(chat_id, "voice", True)
async def unlock_voice(chat_id: str):
    await set_lock(chat_id, "voice", False)
async def is_voice_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "voice")
async def toggle_voice_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "voice")
async def lock_sticker(chat_id: str):
    await set_lock(chat_id, "sticker", True)
async def unlock_sticker(chat_id: str):
    await set_lock(chat_id, "sticker", False)
async def is_sticker_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "sticker")
async def toggle_sticker_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "sticker")
async def lock_forward(chat_id: str):
    await set_lock(chat_id, "forward", True)
async def unlock_forward(chat_id: str):
    await set_lock(chat_id, "forward", False)
async def is_forward_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "forward")
async def toggle_forward_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "forward")
async def lock_bot(chat_id: str):
    await set_lock(chat_id, "bot", True)
async def unlock_bot(chat_id: str):
    await set_lock(chat_id, "bot", False)
async def is_bot_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "bot")
async def toggle_bot_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "bot")
async def lock_url(chat_id: str):
    await set_lock(chat_id, "url", True)
async def unlock_url(chat_id: str):
    await set_lock(chat_id, "url", False)
async def is_url_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "url")
async def toggle_url_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "url")
async def lock_mention(chat_id: str):
    await set_lock(chat_id, "mention", True)
async def unlock_mention(chat_id: str):
    await set_lock(chat_id, "mention", False)
async def is_mention_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "mention")
async def toggle_mention_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "mention")
async def lock_hashtag(chat_id: str):
    await set_lock(chat_id, "hashtag", True)
async def unlock_hashtag(chat_id: str):
    await set_lock(chat_id, "hashtag", False)
async def is_hashtag_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "hashtag")
async def toggle_hashtag_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "hashtag")
async def lock_spoiler(chat_id: str):
    await set_lock(chat_id, "spoiler", True)
async def unlock_spoiler(chat_id: str):
    await set_lock(chat_id, "spoiler", False)
async def is_spoiler_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "spoiler")
async def toggle_spoiler_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "spoiler")
async def lock_invite(chat_id: str):
    await set_lock(chat_id, "invite", True)
async def unlock_invite(chat_id: str):
    await set_lock(chat_id, "invite", False)
async def is_invite_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "invite")
async def toggle_invite_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "invite")
async def lock_arabic(chat_id: str):
    await set_lock(chat_id, "arabic", True)
async def unlock_arabic(chat_id: str):
    await set_lock(chat_id, "arabic", False)
async def is_arabic_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "arabic")
async def toggle_arabic_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "arabic")
async def lock_english(chat_id: str):
    await set_lock(chat_id, "english", True)
async def unlock_english(chat_id: str):
    await set_lock(chat_id, "english", False)
async def is_english_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "english")
async def toggle_english_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "english")
async def lock_persian(chat_id: str):
    await set_lock(chat_id, "persian", True)
async def unlock_persian(chat_id: str):
    await set_lock(chat_id, "persian", False)
async def is_persian_locked(chat_id: str) -> bool:
    return await get_lock_status(chat_id, "persian")
async def toggle_persian_lock(chat_id: str) -> bool:
    return await toggle_lock(chat_id, "persian")
async def set_member(
    chat_id: str,
    sender_id: str,
    is_exempt: bool = None,
    original: str = None,
    nickname: str = None,
    sokot: bool = None,
):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT is_exempt, original, nickname, sokot FROM members WHERE chat_id = ? AND sender_id = ?",
        (chat_id, sender_id),
    ) as cursor:
        existing = await cursor.fetchone()
    if existing:
        fields, values = [], []
        if is_exempt is not None:
            fields.append("is_exempt = ?")
            values.append(int(is_exempt))
        if original is not None:
            fields.append("original = ?")
            values.append(original)
        if nickname is not None:
            fields.append("nickname = ?")
            values.append(nickname)
        if sokot is not None:
            fields.append("sokot = ?")
            values.append(int(sokot))
        if fields:
            values.extend([chat_id, sender_id])
            await conn.execute(
                f"UPDATE members SET {', '.join(fields)} WHERE chat_id = ? AND sender_id = ?",
                values,
            )
    else:
        await conn.execute(
            """
            INSERT INTO members (chat_id, sender_id, is_exempt, original, nickname, sokot)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                sender_id,
                int(is_exempt) if is_exempt is not None else 0,
                original,
                nickname,
                int(sokot) if sokot is not None else 0,
            ),
        )
    await conn.commit()
async def get_member_by(chat_id: str, sender_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT is_exempt, original, nickname, sokot FROM members WHERE chat_id = ? AND sender_id = ?",
        (chat_id, sender_id),
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            return False
        return {
            "chat_id": chat_id,
            "sender_id": sender_id,
            "is_exempt": bool(row[0]),
            "original": row[1] if row[1] else None,
            "nickname": row[2] if row[2] else None,
            "sokot": bool(row[3]) if row[3] is not None else False,
        }
async def get_original(chat_id: str, sender_id: str):
    member = await get_member_by(chat_id, sender_id)
    if not member:
        return None
    return member.get("original")
async def get_nickname(chat_id: str, sender_id: str):
    member = await get_member_by(chat_id, sender_id)
    if not member:
        return None
    return member.get("nickname")
async def get_sokot(chat_id: str, sender_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT sokot FROM members WHERE chat_id = ? AND sender_id = ?",
        (chat_id, sender_id),
    ) as cursor:
        row = await cursor.fetchone()
        if row and row[0] is not None:
            return bool(row[0])
    return False
async def update_member(chat_id: str, sender_id: str, **kwargs):
    allowed, fields, values = ["is_exempt", "original", "nickname", "sokot"], [], []
    for k, v in kwargs.items():
        if k in allowed:
            fields.append(f"{k} = ?")
            if k in ["is_exempt", "sokot"]:
                values.append(int(v))
            else:
                values.append(v)
    if not fields:
        return False
    values.extend([chat_id, sender_id])
    conn = await get_db_conn()
    query = (
        f"UPDATE members SET {', '.join(fields)} WHERE chat_id = ? AND sender_id = ?"
    )
    await conn.execute(query, values)
    await conn.commit()
    return True
async def delete_member(chat_id: str, sender_id: str):
    conn = await get_db_conn()
    await conn.execute(
        "DELETE FROM members WHERE chat_id = ? AND sender_id = ?", (chat_id, sender_id)
    )
    await conn.commit()
async def get_all_members(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT sender_id, is_exempt, original, nickname, sokot FROM members WHERE chat_id = ?",
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
    result = []
    for r in rows:
        result.append(
            {
                "sender_id": r[0],
                "is_exempt": bool(r[1]),
                "original": r[2],
                "nickname": r[3],
                "sokot": bool(r[4]),
            }
        )
    return result
async def whois_member(chat_id: str, sender_id: str):
    member = await get_member_by(chat_id, sender_id)
    if not member:
        return "⚠️ این کاربر در دیتابیس ثبت نشده است."
    exempt = "✔️ معاف" if member["is_exempt"] else "❌ غیرمعاف"
    sokot_status = "🔇 ساکت" if member["sokot"] else "🔊 فعال"
    return (
        f"👤 **اطلاعات کاربر:**\n"
        f"🆔 آیدی: `{sender_id}`\n"
        f"📛 لقب: {member['nickname'] or '—'}\n"
        f"📌 مقدار اصلی: {member['original'] or '—'}\n"
        f"🚫 وضعیت معافیت: {exempt}\n"
        f"🔔 وضعیت سکوت: {sokot_status}"
    )
async def set_nickname(chat_id: str, sender_id: str, nickname: str):
    return await update_member(chat_id, sender_id, nickname=nickname)
async def set_original(chat_id: str, sender_id: str, original: str):
    return await update_member(chat_id, sender_id, original=original)
async def exempt_member(chat_id: str, sender_id: str, exempt: bool = True):
    return await update_member(chat_id, sender_id, is_exempt=exempt)
async def set_sokot(chat_id: str, sender_id: str, sokot: bool = True):
    return await update_member(chat_id, sender_id, sokot=sokot)
async def member_list(chat_id: str):
    members = await get_all_members(chat_id)
    if not members:
        return "❌ هیچ عضوی در این گروه ثبت نشده"
    text = "👥 **لیست اعضای ثبت شده:**\n\n"
    for m in members:
        exempt = "✔️" if m["is_exempt"] else "❌"
        sokot_status = "🔇" if m["sokot"] else "🔊"
        nickname = m["nickname"] or "—"
        text += f"🆔 `{m['sender_id']}` | {nickname} | معاف: {exempt} | سکوت: {sokot_status}\n"
    return text
async def is_member_exempt(chat_id: str, sender_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT is_exempt FROM members WHERE chat_id = ? AND sender_id = ?",
        (chat_id, sender_id),
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row[0]) if row else False
async def get_exempt_members(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT sender_id, nickname, original, sokot FROM members WHERE chat_id = ? AND is_exempt = 1",
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        {
            "sender_id": row[0],
            "nickname": row[1] or "بدون لقب",
            "original": row[2] or "بدون مقدار اصلی",
            "sokot": bool(row[3]),
        }
        for row in rows
    ]
async def get_sokot_members(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT sender_id, nickname, original FROM members WHERE chat_id = ? AND sokot = 1",
        (chat_id,),
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        {
            "sender_id": row[0],
            "nickname": row[1] or "بدون لقب",
            "original": row[2] or "بدون مقدار اصلی",
        }
        for row in rows
    ]
async def handle_sokot_list_command(msg, is_deleted_timer, delet_timer):
    chat_id = str(msg.chat_id)
    sokot_members = await get_sokot_members(chat_id)
    if not sokot_members:
        await reply(msg, "📝 هیچ کاربر ساکتی وجود ندارد", is_deleted_timer, delet_timer)
        return
    text = "🔇 **لیست کاربران سکوت:**\n\n"
    for i, member in enumerate(sokot_members, 1):
        text += f"{i}. آیدی: `{member['sender_id']}` - {member['nickname']}\n"
    await reply(msg, text, is_deleted_timer, delet_timer)
async def handle_exempt_list_command(
    msg, lang="fa", is_deleted_timer=False, delet_timer=10
):
    chat_id = str(msg.chat_id)
    exempt_members = await get_exempt_members(chat_id)
    if not exempt_members:
        await reply(msg, "📝 هیچ کاربر معافی وجود ندارد", is_deleted_timer, delet_timer)
        return
    text = "📋 **لیست کاربران معاف:**\n\n"
    for i, member in enumerate(exempt_members, 1):
        sokot = "🔇" if member["sokot"] else "🔊"
        text += f"{i}. آیدی: `{member['sender_id']}` - {member['nickname']} - {sokot}\n"
    await reply(msg, text, is_deleted_timer, delet_timer)
async def get_user_message(chatid):
    conn = await get_db_conn()
    try:
        async with conn.execute(
            "SELECT name, active FROM groups WHERE chat_id = ?", (chatid,)
        ) as cursor:
            group_info = await cursor.fetchone()
        if not group_info:
            return None
        group_name, active = group_info
        async with conn.execute(
            "SELECT role, COUNT(*) FROM group_members WHERE chat_id = ? GROUP BY role",
            (chatid,),
        ) as cursor:
            roles = await cursor.fetchall()
        role_stats = {"owner": 0, "admin": 0, "vip": 0, "member": 0}
        for role, count in roles:
            role_stats[role] = count
        async with conn.execute(
            """
            SELECT user_id, messages, role
            FROM group_members
            WHERE chat_id = ? AND messages > 0
            ORDER BY messages DESC
            """,
            (chatid,),
        ) as cursor:
            top_users = await cursor.fetchall()
        top_users_list = []
        for user_id, messages, role in top_users:
            top_users_list.append(
                {"user_id": user_id, "messages": messages, "role": role}
            )
        return {
            "top_users": top_users_list,
        }
    except Exception as e:
        print(f"Error in get_group_status: {e}")
        return None
async def get_group_status(chat_id: str):
    conn = await get_db_conn()
    try:
        async with conn.execute(
            "SELECT name, active FROM groups WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            group_info = await cursor.fetchone()
        if not group_info:
            return None
        group_name, active = group_info
        async with conn.execute(
            "SELECT role, COUNT(*) FROM group_members WHERE chat_id = ? GROUP BY role",
            (chat_id,),
        ) as cursor:
            roles = await cursor.fetchall()
        role_stats = {"owner": 0, "admin": 0, "vip": 0, "member": 0}
        for role, count in roles:
            role_stats[role] = count
        async with conn.execute(
            """
            SELECT 
                SUM(messages) as total_messages,
                SUM(id) as total_gifs,
                SUM(links) as total_links,
                SUM(media) as total_media,
                SUM(photos) as total_photos,
                SUM(videos) as total_videos,
                SUM(documents) as total_documents,
                SUM(polls) as total_polls,
                SUM(location) as total_location,
                SUM(voice) as total_voice,
                SUM(sticker) as total_sticker,
                SUM(forward) as total_forward,
                SUM(hashtag) as total_hashtag,
                SUM(english) as total_english,
                SUM(persian) as total_persian
            FROM group_members
            WHERE chat_id = ?
            """,
            (chat_id,),
        ) as cursor:
            stats = await cursor.fetchone()
        async with conn.execute(
            """
            SELECT user_id, messages, role
            FROM group_members
            WHERE chat_id = ? AND messages > 0
            ORDER BY messages DESC
            LIMIT 10
            """,
            (chat_id,),
        ) as cursor:
            top_users = await cursor.fetchall()
        top_users_list = []
        for user_id, messages, role in top_users:
            top_users_list.append(
                {"user_id": user_id, "messages": messages, "role": role}
            )
        return {
            "group_name": group_name,
            "active": bool(active),
            "roles": role_stats,
            "stats": {
                "messages": stats[0] or 0,
                "gifs": stats[1] or 0,
                "links": stats[2] or 0,
                "media": stats[3] or 0,
                "photos": stats[4] or 0,
                "videos": stats[5] or 0,
                "documents": stats[6] or 0,
                "polls": stats[7] or 0,
                "location": stats[8] or 0,
                "voice": stats[9] or 0,
                "sticker": stats[10] or 0,
                "forward": stats[11] or 0,
                "hashtag": stats[12] or 0,
                "english": stats[13] or 0,
                "persian": stats[14] or 0,
            },
            "top_users": top_users_list,
            "total_members": sum(role_stats.values()),
        }
    except Exception as e:
        print(f"Error in get_group_status: {e}")
        return None
def message_type(msg: dict):
    raw = msg.get("raw_data", {})
    meta = raw.get("metadata", {})
    if meta.get("meta_data_parts"):
        meta_type = meta["meta_data_parts"][0].get("type")
        return f"{meta_type}"
    if msg.get("text") and msg["text"].startswith("http"):
        return "link"
    if "sticker" in raw:
        return "sticker"
    if raw.get("forwarded_from"):
        return "forward"
    if "gif" in raw:
        return "gif"
    if raw.get("text"):
        return "text"
    if "file" in raw:
        filename = raw["file"].get("file_name", "").lower()
        if filename.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
            return "photo"
        if filename.endswith((".mp4", ".mkv", ".avi", ".mov")):
            return "video"
        if filename.endswith((".ogg", ".opus")):
            return "voice"
        if filename.endswith((".mp3", ".wav", ".flac", ".m4a")):
            return "audio"
        return "file"
    if "location" in raw:
        return "location"
    if "poll" in raw:
        return "poll"
    return "unknown"
async def check_locks(bot, message):
    chat_id = str(message.chat_id)
    text = message.text or ""
    if await are_links_locked(chat_id):
        if any(link in text for link in ["http", "t.me", "www."]):
            await delete_and_warn(bot, message, "لینک")
            return True
    if await get_lock_status(chat_id, "location") and message.location:
        await delete_and_warn(bot, message, "موقعیت")
        return True
    if await get_lock_status(chat_id, "voice") and message.voice:
        await delete_and_warn(bot, message, "ویس")
        return True
    if await get_lock_status(chat_id, "photos") and message.photo:
        await delete_and_warn(bot, message, "عکس")
        return True
    return False
async def delete_and_warn(bot, message, lock_type):
    try:
        await bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        await message.reply(f"❌ ارسال {lock_type} در این گروه ممنوع است!")
    except Exception as e:
        print(f"Error deleting message: {e}")
def contains_arabic(text):
    arabic_range = range(0x0600, 0x06FF)
    return any(ord(char) in arabic_range for char in text)
async def set_group_model(chat_id: str, model: int):
    conn = await get_db_conn()
    await conn.execute(
        """
        INSERT OR REPLACE INTO group_model (chat_id, model)
        VALUES (?, ?)
    """,
        (chat_id, model),
    )
    await conn.commit()
async def get_group_model(chat_id: str) -> int:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT model FROM group_model WHERE chat_id = ?", (chat_id,)
    ) as c:
        row = await c.fetchone()
        return row[0] if row else 0
async def get_group_sticker_emoji(chat_id: str) -> str:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT sticker_emoji FROM group_model WHERE chat_id = ?", (chat_id,)
    ) as c:
        row = await c.fetchone()
        if row and row[0]:
            return row[0]
        return "🐉"
async def set_group_sticker_emoji(chat_id: str, emoji: str) -> bool:
    if not emoji or len(emoji.strip()) == 0:
        emoji = "🐉"
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT 1 FROM group_model WHERE chat_id = ?", (chat_id,)
    ) as c:
        exists = await c.fetchone()
    if exists:
        await conn.execute(
            "UPDATE group_model SET sticker_emoji = ? WHERE chat_id = ?",
            (emoji, chat_id),
        )
    else:
        await conn.execute(
            "INSERT INTO group_model (chat_id, model, sticker_emoji) VALUES (?, ?, ?)",
            (chat_id, 0, emoji),
        )
    await conn.commit()
    return True
async def remove_group_sticker_emoji(chat_id: str) -> bool:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT 1 FROM group_model WHERE chat_id = ?", (chat_id,)
    ) as c:
        exists = await c.fetchone()
    if exists:
        await conn.execute(
            "UPDATE group_model SET sticker_emoji = '🐉' WHERE chat_id = ?", (chat_id,)
        )
        await conn.commit()
        return True
    return False
async def add_note(chat_id: str, text: str):
    conn = await get_db_conn()
    date = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    await conn.execute(
        """
        INSERT INTO group_notes (chat_id, text, date)
        VALUES (?, ?, ?)
    """,
        (chat_id, text, date),
    )
    await conn.commit()
async def get_notes(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        """
        SELECT id, text, date 
        FROM group_notes 
        WHERE chat_id = ?
        ORDER BY id DESC
    """,
        (chat_id,),
    ) as c:
        return [{"id": r[0], "text": r[1], "date": r[2]} for r in await c.fetchall()]
async def delete_note(chat_id: str, note_id: int):
    conn = await get_db_conn()
    await conn.execute(
        """
        DELETE FROM group_notes 
        WHERE id = ? AND chat_id = ?
    """,
        (note_id, chat_id),
    )
    await conn.commit()
async def add_timer(chat_id: str, text: str, run_time: str):
    conn = await get_db_conn()
    await conn.execute(
        """
        INSERT INTO group_timers (chat_id, text, run_time)
        VALUES (?, ?, ?)
    """,
        (chat_id, text, run_time),
    )
    await conn.commit()
async def get_timers(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        """
        SELECT id, text, run_time
        FROM group_timers
        WHERE chat_id = ?
        ORDER BY id DESC
    """,
        (chat_id,),
    ) as c:
        rows = await c.fetchall()
        return [{"id": r[0], "text": r[1], "time": r[2]} for r in rows]
async def delete_timer(chat_id: str, timer_id: int):
    conn = await get_db_conn()
    await conn.execute(
        """
        DELETE FROM group_timers
        WHERE id = ? AND chat_id = ?
    """,
        (timer_id, chat_id),
    )
    await conn.commit()
LOCK_TYPESS = [
    "time",
    "tas",
    "seke",
    "random_num",
    "chalesh",
    "bio",
    "hadis",
    "danetani",
    "jok",
    "dastan",
    "dialog",
    "fal",
    "gazal",
    "fake",
    "list",
    "list_sar",
    "gpt",
    "currency",
    "coin",
    "gold",
    "gimat",
    "trans",
    "font",
    "date",
    "qr_code"
]
LOCK_TRANSLATIONSS = {
    "time": "ساعت",
    "tas": "تاس",
    "seke": "سکه",
    "random_num": "عدد شانسی",
    "chalesh": "چالش",
    "bio": "بیو",
    "hadis": "حدیث",
    "danetani": "دانستنی",
    "jok": "جوک",
    "dastan": "داستان",
    "dialog": "دیالوگ",
    "fal": "فال",
    "gazal": "غزل",
    "fake": "فیک",
    "list": "لیست",
    "list_sar": "لیست سرگرمی",
    "gpt": "چت جی پی تی",
    "currency": "ارز",
    "coin": "سکه",
    "gold": "طلا",
    "gimat": "ارز دیجیتال",
    "trans": "ترجمه",
    "font": "فونت",
    "date" : "تاریخ",
    "qr_code" : "کیو ار کد"
}
async def set_entertainment_lock(chat_id: str, lock_type: str, is_locked: bool = True):
    if lock_type not in LOCK_TYPESS:
        raise ValueError(f"Invalid lockثث type: {lock_type}")
    conn = await get_db_conn()
    await conn.execute(
        "INSERT OR REPLACE INTO sargarmi_lock (chat_id, lock_type, is_locked) VALUES (?, ?, ?)",
        (chat_id, lock_type, int(is_locked)),
    )
    await conn.commit()
async def get_entertainment_lock_status(chat_id: str, lock_type: str) -> bool:
    if lock_type not in LOCK_TYPESS:
        return False
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT is_locked FROM sargarmi_lock WHERE chat_id = ? AND lock_type = ?",
        (chat_id, lock_type),
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row[0]) if row else False
async def toggle_entertainment_lock(chat_id: str, lock_type: str) -> bool:
    current_status = await get_entertainment_lock_status(chat_id, lock_type)
    new_status = not current_status
    await set_entertainment_lock(chat_id, lock_type, new_status)
    return new_status
async def get_all_entertainment_locks(chat_id: str):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT lock_type, is_locked FROM sargarmi_lock WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        return {row[0]: bool(row[1]) for row in rows}
async def reset_entertainment_locks(chat_id: str):
    conn = await get_db_conn()
    await conn.execute("DELETE FROM sargarmi_lock WHERE chat_id = ?", (chat_id,))
    await conn.commit()
async def handle_entertainment_lock_command(msg, lang="fa"):
    chat_id = str(msg.chat_id)
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.reply(
            "❌ فرمت صحیح: /lock_entertainment <نوع>\nمثال: /lock_entertainment tas"
        )
        return
    lock_type = parts[1].lower()
    if lock_type not in LOCK_TYPESS:
        await msg.reply(
            f"❌ نوع قفل نامعتبر!\nانواع معتبر: {', '.join(LOCK_TYPESS[:5])}..."
        )
        return
    new_status = await toggle_entertainment_lock(chat_id, lock_type)
    persian_name = LOCK_TRANSLATIONSS.get(lock_type, lock_type)
    if new_status:
        await msg.reply(f"🔒 {persian_name} قفل شد")
    else:
        await msg.reply(f"🔓 قفل {persian_name} باز شد")
async def handle_entertainment_lock_status(
    msg, bot, lang="fa", is_deleted_timer=False, delet_timer=10
):
    chat_id = str(msg.chat_id)
    locks = await get_all_entertainment_locks(chat_id)
    active_locks = []
    inactive_locks = []
    for lock_type in LOCK_TYPESS:
        status = locks.get(lock_type, False)
        persian_name = LOCK_TRANSLATIONSS.get(lock_type, lock_type)
        if status:
            active_locks.append(f"✅ {persian_name}")
        else:
            inactive_locks.append(f"❌ {persian_name}")
    text = "🔐 **وضعیت قفل‌های سرگرمی گروه**\n\n"
    if active_locks:
        text += "**قفل‌های فعال:**\n" + "\n".join(active_locks) + "\n\n"
    else:
        text += "**قفل‌های فعال:** ❌\n\n"
    if inactive_locks:
        text += "**قفل‌های غیرفعال:**\n" + "\n".join(inactive_locks[:500])
        if len(inactive_locks) > 500:
            text += f"\n... و {len(inactive_locks) - 10} مورد دیگر"
    await reply(msg, await MPro(text, chat_id), is_deleted_timer, delet_timer)
async def lock_qr_code(chat_id: str):
    await set_entertainment_lock(chat_id, "qr_code", True)
async def unlock_qr_code(chat_id: str):
    await set_entertainment_lock(chat_id, "qr_code", False)
async def is_qr_code_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "qr_code")
async def lock_date(chat_id: str):
    await set_entertainment_lock(chat_id, "date", True)
async def unlock_date(chat_id: str):
    await set_entertainment_lock(chat_id, "date", False)
async def is_date_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "date")
async def lock_font(chat_id: str):
    await set_entertainment_lock(chat_id, "font", True)
async def unlock_font(chat_id: str):
    await set_entertainment_lock(chat_id, "font", False)
async def is_font_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "font")
async def lock_gpt(chat_id: str):
    await set_entertainment_lock(chat_id, "gpt", True)
async def unlock_gpt(chat_id: str):
    await set_entertainment_lock(chat_id, "gpt", False)
async def is_gpt_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "gpt")
async def toggle_gpt_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "gpt")
async def lock_gold(chat_id: str):
    await set_entertainment_lock(chat_id, "gold", True)
async def unlock_gold(chat_id: str):
    await set_entertainment_lock(chat_id, "gold", False)
async def is_gold_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "gold")
async def toggle_gold_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "gold")
async def lock_coin(chat_id: str):
    await set_entertainment_lock(chat_id, "coin", True)
async def unlock_coin(chat_id: str):
    await set_entertainment_lock(chat_id, "coin", False)
async def is_coin_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "coin")
async def toggle_coin_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "coin")
async def lock_currency(chat_id: str):
    await set_entertainment_lock(chat_id, "currency", True)
async def unlock_currency(chat_id: str):
    await set_entertainment_lock(chat_id, "currency", False)
async def is_currency_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "currency")
async def toggle_currency_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "currency")
async def lock_time(chat_id: str):
    await set_entertainment_lock(chat_id, "time", True)
async def unlock_time(chat_id: str):
    await set_entertainment_lock(chat_id, "time", False)
async def is_time_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "time")
async def toggle_time_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "time")
async def lock_tas(chat_id: str):
    await set_entertainment_lock(chat_id, "tas", True)
async def unlock_tas(chat_id: str):
    await set_entertainment_lock(chat_id, "tas", False)
async def is_tas_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "tas")
async def toggle_tas_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "tas")
async def lock_seke(chat_id: str):
    await set_entertainment_lock(chat_id, "seke", True)
async def unlock_seke(chat_id: str):
    await set_entertainment_lock(chat_id, "seke", False)
async def is_seke_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "seke")
async def toggle_seke_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "seke")
async def lock_random_num(chat_id: str):
    await set_entertainment_lock(chat_id, "random_num", True)
async def unlock_random_num(chat_id: str):
    await set_entertainment_lock(chat_id, "random_num", False)
async def is_random_num_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "random_num")
async def toggle_random_num_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "random_num")
async def lock_chalesh(chat_id: str):
    await set_entertainment_lock(chat_id, "chalesh", True)
async def unlock_chalesh(chat_id: str):
    await set_entertainment_lock(chat_id, "chalesh", False)
async def is_chalesh_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "chalesh")
async def toggle_chalesh_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "chalesh")
async def lock_bio(chat_id: str):
    await set_entertainment_lock(chat_id, "bio", True)
async def unlock_bio(chat_id: str):
    await set_entertainment_lock(chat_id, "bio", False)
async def is_bio_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "bio")
async def toggle_bio_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "bio")
async def lock_hadis(chat_id: str):
    await set_entertainment_lock(chat_id, "hadis", True)
async def unlock_hadis(chat_id: str):
    await set_entertainment_lock(chat_id, "hadis", False)
async def is_hadis_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "hadis")
async def toggle_hadis_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "hadis")
async def lock_danetani(chat_id: str):
    await set_entertainment_lock(chat_id, "danetani", True)
async def unlock_danetani(chat_id: str):
    await set_entertainment_lock(chat_id, "danetani", False)
async def is_danetani_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "danetani")
async def toggle_danetani_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "danetani")
async def lock_jok(chat_id: str):
    await set_entertainment_lock(chat_id, "jok", True)
async def unlock_jok(chat_id: str):
    await set_entertainment_lock(chat_id, "jok", False)
async def is_jok_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "jok")
async def toggle_jok_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "jok")
async def lock_dastan(chat_id: str):
    await set_entertainment_lock(chat_id, "dastan", True)
async def unlock_dastan(chat_id: str):
    await set_entertainment_lock(chat_id, "dastan", False)
async def is_dastan_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "dastan")
async def toggle_dastan_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "dastan")
async def lock_dialog(chat_id: str):
    await set_entertainment_lock(chat_id, "dialog", True)
async def unlock_dialog(chat_id: str):
    await set_entertainment_lock(chat_id, "dialog", False)
async def is_dialog_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "dialog")
async def toggle_dialog_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "dialog")
async def lock_fal(chat_id: str):
    await set_entertainment_lock(chat_id, "fal", True)
async def unlock_fal(chat_id: str):
    await set_entertainment_lock(chat_id, "fal", False)
async def is_fal_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "fal")
async def toggle_fal_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "fal")
async def lock_gazal(chat_id: str):
    await set_entertainment_lock(chat_id, "gazal", True)
async def unlock_gazal(chat_id: str):
    await set_entertainment_lock(chat_id, "gazal", False)
async def is_gazal_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "gazal")
async def toggle_gazal_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "gazal")
async def lock_fake(chat_id: str):
    await set_entertainment_lock(chat_id, "fake", True)
async def unlock_fake(chat_id: str):
    await set_entertainment_lock(chat_id, "fake", False)
async def is_fake_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "fake")
async def toggle_fake_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "fake")
async def lock_list(chat_id: str):
    await set_entertainment_lock(chat_id, "list", True)
async def unlock_list(chat_id: str):
    await set_entertainment_lock(chat_id, "list", False)
async def is_list_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "list")
async def toggle_list_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "list")
async def lock_gimat(chat_id: str):
    await set_entertainment_lock(chat_id, "gimat", True)
async def unlock_gimat(chat_id: str):
    await set_entertainment_lock(chat_id, "gimat", False)
async def is_gimat_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "gimat")
async def lock_trans(chat_id: str):
    await set_entertainment_lock(chat_id, "trans", True)
async def unlock_trans(chat_id: str):
    await set_entertainment_lock(chat_id, "trans", False)
async def is_trans_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "trans")
async def lock_list_sar(chat_id: str):
    await set_entertainment_lock(chat_id, "list_sar", True)
async def unlock_list_sar(chat_id: str):
    await set_entertainment_lock(chat_id, "list_sar", False)
async def is_list_sar_locked(chat_id: str) -> bool:
    return await get_entertainment_lock_status(chat_id, "list_sar")
async def toggle_list_sar_lock(chat_id: str) -> bool:
    return await toggle_entertainment_lock(chat_id, "list_sar")
class ReportGenerator:
    @staticmethod
    async def generate_group_report(chat_id: str, period_days: int = 30) -> str:
        report_parts = []
        basic_info = await ReportGenerator.get_basic_group_info(chat_id)
        report_parts.append(basic_info)
        messages_stats = await ReportGenerator.get_messages_statistics(
            chat_id, period_days
        )
        report_parts.append(messages_stats)
        members_stats = await ReportGenerator.get_members_statistics(chat_id)
        report_parts.append(members_stats)
        activity_stats = await ReportGenerator.get_activity_statistics(
            chat_id, period_days
        )
        report_parts.append(activity_stats)
        settings_stats = await ReportGenerator.get_settings_statistics(chat_id)
        report_parts.append(settings_stats)
        summary = await ReportGenerator.get_report_summary(
            chat_id,
            {
                "basic": basic_info,
                "messages": messages_stats,
                "members": members_stats,
                "activity": activity_stats,
                "settings": settings_stats,
            },
        )
        report_parts.append(summary)
        return "\n" + "═" * 15 + "\n".join(report_parts)
    @staticmethod
    async def get_basic_group_info(chat_id: str) -> str:
        conn = await get_db_conn()
        info_text = "\n📋 **اطلاعات گروه**\n"
        info_text += "═" * 15 + "\n"
        async with conn.execute(
            "SELECT name, active FROM groups WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            group_row = await cursor.fetchone()
        if group_row:
            name, active = group_row
            status = "✅ فعال" if active else "❌ غیرفعال"
            info_text += f"🏷️ نام گروه: {name}\n"
            info_text += f"📊 وضعیت: {status}\n"
        async with conn.execute(
            """
            SELECT MIN(time) FROM (
                SELECT created_at as time FROM broadcast_messages WHERE sender_chat_id = ?
                UNION
                SELECT join_time as time FROM users WHERE chat_id = ?
                UNION
                SELECT time as time FROM tickets WHERE chat_id = ?
            ) WHERE time IS NOT NULL
            """,
            (chat_id, chat_id, chat_id),
        ) as cursor:
            first_date_row = await cursor.fetchone()
        if first_date_row and first_date_row[0]:
            try:
                gregorian_date = datetime.strptime(
                    first_date_row[0], "%Y-%m-%d %H:%M:%S"
                )
                jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
                info_text += f"📅 تاریخ ایجاد: {jalali_date.strftime('%Y/%m/%d')}\n"
            except:
                info_text += f"📅 تاریخ ایجاد: {first_date_row[0]}\n"
        days_active = await ReportGenerator.get_days_active(chat_id)
        info_text += f"⏳ روزهای فعالیت: {days_active} روز\n"
        return info_text
    @staticmethod
    async def get_messages_statistics(chat_id: str, period_days: int) -> str:
        conn = await get_db_conn()
        stats_text = "\n📊 **آمار پیام‌ها**\n"
        stats_text += "═" * 15 + "\n"
        total_messages = 0
        stats_data = {}
        async with conn.execute(
            """
            SELECT 
                SUM(messages) as total,
                SUM(links) as links,
                SUM(media) as media,
                SUM(photos) as photos,
                SUM(videos) as videos,
                SUM(documents) as documents,
                SUM(polls) as polls,
                SUM(location) as location,
                SUM(voice) as voice,
                SUM(sticker) as sticker,
                SUM(forward) as forward,
                SUM(hashtag) as hashtag,
                SUM(english) as english,
                SUM(persian) as persian
            FROM group_members 
            WHERE chat_id = ?
            """,
            (chat_id,),
        ) as cursor:
            row = await cursor.fetchone()
        if row:
            stats_data = {
                "کل پیام‌ها": row[0] or 0,
                "لینک‌ها": row[1] or 0,
                "رسانه": row[2] or 0,
                "عکس‌ها": row[3] or 0,
                "ویدیوها": row[4] or 0,
                "فایل‌ها": row[5] or 0,
                "نظرسنجی": row[6] or 0,
                "موقعیت": row[7] or 0,
                "ویس": row[8] or 0,
                "استیکر": row[9] or 0,
                "فوروارد": row[10] or 0,
                "هشتگ": row[11] or 0,
                "انگلیسی": row[12] or 0,
                "فارسی": row[13] or 0,
            }
            total_messages = stats_data["کل پیام‌ها"]
        for key, value in stats_data.items():
            if total_messages > 0 and key != "کل پیام‌ها" and value > 0:
                percentage = (value / total_messages) * 100
                stats_text += f"• {key}: {value:,}  -({percentage:.1f}%)\n"
        return stats_text
    @staticmethod
    async def get_members_statistics(chat_id: str) -> str:
        conn = await get_db_conn()
        members_text = "\n👥 **آمار اعضا**\n"
        members_text += "═" * 15 + "\n"
        total_members = await ReportGenerator.get_total_members_count(chat_id)
        if total_members == 0:
            return members_text + "⚠️ هیچ عضوی ثبت نشده است\n"
        roles_stats = {}
        async with conn.execute(
            "SELECT role, COUNT(*) FROM group_members WHERE chat_id = ? GROUP BY role",
            (chat_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            for role, count in rows:
                roles_stats[role] = count
        role_translations = {
            "owner": "مالک",
            "admin": "ادمین",
            "vip": "ویژه",
            "member": "عضو عادی",
        }
        for role_en, role_fa in role_translations.items():
            count = roles_stats.get(role_en, 0)
            percentage = (count / total_members) * 100 if total_members > 0 else 0
            members_text += f"• {role_fa}: {count}  -({percentage:.1f}%)\n"
        return members_text
    @staticmethod
    async def get_activity_statistics(chat_id: str, period_days: int) -> str:
        activity_text = "\n📈 **آمار فعالیت**\n"
        activity_text += "═" * 15 + "\n"
        days_active = await ReportGenerator.get_days_active(chat_id)
        total_messages = await ReportGenerator.get_total_messages(chat_id)
        if days_active > 0:
            avg_daily = total_messages / days_active
            activity_text += f"📅 میانگین روزانه: {avg_daily:.1f} پیام\n"
        total_members = await ReportGenerator.get_total_members_count(chat_id)
        if total_members > 0:
            avg_per_member = total_messages / total_members
            activity_text += f"📊 میانگین هر کاربر: {avg_per_member:.1f} پیام\n"
        return activity_text
    @staticmethod
    async def get_settings_statistics(chat_id: str) -> str:
        settings_text = "\n⚙️ **آمار تنظیمات**\n"
        settings_text += "═" * 15 + "\n"
        dashboards = await get_all_dashboards(chat_id)
        dashboard_count = 0
        active_dashboards = 0
        for key, value in dashboards.items():
            if key not in ["text_mode", "sticker_emoji"]:
                dashboard_count += 1
                if value:
                    active_dashboards += 1
        if dashboard_count > 0:
            percentage = (active_dashboards / dashboard_count) * 100
            settings_text += f"📊 داشبورد فعال: {active_dashboards}/{dashboard_count}  -({percentage:.1f}%)\n"
        locks = await get_all_locks(chat_id)
        total_locks = len(LOCK_TYPES)
        active_locks = sum(1 for lock_type in LOCK_TYPES if locks.get(lock_type, False))
        if total_locks > 0:
            percentage = (active_locks / total_locks) * 100
            settings_text += (
                f"🔒 قفل‌های فعال: {active_locks}/{total_locks}  -({percentage:.1f}%)\n"
            )
        entertainment_locks = await get_all_entertainment_locks(chat_id)
        total_entertainment = len(LOCK_TYPESS)
        active_entertainment = sum(
            1 for lock_type in LOCK_TYPESS if entertainment_locks.get(lock_type, False)
        )
        if total_entertainment > 0:
            percentage = (active_entertainment / total_entertainment) * 100
            settings_text += f"🎮 قفل سرگرمی: {active_entertainment}/{total_entertainment}  -({percentage:.1f}%)\n"
        return settings_text
    @staticmethod
    async def get_report_summary(chat_id: str, data: dict) -> str:
        summary_text = "\n📝 **گزارش**\n"
        summary_text += "═" * 15 + "\n"
        now = jdatetime.datetime.now()
        summary_text += f"\n📅 تاریخ گزارش: {now.strftime('%Y/%m/%d %H:%M')}"
        return summary_text
    @staticmethod
    async def get_total_members_count(chat_id: str) -> int:
        conn = await get_db_conn()
        async with conn.execute(
            "SELECT COUNT(*) FROM group_members WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            return (await cursor.fetchone())[0] or 0
    @staticmethod
    async def get_days_active(chat_id: str) -> int:
        conn = await get_db_conn()
        async with conn.execute(
            """
            SELECT COUNT(DISTINCT DATE(time)) FROM (
                SELECT created_at as time FROM broadcast_messages WHERE sender_chat_id = ?
                UNION
                SELECT time as time FROM tickets WHERE chat_id = ?
            ) WHERE time IS NOT NULL
            """,
            (chat_id, chat_id),
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] or 0 if result else 0
    @staticmethod
    async def get_total_messages(chat_id: str) -> int:
        conn = await get_db_conn()
        async with conn.execute(
            "SELECT SUM(messages) FROM group_members WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] or 0 if result else 0
async def upgrade_database():
    conn = await get_db_conn()
    try:
        async with conn.execute("PRAGMA table_info(group_model)") as cursor:
            columns = [col[1] for col in await cursor.fetchall()]
        if "sticker_emoji" not in columns:
            await conn.execute(
                "ALTER TABLE group_model ADD COLUMN sticker_emoji TEXT DEFAULT '😊'"
            )
            await conn.commit()
    except Exception as e:
        print(f"❌ خطا در آپگرید دیتابیس: {e}")
async def add_warning(chat_id: str, user_id: str, reason: str = None):
    conn = await get_db_conn()
    max_warnings = await get_group_max_warnings(chat_id)
    penalty_type = await get_group_penalty_type(chat_id)
    async with conn.execute(
        "SELECT warnings_count FROM warnings WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    ) as cursor:
        row = await cursor.fetchone()
    now = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")
    if row:
        current_warnings = row[0]
        new_warnings = current_warnings + 1
        await conn.execute(
            """
            UPDATE warnings 
            SET warnings_count = ?, last_warning_time = ?
            WHERE chat_id = ? AND user_id = ?
            """,
            (new_warnings, now, chat_id, user_id),
        )
        if new_warnings >= max_warnings:
            await reset_warnings(chat_id, user_id)
            return {
                "status": "max_reached",
                "current": new_warnings,
                "max": max_warnings,
                "penalty_type": penalty_type,
                "action": penalty_type,
            }
        await conn.commit()
        return {
            "status": "added",
            "current": new_warnings,
            "max": max_warnings,
            "reason": reason,
        }
    else:
        await conn.execute(
            """
            INSERT INTO warnings (chat_id, user_id, warnings_count, last_warning_time)
            VALUES (?, ?, 1, ?)
            """,
            (chat_id, user_id, now),
        )
        await conn.commit()
        if 1 >= max_warnings:
            await reset_warnings(chat_id, user_id)
            return {
                "status": "max_reached",
                "current": 1,
                "max": max_warnings,
                "penalty_type": penalty_type,
                "action": penalty_type,
            }
        return {"status": "added", "current": 1, "max": max_warnings, "reason": reason}
async def remove_warning(chat_id: str, user_id: str, count: int = 1):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT warnings_count FROM warnings WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    ) as cursor:
        row = await cursor.fetchone()
    if row:
        current_warnings = row[0]
        new_warnings = max(0, current_warnings - count)
        if new_warnings == 0:
            await conn.execute(
                "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id),
            )
        else:
            await conn.execute(
                "UPDATE warnings SET warnings_count = ? WHERE chat_id = ? AND user_id = ?",
                (new_warnings, chat_id, user_id),
            )
        await conn.commit()
        return {
            "status": "removed",
            "current": new_warnings,
            "removed": min(count, current_warnings),
            "user_deleted": new_warnings == 0,
        }
    return {"status": "not_found"}
async def reset_warnings(chat_id: str, user_id: str = None):
    conn = await get_db_conn()
    if user_id:
        await conn.execute(
            "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
        )
    else:
        await conn.execute("DELETE FROM warnings WHERE chat_id = ?", (chat_id,))
    await conn.commit()
    if user_id:
        return {"status": "reset", "user_id": user_id}
    else:
        return {"status": "reset_all", "chat_id": chat_id}
async def get_warnings(chat_id: str, user_id: str = None):
    conn = await get_db_conn()
    if user_id:
        async with conn.execute(
            "SELECT warnings_count, last_warning_time FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                max_warnings = await get_group_max_warnings(chat_id)
                return {
                    "user_id": user_id,
                    "warnings": row[0],
                    "max": max_warnings,
                    "last_warning": row[1],
                }
            return None
    else:
        max_warnings = await get_group_max_warnings(chat_id)
        async with conn.execute(
            "SELECT user_id, warnings_count, last_warning_time FROM warnings WHERE chat_id = ?",
            (chat_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "user_id": row[0],
                    "warnings": row[1],
                    "max": max_warnings,
                    "last_warning": row[2],
                }
                for row in rows
            ]
async def set_group_warning_settings(
    chat_id: str, max_warnings: int = 3, penalty_type: str = "ban"
):
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT 1 FROM group_settings WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        exists = await cursor.fetchone()
    if exists:
        await conn.execute(
            "UPDATE group_settings SET max_warnings = ?, penalty_type = ? WHERE chat_id = ?",
            (max_warnings, penalty_type, chat_id),
        )
    else:
        await conn.execute(
            "INSERT INTO group_settings (chat_id, max_warnings, penalty_type) VALUES (?, ?, ?)",
            (chat_id, max_warnings, penalty_type),
        )
    await conn.commit()
    return {
        "status": "updated",
        "max_warnings": max_warnings,
        "penalty_type": penalty_type,
    }
async def get_group_max_warnings(chat_id: str) -> int:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT max_warnings FROM group_settings WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if row and row[0]:
        return row[0]
    return 3
async def get_group_penalty_type(chat_id: str) -> str:
    conn = await get_db_conn()
    async with conn.execute(
        "SELECT penalty_type FROM group_settings WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if row and row[0]:
        return row[0]
    return "ban"
async def get_warning_stats(chat_id: str):
    conn = await get_db_conn()
    max_warnings = await get_group_max_warnings(chat_id)
    penalty_type = await get_group_penalty_type(chat_id)
    async with conn.execute(
        "SELECT COUNT(*) FROM warnings WHERE chat_id = ? AND warnings_count > 0",
        (chat_id,),
    ) as cursor:
        warned_users = (await cursor.fetchone())[0]
    async with conn.execute(
        "SELECT SUM(warnings_count) FROM warnings WHERE chat_id = ?", (chat_id,)
    ) as cursor:
        total_warnings = (await cursor.fetchone())[0] or 0
    async with conn.execute(
        """
        SELECT user_id, warnings_count 
        FROM warnings 
        WHERE chat_id = ? AND warnings_count >= ?
        """,
        (chat_id, max_warnings - 1),
    ) as cursor:
        near_penalty = await cursor.fetchall()
    async with conn.execute(
        """
        SELECT user_id, warnings_count 
        FROM warnings 
        WHERE chat_id = ? AND warnings_count >= ?
        """,
        (chat_id, max_warnings),
    ) as cursor:
        max_reached = await cursor.fetchall()
    return {
        "max_warnings": max_warnings,
        "penalty_type": penalty_type,
        "total_warned_users": warned_users,
        "total_warnings": total_warnings,
        "near_penalty_users": [
            {"user_id": row[0], "warnings": row[1], "remaining": max_warnings - row[1]}
            for row in near_penalty
        ],
        "max_reached_users": [
            {"user_id": row[0], "warnings": row[1]} for row in max_reached
        ],
    }
async def apply_penalty(
    bot, chat_id: str, user_id: str, penalty_type: str, duration: int = None
):
    try:
        if penalty_type == "ban":
            return {"status": "banned", "user_id": user_id}
        elif penalty_type == "mute":
            mute_duration = duration or 3600
            await set_sokot(chat_id, user_id, True)
            return {"status": "muted", "user_id": user_id, "duration": mute_duration}
        else:
            return {"status": "unknown_penalty", "penalty_type": penalty_type}
    except Exception as e:
        print(f"Error applying penalty: {e}")
        return {"status": "error", "error": str(e)}
async def get_user_owned_groups(sender_id: str) -> list:
    conn = await get_db_conn()
    async with conn.execute(
        """
        SELECT g.chat_id, g.name, g.active
        FROM groups g
        INNER JOIN group_members gm ON g.chat_id = gm.chat_id
        WHERE gm.user_id = ? AND gm.role = 'owner'
        ORDER BY g.name
        """,
        (sender_id,),
    ) as cursor:
        rows = await cursor.fetchall()
    groups = []
    for row in rows:
        groups.append(
            {
                "chat_id": row[0],
                "name": row[1] if row[1] else "بدون نام",
                "active": bool(row[2]),
            }
        )
    return groups
async def get_group_locks_status(chat_id: str) -> dict:
    locks = await get_all_locks(chat_id)
    active_locks = [lock_type for lock_type, status in locks.items() if status]
    return {
        "total_locks": len(LOCK_TYPES),
        "active_locks": len(active_locks),
        "is_locked": len(active_locks) > 0,
        "active_lock_types": active_locks,
    }
async def get_group_entertainment_locks_status(chat_id: str) -> dict:
    locks = await get_all_entertainment_locks(chat_id)
    active_locks = [lock_type for lock_type, status in locks.items() if status]
    return {
        "total_locks": len(LOCK_TYPESS),
        "active_locks": len(active_locks),
        "is_locked": len(active_locks) > 0,
        "active_lock_types": active_locks,
    }
async def get_group_dashboards_status(chat_id: str) -> dict:
    dashboards = await get_all_dashboards(chat_id)
    active_dashboards = [
        dash_type
        for dash_type, status in dashboards.items()
        if dash_type not in ["text_mode", "sticker_emoji"] and status
    ]
    return {
        "total_dashboards": len(DASHBOARD_TYPES),
        "active_dashboards": len(active_dashboards),
        "is_active": len(active_dashboards) > 0,
        "active_dashboard_types": active_dashboards,
    }
async def toggle_group_all_locks(chat_id: str, lock_status: bool = True) -> dict:
    for lock_type in LOCK_TYPES:
        await set_lock(chat_id, lock_type, lock_status)
    return {
        "status": "success",
        "action": "lock_all" if lock_status else "unlock_all",
        "count": len(LOCK_TYPES),
    }
async def toggle_group_all_entertainment_locks(
    chat_id: str, lock_status: bool = True
) -> dict:
    for lock_type in LOCK_TYPESS:
        await set_entertainment_lock(chat_id, lock_type, lock_status)
    return {
        "status": "success",
        "action": "lock_all" if lock_status else "unlock_all",
        "count": len(LOCK_TYPESS),
    }
async def add_group_charge(chat_id: str, days: int):
    conn = await get_db_conn()
    now = datetime.now()
    async with conn.execute(
        """
        SELECT is_active, remaining_days, end_time 
        FROM group_charges WHERE chat_id = ?
    """,
        (chat_id,),
    ) as cursor:
        existing = await cursor.fetchone()
    if existing and existing[0] and existing[2]:
        current_end = datetime.fromisoformat(existing[2])
        if current_end > now:
            new_end = current_end + timedelta(days=days)
            new_remaining = existing[1] + days
        else:
            new_end = now + timedelta(days=days)
            new_remaining = days
    else:
        new_end = now + timedelta(days=days)
        new_remaining = days
    new_total_days = (existing[1] if existing else 0) + days
    new_used_days = existing[2] if existing else 0
    await conn.execute(
        """
        INSERT INTO group_charges 
            (chat_id, is_active, total_days, used_days, remaining_days, 
             start_time, end_time, last_warning_day, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            is_active = 1,
            total_days = excluded.total_days,
            used_days = excluded.used_days,
            remaining_days = excluded.remaining_days,
            start_time = COALESCE(excluded.start_time, start_time),
            end_time = excluded.end_time,
            last_warning_day = 0,
            updated_at = excluded.updated_at
    """,
        (
            chat_id,
            True,
            new_total_days,
            new_used_days,
            new_remaining,
            now.isoformat(),
            new_end.isoformat(),
            now.isoformat(),
        ),
    )
    await conn.commit()
    return {
        "success": True,
        "chat_id": chat_id,
        "days_added": days,
        "new_end_date": new_end.isoformat(),
        "remaining_days": new_remaining,
        "total_days": new_total_days,
    }
async def remove_group_charge(chat_id: str, remove_type: str = "delete"):
    conn = await get_db_conn()
    now = datetime.now().isoformat()
    if remove_type == "delete":
        await conn.execute("DELETE FROM group_charges WHERE chat_id = ?", (chat_id,))
        action = "deleted"
    elif remove_type == "reset":
        await conn.execute(
            """
            UPDATE group_charges 
            SET is_active = 0,
                total_days = 0,
                used_days = 0,
                remaining_days = 0,
                start_time = NULL,
                end_time = NULL,
                last_warning_day = 0,
                updated_at = ?
            WHERE chat_id = ?
        """,
            (now, chat_id),
        )
        action = "reset"
    else:
        await conn.execute(
            """
            UPDATE group_charges 
            SET is_active = 0,
                updated_at = ?
            WHERE chat_id = ?
        """,
            (now, chat_id),
        )
        action = "deactivated"
    await conn.commit()
    return {"success": True, "chat_id": chat_id, "action": action}
async def get_group_charge_status(chat_id: int):
    conn = await get_db_conn()
    now = datetime.now()
    async with conn.execute(
        """
        SELECT is_active, total_days, used_days, remaining_days, start_time, end_time
        FROM group_charges WHERE chat_id = ?
    """,
        (chat_id,),
    ) as cursor:
        row = await cursor.fetchone()
    if not row:
        return {
            "chat_id": chat_id,
            "is_active": False,
            "total_days": 0,
            "used_days": 0,
            "remaining_days": 0,
            "start_time": None,
            "end_time": None,
            "status": "no_charge",
        }
    ac = row[0]
    if ac == 1:
        is_active = True
    else:
        is_active = False
    end_time = row[5]
    start_time = row[4]
    if is_active and end_time:
        end_date = datetime.fromisoformat(end_time)
        if end_date <= now:
            await remove_group_charge(chat_id, "deactivate")
            return {
                "chat_id": chat_id,
                "is_active": False,
                "total_days": row[1],
                "used_days": row[2],
                "remaining_days": 0,
                "start_time": row[4],
                "end_time": row[5],
                "status": "expired",
            }
    if start_time and end_time:
        start_date = datetime.fromisoformat(start_time)
        end_date = datetime.fromisoformat(end_time)
        total_period_days = (end_date - start_date).days
        if total_period_days > 0:
            actual_used = row[1] - row[3]
        else:
            actual_used = 0
    else:
        actual_used = row[2]
    return {
        "chat_id": chat_id,
        "is_active": bool(is_active),
        "total_days": row[1],
        "used_days": actual_used,
        "remaining_days": row[3],
        "start_time": start_time,
        "end_time": end_time,
        "status": "active" if is_active else "inactive",
    }
async def list_all_group_charges(active_only: bool = True):
    conn = await get_db_conn()
    if active_only:
        query = """
            SELECT chat_id, is_active, total_days, remaining_days, start_time, end_time
            FROM group_charges 
            WHERE is_active = 1 
            ORDER BY remaining_days ASC, end_time ASC
        """
    else:
        query = """
            SELECT chat_id, is_active, total_days, remaining_days, start_time, end_time
            FROM group_charges 
            ORDER BY is_active DESC, end_time ASC
        """
    async with conn.execute(query) as cursor:
        rows = await cursor.fetchall()
    return [list(row) for row in rows]
async def ops(ch):
    group_charges = await list_all_group_charges()
    for i in group_charges:
        if ch == i[0]:
            end_time = i[5]
            start_date = datetime.now()
            if isinstance(end_time, str):
                end_date = datetime.fromisoformat(end_time)
            else:
                end_date = end_time
            diff = end_date - start_date
            total_hours = diff.total_seconds() / 3600
            total_days = total_hours / 24
            days_formatted = f"{total_days:.2f}"
            return days_formatted
async def ops1():
    group_charges = await list_all_group_charges()
    for i in group_charges:
        end_time = i[5]
        start_date = datetime.now()
        if isinstance(end_time, str):
            end_date = datetime.fromisoformat(end_time)
        else:
            end_date = end_time
        diff = end_date - start_date
        if diff.total_seconds() <= 0:
            total_days = abs(diff.total_seconds()) / 86400
            if diff.total_seconds() == 0:
                await remove_group_charge(chat_id=i[0])
            else:
                status = ""
async def initialize_database():
    await setup_all_tables()
    await upgrade_database()
    print("✅ Database initialized successfully!")
