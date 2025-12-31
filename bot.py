import os
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Берёт из Environment Variables

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, 
        "Привет! Я бот для проверки хостинга серверов Minecraft Bedrock. Введите /whois <домен или IP> для получения информации."
    )

@bot.message_handler(commands=['whois'])
def cmd_whois(message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        bot.reply_to(message, "Использование: /whois <домен или IP[:порт]>")
        return

    address = text[1].strip()

    # Отправляем сообщение, которое будем редактировать (для скорости)
    status_msg = bot.reply_to(message, "<i>🔍 Получаю информацию...</i>")

    host = address
    port = 19132

    if ':' in host:
        parts = host.split(':', 1)
        host = parts[0]
        try:
            port = int(parts[1])
        except:
            port = 19132

    server_online = False
    server_name = 'Неизвестно'
    core = 'Неизвестно'
    online_players = '0/0'
    ip_for_geo = host
try:
        url = f"https://api.mcsrvstat.us/bedrock/3/{host}"
        if port != 19132:
            url += f":{port}"
        headers = {"User-Agent": "CubexBot/1.0"}  # Ускоряет ответ от API
        resp = requests.get(url, timeout=8, headers=headers)
        data = resp.json()

        if data.get("online"):
            server_online = True
            server_name = data.get("motd", {}).get("clean", ["Без названия"])[0]
            players = data.get("players", {})
            online_players = f"{players.get('online', 0)}/{players.get('max', 0)}"
            version = data.get("version", "Неизвестно")

            ver_lower = version.lower()
            if "pocketmine" in ver_lower:
                core = "PocketMine-MP"
            elif "nukkit" in ver_lower:
                core = "Nukkit"
            elif "litecore" in ver_lower:
                core = "LiteCore"
            elif "submarine" in ver_lower:
                core = "Submarine"
            elif "bedrock" in ver_lower:
                core = "Vanilla Bedrock"
            else:
                core = version

            if data.get("ip"):
                ip_for_geo = data["ip"]
    except:
        pass
org = 'Неизвестно'
    provider = 'Неизвестно'
    country = 'Неизвестно'
    city = 'Неизвестно'
    timezone = 'Неизвестно'

    geo_urls = [
        f"https://ip-api.com/json/{ip_for_geo}?fields=org,isp,as,asname,country,countryCode,city,timezone&lang=ru",
        f"https://ipwho.is/{ip_for_geo}",
        f"https://free.freeipapi.com/api/json/{ip_for_geo}",
        f"https://ipinfo.io/{ip_for_geo}/json",
        f"https://ipapi.co/{ip_for_geo}/json/",
        f"https://api.ipgeolocation.io/ipgeo?ip={ip_for_geo}"
    ]

    headers = {"User-Agent": "CubexBot/1.0"}

    for url in geo_urls:
        try:
            resp = requests.get(url, timeout=6, headers=headers)
            if resp.status_code != 200:
                continue
            geo = resp.json()

            if "ip-api.com" in url:
                if geo.get("status") == "fail":
                    continue
                org = geo.get("org", "Неизвестно")
                provider = geo.get("isp") or geo.get("asname") or (geo.get("as") and geo["as"].split(' ', 1)[1] if ' ' in geo.get("as", "") else "Неизвестно") or "Неизвестно"
                country = f"{geo.get('country', 'Неизвестно')} ({geo.get('countryCode', '')})"
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", "Неизвестно")
                break

            elif "ipwho.is" in url:
                if not geo.get("success"):
                    continue
                org = geo.get("org") or geo.get("connection", {}).get("org") or "Неизвестно"
                provider = geo.get("connection", {}).get("isp") or org or "Неизвестно"
                country = f"{geo.get('country', 'Неизвестно')} ({geo.get('country_code', '')})"
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", {}).get("name", "Неизвестно")
                break

            elif "freeipapi" in url:
                org = geo.get("organization", "Неизвестно")
                provider = geo.get("isp", "Неизвестно")
                country = f"{geo.get('countryName', 'Неизвестно')} ({geo.get('countryCode', '')})"
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timeZone", "Неизвестно")
                break

            elif "ipinfo.io" in url:
                if geo.get("error"):
                    continue
                org = geo.get("company", {}).get("name", "Неизвестно")
                provider = geo.get("org", "Неизвестно").split(' ', 1)[1] if ' ' in geo.get("org", "") else "Неизвестно"
                country = geo.get("country", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", "Неизвестно")
                break

            elif "ipapi.co" in url:
                org = geo.get("org", "Неизвестно")
                provider = geo.get("asn", "Неизвестно")
                country = f"{geo.get('country_name', 'Неизвестно')} ({geo.get('country', '')})"
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", "Неизвестно")
                break

            elif "ipgeolocation" in url:
                if geo.get("message"):
                    continue
                org = geo.get("organization", "Неизвестно")
                provider = geo.get("isp", "Неизвестно")
                country = f"{geo.get('country_name', 'Неизвестно')} ({geo.get('country_code2', '')})"
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("time_zone", {}).get("name", "Неизвестно")
                break
        except:
            continue

    response = (
        f"<b>Информация о адресе:</b>\n\n"
        f"💻 <b>Домен ресурса:</b> {address}\n"
        f"👥 <b>Организация:</b> {org}\n"
        f"💎 <b>Провайдер:</b> {provider}\n\n"
        f"🌐 <b>Страна:</b> {country}\n"
        f"🏠 <b>Город:</b> {city}\n"
        f"🌍 <b>Часовой пояс:</b> {timezone}"
    )

    if server_online:
        response += (
            f"\n\n<b>🎮 Информация о сервере Minecraft Bedrock:</b>\n\n"
            f"📛 <b>Название сервера:</b> {server_name}\n"
            f"🔢 <b>Онлайн игроков:</b> {online_players}\n"
            f"🛠 <b>Ядро / Версия:</b> {core}"
        )
    else:
        response += "\n\n❌ Сервер Minecraft Bedrock сейчас оффлайн или недоступен по указанному адресу."

    # Редактируем сообщение "Получаю информацию..." на полный ответ
    bot.edit_message_text(chat_id=status_msg.chat.id, message_id=status_msg.message_id, text=response)

bot.infinity_polling(timeout=20, long_polling_timeout=10)
