from rubka.asynco import Robot, filters, Message
from rubka.context import Message
from rubka.exceptions import *
from rubka.keypad import ChatKeypadBuilder, InlineBuilder
import asyncio
from collections import defaultdict
import shutil
import os
import random
from pathlib import Path
from datetime import datetime
import logging
from database import initialize_database
from database import *
from method import *
from apis import *
from config import *
import re
import time
import traceback
user_states = defaultdict(dict)
V = "**v1.3.5**"
LANGS = {
    "fa": {
        "welcome": "👋 خوش آمدید، {name} عزیز!",
        "join_text": f"لطفاً ابتدا عضو کانال‌های رسمی ما شوید تا از ربات استفاده کنید.\n {CHANNEL_MAIN}\n{CHANNEL_LINKDONI}",
        "owner": "🌟 سلام کاربر گرامی!\nشما به عنوان مالک ربات شناسایی شدید.",
        "join": "✅ عضو شدم",
        "set": "🔹 زبان شما با موفقیت به فارسی تغییر یافت.",
        "add": "➕ افزودن به گروه",
        "help": "📘 راهنما",
        "report": "📞 تماس با پشتیبانی",
        "report_success": "✅ گزارش شما با شماره پیگیری {num} با موفقیت ثبت شد.\n\n📨 متن شما:\n{cmd}\n\n💙 با تشکر از همکاری شما.",
        "chanel": "🔥 مجموعه دراگون",
        "btn_change_lang": "🌐 تغییر زبان",
        "add_group": f"➕ افزودن ربات به گروه\nلطفاً ابتدا ربات را به گروه اضافه کرده و ادمین کامل کنید.\nارسال کلمه 'فعال' برای فعالسازی.\n📢 لینک کانال: {LINK_CHANNEL_MAIN}\n🎬 آموزش استفاده از ربات در ویدیو {LINK_TUTORIAL_VIDEO}",
        "help_info": "📘 راهنما\nیکم درباره ربات و کانال و دستوراتش توضیح می‌دهد.",
        "report_prompt": "📩 لطفا متن خود را وارد کنید.",
        "channels_info": f"🔥 کانال‌های رسمی ما:\n🔗 کانال اصلی: {CHANNEL_MAIN}\n🎬 فیلم آموزشی: {LINK_TUTORIAL_VIDEO}",
        "change_language": "🌐 زبان مورد نظر خود را انتخاب کنید:",
        "back": "🔙 بازگشت",
        "start_text": f"🤖 به ربات ما خوش آمدید!\n\nبرای فعال‌سازی کامل امکانات، لطفاً مراحل زیر را انجام دهید:\n━━━━━━━━━━━━━━━\n1️⃣ ربات را به گروه خود اضافه کنید.\n2️⃣ پس از افزودن، حتماً به عنوان مدیر تنظیمش کنید.\n3️⃣ برای راهنمایی کامل، ویدیو آموزشی را ببینید 👇\n\n🎬 آموزش استفاده از ربات: {LINK_TUTORIAL_VIDEO}\n📢 کانال‌های رسمی ما:\n🔗 کانال اصلی: {LINK_CHANNEL_MAIN}\n\nلینکدونی ما: {CHANNEL_LINKDONI}\n\n💬 از طریق دکمه‌های زیر هم می‌توانید به راحتی اقدام کنید 👇",
        "inline_users": "تعداد کاربر ({num})",
        "inline_groups": "تعداد گروه ({num})",
        "Error_send_tiket": "❌ دستور ناقص است.\nفرمت صحیح:\n/send_tiket <chat_id> <tracking_number> <متن پاسخ>",
        "tiket_message": (
            "سلام کاربر گرامی 🌟\n"
            "تیکت شما پاسخ داده شد ✅\n"
            "━━━━━━━━━━━━━━━\n"
            "📌 شماره پیگیری: {tracking_number}\n"
            "🆔 چت آیدی شما: {chat_id_user}\n"
            "💬 متن شما: {original_text}\n\n"
            "📨 پاسخ پشتیبانی:\n{support_text}\n\n"
            "📢 کانال‌های ما:\n{chanel}"
        ),
        "e_for": "✅ پیام با موفقیت به کاربر {chat_id_user} ارسال شد.",
        "ee_for": "❌ خطا در ارسال پیام به کاربر {chat_id_user}:\n{e}",
        "is_blocked": "❌ شما مسدود شده‌اید و نمی‌توانید از ربات استفاده کنید.",
        "report_notify": "📩 گزارش جدید از طرف کاربر: {name}\n🆔 چت آیدی: {chat_id}\n🔢 شماره پیگیری: {ticket_num}\n📊 تعداد گزارشات کاربر: {ticket_count}\n\n💬 متن پیام:\n{cmd}",
        "only_owner_send": "⛔ فقط مالک ربات اجازه استفاده از این دستور را دارد.",
        "no_users_yet": "⚠️ هنوز هیچ کاربری ثبت نشده است.",
        "sending_to_users": "📢 در حال ارسال پیام به {count} کاربر...",
        "send_report": "📬 پیام ارسال شد!\n\n✅ موفق: {sent}\n❌ ناموفق: {failed}\n👥 کل کاربران: {total}",
        "prompt_send_all": "📝 لطفاً پیام خود را ارسال کنید تا برای همه کاربران فرستاده شود.",
        "ticket_not_found": "❌ تیکت با شماره {tracking_number} پیدا نشد.",
        "activate_message": (
            "✅ ربات با موفقیت در گروه فعال شد!\n\n"
            "🌟 از این پس تمام قابلیت‌های مدیریت گروه در دسترس شماست.\n"
            "━━━━━━━━━━━━━━━\n"
            f"📢 کانال رسمی ربات: {CHANNEL_MAIN}\n"
            "💬 برای مشاهده دستورها، کلمه «دستورات» را ارسال کنید.\n"
            "🎬 آموزش کامل استفاده از ربات در ویدیو موجود در کانال قرار دارد.\n\n"
            "🔥 با دراگون‌بات، مدیریت گروه‌تون حرفه‌ای‌تر از همیشه!\n\n"
            "🌟 قابلیت های فعال پیش فرض:\n"
            "✅ ضد لینک\n"
            "✅ ضد کد هنگی\n"
            "✅ ضد متن نامناسب\n"
            "✅ ضد فوروارد\n"
            "✅ شکل متن 2 تظیم شد\n"
            "✅ علامت پیش فرض تنظیم شد\n"
            f"لینکدونی ما: {CHANNEL_LINKDONI}"
        ),
        "commands_message": (
            "📘 لیست دستورات ربات:\n"
            "━━━━━━━━━━━━━━━\n"
            "🔹 برای دیدن همه‌ی دستورات و آموزش‌ها به کانال زیر برو:\n"
            f"🔹 دستورات: {CHANNEL_COMMANDS}\n"
            f"📢 چنل بات: {CHANNEL_MAIN}\n"
            "━━━━━━━━━━━━━━━\n"
        ),
        "language_changed": "✅ زبان شما به فارسی تغییر یافت.",
        "select_language": "🌐 لطفا زبان خود را انتخاب کنید:",
        "broadcast_start": "📢 شروع ارسال همگانی...",
        "broadcast_complete": "✅ ارسال همگانی تکمیل شد!\n\n📊 آمار:\n✅ ارسال موفق: {sent}\n❌ ارسال ناموفق: {failed}\n👥 کل کاربران: {total}",
        "broadcast_to_all": "📤 ارسال به همه کاربران",
        "broadcast_by_lang": "🌍 ارسال بر اساس زبان",
        "admin_m": " ✅ شما با موفقیت به مالکیت بات در امدید",
        "admin_v": " ✅ کاربر ادمین ویژه شد",
        "admin_a": " ✅ کاربر ادمین ساده شد",
        "admin_n": "کاربر برکنار شد✅ ",
        "rim": "گروه با موفقیت ریست شد",
        "new_ow": "سازنده با موفقیت تغییر یافت",
    }
}
SET_DB = "bot_data.db"
DATABASES = {
    "bot_data": SET_DB,
}
BACKUP_DIR = "backups"
MAX_BACKUPS = 4
BACKUP_INTERVAL = 6 * 60 * 60
def kb():
    return ChatKeypadBuilder()
def btn(id, text):
    return ChatKeypadBuilder().button(id=id, text=text)
async def show_control_panel(bot, message, user_id):
    groups = await get_user_owned_groups(user_id)
    if not groups:
        return await message.reply("❌ شما مالک هیچ گروهی نیستید")
    user_states[user_id] = {"state": "select_group", "owned_groups": groups}
    kb_builder = kb()
    for g in groups:
        icon = "✅" if g["active"] else "❌"
        kb_builder.row(btn(f"group_{g['chat_id']}", f"{icon} {g['name']}"))
    kb_builder.row(btn("close", "❌ بستن"))
    await bot.send_message(
        chat_id=message.chat_id,
        text="👑 **کنترل پنل مدیریت گروه‌ها**\n\nگروه را انتخاب کنید:",
        chat_keypad=kb_builder.build(),
    )
async def show_group_menu(bot, message, user_id, group):
    user_states[user_id]["state"] = "group_menu"
    user_states[user_id]["selected_group"] = group
    locks = await get_group_locks_status(group["chat_id"])
    ent = await get_group_entertainment_locks_status(group["chat_id"])
    dash = await get_group_dashboards_status(group["chat_id"])
    await bot.send_message(
        chat_id=message.chat_id,
        text=(
            f"👑 **مدیریت گروه:** {group['name']}\n\n"
            f"🔒 قفل‌ها: {'✅' if locks['is_locked'] else '❌'}\n"
            f"🎮 سرگرمی: {'✅' if ent['is_locked'] else '❌'}\n"
            f"📊 داشبورد: {'✅' if dash['is_active'] else '❌'}"
        ),
        chat_keypad=(
            ChatKeypadBuilder()
            .row(
                btn("locks", "🔒 قفل‌ها"),
                btn("ent", "🎮 سرگرمی"),
            )
            .row(
                btn("dash", "📊 داشبورد"),
                btn("text", "⚙️ تنظیمات متنی"),
            )
            .row(
                btn("stats", "📈 آمار گروه"),
            )
            .row(
                btn("back", "🔙 بازگشت"),
                btn("close", "❌ بستن"),
            )
            .build()
        ),
    )
async def show_locks_menu(bot, message, user_id, chat_id):
    user_states[user_id]["state"] = "manage_locks"
    locks = await get_group_locks_status(chat_id)
    await bot.send_message(
        chat_id=message.chat_id,
        text=(
            "🔒 **مدیریت قفل‌های گروه**\n\n"
            f"• کل قفل‌ها: {locks['total_locks']}\n"
            f"• قفل‌های فعال: {locks['active_locks']}\n"
            f"• وضعیت کلی: {'✅ فعال' if locks['is_locked'] else '❌ غیرفعال'}"
        ),
        chat_keypad=(
            ChatKeypadBuilder()
            .row(
                ChatKeypadBuilder().button(id="lock_all", text="🔒 قفل کردن همه"),
                ChatKeypadBuilder().button(id="unlock_all", text="🔓 باز کردن همه"),
            )
            .row(ChatKeypadBuilder().button(id="lock_status", text="📊 وضعیت فعلی"))
            .row(
                ChatKeypadBuilder().button(id="backk", text="🔙 بازگشت"),
                ChatKeypadBuilder().button(id="close", text="❌ بستن"),
            )
            .build()
        ),
    )
