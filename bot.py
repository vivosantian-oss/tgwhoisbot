import telebot
import requests
import os

BOT_TOKEN = os.getenv("8396206351:AAEZv2BNBD_iWy5gFE-1D2zeqzBAoMWQcE8")

if BOT_TOKEN is None:
    print("ОШИБКА: BOT_TOKEN не найден! Добавь в Secrets на Replit.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, 
        "Привет! Я бот для проверки хостинга серверов Minecraft Bedrock.\n\n"
        "Введите /whois <домен или IP> для получения информации."
    )

@bot.message_handler(commands=['whois'])
def cmd_whois(message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        bot.reply_to(message, "Использование: /whois <домен или IP[:порт]>")
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
    ip_for_geo = host
    real_ip = 'Неизвестно'

    try:
        url = f"https://api.mcsrvstat.us/bedrock/3/{host}"
        if port != 19132:
            url += f":{port}"
        headers = {"User-Agent": "CubexBot/1.0"}
        resp = requests.get(url, timeout=10, headers=headers)
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
                real_ip = data["ip"]
    except Exception as e:
        print(f"Ошибка mcsrvstat: {e}")

    # Максимум geo-API (10 штук) + fallback на лучшие поля
    org = 'Неизвестно'
    provider = 'Неизвестно'
    country = 'Неизвестно'
    city = 'Неизвестно'
    timezone = 'Неизвестно'
    region = 'Неизвестно'
    asn = 'Неизвестно'

    geo_urls = [
        f"https://ip-api.com/json/{ip_for_geo}?fields=org,isp,as,asname,country,countryCode,regionName,city,timezone&lang=ru",  # Самый точный для RU
        f"https://ipwho.is/{ip_for_geo}",
        f"https://free.freeipapi.com/api/json/{ip_for_geo}",
        f"https://ipinfo.io/{ip_for_geo}/json",
        f"https://ipapi.co/{ip_for_geo}/json/",
        f"https://api.ipgeolocation.io/ipgeo?ip={ip_for_geo}&fields=organization,isp,asn,country_name,country_code2,state_prov,city,time_zone",
        f"https://ipwhois.app/json/{ip_for_geo}",
        f"https://reallyfreegeoip.com/json/{ip_for_geo}",
        f"https://api.iplocation.net/?ip={ip_for_geo}",
        f"https://ip-api.pro/json/{ip_for_geo}"
    ]

    headers = {"User-Agent": "CubexBot/1.0"}

    for url in geo_urls:
        try:
            resp = requests.get(url, timeout=8, headers=headers)
            if resp.status_code != 200:
                continue
            geo = resp.json()

            # ip-api.com — приоритет (лучше всего определяет организацию и пояс для RU IP)
            if "ip-api.com" in url or "ip-api.pro" in url:
                if geo.get("status") == "success" or "query" in geo:
                    org = geo.get("org", org) or geo.get("asname", org) or org
                    provider = geo.get("isp", provider) or geo.get("asname", provider) or provider
                    asn = geo.get("as", asn) or asn
                    country = f"{geo.get('country', country.split(' (')[0] if '(' in country else country)} ({geo.get('countryCode', '')})"
                    region = geo.get("regionName", region) or region
                    city = geo.get("city", city) or city
                    timezone = geo.get("timezone", timezone) or timezone
                    if timezone != 'Неизвестно':
                        break  # Если пояс найден — выходим (он самый важный)

            # Резервные API — заполняют недостающее
            elif "ipwho.is" in url:
                if geo.get("success"):
                    org = geo.get("org", org)
                    provider = geo.get("connection", {}).get("isp", provider)
                    asn = geo.get("connection", {}).get("asn", asn)
                    country = f"{geo.get('country', country.split(' (')[0] if '(' in country else country)} ({geo.get('country_code', '')})"
                    region = geo.get("region", region)
                    city = geo.get("city", city)
                    timezone = geo.get("timezone", {}).get("name", timezone)

            elif "freeipapi" in url:
                org = geo.get("organization", org)
                provider = geo.get("isp", provider)
                asn = geo.get("asn", asn)
                country = f"{geo.get('countryName', country.split(' (')[0] if '(' in country else country)} ({geo.get('countryCode', '')})"
                region = geo.get("regionName", region)
                city = geo.get("city", city)
                timezone = geo.get("timeZone", timezone)

            elif "ipinfo.io" in url:
                if not geo.get("error"):
                    org = geo.get("company", {}).get("name", org)
                    provider = geo.get("org", "").split(' ', 1)[1] if ' ' in geo.get("org", "") else provider
                    asn = geo.get("org", "").split(' ', 1)[0] if ' ' in geo.get("org", "") else asn
                    country = geo.get("country", country.split(' (')[0] if '(' in country else country)
                    region = geo.get("region", region)
                    city = geo.get("city", city)
                    timezone = geo.get("timezone", timezone)

            elif "ipapi.co" in url:
                org = geo.get("org", org)
                provider = geo.get("asn", provider)
                asn = geo.get("asn", asn)
                country = f"{geo.get('country_name', country.split(' (')[0] if '(' in country else country)} ({geo.get('country', '')})"
                region = geo.get("region", region)
                city = geo.get("city", city)
                timezone = geo.get("timezone", timezone)

            elif "ipgeolocation" in url:
                if not geo.get("message"):
                    org = geo.get("organization", org)
                    provider = geo.get("isp", provider)
                    asn = geo.get("asn", asn)
                    country = f"{geo.get('country_name', country.split(' (')[0] if '(' in country else country)} ({geo.get('country_code2', '')})"
                    region = geo.get("state_prov", region)
                    city = geo.get("city", city)
                    timezone = geo.get("time_zone", {}).get("name", timezone)

            elif "ipwhois.app" in url:
                org = geo.get("org", org)
                provider = geo.get("isp", provider)
                asn = geo.get("asn", asn)
                country = f"{geo.get('country', country.split(' (')[0] if '(' in country else country)} ({geo.get('country_code', '')})"
                region = geo.get("region", region)
                city = geo.get("city", city)
                timezone = geo.get("timezone", timezone)

            elif "reallyfreegeoip" in url:
                org = geo.get("org", org)
                provider = geo.get("isp", provider)
                country = f"{geo.get('country_name', country.split(' (')[0] if '(' in country else country)} ({geo.get('country_code', '')})"
                region = geo.get("region", region)
                city = geo.get("city", city)
                timezone = geo.get("time_zone", timezone)

            elif "iplocation.net" in url:
                org = geo.get("org", org)
                provider = geo.get("isp", provider)
                country = f"{geo.get('country_name', country.split(' (')[0] if '(' in country else country)} ({geo.get('country_code', '')})"
                city = geo.get("city", city)
                timezone = geo.get("timezone", timezone)

        except Exception as e:
            print(f"Geo ошибка {url}: {e}")
            continue

    # Финальный fallback — если всё равно не определено
    if timezone == 'Неизвестно':
        # Для RU IP часто Europe/Moscow
        if 'Russia' in country or 'RU' in country:
            timezone = "Europe/Moscow"

    if org == 'Неизвестно':
        org = provider  # Если организация не найдена — показываем провайдера

    response = (
        f"<b>Информация о адресе {address}</b>\n\n"
        f"🌐 <b>Реальный IP:</b> {real_ip}\n"
        f"🔌 <b>Порт:</b> {port}\n\n"
        f"🏢 <b>Организация:</b> {org}\n"
        f"💎 <b>Провайдер:</b> {provider}\n"
        f"🔢 <b>ASN:</b> {asn}\n"
        f"🌍 <b>Страна:</b> {country}\n"
        f"🗺 <b>Регион:</b> {region}\n"
        f"🏙 <b>Город:</b> {city}\n"
        f"🕐 <b>Часовой пояс:</b> {timezone}"
    )

    if server_online:
        response += (
            f"\n\n<b>🎮 Сервер Minecraft Bedrock онлайн!</b>\n\n"
            f"📛 <b>Название:</b> {server_name}\n"
            f"👥 <b>Онлайн игроков:</b> {online_players}\n"
            f"🛠 <b>Ядро / Версия:</b> {core}"
        )
    else:
        response += "\n\n<b>❌ Сервер Minecraft Bedrock оффлайн или недоступен.</b>"

    bot.edit_message_text(chat_id=status_msg.chat.id, message_id=status_msg.message_id, text=response, parse_mode="HTML")

bot.infinity_polling(none_stop=True)
