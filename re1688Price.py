import requests
import re, csv
from random import randint
from time import sleep

#导入URL
urlList = []
f = open('urlList.txt', mode='r')
urls = f.readlines()
for url in urls:
    urlList.append(url.strip())
f.close()#关闭文件读取

#生成结果导出文件
f = open('productPrice.csv', mode='w', encoding='UTF-8')
csvwriter = csv.writer(f)
csvwriter.writerow(['产品标题', '店铺名称', '店铺地址', '运费', '起批量', '区间价格', 'SKU名称', 'SKU价格', 'SKU销量'])

#避免被封手动输入cookie
cookie = input("输入Cookie：")
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'cookie': cookie.encode('utf-8').decode('latin-1')
}

#抓取产品信息模块
def get_product(product_url):
    resp = requests.get(url=product_url, headers=headers)
    savedPage = resp.text
    resp.close()#关闭requests get
    # print(savedPage)

    #产品标题
    objProductTitle = re.compile('<title>(?P<productTitle>.*?)</title>')
    productTitle = objProductTitle.search(savedPage)

    # 店铺名称 地址
    objStoreName = re.compile('"companyName":"(?P<companyName>.*?)",.*?"detailAddress":"(?P<address>.*?)"', re.S)
    storeName = objStoreName.search(savedPage)

    # 运费
    objShippingCost = re.compile(r'\"totalCost\":(?P<shipping>.*?),')
    shippingCost = objShippingCost.search(savedPage)

    # 起定量
    objMOQ = re.compile(r'"offerBeginAmount\\":(?P<moq>.*?),', re.S)
    moq = objMOQ.search(savedPage)

    # 区间价格
    objPriceRange = re.compile(r'"offerPriceDisplay\\":\\"(?P<priceRange>.*?)\\",')
    priceRange = objPriceRange.search(savedPage)

    # sku及价格(无及多SKU）
    checkSKU = re.compile(r'"isSkuOffer":(?P<check>.*?),"', re.S)
    checkRes = checkSKU.search(savedPage)

    if checkRes.group('check') == 'true':
        #写入文件：
        csvwriter.writerow([productTitle.group('productTitle'), storeName.group('companyName'), storeName.group('address'), shippingCost.group('shipping'),moq.group('moq'), priceRange.group('priceRange')])
        objSKU = re.compile(r'\{\\"specId.*?specAttrs\\":\\"(?P<skuName>.*?)\\",\\"price\\":\\"(?P<skuPrice>.*?)\\",\\"saleCount\\":(?P<saleCount>.*?),.*?\}.*?',re.S)
        sku = objSKU.finditer(savedPage)
        temp = []
        for i in sku:
            if i.group('skuName') not in temp:
                temp.append(i.group('skuName'))
                csvwriter.writerow(['', '', '', '', '', '', i.group('skuName') ,  i.group('skuPrice'),  i.group('saleCount')])
        temp.clear()
    else:
        #写入文件：
        csvwriter.writerow([productTitle.group('productTitle'), storeName.group('companyName'), storeName.group('address'), shippingCost.group('shipping'), moq.group('moq'), priceRange.group('priceRange')])

count = 1 #计数器
for product_url in urlList:
    get_product(product_url)
    print("done ",count, '/', len(urlList))
    count += 1
    sleep(randint(3,5)) #随机等待3-5秒抓取下一个
f.close()#关闭文件写入