async def handle_control_panel(bot, message, user_id, button_id):
    state = user_states.get(user_id, {}).get("state")
    if button_id == "close":
        user_states.pop(user_id, None)
        return await bot.send_message(
            message.chat_id, "✅ پنل بسته شد", build_chat_keypad()
        )
    if button_id.startswith("group_"):
        chat_id = button_id.split("_", 1)[1]
        group = next(
            g
            for g in user_states[user_id]["owned_groups"]
            if str(g["chat_id"]) == chat_id
        )
        user_states[user_id]["selected_group"] = group
        return await show_group_menu(bot, message, user_id, group)
    if button_id == "locks":
        return await show_locks_menu(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "ent":
        return await show_entertainment_menu(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "dash":
        return await show_dashboard_menu(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "manage_dashboard":
        return await handle_dashboard_menu(bot, message, user_id, button_id)
    if button_id == "stats":
        return await show_group_stats(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "text":
        return await show_text_settings(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "dash_status":
        return await show_dashboard_status(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "dash_calc":
        await toggle_calculator_dashboard(
            user_states[user_id]["selected_group"]["chat_id"]
        )
        return await message.reply("وضعیت ماشین حساب تغییر کرد")
    if button_id == "dash_speak":
        await toggle_speak_dashboard(user_states[user_id]["selected_group"]["chat_id"])
        return await message.reply("وضعیت سخنگو تغییر کرد")
    if button_id == "lock_status":
        return await show_locks_status(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "lock_all":
        result = await toggle_group_all_locks(
            user_states[user_id]["selected_group"]["chat_id"], True
        )
        await message.reply(f"✅ همه قفل‌ها ({result['count']} مورد) فعال شدند")
        await show_locks_menu(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "unlock_all":
        result = await toggle_group_all_locks(
            user_states[user_id]["selected_group"]["chat_id"], False
        )
        await message.reply(f"✅ همه قفل‌ها ({result['count']} مورد) غیرفعال شدند")
        await show_locks_menu(
            bot, message, user_id, user_states[user_id]["selected_group"]["chat_id"]
        )
    if button_id == "ent_lock_all":
        r = await toggle_group_all_entertainment_locks(
            user_states[user_id]["selected_group"]["chat_id"], True
        )
        await message.reply(f"✅ {r['count']} سرگرمی قفل شد")
    if button_id == "ent_unlock_all":
        r = await toggle_group_all_entertainment_locks(
            user_states[user_id]["selected_group"]["chat_id"], False
        )
        await message.reply(f"✅ {r['count']} سرگرمی باز شد")
    if button_id == "ent_status":
        s = await get_group_entertainment_locks_status(
            user_states[user_id]["selected_group"]["chat_id"]
        )
        text = "🎮 **سرگرمی‌های قفل‌شده:**\n\n"
        for l in s["active_lock_types"]:
            text += f"• {LOCK_TRANSLATIONSS.get(l, l)}\n"
        await message.reply(text or "❌ چیزی قفل نیست")
async def show_entertainment_menu(bot, message, user_id, chat_id):
    user_states[user_id]["state"] = "manage_entertainment"
    ent = await get_group_entertainment_locks_status(chat_id)
    await bot.send_message(
        chat_id=message.chat_id,
        text=(
            "🎮 **مدیریت سرگرمی‌ها**\n\n"
            f"قفل‌شده: {ent['active_locks']} / {ent['total_locks']}"
        ),
        chat_keypad=(
            ChatKeypadBuilder()
            .row(
                btn("ent_lock_all", "🔒 قفل همه سرگرمی‌ها"),
                btn("ent_unlock_all", "🔓 باز همه سرگرمی‌ها"),
            )
            .row(
                btn("ent_status", "📊 وضعیت سرگرمی"),
            )
            .row(
                btn("back", "🔙 بازگشت"),
                btn("close", "❌ بستن"),
            )
            .build()
        ),
    )
async def show_dashboard_menu(bot, message, user_id, chat_id):
    user_states[user_id]["state"] = "manage_dashboard"
    dash = await get_group_dashboards_status(chat_id)
    await bot.send_message(
        chat_id=message.chat_id,
        text=(
            "📊 **داشبوردها**\n\n"
            f"فعال: {dash['active_dashboards']} / {dash['total_dashboards']}"
        ),
        chat_keypad=(
            ChatKeypadBuilder()
            .row(
                btn("dash_speak", "🗣️ سخنگو"),
                btn("dash_calc", "🧮 ماشین حساب"),
            )
            .row(
                btn("dash_status", "📊 وضعیت داشبورد"),
            )
            .row(
                btn("back", "🔙 بازگشت"),
                btn("close", "❌ بستن"),
            )
            .build()
        ),
    )
async def handle_dashboard_menu(bot, message, user_id, button_id):
    chat_id = user_states[user_id]["selected_group"]["chat_id"]
    if button_id == "dash_speak":
        s = await toggle_speak_dashboard(chat_id)
        await message.reply("🗣️ سخنگو " + ("فعال شد" if s else "غیرفعال شد"))
    elif button_id == "dash_calc":
        s = await toggle_calculator_dashboard(chat_id)
        await message.reply("🧮 ماشین حساب " + ("فعال شد" if s else "غیرفعال شد"))
    elif button_id == "dash_status":
        text = "📊 **وضعیت داشبوردها:**\n\n"
        for d in DASHBOARD_TYPES:
            st = await get_dashboard_status(chat_id, d)
            text += f"• {DASHBOARD_TRANSLATIONS.get(d,d)}: {'✅' if st else '❌'}\n"
        await message.reply(text)
    elif button_id == "back":
        return await show_group_menu(
            bot, message, user_id, user_states[user_id]["selected_group"]
        )
    await show_dashboard_menu(bot, message, user_id, chat_id)
async def show_text_settings(bot, message, user_id, chat_id):
    current_model = await get_group_model(chat_id)
    current_emoji = await get_group_sticker_emoji(chat_id)
    keyboard_buttons = [
        [{"text": f"🎭 حالت متنی: {current_model}", "callback": "change_text_mode"}],
        [{"text": f"😊 ایموجی: {current_emoji}", "callback": "change_emoji"}],
        [{"text": "🔙 بازگشت", "callback": "back"}],
        [{"text": "❌ بستن", "callback": "close"}],
    ]
    await bot.send_message(
        chat_id=message.chat_id,
        text=f"⚙️ **تنظیمات متنی گروه**\n\n"
        f"• حالت متنی فعلی: {current_model}\n"
        f"• ایموجی استیکر: {current_emoji}\n\n"
        f"برای تغییر تنظیمات از دکمه‌ها استفاده کنید:",
    )
async def show_dashboard_status(bot, message, user_id, chat_id):
    dashboard_status = await get_group_dashboards_status(chat_id)
    status_text = f"📊 **وضعیت داشبوردها:**\n\n"
    for dash_type in DASHBOARD_TYPES:
        is_active = await get_dashboard_status(chat_id, dash_type)
        status = "✅ فعال" if is_active else "❌ غیرفعال"
        persian_name = DASHBOARD_TRANSLATIONS.get(dash_type, dash_type)
        status_text += f"• {persian_name}: {status}\n"
    await message.reply(status_text)
    await show_dashboard_menu(bot, message, user_id, chat_id)
async def show_group_stats(bot, message, user_id, chat_id):
    stats = await get_group_status(chat_id)
    if not stats:
        await message.reply("❌ اطلاعات گروه یافت نشد!")
        return
    stats_text = f"📊 **آمار گروه:** {stats['group_name']}\n\n"
    stats_text += f"👥 تعداد اعضا: {stats['total_members']}\n"
    stats_text += f"📈 کل پیام‌ها: {stats['stats']['messages']}\n"
    stats_text += f"\n🎭 **توزیع نقش‌ها:**\n"
    stats_text += f"• مالک: {stats['roles']['owner']}\n"
    stats_text += f"• ادمین: {stats['roles']['admin']}\n"
    stats_text += f"• ویژه: {stats['roles']['vip']}\n"
    stats_text += f"• عضو: {stats['roles']['member']}\n"
    await message.reply(stats_text)
    group = next(
        g for g in user_states[user_id]["owned_groups"] if str(g["chat_id"]) == chat_id
    )
    await show_group_menu(bot, message, user_id, group)
async def show_locks_status(bot, message, user_id, chat_id):
    locks_status = await get_group_locks_status(chat_id)
    text = f"🔒 **وضعیت قفل‌ها:**\n\n"
    text += f"• کل قفل‌ها: {locks_status['total_locks']}\n"
    text += f"• قفل‌های فعال: {locks_status['active_locks']}\n"
    if locks_status["active_locks"] > 0:
        text += f"\n📋 **قفل‌های فعال:**\n"
        for lock_type in locks_status["active_lock_types"][:10]:
            persian_name = LOCK_TRANSLATIONS.get(lock_type, lock_type)
            text += f"• {persian_name}\n"
    await message.reply(text)
    await show_locks_menu(bot, message, user_id, chat_id)
async def create_backup():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        os.makedirs(backup_folder)
        for db_name, db_path in DATABASES.items():
            if os.path.exists(db_path):
                backup_path = os.path.join(backup_folder, f"{db_name}.db")
                shutil.copy2(db_path, backup_path)
            else:
                logging.warning(f"⚠️ فایل دیتابیس {db_path} یافت نشد")
        await cleanup_old_backups()
        return True
    except Exception as e:
        return False
async def cleanup_old_backups():
    try:
        if not os.path.exists(BACKUP_DIR):
            return
        backup_folders = []
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isdir(item_path) and item.startswith("backup_"):
                backup_folders.append((item_path, os.path.getctime(item_path)))
        backup_folders.sort(key=lambda x: x[1], reverse=True)
        if len(backup_folders) > MAX_BACKUPS:
            for folder_path, _ in backup_folders[MAX_BACKUPS:]:
                shutil.rmtree(folder_path)
    except Exception as e:
        pass
async def backup_scheduler(stop_event):
    while not stop_event.is_set():
        await create_backup()
        await asyncio.wait_for(stop_event.wait(), timeout=BACKUP_INTERVAL)
async def list_backups():
    try:
        if not os.path.exists(BACKUP_DIR):
            return "📭 هیچ بکاپی وجود ندارد"
        backup_folders = []
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isdir(item_path) and item.startswith("backup_"):
                create_time = os.path.getctime(item_path)
                date_str = datetime.fromtimestamp(create_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                backup_folders.append((item, date_str))
        if not backup_folders:
            return "📭 هیچ بکاپی وجود ندارد"
        backup_folders.sort(reverse=True)
        result = "📂 لیست بکاپ‌های موجود:\n\n"
        for i, (folder, date) in enumerate(backup_folders, 1):
            result += f"{i}. `{folder}` - {date}\n"
        return result
    except Exception as e:
        return f"❌ خطا در دریافت لیست بکاپ‌ها: {e}"
async def restore_backup(backup_name):
    try:
        backup_folder = os.path.join(BACKUP_DIR, backup_name)
        if not os.path.exists(backup_folder):
            return f"❌ بکاپ {backup_name} یافت نشد"
        restored_dbs = []
        for db_name, db_path in DATABASES.items():
            backup_db_path = os.path.join(backup_folder, f"{db_name}.db")
            if os.path.exists(backup_db_path):
                shutil.copy2(backup_db_path, db_path)
                restored_dbs.append(db_name)
        if restored_dbs:
            return f"✅ بازیابی完成. دیتابیس‌های بازیابی شده: {', '.join(restored_dbs)}"
        else:
            return "❌ هیچ دیتابیسی بازیابی نشد"
    except Exception as e:
        return f"❌ خطا در بازیابی: {e}"
def t(lang_code: str = "fa", key: str = "", **kwargs):
    return LANGS.get(lang_code, LANGS["fa"]).get(key, key).format(**kwargs)
def build_chat_keypad(lang="fa"):
    add_text = t(lang, "add")
    help_text = t(lang, "help")
    report_text = t(lang, "report")
    chanel_text = t(lang, "chanel")
    btn_change_lang = t(lang, "btn_change_lang")
    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(id="add", text=add_text),
            ChatKeypadBuilder().button(id="help", text=help_text),
        )
        .row(
            ChatKeypadBuilder().button(id="report", text=report_text),
            ChatKeypadBuilder().button(id="chanel", text=chanel_text),
        )
        .row(ChatKeypadBuilder().button(id="groups", text="👥 گروه های من"))
        .build()
    )
def build_back_keypad(lang):
    return (
        ChatKeypadBuilder()
        .row(ChatKeypadBuilder().button(id="back", text=t(lang, "back")))
        .build()
    )
def build_language_keypad():
    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(id="lang_fa", text="🇮🇷 فارسی"),
            ChatKeypadBuilder().button(id="lang_en", text="🇺🇸 English"),
        )
        .row(
            ChatKeypadBuilder().button(id="lang_ar", text="🇸🇦 العربية"),
        )
        .row(
            ChatKeypadBuilder().button(id="back", text="🔙 بازگشت"),
        )
        .build()
    )
def build_send_type_keypad(lang):
    return (
        ChatKeypadBuilder()
        .row(
            ChatKeypadBuilder().button(id="send_private", text="📩 ارسال به کاربران"),
            ChatKeypadBuilder().button(id="send_group", text="👥 ارسال به گروه‌ها"),
        )
        .row(
            ChatKeypadBuilder().button(id="back", text=t(lang, "back")),
        )
        .build()
    )
def build_inline_keypad(lang, users_count, groups_count):
    return (
        InlineBuilder()
        .row(
            InlineBuilder().button_simple(
                id="a", text=t(lang, "inline_users", num=users_count)
            ),
            InlineBuilder().button_simple(
                id="b", text=t(lang, "inline_groups", num=groups_count)
            ),
        )
        .build()
    )
def contains_english(text):
    if text:
        english_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return any(char in english_chars for char in text)
def contains_pars(text):
    if text:
        pars_chars = "ظطزرذدئوشسیبلاتنمکگضصثقفغعهخحجچپژ"
        return any(char in pars_chars for char in text)
_SPEAK_SKIP = frozenset((
    "دستورات", "الأوامر", "commands", "ورژن", "مقام", "/", "مقامم", "مقامش", "اطلاعات", "info",
    "اینفو", "امار", "آمار", "شامار", "آمارم", "تاس", "سکه", "چالش", "بیو", "حدیث", "دانستنی", "جوک",
    "سازنده", "ماشین حساب", "داستان", "/story", "عدد شانسی", "📖", "دیالوگ", "/dialog", "💭", "فال", "🔮",
    "غزل", "/ghazal", "📜", "فیک", "/fake", "👥", "لیست سرگرمی", "لیست", "/fal", "اصل", "لقب", "بگو",
    "وضعیت قفل‌ ها", "لیست قفل", "لیست ادمین", "لیست ویژه", "داشبورد", "سخنگو روشن", "سخنگو خاموش",
    "ماشین حساب روشن", "ماشین حساب خاموش", "قفل لینک", "قفل انگلیسی", "قفل رسانه", "قفل ایدی",
    "قفل آیدی", "قفل فایل", "قفل نظرسنجی", "قفل موقعیت مکانی", "قفل استیکر", "قفل فوروارد", "قفل عکس",
    "قفل فیلم", "قفل ویس", "قفل اسپویلر", "قفل فارسی", "قفل هشتک", "قفل منش", "قفل نقل قول",
    "قفل برجسته", "قفل کج", "قفل زیر خط", "قفل خط خورده", "قفل تکی", "قفل متن نامناسب", "قفل اسپم",
    "قفل متن بلند", "قفل کد هنگی", "قفل همه", "آزاد کردن لینک", "آزاد کردن انگلیسی", "آزاد کردن رسانه",
    "آزاد کردن ایدی", "آزاد کردن آیدی", "آزاد کردن فایل", "آزاد کردن نظرسنجی",
    "آزاد کردن موقعیت مکانی", "آزاد کردن استیکر", "آزاد کردن فوروارد", "آزاد کردن عکس",
    "آزاد کردن فیلم", "آزاد کردن ویس", "آزاد کردن اسپویلر", "آزاد کردن فارسی", "آزاد کردن هشتگ",
    "آزاد کردن منش", "آزاد کردن نقل قول", "آزاد کردن برجسته", "آزاد کردن کج", "آزاد کردن زیر خط",
    "آزاد کردن خط خورده", "آزاد کردن تکی", "آزاد کردن متن نامناسب", "آزاد کردن اسپم",
    "آزاد کردن متن بلند", "آزاد کردن کد هنگی", "آزاد کردن همه", "لیست شکل", "لیست معاف", "لیست سکوت",
    "تگ", "تگ همه", "تگ ادمین", "تگ ویژه", "تگ مالک", "تگ عضو", "تگ فعال", "تگ ساکت", "تگ غیرفعال",
    "تنظیم شکل", "تنظیم مالک", "تنظیم ویژه", "تنظیم ادمین", "تنظیم اصل", "تنظیم لقب", "برکناری",
    "حذف معاف", "حذف اصل", "حذف لقب", "معاف", "سکوت", "حذف سکوت", "ریست", "ریست گپ", "ریست گروه",
    "ریست لیست ویژه", "ریست لیست ادمین", "انتقال مالکیت", "وضعیت گروه", "وضعیت گپ", "امار گپ",
    "آمار گپ", "امار گروه", "آمار گروه", "گیف", "حذف", "فعال", "active", "تفعيل", "/blocke",
    "/unblocke", "/reset_blocked", "/list_blocked", "/list", "/backup", "/backup_list", "/restore",
    "/start", "/for_tiket", "/send", "/admin", "/del_admin", "/add_chanel", "/add_channel",
    "/remove_channel", "/list_channels", "/channel_count", "!", "قفل ساعت", "قفل تاس", "قفل سکه",
    "قفل عدد شانسی", "قفل چالش", "قفل بیو", "قفل حدیث", "قفل دانستنی", "قفل جوک", "قفل داستان",
    "قفل دیالوگ", "قفل فال", "قفل غزل", "قفل فیک", "قفل لیست", "قفل لیست سرگرمی", "آزاد کردن ساعت",
    "آزاد کردن تاس", "آزاد کردن سکه", "آزاد کردن عدد شانسی", "آزاد کردن چالش", "آزاد کردن بیو",
    "آزاد کردن حدیث", "آزاد کردن دانستنی", "آزاد کردن جوک", "آزاد کردن داستان", "آزاد کردن دیالوگ",
    "آزاد کردن فال", "آزاد کردن غزل", "آزاد کردن فیک", "آزاد کردن لیست", "آزاد کردن لیست سرگرمی",
    "ساعت قفل", "ساعت خاموش", "تاس قفل", "تاس خاموش", "سکه قفل", "سکه خاموش", "عدد شانسی قفل",
    "عدد شانسی خاموش", "چالش قفل", "چالش خاموش", "بیو قفل", "بیو خاموش", "حدیث قفل", "حدیث خاموش",
    "دانستنی قفل", "دانستنی خاموش", "جوک قفل", "جوک خاموش", "داستان قفل", "داستان خاموش", "دیالوگ قفل",
    "دیالوگ خاموش", "فال قفل", "فال خاموش", "غزل قفل", "غزل خاموش", "فیک قفل", "فیک خاموش",
    "لیست خاموش", "لیست سرگرمی قفل", "لیست سرگرمی خاموش", "ساعت آزاد", "ساعت باز", "ساعت روشن",
    "تاس آزاد", "تاس باز", "تاس روشن", "سکه آزاد", "سکه باز", "سکه روشن", "عدد شانسی آزاد",
    "عدد شانسی باز", "عدد شانسی روشن", "چالش آزاد", "چالش باز", "چالش روشن", "بیو آزاد", "بیو باز",
    "بیو روشن", "حدیث آزاد", "حدیث باز", "حدیث روشن", "دانستنی آزاد", "دانستنی باز", "دانستنی روشن",
    "جوک آزاد", "جوک باز", "جوک روشن", "داستان آزاد", "داستان باز", "داستان روشن", "دیالوگ آزاد",
    "دیالوگ باز", "دیالوگ روشن", "فال آزاد", "فال باز", "فال روشن", "غزل آزاد", "غزل باز", "غزل روشن",
    "فیک آزاد", "فیک باز", "فیک روشن", "لیست آزاد", "لیست باز", "لیست روشن", "لیست سرگرمی آزاد",
    "لیست سرگرمی باز", "لیست سرگرمی روشن", "شارژ", "شارژ گروه",
))
async def handle_locked_speak(
    chat_id, message, text, bot_name, delet_timer, is_deleted_timer
):
    if text not in _SPEAK_SKIP:
        try:
            rol = await get_user_role(chat_id=chat_id, user_id=message.sender_id)
            if await are_speak_vip_dashboard(chat_id=chat_id) and rol in [
                "owner",
                "vip",
                "admin",
            ]:
                sep = await get_answer(command=text, TIP_ANS=0, sp_type="polit")
                if sep:
                    answer = sep.get("answer")
                    await reply(
                        message,
                        await MPro(str(answer), chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                    return True
            if await are_speak_dashboard(chat_id=chat_id):
                sep = await get_answer(command=text, TIP_ANS=0, sp_type="polit")
                if sep:
                    answer = sep.get("answer")
                    await reply(
                        message,
                        await MPro(str(answer), chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                    return True
            a = await get_group_charge_status(chat_id)
            if a.get("is_active"):
                if await are_speak_bad_dashboard(chat_id=chat_id):
                    sep = await get_answer(command=text, TIP_ANS=0, sp_type="rude")
                    if sep:
                        answer = sep.get("answer")
                        await reply(
                            message,
                            await MPro(str(answer), chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
                        return True
                return False
        except Exception as e:
            return False
models_list = f"""
🎯 *لیست کامل مدل‌های Dragon AI:*

🤖 *مدل‌های عمومی چت:*
1️⃣ `openai` - OpenAI GPT (پیش‌فرض) - همه‌کاره
2️⃣ `openai-fast` - OpenAI سریع - پاسخ‌دهی سریع‌تر
3️⃣ `openai-large` - OpenAI بزرگ - قدرت پردازش بالا
4️⃣ `openai-reasoning` - OpenAI استدلالی - منطق و تحلیل قوی

🧠 *مدل‌های هوش مصنوعی دیگر:*
5️⃣ `deepseek` - DeepSeek - هوش مصنوعی متن‌باز
6️⃣ `gemini` - Google Gemini - مدل گوگل
7️⃣ `gemini-search` - Gemini با جستجو - دسترسی به اینترنت
8️⃣ `mistral` - Mistral AI - مدل اروپایی

💻 *مدل‌های تخصصی کدنویسی:*
9️⃣ `qwen-coder` - Qwen Coder - تخصصی برنامه‌نویسی
🔟 `unity` - Unity - توسعه بازی و گرافیک

🎨 *مدل‌های خلاقیت و هنر:*
1️⃣1️⃣ `midijourney` - Midjourney - تولید موسیقی و صدا
1️⃣2️⃣ `rtist` - RTist - هنر دیجیتال و خلاقیت
1️⃣3️⃣ `bidara` - Bidara - محتوای خلاقانه

🎮 *مدل‌های سرگرمی و بازی:*
1️⃣4️⃣ `roblox-rp` - Roblox RP - نقش‌آفرینی روبلاکس
1️⃣5️⃣ `chickytutor` - Chicky Tutor - آموزشی و تعاملی

📊 *نکات مهم:*
• مدل پیش‌فرض: `openai`
• پارامتر model اختیاری است
• می‌توانید از نام فارسی یا انگلیسی استفاده کنید

🔧 *نام‌های فارسی معادل:*
- اوپن‌ای‌آی = openai
- دیپ‌سیک = deepseek
- جمینی = gemini
- میسترال = mistral
- کدنویس = qwen-coder
- میدی‌جرنی = midijourney
- آرتیست = rtist
- بیدرا = bidara
- یونیتی = unity
- چیکی‌توتور = chickytutor

📝 *مثال استفاده:*
`/سوال شما openai`
`/کد پایتون qwen-coder`
`/آهنگ بساز midijourney`
`/بازی طراحی کن unity`

👨‍💻 *توسعه‌دهنده:* {SUPPORT_USERNAME}
⚡ *chanel:* {CHANNEL_MAIN_LC}
"""
async def handle_entertainment_features(
    bot, chat_id, message, text, rol, suport, bot_name, delet_timer, is_deleted_timer
):
    cmd = text
    try:
        if text:
            if text == "جی پی تی" or text == "/models":
                if not await is_gpt_locked(chat_id):
                    await reply(
                        message,
                        await MPro(text=models_list, chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                    return
                if text.startswith("/"):
                    text = message.text.strip()
                    pattern = r"^/(\w+[\-\w]*)\s+(.+)$"
                    match = re.match(pattern, text)
                    if match:
                        model = match.group(1)
                        user_text = match.group(2)
                        a = await reply(
                            message,
                            await MPro(text="درحال پردازش...", chat_id=chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
                        aa = ["bar", "spinner"]
                        animation_type = random.choice(aa)
                        frames_bar = [
                            "[]",
                            "[=]",
                            "[==]",
                            "[===]",
                            "[====]",
                            "[=====]",
                            "[======]",
                            "[=======]",
                            "[========]",
                            "[=========]",
                            "[==========]",
                        ]
                        frames_spinner = ["|", "/", "-", "\\"]
                        task_done = False
                        result = None
                        async def get_result():
                            nonlocal task_done, result
                            print(user_text)
                            result = rubigram_chat(text=user_text, model=model)
                            task_done = True
                        asyncio.create_task(get_result())
                        i = 0
                        while not task_done:
                            if animation_type == "bar":
                                frame = frames_bar[i % len(frames_bar)]
                                await bot.edit_message_text(
                                    chat_id=chat_id,
                                    message_id=a.message_id,
                                    text=await MPro(
                                        text=f"در حال پردازش...\n{frame}",
                                        chat_id=chat_id,
                                    ),
                                )
                                await asyncio.sleep(0.25)
                            elif animation_type == "spinner":
                                frame = frames_spinner[i % len(frames_spinner)]
                                await bot.edit_message_text(
                                    chat_id=chat_id,
                                    message_id=a.message_id,
                                    text=await MPro(
                                        text=f"در حال پردازش... {frame}",
                                        chat_id=chat_id,
                                    ),
                                )
                                await asyncio.sleep(0.15)
                            i += 1
                        if result and result.get("status"):
                            await bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=a.message_id,
                                text=await MPro(
                                    text=result.get("response", "📭 پاسخی دریافت نشد"),
                                    chat_id=chat_id,
                                ),
                            )
                        else:
                            await bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=a.message_id,
                                text=await MPro(
                                    text="❌ مشکلی در پردازش رخ داد.", chat_id=chat_id
                                ),
                            )
                    else:
                        await reply(
                            message,
                            """🎮 *فرمت صحیح دستور:*
`/مدل متن شما`

📌 *مثال‌ها:*
`/openai امروز هوا چطوره؟`
`/deepseek فلسفه زندگی چیست؟`
`/qwen-coder یک تابع پایتون بنویس`

📚 برای مشاهده مدل‌ها: /models
""",
                            is_deleted_timer,
                            delet_timer,
                        )
            if text == "مالک":
                ids = await list_group_ow(chat_id)
                for i in ids:
                    o = await get_nickname(chat_id, i)
                    if o == None:
                        orr = "بدون لقب"
                    await reply(
                        message,
                        await MPro(text=f"[{o}]({i})", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text.startswith("سال"):
                cmd = text[4:]
                tex = f"سن دقیق شما:\n{calculate_age_human_readable(cmd)}"
                if tex:
                    await reply(
                        message,
                        await MPro(tex + f"\n{CHANNEL_MAIN_LC}", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text.startswith("تناسب"):
                cmds = text.split()
                if len(cmds) > 3:
                    if len(cmds) == 5:
                        h = int(cmds[2])
                        w = int(cmds[4])
                        res = w / (h / 100) ** 2
                        a = get_bmi_advice(res)
                        await reply(
                            message,
                            await MPro(a + f"\n{CHANNEL_MAIN_LC}", chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
                    else:
                        await reply(
                            message,
                            await MPro(
                                "فرمت درست \nتناسب قد 180 وزk 80" + f"\n{CHANNEL_MAIN_LC}",
                                chat_id,
                            ),
                            is_deleted_timer,
                            delet_timer,
                        )
                else:
                    await reply(
                        message,
                        await MPro(
                            "فرمت درست \nتناسب قد 180 وزن 80" + f"\n{CHANNEL_MAIN_LC}",
                            chat_id,
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text.startswith("کیوارکد"):
                if not await is_qr_code_locked(chat_id):
                    try:
                        cmd = text[8:]
                        pathh = create_qr_code(cmd)
                        await bot.send_image(
                            chat_id,
                            pathh,
                            text="کیوارکد شما ساخته شد",
                            reply_to_message_id=message.message_id,
                        )
                        os.remove(pathh)
                    except:
                        pass
            if text.startswith("فونت"):
                if not await is_font_locked(chat_id):
                    if rol in ["admin", "owner", "vip"] or message.sender_id == suport:
                        if text in ["قفل فونت", "فونت باز"]:
                            return
                        cmd = text[5:]
                        if contains_english(cmd):
                            list_font = Fontmaker(cmd)
                            message1 = f"〔 فونت 〕  : {cmd}\n\n"
                            for i in list_font:
                                message1 += "\u200f" + f"• {i}\n"
                            await reply(
                                message,
                                message1 + f"\n\n{CHANNEL_MAIN_LC}",
                                is_deleted_timer,
                                delet_timer,
                            )
                        else:
                            await reply(
                                message,
                                await MPro(
                                    "لطفا از کلمه انگلیسی استفاده کنین", chat_id
                                ),
                                is_deleted_timer,
                                delet_timer,
                            )
            if text in (bot_name, "دراگون", "ربات"):
                if not await are_speak_bad_dashboard(
                    chat_id=chat_id
                ) and await are_speak_dashboard(chat_id=chat_id):
                    list_text = [
                        "سلام جانم؟",
                        "کسی منو صدا زد؟",
                        "جان",
                        "مدیریت گروه دراگون هستم بفرما",
                        "بله",
                        "صدا نکن مشغول مدیریتم",
                        "ها؟",
                        "بله؟",
                        "کارتو بگو",
                    ]
                    await reply(
                        message,
                        await MPro(text=random.choice(list_text), chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text.startswith("ساعت"):
                if not await is_time_locked(chat_id=chat_id):
                    await send_time(message, text, is_deleted_timer, delet_timer)
            if text == "تایم":
                if not await is_time_locked(chat_id=chat_id):
                    now = Hour()
                    w = Week()
                    await reply(message, f"{now} ⌯ {w}", is_deleted_timer, delet_timer)
            if text == "تاریخ":
                if not await is_date_locked(chat_id):
                    a, b, c, d, e, f = Year(), Month(), Day(), Date(), Hour(), Week()
                    text_response = f"""
📅 **تاریخ و زمان کنونی**

⏰ **ساعت:** {e}
🗓️ **تاریخ:** {d}
📆 **روز:** {f}

📊 **جزئیات:**
├─ 📅 سال: {a}
├─ 📆 ماه: {b}
├─ 📌 روز: {c}
└─ 🕰️ ساعت: {e}

🎊 اوقات خوشی داشته باشید!
                    """
                    await reply(message, text_response, is_deleted_timer, delet_timer)
            if text == "تاس":
                if not await is_tas_locked(chat_id=chat_id):
                    t_result = await roll_dice(message)
                    if is_deleted_timer:
                        a = await bot.send_image(
                            chat_id=chat_id,
                            path=t_result,
                            text="🎲 تاس ریخته شد ",
                            reply_to_message_id=message.message_id,
                        )
                        await asyncio.sleep(delet_timer)
                        await bot.delete_message(chat_id, a.message_id)
                    else:
                        await bot.send_image(
                            chat_id=chat_id,
                            path=t_result,
                            text="🎲 تاس ریخته شد ",
                            reply_to_message_id=message.message_id,
                        )
            if text == "سکه":
                if not await is_seke_locked(chat_id=chat_id):
                    t_result = await flip_coin(message)
                    await reply(
                        message,
                        await MPro(f"🪙 سکه انداخته شد: {t_result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "عدد شانسی":
                if not await is_random_num_locked(chat_id=chat_id):
                    t_result = await random_number(message)
                    await reply(
                        message,
                        await MPro(f"🔢 عدد شانسی: {t_result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "چالش":
                if not await is_chalesh_locked(chat_id):
                    result = await get_chalesh()
                    await reply(
                        message,
                        await MPro(f"🎯 **چالش**\n{result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "بیو":
                if not await is_bio_locked(chat_id):
                    result = await get_bio()
                    await reply(
                        message,
                        await MPro(f"🧍‍♂️ **بیو**\n{result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "حدیث":
                if not await is_hadis_locked(chat_id):
                    result = await get_hadis()
                    await reply(
                        message,
                        await MPro(f"📜 **حدیث**\n{result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text.startswith("ترجمه"):
                if not await is_trans_locked(chat_id):
                    cmd = text.split()
                    if len(cmd) < 3:
                        return await reply(
                            message,
                            "❌ فرمت درست نیست\nمثال:\nترجمه en سلام من علی هستم",
                            is_deleted_timer,
                            delet_timer,
                        )
                    lang = cmd[1]
                    t = " ".join(cmd[2:])
                    try:
                        r = translate_text(text=t, lang=lang)
                        result = r.get("translation")
                        rr = r.get("detected_lang")
                        await reply(
                            message,
                            await MPro(
                                f"📜 **نتیجه ترجمه ({lang})**\n\nزبان: \n{lang} to {rr}\nمتن خروجی: \n{result}",
                                chat_id=chat_id,
                            ),
                            is_deleted_timer,
                            delet_timer,
                        )
                    except Exception as e:
                        pass
            if text == "قیمت طلا":
                if not await is_gold_locked(chat_id):
                    gold_chunks, silver_chunks, update_time = get_gold_lists_sorted()
                    for chunk in gold_chunks:
                        await reply(
                            message,
                            await MPro(
                                chunk + f"\n⏰ بروزرسانی: {update_time}",
                                chat_id=chat_id,
                            ),
                            is_deleted_timer,
                            delet_timer,
                        )
                    for chunk in silver_chunks:
                        await reply(
                            message,
                            await MPro(
                                chunk + f"\n⏰ بروزرسانی: {update_time}",
                                chat_id=chat_id,
                            ),
                            is_deleted_timer,
                            delet_timer,
                        )
            if text == "قیمت سکه":
                if not await is_coin_locked(chat_id):
                    cmd = get_coin_text()
                    await reply(
                        message,
                        await MPro(text=cmd, chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "قیمت ارز":
                if not await is_currency_locked(chat_id):
                    cmd = get_currency_text()
                    await reply(
                        message,
                        await MPro(text=cmd, chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text not in ["قیمت ارز", "قیمت طلا", "قیمت سکه"]:
                if not await is_gimat_locked(chat_id):
                    if text.startswith("قیمت"):
                        cmd = text[5:]
                        r = get_digital_currency_text(cmd)
                        await reply(
                            message,
                            await MPro(text=r, chat_id=chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
            if text == "دانستنی":
                if not await is_danetani_locked(chat_id):
                    result = await get_danestani()
                    await reply(
                        message,
                        await MPro(f"💡 **دانستنی**\n{result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "جوک":
                if not await is_jok_locked(chat_id):
                    result = await get_jok()
                    await reply(
                        message,
                        await MPro(f"😂 **جوک**\n{result}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "سازنده":
                await reply(
                    message,
                    await MPro(
                        f"[👨‍💻 سازنده]({CREATOR_GUID})",
                        chat_id=chat_id,
                    ),
                    is_deleted_timer,
                    delet_timer,
                )
            if text == "ماشین حساب":
                await reply(
                    message,
                    await MPro(
                        "**🧮 ماشین حساب**\n\n"
                        "روش استفاده:\n"
                        "جمع: 10+10\n"
                        "تقسیم: 10÷5\n"
                        "ضرب: 5×5\n"
                        "تفریق: 50-2",
                        chat_id=chat_id,
                    ),
                    is_deleted_timer,
                    delet_timer,
                )
            if text in ["داستان", "/story", "📖"]:
                if not await is_dastan_locked(chat_id):
                    story = await get_dastan()
                    await reply(
                        message,
                        await MPro(f"📖 **داستان**\n{story}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text in ["دیالوگ", "/dialog", "💭"]:
                if not await is_dialog_locked(chat_id):
                    dialog = await get_dialog()
                    await reply(
                        message,
                        await MPro(f"💭 **دیالوگ**\n{dialog}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text in ["فال", "/fal", "🔮"]:
                if not await is_fal_locked(chat_id):
                    fal = await get_fal()
                    await reply(
                        message,
                        await MPro(f"🔮 **فال**\n{fal}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text in ["غزل", "/ghazal", "📜"]:
                if not await is_gazal_locked(chat_id):
                    ghazal = await get_gazal()
                    await reply(
                        message,
                        await MPro(f"📜 **غزل**\n{ghazal}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text in ["فیک", "/fake", "👥"]:
                if not await is_fake_locked(chat_id):
                    fake = await get_fake()
                    await reply(
                        message,
                        await MPro(f"👥 **اطلاعات فیک**\n{fake}", chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "لیست سرگرمی":
                if not await is_list_sar_locked(chat_id):
                    entertainment_commands = [
                        "تاس 🎲",
                        "سکه 🪙",
                        "عدد شانسی 🔢",
                        "چالش 📝",
                        "بیو 👤",
                        "دانستنی 📚",
                        "جوک 😂",
                        "ماشین حساب 🧮",
                        "حدیث 💬",
                        "داستان 📖",
                        "دیالوگ 💭",
                        "فال 🔮",
                        "غزل 📜",
                        "فیک 👥",
                        "ساعت ⏰",
                        "تایم 📅",
                        "بگو 📝",
                        "جی پی تی",
                        "قیمت ارز",
                        "قیمت طلا",
                        "قیمت سکه",
                    ]
                    formatted_text = "**لیست سرگرمی‌ها:**\n\n"
                    for cmd in entertainment_commands:
                        formatted_text += f"- {cmd}\n"
                    await reply(
                        message,
                        await MPro(formatted_text, chat_id=chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "لیست":
                if not await is_list_locked(chat_id):
                    lists = [
                        "لیست ادمین",
                        "لیست ویژه",
                        "لیست قفل",
                        "لیست سرگرمی",
                        "لیست معاف",
                        "لیست سکوت",
                        "لیست شکل",
                        "لیست محدودیت",
                    ]
                    formatted_text = "◄ لیست ها 〔 📑  〕\n\n"
                    for item in lists:
                        formatted_text += f" {item}\n"
                    await reply(
                        message,
                        await MPro(formatted_text, chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
            if text == "ریست" and (rol in ["owner"] or message.sender_id == suport):
                lists = ["ریست گروه", "ریست لیست ادمین", "ریست لیست ویژه"]
                formatted_text = "◄ ریست ها 〔 🚫  〕\n\n"
                for item in lists:
                    formatted_text += f" {item}"
                await reply(
                    message,
                    await MPro(formatted_text, chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            if text == "لیست شکل" and (
                rol in ["owner", "vip"] or message.sender_id == suport
            ):
                lis = [
                    "1 . پیشوند ❖",
                    "2 . پیشوند »",
                    "3 . پیشوند •",
                    "4 . پیشوند ◄",
                    "5 . ```شکل متن```",
                    "6 . ||شکل متن||",
                    "7 . **شکل متن**",
                    "8 . __شمل متن__",
                    "9 . --شکل متن--",
                    "10 . `شکل متن`",
                    "11 . ~~شکل متن~~",
                    "12 . شکسته => س‌ل‌ا‌م",
                    "13 . فاصله دار => س ل ا م",
                    "14 . متن معکوس",
                    "15 . پیشوند تاریخ",
                    "16 . باکس پیام",
                ]
                formatted_text = "◄ لیست شکل 〔 📑  〕\n\n"
                for item in lis:
                    formatted_text += f" {item}\n"
                await reply(
                    message,
                    await MPro(formatted_text, chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            if text == "لیست معاف" and (
                rol in ["owner", "vip"] or message.sender_id == suport
            ):
                await handle_exempt_list_command(
                    msg=message,
                    is_deleted_timer=is_deleted_timer,
                    delet_timer=delet_timer,
                )
            if text == "لیست سکوت" and (
                rol in ["owner", "vip"] or message.sender_id == suport
            ):
                await handle_sokot_list_command(message, is_deleted_timer, delet_timer)
            if text.startswith("تنظیم اسم") and (
                rol == "owner" or message.sender_id == suport
            ):
                cmd = text[10:]
                await add_bot_name(chat_id, cmd)
                await reply(
                    message,
                    await MPro(f"اسم ربات با موفقیت به {cmd} تغییر کرد", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            if cmd in ["اصل", "لقب"]:
                if not message.reply_to_message_id:
                    return await reply(
                        message,
                        await MPro(
                            "❌ لطفاً روی پیام فرد مورد نظر ریپلای کنید.", chat_id
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
                rep = await bot.get_message(
                    chat_id=chat_id, message_id=message.reply_to_message_id
                )
                target_id = rep.get("sender_id") if rep else None
                if not target_id:
                    return await reply(
                        message,
                        await MPro("❌ کاربر یافت نشد.", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                elif cmd == "اصل":
                    orig = await get_original(chat_id, target_id)
                    return await reply(
                        message,
                        await MPro(
                            f"💠 اصل: {orig or 'هیچ مقداری تنظیم نشده'}",
                            chat_id,
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
                elif cmd == "لقب":
                    nick = await get_nickname(chat_id, target_id)
                    return await reply(
                        message,
                        await MPro(
                            f"🏷️ لقب: {nick or 'هیچ لقبی تنظیم نشده'}",
                            chat_id,
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
            elif text.startswith("بگو"):
                badd = await check_text_advanced(text)
                bad = badd["data"]["keywords_found"] if badd.get("success") else None
                if not bad and not any(
                    x in text for x in ["@", "http", ".com", ".ir", "www."]
                ):
                    cmd = text[4:].strip()
                    if cmd:
                        await reply(
                            message,
                            await MPro(cmd, chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
                    else:
                        await reply(
                            message,
                            await MPro("چی باید بگم؟ 😅", chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
            elif "!" in text:
                return
    except Exception as e:
        print(f"Error in entertainment features: {e}")
async def handle_calculator_features(
    chat_id, message, text, bot_name, delet_timer, is_deleted_timer
):
    try:
        if text and any(
            op in text
            for op in [
                "+",
                "-",
                "*",
                "/",
                "^",
                "**",
                "(",
                ")",
                "sqrt",
                "sin",
                "cos",
                "tan",
                "log",
            ]
        ):
            if await are_calculator_dashboard(chat_id=chat_id):
                await smart_calculator(message, is_deleted_timer, delet_timer)
    except Exception as e:
        print(f"Error in calculator features: {e}")
async def handle_user_info_features(
    chat_id,
    message,
    text,
    bot,
    send_id,
    sender_id,
    admin,
    suport,
    bot_name,
    delet_timer,
    is_deleted_timer,
):
    try:
        if text:
            if (
                text == "اطلاعات"
                or text == "info"
                or text == "اینفو"
                or text == "امار"
                or text == "آمار"
                or text == "شامار"
                or text == "آمارم"
                or text == "امارم"
            ):
                chat_id = message.chat_id
                if message.reply_to_message_id:
                    get_mess = await bot.get_message(
                        chat_id=chat_id, message_id=message.reply_to_message_id
                    )
                    try:
                        rep = await bot.get_message(
                            chat_id=chat_id, message_id=message.reply_to_message_id
                        )
                        target_user_id = rep["sender_id"]
                    except:
                        await reply(
                            message,
                            await MPro(
                                "❌ نتونستم پیام ریپلای شده رو پیدا کنم.", chat_id
                            ),
                            is_deleted_timer,
                            delet_timer,
                        )
                        return
                else:
                    get_mess = await bot.get_message(
                        chat_id=chat_id, message_id=message.message_id
                    )
                    target_user_id = sender_id
                data = await get_member(chat_id, target_user_id)
                if not data:
                    await add_member(chat_id, target_user_id, "member")
                    data = await get_member(chat_id, target_user_id)
                role = data.get("role", None)
                messages = data.get("messages", 0)
                photos = data.get("photos", 0)
                videos = data.get("videos", 0)
                documents = data.get("documents", 0)
                links = data.get("links", 0)
                voice = data.get("voice", 0)
                hashtag = data.get("hashtag", 0)
                english = data.get("english", 0)
                persian = data.get("persian", 0)
                sticker = data.get("sticker", 0)
                gif = data.get("id", 0)
                name = await bot.get_name(chat_id=chat_id)
                orig = await get_original(chat_id, target_user_id)
                nick = await get_nickname(chat_id, target_user_id)
                if nick == None:
                    nick = "بدون لقب"
                if orig == None:
                    orig = "بدون اصل"
                info_text = f"""
📊 **اطلاعات کاربر**

👤 **group:** [{name}]({get_mess["chat_id"]})
👤 **User:** [{nick}]({target_user_id})


👑 **سمت:**〔 {role} 〕
👤 **اصل:** 〔 {orig} 〕
📝 **پیام‌ها:** 「{messages}」
📷 عکس: 「{photos}」
🔗 لینک: 「{links}」
🎥 ویدیو: 「{videos}」
📄 فایل: 「{documents}」
🎤 ویس: 「{voice}」
🏷 هشتگ: 「{hashtag}」
🇬🇧 متن انگلیسی: 「{english}」
🇮🇷 متن فارسی: 「{persian}」
🎭 استیکر: 「{sticker}」
"""
                await reply(
                    message,
                    await MPro(info_text, chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            elif text == "گویدم":
                await reply(
                    message,
                    await MPro(
                        f"🌟اطلاعات شما:\n\n🔹️چت ایدی: `{message.chat_id}`\n🔹️یوزر ایدی: `{message.sender_id}`"
                    ),
                    is_deleted_timer,
                    delet_timer,
                )
            elif text == "گوید":
                rep = await bot.get_message(
                    chat_id=chat_id, message_id=message.reply_to_message_id
                )
                target_user_id = rep["sender_id"]
                if message.reply_to_message_id:
                    await reply(
                        message,
                        await MPro(
                            f"🌟اطلاعات کاربر:\n\n🔹️چت ایدی: `{message.chat_id}`\n🔹️یوزر ایدی: `{target_user_id}`"
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
    except Exception as e:
        print(f"Error in user info features: {e}")
async def handle_admin_management_features(
    chat_id,
    message,
    text,
    bot,
    send_id,
    rol,
    suport,
    bot_name,
    delet_timer,
    is_deleted_timer,
):
    if text:
        async def list_group_admins_cmd():
            lists = await list_group_admins(chat_id=chat_id)
            if not lists:
                await reply(
                    message,
                    await MPro("⚡ هیچ ادمینی ثبت نشده!", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
                return
            msg = "⚡ **لیست ادمین‌ها گروه:**\n\n"
            for idx, user_id in enumerate(lists, start=1):
                msg += f"{idx}. 👤 | `{user_id}`\n"
            msg += f"\n📌 تعداد ادمین ها: {len(lists)} نفر"
            await reply(
                message, await MPro(msg, chat_id), is_deleted_timer, delet_timer
            )
        async def handle_entertainment_lock():
            await handle_entertainment_lock_status(
                msg=message, bot=bot, is_deleted_timer=False, delet_timer=10
            )
        async def list_group_vips_cmd():
            lists = await list_group_vips(chat_id=chat_id)
            if not lists:
                await reply(
                    message,
                    await MPro("⚡ هیچ ادمین ویژه‌ای ثبت نشده!", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
                return
            msg = "⚡ **لیست ادمین‌های ویژه گروه:**\n\n"
            for idx, user_id in enumerate(lists, start=1):
                msg += f"{idx}. 👤 | `{user_id}`\n"
            msg += f"\n📌 تعداد ویژه‌ها: {len(lists)} نفر"
            await reply(
                message, await MPro(msg, chat_id), is_deleted_timer, delet_timer
            )
        async def dashboard_cmd():
            lists = await get_all_dashboards(chat_id=chat_id)
            result = format_dashboard(lists, 5)
            await reply(message, result, is_deleted_timer, delet_timer)
        async def handle_lock_status_cmd():
            await handle_lock_status(
                msg=message,
                bot=bot,
                is_deleted_timer=is_deleted_timer,
                delet_timer=delet_timer,
            )
        async def cmd_dashboard_speak_vip():
            await dashboard_speak_vip(chat_id=chat_id)
            await undashboard_speak(chat_id=chat_id)
            await undashboard_speak_bad(chat_id=chat_id)
            await reply(
                message,
                await MPro("سخنگو شخصی روشن شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_dashboard_delet_timer():
            await dashboard_delet_timer(chat_id=chat_id)
            await reply(
                message,
                await MPro("حذف خودکار روشن شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_undashboard_delet_timer():
            await undashboard_delet_timer(chat_id=chat_id)
            await reply(
                message,
                await MPro("حذف خودکار خاموش شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_undashboard_speak_vip():
            await undashboard_speak_vip(chat_id=chat_id)
            await reply(
                message,
                await MPro("سخنگو شخصی خاموش شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_dashboard_speak():
            await dashboard_speak(chat_id=chat_id)
            await undashboard_speak_bad(chat_id=chat_id)
            await undashboard_speak_vip(chat_id=chat_id)
            await reply(
                message,
                await MPro("سخنگو روشن شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_undashboard_speak():
            await undashboard_speak(chat_id=chat_id)
            await reply(
                message,
                await MPro("سخنگو خاموش شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_dashboard_speak_bad():
            a = await get_group_charge_status(chat_id)
            v = a.get("is_active")
            if v:
                await dashboard_speak_bad(chat_id=chat_id)
                await undashboard_speak(chat_id=chat_id)
                await undashboard_speak_vip(chat_id=chat_id)
                await reply(
                    message,
                    await MPro("سخنگو بی ادب روشن شد", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            else:
                await reply(
                    message,
                    f"برای گروه شما شارژی تایین نشده جهت خرید به ایدی زیر مراجعه کنید\n\n{SUPPORT_USERNAME}",
                    is_deleted_timer,
                    delet_timer,
                )
        async def cmd_undashboard_speak_bad():
            await undashboard_speak_bad(chat_id=chat_id)
            await reply(
                message,
                await MPro("سخنگو بی ادب خاموش شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_dashboard_calculator():
            await dashboard_calculator(chat_id=chat_id)
            await reply(
                message,
                await MPro("ماشین حساب روشن شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        async def cmd_undashboard_calculator():
            await undashboard_calculator(chat_id=chat_id)
            await reply(
                message,
                await MPro("ماشین حساب خاموش شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        def _mk(fn, txt, cid=True):
            async def run():
                await fn(chat_id)
                await reply(message, await (MPro(txt, chat_id) if cid else MPro(txt)), is_deleted_timer, delet_timer)
            return run
        cmd_lock_links = _mk(lock_links, "🔒 لینک‌ها قفل شدند")
        cmd_unlock_links = _mk(unlock_links, "🔓 قفل لینک‌ها باز شد")
        cmd_lock_english = _mk(lock_english, "🔒 متن انگلیسی قفل شد")
        cmd_unlock_english = _mk(unlock_english, "🔓 قفل متن انگلیسی باز شد", False)
        cmd_lock_media = _mk(lock_media, "🔒 رسانه قفل شد")
        cmd_unlock_media = _mk(unlock_media, "🔓 ارسال رسانه آزاد شد")
        cmd_lock_ids = _mk(lock_ids, "🔒 ایدی با موفقیت قفل شد")
        cmd_unlock_ids = _mk(unlock_ids, "🔓 ایدی با موفقیت آزاد شد")
        cmd_lock_documents = _mk(lock_documents, "🔒 فایل قفل شد")
        cmd_unlock_documents = _mk(unlock_documents, "🔓 فایل آزاد شد")
        cmd_lock_polls = _mk(lock_polls, "🔒 نظرسنجی قفل شد")
        cmd_unlock_polls = _mk(unlock_polls, "🔓 نظرسنجی آزاد شد")
        cmd_lock_location = _mk(lock_location, "🔒 موقعیت مکانی قفل شد")
        cmd_unlock_location = _mk(unlock_location, "🔓 موقعیت مکانی آزاد شد")
        cmd_lock_sticker = _mk(lock_sticker, "🔒 استیکر قفل شد")
        cmd_unlock_sticker = _mk(unlock_sticker, "🔓 استیکر آزاد شد")
        cmd_lock_forward = _mk(lock_forward, "🔒 فوروارد قفل شد")
        cmd_unlock_forward = _mk(unlock_forward, "🔓 فوروارد آزاد شد")
        cmd_lock_photos = _mk(lock_photos, "🔒 عکس قفل شد")
        cmd_unlock_photos = _mk(unlock_photos, "🔓 عکس آزاد شد")
        cmd_lock_videos = _mk(lock_videos, "🔒 فیلم قفل شد")
        cmd_unlock_videos = _mk(unlock_videos, "🔓 فیلم آزاد شد")
        cmd_lock_voice = _mk(lock_voice, "🔒 ویس قفل شد")
        cmd_unlock_voice = _mk(unlock_voice, "🔓 ویس آزاد شد")
        cmd_lock_spoiler = _mk(lock_spoiler, "🔒 اسپویلر قفل شد")
        cmd_unlock_spoiler = _mk(unlock_spoiler, "🔓 اسپویلر آزاد شد")
        cmd_lock_persian = _mk(lock_persian, "🔒 فارسی قفل شد")
        cmd_unlock_persian = _mk(unlock_persian, "🔓 فارسی آزاد شد")
        cmd_lock_hashtag = _mk(lock_hashtag, "🔒 هشتک قفل شد")
        cmd_unlock_hashtag = _mk(unlock_hashtag, "🔓 هشتک آزاد شد")
        cmd_lock_mention = _mk(lock_mention, "🔒 منش قفل شد")
        cmd_unlock_mention = _mk(unlock_mention, "🔓 منش آزاد شد")
        cmd_lock_Quote = _mk(lock_Quote, "🔒 نقل قول قفل شد")
        cmd_unlock_Quote = _mk(unlock_Quote, "🔓 نقل قول آزاد شد")
        cmd_lock_Bold = _mk(lock_Bold, "🔒 برجسته قفل شد")
        cmd_unlock_Bold = _mk(unlock_Bold, "🔓 برجسته آزاد شد")
        cmd_lock_Italic = _mk(lock_Italic, "🔒 کج قفل شد")
        cmd_unlock_Italic = _mk(unlock_Italic, "🔓 کج آزاد شد")
        cmd_lock_Underline = _mk(lock_Underline, "🔒 زیر خط قفل شد")
        cmd_unlock_Underline = _mk(unlock_Underline, "🔓 زیر خط آزاد شد")
        cmd_lock_Strike = _mk(lock_Strike, "🔒 خط خورده قفل شد")
        cmd_unlock_Strike = _mk(unlock_Strike, "🔓 خط خورده آزاد شد")
        cmd_lock_Mono = _mk(lock_Mono, "🔒 تکی قفل شد")
        cmd_unlock_Mono = _mk(unlock_Mono, "🔓 تکی آزاد شد")
        cmd_lock_bad = _mk(lock_bad, "🔒 متن نامناسب قفل شد")
        cmd_unlock_bad = _mk(unlock_bad, "🔓 متن نامناسب آزاد شد")
        cmd_lock_spam = _mk(lock_spam, "🔒 اسپم قفل شد")
        cmd_unlock_spam = _mk(unlock_spam, "🔓 اسپم آزاد شد")
        cmd_lock_long_text = _mk(lock_long_text, "🔒 متن بلند قفل شد")
        cmd_unlock_long_text = _mk(unlock_long_text, "🔓 متن بلند آزاد شد")
        cmd_lock_filter = _mk(lock_filter, "🔒 کد هنگی قفل شد")
        cmd_unlock_filter = _mk(unlock_filter, "🔓 کد هنگی آزاد شد")
        cmd_lock_time = _mk(lock_time, "🔒 ساعت قفل شد")
        cmd_unlock_time = _mk(unlock_time, "🔓 ساعت آزاد شد")
        cmd_lock_tas = _mk(lock_tas, "🔒 تاس قفل شد")
        cmd_unlock_tas = _mk(unlock_tas, "🔓 تاس آزاد شد")
        cmd_lock_seke = _mk(lock_seke, "🔒 سکه قفل شد")
        cmd_unlock_seke = _mk(unlock_seke, "🔓 سکه آزاد شد")
        cmd_lock_random_num = _mk(lock_random_num, "🔒 عدد شانسی قفل شد")
        cmd_unlock_random_num = _mk(unlock_random_num, "🔓 عدد شانسی آزاد شد")
        cmd_lock_chalesh = _mk(lock_chalesh, "🔒 چالش قفل شد")
        cmd_unlock_chalesh = _mk(unlock_chalesh, "🔓 چالش آزاد شد")
        cmd_lock_bio = _mk(lock_bio, "🔒 بیو قفل شد")
        cmd_unlock_bio = _mk(unlock_bio, "🔓 بیو آزاد شد")
        cmd_lock_hadis = _mk(lock_hadis, "🔒 حدیث قفل شد")
        cmd_unlock_hadis = _mk(unlock_hadis, "🔓 حدیث آزاد شد")
        cmd_lock_danetani = _mk(lock_danetani, "🔒 دانستنی قفل شد")
        cmd_unlock_danetani = _mk(unlock_danetani, "🔓 دانستنی آزاد شد")
        cmd_lock_jok = _mk(lock_jok, "🔒 جوک قفل شد")
        cmd_unlock_jok = _mk(unlock_jok, "🔓 جوک آزاد شد")
        cmd_lock_dastan = _mk(lock_dastan, "🔒 داستان قفل شد")
        cmd_unlock_dastan = _mk(unlock_dastan, "🔓 داستان آزاد شد")
        cmd_lock_dialog = _mk(lock_dialog, "🔒 دیالوگ قفل شد")
        cmd_unlock_dialog = _mk(unlock_dialog, "🔓 دیالوگ آزاد شد")
        cmd_lock_fal = _mk(lock_fal, "🔒 فال قفل شد")
        cmd_unlock_fal = _mk(unlock_fal, "🔓 فال آزاد شد")
        cmd_lock_gazal = _mk(lock_gazal, "🔒 غزل قفل شد")
        cmd_unlock_gazal = _mk(unlock_gazal, "🔓 غزل آزاد شد")
        cmd_lock_fake = _mk(lock_fake, "🔒 فیک قفل شد")
        cmd_unlock_fake = _mk(unlock_fake, "🔓 فیک آزاد شد")
        cmd_lock_list = _mk(lock_list, "🔒 لیست قفل شد")
        cmd_unlock_list = _mk(unlock_list, "🔓 لیست آزاد شد")
        cmd_lock_list_sar = _mk(lock_list_sar, "🔒 لیست سرگرمی قفل شد")
        cmd_unlock_list_sar = _mk(unlock_list_sar, "🔓 لیست سرگرمی آزاد شد")
        cmd_lock_gpt = _mk(lock_gpt, "🔒 هوش مصنوعی قفل شد")
        cmd_unlock_gpt = _mk(unlock_gpt, "🔓 هوش مصنوعی آزاد شد")
        cmd_lock_gold = _mk(lock_gold, "🔒 سرویس قیمت طلا قفل شد")
        cmd_unlock_gold = _mk(unlock_gold, "🔓 سرویس قیمت طلا آزاد شد")
        cmd_lock_coin = _mk(lock_coin, "🔒 سرویس قیمت سکه قفل شد")
        cmd_unlock_coin = _mk(unlock_coin, "🔓 سرویس قیمت سکه آزاد شد")
        cmd_lock_currency = _mk(lock_currency, "🔒 سرویس قیمت ارز قفل شد")
        cmd_unlock_currency = _mk(unlock_currency, "🔓 سرویس قیمت ارز آزاد شد")
        cmd_lock_translate = _mk(lock_trans, "🔒 سرویس ترجمه قفل شد")
        cmd_unlock_translate = _mk(unlock_trans, "🔓 سرویس ترجمه آزاد شد")
        cmd_lock_crypto = _mk(lock_gimat, "🔒 سرویس قیمت ارزهای دیجیتال قفل شد")
        cmd_unlock_crypto = _mk(unlock_gimat, "🔓 سرویس قیمت ارزهای دیجیتال آزاد شد")
        cmd_lock_font = _mk(lock_font, "🔒 فونت قفل شد")
        cmd_unlock_font = _mk(unlock_font, "🔓 فونت آزاد شد")
        cmd_lock_date = _mk(lock_date, "🔒 تاریخ قفل شد")
        cmd_unlock_date = _mk(unlock_date, "🔓 تاریخ آزاد شد")
        cmd_lock_qr_code = _mk(lock_qr_code, "🔒 کیوارکد قفل شد")
        cmd_unlock_qr_code = _mk(unlock_qr_code, "🔓 کیوارکد آزاد شد")
        async def cmd_lock_all():
            await handle_lock_all(
                msg=message, is_deleted_timer=is_deleted_timer, delet_timer=delet_timer
            )
        async def cmd_unlock_all():
            await reset_locks(chat_id)
            await message.reply(
                await MPro("🔓 کل لیست قفل آزاد شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        try:
            admin = rol in ["owner", "vip"] or send_id == suport
            if admin:
                command_map = {}
                for _f, _names in (
                    (handle_lock_status_cmd, ("وضعیت قفل‌ ها", "لیست قفل")),
                    (list_group_admins_cmd, ("لیست ادمین",)),
                    (list_group_vips_cmd, ("لیست ویژه",)),
                    (dashboard_cmd, ("داشبورد",)),
                    (handle_entertainment_lock, ("محدودیت", "لیست محدودیت")),
                    (cmd_dashboard_speak, ("سخنگو روشن",)),
                    (cmd_undashboard_speak, ("سخنگو خاموش",)),
                    (cmd_dashboard_speak_bad, ("سخنگو بی ادب روشن",)),
                    (cmd_undashboard_speak_bad, ("سخنگو بی ادب خاموش",)),
                    (cmd_dashboard_calculator, ("ماشین حساب روشن",)),
                    (cmd_undashboard_calculator, ("ماشین حساب خاموش",)),
                    (cmd_dashboard_speak_vip, ("سخنگو شخصی روشن",)),
                    (cmd_undashboard_speak_vip, ("سخنگو شخصی خاموش",)),
                    (cmd_dashboard_delet_timer, ("حذف خودکار روشن",)),
                    (cmd_undashboard_delet_timer, ("حذف خودکار خاموش",)),
                    (cmd_lock_date, ("قفل تاریخ",)),
                    (cmd_lock_font, ("قفل فونت",)),
                    (cmd_lock_currency, ("قفل قیمت ارز", "قفل ارز", "قیمت ارز قفل", "ارز قفل", "قیمت ارز خاموش")),
                    (cmd_lock_translate, ("قفل ترجمه", "ترجمه قفل", "ترجمه خاموش")),
                    (cmd_lock_crypto, ("قفل قیمت ارز دیجیتال", "قفل ارز دیجیتال", "قفل رمزارز", "قیمت ارز دیجیتال قفل", "ارز دیجیتال قفل", "رمزارز قفل", "ارز دیجیتال خاموش")),
                    (cmd_lock_links, ("قفل لینک", "لینک قفل")),
                    (cmd_lock_english, ("قفل انگلیسی", "انگلیسی قفل")),
                    (cmd_lock_media, ("قفل رسانه", "رسانه قفل")),
                    (cmd_lock_ids, ("قفل ایدی", "قفل آیدی", "آیدی قفل")),
                    (cmd_lock_documents, ("قفل فایل", "فایل قفل")),
                    (cmd_lock_polls, ("قفل نظرسنجی", "نظرسنجی قفل")),
                    (cmd_lock_location, ("قفل موقعیت مکانی", "موقعیت مکانی قفل")),
                    (cmd_lock_sticker, ("قفل استیکر", "استیکر قفل")),
                    (cmd_lock_forward, ("قفل فوروارد", "فوروارد قفل")),
                    (cmd_lock_photos, ("قفل عکس", "عکس قفل")),
                    (cmd_lock_videos, ("قفل فیلم", "فیلم قفل")),
                    (cmd_lock_voice, ("قفل ویس", "ویس قفل")),
                    (cmd_lock_spoiler, ("قفل اسپویلر", "اسپویلر قفل")),
                    (cmd_lock_persian, ("قفل فارسی", "فارسی قفل")),
                    (cmd_lock_hashtag, ("قفل هشتک", "هشتک قفل")),
                    (cmd_lock_mention, ("قفل منش", "منشن قفل")),
                    (cmd_lock_Quote, ("قفل نقل قول", "نقل قول قفل")),
                    (cmd_lock_Bold, ("قفل برجسته", "برجسته قفل")),
                    (cmd_lock_Italic, ("قفل کج", "کج قفل")),
                    (cmd_lock_Underline, ("قفل زیر خط", "زیر خط قفل")),
                    (cmd_lock_Strike, ("قفل خط خورده", "خط خورده قفل")),
                    (cmd_lock_Mono, ("قفل تکی", "تکی قفل")),
                    (cmd_lock_bad, ("قفل متن نامناسب", "متن نامناسب قفل")),
                    (cmd_lock_spam, ("قفل اسپم", "اسپم قفل")),
                    (cmd_lock_long_text, ("قفل متن بلند", "متن بلند قفل")),
                    (cmd_lock_filter, ("قفل کد هنگی", "کد هنگی قفل")),
                    (cmd_lock_all, ("قفل همه", "همه قفل")),
                    (cmd_lock_time, ("قفل ساعت", "ساعت قفل", "ساعت خاموش")),
                    (cmd_lock_tas, ("قفل تاس", "تاس قفل", "تاس خاموش")),
                    (cmd_lock_coin, ("قفل سکه", "سکه خاموش")),
                    (cmd_lock_random_num, ("قفل عدد شانسی", "عدد شانسی قفل", "عدد شانسی خاموش")),
                    (cmd_lock_chalesh, ("قفل چالش", "چالش قفل", "چالش خاموش")),
                    (cmd_lock_bio, ("قفل بیو", "بیو قفل", "بیو خاموش")),
                    (cmd_lock_hadis, ("قفل حدیث", "حدیث قفل", "حدیث خاموش")),
                    (cmd_lock_danetani, ("قفل دانستنی", "دانستنی قفل", "دانستنی خاموش")),
                    (cmd_lock_jok, ("قفل جوک", "جوک قفل", "جوک خاموش")),
                    (cmd_lock_dastan, ("قفل داستان", "داستان قفل", "داستان خاموش")),
                    (cmd_lock_dialog, ("قفل دیالوگ", "دیالوگ قفل", "دیالوگ خاموش")),
                    (cmd_lock_fal, ("قفل فال", "فال قفل", "فال خاموش")),
                    (cmd_lock_gazal, ("قفل غزل", "غزل قفل", "غزل خاموش")),
                    (cmd_lock_fake, ("قفل فیک", "فیک قفل", "فیک خاموش")),
                    (cmd_lock_list, ("قفل لیست", "لیست خاموش")),
                    (cmd_lock_list_sar, ("قفل لیست سرگرمی", "لیست سرگرمی قفل", "لیست سرگرمی خاموش")),
                    (cmd_lock_gpt, ("قفل هوش مصنوعی", "هوش مصنوعی خاموش")),
                    (cmd_lock_seke, ("سکه قفل",)),
                    (cmd_lock_gold, ("قفل طلا", "طلا خاموش")),
                    (cmd_lock_qr_code, ("قفل کیوارکد",)),
                    (cmd_unlock_date, ("تاریخ باز",)),
                    (cmd_unlock_qr_code, ("کیوارکد باز",)),
                    (cmd_unlock_font, ("ازاد کردن فونت", "فونت باز")),
                    (cmd_unlock_gpt, ("آزاد کردن هوش مصنوعی", "هوش مصنوعی باز", "هوش مصنوعی روشن")),
                    (cmd_unlock_gold, ("آزاد کردن طلا", "طلا باز")),
                    (cmd_unlock_seke, ("آزاد کردن سکه", "سکه باز", "سکه آزاد", "سکه روشن")),
                    (cmd_unlock_links, ("آزاد کردن لینک", "لینک آزاد", "لینک باز")),
                    (cmd_unlock_english, ("آزاد کردن انگلیسی", "انگلیسی آزاد", "انگلیسی باز")),
                    (cmd_unlock_media, ("آزاد کردن رسانه", "رسانه آزاد", "رسانه باز")),
                    (cmd_unlock_ids, ("آزاد کردن ایدی", "آزاد کردن آیدی", "آیدی آزاد", "آیدی باز")),
                    (cmd_unlock_documents, ("آزاد کردن فایل", "فایل آزاد", "فایل باز")),
                    (cmd_unlock_polls, ("آزاد کردن نظرسنجی", "نظرسنجی آزاد", "نظرسنجی باز")),
                    (cmd_unlock_location, ("آزاد کردن موقعیت مکانی", "موقعیت مکانی آزاد", "موقعیت مکانی باز")),
                    (cmd_unlock_sticker, ("آزاد کردن استیکر", "استیکر آزاد", "استیکر باز")),
                    (cmd_unlock_forward, ("آزاد کردن فوروارد", "فوروارد آزاد", "فوروارد باز")),
                    (cmd_unlock_photos, ("آزاد کردن عکس", "عکس آزاد", "عکس باز")),
                    (cmd_unlock_videos, ("آزاد کردن فیلم", "فیلم آزاد", "فیلم باز")),
                    (cmd_unlock_voice, ("آزاد کردن ویس", "ویس آزاد", "ویس باز")),
                    (cmd_unlock_spoiler, ("آزاد کردن اسپویلر", "اسپویلر آزاد", "اسپویلر باز")),
                    (cmd_unlock_persian, ("آزاد کردن فارسی", "فارسی آزاد", "فارسی باز")),
                    (cmd_unlock_hashtag, ("آزاد کردن هشتک", "هشتک آزاد", "هشتک باز")),
                    (cmd_unlock_mention, ("آزاد کردن منش", "منشن آزاد", "منشن باز")),
                    (cmd_unlock_Quote, ("آزاد کردن نقل قول", "نقل قول آزاد", "نقل قول باز")),
                    (cmd_unlock_Bold, ("آزاد کردن برجسته", "برجسته آزاد", "برجسته باز")),
                    (cmd_unlock_Italic, ("آزاد کردن کج", "کج آزاد", "کج باز")),
                    (cmd_unlock_Underline, ("آزاد کردن زیر خط", "زیر خط آزاد", "زیر خط باز")),
                    (cmd_unlock_Strike, ("آزاد کردن خط خورده", "خط خورده آزاد", "خط خورده باز")),
                    (cmd_unlock_Mono, ("آزاد کردن تکی", "تکی آزاد", "تکی باز")),
                    (cmd_unlock_bad, ("آزاد کردن متن نامناسب", "متن نامناسب آزاد", "متن نامناسب باز")),
                    (cmd_unlock_spam, ("آزاد کردن اسپم", "اسپم آزاد", "اسپم باز")),
                    (cmd_unlock_long_text, ("آزاد کردن متن بلند", "متن بلند آزاد", "متن بلند باز")),
                    (cmd_unlock_filter, ("آزاد کردن کد هنگی", "کد هنگی آزاد", "کد هنگی باز")),
                    (cmd_unlock_all, ("آزاد کردن همه", "همه آزاد", "همه باز")),
                    (cmd_unlock_time, ("آزاد کردن ساعت", "ساعت آزاد", "ساعت باز", "ساعت روشن")),
                    (cmd_unlock_tas, ("آزاد کردن تاس", "تاس آزاد", "تاس باز", "تاس روشن")),
                    (cmd_unlock_random_num, ("آزاد کردن عدد شانسی", "عدد شانسی آزاد", "عدد شانسی باز", "عدد شانسی روشن")),
                    (cmd_unlock_chalesh, ("آزاد کردن چالش", "چالش آزاد", "چالش باز", "چالش روشن")),
                    (cmd_unlock_bio, ("آزاد کردن بیو", "بیو آزاد", "بیو باز", "بیو روشن")),
                    (cmd_unlock_hadis, ("آزاد کردن حدیث", "حدیث آزاد", "حدیث باز", "حدیث روشن")),
                    (cmd_unlock_danetani, ("آزاد کردن دانستنی", "دانستنی آزاد", "دانستنی باز", "دانستنی روشن")),
                    (cmd_unlock_jok, ("آزاد کردن جوک", "جوک آزاد", "جوک باز", "جوک روشن")),
                    (cmd_unlock_dastan, ("آزاد کردن داستان", "داستان آزاد", "داستان باز", "داستان روشن")),
                    (cmd_unlock_dialog, ("آزاد کردن دیالوگ", "دیالوگ آزاد", "دیالوگ باز", "دیالوگ روشن")),
                    (cmd_unlock_fal, ("آزاد کردن فال", "فال آزاد", "فال باز", "فال روشن")),
                    (cmd_unlock_gazal, ("آزاد کردن غزل", "غزل آزاد", "غزل باز", "غزل روشن")),
                    (cmd_unlock_fake, ("آزاد کردن فیک", "فیک آزاد", "فیک باز", "فیک روشن")),
                    (cmd_unlock_list, ("آزاد کردن لیست", "لیست آزاد", "لیست باز", "لیست روشن")),
                    (cmd_unlock_list_sar, ("آزاد کردن لیست سرگرمی", "لیست سرگرمی آزاد", "لیست سرگرمی باز", "لیست سرگرمی روشن")),
                ):
                    for _n in _names:
                        command_map[_n] = _f
                commands_to_execute = []
                if text.lower().startswith("multi commands"):
                    lines = text.strip().split("\n")
                    if len(lines) >= 2:
                        commands_to_execute = [
                            line.strip() for line in lines[1:] if line.strip()
                        ]
                    else:
                        return
                else:
                    commands_to_execute = [text]
                for cmd_text in commands_to_execute:
                    func = command_map.get(cmd_text)
                    if func:
                        try:
                            await func()
                            if len(commands_to_execute) > 1:
                                await asyncio.sleep(0.05)
                        except Exception:
                            pass
                if len(commands_to_execute) > 1:
                    await reply(
                        message,
                        await MPro(
                            f"✅ {len(commands_to_execute)} دستور با موفقیت اجرا شدند",
                            chat_id,
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
                if text.startswith("گیف"):
                    a = await reply(
                        message,
                        await MPro("لطفا صبر کنید...", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                    id = a.message_id
                    text = text[4:]
                    gif_path = "dragn.gif"
                    await create_farsi_typing_gif(
                        text=text,
                        filename=gif_path,
                        size=(600, 550),
                        duration_per_char=2,
                    )
                    gif_path = Path(r"dragn.gif")
                    if not gif_path.exists():
                        await bot.edit_message_text(
                            chat_id=chat_id, message_id=id, text="خطا در پیدا کردن فایل"
                        )
                    else:
                        await bot.delete_message(chat_id=chat_id, message_id=id)
                        await bot.send_gif(chat_id=chat_id, path=gif_path)
                elif text.startswith("تنظیم شکل"):
                    cmd = text[10:]
                    await set_group_model(chat_id=chat_id, model=int(cmd))
                    await reply(
                        message,
                        await MPro("شکل با موفقیت تنظیم شد", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                elif text == "وضعیت اخطار":
                    stats = await get_warning_stats(chat_id)
                    text = f"📊 **وضعیت اخطارهای گروه**\n\n"
                    text += f"🎯 سقف اخطار: {stats['max_warnings']}\n"
                    text += f"🔨 مجازات: {stats['penalty_type']}\n"
                    text += f"👤 کاربران اخطاردار: {stats['total_warned_users']}\n"
                    text += f"📈 کل اخطارها: {stats['total_warnings']}\n\n"
                    if stats["near_penalty_users"]:
                        text += "⚠️ **کاربران نزدیک به مجازات:**\n"
                        for user in stats["near_penalty_users"][
                            :10
                        ]:
                            text += f"• `{user['user_id']}`: {user['warnings']}/{stats['max_warnings']} (فقط {user['remaining']} اخطار باقی مانده)\n"
                    if stats["max_reached_users"]:
                        text += f"\n🚨 **کاربران نیازمند مجازات ({len(stats['max_reached_users'])} نفر):**\n"
                        for user in stats["max_reached_users"][:10]:
                            text += f"• `{user['user_id']}`: {user['warnings']}/{stats['max_warnings']}\n"
                    await reply(message, text, is_deleted_timer, delet_timer)
                elif text == "تعداد اخطار" or (
                    bot_name in text
                    and "تعداد" in text
                    and "اخطار" in text
                    and rol in ["owner", "vip"]
                ):
                    if message.reply_to_message_id:
                        get_mess = await bot.get_message(
                            chat_id=chat_id, message_id=message.reply_to_message_id
                        )
                        if get_mess:
                            target_user_id = str(get_mess["sender_id"])
                        try:
                            warning_result = await get_warnings(chat_id, target_user_id)
                            if warning_result:
                                war = warning_result.get("warnings")
                                max_war = warning_result.get("max")
                                last_war = warning_result.get("last_warning")
                                warning_text = (
                                    f"⚠️ اخطار های کاربر {target_user_id}\n"
                                    f"📊 تعداد اخطار: {war}\n"
                                    f"🚨 حداکثر اخطار: {max_war}\n"
                                    f"🔨 تاریخ اخرین اخطار: {last_war}\n"
                                )
                                await reply(
                                    message, warning_text, is_deleted_timer, delet_timer
                                )
                            else:
                                await reply(
                                    message,
                                    await MPro("کاربر خطایی ندارد", chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                        except Exception as e:
                            await reply(
                                message,
                                f"❌ خطا در دریافت اطلاعات کاربر: {e}",
                                is_deleted_timer,
                                delet_timer,
                            )
                    else:
                        await reply(
                            message,
                            "❌ لطفاً روی پیام کاربر ریپلای کنید و دستور تعداد اخطار را وارد کنید",
                            is_deleted_timer,
                            delet_timer,
                        )
                elif text == "حذف اخطار" or (
                    bot_name in text
                    and "اخطار" in text
                    and "حذف" in text
                    and rol in ["owner", "vip"]
                ):
                    if message.reply_to_message_id:
                        get_mess = await bot.get_message(
                            chat_id=chat_id, message_id=message.reply_to_message_id
                        )
                        if get_mess:
                            target_user_id = str(get_mess["sender_id"])
                        try:
                            warning_result = await reset_warnings(
                                chat_id, target_user_id
                            )
                            if warning_result:
                                warning_text = (
                                    f"⚠️ اخطار به کاربر {target_user_id}\n"
                                    f"📊 پاک شد ✅"
                                )
                                await reply(
                                    message, warning_text, is_deleted_timer, delet_timer
                                )
                        except Exception as e:
                            await reply(
                                message,
                                f"❌ خطا در دریافت اطلاعات کاربر: {e}",
                                is_deleted_timer,
                                delet_timer,
                            )
                    else:
                        await reply(
                            message,
                            "❌ لطفاً روی پیام کاربر ریپلای کنید و دستور حذف اخطار را وارد کنید",
                            is_deleted_timer,
                            delet_timer,
                        )
                elif (
                    text == "اخطار"
                    or text.startswith("اخطار")
                    or (
                        bot_name in text and "اخطار" in text and rol in ["owner", "vip"]
                    )
                ):
                    if message.reply_to_message_id:
                        get_mess = await bot.get_message(
                            chat_id=chat_id, message_id=message.reply_to_message_id
                        )
                        if get_mess:
                            target_user_id = str(get_mess["sender_id"])
                        roll = await get_user_role(
                            chat_id=chat_id, user_id=target_user_id
                        )
                        if await is_member_exempt(
                            chat_id=chat_id, sender_id=target_user_id
                        ):
                            await reply(
                                message,
                                await MPro("کاربر معاف است", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                            return
                        if roll == "vip":
                            await reply(
                                message,
                                await MPro("کاربر ویژه است", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                            return
                        if roll == "admin":
                            await reply(
                                message,
                                await MPro("کاربر ادمین است", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                            return
                        if roll == "owner":
                            await reply(
                                message,
                                await MPro("کاربر مالک است", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                            return
                        reply_message_id = message.reply_to_message_id
                        try:
                            reason = "بدون دلیل"
                            if text.startswith("اخطار "):
                                cmd_parts = text.split()
                                if len(cmd_parts) > 1:
                                    reason = " ".join(cmd_parts[1:])
                            warning_result = await add_warning(
                                chat_id, target_user_id, reason
                            )
                            if warning_result["status"] == "added":
                                warning_text = (
                                    f"⚠️ اخطار به کاربر {target_user_id}\n"
                                    f"📊 اخطارهای فعلی: {warning_result['current']}/{warning_result['max']}\n"
                                    f"📝 دلیل: {reason}\n"
                                )
                                remaining = (
                                    warning_result["max"] - warning_result["current"]
                                )
                                if remaining <= 2:
                                    warning_text += (
                                        f"⚠️ توجه: فقط {remaining} اخطار باقی مانده!\n"
                                    )
                                await reply(
                                    message, warning_text, is_deleted_timer, delet_timer
                                )
                            elif warning_result["status"] == "max_reached":
                                penalty_type = await get_group_penalty_type(chat_id)
                                warning_text = (
                                    f"🚨 کاربر {target_user_id} به سقف اخطار رسید!\n"
                                    f"📊 اخطارها: {warning_result['current']}/{warning_result['max']}\n"
                                    f"🔨 مجازات: {penalty_type}\n"
                                )
                                await reply(
                                    message, warning_text, is_deleted_timer, delet_timer
                                )
                                penalty_result = await apply_penalty(
                                    bot, chat_id, target_user_id, penalty_type
                                )
                                if penalty_result["status"] == "banned":
                                    await bot.ban_member_chat(chat_id, target_user_id)
                                    await reply(
                                        message,
                                        f"✅ کاربر {target_user_id} بن شد.",
                                        is_deleted_timer,
                                        delet_timer,
                                    )
                                elif penalty_result["status"] == "muted":
                                    await reply(
                                        message,
                                        f"✅ کاربر {target_user_id} میوت شد.",
                                        is_deleted_timer,
                                        delet_timer,
                                    )
                                await reset_warnings(chat_id, target_user_id)
                            else:
                                await reply(
                                    message,
                                    "❌ خطا در ثبت اخطار",
                                    is_deleted_timer,
                                    delet_timer,
                                )
                        except Exception as e:
                            await reply(
                                message,
                                f"❌ خطا در دریافت اطلاعات کاربر: {e}",
                                is_deleted_timer,
                                delet_timer,
                            )
                    else:
                        await reply(
                            message,
                            "❌ لطفاً روی پیام کاربر ریپلای کنید و دستور اخطار را وارد کنید",
                            is_deleted_timer,
                            delet_timer,
                        )
                elif text.startswith("تنظیم حداکثر اخطار") or text.startswith(
                    "تنظیم مجازات"
                ):
                    if text.startswith("تنظیم حداکثر اخطار"):
                        try:
                            cmd = text[19:]
                            if 0 < int(cmd) < 10:
                                warning_result = await set_group_warning_settings(
                                    chat_id, cmd
                                )
                                if warning_result.get("status") == "updated":
                                    maxw = warning_result.get("max_warnings")
                                    warning_text = (
                                        f"⚠️ حداکثر اخطار به {maxw} تغییر کرد ✅\n"
                                    )
                                    await reply(
                                        message,
                                        await MPro(warning_text, chat_id),
                                        is_deleted_timer,
                                        delet_timer,
                                    )
                            else:
                                await reply(
                                    message,
                                    await MPro("عدد باید بین صفر تا ده باشد", chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                        except Exception as e:
                            await reply(
                                message,
                                f"❌ خطا در دریافت اطلاعات گروه",
                                is_deleted_timer,
                                delet_timer,
                            )
                    elif text.startswith("تنظیم مجازات"):
                        try:
                            max_war = await get_group_max_warnings(chat_id)
                            cmd = text[13:]
                            if cmd in ["ban", "mute"]:
                                warning_result = await set_group_warning_settings(
                                    chat_id, max_war, cmd
                                )
                                if warning_result.get("status") == "updated":
                                    maxw = warning_result.get("penalty_type")
                                    warning_text = (
                                        f"⚠️ مجازات اخطار به {maxw} تغییر کرد ✅\n"
                                    )
                                    await reply(
                                        message,
                                        await MPro(warning_text, chat_id),
                                        is_deleted_timer,
                                        delet_timer,
                                    )
                            else:
                                await reply(
                                    message,
                                    await MPro(
                                        "مجازات فقط ban  و mute مورد قبول میباشد",
                                        chat_id,
                                    ),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                        except Exception as e:
                            await reply(
                                message,
                                f"❌ خطا در دریافت اطلاعات گروه",
                                is_deleted_timer,
                                delet_timer,
                            )
                elif text.startswith("تنظیم علامت"):
                    emoji = text[12:]
                    await set_group_sticker_emoji(chat_id, emoji)
                    await reply(
                        message,
                        await MPro(f"علامت با موفقیت {emoji} ثبت شد"),
                        is_deleted_timer,
                        delet_timer,
                    )
                elif text == "علامت":
                    a = await get_group_sticker_emoji(chat_id)
                    await reply(
                        message,
                        await MPro(f"علامت گروه {a} میباشد."),
                        is_deleted_timer,
                        delet_timer,
                    )
                elif text == "گزارشات" or (
                    bot_name in text and "کزارشات" in text and rol in ["owner", "vip"]
                ):
                    parts = message.text.split()
                    period_days = 30
                    if len(parts) > 1:
                        try:
                            period_days = int(parts[1])
                        except:
                            pass
                    processing_msg = await reply(
                        message,
                        "🔄 در حال تولید گزارش...",
                        is_deleted_timer,
                        delet_timer,
                    )
                    report = await ReportGenerator.generate_group_report(
                        chat_id, period_days
                    )
                    formatted_report = await MPro(
                        f"📊 **گزارش گروه**\n{report}", chat_id
                    )
                    await bot.edit_message_text(
                        chat_id=message.chat_id,
                        message_id=processing_msg.message_id,
                        text=formatted_report,
                    )
                elif text.startswith("تگ"):
                    parts = text.split()
                    if len(parts) < 2:
                        menu = """
    🎯 **دستورات تگ کاربران**

    📌 **تگ با تعداد:**
    • `تگ 5`
    • `تگ 10`
    • `تگ 20`

    👥 **بر اساس نقش:**
    • `تگ همه`
    • `تگ ادمین`
    • `تگ ویژه`
    • `تگ مالک`
    • `تگ عضو`

    🎭 **فعال‌ترین‌ها:**
    • `تگ فعال`
    • `تگ فعال 5`

    ⚠️ **غیرفعال‌ها:**
    • `تگ ساکت`
    • `تگ غیرفعال`
                """
                        await reply(
                            message,
                            await MPro(menu, chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
                        return
                    command = parts[1]
                    try:
                        members = await list_members(chat_id)
                        if not members:
                            await reply(
                                message,
                                await MPro("❌ کاربری ثبت نشده است.", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                            return
                        if command.isdigit():
                            count = min(max(1, int(command)), 600)
                            selected = random.sample(members, min(count, len(members)))
                            links = [f"[کاربر]({m['user_id']})" for m in selected]
                            await send_in_chunks(
                                links,
                                f"🎲 تگ {count} کاربر تصادفی",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        elif command == "فعال":
                            count = 40
                            if len(parts) > 2 and parts[2].isdigit():
                                count = min(max(1, int(parts[2])), 600)
                            sorted_members = sorted(
                                members, key=lambda x: x["messages"], reverse=True
                            )[:count]
                            links = [
                                f"[کاربر({m['messages']}📨)]({m['user_id']})"
                                for m in sorted_members
                            ]
                            await send_in_chunks(
                                links,
                                f"🏆 تگ {count} کاربر فعال",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        elif command == "ساکت":
                            silent = [m for m in members if m["messages"] == 0]
                            if not silent:
                                await reply(
                                    message,
                                    await MPro("✅ کاربر ساکتی وجود ندارد.", chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                                return
                            links = [f"[ساکت]({m['user_id']})" for m in silent]
                            await send_in_chunks(
                                links,
                                f"🔇 کاربران ساکت ({len(silent)})",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        elif command == "غیرفعال":
                            inactive = [m for m in members if m["messages"] < 5]
                            if not inactive:
                                await reply(
                                    message,
                                    await MPro("✅ همه فعال‌اند.", chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                                return
                            links = [
                                f"[غیرفعال({m['messages']}📨)]({m['user_id']})"
                                for m in inactive
                            ]
                            await send_in_chunks(
                                links,
                                f"😴 کاربران غیرفعال ({len(inactive)})",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        elif command == "همه":
                            links = [f"[کاربر]({m['user_id']})" for m in members]
                            await send_in_chunks(
                                links,
                                "👥 تگ همه کاربران",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        elif command == "ادمین":
                            admins = [m for m in members if m["role"] == "admin"]
                            links = [f"[ادمین]({m['user_id']})" for m in admins]
                            await send_in_chunks(
                                links, "⚡ تگ ادمین‌ها", message, chunk_size=20, bot=bot
                            )
                        elif command == "ویژه":
                            vips = [m for m in members if m["role"] == "vip"]
                            links = [f"[ویژه]({m['user_id']})" for m in vips]
                            await send_in_chunks(
                                links,
                                "⭐ تگ کاربران ویژه",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        elif command == "مالک":
                            owners = [m for m in members if m["role"] == "owner"]
                            links = [f"[مالک]({m['user_id']})" for m in owners]
                            await send_in_chunks(
                                links, "👑 تگ مالک", message, chunk_size=1, bot=bot
                            )
                        elif command == "عضو":
                            regular = [m for m in members if m["role"] == "member"]
                            links = [f"[عضو]({m['user_id']})" for m in regular]
                            await send_in_chunks(
                                links,
                                "👤 تگ اعضای معمولی",
                                message,
                                chunk_size=20,
                                bot=bot,
                            )
                        else:
                            await reply(
                                message,
                                await MPro("❌ دستور نامعتبر.", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                    except Exception as e:
                        await reply(
                            message,
                            await MPro(f"❌ خطا: {str(e)[:100]}", chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
        except Exception as e:
            print(f"Error in: {e}")
async def handle_member_management_features(
    chat_id,
    message,
    text,
    bot,
    send_id,
    rol,
    suport,
    bot_name,
    delet_timer,
    is_deleted_timer,
):
    try:
        if await group_exists(chat_id=chat_id):
            if not message.reply_to_message_id and text == "تنظیم مالک":
                if await has_ownerr(user_id=send_id, chat_id=chat_id):
                    await reply(
                        message,
                        await MPro("مالک از قبل وجود داشت", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                else:
                    try:
                        success = await add_member(
                            chat_id=chat_id, user_id=send_id, role="owner"
                        )
                        if success:
                            await reply(
                                message,
                                await MPro(t(key="admin_m"), chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                        else:
                            await reply(
                                message,
                                await MPro("❌ امکان تنظیم مالک وجود ندارد", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                    except Exception as e:
                        print(f"Error in owner setting: {e}")
                        await reply(
                            message,
                            await MPro("❌ خطا در تنظیم مالک", chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
            elif message.reply_to_message_id and text in [
                "تنظیم ویژه",
                "ویژه",
                "ادمین",
                "تنظیم ادمین",
                "برکناری",
                "انبن",
                "رفع محدودیت",
                "بن",
            ]:
                id = message.reply_to_message_id
                get_mess = await bot.get_message(chat_id=chat_id, message_id=id)
                if get_mess:
                    target_user_id = get_mess["sender_id"]
                    if (
                        (text == "تنظیم ویژه" or text == "ویژه")
                        and rol == "owner"
                        or (
                            bot_name in text
                            and "ویژه" in text
                            and rol in ["owner", "vip"]
                        )
                    ):
                        try:
                            success = await add_member(
                                chat_id=chat_id, user_id=target_user_id, role="vip"
                            )
                            if success:
                                await reply(
                                    message,
                                    await MPro(t(key="admin_v"), chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                            else:
                                await edit_member(
                                    chat_id=chat_id,
                                    user_id=target_user_id,
                                    new_role="vip",
                                )
                                await reply(
                                    message,
                                    await MPro(t(key="admin_v"), chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                        except Exception:
                            await reply(
                                message,
                                await MPro("❌ خطا در افزودن کاربر ویژه", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                    elif (
                        (text == "تنظیم ادمین" or text == "ادمین")
                        and rol
                        in [
                            "owner",
                            "vip",
                        ]
                        or (
                            bot_name in text
                            and "ادمین" in text
                            and rol in ["owner", "vip"]
                        )
                    ):
                        try:
                            success = await add_member(
                                chat_id=chat_id,
                                user_id=target_user_id,
                                role="admin",
                            )
                            if success:
                                await reply(
                                    message,
                                    await MPro(t(key="admin_a"), chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                            else:
                                await edit_member(
                                    chat_id=chat_id,
                                    user_id=target_user_id,
                                    new_role="admin",
                                )
                                await reply(
                                    message,
                                    await MPro(t(key="admin_a"), chat_id),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                        except Exception as e:
                            await reply(
                                message,
                                await MPro("❌ خطا در تنظیم ادمین", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                    elif text == "برکناری" or (
                        bot_name in text
                        and "برکنار" in text
                        and rol in ["owner", "vip"]
                    ):
                        try:
                            target_role = await get_user_role(
                                chat_id=chat_id, user_id=target_user_id
                            )
                            if target_role is None:
                                await reply(
                                    message,
                                    await MPro(
                                        "❌ این کاربر در گروه ثبت نشده است", chat_id
                                    ),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                                return
                            if rol == "owner":
                                can_remove = True
                            elif rol == "vip":
                                can_remove = target_role == "admin"
                            else:
                                can_remove = False
                            if not can_remove:
                                await reply(
                                    message,
                                    await MPro(
                                        "❌ شما اجازه برکناری این کاربر را ندارید",
                                        chat_id,
                                    ),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                                return
                            if target_role == "vip":
                                await edit_member(chat_id, target_user_id, "member")
                            elif target_role == "admin":
                                await edit_member(chat_id, target_user_id, "member")
                            else:
                                await reply(
                                    message,
                                    await MPro(
                                        "ℹ این کاربر هم‌اکنون عضو معمولی است", chat_id
                                    ),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                                return
                            await reply(
                                message,
                                await MPro("✅ کاربر با موفقیت برکنار شد", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                        except Exception as e:
                            print(f"Error in admin removal: {e}")
                            await reply(
                                message,
                                await MPro("❌ خطا در برکناری", chat_id),
                                is_deleted_timer,
                                delet_timer,
                            )
                    elif (
                        text == "انبن"
                        or text == "رفع محدودیت"
                        and rol in ["owner", "vip"]
                        or (
                            bot_name in text
                            and "انبن" in text
                            and rol in ["owner", "vip"]
                        )
                    ):
                        if message.reply_to_message_id:
                            id = message.reply_to_message_id
                            get_mess = await bot.get_message(
                                chat_id=chat_id, message_id=id
                            )
                            if get_mess:
                                target_user_id = get_mess["sender_id"]
                                chat_id1 = (
                                    str(message.chat_id)
                                    if isinstance(message.chat_id, str)
                                    else message.chat_id
                                )
                                user_id1 = (
                                    str(target_user_id)
                                    if isinstance(target_user_id, str)
                                    else target_user_id
                                )
                                await bot.unban_chat_member(
                                    chat_id=chat_id1, user_id=user_id1
                                )
                                await reply(
                                    message,
                                    await MPro("با موفقیت انبن شد"),
                                    is_deleted_timer,
                                    delet_timer,
                                )
                    elif (text == "بن" and rol in ["owner", "vip"]) or (
                        bot_name in text and "بن" in text and rol in ["owner", "vip"]
                    ):
                        if message.reply_to_message_id:
                            id = message.reply_to_message_id
                            get_mess = await bot.get_message(
                                chat_id=chat_id, message_id=id
                            )
                            if get_mess:
                                target_user_id = get_mess["sender_id"]
                                if not target_user_id == message.sender_id:
                                    roll = await get_user_role(
                                        chat_id=chat_id, user_id=target_user_id
                                    )
                                    if roll == "owner":
                                        await reply(
                                            message,
                                            await MPro("ایشون مالک بنده است"),
                                            is_deleted_timer,
                                            delet_timer,
                                        )
                                        return
                                    if roll == "vip":
                                        await reply(
                                            message,
                                            await MPro("ایشون ادمین ویژه است"),
                                            is_deleted_timer,
                                            delet_timer,
                                        )
                                        return
                                    if roll == "admin":
                                        await reply(
                                            message,
                                            await MPro("ایشون ادمین است"),
                                            is_deleted_timer,
                                            delet_timer,
                                        )
                                        return
                                    await bot.ban_member_chat(chat_id, target_user_id)
                                    await reply(
                                        message,
                                        await MPro("با موفقیت بن شد"),
                                        is_deleted_timer,
                                        delet_timer,
                                    )
                                else:
                                    await reply(
                                        message,
                                        await MPro("خودتو نمیتونی بن کنی"),
                                        is_deleted_timer,
                                        delet_timer,
                                    )
            elif rol == "owner" or send_id == suport:
                if text in ["ریست گپ", "ریست گروه"]:
                    await remove_group(chat_id=chat_id)
                    await reply(
                        message,
                        await MPro(t(key="rim"), chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                if text == "غیرفعال":
                    if await is_group_active(chat_id=chat_id):
                        await deactivate_group(chat_id=chat_id)
                        await reply(
                            message,
                            await MPro("دراگون غیرفعال شد", chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
                if text == "ریست لیست ویژه":
                    await reset_vips(chat_id=chat_id)
                    await reply(
                        message,
                        await MPro("لیست ویژه خالی شد", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                if text == "ریست لیست ادمین":
                    await reset_admins(chat_id=chat_id)
                    await reply(
                        message,
                        await MPro("لیست ادمین خالی شد", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
    except Exception as e:
        print(f"Error in member management features: {e}")
LOCK_RULES = (
    (("file",), are_documents_locked, "❌ ارسال فایل در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("photo", "video", "voice", "audio", "file",), is_media_locked, "❌ ارسال رسانه در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("poll",), are_polls_locked, "❌ ارسال نظرسنجی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("location",), is_location_locked, "❌ ارسال موقعیت مکانی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("sticker",), is_sticker_locked, "❌ ارسال استیکر در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("photo",), are_photos_locked, "❌ ارسال عکس در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("video",), are_videos_locked, "❌ ارسال فیلم در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("voice",), is_voice_locked, "❌ ارسال ویس در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("forward",), is_forward_locked, "❌ فوروارد در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Spoiler",), is_spoiler_locked, "❌ ارسال اسپویلر در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Quote",), is_Quote_locked, "❌ ارسال نقل قول در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Bold",), is_Bold_locked, "❌ ارسال برجسته در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Italic",), is_Italic_locked, "❌ ارسال کج در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Mono",), is_Mono_locked, "❌ ارسال تکی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Strike",), is_Strike_locked, "❌ ارسال خط خورده در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Underline",), is_Underline_locked, "❌ ارسال زیر خط در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
    (("Link",), is_mention_locked, "❌ ارسال پیام لینک دار در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!"),
)
async def handle_lock_check_features(
    chat_id,
    message,
    text,
    bot,
    admin,
    suport,
    send,
    bot_name,
    delet_timer,
    is_deleted_timer,
):
    try:
        if admin or message.sender_id == suport:
            return
        if await is_member_exempt(chat_id=chat_id, sender_id=message.sender_id):
            return
        if await get_sokot(chat_id=chat_id, sender_id=send):
            try:
                await bot.delete_message(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                )
            except Exception:
                pass
            return
        if text:
            link_indicators = [
                "http://",
                "https://",
                "t.me/",
                "www.",
                ".com",
                ".ir",
                ".org",
                ".net",
            ]
            if any(indicator in text.lower() for indicator in link_indicators):
                if await are_links_locked(chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال لینک در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            if await detect_long_text(message_text=text):
                if await are_long_text_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال متن بلند در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            if await detect_forbidden_message(text):
                if await are_filter_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال کد هنگی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            if contains_english(text):
                if await is_english_locked(chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال متن انگلیسی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            p = r"^@[a-zA-Z]{2,30}$"
            if bool(re.match(p, text)):
                if await are_ids_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال ایدی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            if contains_pars(text):
                if await is_persian_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال متن فارسی در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            if "#" in text:
                if await is_hashtag_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال متن هشتک دار در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            badd = await check_text_advanced(text)
            bad = badd["data"]["keywords_found"] if badd.get("success") else None
            if bad:
                if await are_bad_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال پیام نامناسب در این گروه ممنوع است!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    return
            if await detect_spam(chat_id=chat_id, sender_id=message.sender_id):
                if await are_spam_locked(chat_id=chat_id):
                    await _delete_and_reply(
                        bot,
                        message,
                        chat_id,
                        "❌ ارسال اسپم در این گروه ممنوع است شما سکوت شدید!\n\nاین پیام بعد از 30 ثانیه حذف میشود!",
                    )
                    s_ = mes["sender_id"]
                    rolee = await get_user_role(chat_id=chat_id, user_id=s_)
                    if rolee in ["owner", "vip", "admin"] or s_ == suport:
                        pass
                    else:
                        await set_sokot(chat_id, message.message_id, True)
                        return await reply(
                            message,
                            await MPro(
                                f"🔇 کاربر `{message.message_id}` به حالت سکوت رفت.",
                                chat_id,
                            ),
                            is_deleted_timer,
                            delet_timer,
                        )
                    return
        mes = None
        message_type_val = None
        mes = await bot.get_message(
            chat_id=chat_id,
            message_id=message.message_id or message.reply_to_message_id,
        )
        if mes:
            message_type_val = message_type(mes)
            for _types, _locked, _msg in LOCK_RULES:
                if message_type_val in _types and await _locked(chat_id=chat_id):
                    await _delete_and_reply(bot, message, chat_id, _msg)
                    return
    except Exception as e:
        pass
async def _delete_and_reply(bot, message, chat_id, text):
    try:
        await bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id,
        )
        await message.reply(
            await MPro(f"[{text}]({message.sender_id})", chat_id),
            delete_after=30,
        )
    except Exception as e:
        print(f"Error in _delete_and_reply: {e}")
async def handle_general_features(
    bot,
    chat_id=None,
    message=None,
    text=None,
    send_id=None,
    rol=None,
    data=None,
    bot_name=None,
    delet_timer=8,
    is_deleted_timer=False,
):
    try:
        if text in ["دستورات", "الأوامر", "راهنما"] or text == "commands":
            user_lang = await get_user_lang(send_id)
            await reply(
                message,
                await MPro(t(user_lang, key="commands_message"), chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if text == "ورژن":
            await reply(message, await MPro(V, chat_id), is_deleted_timer, delet_timer)
        if (text == "تعداد کل پیام" or text == "تعداد پیام گروه") and rol in [
            "owner",
            "vip",
            "admin",
        ]:
            await reply(
                message,
                await MPro(f"تعداد کل پیام های گروه: {data['stats']['messages']}"),
                is_deleted_timer,
                delet_timer,
            )
        if (
            text == "تعداد پیام"
            and rol in ["owner", "vip", "admin"]
            and message.reply_to_message_id
        ):
            l = await get_user_message(chat_id)
            rep_msg = await bot.get_message(
                chat_id=chat_id, message_id=message.reply_to_message_id
            )
            if not rep_msg:
                await reply(
                    message,
                    await MPro("❌ پیام ریپلای شده یافت نشد", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            target_user_id = rep_msg["sender_id"]
            for i in l["top_users"]:
                if target_user_id == i.get("user_id"):
                    await reply(
                        message,
                        await MPro(f"تعداد پیام کاربر: {i.get('messages')}", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                    break
        if text in [
            "وضعیت گروه",
            "وضعیت گپ",
            "امار گپ",
            "آمار گپ",
            "امار گروه",
            "آمار گروه",
        ] and rol in [
            "owner",
            "vip",
            "admin",
        ]:
            if data:
                top_users_text = ""
                if data.get("top_users"):
                    for i, user in enumerate(data["top_users"], 1):
                        role_emoji = {
                            "owner": "👑",
                            "admin": "⚡",
                            "vip": "⭐",
                            "member": "👤",
                        }.get(user.get("role", "member"), "👤")
                        user_id_short = (
                            user["user_id"][:60] + "..."
                            if len(user["user_id"]) > 600
                            else user["user_id"]
                        )
                        top_users_text += f"{i}. {role_emoji} [{user_id_short}]({user_id_short}) - {user['messages']} پیام\n"
                        remaining_days = await ops(chat_id)
                else:
                    top_users_text = "هیچ فعالیتی ثبت نشده"
                textt = "\n".join(
                    [
                        "📊 **وضعیت گروه**",
                        "",
                        f"🏷 **نام گروه:** {data['group_name']}",
                        f"🔌 **وضعیت ربات:** {'فعال ✅' if data['active'] else 'غیرفعال ❌'}",
                        f"⚡️ شارژ گروه: {remaining_days}",
                        f"👥 **کل اعضا:** {data.get('total_members', 0)} نفر",
                        "",
                        "🎭 **توزیع نقش‌ها:**",
                        f"• 👑 مالکین: {data['roles']['owner']} نفر",
                        f"• ⚡ ادمین‌ها: {data['roles']['admin']} نفر",
                        f"• ⭐ ویژه‌ها (VIP): {data['roles']['vip']} نفر",
                        f"• 👤 اعضای معمولی: {data['roles']['member']} نفر",
                        "",
                        "📈 **آمار کامل فعالیت گروه:**",
                        f"• 💬 **پیام‌ها:** {data['stats']['messages']}",
                        f"• 🔗 **لینک‌ها:** {data['stats']['links']}",
                        f"• 🖼️ **عکس‌ها:** {data['stats']['photos']}",
                        f"• 🎬 **ویدیوها:** {data['stats']['videos']}",
                        f"• 📄 **فایل‌ها:** {data['stats']['documents']}",
                        f"• 📊 **نظرسنجی‌ها:** {data['stats']['polls']}",
                        f"• 📍 **موقعیت‌ها:** {data['stats']['location']}",
                        f"• 🎤 **ویس‌ها:** {data['stats']['voice']}",
                        f"• 🎴 **استیکرها:** {data['stats']['sticker']}",
                        f"• #️⃣ **هشتگ‌ها:** {data['stats']['hashtag']}",
                        f"• 🇺🇸 **متن انگلیسی:** {data['stats']['english']}",
                        f"• 🇮🇷 **متن فارسی:** {data['stats']['persian']}",
                        "",
                        "🏆 **10 کاربر فعال برتر:**",
                        top_users_text,
                    ]
                )
                await reply(
                    message, await MPro(textt, chat_id), is_deleted_timer, delet_timer
                )
        if text in ["مقام", "مقامم", "مقامش"]:
            role_map = {
                "owner": "👑 مالک",
                "vip": "⚡ ادمین ویژه",
                "admin": "⚜️ ادمین ساده",
                "member": "👤 کاربر",
            }
            if text == "مقامم":
                magam = await get_user_role(chat_id=chat_id, user_id=send_id)
                magamm = role_map.get(magam, "❓ ناشناس")
                text = f"[مقام شما: {magamm}]({send_id})"
                await reply(
                    message, await MPro(text, chat_id), is_deleted_timer, delet_timer
                )
            elif text in ["مقام", "مقامش"]:
                if message.reply_to_message_id:
                    get_mess = await bot.get_message(
                        chat_id=chat_id,
                        message_id=message.reply_to_message_id,
                    )
                    magam = await get_user_role(
                        chat_id=chat_id, user_id=get_mess["sender_id"]
                    )
                    magamm = role_map.get(magam, "❓ ناشناس")
                    await reply(
                        message,
                        await MPro(f"مقام کاربر: {magamm}", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                else:
                    magam = await get_user_role(chat_id=chat_id, user_id=send_id)
                    magamm = role_map.get(magam, "❓ ناشناس")
                    await reply(
                        message,
                        await MPro(f"مقام شما: {magamm}", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
    except Exception as e:
        pass
async def handle_delet_message(
    bot,
    text=None,
    chat_id=None,
    message=None,
    rol=None,
    admin=None,
    suport=None,
    bot_name=None,
    delet_timer=8,
    is_deleted_timer=False,
):
    if message.sender_id == suport:
        if text.startswith("شارژ"):
            cmd = text[5:]
            await add_group_charge(chat_id, int(cmd))
            await reply(
                message,
                await MPro(f"برای گروه {cmd} روز شارژ اضافه شد", chat_id),
                is_deleted_timer,
                delet_timer,
            )
    if rol == "owner" or message.sender_id == suport:
        if text == "شارژ گروه":
            a = await get_group_charge_status(chat_id)
            chat_id = a.get("chat_id")
            is_active = a.get("is_active")
            if not is_active:
                await reply(
                    message,
                    f"برای گروه شما شارژی تایین نشده جهت خرید به ایدی زیر مراجعه کنید\n\n{SUPPORT_USERNAME}",
                    is_deleted_timer,
                    delet_timer,
                )
            remaining_days = await ops(chat_id)
            if is_active:
                is_activ = "فعال"
            messages = f"""{remaining_days} روز از شارژ شما باقیمانده است"""
            if is_active:
                await reply(
                    message,
                    await MPro(str(messages), chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            else:
                await reply(
                    message,
                    f"برای گروه شما شارژی تایین نشده جهت خرید به ایدی زیر مراجعه کنید\n\n{SUPPORT_USERNAME}",
                    is_deleted_timer,
                    delet_timer,
                )
        if text.startswith("حذف"):
            parts = text.split()
            if len(parts) > 1:
                try:
                    number = int(parts[1])
                    msgs = await bot.get_messages_by_id(
                        chat_id=chat_id, message_id=message.message_id, limit=number
                    )
                    for m in msgs:
                        await bot.delete_message(
                            chat_id=chat_id, message_id=m["message_id"]
                        )
                    await reply(
                        message,
                        await MPro(f"تعداد {number} پیام حذف شد", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                except:
                    pass
        if text == "انتقال مالکیت":
            try:
                rep_msg = await bot.get_message(
                    chat_id=chat_id, message_id=message.reply_to_message_id
                )
                if not rep_msg:
                    await reply(
                        message,
                        await MPro("❌ پیام ریپلای شده یافت نشد", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                    return
                target_user_id = rep_msg["sender_id"]
                if target_user_id == message.sender_id:
                    await reply(
                        message,
                        await MPro(
                            "❌ نمی‌توانید مالکیت را به خودتان انتقال دهید",
                            chat_id,
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
                    return
                target_role = await get_user_role(
                    chat_id=chat_id, user_id=target_user_id
                )
                if not target_role:
                    await add_member(
                        chat_id=chat_id, user_id=target_user_id, role="owner"
                    )
                else:
                    await edit_member(
                        chat_id=chat_id,
                        user_id=target_user_id,
                        new_role="owner",
                    )
                await edit_member(
                    chat_id=chat_id, user_id=message.sender_id, new_role="vip"
                )
                success_text = await MPro(t("fa", key="new_ow"), chat_id)
                if success_text.strip():
                    await reply(message, success_text, is_deleted_timer, delet_timer)
                else:
                    await reply(
                        message,
                        await MPro("✅ مالکیت با موفقیت انتقال یافت", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                await bot.send_message(
                    chat_id=LOG_CHAT_GUID,
                    text=f"✅ مالکیت انتقال یافت: \n{message.sender_id} ---> {target_user_id}\n در گروه: \n{chat_id}",
                )
            except Exception as e:
                error_msg = f"❌ خطا در انتقال مالکیت: {str(e)[:100]}"
                await reply(
                    message,
                    await MPro(error_msg, chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
                print(f"Error in transfer ownership: {e}")
async def handle_add_op(
    bot,
    message=None,
    text: str = None,
    chat_id: str = None,
    send_id: str = None,
    rol: str = None,
    admin: bool = None,
    suport: str = None,
    bot_name=None,
    delet_timer=8,
    is_deleted_timer=False,
):
    if not text:
        return
    multi_cmds = [
        "تنظیم اصل",
        "تنظیم لقب",
        "حذف معاف",
        "حذف اصل",
        "حذف لقب",
        "سکوت",
        "حذف سکوت",
    ]
    cmd = None
    rest = None
    for mc in multi_cmds:
        if text.startswith(mc):
            cmd = mc
            rest = text[len(mc) :].strip()
            break
    if not cmd:
        parts = text.split(maxsplit=1)
        cmd = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
    target_id = None
    value = None
    try:
        if message.reply_to_message_id:
            rep = await bot.get_message(
                chat_id=chat_id, message_id=message.reply_to_message_id
            )
            target_id = rep.get("sender_id")
            if cmd in ["تنظیم اصل", "تنظیم لقب"] and rest:
                value = rest
        else:
            parts = rest.split(maxsplit=1)
            if cmd in ["تنظیم اصل", "تنظیم لقب"]:
                if len(parts) < 2:
                    return await reply(
                        message,
                        await MPro(
                            "❌ فرمت اشتباه. مثال:\nتنظیم لقب 12345 علی", chat_id
                        ),
                        is_deleted_timer,
                        delet_timer,
                    )
                target_id = parts[0]
                value = parts[1]
            elif cmd in ["حذف اصل", "حذف لقب", "معاف", "حذف معاف", "سکوت", "حذف سکوت"]:
                if len(parts) < 1:
                    return await reply(
                        message,
                        await MPro("❌ لطفاً آیدی کاربر را وارد کنید.", chat_id),
                        is_deleted_timer,
                        delet_timer,
                    )
                target_id = parts[0]
        if cmd in ["حذف اصل", "حذف لقب"]:
            value = ""
    except Exception as e:
        pass
    try:
        if not (admin or send_id == suport):
            return
        if cmd == "تنظیم اصل":
            await set_original(chat_id, target_id, value)
            return await reply(
                message,
                await MPro(f"✔️ مقدار اصل برای [کاربر]({target_id}) تنظیم شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if cmd == "تنظیم لقب":
            await set_nickname(chat_id, target_id, value)
            return await reply(
                message,
                await MPro(f"✔️ لقب [کاربر]({target_id}) تنظیم شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if cmd == "حذف اصل":
            await set_original(chat_id, target_id, "")
            return await reply(
                message,
                await MPro(f"🗑 مقدار اصل [کاربر]({target_id}) حذف شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if cmd == "حذف لقب":
            await set_nickname(chat_id, target_id, "")
            return await message.reply(
                await MPro(f"🗑 لقب [کاربر]({target_id}) حذف شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if cmd == "معاف":
            await exempt_member(chat_id, target_id, True)
            return await reply(
                message,
                await MPro(f"🎖 [کاربر]({target_id}) معاف شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if cmd == "حذف معاف":
            await exempt_member(chat_id, target_id, False)
            return await reply(
                message,
                await MPro(f"🚫 معافیت [کاربر]({target_id}) حذف شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
        if cmd == "سکوت":
            s_ = rep["sender_id"]
            rolee = await get_user_role(chat_id=chat_id, user_id=s_)
            if rolee in ["owner", "vip", "admin"] or s_ == suport:
                await reply(
                    message,
                    await MPro("کاربر ادمین است", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
            else:
                await set_sokot(chat_id, target_id, True)
                return await reply(
                    message,
                    await MPro(f"🔇 [کاربر]({target_id}) به حالت سکوت رفت.", chat_id),
                    is_deleted_timer,
                    delet_timer,
                )
        if cmd == "حذف سکوت":
            await set_sokot(chat_id, target_id, False)
            return await reply(
                message,
                await MPro(f"🔊 سکوت [کاربر]({target_id}) برداشته شد.", chat_id),
                is_deleted_timer,
                delet_timer,
            )
    except Exception as e:
        return
async def check_expired_chargess():
    while True:
        await ops1()
        await asyncio.sleep(1000)
async def run_all_features_parallel(
    chat_id,
    message,
    text,
    bot,
    send_id,
    sender_id,
    rol,
    admin,
    data,
    suport,
    bot_name,
    delet_timer,
    is_deleted_timer,
):
    if not await is_group_active(chat_id=chat_id):
        return
    try:
        semaphore = asyncio.Semaphore(20)
        async def run_task(coro):
            async with semaphore:
                try:
                    await coro
                except Exception as e:
                    pass
        tasks = [
            run_task(
                handle_entertainment_features(
                    bot,
                    chat_id,
                    message,
                    text,
                    rol,
                    suport,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_locked_speak(
                    chat_id, message, text, bot_name, delet_timer, is_deleted_timer
                )
            ),
            run_task(
                handle_calculator_features(
                    chat_id, message, text, bot_name, delet_timer, is_deleted_timer
                )
            ),
            run_task(
                handle_user_info_features(
                    chat_id,
                    message,
                    text,
                    bot,
                    send_id,
                    sender_id,
                    admin,
                    suport,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_admin_management_features(
                    chat_id,
                    message,
                    text,
                    bot,
                    send_id,
                    rol,
                    suport,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_member_management_features(
                    chat_id,
                    message,
                    text,
                    bot,
                    send_id,
                    rol,
                    suport,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_general_features(
                    bot,
                    chat_id,
                    message,
                    text,
                    send_id,
                    rol,
                    data,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_delet_message(
                    bot,
                    text,
                    chat_id,
                    message,
                    rol,
                    admin,
                    suport,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_add_op(
                    bot,
                    message,
                    text,
                    chat_id,
                    send_id,
                    rol,
                    admin,
                    suport,
                    bot_name,
                    delet_timer,
                    is_deleted_timer,
                )
            ),
            run_task(
                handle_lock_check_features(
                    chat_id,
                    message,
                    text,
                    bot,
                    admin,
                    suport,
                    send=send_id,
                    bot_name=bot_name,
                    delet_timer=delet_timer,
                    is_deleted_timer=is_deleted_timer,
                )
            ),
            run_task(check_expired_chargess()),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logging.exception("⚠️ خطا در اجرای یکی از قابلیت‌ها", exc_info=result)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        pass
async def main():
    await initialize_database()
    bot = Robot(
        token=BOT_TOKEN,
        session_name="dragon_bot",
        web_hook=WEBHOOK_URL,
        safeSendMode=True,
        api_endpoint="botapi",
    )
    bot.start_save_message()
    @bot.on_message_private(filters=filters.is_text)
    async def handler_pv(bot: Robot, message: Message):
        chat_id = message.chat_id
        callback = message.aux_data.button_id if message.aux_data else None
        text = message.text.strip() if message.text else ""
        exists = await user_exists(chat_id)
        name = await bot.get_name(chat_id=chat_id)
        lang = await get_user_lang(chat_id=chat_id)
        users_count = await count_users()
        groups_count = await count_groups()
        chat_owner_ids = await get_owner_ids()
        state = user_states[chat_id].get("state")
        msg = message
        chat_keypad_main = build_chat_keypad(lang)
        chat_keypad_back = build_back_keypad(lang)
        broadcast_keypad = build_send_type_keypad(lang)
        inline_keypad = build_inline_keypad(lang, users_count, groups_count)
        admin = await owner_exists(chat_id)
        user_id = message.sender_id
        if await is_blocked(chat_id):
            m = t(lang, "is_blocked")
            await message.reply(m)
            return
        if admin:
            if msg.text and msg.text.startswith("/blocke"):
                if not chat_id in await list_owners():
                    await handle_bloke_command(msg, bot, lang=lang)
                    return
            elif msg.text and msg.text.startswith("/unblocke"):
                await handle_unbloke_command(msg, bot, lang=lang)
                return
            elif msg.text == "/reset_blocked":
                await handle_reset_blocked(msg, lang=lang)
            elif msg.text == "/list_blocked":
                await handle_list_blocked(msg, lang=lang)
            elif msg.text == "/list":
                await send_groups_list(message, bot)
            elif text == "/backup":
                success = await create_backup()
                if success:
                    await message.reply("✅ بکاپ با موفقیت ایجاد شد")
                else:
                    await message.reply("❌ خطا در ایجاد بکاپ")
            elif text == "/backup_list":
                backup_list = await list_backups()
                await message.reply(backup_list)
            elif text.startswith("/restore "):
                backup_name = text.replace("/restore ", "").strip()
                result = await restore_backup(backup_name)
                await message.reply(result)
        if not await has_owner():
            await add_owner(name=name, guid=chat_id)
            await message.reply(t(lang, "owner"))
            return
        if callback:
            if callback == "back":
                await message.reply(
                    t(lang, "start_text"),
                    chat_keypad=chat_keypad_main,
                    inline_keypad=inline_keypad,
                )
                return
            if callback == "btn_join":
                try:
                    await set_user_joined(chat_id)
                    await message.reply(
                        t(lang, "start_text"),
                        chat_keypad=chat_keypad_main,
                        inline_keypad=inline_keypad,
                    )
                    return
                except:
                    pass
            if callback == "add":
                await message.reply(t(lang, "add_group"), chat_keypad=chat_keypad_back)
                return
            if callback == "help":
                await message.reply(
                    t(lang, "commands_message"), chat_keypad=chat_keypad_back
                )
                return
            if callback == "report":
                user_states[chat_id]["state"] = "report"
                await message.reply(
                    t(lang, "report_prompt"), chat_keypad=chat_keypad_back
                )
                return
            if callback == "chanel":
                await message.reply(
                    t(lang, "channels_info"), chat_keypad=chat_keypad_back
                )
                return
            if callback == "send_private":
                if admin:
                    user_states[chat_id]["state"] = "broadcast_all"
                    await message.reply(
                        t(lang, "prompt_send_all"), chat_keypad=chat_keypad_back
                    )
                return
            if callback == "send_group":
                if admin:
                    user_states[chat_id]["state"] = "broadcast_groups"
                    await message.reply(
                        "📝 لطفاً پیام خود را ارسال کنید تا برای همه گروه‌ها فرستاده شود:",
                        chat_keypad=chat_keypad_back,
                    )
                return
            if callback == "groups":
                user_id = message.sender_id
                if text:
                    await show_control_panel(bot, message, user_id)
            if callback:
                await handle_control_panel(bot, message, user_id, callback)
        if state == "report":
            cmd = text
            ticket_count = await get_tickets_count(chat_id) + 1
            await increase_tickets(chat_id)
            ticket_num = await add_ticket(chat_id, name, cmd)
            for owner_id in chat_owner_ids:
                await bot.send_message(
                    chat_id=owner_id,
                    text=t(
                        lang,
                        "report_notify",
                        name=name,
                        chat_id=chat_id,
                        ticket_num=ticket_num,
                        ticket_count=ticket_count,
                        cmd=cmd,
                    ),
                )
            await message.reply(
                t(lang, "report_success", num=ticket_num, cmd=cmd),
                chat_keypad=chat_keypad_main,
            )
            user_states[chat_id]["state"] = None
            return
        elif state == "broadcast_groups":
            if admin:
                groups = await get_all_groups()
                if not groups:
                    await msg.reply("⚠️ هنوز هیچ گروهی ثبت نشده است.")
                    user_states[chat_id]["state"] = None
                    return
                sent, failed = 0, 0
                broadcast_id = await save_broadcast_message(
                    message.sender_id, chat_id, text, "groups"
                )
                await msg.reply(f"📢 در حال ارسال پیام به {len(groups)} گروه...")
                for group_id in groups:
                    try:
                        await bot.send_message(chat_id=group_id, text=text)
                        sent += 1
                        await asyncio.sleep(0.00001)
                    except:
                        failed += 1
                await update_broadcast_stats(broadcast_id, sent, failed)
                report_text = f"📬 پیام ارسال شد!\n\n✅ موفق: {sent}\n❌ ناموفق: {failed}\n👥 کل گروه‌ها: {len(groups)}"
                for owner_id in chat_owner_ids:
                    try:
                        await bot.send_message(chat_id=owner_id, text=report_text)
                    except:
                        pass
                user_states[chat_id]["state"] = None
                await msg.reply(report_text, chat_keypad=chat_keypad_main)
            return
        elif state == "broadcast_all":
            if admin:
                pv = await list_users()
                if not pv:
                    await msg.reply("⚠️ هنوز هیچ کاربری ثبت نشده است.")
                    user_states[chat_id]["state"] = None
                    return
                sent, failed = 0, 0
                broadcast_id = await save_broadcast_message(
                    message.sender_id, chat_id, text, "private"
                )
                await msg.reply(f"📢 در حال ارسال پیام به {len(pv)} پیوی...")
                for pv_id in pv:
                    pv_id = pv_id.get("chat_id")
                    try:
                        await bot.send_message(chat_id=pv_id, text=text)
                        sent += 1
                        await asyncio.sleep(0.00001)
                    except:
                        failed += 1
                await update_broadcast_stats(broadcast_id, sent, failed)
                report_text = f"📬 پیام ارسال شد!\n\n✅ موفق: {sent}\n❌ ناموفق: {failed}\n👥 کل پیوی: {len(pv)}"
                for owner_id in chat_owner_ids:
                    try:
                        await bot.send_message(chat_id=owner_id, text=report_text)
                    except:
                        pass
                user_states[chat_id]["state"] = None
                await msg.reply(report_text, chat_keypad=chat_keypad_main)
            return
        if text == "/start":
            if not exists:
                await add_user(chat_id, name)
                return
            if not await has_joined(chat_id):
                join_button = (
                    ChatKeypadBuilder()
                    .row(
                        ChatKeypadBuilder().button(id="btn_join", text=t(lang, "join"))
                    )
                    .build()
                )
                await message.reply(t(lang, "join_text"), chat_keypad=join_button)
                return
            try:
                await set_user_joined(chat_id, True)
                await message.reply(
                    t(lang, "start_text"),
                    chat_keypad=chat_keypad_main,
                    inline_keypad=inline_keypad,
                )
            except Exception as e:
                print(f"Error checking channel membership: {e}")
                await message.reply(
                    "⚠️ خطا در بررسی عضویت. لطفاً دوباره امتحان کنید.",
                    chat_keypad=chat_keypad_main,
                )
        elif text.startswith("شارژ"):
            cmd = text.split()
            chat_id_ = cmd[1]
            b = await get_group_charge_status(chat_id_)
            if b.get("is_active"):
                await message.reply(f"شارژ گروه شما: {str(b)}")
            else:
                await message.reply(
                    f"برای گروه شما شارژی تایین نشده جهت خرید به ایدی زیر مراجعه کنید\n\n{SUPPORT_USERNAME}"
                )
        if await owner_exists(chat_id):
            if text.startswith("/for_tiket"):
                parts = text.split(" ", 3)
                if len(parts) < 4:
                    await message.reply(t(lang, "Error_send_tiket"))
                    return
                target_chat, tracking_number, support_text = map(str.strip, parts[1:4])
                tickets = await get_tickets_by_chat(target_chat)
                ticket_data = next(
                    (t for t in tickets if str(t["ticket_id"]) == tracking_number), None
                )
                if not ticket_data:
                    await message.reply(
                        t(lang, "ticket_not_found", tracking_number=tracking_number)
                    )
                    return
                original_text = ticket_data["text"]
                channels = await list_channels()
                message_to_user = t(
                    lang,
                    "tiket_message",
                    tracking_number=tracking_number,
                    chat_id_user=target_chat,
                    original_text=original_text,
                    support_text=support_text,
                    chanel=channels,
                )
                try:
                    await bot.send_message(chat_id=target_chat, text=message_to_user)
                    await message.reply(t(lang, "e_for", chat_id_user=target_chat))
                except Exception as e:
                    await message.reply(
                        t(lang, "ee_for", chat_id_user=target_chat, e=str(e))
                    )
            elif text.startswith("+"):
                cmd = text.split()
                chat_id_ = cmd[1]
                v = cmd[2]
                await add_group_charge(chat_id_, int(v))
                await message.reply("شارژ اضافه شد", chat_id)
                await bot.send_message(
                    chat_id=chat_id_,
                    text=await MPro(f"{v} روز به شارژ گروه اضافه شد", chat_id_),
                )
            elif text.startswith("-"):
                cmd = text.split()
                chat_id_ = cmd[1]
                v = cmd[2]
                await remove_group_charge(chat_id_)
                await message.reply("شارژ کم شد", chat_id)
            elif text.startswith("!"):
                cmd = text.split()
                chat_id_ = cmd[1]
                a = await get_group_charge_status(chat_id_)
                chat_id = a.get("chat_id")
                remaining_days = await ops(chat_id_)
                messages = f"""{remaining_days} روز از شارژ شما باقیمانده است"""
                await message.reply(str(messages), chat_id)
            elif text.startswith("/send"):
                if not admin:
                    await msg.reply(t(lang, "only_owner_send"))
                    return
                await message.reply(
                    "📢 لطفا نوع ارسال همگانی را انتخاب کنید:",
                    chat_keypad=build_send_type_keypad(lang),
                )
            elif text.startswith("/admin"):
                await handle_add_admin(msg, bot)
            elif text.startswith("/del_admin"):
                await handle_remove_admin(msg, bot)
            elif text.startswith("/add_chanel"):
                try:
                    parts = text.split(maxsplit=2)
                    if len(parts) < 3:
                        await message.reply(
                            "❌ فرمت صحیح: /add_chanel <نام> <لینک>\nمثال: /add_chanel کانال_من https://t.me/my_channel"
                        )
                        return
                    name = parts[1].strip()
                    link = parts[2].strip()
                    if not link.startswith(("https://", "http://", "t.me/", "@")):
                        await message.reply(
                            "❌ لینک معتبر نیست. باید با https:// یا t.me/ یا @ شروع شود"
                        )
                        return
                    if await channel_exists(link):
                        await message.reply("⚠️ این کانال قبلاً اضافه شده است")
                        return
                    await add_channel(name=name, link=link)
                    await message.reply(
                        f"✅ کانال با موفقیت اضافه شد:\n📝 نام: {name}\n🔗 لینک: {link}"
                    )
                except Exception as e:
                    await message.reply(f"❌ خطا در اضافه کردن کانال: {str(e)}")
            elif text.startswith("/remove_channel"):
                parts = text.split(maxsplit=1)
                if len(parts) >= 2:
                    link = parts[1]
                    if not await channel_exists(link):
                        await msg.reply("❌ این کانال در لیست وجود ندارد")
                        return
                    await remove_channel(link)
                    await msg.reply(f"✅ کانال با لینک {link} حذف شد")
                else:
                    await msg.reply("❌ فرمت صحیح: /remove_channel <لینک>")
            elif text.startswith("/list_channels"):
                data = await get_data()
                channels = data["channels"]
                if not channels:
                    await message.reply("📭 هیچ کانالی ثبت نشده است.")
                    return
                text = "📢 **لیست کانال‌های ثبت شده:**\n\n"
                for i, channel in enumerate(channels, 1):
                    text += f"{i}. **{channel['name']}**\n"
                    text += f"   🔗 {channel['link']}\n\n"
                text += f"📊 تعداد کل: {len(channels)} کانال"
                await message.reply(text)
            elif text.startswith("/channel_count"):
                count = await count_channels()
                await msg.reply(f"📊 تعداد کانال‌های ثبت شده: {count}")
    @bot.on_message_group(filters=filters.is_text)
    async def handler_gp(bot: Robot, message: Message):
        try:
            text = message.text
            chat_id = message.chat_id
            send_id = message.sender_id
            sender_id = message.sender_id
            start = ["فعال", "active", "تفعيل"]
            gp_name = await bot.get_name(chat_id=chat_id)
            rol = await get_user_role(chat_id=chat_id, user_id=send_id)
            suport = SUPPORT_GUID
            admin = rol in ["owner", "vip"] or send_id == suport
            chat_id = message.chat_id
            bot_name = await get_bot_name(chat_id)
            delet_timer = await get_time_deleter(chat_id)
            is_deleted_timer = await are_delet_timer_dashboard(chat_id)
            msg = message
            data = await get_group_status(chat_id)
            if text in start:
                if not await group_exists(chat_id=chat_id):
                    await add_group(chat_id=chat_id, name=gp_name, active=True)
                    await add_member(chat_id=chat_id, user_id=send_id, role="owner")
                    await lock_links(chat_id)
                    await lock_forward(chat_id)
                    await lock_bad(chat_id)
                    await lock_filter(chat_id)
                    await set_group_model(chat_id=chat_id, model=int(2))
                    await message.reply(
                        await MPro(t("fa", key="activate_message"), chat_id)
                    )
                else:
                    if await has_ownerr(user_id=send_id, chat_id=chat_id):
                        if await is_group_active(chat_id=chat_id):
                            grop_name = await bot.get_name(chat_id=chat_id)
                            await reply(
                                message,
                                await MPro(
                                    f"ربات در گروه {grop_name} فعال بود", chat_id
                                ),
                                is_deleted_timer,
                                delet_timer,
                            )
                        else:
                            await activate_group(chat_id=chat_id)
                            await reply(
                                message,
                                await MPro("ربات در گروه فعال شد"),
                                is_deleted_timer,
                                delet_timer,
                            )
                    else:
                        await reply(
                            message,
                            await MPro("شما دسترسی ندارید", chat_id),
                            is_deleted_timer,
                            delet_timer,
                        )
            if await group_exists(chat_id=chat_id) and await is_group_active(
                chat_id=chat_id
            ):
                if not await get_member(chat_id, sender_id):
                    await add_member(chat_id=chat_id, user_id=send_id, role="member")
                if await get_member_by(chat_id, sender_id):
                    pass
                else:
                    await set_member(
                        chat_id=chat_id,
                        sender_id=send_id,
                        original="بدون اصل",
                        nickname="بدون لقب",
                    )
            mes = await bot.get_message(
                chat_id=chat_id,
                message_id=message.message_id or message.reply_to_message_id,
            )
            type_ = message_type(mes)
            if await can_welcome(chat_id):
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"""بدو بیاد گپتو تبلیغ کن😉❤️
            {LINK_LINKDONI}
            بیا همشهریتو پیدا کن ✔️💯
            {LINK_LINKDONI}
            پاشو بیا تا از دست نرفته پر دختر🤧✅
            {LINK_LINKDONI}
            
            ربات نیاز داشتی بدو بیا تو کانال
            {CHANNEL_MAIN_LC}"""
                        )
            stat_map = {"text": "messages", "photo": "photos"}
            if type_ in stat_map:
                chat_id_ = str(mes.get("chat_id", chat_id))
                sender_id_ = str(mes.get("sender_id", message.sender_id))
                await increment_stat(
                    chat_id=chat_id_,
                    user_id=sender_id_,
                    stat=stat_map[type_],
                )
            links = [
                "http://",
                "https://",
                "t.me/",
                "www.",
                ".com",
                ".ir",
                ".org",
                ".net",
            ]
            if text and any(link in text for link in links):
                await increment_stat(
                    chat_id=str(msg.chat_id),
                    user_id=str(msg.sender_id),
                    stat="links",
                )
            type = message_type(mes)
            if type == "photo":
                op = "photos"
            elif type == "video":
                op = "videos"
            elif type == "file":
                op = "documents"
            elif type == "voice":
                op = "voice"
            elif type == "sticker":
                op = "sticker"
            elif type == "file":
                op = "documents"
            elif contains_english(text):
                op = "english"
            elif contains_pars(text):
                op = "persian"
            elif type == "location":
                op = "location"
            elif type == "poll":
                op = "polls"
            elif type == "forward":
                op = "forward"
            elif type == "text":
                text = msg.text or ""
                if (
                    "http://" in text
                    or "https://" in text
                    or "t.me" in text
                    or "www." in text
                ):
                    op = "links"
                elif "#" in text:
                    op = "hashtag"
                else:
                    op = "messages"
            else:
                op = "messages"
            if op:
                await increment_stat(
                    chat_id=str(msg.chat_id),
                    user_id=str(msg.sender_id),
                    stat=op,
                )
            await run_all_features_parallel(
                chat_id,
                message,
                text,
                bot,
                send_id,
                sender_id,
                rol,
                admin,
                data,
                suport,
                bot_name,
                delet_timer,
                is_deleted_timer,
            )
        except Exception as e:
            print("Error" + e)
    stop_event = asyncio.Event()
    asyncio.create_task(backup_scheduler(stop_event))
    await bot.run(sleep_time=0)
async def runner():
    while True:
        try:
            await main()
        except Exception as e:
            print("❌ Bot crashed")
            traceback.print_exc()
            await asyncio.sleep(2)
if __name__ == "__main__":
    asyncio.run(runner())
