from cachetools import cached, TTLCache
import requests
from datetime import datetime, timedelta
import pytz
from main import OPENWEATHER_KEY
today_forecast_cache = TTLCache(maxsize=10, ttl=2300)
@cached(today_forecast_cache)
def get_daily_forecast():
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params = {
            "q": "Vladivostok",
            "appid": OPENWEATHER_KEY,
            "units": "metric",
            "lang": "ru"
        },
    )

    data = response.json()
    forecast_list = data['list']
    utc_now = datetime.now(pytz.utc)
    vdk_timezone = pytz.timezone('Asia/Vladivostok')
    vdk_now = utc_now.astimezone(vdk_timezone)

    today_start_vdk = vdk_now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end_vdk = today_start_vdk + timedelta(days=1)
    today_forecasts = []
    for forecast in forecast_list:
        forecast_time_naive = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        forecast_time_utc = pytz.utc.localize(forecast_time_naive)
        forecast_time_vdk = forecast_time_utc.astimezone(vdk_timezone)
        forecast['vdk_time'] = forecast_time_vdk
        if today_start_vdk <= forecast_time_vdk < today_end_vdk:
            today_forecasts.append(forecast)
    if not today_forecasts:
        today_forecasts = forecast_list[:4]
        warning = f"Внимание: прогноз на сегодня не полный, показан ближайший.\n\n"
    else:
        warning = ''

    temp_list = []
    feel_list = []
    conditions = []
    wind_list = []
    time_forecasts = []
    for forecast in today_forecasts:
        time = forecast['vdk_time']
        temp = forecast['main']['temp']
        feels_like = forecast['main']['feels_like']
        condition = forecast['weather'][0]['description']
        wind = forecast['wind']['speed']

        temp_list.append(temp)
        conditions.append(condition)
        wind_list.append(wind)
        feel_list.append(feels_like)

        hour = int(time.hour)
        time_str = f"{hour}:00"
        time_forecasts.append({
            'time': time_str,
            'temp': temp,
            'feels_like': feels_like,
            'condition': condition,
            'wind': wind
        })

    has_rain = any('дождь' in cond.lower() or 'ливень' in cond.lower() for cond in conditions)
    has_snow = any('снег' in cond.lower() for cond in conditions)
    max_wind = max(wind_list)
    avg_temp = sum(temp_list) / len(temp_list)
    avg_feel_temp = sum(feel_list) / len(feel_list)
    message = warning
    message = f"🌤️ Прогноз погоды во Владивостоке на сегодня ({vdk_now.day}.{vdk_now.month}):\n\n"
    message += f"📊 Основные показатели:\n"
    message += f"• Температура: от {min(temp_list):.0f}°C до {max(temp_list):.0f}°C\n"
    message += f"• Средняя температура: {avg_temp:.0f}°C (по ощущениям {avg_feel_temp:.0f}°C)\n"
    message += f"• Ветер: до {max_wind} м/с\n"

    if has_rain:
        message += f"• Ожидается дождь\n"
    elif has_snow:
        message += f"• Ожидается снег\n"
    else:
        mx = -1000
        major_condition = conditions[0]
        for i in range(len(conditions)):
            if conditions.count(conditions[i]) > mx:
                mx = conditions.count(conditions[i])
                major_condition = conditions[i]

        message += f'• Преимущественно: {major_condition}\n'

    message += f"\n🕒 Погода в течение дня:\n"


    for tf in time_forecasts:
        hour = int(tf['time'].split(':')[0])

        if 6 <= hour < 12:
            time_of_day = "Утро"
        elif 12 <= hour < 18:
            time_of_day = "День"
        elif 18 <= hour < 23:
            time_of_day = "Вечер"
        else:
            time_of_day = "Ночь"

        message += f"• {time_of_day} ({tf['time']}): {tf['temp']:.0f}°C, {tf['condition']}"
        if tf['wind'] > 8:
            message += f", ветрено ({tf['wind']} м/с)"
        elif tf['wind'] <= 5:
            message += f', слабый ветер ({tf['wind']} м/с)'
        elif 5 < tf['wind'] <= 8:
            message += f', умеренный ветер ({tf['wind']} м/с)'
        message += "\n"

    message += f'\n👔 Рекомендации по одежде:\n'

    if avg_temp >= 20:
        message += 'Легкая одежда. Футболка, шорты из льна или хлопка.\n'
    elif 15 <= avg_temp < 20:
        message += 'Легкая одежда. Футболка или рубашка. На вечер можно взять ветровку\n'
    elif 10 <= avg_temp < 15:
        message += 'Лонгслив + толстовка/кофта или легкая куртка.\n'
    elif 5 <= avg_temp < 10:
        message += 'Тренч, куртка с подкладкой, легкое пальто или бомбер.\n'
    elif -5 <= avg_temp < 5:
        message += ('Легкий пуховик, утепленное пальто или дафлкот. '
                    'Обувь на высокой подошве\n')
    elif -15 <= avg_temp < -5:
        message += ('Зимняя куртка или зимнее пальто. '
                    'Стоит надеть термобелье и не забыть шапку и перчатки. Утепленная непромокаемая обувь.\n')
    elif avg_temp < -15:
        message += ('Максимальное утепление. Зимний пуховик с высоким индексом набивки. '
                    'Обязательно термобелье, теплая шапка и утепленная непромокаемая обувь\n')

    if has_rain:
        message += f"Не забудь взять зонт и надеть дождевик и непромокаемую обувь\n"
    if max_wind > 7:
        message += 'Наденьте ветрозащитный слой.\n'

    # print(message)
    return message
