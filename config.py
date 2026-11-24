# ============================================================
#  config.py  —  همه‌ی توکن‌ها، آیدی‌ها و لینک‌های ربات فقط اینجاست
#  برای تحویل ربات به دوستان فقط همین فایل را ویرایش کنید.
# ============================================================


# ---------------------- توکن و اتصال ربات ----------------------

# توکن ربات روبیکا (از بات‌فادر / @BotFather روبیکا گرفته می‌شود).
# ⚠️ هر کسی این توکن را داشته باشد کنترل کامل ربات را دارد؛ برای دوستان توکن ربات خودشان را بگذارید.
BOT_TOKEN = "FFCFC0HLOOUGYLDBZRMLWMPNIAKHNHZHKYKHAFCWLMCERPFFPLRJTYINVKRKZYKC"

# آدرس وب‌هوک (webhook) که ربات رویدادها/لاگ‌ها را به آن می‌فرستد.
# اگر وب‌هوک ندارید می‌توانید به None تغییر دهید (در این صورت باید پارامتر web_hook هم در Robot(...) حذف شود).
WEBHOOK_URL = "https://python-dragon-bot.ir/webhook_logger.php"


# ---------------------- آیدی‌های عددی/GUID روبیکا ----------------------

# GUID پشتیبان/سازنده‌ی ربات (سوپر ادمین).
# این کاربر در «همه‌ی گروه‌ها» دسترسی کامل مالک دارد (قفل‌ها، ریست، شارژ، انتقال مالکیت و ...).
# ⚠️ حتماً با GUID خودتان جایگزین کنید، وگرنه سازنده‌ی اصلی روی گروه‌های شما اختیار کامل دارد.
SUPPORT_GUID = "u0I2kJn05e721fd6be55067449514653"

# GUID حساب سازنده؛ دکمه‌ی لینک‌دار «👨‍💻 سازنده» وقتی کاربر کلمه‌ی «سازنده» را می‌فرستد به این حساب لینک می‌دهد.
CREATOR_GUID = "u0IjUXv07676164059a3c5e7480d7f68"

# GUID چت/کانالی که گزارش «انتقال مالکیت گروه» به آن ارسال می‌شود (چه کسی به چه کسی در کدام گروه).
LOG_CHAT_GUID = "b0I2kJn0LC506c3acaf0832012bd6af9"

# GUID کانال اصلی ربات برای بررسی عضویت اجباری.
# توجه: در نسخه‌ی فعلی بررسی عضویت غیرفعال است (کامنت شده بود) و این مقدار استفاده نمی‌شود.
GUID_CHANNEL = "c0Cvh1k09424c0bb395fcc6dd7acb1a6"

# GUID کانال دوم (کانال اسپانسر) برای بررسی عضویت اجباری. مثل مورد بالا فعلاً استفاده نمی‌شود.
GUID_CHANNEL_SPONSOR = "c0BiLJE06414f7a7a5c5c6af47f4c0b7"


# ---------------------- آیدی‌ها و لینک‌های کانال/پشتیبانی (متن پیام‌ها) ----------------------

# آیدی بدون @ کانال اصلی ربات. بقیه‌ی آیدی‌ها و لینک‌های این کانال از روی همین ساخته می‌شوند.
CHANNEL_ID = "Dragonbot_ch"

# آیدی کانال اصلی با @ — در پیام خوش‌آمد، راهنما، قیمت‌ها و ... نمایش داده می‌شود.
CHANNEL_MAIN = "@" + CHANNEL_ID

# همان آیدی کانال اصلی با حروف کوچک (در چند پیام به همین شکل نوشته شده بود).
CHANNEL_MAIN_LC = CHANNEL_MAIN.lower()

# لینک کانال اصلی در روبیکا.
LINK_CHANNEL_MAIN = "https://rubika.ir/" + CHANNEL_ID

# لینک ویدیوی آموزشی استفاده از ربات (پستی داخل کانال اصلی).
LINK_TUTORIAL_VIDEO = LINK_CHANNEL_MAIN + "/BEEAHFAJHCFICBHG"

# آیدی بدون @ کانال لینکدونی.
LINKDONI_ID = "Linkdoniturkih"

# آیدی کانال لینکدونی با @.
CHANNEL_LINKDONI = "@" + LINKDONI_ID

# لینک (بدون https) کانال لینکدونی که در پیام تبلیغاتی گروه‌ها استفاده می‌شود.
LINK_LINKDONI = "rubika.ir/" + LINKDONI_ID

# آیدی کانال پشتیبانی که لیست کامل دستورات آنجاست.
CHANNEL_COMMANDS = "@DragonBot_Support"

# آیدی پشتیبانی/سازنده برای خرید شارژ گروه و توسعه‌دهنده‌ی ربات.
SUPPORT_USERNAME = "@ali_ceder"


# ---------------------- APIهای خدمات سرگرمی (سایت dragon-bot.ir) ----------------------

# آدرس پایه‌ی APIهای سرگرمی.
API_BASE = "https://dragon-bot.ir/api/"

# آدرس هر سرویس: بیو، چالش، دانستنی، جوک، حدیث، فحش‌یاب (فیلتر متن نامناسب)، داستان، دیالوگ، فیک، فال، غزل.
API_URLS = {
    "bio": API_BASE + "bio/",
    "chalesh": API_BASE + "chalesh/",
    "danestani": API_BASE + "danestan/",
    "jok": API_BASE + "jok/",
    "hadis": API_BASE + "hadis/",
    "fohsh": API_BASE + "fohsh/",
    "dastan": API_BASE + "dastan/dastan.php",
    "dialog": API_BASE + "dialog/",
    "fake": API_BASE + "fake/",
    "fal": API_BASE + "fal/",
    "gazal": API_BASE + "gazal/",
}


# ---------------------- APIهای قیمت و هوش مصنوعی (سایت rubigram.ir) ----------------------

# API چت هوش مصنوعی (دستورهایی مثل /openai سوال).
AI_CHAT_URL = "https://rubigram.ir/api/ai/chat/text"

# API قیمت طلا و نقره.
GOLD_API = "https://rubigram.ir/api/gold.php"

# API قیمت سکه.
COIN_API = "https://rubigram.ir/api/coin.php"

# API قیمت ارز.
CURRENCY_API = "https://rubigram.ir/api/currency.php"

# API قیمت ارز دیجیتال (با پارامتر id).
DIGITAL_API = "https://rubigram.ir/api/price/search-digital-currency"


# ---------------------- APIهای سخنگو ----------------------

# API دریافت پاسخ سخنگو (مودب/بی‌ادب) برای پیام‌های گروه.
SPEAK_URL = "https://l8p.ir/API-SPEAK/speak.php"

# API ثبت جواب جدید برای سخنگو (تابع send_answer).
SPEAK_SEND_URL = "https://alicoder.atlas.fastsub.site/api/speak/speak.php"

# API آموزش سخنگو با دستور «سوال!جواب» (تابع add_question_answer؛ در نسخه‌ی فعلی غیرفعال است).
SPEAK_LEARN_URL = "https://alicoder.atlas.fastsub.site/api/drag_speak/"
