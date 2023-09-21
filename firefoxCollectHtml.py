import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
from bs4 import BeautifulSoup
import urllib.request
from PIL import Image


# 创建一个新的浏览器实例
options = Options()
options.add_argument("--start-maximized")
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')

# 如果你已经将geckodriver添加到了你的PATH环境变量，那么你可以省略executable_path参数。
driver = webdriver.Firefox(options=options)

# 读取url列表
with open('urllist.txt', 'r', encoding='utf-8') as f:
    urls = f.read().splitlines()

# 创建输出文件夹
if not os.path.exists('outputHtml'):
    os.makedirs('outputHtml')

# 创建图片url输出文件夹
if not os.path.exists('outputUrl'):
    os.makedirs('outputUrl')

# 创建图片输出文件夹
if not os.path.exists('outputImage'):
    os.makedirs('outputImage')

file_num = 1
for url in urls:
    driver.get(url)

    time.sleep(4)

    # 滚动5次，每次滚动500px
    for times in range(6):
        print("尝试滚动....", times)
        # 执行JavaScript代码进行滚动
        driver.execute_script("window.scrollBy(0,500);")

        # 等待2秒
        time.sleep(8)

    # 此时，页面应该已经滚动到了适当的位置，你可以获取页面内容
    page_source = driver.page_source

    # 保存页面源码到文件
    print("开始保存页面源码到文件...")
    with open(f'outputHtml/{file_num}.html', 'w', encoding='utf-8') as f:
        f.write(page_source)

    # 使用BeautifulSoup解析页面并提取所有图片链接
    soup = BeautifulSoup(page_source, 'html.parser')
    img_tags = soup.find_all('img')
    img_urls = [img['src'] for img in img_tags if
                'src' in img.attrs and (img['src'].endswith('.jpg') or img['src'].endswith('.jpeg'))]

    # 保存图片链接到文件
    print("开始保存图片链接到文件...")
    with open(f'outputUrl/{file_num}.txt', 'w', encoding='utf-8') as f:
        for img_url in img_urls:
            f.write(img_url + '\n')


    # print("开始下载图片了哦...")
    # # 从文件中读取图片链接
    # with open(f'outputUrl/{file_num}.txt', 'r', encoding='utf-8') as f:
    #     img_urls = [line.strip() for line in f]
    #
    # if not os.path.exists(f'outputImage/{file_num}'):
    #     os.makedirs(f'outputImage/{file_num}')
    #
    # for i, img_url in enumerate(img_urls):
    #     # 下载图片
    #     response = requests.get(img_url, stream=True)
    #     response.raise_for_status()
    #
    #     # 将图片保存到本地
    #     img_path = f'outputImage/{file_num}/img_{i}.jpg'
    #     with open(img_path, 'wb') as out_file:
    #         out_file.write(response.content)
    #
    #     # 使用PIL库打开图片并获取尺寸
    #     img = Image.open(img_path)
    #     width, height = img.size
    #
    #     # 关闭打开的图片
    #     img.close()
    #
    #     # 如果图片尺寸小于100*150，删除图片
    #     if width < 100 or height < 150:
    #         os.remove(img_path)

    # 继续下一个链接
    file_num += 1

# 不要忘记关闭浏览器
driver.quit()
