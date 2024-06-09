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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
                  'Safari/537.36 Edg/119.0.0.0'}
urls = []
shengshi_names = ["长沙", "娄底", "衡阳", "常德", "南宁", "湖南", "山东", "江西"]
pinyin_names = ["".join(lazy_pinyin(name, errors=lambda x: x)) for name in shengshi_names]
print(f'本次查询{shengshi_names}的酒店频道。')

# 省直辖市自治区名称列表
provinces = ["湖南", "湖北", "广东", "广西", "江西", "江苏", "浙江", "安徽", "河南", "四川", "河北", "山西",
             "福建", "山东", "北京", "天津", "上海", "重庆", "广西壮族自治区", "贵州", "云南", "陕西", "海南",
             "辽宁", "吉林", "黑龙江", "甘肃", "青海", "内蒙古自治区", "宁夏回族自治区"]

# 城市名称列表
cities = ["长沙", "娄底", "衡阳", "常德", "株洲", "湘潭", "邵阳", "张家界", "益阳", "郴州", "永州", "怀化", "岳阳",
          "广州", "韶关", "深圳", "珠海", "汕头", "佛山", "江门", "湛江", "茂名", "肇庆", "惠州", "梅州", "汕尾",
          "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮",
          "南宁", "贵港", "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "玉林", "百色", "贺州", "河池", "来宾",
          "崇左",
          "武汉", "黄石", "十堰", "宜昌", "襄阳", "鄂州", "荆门", "孝感", "荆州", "黄冈", "咸宁", "随州",
          "南昌", "景德镇", "萍乡", "九江", "抚州", "鹰潭", "赣州", "吉安", "宜春", "新余", "上饶",
          "郑州", "开封", "洛阳", "平顶山", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳",
          "商丘", "信阳", "周口", "驻马店",
          "石家庄", "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水",
          "太原", "大同", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁",
          "呼和浩特", "包头", "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "巴彦淖尔", "乌兰察布", "沈阳",
          "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛",
          "长春", "吉林", "四平", "辽源", "通化", "白山", "松原", "白城",
          "哈尔滨", "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "大庆", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化",
          "南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁",
          "杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水",
          "合肥", "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "阜阳", "宿州", "滁州", "六安",
          "宣城", "池州", "亳州",
          "福州", "厦门", "莆田", "三明", "泉州", "漳州", "南平", "龙岩", "宁德",
          "济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照", "临沂", "德州",
          "聊城", "滨州", "菏泽",
          "海口", "三亚", "三沙", "儋州",
          "成都", "自贡", "攀枝花", "泸州", "德阳", "绵阳", "广元", "遂宁", "内江", "乐山", "南充", "眉山", "宜宾",
          "广安", "达州", "雅安", "巴中", "资阳",
          "贵阳", "六盘水", "遵义", "安顺", "毕节", "铜仁",
          "昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧",
          "拉萨", "日喀则", "昌都", "林芝", "山南", "那曲",
          "西安", "铜川", "宝鸡", "咸阳", "渭南", "延安", "汉中", "榆林", "安康", "商洛",
          "兰州", "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南",
          "西宁", "海东", "银川", "石嘴山", "吴忠", "固原", "中卫", "乌鲁木齐", "克拉玛依", "吐鲁番", "哈密"]


# 判断一个名称是省份还是城市
def is_province(name, provinces, cities):
    return name in provinces and name not in cities


# 判断一个名称是城市还是省份
def is_city(name, provinces, cities):
    return name not in provinces and name in cities


# 定义运营商的名称和对应的组织名称
operators = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    # "中国移动": "China Mobile Communications Corporation"
}
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
            continue  # 如果不是省份或城市，则跳过
            # 编码和构建URL
        bytes_string = search_txt.encode('utf-8')
        encoded_search_txt = base64.b64encode(bytes_string).decode('utf-8')
        url = f'https://fofa.info/result?qbase64={encoded_search_txt}'
        print(f"正在扫描 {shengshi} {operator_name}地址: ")
        print(f"{url}")
        all_urls.append(url)  # 添加到所有URL的列表中

    # 现在 all_urls 包含了所有省份和城市的URL
    urls = all_urls  # 将所有查询到的URL赋值给 urls 变量


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


