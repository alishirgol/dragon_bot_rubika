import aiohttp
import requests
from config import API_URLS, AI_CHAT_URL, GOLD_API, COIN_API, CURRENCY_API, DIGITAL_API
import json
import asyncio
import threading
import time
import random
API_KEYS = {
    "bio": "bio",
    "chalesh": "chlesh",
    "danestani": "dastan",
    "jok": "joke",
    "hadis": "hadis",
    "fohsh": "fohsh",
    "dastan": "dastan",
    "dialog": "dialog",
    "fake": "faker",
    "fal": "fal",
    "gazal": "ghazal",
}
async def get_api_text(api_name: str) -> str:
    url = API_URLS.get(api_name)
    if not url:
        return f"API '{api_name}' not found"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return f"Error: HTTP {response.status}"
                raw_text = await response.text()
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError:
                    fixed = (
                        raw_text.replace("'", '"')
                        .replace("True", "true")
                        .replace("False", "false")
                        .replace("None", "null")
                    )
                    try:
                        data = json.loads(fixed)
                    except Exception:
                        return f"Invalid JSON response: {raw_text[:150]}"
                key = API_KEYS.get(api_name)
                if key and key in data:
                    block = data[key]
                    if isinstance(block, dict) and "data" in block:
                        try:
                            info = block["data"]
                            for k, v in info.items():
                                if isinstance(v, list):
                                    info[k] = "، ".join(map(str, v))
                            fake_text = (
                                f"👥 اطلاعات فیک\n\n"
                                f"👩‍🦰 نام زن: {info.get('firstNameFemale', '')}\n"
                                f"👨‍🦱 نام مرد: {info.get('firstnamemale', '')} {info.get('lastname', '')}\n"
                                f"🏙 استان: {info.get('cityName', '')}\n"
                                f"🏢 زمینه شغلی: {info.get('companyField', '')}\n"
                                f"📱 موبایل: {info.get('mobileNumberPrefixes', '')}\n"
                                f"📬 کد پستی: {info.get('formats', '')}\n"
                                f"📝 بیوگرافی: {info.get('biography', 'بیوگرافی ثبت نشده')}\n"
                                f"📄 نوع قرارداد: {info.get('contract', '')}"
                            )
                            return fake_text.strip()
                        except Exception as e:
                            return f"❌ خطا در پردازش داده فیک: {e}"
                    if isinstance(block, dict):
                        if "text" in block:
                            return block["text"]
                        elif "developer" in block:
                            return f"{block.get('text', 'متنی یافت نشد.')}\n\n👨‍💻 {block.get('developer', '')}"
                        else:
                            return str(block)
                    if isinstance(block, str):
                        return block
                elif "text" in data:
                    return data["text"]
                elif "error" in data:
                    err = data["error"]
                    if isinstance(err, dict):
                        return err.get("text", "Error but no message")
                    return str(err)
                else:
                    return f"Unknown response format: {data}"
    except asyncio.TimeoutError:
        return "Timeout: ⏰ سرور پاسخ نداد"
    except aiohttp.ClientError as e:
        return f"Connection error: {str(e)}"
    except json.JSONDecodeError:
        return "Invalid JSON response"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
