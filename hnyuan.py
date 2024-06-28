import time
import os
import concurrent.futures
import requests
import re
import base64
from datetime import datetime
import threading
from queue import Queue
from pypinyin import lazy_pinyin
from bs4 import BeautifulSoup
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

url = "https://mirror.ghproxy.com/https://raw.githubusercontent.com/Fairy8o/IPTV/main/PDX-V4.txt"
r = requests.get(url)
open('DIYP-v4.txt', 'wb').write(r.content)

keywords = ['TVB 翡翠台', 'TVB 无线新闻台', 'TVB PLUS', 'TVB 黄金翡翠台''TVB 黄金华剧台', 'TVB 千禧经典台',
            'TVB 粤语片台', 'TVB 星河台', 'TVB 亚洲剧台', 'TVB 娱乐新闻台', 'TVB J2', 'TVB 华语剧台', 'HOY 资讯台',
            'HOY TV', 'HOY国际财经', 'ViuTV', '天映频道', '天映经典', 'Thrill', '星空卫视', '香港卫视', '澳亚卫视', '澳门卫视',
            '澳门资讯', '澳视澳门', 'HKC 18台', '港台电视 31', '港台电视 32', 'Now 财经台', 'Now 爆谷台',
            'Now 星影台', 'Now 新闻台', 'Now 直播台', 'Now报价台', 'Now jelli紫金国际台', 'Now华剧台', 'NowViu剧集台',
            '华丽翡翠', '翡翠台', 'J2', '明珠台', '无线新闻台', '财经资讯台', 'VIUTV6', 'VIUTV', 'TVB星河',
            'RTHK32', 'RTHK31', 'TVN', 'TVB-Plus', '凤凰中文', '凤凰资讯', '凤凰香港', '翡翠台', '星空卫视', 'TVB星河台',
            '无线娱乐新闻台', 'TVB功夫台', 'TVB娱乐新闻台', '凤凰卫视', '凤凰香港', 'TVB翡翠台', 'TVB明珠台', 'TVB无线新闻台',
            'TVB J2台', 'TVB翡翠台 4K', 'TVB J1', '星空卫视', '耀才财经台HD', '香港佛陀', '面包台', '香港卫视', '香港34台全网',
            '港台RTHK33HD', '港台RTHK34HD', '翡翠台', '无线新闻台', 'TVB Plus', '黄金翡翠台', '黄金华剧台', '千禧经典台',
            'TVB粤语片台', 'TVB亚洲剧台', 'TVB华语剧台', 'HOY TV', 'HOY资讯台', 'Viu TV', '天映频道', '天映经典', 'Thrill',
            '澳亚卫视', '澳门卫视', 'RTHK31', 'RTHK32', 'NOW新闻台', 'NOW财经台', 'NOW直播台', 'NOW爆谷台', 'NOW星影台',
            'NOW紫金国际台', 'NOW华剧台', 'NowViu剧集台', 'ViuTV', '澳视澳门', '澳视葡语', '澳门资讯', '澳门macau', '明珠台',
            '無綫新聞台', '鳳凰衛視香港台', '翡翠台', '澳视澳门', '澳视葡语', '澳门资讯', '澳门macau', ]  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
with open('DIYP-v4.txt', 'r', encoding='utf-8') as file, open('HK.txt', 'w', encoding='utf-8') as HK:
    HK.write('\n港澳频道,#genre#\n')
    for line in file:
        if re.search(pattern, line):  # 如果行中有任意关键字
            HK.write(line)  # 将该行写入输出文件

keywords = ['纬来体育', '纬来日本', '纬来电影', '天映频道', '探索亚洲', '探索频道', '探索', '台视新闻', '时尚频道',
            '年代新闻', '中天综合', '中天亚洲', '中天娱乐', '中天新闻', '中视新闻', '亚洲旅游台', '三立综合台', '三立戏剧',
            '三立台湾台', '民视新闻台', '民视台湾台', '民视第一台', '民视', '美亚电影台', '美食星球', '龙祥时代', '龙华洋片',
            '龙华戏剧', '龙华偶像', '龙华电影', '靖天卡通', '靖天国际台', '寰宇新闻台', '华艺moc', '华纳TV', '好莱坞电影台', '非凡新闻',
            '动物星球', '東森新闻', '東森戏剧', '東森电影台', '东森综合台', '东森洋片', '东森超视', '东森财经新闻', '大爱', '博斯运动II',
            '博斯网球', '博斯魅力', '博斯高球II', '博斯高球I', '八大综合台', '八大戏剧台', '八大第1台', '公视', '爱奇艺', 'WWE',
            'TVBS新闻台', 'TVBS欢乐台', 'TVBS',  'EYE戏剧', 'EYE旅游', 'ELTA综合', 'ELTA影剧', 'ELTA体育1台', 'ELTA体育2台',
            'ELTA体育3台', 'ELTA体育4台', ]  # 需要提取的关键字列表
