import requests
from bs4 import BeautifulSoup
import re
import time
import threading
from queue import Queue
from datetime import datetime
import os
import eventlet

eventlet.monkey_patch()


# def ip_exists(ip):
#     check_ip = ['Multicast.txt', 'Hotel.txt']
#     for file_name in check_ip:
#         try:
#             with open(file_name, 'r', encoding='utf-8') as f:
#                 for line in f:
#                     if ip in line:
#                         return True
#         except FileNotFoundError:
#             print(f"文件 {file_name} 不存在，跳过检查。")
#     return False


def get_ip(diqu):
    """爬取ip"""
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "upgrade-insecure-requests": "1",
        "cookie": "REFERER2=Game; REFERER1=Over",
        "Referer": "http://www.foodieguide.com/iptvsearch/hoteliptv.php",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    base_url = "http://www.foodieguide.com/iptvsearch/hoteliptv.php"
    data = {"saerch": diqu, "Submit": "+", "names": "Tom", "city": "HeZhou", "address": "Ca94122"}

    response = requests.post(base_url, headers=headers, data=data)

    ip_list = set()
    print(f"\n开始获取{diqu}地区的ip")
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有的 result div
        results = soup.find_all("div", class_="result")

        for result in results:
            # 提取 IP 地址
            ip_link = result.find("a", href=re.compile(r"hotellist\.html\?s="))
            if ip_link:
                # 从 href 中提取 IP 地址及端口
                ip_address = re.search(r"s=([^&]+)", ip_link['href'])
                if ip_address:
                    # 提取状态
                    status_div = result.find("div", style="color: crimson;")
                    if status_div and "暂时失效" in status_div.get_text():
                        continue  # 如果状态为“暂时失效”，则跳过此 IP
                    ip_list.add(ip_address.group(1))  # 添加有效的 IP 地址


    else:
        ip_list.add(f"请求失败，状态码: {response.status_code}")

    for ip in ip_list:
        print(ip)
    return ip_list


