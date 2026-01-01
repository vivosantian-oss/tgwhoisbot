import telebot
import requests
from dotenv import load_dotenv
import os

load_dotenv(8396206351:AAEZv2BNBD_iWy5gFE-1D2zeqzBAoMWQcE8)  # Загружает .env файл на Bothost.ru

BOT_TOKEN = os.getenv("8396206351:AAEZv2BNBD_iWy5gFE-1D2zeqzBAoMWQcE8")

if BOT_TOKEN is None:
    print("ОШИБКА: BOT_TOKEN не найден в .env!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, 
        "Привет! Я бот для проверки хостинга серверов Minecraft Bedrock.\n\n"
        "Команды:\n/start — это сообщение\n/whois <домен или IP[:порт]> — подробная информация о сервере и хостинге"
    )

@bot.message_handler(commands=['whois'])
def cmd_whois(message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        bot.reply_to(message, "Использование: /whois <домен или IP[:порт]>\nПример: /whois play.hypixel.net")
        return

    address = text[1].strip()

    status_msg = bot.reply_to(message, f"🔍 Получаю информацию о {address}...")

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
    version_full = 'Неизвестно'
    ip_for_geo = host
    real_ip = 'Неизвестно'
    motd_full = 'Неизвестно'

    # Получаем информацию о сервере Minecraft Bedrock (максимум деталей)
    try:
        url = f"https://api.mcsrvstat.us/bedrock/3/{host}"
        if port != 19132:
            url += f":{port}"
        headers = {"User-Agent": "CubexWhoisBot/1.0"}
        resp = requests.get(url, timeout=10, headers=headers)
        data = resp.json()

        if data.get("online"):
            server_online = True
            server_name = data.get("motd", {}).get("clean", ["Без названия"])[0]
            motd_full = " ".join(data.get("motd", {}).get("clean", [""]))
            players = data.get("players", {})
            online_players = f"{players.get('online', 0)}/{players.get('max', 0)}"
            version_full = data.get("version", "Неизвестно")
            list_players = data.get("players", {}).get("list", [])
            players_list = ", ".join(list_players[:20]) if list_players else "Нет в списке"

            ver_lower = version_full.lower()
            if "pocketmine" in ver_lower:
                core = "PocketMine-MP"
            elif "nukkit" in ver_lower:
                core = "Nukkit"
            elif "litecore" in ver_lower:
                core = "LiteCore"
            elif "submarine" in ver_lower:
                core = "Submarine"
            elif "bedrock" in ver_lower or "minecraft" in ver_lower:
                core = "Vanilla Bedrock"
            else:
                core = version_full

            if data.get("ip"):
                ip_for_geo = data["ip"]
                real_ip = data["ip"]
            if data.get("port"):
                port = data["port"]
    except Exception as e:
        print(f"Ошибка mcsrvstat: {e}")

    # Максимум geo-API (9 штук) для точного определения организации, провайдера, города, пояса
    org = 'Неизвестно'
    provider = 'Неизвестно'
    country = 'Неизвестно'
    city = 'Неизвестно'
    timezone = 'Неизвестно'
    region = 'Неизвестно'
    asn = 'Неизвестно'

    geo_urls = [
        f"https://ip-api.com/json/{ip_for_geo}?fields=org,isp,as,asname,country,countryCode,regionName,city,timezone&lang=ru",
        f"https://api.ipwho.is/{ip_for_geo}?fields=connection,timezone,country,country_code,city,region",
        f"https://free.freeipapi.com/api/json/{ip_for_geo}",
        f"https://ipinfo.io/{ip_for_geo}/json",
        f"https://ipapi.co/{ip_for_geo}/json/",
        f"https://api.ipgeolocation.io/ipgeo?ip={ip_for_geo}&fields=organization,isp,country_name,country_code2,region_name,city,time_zone",
        f"https://reallyfreegeoip.com/json/{ip_for_geo}",
        f"https://ipwhois.app/json/{ip_for_geo}",
        f"https://www.iplocation.net/ip/{ip_for_geo}"
    ]

    headers = {"User-Agent": "CubexWhoisBot/1.0"}

    for url in geo_urls:
        try:
            resp = requests.get(url, timeout=7, headers=headers)
            if resp.status_code != 200:
                continue
            geo = resp.json()

            success = False

            if "ip-api.com" in url:
                if geo.get("status") == "success":
                    success = True
                    org = geo.get("org", "Неизвестно")
                    provider = geo.get("isp") or geo.get("asname") or "Неизвестно"
                    asn = geo.get("as", "Неизвестно")
                    country = f"{geo.get('country', 'Неизвестно')} ({geo.get('countryCode', '')})"
                    region = geo.get("regionName", "Неизвестно")
                    city = geo.get("city", "Неизвестно")
                    timezone = geo.get("timezone", "Неизвестно")

            elif "ipwho.is" in url:
                if geo.get("success"):
                    success = True
                    org = geo.get("org", "Неизвестно")
                    provider = geo.get("connection", {}).get("isp", "Неизвестно")
                    asn = geo.get("connection", {}).get("asn", "Неизвестно")
                    country = f"{geo.get('country', 'Неизвестно')} ({geo.get('country_code', '')})"
                    region = geo.get("region", "Неизвестно")
                    city = geo.get("city", "Неизвестно")
                    timezone = geo.get("timezone", {}).get("name", "Неизвестно")

            elif "freeipapi" in url:
                success = True
                org = geo.get("organization", "Неизвестно")
                provider = geo.get("isp", "Неизвестно")
                asn = geo.get("asn", "Неизвестно")
                country = f"{geo.get('countryName', 'Неизвестно')} ({geo.get('countryCode', '')})"
                region = geo.get("regionName", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timeZone", "Неизвестно")

            elif "ipinfo.io" in url:
                if geo.get("error"):
                    continue
                success = True
                org = geo.get("company", {}).get("name", "Неизвестно")
                provider = geo.get("org", "Неизвестно").split(' ', 1)[1] if ' ' in geo.get("org", "") else "Неизвестно"
                asn = geo.get("org", "Неизвестно").split(' ', 1)[0] if ' ' in geo.get("org", "") else "Неизвестно"
                country = geo.get("country", "Неизвестно")
                region = geo.get("region", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", "Неизвестно")

            elif "ipapi.co" in url:
                success = True
                org = geo.get("org", "Неизвестно")
                provider = geo.get("asn", "Неизвестно")
                asn = geo.get("asn", "Неизвестно")
                country = f"{geo.get('country_name', 'Неизвестно')} ({geo.get('country', '')})"
                region = geo.get("region", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", "Неизвестно")

            elif "ipgeolocation" in url:
                if geo.get("message"):
                    continue
                success = True
                org = geo.get("organization", "Неизвестно")
                provider = geo.get("isp", "Неизвестно")
                asn = geo.get("asn", "Неизвестно")
                country = f"{geo.get('country_name', 'Неизвестно')} ({geo.get('country_code2', '')})"
                region = geo.get("state_prov", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("time_zone", {}).get("name", "Неизвестно")

            elif "reallyfreegeoip" in url:
                success = True
                org = geo.get("org", "Неизвестно")
                provider = geo.get("isp", "Неизвестно")
                country = f"{geo.get('country_name', 'Неизвестно')} ({geo.get('country_code', '')})"
                region = geo.get("region", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("time_zone", "Неизвестно")

            elif "ipwhois.app" in url:
                success = True
                org = geo.get("org", "Неизвестно")
                provider = geo.get("isp", "Неизвестно")
                asn = geo.get("asn", "Неизвестно")
                country = f"{geo.get('country', 'Неизвестно')} ({geo.get('country_code', '')})"
                region = geo.get("region", "Неизвестно")
                city = geo.get("city", "Неизвестно")
                timezone = geo.get("timezone", "Неизвестно")

            if success:
                break
        except Exception as e:
            print(f"Geo ошибка {url}: {e}")
            continue

    # Насыщенный ответ с максимум информации
    response = (
        f"<b>🔍 Информация о адресе {address}</b>\n\n"
        f"🌐 <b>Реальный IP:</b> {real_ip}\n"
        f"🔌 <b>Порт:</b> {port}\n\n"
        f"🏢 <b>Организация:</b> {org}\n"
        f"💎 <b>Провайдер / ASN:</b> {provider} ({asn})\n"
        f"🌍 <b>Страна:</b> {country}\n"
        f"🗺 <b>Регион:</b> {region}\n"
        f"🏙 <b>Город:</b> {city}\n"
        f"🕐 <b>Часовой пояс:</b> {timezone}\n"
    )

    if server_online:
        response += (
            f"\n<b>🎮 Сервер Minecraft Bedrock онлайн!</b>\n\n"
            f"📛 <b>Название:</b> {server_name}\n"
            f"📜 <b>MOTD:</b> {motd_full}\n"
            f"👥 <b>Онлайн игроков:</b> {online_players}\n"
            f"🛠 <b>Ядро / Версия:</b> {core} ({version_full})\n"
        )
        if 'players_list' in locals() and players_list:
            response += f"👤 <b>Игроки онлайн:</b> {players_list}\n"
    else:
        response += "\n<b>❌ Сервер Minecraft Bedrock оффлайн или недоступен.</b>"

    bot.edit_message_text(chat_id=status_msg.chat.id, message_id=status_msg.message_id, text=response, parse_mode="HTML")

bot.infinity_polling(none_stop=True)
