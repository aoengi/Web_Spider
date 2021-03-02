# -*- coding= utf-8 -*-
# @Time: 2020/7/2512:40
# @File: 7-24.py
# @Software:PyCharm.py

import http.client
import re                       # 正则表达式进行文字匹配
from bs4 import BeautifulSoup   # 网页解析，获取数据
import urllib.request as ur           # 指定URL，获取网页数据
import urllib.error
import urllib
import xlwt             # 进行excel操作
import time
import random
import socket

from selenium import webdriver

socket.setdefaulttimeout(20)

def main():
    # 获取城市及不同城市对应的网址
    # places = getPlace('https://you.ctrip.com/place/')
    # for i in range(len(places)):
    #     places[i][1] = places[i][1].replace('place','sight')
    #     places[i][1] = 'https://you.ctrip.com' + places[i][1]
    # print(places)

    # 用一个城市先进行测试
    places = [['上海', 'https://you.ctrip.com/sight/shanghai2.html']]
    # datalist = []  # 用于存放所有爬取到的景点信息
    # num = 0
    for place in places:
        print("正在爬取："+str(place[0]))
        # 定义数据的起始位置，本次place的xls存储起始位置
        # num = num+len(datalist)
        # 爬取网页
        datalist = getDate(place[1])
        # 保存数据在xls表************************注意后面的保存方式***********************
        # saveData(datalist,num)
    # 用来测试城市景点一共有多少页
    # getPage(baseurl)


# 创建表单
tour = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = tour.add_sheet('景点信息', cell_overwrite_ok=True)
col = ("景点名字", "图片链接", "详细信息网址", "介绍", "景色分数", "趣味", "性价比", "总分", "等级", "地址","门票价格")
for i in range(0, 11):
    sheet.write(0, i, col[i])

# 保存数据
def saveData(datalist,num):
    print("save...")
    print(len(datalist))
    for i in range(num,num+len(datalist)):
        # print("第%d条" % (i + 1))
        data = datalist[i-num]
        for j in range(0, 11):
            sheet.write(i + 1, j, data[j])
    tour.save(".\\携程上海热门景点信息.xls")

#获取国内地区的名字、网址
def getPlace(baseurl):
    html = askURL(baseurl)

    soup = BeautifulSoup(html, "lxml")
    # place = soup.find_all('div',class_='goto-items')[0]
    place = soup.find_all('dd',class_ = 'panel-con')[0]
    places = []
    place_names = place.find_all('li')
    for k in place_names:
        place_names = k.find_all('a')
        for j in place_names:
            place_naur = []
            place_name = j.text
            place_url = j['href']
            place_naur.append(place_name)
            place_naur.append(place_url)
            places.append(place_naur)
    return places

# 获取各景点信息
def getDate(baseurl):
    num = 0
    # page_num = getPage(baseurl)+1
    # 只有1页的时候
    # if page_num == 1:
    #     page_num = 2
    # 只爬取前20页
    # if page_num > 21:
    #     page_num = 21
    # print("总页数为：",page_num-1)
    # 生成带有页数的网址
    baseurl = baseurl[:-5]
    baseurl = baseurl + str('/s0-p')
    # 按页数循环爬取
    for i in range(61, 121):
        print("第",i)
        datalist = []
        # 将第几页添加至网址后面，生成完整的网址
        url = baseurl + str(i)
        url = url + '.html#sightname'
        # print(url)
        html = askURL(url)

        # 2、逐一解析数据
        soup = BeautifulSoup(html,"lxml")
        tour = soup.find_all('div',class_='list_mod2')

        for item in tour:
            # print(item)
            data = []

            # 1、景区名字
            tour_name = item.find_all('div',class_='rdetailbox')[0].find_all('dt')[0].a['title']
            data.append(tour_name)
            print(tour_name)

            # 2、景区的图片
            tour_img = item.find_all('div',class_='leftimg')[0].img['src']
            data.append(tour_img)
            # print(tour_img)

            # 3、景区的详细信息网址
            tour_url = item.find_all('div',class_='leftimg')[0].a['href']
            tour_url = 'https://you.ctrip.com' + tour_url
            data.append(tour_url)
            # print(tour_url)

            tour_html = ask_tourURL(tour_url)
            tour_soup = BeautifulSoup(tour_html,"lxml")

            # 4、景点介绍
            try:
                tour_intros = tour_soup.find_all('div',class_='LimitHeightText')[0].find_all('div')[0]
                # re_first = '<p .*?</p>'
                # tour_intros = re.compile(re_first).findall(str(tour_intros))
                tour_string = ''
                for intros in tour_intros:
                    # print(intros)
                    re_intro = ">(.*?)<"
                    tour_intro = re.compile(re_intro).findall(str(intros))
                    for intro in tour_intro:
                        tour_string += intro
            except:
                tour_string = '暂无介绍'
            # print(tour_string)
            data.append(tour_string)

            re_detail = '\d+\.?\d*'
            try:
                tour_detail = tour_soup.find_all('span',class_='featureScore')
            # tour_detail = tour_soup.find_all('span',class_='featureScore')
            #     print(tour_detail)

                # 5、景色
                tour_jingse = tour_detail[0].text
                tour_jingse = re.compile(re_detail).findall(str(tour_jingse))[0]

                # 6、趣味
                tour_quwei = tour_detail[1].text
                tour_quwei = re.compile(re_detail).findall(str(tour_quwei))[0]

                # 7、性价比
                tour_xingjiabi = tour_detail[2].text
                tour_xingjiabi = re.compile(re_detail).findall(str(tour_xingjiabi))[0]
            except:
                tour_jingse = 0
                tour_quwei = 0
                tour_xingjiabi = 0

            data.append(tour_jingse)
            # print(tour_jingse)
            data.append(tour_quwei)
            # print(tour_quwei)
            data.append(tour_xingjiabi)
            # print(tour_xingjiabi)

            # 8、景区总分
            try:
                tour_score = item.find_all('ul', class_='r_comment')[0].find_all('li')[0].find_all('strong')[0].text
            except:
                tour_score = '暂无评分'
            data.append(tour_score)
            # print(tour_score)

            # 9、景区等级 A级
            try:

                tour_lev = item.find_all('div', class_='rdetailbox')[0].find_all('dl')[0].find_all('dd')
                tour_level = tour_lev[1].text
                re_level = 'A*级景区'
                tour_level = re.compile(re_level).findall(tour_level)[0]
            except:
                tour_level = '普通景区'

            # 10、景区价格
            try:
                re_price = '¥\d*\S'
                tour_price = tour_lev[1].find_all('span',class_='price')[0].text
                tour_price = re.compile(re_price).findall(tour_price)[0]
            except:
                tour_price = '暂无价格明细'

            # 将level添加到data中
            if(tour_level==''):
                tour_level = '普通景区'
            data.append(tour_level)
            # print(tour_level)

            # 11、景区地址
            tour_address = item.find_all('div',class_='rdetailbox')[0].find_all('dl')[0].find_all('dd')
            tour_address = tour_address[0].text
            tour_address = str(tour_address).replace('\n', '').replace('\r', '').replace(' ', '')
            data.append(tour_address)
            # print(tour_address)

            # 将price添加到data中
            if tour_price == '':
                tour_price = '暂无价格明细'
            data.append(tour_price)
            # print(tour_price)

            datalist.append(data)
            time.sleep(random.randint(1, 5))
    # print(datalist)
        saveData(datalist, num)
        num = num + len(datalist)
    return datalist