def get_iptv(ip_list):
    """获取频道信息，同时对频道名称进行筛选和修改替换"""
    print("\n开始获取频道列表")
    all_results = []  # 用于存储所有 IP 的结果

    for ip in ip_list:
    #     if ip_exists(ip):
    #         print(f"\nIP {ip} 已存在，不需要重复获取。")
    #         continue  # 如果 IP 存在，则跳过

        # 定义目标 URL，使用当前 IP 地址
        base_url = f"http://www.foodieguide.com/iptvsearch/allllist.php?s={ip}&y=false"

        # 设置请求头
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"http://www.foodieguide.com/iptvsearch/hotellist.html?s={ip}",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            # 使用 eventlet.Timeout 设置超时时间为 10 秒，超过10秒未获取到频道列表则跳过，继续下一个ip的获取。
            with eventlet.Timeout(10, False):
                response = requests.get(base_url, headers=headers)
                response.raise_for_status()  # 检查请求是否成功

                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                seen_urls = set()  # 用于存储已存在的 URL

                for result in soup.find_all("div", class_="result"):
                    channel_div = result.find("div", style="float: left;")
                    if channel_div:  # 确保找到 channel_div
                        channel_name = channel_div.text.strip()
                        url_tag = result.find("td", style="padding-left: 6px;")

                        if url_tag:
                            url = url_tag.text.strip()

                            # 过滤掉包含 'udp' 的 URL
                            # if 'udp' not in url and url not in seen_urls:
                            #     seen_urls.add(url)
                            #     results.append((channel_name, url))

                            # 不过滤掉包含 'udp' 的 URL
                            if url not in seen_urls:
                                seen_urls.add(url)
                                results.append((channel_name, url))

                print(f"\nIP {ip} 下解析到 {len(results)} 条频道信息")
                for channel_name, url in results:
                    print(f"{channel_name},{url}")

                    # 将当前 IP 的频道列表添加到总结果中
                    all_results.extend(results)

        except eventlet.timeout.Timeout:
            print(f"解析 IP {ip} 下的频道列表超时，跳过。")
        except requests.exceptions.RequestException as e:
            print(f"无法访问: {base_url}, 错误: {e}")

    # 对所有频道名称进行筛选和修改替换
    keywords = ["CCTV", "卫视", "凤凰", "影院", "剧场", "CHC", "娱乐", "经典电影", "湖南", "金鹰", "长沙"]  # 需要保留频道名称的关键字
    replace_keywords = {
        'HD': '', '-': '', 'IPTV': '', '[': '', ']': '', '超清': '', '高清': '', '标清': '', "上海东方": "",
        '中文国际': '', 'BRTV': '北京', ' ': '', '北京淘': '', '⁺': '+', "R": "", "4K": "", "测试": "", "F": "",
        "奥林匹克": "", "内蒙古": "内蒙", "台": "", "频道": "", "CCTV1综合": "CCTV1", "CCTV2财经": "CCTV2",
        "CCTV3综艺": "CCTV3", "CCTV4国际": "CCTV4", "CCTV5体育": "CCTV5", "CCTV6电影": "CCTV6", "CCTV7军农": "CCTV7",
        "CCTV8电视剧": "CCTV8", "CCTV9纪录": "CCTV9", "CCTV10科教": "CCTV10", "CCTV11戏曲": "CCTV11",
        "CCTV12社会与法": "CCTV12", "CCTV13新闻": "CCTV13", "CCTV14少儿": "CCTV14", "CCTV15音乐": "CCTV15",
        "CCTV16奥林匹克": "CCTV16", "CCTV17国防军事": "CCTV17", "中央一": "CCTV1", "中央二": "CCTV2", "中央三": "CCTV3",
        "中央四": "CCTV4", "中央五": "CCTV5", "中央六": "CCTV6", "中央七": "CCTV7", "中央八": "CCTV8",
        "中央九": "CCTV9", "中央十": "CCTV10", "中央十一": "CCTV11", "中央十二": "CCTV12", "中央十三": "CCTV13", "中央十四": "CCTV14",
        "中央十五": "CCTV15", "中央十六": "CCTV16", "中央十七": "CCTV17",
    }
    unique_channels = {}
    filtered_out = []

    for channel_name, url in all_results:
        for key, value in replace_keywords.items():
            channel_name = channel_name.replace(key, value)

        if url not in unique_channels:
            if any(keyword in channel_name for keyword in keywords):
                if "CCTV" in channel_name and channel_name != "CCTV4":
                    channel_name = ''.join(filter(lambda x: x not in "汉字", channel_name))
                unique_channels[url] = channel_name
            else:
                filtered_out.append((channel_name, url))

    # 将去重后的所有频道列表根据是否包含 rtp 或 udp 写入不同的文件
    with open('Multicast.txt', 'w', encoding='utf-8') as f_Multicast, open('Hotel.txt', 'w', encoding='utf-8') as f_Hotel:
        for url, channel_name in unique_channels.items():
            if 'rtp' in url or 'udp' in url:
                f_Multicast.write(f"{channel_name},{url}\n")
            else:
                f_Hotel.write(f"{channel_name},{url}\n")

    # 将过滤掉的频道写入 gl_list.txt 文件
    with open('gl_list.txt', 'w', encoding='utf-8') as f:
        for channel_name, url in filtered_out:
            f.write(f"{channel_name},{url}\n")

    return all_results  # 返回所有 IP 的结果


def download_speed(url, test_duration=5):
    """ 测试下载速度 """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=test_duration + 5, stream=True)
        response.raise_for_status()

        downloaded = 0
        elapsed_time = 0  # 初始化 elapsed_time
        for chunk in response.iter_content(chunk_size=4096):
            downloaded += len(chunk)
            elapsed_time = time.time() - start_time
            if elapsed_time > test_duration:
                break

        speed = downloaded / elapsed_time if elapsed_time > 0 else 0  # 防止除以零
        return speed / (1024 * 1024)  # 转换为 MB/s

    except requests.RequestException:
        return 0


