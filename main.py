import os
import re
import random
import requests
from loguru import logger
from wxpusher import WxPusher
from lunardate import LunarDate
from datetime import datetime, timedelta, date

logger.add("wxpusher.log", rotation="14 days")

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = str(nowtime.year) + "-" + str(nowtime.month) + "-" + str(nowtime.day) + " " + str(nowtime.hour) + ":" + str(nowtime.minute) + ":" + str(nowtime.second)  # 今天的日期

city = os.getenv("CITYS", "")
wether_key = os.getenv("Wether_KEY", "")
token = os.getenv("TOKEN", "")
uid = os.getenv("UID", [""])
day = os.getenv("DAY", "")
bao = os.getenv("BAO", "")
birthday = os.getenv("BTHDAY", "")


def random_color():
    color_code = "0123456789ABCDEF"
    color_str = ""
    for num in range(6):
        color_str += random.choice(color_code)
    return color_str

# 阳历生日倒计时
def get_birthday_gongli_until():
    today = date.today()
    birth_date = date(int(birthday.split('-')[0]), int(birthday.split('-')[1]), int(birthday.split('-')[2]))
    next_birthday = date(today.year, birth_date.month, birth_date.day)
    if next_birthday < today:
        next_birthday = date(today.year + 1, birth_date.month, birth_date.day)
    days_until_birthday = (next_birthday - today).days

    return days_until_birthday

# 农历生日倒计时
def get_birthday_nongli_until():
    import datetime
    year, month, days = int(bao.split('-')[0]), int(bao.split('-')[1]), int(bao.split('-')[2])
    lunar_date = LunarDate(year, month, days).toSolarDate()  # 农历 转阳历
    now = datetime.date(nowtime.year, nowtime.month, nowtime.day)
    if lunar_date > now:
        return (lunar_date-now).days
    elif lunar_date == now:
        return 0
    else:
        return (datetime.date(nowtime.year+1, nowtime.month, nowtime.day)- lunar_date).days

# 纪念日, 生日
def get_anniversary():
    now = datetime(nowtime.year, nowtime.month, nowtime.day)
    count_day = (now - datetime.strptime(day, '%Y-%m-%d')).days
    myself,bigboy = get_birthday_gongli_until(), get_birthday_nongli_until()
    return count_day, myself, bigboy

def get_music():
    kinds = ["热歌榜", "新歌榜", "飙升榜", "抖音榜", "电音榜"]
    res = requests.get(
        f"https://api.uomg.com/api/rand.music?sort={random.choice(kinds)}&format=json").json()
    music_name = res["data"]["name"]
    music_url = res["data"]["url"]
    return [music_name, music_url]


def get_weather():
    weather_dict = {}
    url = f"http://apis.juhe.cn/simpleWeather/query?city={city}&key={wether_key}"
    res = requests.get(url).json()["result"]
    if res is None:
        return None
    weather_dict['city'] = res["city"]
    weather_dict['temperature'] = res['realtime']['temperature']
    weather_dict['humidity'] = res['realtime']['humidity'] # 湿度
    weather_dict['info'] = res['realtime']['info'] # 天气状况

    return weather_dict # {'city': '北京', 'temperature': '33', 'humidity': '45', 'info': '阴'}


def get_week_day():
    week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    week_day = week_list[datetime.date(
        datetime.strptime(today, "%Y-%m-%d %H:%M:%S")).weekday()]
    return week_day


def get_caihongpi():
    pi = requests.get("https://api.shadiao.pro/chp").json()["data"]["text"]
    duanzi_html = requests.get(
        "http://www.yduanzi.com/?utm_source=https://shadiao.pro").text
    kaishi = re.search("<span id='duanzi-text'>", duanzi_html).span()[1]
    end = re.search("</span>", duanzi_html).span()[0]
    duanzi = duanzi_html[kaishi:end]
    return pi, duanzi


def main():
    pi, duanzi = get_caihongpi()
    weather = get_weather()
    count_day, myself, bigboy = get_anniversary()
    tmp = ""
    tmp += f"<b>今日份计时器</b>\n和大宝在一起已经 {count_day} 天啦 ❤️\n距离我的生日还有 <font color={random_color()}>{myself}</font> 天 🎂\n距离大宝的生日还有 <font color={random_color()}>{bigboy}</font> 天 🎂\n<hr>"
    tmp += f"<b>今日天气预报</b>\n{weather['city']} <font color={random_color()}>天气: {weather['info']}&nbsp;&nbsp;&nbsp;当前温度: {weather['temperature']}℃</font>\n<hr>"
    tmp += f"<b>今日份彩虹屁</b>\n<font color={random_color()}>{pi}</font><hr>"
    tmp += f"<b>今日份段子</b>\n<font color={random_color()}>{duanzi}</font>\n<hr>"
    tmp += f"<b>今日份歌曲</b>\n歌曲名: {get_music()[0]}\n<audio src={get_music()[1]} controls autoplay loop></div>"
    contents = f"<div style='background-repeat: no-repeat; background-size: cover; background-attachment: fixed; background-position-y: center;background-image: url(https://img2.baidu.com/it/u=1550919657,3261887531&fm=253&fmt=auto&app=120&f=JPEG?w=800&h=1422)'>现在是&nbsp;&nbsp;<font color={random_color()}>{today}</font>&nbsp;&nbsp;<font color={random_color()}>{get_week_day()}</font>\n<hr>" + tmp

    rep = WxPusher.send_message(content=contents, uids=uid, token=f"{token}")
    logger.info(rep["data"])

if __name__ == "__main__":
    main()