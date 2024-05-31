import requests
from bs4 import BeautifulSoup
import random


# 爬取代理IP
def crawl_proxies(start_page, end_page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    proxies = []

    for page in range(start_page, end_page + 1):
        url = f'http://www.kxdaili.com/dailiip/2/{page}.html'
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        # 解析代理IP列表
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                try:
                    proxy = cols[0].text.strip() + ':' + cols[1].text.strip()
                    proxies.append(proxy)
                except Exception as e:
                    print(f"Error parsing proxy on page {page}: {e}")

    return proxies


def test_proxy_and_write(proxy, file_path):
    url = 'http://baidu.com'  # 测试网站
    proxies = {
        'http': 'http://' + proxy,
        'https': 'https://' + proxy
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=10)  # 增加超时时间为10秒
        if response.status_code == 200:
            with open(file_path, 'a', encoding='utf-8') as file:  # 使用 'a' 模式追加写入
                file.write(proxy + '\n')
                print(f"找到有效代理IP: {proxy}")  # 打印有效代理IP
                return True
    except requests.exceptions.RequestException as e:
        print(f"Error testing proxy {proxy}: {e}")
    return False


# 随机选择代理IP
def get_random_proxy(proxy_pool):
    if proxy_pool:
        return random.choice(proxy_pool)
    else:
        return None


# 构建代理IP池
def build_proxy_pool(proxies, file_path):
    # 清空文件，准备写入新的代理IP
    open(file_path, 'w').close()
    proxy_pool = []
    for proxy in proxies:
        if test_proxy_and_write(proxy, file_path):
            proxy_pool.append(proxy)
    return proxy_pool


# 示例使用
if __name__ == '__main__':
    start_page = 1
    end_page = 2  # 最大页数为1-10
    proxies = crawl_proxies(start_page, end_page)
    file_path = 'proxy_ip.txt'  # 指定一个文件路径来存储可用代理
    proxy_pool = build_proxy_pool(proxies, file_path)  # 构建代理池时，同时写入文件

    # 打印所有有效的代理IP
    for proxy in proxy_pool:
        print(f"有效代理IP: {proxy}")

    if proxy_pool:
        print(f"本次扫描共获取到 {len(proxy_pool)} 个有效的代理IP.")
    if not proxy_pool:
        print("未获取到有效的代理IP.")
        exit()  # 如果没有有效的代理IP，则退出程序