def measure_download_speed_parallel(channels, max_threads=5):
    """并行测量下载速度"""
    results = []
    queue = Queue()
    processed_count = 0  # 记录处理的频道数

    for channel in channels:
        queue.put(channel)

    def worker():
        nonlocal processed_count  # 使用 nonlocal 声明变量
        while not queue.empty():
            channel = queue.get()
            name, url = channel  # 只解包两个值
            speed = download_speed(url)
            results.append((name, url, speed))
            processed_count += 1  # 增加已处理的频道数
            print(f"{name},{url} 下载速率: {speed:.2f}MB/s")
            queue.task_done()

    threads = []
    for _ in range(max_threads):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    queue.join()

    for thread in threads:
        thread.join()

    return results


def natural_key(string):
    """生成自然排序的键"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', string)]


def group_and_sort_channels(channels):
    """根据规则分组并排序频道信息，并保存到Multicast_list"""
    groups = {
        '央视频道,#genre#': [],
        '卫视频道,#genre#': [],
        '湖南频道,#genre#': [],
        '其他频道,#genre#': []
    }

    for name, url, speed in channels:
        if 'cctv' in name.lower():
            groups['央视频道,#genre#'].append((name, url, speed))
        elif '卫视' in name or '凤凰' in name or '翡翠' in name or 'CHC' in name:
            groups['卫视频道,#genre#'].append((name, url, speed))
        elif '湖南' in name or '金鹰' in name or '长沙' in name:
            groups['湖南频道,#genre#'].append((name, url, speed))
        else:
            groups['其他频道,#genre#'].append((name, url, speed))

        # 对每组进行排序
        for group in groups.values():
            group.sort(key=lambda x: (
                natural_key(x[0]),  # 名称自然排序
                -x[2] if x[2] is not None else float('-inf')  # 速度从高到低排序
            ))

    # 筛选相同名称的频道，只保存10个
    filtered_groups = {}
    overflow_groups = {}

    for group_name, channel_list in groups.items():
        seen_names = {}
        filtered_list = []
        overflow_list = []

        for channel in channel_list:
            name = channel[0]
            if name not in seen_names:
                seen_names[name] = 0

            if seen_names[name] < 10:
                filtered_list.append(channel)
                seen_names[name] += 1
            else:
                overflow_list.append(channel)

        filtered_groups[group_name] = filtered_list
        overflow_groups[group_name] = overflow_list

    return groups


if __name__ == "__main__":
    # 定义一个列表，包含要获取IP的地方
    places_to_get_ip = ["湖南"]
    ip_list = {ip for place in places_to_get_ip for ip in get_ip(place)}
    if ip_list:
        iptv_list = get_iptv(ip_list)

        # 读取 Multicast.txt 文件中的频道信息
        channels = []
        with open('Multicast.txt', 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    name, url = parts
                    channels.append((name, url))

        # 检测下载速度
        results = measure_download_speed_parallel(channels, max_threads=5)
        # 对频道进行分组和排序
        grouped_channels = group_and_sort_channels(results)

        # 获取当前时间
        now = datetime.now()
        update_time_line = f"更新时间,#genre#\n{now.strftime('%Y-%m-%d')},url\n{now.strftime('%H:%M:%S')},url\n"
        # 保存到 Multicast_list.txt 文件
        with open('Multicast_list.txt', 'w', encoding='utf-8') as f:
            f.write(update_time_line)
            for group_name, channel_list in grouped_channels.items():
                f.write(f"{group_name}:\n")
                for name, url, speed in channel_list:
                    # if speed >= 0.1:  # 写入下载速度大于或等于 0.1 MB/s 的频道列表
                    f.write(f"{name},{url}\n")
                f.write("\n")  # 打印空行分隔组

        print("组播源频道列表已保存到Multicast_list.txt文件！")

# 线程安全的队列，用于存储下载任务
task_queue = Queue()
# 线程安全的列表，用于存储结果
results = []
channels = []
error_channels = []

# 从iptv.txt文件提取cctv频道进行检测
with open("Hotel.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'CCTV' in channel_name:
                channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if
                        line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                download_speed = file_size / response_time / 1024
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                print(
                    f"\n检测频道: {channel_name},{channel_url}\n下载速度：{download_speed:.3f} kB/s，标准化后的速率：{normalized_speed:.3f} MB/s")
                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
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


# 对频道进行下载速率降序排序，将CCTV频道进行升序排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
results.sort(key=lambda x: channel_key(x[0]))

result_counter = 10  # 每个频道需要保留下来的个数

# 写入cctv.txt和.m3u文件
with open("Hotel_CCTV.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('\n央视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
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

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

# 线程安全的列表，用于存储结果
results = []
channels = []
error_channels = []

with open("Hotel.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line:
            channel_name, channel_url = line.split(',')
            if 'CCTV' not in channel_name:
                channels.append((channel_name, channel_url))


# 定义工作线程函数
def worker():
    while True:
        # 从队列中获取一个任务
        channel_name, channel_url = task_queue.get()
        try:
            channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])  # m3u8链接前缀
            lines = requests.get(channel_url).text.strip().split('\n')  # 获取m3u8文件内容
            ts_lists = [line.split('/')[-1] for line in lines if
                        line.startswith('#') == False]  # 获取m3u8文件下视频流后缀
            ts_lists_0 = ts_lists[0].rstrip(ts_lists[0].split('.ts')[-1])  # m3u8链接前缀
            ts_url = channel_url_t + ts_lists[0]  # 拼接单个视频片段下载链接

            # 多获取的视频数据进行5秒钟限制
            with eventlet.Timeout(5, False):
                start_time = time.time()
                content = requests.get(ts_url).content
                end_time = time.time()
                response_time = (end_time - start_time) * 1

            if content:
                with open(ts_lists_0, 'ab') as f:
                    f.write(content)  # 写入文件
                file_size = len(content)
                # print(f"文件大小：{file_size} 字节")
                download_speed = file_size / response_time / 1024
                # print(f"{ts_url}")
                normalized_speed = min(max(download_speed / 1024, 0.001), 100)  # 将速率从kB/s转换为MB/s并限制在1~100之间
                print(
                    f"\n检测频道: {channel_name},{channel_url}\n下载速度：{download_speed:.3f} kB/s，标准化后的速率：{normalized_speed:.3f} MB/s")
                # 删除下载的文件
                os.remove(ts_lists_0)
                result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
                results.append(result)
                numberx = (len(results) + len(error_channels)) / len(channels) * 100
                print(
                    f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channel = channel_name, channel_url
            error_channels.append(error_channel)
            numberx = (len(results) + len(error_channels)) / len(channels) * 100
            print(
                f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(channels)} 个 ,总进度：{numberx:.2f} %。")

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


# 对频道进行下载速率降序排序
results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))

result_counter = 10  # 每个频道需要保留下来的个数

# 生成txt文件
with open("Hotel_list.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('\n卫视频道,#genre#\n')
    for result in results:
        channel_name, channel_url, speed = result
        if '卫视' in channel_name or '凤凰' in channel_name or '翡翠' in channel_name or 'CHC' in channel_name:
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
        channel_name, channel_url, speed = result
        if '湖南' in channel_name or '长沙' in channel_name or '金鹰' in channel_name:
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
        hannel_name, channel_url, speed = result
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name and '凤凰' not in \
                channel_name and '翡翠' not in channel_name and 'CHC' not in channel_name and '湖南' not in channel_name \
                and '长沙' not in channel_name and '金鹰' not in channel_name and '先锋乒羽' not in channel_name:
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
file_paths = ["Hotel_CCTV.txt", "Hotel_list.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)
# 获取当前时间
now = datetime.now()
update_time_line = f"更新时间,#genre#\n{now.strftime('%Y-%m-%d %H:%M:%S')},url\n"
# 写入合并后的txt文件
with open("Hotel_list.txt", "w", encoding="utf-8") as output:
    output.write(update_time_line)
    output.write('\n'.join(file_contents))

os.remove("Multicast.txt")
os.remove("Hotel.txt")
os.remove("Hotel_CCTV.txt")

print("酒店源频道列表已保存到Hotel_list.txt文件！")
