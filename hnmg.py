import requests

file_path = 'mgtv.txt'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
}
proxy = {
    'http': '120.37.121.209:9091',
}
url = 'http://mpp.liveapi.mgtv.com/v1/epg/turnplay/getLivePlayUrlMPP?version=PCweb_1.0&platform=1&buss_id=2000001&channel_id='
channel_dic = {
    '湖南经视': ['280', 'hn01'],
    '湖南都市': ['346', 'hn02'],
    '湖南电视剧': ['484', 'hn03'],
    '湖南电影': ['221', 'hn04'],
    '湖南爱晚': ['261', 'hn05'],
    '湖南国际': ['229', 'hn06'],
    '湖南娱乐': ['344', 'hn07'],
    '快乐购': ['267', 'hn08'],
    '茶频道': ['578', 'hn09'],
    '金鹰纪实': ['316', 'hn10'],
    '金鹰卡通': ['287', 'hn11'],
    '快乐垂钓': ['218', 'hn12'],
    '先锋乒羽': ['329', 'hn13'],
    '长沙新闻': ['269', 'hn14'],
    '长沙政法': ['254', 'hn15'],
    '长沙女性': ['230', 'hn16'],
}

txt_lis = []

for channel in channel_dic:
    response = requests.get(url=url + channel_dic[channel][0], proxies=proxy, headers=headers)
    json_data = response.json()
    txt_url = json_data['data']['url']
    txt_lis.append(f'{channel},{txt_url}\n')

txt_string = ''.join(txt_lis)

with open(file_path, 'w', encoding='utf-8') as file:
    file.write('湖南芒果,#genre#\n')
    file.write(txt_string)

print(f'湖南芒果频道列表文件已保存至{file_path}！')