# 对iptv.txt内所有频道列表所在的ip地址及端口进行抽检测速
def download_m3u8(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            m3u8_content = response.text
            ts_urls = [line.strip() for line in m3u8_content.split('\n') if line and not line.startswith('#')]

            if not ts_urls:
                print("Error: 没有找到任何TS文件链接", flush=True)
                return 0

            total_size = 0
            start_time = time.time()
            ts_timeout = 15  # 设置每个.ts文件下载的超时值（秒）
            for ts_url in ts_urls:
                if (time.time() - start_time) > 30:
                    print("Error: 总下载时间超过30秒，速度检测不合格", flush=True)
                    return 0

                if ts_url.startswith('http'):
                    full_ts_url = ts_url
                else:
                    base_url = url.rsplit('/', 1)[0]
                    if ts_url.startswith('/'):
                        base_url = "/".join(base_url.split('/')[:-2])
                    full_ts_url = base_url + '/' + ts_url

                ts_response = requests.get(full_ts_url, timeout=ts_timeout)
                total_size += len(ts_response.content)

            end_time = time.time()
            download_time = end_time - start_time
            if download_time == 0:
                print("Error: 下载时间计算为0，不能计算下载速度", flush=True)
                return 0

            speed = total_size / (download_time * 1024)  # 计算速度，单位为KB/s
            return speed
        else:
            print(f"Error: 下载.m3u8文件失败, 状态码: {response.status_code}", flush=True)
            return 0
    except requests.exceptions.RequestException as e:
        print("HTTP请求错误:", e, flush=True)
        return 0
    except Exception as e:
        print("Error:", e, flush=True)
        return 0


def is_multicast_url(url):
    return re.search(r'udp|rtp', url, re.I)


def process_domain(domain, cctv_links, all_links):
    if not cctv_links:
        print(f"IP {domain} 下没有找到任何 CCTV 相关的链接，跳过。")
        return None, domain

    random.shuffle(cctv_links)
    selected_link = cctv_links[0]

    speed = download_m3u8(selected_link)
    if speed >= 1300:  # 更改这个数值可改变要保留频道列表的最低下载速率
        print(f"频道链接： {selected_link} 在IP {domain} 下的下载速度为：{speed:.2f} KB/s")
        genre = "genre"
        result = [f"下载速率{speed:.2f},#{genre}#"]
        result.extend(f"{name},{url}" for name, url in all_links)
        return result, domain, speed
    else:
        print(f"频道链接: {selected_link} 在IP {domain} 下未通过速度测试,下载速度为：{speed:.2f} KB/s。")
        return None, domain, speed


def process_ip_addresses(ip_data):
    # print(f"正在处理数据：{ip_data}\n", flush=True)
    print(f"......开始抽取频道列表所在的IP地址及端口进行速率检测......\n")

    channels_info = []
    lines = ip_data.strip().split('\n')
    for line in lines:
        if ',' in line:
            channel_name, m3u8_link = line.split(',', 1)
            channels_info.append((channel_name.strip(), m3u8_link.strip()))

    if not channels_info:
        print(f"处理数据时没有找到有效的频道，跳过测速。")
        return []

    domain_dict = {}
    for name, link in channels_info:
        match = re.search(r'https?://([^/]+)/', link)
        if match:
            domain = match.group(1)
            if domain not in domain_dict:
                domain_dict[domain] = []
            domain_dict[domain].append((name, link))
        else:
            print(f"链接 {link} 无法提取IP，跳过。")

    # 存储每个域的最快速度和频道列表
    domain_speeds = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain = {
            executor.submit(process_domain, domain, [link for name, link in links if "CCTV" in name], links): domain
            for domain, links in domain_dict.items()
        }

        for future in as_completed(future_to_domain):
            try:
                result, domain, speed = future.result()
                if result:
                    if domain not in domain_speeds or speed > domain_speeds[domain]['speed']:
                        domain_speeds[domain] = {'speed': speed, 'channels': result}
            except ValueError:
                print(f"Error: 无法正确解析出结果 from domain {domain}")
                continue
    # 根据速度对IP进行降序排序
    sorted_domains = sorted(domain_speeds.items(), key=lambda item: item[1]['speed'], reverse=True)
    valid_urls = []
    for domain, data in sorted_domains:
        valid_urls.extend(data['channels'])

    return valid_urls


# 获取当前脚本运行的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = script_dir

# 指定iptv.txt和SpeedTest.txt的路径
input_file_path = os.path.join(file_path, "iptv.txt")
output_file_path = os.path.join(file_path, "SpeedTest.txt")

# 加载iptv.txt文件内频道列表数据
with open(input_file_path, "r", encoding="utf-8") as file:
    ip_data = file.read()

result = process_ip_addresses(ip_data)

# 输出结果到SpeedTest.txt文件
with open(output_file_path, "w", encoding="utf-8") as output_file:
    for line in result:
        output_file.write(line + '\n')

print(f"\n检测合格的频道列表已写入 {output_file_path} 文件。\n", flush=True)


# 对SpeedTest.txt内所有频道列表进行排序分类
def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


# 从SpeedTest.txt文件中读取频道列表
results = []
with open("SpeedTest.txt", 'r', encoding='utf-8') as file:
    for line in file:
        channel_info = line.strip().split(',')
        channel_name = channel_info[0]
        channel_url = channel_info[1]
        results.append((channel_name, channel_url))

# 对频道进行排序
results.sort(key=lambda x: channel_key(x[0]))
# 每个频道需要保留下来的个数
result_counter = 10
# 对频道进行分类
with open("iptv_list.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url = result
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
        channel_name, channel_url = result
        if '卫视' in channel_name or '重温经典' in channel_name or '影迷电影' in channel_name or '凤凰' in channel_name \
                or '家庭影院' in channel_name or '动作电影' in channel_name or 'CHC' in channel_name or '翡翠' in channel_name:
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
        channel_name, channel_url = result
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
        channel_name, channel_url = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and 'CHC' not in channel_name and '湖南' not in \
                channel_name and '长沙' not in channel_name and '金鹰' not in channel_name and '先锋乒羽' not in \
                channel_name and '下载速率' not in channel_name and '测试' not in channel_name and '重温经典' not in \
                channel_name and '影迷电影' not in channel_name and '家庭影院' not in channel_name and '动作电影' not in \
                channel_name and '购' not in channel_name and 'CHC' not in channel_name and '凤凰' not in channel_name:
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
file_paths = ["YD-IPTV.txt", "iptv_list.txt", "gangaotai.txt"]  # 替换为实际的文件路径列表
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
# os.remove("SpeedTest.txt")
os.remove("gangaotai.txt")

print("频道分类完成已写入iptv_list.txt文件。")

