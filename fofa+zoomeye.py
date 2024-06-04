import time
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
import base64
from datetime import datetime
import threading
from queue import Queue
from pypinyin import lazy_pinyin
import random
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

shengshi_names = ["山东", "南宁", "江西"]
print(f'本次扫描{shengshi_names}的酒店频道。')
pinyin_names = ["".join(lazy_pinyin(name, errors=lambda x: x)) for name in shengshi_names]

# 省直辖市自治区名称列表
provinces = ["湖南", "湖北", "广东", "广西壮族自治区", "江西", "江苏", "浙江", "安徽", "河南", "四川", "河北", "山西",
             "福建", "山东", "北京", "天津", "上海", "重庆", "广西壮族自治区", "贵州", "云南", "陕西", "海南", "辽宁",
             "吉林", "黑龙江", "甘肃", "青海", "内蒙古自治区", "宁夏回族自治区"]

# 省会及地级城市名称列表
cities = ["长沙", "娄底", "衡阳", "常德", "株洲", "湘潭", "邵阳", "张家界", "益阳", "郴州", "永州", "怀化", "岳阳",
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
          "南昌", "景德镇", "萍乡", "九江", "抚州", "鹰潭", "赣州", "吉安", "宜春", "新余", "上饶",
          "济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照", "临沂", "德州",
          "聊城", "滨州", "菏泽",
          "郑州", "开封", "洛阳", "平顶山", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳",
          "商丘", "信阳", "周口", "驻马店",
          "武汉", "黄石", "十堰", "宜昌", "襄阳", "鄂州", "荆门", "孝感", "荆州", "黄冈", "咸宁", "随州",
          "广州", "韶关", "深圳", "珠海", "汕头", "佛山", "江门", "湛江", "茂名", "肇庆", "惠州", "梅州", "汕尾",
          "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮",
          "南宁", "贵港", "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "玉林", "百色", "贺州", "河池", "来宾", "崇左",
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


# 获取FOFA的URL
def get_fofa_urls(shengshi_names, operators, provinces, cities):
    fofa_urls = []
    for shengshi in shengshi_names:
        pinyin_name = "".join(lazy_pinyin(shengshi, errors=lambda x: x))
        for operator_name, org_name in operators.items():
            search_txt = ""
            if is_province(shengshi, provinces, cities):
                search_txt = f'"iptv/live/zh_cn.js" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
            elif is_city(shengshi, provinces, cities):
                search_txt = f'"iptv/live/zh_cn.js" && country="CN" && city="{pinyin_name}" && org="{org_name}"'
            if search_txt:
                bytes_string = search_txt.encode('utf-8')
                encoded_search_txt = base64.b64encode(bytes_string).decode('utf-8')
                fofa_url = f'https://fofa.info/result?qbase64={encoded_search_txt}'
                print(f"正在扫描FOFA上 {shengshi} {operator_name}地址: {fofa_url}")
                fofa_urls.append(fofa_url)
    return fofa_urls


# 获取ZoomEye的URL
def get_zoomeye_urls(shengshi_names, provinces, cities):
    zoomeye_urls = []
    for shengshi in shengshi_names:
        pinyin_name = "".join(lazy_pinyin(shengshi, errors=lambda x: x))
        search_txt = ""
        if is_province(shengshi, provinces, cities):
            search_txt = f'%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22{pinyin_name}%22'
        elif is_city(shengshi, provinces, cities):
            search_txt = f'%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bcity%3A%22{pinyin_name}%22'
        if search_txt:
            zoomeye_url = f'https://www.zoomeye.org/searchResult?q={search_txt}'
            print(f"正在扫描ZoomEye上 {shengshi} 地址: {zoomeye_url}")
            zoomeye_urls.append(zoomeye_url)
    return zoomeye_urls


fofa_urls = get_fofa_urls(shengshi_names, operators, provinces, cities)
zoomeye_urls = get_zoomeye_urls(shengshi_names, provinces, cities)
urls = fofa_urls + zoomeye_urls


# 检查URL是否可访问
def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


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
    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    # 使用WebDriver访问网页
    driver.get(url)  # 将网址替换为你要访问的网页地址
    time.sleep(10)
    # 获取网页内容
    page_content = driver.page_source

    # 关闭WebDriver
    driver.quit()

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
    #   多线程获取可用url
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
                            name = name.replace("搞清", "")
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
total_channels = len(results)
print(f"频道列表文件iptv.txt生成完毕，共获取到{total_channels}个频道。\n")