pattern = '|'.join(keywords)  # 创建正则表达式模式，匹配任意一个关键字
with open('DIYP-v4.txt', 'r', encoding='utf-8') as file, open('TW.txt', 'w', encoding='utf-8') as TW:
    TW.write('\n台湾频道,#genre#\n')
    for line in file:
        if re.search(pattern, line):  # 如果行中有任意关键字
            TW.write(line)  # 将该行写入输出文件

# 读取要合并的香港频道和台湾频道文件
file_contents = []
file_paths = ["HK.txt", "TW.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)
# 生成合并后的文件
with open("GAT.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

print("港澳台频道文件GAT.txt生成完毕！")


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
                  'Safari/537.36 Edg/119.0.0.0'}

shengshi_names = ["长沙", "娄底", "衡阳", "常德", "邯郸", "包头", "济宁", "周口", "贵港", "南宁", "梅州", "揭阳", "濮阳", 
                  "金华", "平顶山", "安阳", "保定", "厦门", "武汉"]
pinyin_names = ["".join(lazy_pinyin(name, errors=lambda x: x)) for name in shengshi_names]
print(f'本次查询{shengshi_names}的酒店频道。')

def read_names_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        names = [name.strip() for name in content.split(',')]
    return names


# 读取省份和城市名称
provinces = read_names_from_file('provinces.txt')
cities = read_names_from_file('cities.txt')


# 判断名称是省份还是城市
def is_province(name, provinces, cities):
    return name in provinces and name not in cities


def is_city(name, provinces, cities):
    return name in cities and name not in provinces


# 定义运营商的名称和对应的组织名称
operators = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    # "中国移动": "China Mobile Communications Corporation"
}

urls = []
all_urls = []

for shengshi in shengshi_names:
    pinyin_name = "".join(lazy_pinyin(shengshi, errors=lambda x: x))
    for operator_name, org_name in operators.items():
        # 省份查询
        if is_province(shengshi, provinces, cities):
            search_txt = f'"iptv/live/zh_cn.js" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
        # 城市查询
        elif is_city(shengshi, provinces, cities):
            search_txt = f'"iptv/live/zh_cn.js" && country="CN" && city="{pinyin_name}" && org="{org_name}"'
        else:
            continue
        # 编码和构建URL
        bytes_string = search_txt.encode('utf-8')
        encoded_search_txt = base64.b64encode(bytes_string).decode('utf-8')
        url = f'https://fofa.info/result?qbase64={encoded_search_txt}'
        print(f"正在扫描 {shengshi} {operator_name}地址: ")
        print(f"{url}")
        all_urls.append(url)
        urls = all_urls  