async def check_text_advanced(
    text: str = None, php_url: str = API_URLS.get("fohsh"), **kwargs
):
    try:
        params = {"text": text}
        async with aiohttp.ClientSession() as session:
            async with session.get(php_url, params=params, **kwargs) as resp:
                if resp.status != 200:
                    return {
                        "success": False,
                        "error": f"خطای HTTP: {resp.status}",
                        "status_code": resp.status,
                    }
                raw = await resp.text()
                if not raw.strip():
                    return {
                        "success": False,
                        "error": "پاسخ خالی از سرور",
                        "status_code": resp.status,
                    }
                try:
                    data = json.loads(raw)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"خطای JSON: {str(e)}",
                        "status_code": resp.status,
                        "raw_response": raw[:100],
                    }
                return {"success": True, "data": data, "status_code": resp.status}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout: سرور در زمان مشخص شده پاسخ نداد"}
    except aiohttp.ClientError as e:
        return {"success": False, "error": f"خطای ارتباط: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"خطای ناشناخته: {str(e)}"}
async def get_bio() -> str:
    return await get_api_text("bio")
async def get_chalesh() -> str:
    return await get_api_text("chalesh")
async def get_danestani() -> str:
    return await get_api_text("danestani")
async def get_jok() -> str:
    return await get_api_text("jok")
async def get_hadis() -> str:
    return await get_api_text("hadis")
async def get_fohsh() -> str:
    return await get_api_text("fohsh")
async def get_dastan() -> str:
    return await get_api_text("dastan")
async def get_dialog() -> str:
    return await get_api_text("dialog")
async def get_fake() -> str:
    return await get_api_text("fake")
async def get_fal() -> str:
    return await get_api_text("fal")
async def get_gazal() -> str:
    return await get_api_text("gazal")
VALID_MODELS = frozenset((
    "openai", "deepseek", "gemini", "gemini-search", "mistral",
    "openai-fast", "openai-large", "openai-reasoning", "qwen-coder", "roblox-rp",
    "bidara", "chickytutor", "midijourney", "rtist", "unity",
))
def rubigram_chat(text: str, model: str = "openai"):
    model = str(model).lower().strip()
    if model not in VALID_MODELS:
        model = "openai"
    try:
        response = requests.get(
            AI_CHAT_URL,
            params={"text": text, "model": model},
            timeout=30,
        )
        return response.json()
    except Exception as e:
        return {"status": False, "error": str(e)}
def split_text_lines(text: str, max_chars=4000, max_lines=120):
    lines = text.split("\n")
    chunks = []
    current = []
    current_len = 0
    for line in lines:
        line_len = len(line) + 1
        if current_len + line_len > max_chars or len(current) >= max_lines:
            chunks.append("\n".join(current))
            current = [line]
            current_len = line_len
        else:
            current.append(line)
            current_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks
def get_gold_lists_sorted():
    try:
        r = requests.get(GOLD_API, timeout=10)
        data = r.json()
    except Exception:
        return [], [], "❌ خطا در دریافت اطلاعات طلا"
    items = data.get("response", [])
    if not items:
        return [], [], "❌ اطلاعاتی یافت نشد"
    gold_blocks = []
    silver_blocks = []
    last_time = ""
    for i in items:
        name = i["name"]
        last_time = i["time"]
        try:
            price = float(i["price"].replace(",", ""))
        except:
            price = 0.0
        block_text = (
            f"🔹 {name}\n"
            f"💰 قیمت: {i['price']} ریال\n"
            f"📈 تغییر: {i['change']}\n"
            f"⬇️ کمترین: {i['low']}\n"
            f"⬆️ بیشترین: {i['high']}\n"
        )
        block = {"name": name, "price": price, "text": block_text}
        if "نقره" in name:
            silver_blocks.append(block)
        else:
            gold_blocks.append(block)
    gold_blocks.sort(key=lambda x: x["price"], reverse=True)
    silver_blocks.sort(key=lambda x: x["price"], reverse=True)
    gold_text = (
        "💛 **طلا و صندوق‌ها**\n"
        + "─" * 18
        + "\n"
        + "\n".join([b["text"] for b in gold_blocks])
    )
    silver_text = (
        "🪙 **نقره**\n"
        + "─" * 18
        + "\n"
        + "\n".join([b["text"] for b in silver_blocks])
    )
    gold_chunks = split_text_lines(gold_text)
    silver_chunks = split_text_lines(silver_text)
    return gold_chunks, silver_chunks, last_time
def get_coin_text() -> str:
    try:
        r = requests.get(COIN_API, timeout=10)
        data = r.json()
    except Exception:
        return "❌ خطا در دریافت قیمت سکه"
    items = data.get("response", [])
    if not items:
        return "❌ اطلاعات سکه یافت نشد"
    text = "🪙 **قیمت لحظه‌ای سکه**\n━━━━━━━━━━━━━━━\n"
    last_time = ""
    for i in items:
        last_time = i["time"]
        text += (
            f"🔹 {i['name']}\n"
            f"💰 قیمت: {i['price']} ریال\n"
            f"📈 تغییر: {i['change']}\n"
            f"⬇️ کمترین: {i['low']}\n"
            f"⬆️ بیشترین: {i['high']}\n\n"
        )
    text += f"⏰ بروزرسانی: {last_time}\n📡 {CHANNEL_MAIN}"
    return text
def get_currency_text() -> str:
    try:
        r = requests.get(CURRENCY_API, timeout=10)
        data = r.json()
    except Exception:
        return "❌ خطا در دریافت قیمت ارز"
    items = data.get("response", [])
    if not items:
        return "❌ اطلاعات ارزی یافت نشد"
    text = "💱 **قیمت لحظه‌ای ارز**\n━━━━━━━━━━━━━━━\n"
    last_time = ""
    for i in items:
        last_time = i["time"]
        text += (
            f"🔹 {i['name']}\n"
            f"💰 قیمت: {i['price']} ریال\n"
            f"📈 تغییر: {i['change']}\n"
            f"⬇️ کمترین: {i['low']}\n"
            f"⬆️ بیشترین: {i['high']}\n\n"
        )
    text += f"⏰ بروزرسانی: {last_time}\n📡 {CHANNEL_MAIN}"
    return text
def get_digital_currency_text(currency_id: str) -> str:
    try:
        r = requests.get(DIGITAL_API, params={"id": currency_id}, timeout=10)
        data = r.json()
    except Exception:
        return "❌ خطا در دریافت اطلاعات ارز دیجیتال"
    if not data.get("status"):
        return "❌ ارز مورد نظر پیدا نشد"
    info = data.get("response", {})
    text = (
        "📈 **اطلاعات ارز دیجیتال**\n"
        "━━━━━━━━━━━━━━━\n"
        f"🔹 نام: {info.get('name')} ({info.get('fa_name')})\n"
        f"💠 نماد: {info.get('symbol')}\n"
        f"🏆 رتبه بازار: {info.get('rank')}\n"
        f"💰 قیمت جهانی: ${info.get('price')}\n"
        f"💵 قیمت به تومان: {info.get('price_irt')} تومان\n"
        f"📊 حجم معاملات: {info.get('volume')}\n"
        f"🏦 ارزش بازار: {info.get('market_cap')}\n"
        f"⏰ بروزرسانی: {info.get('last_updated')}\n"
        f"📡 {CHANNEL_MAIN}"
    )
    return text
def run_async_in_thread(async_func, *args, **kwargs):
    def wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    thread = threading.Thread(target=wrapper)
    thread.start()
    return thread
def get_api_text_threaded(api_name: str, timeout=30):
    result_container = {"result": None, "error": None}
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(get_api_text(api_name))
            result_container["result"] = result
        except Exception as e:
            result_container["error"] = str(e)
        finally:
            if loop:
                loop.close()
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=timeout)
    if thread.is_alive():
        return f"Timeout: API '{api_name}' took too long"
    if result_container["error"]:
        return f"Error: {result_container['error']}"
    return result_container["result"]
