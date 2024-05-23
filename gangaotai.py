import os
import requests

# 获取远程直播源文件
url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/Fairy8o/IPTV/main/DIYP-v4.txt"
r = requests.get(url)

# 确保内容是字符串
content = r.content.decode('utf-8')

with open('DIYP-v4.txt', 'w', encoding='utf-8') as f:
    f.write(content)

# 打开要读取文件和需要输出的文件
input_filename = 'DIYP-v4.txt'
output_filename_hong_kong = 'hong_kong_channels.txt'
output_filename_taiwan = 'taiwan_channels.txt'

# 逐行读取需要提取包含关键字的内容
with open(input_filename, 'r', encoding='utf-8') as infile, \
        open(output_filename_hong_kong, 'w', encoding='utf-8') as out_hk, \
        open(output_filename_taiwan, 'w', encoding='utf-8') as out_tw:
    out_hk.write('港澳频道,#genre#\n')
    out_tw.write('台湾频道,#genre#\n')

    for line in infile:
        # 香港频道关键词
        if any(keyword in line for keyword in
               ["重温经典", "凤凰卫视", "凤凰资讯", "TVB翡翠", "TVB明珠", "TVB星河", "J2", "J1", "无线", "有线", "天映",
                "VIU", "探索频道", "RTHK", "HOY", "香港卫视", "美亚电影", "hoy", "ASTRO"]):
            out_hk.write(line)
        # 台湾频道关键词
        if any(keyword in line for keyword in
               ["民视", "中视", "台视", "华视", "新闻台", "動物星球", "國家地理野生", "动物频道", "东森", "龙祥",
                "公视", "三立", "大爱", "年代新闻", "人间卫视", "人間", "大立", "TVBS", "八大"]):
            out_tw.write(line)

# 合并香港频道和台湾频道文件
with open(output_filename_hong_kong, 'r', encoding='utf-8') as file_hk, \
        open(output_filename_taiwan, 'r', encoding='utf-8') as file_tw:
    hong_kong_content = file_hk.read()
    taiwan_content = file_tw.read()

# 生成合并后的文件
with open("gangaotai.txt", "w", encoding="utf-8") as output:
    output.write(hong_kong_content + '\n' + taiwan_content)  # 在两个内容之间加上换行符

# 删除临时文件
try:
    os.remove("DIYP-v4.txt")
    os.remove("hong_kong_channels.txt")
    os.remove("taiwan_channels.txt")
except FileNotFoundError:
    print("文件不存在，无法删除")

print("港澳台频道文件gangaotai.txt生成完毕！")

os.remove("hong_kong_channels.txt")
os.remove("taiwan_channels.txt")

print("港澳台频道文件gangaotai.txt生成完毕！")
