from wxpusher import WxPusher
from loguru import logger
from datetime import datetime, timedelta
import requests
import random
import os
import re

city = os.getenv("CITYS")
token = os.getenv("TOKEN")
uid = os.getenv("UID")

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = str(nowtime.year) + "-" + str(nowtime.month) + "-" + str(nowtime.day) + " " + \
    str(nowtime.hour) + ":" + str(nowtime.minute) + \
    ":" + str(nowtime.second)  # 今天的日期


def random_color():
    color_code = "0123456789ABCDEF"
    color_str = ""
    for num in range(6):
        color_str += random.choice(color_code)
    return color_str


def get_music():
    kinds = ["热歌榜", "新歌榜", "飙升榜", "抖音榜", "电音榜"]
    res = requests.get(
        f"https://api.uomg.com/api/rand.music?sort={random.choice(kinds)}&format=json").json()
    music_name = res["data"]["name"]
    music_url = res["data"]["url"]
    return [music_name, music_url]


def get_weather():
    weather_dict = {}
    url = f"https://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={city}&needMoreData=true&pageNo=1&pageSize=1"
    res = requests.get(url).json()
    if res is None:
        return None
    weather = res["data"]["list"][0]
    weather_dict[city] = [weather["weather"], weather["temp"],
                          weather["low"], weather["high"]]  # 天气，温度， 最低温，最高温
    return weather_dict


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
    tmp = ""
    for k, v in get_weather().items():
        tmp += f"<b>{k}</b>\n<font color={random_color()}>天气: {v[0]}&nbsp;&nbsp;&nbsp;当前温度: {v[1]}℃&nbsp;&nbsp;&nbsp;最低温: {v[2]}℃&nbsp;&nbsp;&nbsp;最高温: {v[3]}℃</font>\n<hr>"
    tmp += f"<b>今日彩虹屁</b>\n<font color={random_color()}>{pi}</font><hr><b>今日段子</b>\n<font color={random_color()}>{duanzi}</font>\n<hr><b>今日歌曲</b>\n歌曲名: {get_music()[0]}\n<audio src={get_music()[1]} controls='controls'>\n<hr>\n"
    contents = f" 现在是&nbsp;&nbsp;<font color={random_color()}>{today}</font>&nbsp;&nbsp;<font color={random_color()}>{get_week_day()}</font>\n<hr>" + tmp

    rep = WxPusher.send_message(content=contents, uids=[uid], token=f"{token}")
    logger.info(rep["data"])

if __name__ == "__main__":
    main()