def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    response = requests.get(url, headers=headers, timeout=15)
    page_content = response.text
    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
    urls_all = re.findall(pattern, page_content)
    urls = set(urls_all)  # 去重得到唯一的URL列表
    x_urls = []
    for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
        url = url.strip()
        ip_start_index = url.find("//") + 2
        ip_end_index = url.find(":", ip_start_index)
        ip_dot_start = url.find(".") + 1
        ip_dot_second = url.find(".", ip_dot_start) + 1
        ip_dot_three = url.find(".", ip_dot_second) + 1
        base_url = url[:ip_start_index]  # http:// or https://
        ip_address = url[ip_start_index:ip_dot_three]
        port = url[ip_end_index:]
        ip_end = "1"
        modified_ip = f"{ip_address}{ip_end}"
        x_url = f"{base_url}{modified_ip}{port}"
        x_urls.append(x_url)
    urls = set(x_urls)  # 去重得到唯一的URL列表

    valid_urls = []
    # 多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls:
            url = url.strip()
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)

    for url in valid_urls:
        print(url)

    # 遍历网址列表，获取JSON文件并解析
    for url in valid_urls:
        try:
            # 发送GET请求获取JSON文件，设置超时时间为0.5秒
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_port = url[ip_start_index:ip_end_index + 5]  # 这里获取ip地址和端口
            print(f"获取到有效的酒店源IP地址：{ip_port}")
            response = requests.get(url, timeout=0.5)
            json_data = response.json()

            try:
                # 解析JSON文件，获取name和url字段
                for item in json_data['data']:
                    if isinstance(item, dict):
                        name = item.get('name')
                        chid = str(item.get('chid')).zfill(4)  # 补全 chid 为四位数
                        srcid = item.get('srcid')
                        # 替换频道名称中的特定字符串
                        name = name.replace("中央", "CCTV")
                        name = name.replace("高清", "")
                        name = name.replace("超清", "")
                        name = name.replace("HD", "")
                        name = name.replace("标清", "")
                        name = name.replace("超高", "")
                        name = name.replace("频道", "")
                        name = name.replace("-", "")
                        name = name.replace(" ", "")
                        name = name.replace("PLUS", "+")
                        name = name.replace("＋", "+")
                        name = name.replace("(", "")
                        name = name.replace(")", "")
                        name = name.replace("L", "")
                        name = name.replace("CMIPTV", "")
                        name = name.replace("cctv", "CCTV")
                        name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                        name = name.replace("CCTV1综合", "CCTV1")
                        name = name.replace("CCTV2财经", "CCTV2")
                        name = name.replace("CCTV3综艺", "CCTV3")
                        name = name.replace("CCTV4国际", "CCTV4")
                        name = name.replace("CCTV4中文国际", "CCTV4")
                        name = name.replace("CCTV4欧洲", "CCTV4")
                        name = name.replace("CCTV5体育", "CCTV5")
                        name = name.replace("CCTV5+体育", "CCTV5+")
                        name = name.replace("CCTV6电影", "CCTV6")
                        name = name.replace("CCTV7军事", "CCTV7")
                        name = name.replace("CCTV7军农", "CCTV7")
                        name = name.replace("CCTV7农业", "CCTV7")
                        name = name.replace("CCTV7国防军事", "CCTV7")
                        name = name.replace("CCTV8电视剧", "CCTV8")
                        name = name.replace("CCTV8纪录", "CCTV9")
                        name = name.replace("CCTV9记录", "CCTV9")
                        name = name.replace("CCTV9纪录", "CCTV9")
                        name = name.replace("CCTV10科教", "CCTV10")
                        name = name.replace("CCTV11戏曲", "CCTV11")
                        name = name.replace("CCTV12社会与法", "CCTV12")
                        name = name.replace("CCTV13新闻", "CCTV13")
                        name = name.replace("CCTV新闻", "CCTV13")
                        name = name.replace("CCTV14少儿", "CCTV14")
                        name = name.replace("央视14少儿", "CCTV14")
                        name = name.replace("CCTV少儿超", "CCTV14")
                        name = name.replace("CCTV15音乐", "CCTV15")
                        name = name.replace("CCTV音乐", "CCTV15")
                        name = name.replace("CCTV16奥林匹克", "CCTV16")
                        name = name.replace("CCTV17农业农村", "CCTV17")
                        name = name.replace("CCTV17军农", "CCTV17")
                        name = name.replace("CCTV17农业", "CCTV17")
                        name = name.replace("CCTV5+体育赛视", "CCTV5+")
                        name = name.replace("CCTV5+赛视", "CCTV5+")
                        name = name.replace("CCTV5+体育赛事", "CCTV5+")
                        name = name.replace("CCTV5+赛事", "CCTV5+")
                        name = name.replace("CCTV5+体育", "CCTV5+")
                        name = name.replace("CCTV5赛事", "CCTV5+")
                        name = name.replace("凤凰中文台", "凤凰中文")
                        name = name.replace("凤凰资讯台", "凤凰资讯")
                        name = name.replace("CCTV4K测试）", "CCTV4")
                        name = name.replace("CCTV164K", "CCTV16")
                        name = name.replace("上海东方卫视", "上海卫视")
                        name = name.replace("东方卫视", "上海卫视")
                        name = name.replace("内蒙卫视", "内蒙古卫视")
                        name = name.replace("福建东南卫视", "东南卫视")
                        name = name.replace("广东南方卫视", "南方卫视")
                        name = name.replace("金鹰卡通卫视", "金鹰卡通")
                        name = name.replace("湖南金鹰卡通", "金鹰卡通")
                        name = name.replace("炫动卡通", "哈哈炫动")
                        name = name.replace("卡酷卡通", "卡酷少儿")
                        name = name.replace("卡酷动画", "卡酷少儿")
                        name = name.replace("BRTVKAKU少儿", "卡酷少儿")
                        name = name.replace("优曼卡通", "优漫卡通")
                        name = name.replace("优曼卡通", "优漫卡通")
                        name = name.replace("嘉佳卡通", "佳嘉卡通")
                        name = name.replace("世界地理", "地理世界")
                        name = name.replace("CCTV世界地理", "地理世界")
                        name = name.replace("BTV北京卫视", "北京卫视")
                        name = name.replace("BTV冬奥纪实", "冬奥纪实")
                        name = name.replace("东奥纪实", "冬奥纪实")
                        name = name.replace("卫视台", "卫视")
                        name = name.replace("湖南电视台", "湖南卫视")
                        name = name.replace("2金鹰卡通", "金鹰卡通")
                        name = name.replace("湖南教育台", "湖南教育")
                        name = name.replace("湖南金鹰纪实", "金鹰纪实")
                        name = name.replace("少儿科教", "少儿")
                        name = name.replace("影视剧", "影视")

                        if name and chid and srcid:
                            # 格式化 URL
                            channel_url = ('{name},http://{ip_port}/tsfile/live/{chid}_{'
                                           'srcid}.m3u8').format(
                                name=name,
                                ip_port=ip_port,
                                chid=chid,
                                srcid=srcid
                            )
                            results.append(channel_url)

            except:
                continue
        except:
            continue

