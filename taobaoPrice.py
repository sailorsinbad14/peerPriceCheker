"""
written by sailorsinbad
education purpose only, do not use for any illegal purposes
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import random
import time
import re, csv, requests

#配置webdriver，driver要放在全局变量中否则闪退
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'})#置入自己浏览器的user-agent,模仿真人使用
# print(driver.execute_script("return navigator.userAgent;"))

#加载淘宝链接列表文件
urlList = []
f = open('urlListTaobao.txt', mode='r')
urls = f.readlines()
for url in urls:
    urlList.append(url.strip())
f.close()#关闭文件读取

#生存导出csv表格
f = open('productPriceTaobao.csv', mode='w', encoding='UTF-8')
csvwriter = csv.writer(f)
csvwriter.writerow(['产品标题', '店铺名称', '卖家名', '区间价格', 'SKU名称', 'SKU价格'])

#淘宝登录（仅首次需要）
def get_login():
    #初始化浏览器并打开淘宝首页准备登录
    driver.get('https://www.taobao.com')
    driver.implicitly_wait(10)

    #登录（进入页面后扫码登录）
    driver.find_element('xpath','/html/body/div[3]/div[2]/div[2]/div[2]/div[6]/div/div[2]/div[1]/a[1]').click()
    time.sleep(random.randint(1,3))
    handles = driver.window_handles
    for handle in handles:
        # print('handle:',handle)
        if handle != driver.current_window_handle:
            driver.close()
            driver.switch_to.window(handle)
            # print(driver.current_window_handle)
            break
    while True:
        print('waiting')
        time.sleep(3)
        # print(driver.current_url)
        if driver.current_url == 'https://www.taobao.com/':
            print('login success')
            # print(driver.execute_script("return navigator.userAgent;"))
            break

def get_product(product_url):
    s = requests.Session()
    selenium_user_agent = driver.execute_script("return navigator.userAgent;")
    s.headers.update({'user-agent': selenium_user_agent})
    # print(driver.get_cookies())
    for cookie in driver.get_cookies():
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    resp = s.get(product_url)
    savedPage = resp.text
    resp.close()#关闭requests get
    # print(savedPage)

    #产品标题
    objProductTitle = re.compile('<h3 class="tb-main-title" data-title="(?P<productTitle>.*?)">',re.S)
    productTitle = objProductTitle.search(savedPage).group('productTitle')
    # print(productTitle)

    #卖家名称
    objSellerName = re.compile("sellerNick.*?'(?P<sellerName>.*?)',",re.S)
    sellerName = objSellerName.search(savedPage).group('sellerName')
    # print(sellerName)

    #店铺名称：企业店和个人店铺
    # print(re.search('tb-shop-info-wrap',savedPage).group())
    if re.search('tb-shop-info-wrap',savedPage):

        objStoreName = re.compile('<div class="tb-shop-info-wrap">.*? <a href=".*?" title="(?P<companyName>.*?)" target="_blank">', re.S)
        storeName = objStoreName.search(savedPage).group('companyName')
    else:
        storeName = sellerName

    # 区间价格
    objPriceRange = re.compile(r'J_StrPrice.*?tb-rmb-num">(?P<priceRange>.*?)</em>',re.S)
    priceRange = objPriceRange.search(savedPage).group('priceRange')
    csvwriter.writerow([productTitle, storeName, sellerName, priceRange])
    #SKU价格
    if re.search('skuMap',savedPage): #如果有多个SKU价格
        # print('has skuMap')
        objTemp = re.compile(r'skuMap     : (\{";.*?;":\{"price":".*?".*?oversold":.*?\}).*\}')
        temp = objTemp.search(savedPage).group()
        # print('temp',temp)
        objTemp2 = re.compile(r'";(?P<id>.*?);":\{"price":"(?P<skuPrice>.*?)".*?oversold":.*?\}',re.S)
        temp2 = objTemp2.finditer(temp)
        objTemp3 = re.compile(r'propertyMemoMap: \{(".*?":".*?").*\}')
        temp3 = objTemp3.search(savedPage).group()
        # print('temp3',temp3)
        objTemp4 = re.compile(r'"(?P<id2>.*?)":"(?P<skuName>.*?)"')
        temp4 = objTemp4.finditer(temp3)

        dic1 = {}
        dic2 = {}
        for i in temp2:
            dic1.update({i.group('id'):i.group('skuPrice')})
        for j in temp4:
            dic2.update({j.group('id2'):j.group('skuName')})

        for k1 in dic1:
            for k2 in dic2:
                if k1 == k2:
                    csvwriter.writerow(['','','','',dic2[k2],dic1[k1]])

"""
主程序开始
"""

# print('current handle ', driver.current_window_handle)
get_login()

count = 1
for product_url in urlList:

    try:
        # print('current handle ', driver.current_window_handle)
        get_product(product_url)
    except AttributeError:
        print('被反爬，重新刷新')
        time.sleep(random.randint(3,5))
        driver.refresh()
        get_product(product_url)

    print("done ",count, '/', len(urlList))
    count += 1
    time.sleep(random.randint(5,10)) #随机等待5-10秒抓取下一个

f.close()
driver.quit()