def batch_get_apis_threaded(api_names, timeout_per_api=10):
    results = {}
    threads = {}
    def fetch_api(api_name):
        results[api_name] = get_api_text_threaded(api_name, timeout_per_api)
    for api_name in api_names:
        thread = threading.Thread(target=fetch_api, args=(api_name,))
        thread.start()
        threads[api_name] = thread
    start_time = time.time()
    for api_name, thread in threads.items():
        remaining = max(0, timeout_per_api - (time.time() - start_time))
        if remaining > 0:
            thread.join(timeout=remaining)
        else:
            if api_name not in results:
                results[api_name] = f"Timeout for {api_name}"
    return results
def get_all_apis_parallel():
    all_apis = [
        "bio",
        "chalesh",
        "danestani",
        "jok",
        "hadis",
        "fohsh",
        "dastan",
        "dialog",
        "fake",
        "fal",
        "gazal",
    ]
    return batch_get_apis_threaded(all_apis)
def get_bio_threaded():
    return get_api_text_threaded("bio")
def get_chalesh_threaded():
    return get_api_text_threaded("chalesh")
def get_danestani_threaded():
    return get_api_text_threaded("danestani")
def get_jok_threaded():
    return get_api_text_threaded("jok")
def get_hadis_threaded():
    return get_api_text_threaded("hadis")
def get_fohsh_threaded():
    return get_api_text_threaded("fohsh")
def get_dastan_threaded():
    return get_api_text_threaded("dastan")
def get_dialog_threaded():
    return get_api_text_threaded("dialog")
def get_fake_threaded():
    return get_api_text_threaded("fake")
def get_fal_threaded():
    return get_api_text_threaded("fal")
def get_gazal_threaded():
    return get_api_text_threaded("gazal")
