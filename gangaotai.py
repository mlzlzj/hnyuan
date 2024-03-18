import os
import requests

#  获取远程直播源文件
url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/Fairy8o/IPTV/main/DIYP-v4.txt"
r = requests.get(url)
open('DIYP-v4.txt', 'wb').write(r.content)

# 打开要读取文件和需要输出的文件
input_filename = 'DIYP-v4.txt'
output_filename_hong_kong = 'hong_kong_channels.txt'
output_filename_taiwan = 'taiwan_channels.txt'

with open(input_filename, 'r', encoding='utf-8') as infile, \
        open(output_filename_hong_kong, 'w', encoding='utf-8') as out_hk, \
        open(output_filename_taiwan, 'w', encoding='utf-8') as out_tw:
    out_hk.write('港澳频道,#genre#\n')
    out_tw.write('台湾频道,#genre#\n')

    # 逐行读取需要提取包含关键字的内容
    for line in infile:
        if "凤凰卫视" in line or "凤凰资讯" in line or "TVB翡翠" in line or "TVB明珠" in line or "TVB星河" in line \
                or "J2" in line or "无线" in line or "有线" in line or "天映" in line or "VIU" in line \
                or "RTHK" in line or "HOY" in line or "香港卫视" in line or "澳亚" in line or "澳视" in line:
            out_hk.write(line)  # 写入香港频道文件
        if "民视" in line or "中视" in line or "台视" in line or "华视" in line or "新闻台" in line \
                or "东森" in line or "龙祥" in line or "公视" in line or "三立" in line or "大爱" in line \
                or "年代" in line or "人间卫视" in line or "人間" in line or "大立" in line:
            out_tw.write(line)  # 写入台湾频道文件

# 合并香港频道和台湾频道文件
file_contents = []
file_paths = ["hong_kong_channels.txt", "taiwan_channels.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 生成合并后的文件
with open("gangaotai.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

os.remove("DIYP-v4.txt")
os.remove("hong_kong_channels.txt")
os.remove("taiwan_channels.txt")

print("港澳台频道文件gangaotai.txt生成完毕！")
