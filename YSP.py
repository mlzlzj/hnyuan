import requests

# 获取央视频道
url = 'https://taoiptv.com/source/Yshipin.txt?token=8zlxhttq9h01ahaw'
r = requests.get(url)
with open("Yshipin.txt", "wb") as code:
    code.write(r.content)
