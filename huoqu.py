import requests
import difflib

urls = [
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/frxz751113/IPTVzb1/refs/heads/main/1014%E7%BD%91%E7%BB%9C%E6%94%B6%E9%9B%86.txt"]

final = []


def txt_decode(file_content):
    result = []
    for line in file_content.split("\n"):
        line = line.strip()
        if "#genre#" not in line and line != "":
            r = line.split(",")
            result.append({
                "name": r[0],
                "url": r[1]
            })
    return result


def m3u8_decode(file_content):
    tv_name = ""
    result = []
    for file_line in file_content.split("\n"):
        file_line = file_line.strip()
        if file_line.startswith("#EXTINF"):
            tv_name = file_line.split(",")[-1]
        elif file_line and not file_line.startswith("#"):
            result.append({
                "name": tv_name,
                "url": file_line
            })
        # tv_name = ""
    return result


def isSimilar(str1, str2, threshold=0.8):
    ratio = difflib.SequenceMatcher(None, str1, str2).ratio()
    return ratio >= threshold


tvData = {
    "港台频道": ["AMC电影台", "EYETV戏剧台", "八大戏剧台", "榜单电影台", "采昌影剧台", "电影[768p]", "东森电影台",
                 "东森戏剧台", "公视戏剧台", "好莱坞电影台", "金马影院", "靖天戏剧台",
                 "靖洋戏剧台", "句容影院", "开心影院", "龙华电影台", "龙华戏剧台", "美亚电影台", "民视影剧台",
                 "三立戏剧台", "纬来电影台", "星卫电影台", "影迷数位电影台", "BLOOMBERG", "CNBC",
                 "CinemaWorld", "Dbox", "HISTORY", "HakkaTV", "LISTENONSPOTIFY", "MTV", "TVB浜𣱝床鍓у彴", "TVB翡翠台",
                 "TVB华丽台", "TVB星河", "TVB星河国语", "TVB星河台", "TVB1",
                 "TVBDrama", "TVBE", "TVBJ1", "TVBRICS", "TVBS欢乐台", "TVBS新闻台", "TVBS", "TVBSNews", "TVBSUPERFREE",
                 "TVBS", "TVBplus", "八大第一台", "八大精彩台", "八大综合台",
                 "博斯运动1", "大爱1台", "大爱2台", "大爱", "大立电视", "东森", "东森财经", "东森超视", "东森新闻台",
                 "东森中", "东森综合台", "动物星球1", "动物星球", "番薯111", "中天",
                 "番薯", "番薯台", "翡翠台", "凤凰卫视", "凤凰卫视香港台", "凤凰卫视中文台", "凤凰卫视资讯台",
                 "凤凰香港", "凤凰中文", "凤凰资讯台", "公视", "互动英语", "华视", "中天新闻台",
                 "华视新闻台", "寰宇财经", "寰宇新闻台", "靖天", "靖天国际", "靖天卡通台", "靖天日本台", "靖天育乐",
                 "靖天资讯台", "靖天综合台", "龙华卡通台", "龙华偶像台", "民视", "中天亚洲",
                 "民视第一台", "民视旅游", "民视台湾台", "民视新闻台", "民视综艺台", "nhkworld", "三立", "三立都会",
                 "三立台湾台", "三立新闻台", "三立综合台", "台视", "台视财经", "中天亚洲",
                 "探案台", "探索亚洲", "纬来精彩台", "纬来体育", "无线翡翠", "无线华丽", "无线新闻台", "无线直播",
                 "亚洲旅游", "中华小当家", "中视", "中视菁采台", "中视经典台", "中视新闻台",
                 "中天娱乐", "中天综合台", "猪哥亮音乐秀"],
    # "影视频道": ["CHC动作电影,", "CHC家庭影院", "CHC影迷电影", "黑莓电影", "家庭影院", ]
}

allTvs = []

for url in urls:
    # global allTVs
    r = requests.get(url)
    r.encoding = "utf-8"
    allTvs.extend(txt_decode(r.text))

for key, value in tvData.items():
    final.append(f"{key},#genre#")
    for name in value:
        haveOne = False
        for tv in allTvs:
            if isSimilar(name, tv["name"]):
                final.append(f"{name},{tv['url']}")
                haveOne = True
        if not haveOne:
            final.append(f"{name},none")

# 打印频道列表内容
for item in final:
    print(item)

with open("./huoqu.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(final))