ai_forecast_cache = TTLCache(maxsize=10, ttl=2300)
@cached(ai_forecast_cache)
def ai_weather():
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "q": "Vladivostok",
            "appid": OPENWEATHER_KEY,
            "units": "metric",
            "lang": "ru"
        },
    )

    data = response.json()
    forecast_list = data['list']
    utc_now = datetime.now(pytz.utc)
    vdk_timezone = pytz.timezone('Asia/Vladivostok')
    vdk_now = utc_now.astimezone(vdk_timezone)

    today_start_vdk = vdk_now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end_vdk = today_start_vdk.replace(day=today_start_vdk.day + 1)
    today_forecasts = []
    for forecast in forecast_list:
        forecast_time_naive = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        forecast_time_utc = pytz.utc.localize(forecast_time_naive)
        forecast_time_vdk = forecast_time_utc.astimezone(vdk_timezone)
        forecast['vdk_time'] = forecast_time_vdk
        if today_start_vdk <= forecast_time_vdk < today_end_vdk:
            today_forecasts.append(forecast)
    if not today_forecasts:
        today_forecasts = forecast_list[:4]
        warning = f"Внимание: прогноз на сегодня не полный, показан ближайший.\n\n"
    else:
        warning = ""

    temp_list = []
    feel_list = []
    conditions = []
    wind_list = []
    time_forecasts = []
    for forecast in today_forecasts:
        time = forecast['vdk_time']
        temp = forecast['main']['temp']
        feels_like = forecast['main']['feels_like']
        condition = forecast['weather'][0]['description']
        wind = forecast['wind']['speed']

        temp_list.append(temp)
        conditions.append(condition)
        wind_list.append(wind)
        feel_list.append(feels_like)

        hour = int(time.hour)
        time_str = f"{hour}:00"
        time_forecasts.append({
            'time': time_str,
            'temp': temp,
            'feels_like': feels_like,
            'condition': condition,
            'wind': wind
        })

    has_rain = any('дождь' in cond.lower() or 'ливень' in cond.lower() for cond in conditions)
    has_snow = any('снег' in cond.lower() for cond in conditions)
    max_wind = max(wind_list)
    avg_temp = sum(temp_list) / len(temp_list)
    avg_feel_temp = sum(feel_list) / len(feel_list)
    message = warning
    message = f"🌤️ Прогноз погоды во Владивостоке на день:\n\n"
    message += f"📊 Основные показатели:\n"
    message += f"• Температура: от {min(temp_list):.0f}°C до {max(temp_list):.0f}°C\n"
    message += f"• Средняя температура: {avg_temp:.0f}°C (по ощущениям {avg_feel_temp:.0f}°C)\n"
    message += f"• Ветер: до {max_wind} м/с\n"

    if has_rain:
        message += f"• Ожидается дождь\n"
    elif has_snow:
        message += f"• Ожидается снег\n"
    else:
        mx = -1000
        major_condition = conditions[0]
        for i in range(len(conditions)):
            if conditions.count(conditions[i]) > mx:
                mx = conditions.count(conditions[i])
                major_condition = conditions[i]

        message += f'• Преимущественно: {major_condition}\n'
    return message