channels = []

for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))
# 去重得到唯一的URL列表
results = set(results)
results = sorted(results)

with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)
# 写入频道列表文件iptv.txt
print(f"共获取到频道{len(channels)}个，频道列表文件iptv.txt生成完毕！")

import eventlet

eventlet.monkey_patch()
# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []

channels = []
error_channels = []

with open("iptv.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            # if '卫视' in channel_name or 'CCTV' in channel_name:
            channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url, timeout=1).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url, timeout=1).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                download_speed = file_size / response_time / 1024
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                print(f"\n检测频道: {channel_name},{channel_url}\n下载速度：{download_speed:.3f} kB/s，标准化后的速率：{normalized_speed:.3f} MB/s")

                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 10
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()

# 添加下载任务到队列
for channel in channels:
    task_queue.put(channel)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 对频道进行排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))

# 将结果写入文件
with open("iptv_results.txt", 'w', encoding='utf-8') as file:
    for result in results:
        channel_name, channel_url, speed = result
        file.write(f"{channel_name},{channel_url},  {speed}\n")
#
# with open("iptv_speed.txt", 'w', encoding='utf-8') as file:
#     for result in results:
#         channel_name, channel_url, speed = result
#         file.write(f"{channel_name},{channel_url}\n")

result_counter = 10  # 每个频道需要保留的个数

with open("iptv_list.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, _ = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('\n卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, _ = result
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('\n港澳影视,#genre#\n')
    for result in results:
        channel_name, channel_url, _ = result
        if '凤凰' in channel_name or '翡翠' in channel_name or '明珠' in channel_name or '本港' in channel_name or '星河' in channel_name \
            or '重温经典' in channel_name or '影迷电影' in channel_name or '凤凰' in channel_name or '家庭影院' in channel_name \
            or '动作电影' in channel_name or 'CHC' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1            
    channel_counters = {}
    file.write('\n湖南频道,#genre#\n')
    for result in results:
        channel_name, channel_url, _ = result
        if '湖南' in channel_name or '长沙' in channel_name or '金鹰' in channel_name or '先锋乒羽' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('\n其他频道,#genre#\n')
    for result in results:
        channel_name, channel_url, _ = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and 'CHC' not in channel_name and '湖南' not in \
                channel_name and '长沙' not in channel_name and '金鹰' not in channel_name and '先锋乒羽' not in \
                channel_name and '下载速率' not in channel_name and '测试' not in channel_name and '重温经典' not in \
                channel_name and '影迷电影' not in channel_name and '家庭影院' not in channel_name and '动作电影' not in \
                channel_name and '购' not in channel_name and '凤凰' not in channel_name and '翡翠' not in channel_name \
                and '明珠' not in channel_name and '本港' not in channel_name and '星河' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
# 合并所有的txt文件
file_contents = []
file_paths = ["YD-IPTV.txt", "iptv_list.txt", "GAT.txt", "zdy.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的txt文件
with open("iptv_list.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))
    # 写入更新日期时间
    now = datetime.now()
    output.write(f"更新时间,#genre#\n")
    output.write(f"{now.strftime("%Y-%m-%d %H:%M:%S")},url\n")
os.remove("iptv.txt")
os.remove("DIYP-v4.txt")
os.remove("HK.txt")
os.remove("TW.txt")
os.remove("GAT.txt")
os.remove("iptv_results.txt")

print("频道分类完成已写入iptv_list.txt文件。")


# 将.txt文件转换为.m3u文件
def txt_to_m3u(input_file, output_file):
    # 读取txt文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 打开m3u文件并写入内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')

        # 初始化genre变量
        genre = ''

        # 遍历txt文件内容
        for line in lines:
            line = line.strip()
            if "," in line:  # 防止文件里面缺失“,”号报错
                # if line:
                # 检查是否是genre行
                channel_name, channel_url = line.split(',', 1)
                if channel_url == '#genre#':
                    genre = channel_name
                    print(genre)
                else:
                    # 将频道信息写入m3u文件
                    f.write(f'#EXTINF:-1 group-title="{genre}",{channel_name}\n')
                    f.write(f'{channel_url}\n')


txt_to_m3u('iptv_list.txt', 'iptv_list.m3u')