# 获取总页数
def getPage(baseurl):
    html = askURL(baseurl)
    try:
        soup = BeautifulSoup(html, "html.parser")
        page = soup.find_all('div', class_='pager_v1')[0].find_all('b')
        page_num = int(page[0].text)
    except:
        page_num = 0
    print(page_num)
    return page_num

def ask_tourURL(url):
    browser = webdriver.Chrome()  # 声明浏览器驱动对象

    while True:
        try:
            browser.get(url)
            time.sleep(random.randint(3, 5))
            return browser.page_source
            browser.close()  # 关闭浏览器
            break
        except Exception as e:
            print('error, retrying…')
            time.sleep(3)
    # try:
    #     browser.get(url)
    #     time.sleep(random.randint(5, 10))
    #     return browser.page_source
    # except:
    #     return ask_tourURL(url)
    # finally:
    #     browser.close()  # 关闭浏览器

def askURL(url):
    # 反爬措施 使用不同的agent
    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
    ]
    user_agent = random.choice(USER_AGENTS)
    head = {
        "user-agent": user_agent,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "_abtest_userid=19c3b2fa-ae30-4494-843c-93d16b435d28; _RSG=Gk4P9Qb8FC6BCvQcKMfMlA; _RDG=280c4f97837da121b53baa45d23f8c5d2c; _RGUID=630f2256-8964-4b90-abd6-a565266b930b; GUID=09031058110904512400; MKT_Pagesource=PC; _ga=GA1.2.122235514.1590544427; MKT_CKID=1590544438383.1c0b6.9q6c; StartCity_Pkg=PkgStartCity=110; Session=SmartLinkCode=csdn&SmartLinkKeyWord=&SmartLinkQuary=_UTF.&SmartLinkHost=blog.csdn.net&SmartLinkLanguage=zh; __utma=1.122235514.1590544427.1590761474.1590848683.2; __utmz=1.1590848683.2.2.utmcsr=huodong.ctrip.com|utmccn=(referral)|utmcmd=referral|utmcct=/things-to-do/list; ASP.NET_SessionSvc=MTAuNjEuMjIuMjQ0fDkwOTB8amlucWlhb3xkZWZhdWx0fDE1ODkwMDM3MTEwNzE; MKT_CKID_LMT=1591417333465; _gid=GA1.2.1034050141.1591417334; _RF1=123.138.251.200; _bfa=1.1590544419100.396b4y.1.1590853124374.1591417331238.6.138.10650014170; _jzqco=%7C%7C%7C%7C1591417333652%7C1.1553316630.1590544438372.1591419060312.1591419611530.1591419060312.1591419611530.undefined.0.0.93.93; __zpspc=9.6.1591417333.1591419611.4%234%7C%7C%7C%7C%7C%23; appFloatCnt=96; _bfi=p1%3D290510%26p2%3D10650000804%26v1%3D138%26v2%3D137"
    }

    # 每次爬取页面时等待5秒
    time.sleep(random.randint(1, 5))
    # 使用urllib库
    request = urllib.request.Request(url, headers=head)

    # 对没有爬取到的网页采取的一些措施
    try:
        response = urllib.request.urlopen(request,timeout=60)

        # 成功爬取到网页时，返回html
        if response.code == 200:
            html = response.read().decode("utf-8")
            response.close()
            return html
        else:
            # 没有爬取到 等待60到120秒左右，再重新调用askURL进行爬取
            time.sleep(random.randint(60, 120))
            print("等待ing")
            return askURL(url)
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e, "code")
        if hasattr(e, "reason"):
            print(e.reason)
    except UnicodeDecodeError as e:
        print('-----UnicodeDecodeError url:', url)
    except socket.timeout as e:
        print("-----socket timout:", url)
    except http.client.IncompleteRead as e:
        time.sleep(60)
        html = e.partial
        return askURL(url)

if __name__ == '__main__':
    main()
    print('爬取完毕')
