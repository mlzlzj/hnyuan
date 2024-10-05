import requests
import difflib

urls = ["https://mirror.ghproxy.com/https://raw.githubusercontent.com/wwb521/live/refs/heads/main/tv.txt"]

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
    "港台频道": ["凤凰中文", "凤凰香港", "面包台", "点掌财经", "TVBS 欢乐", "澳门莲花", "番薯台", "翡翠台", "凤凰资讯",
                 "民视", "明珠台", "香港佛陀", "有线新闻台", "TVBS 新闻", "TVB 星河", "三立都会台", "三立综合台",
                 "台视新闻", "大爱二台", "中天新闻台", "中天综合", "中视新闻", "中视菁采台", "中视经典", "非凡新闻",
                 "民视新闻", "民视台湾台", "民视第一台", "民视综艺台", "东森新闻", "亚洲新闻", "华视新闻"],
    "影视频道": ["CHC动作电影,", "CHC家庭影院", "CHC影迷电影", "黑莓电影", "家庭影院", ]
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