tomorrow_forecast_cache = TTLCache(maxsize=10, ttl=2300)
@cached(tomorrow_forecast_cache)
def get_tomorrow_forecast():
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params = {
            "q": "Vladivostok",
            "appid": OPENWEATHER_KEY,
            "units": "metric",
            "lang": "ru"
        },
    )

    data = response.json()
    forecast_list = data['list']
    utc_now = datetime.now(pytz.utc)
    vdk_timezone = pytz.timezone('Asia/Vladivostok')
    vdk_now = utc_now.astimezone(vdk_timezone)

    tomorrow_start_vdk = vdk_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_end_vdk = tomorrow_start_vdk + timedelta(days=1)
    tomorrow_forecasts = []
    for forecast in forecast_list:
        forecast_time_naive = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
        forecast_time_utc = pytz.utc.localize(forecast_time_naive)
        forecast_time_vdk = forecast_time_utc.astimezone(vdk_timezone)
        forecast['vdk_time'] = forecast_time_vdk
        if tomorrow_start_vdk <= forecast_time_vdk < tomorrow_end_vdk:
            tomorrow_forecasts.append(forecast)
    if not tomorrow_forecasts:
        tomorrow_forecasts = forecast_list[:4]
        warning = f"Внимание: прогноз на сегодня не полный, показан ближайший.\n\n"
    else:
        warning = ''
    temp_list = []
    feel_list = []
    conditions = []
    wind_list = []
    time_forecasts = []
    for forecast in tomorrow_forecasts:
        time = forecast['vdk_time']
        temp = forecast['main']['temp']
        feels_like = forecast['main']['feels_like']
        condition = forecast['weather'][0]['description']
        wind = forecast['wind']['speed']

        temp_list.append(temp)
        conditions.append(condition)
        wind_list.append(wind)
        feel_list.append(feels_like)

        hour = int(time.hour)
        time_str = f"{hour}:00"
        time_forecasts.append({
            'time': time_str,
            'temp': temp,
            'feels_like': feels_like,
            'condition': condition,
            'wind': wind
        })

    has_rain = any('дождь' in cond.lower() or 'ливень' in cond.lower() for cond in conditions)
    has_snow = any('снег' in cond.lower() for cond in conditions)
    max_wind = max(wind_list)
    avg_temp = sum(temp_list) / len(temp_list)
    avg_feel_temp = sum(feel_list) / len(feel_list)
    message = warning
    message += f"🌤️ Прогноз погоды во Владивостоке на завтра ({(vdk_now + timedelta(days=1)).day}.{(vdk_now + timedelta(days=1)).month}):\n\n"
    message += f"📊 Основные показатели:\n"
    message += f"• Температура: от {min(temp_list):.0f}°C до {max(temp_list):.0f}°C\n"
    message += f"• Средняя температура: {avg_temp:.0f}°C (по ощущениям {avg_feel_temp:.0f}°C)\n"
    message += f"• Ветер: до {max_wind} м/с\n"

    if has_rain:
        message += f"• Ожидаются дождь\n"
    elif has_snow:
        message += f"• Ожидается снег\n"
    else:
        mx = -1000
        major_condition = conditions[0]
        for i in range(len(conditions)):
            if conditions.count(conditions[i]) > mx:
                mx = conditions.count(conditions[i])
                major_condition = conditions[i]

        message += f'• Преимущественно: {major_condition}\n'

    message += f"\n🕒 Погода в течение дня:\n"


    for tf in time_forecasts:
        hour = int(tf['time'].split(':')[0])

        if 6 <= hour < 12:
            time_of_day = "Утро"
        elif 12 <= hour < 18:
            time_of_day = "День"
        elif 18 <= hour < 23:
            time_of_day = "Вечер"
        else:
            time_of_day = "Ночь"

        message += f"• {time_of_day} ({tf['time']}): {tf['temp']:.0f}°C, {tf['condition']}"
        if tf['wind'] > 8:
            message += f", ветрено ({tf['wind']} м/с)"
        elif tf['wind'] <= 5:
            message += f', слабый ветер ({tf['wind']} м/с)'
        elif 5 < tf['wind'] <= 8:
            message += f', умеренный ветер ({tf['wind']} м/с)'
        message += "\n"

    message += f'👔 Рекомендации по одежде:\n'

    if avg_temp >= 20:
        message += 'Легкая одежда. Футболка, шорты из льна или хлопка.\n'
    elif 15 <= avg_temp < 20:
        message += 'Легкая одежда. Футболка или рубашка. На вечер можно взять ветровку\n'
    elif 10 <= avg_temp < 15:
        message += 'Лонгслив + толстовка/кофта или легкая куртка.\n'
    elif 5 <= avg_temp < 10:
        message += 'Тренч, куртка с подкладкой, легкое пальто или бомбер. Шарф\n'
    elif -5 <= avg_temp < 5:
        message += ('Легкий пуховик, утепленное пальто или дафлкот. '
                    'Обувь на высокой подошве\n')
    elif -15 <= avg_temp < -5:
        message += ('Зимняя куртка или зимнее пальто. '
                    'Стоит надеть термобелье и не забыть шапку и перчатки. Утепленная непромокаемая обувь.\n')
    elif avg_temp < -15:
        message += ('Максимальное утепление. Зимний пуховик с высоким индексом набивки. '
                    'Обязательно термобелье, теплая шапка и утепленная непромокаемая обувь\n')

    if has_rain:
        message += f"Не забудь взять зонт и надеть дождевик и непромокаемую обувь\n"
    if max_wind > 7:
        message += 'Наденьте ветрозащитный слой.\n'

    # print(message)
    return message

# get_daily_forecast()
# get_tomorrow_forecast()