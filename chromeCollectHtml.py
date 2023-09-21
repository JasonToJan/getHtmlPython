from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
from bs4 import BeautifulSoup
import urllib.request

# 创建一个新的浏览器实例
options = Options()
options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 读取url列表
with open('urllist.txt', 'r', encoding='utf-8') as f:
    urls = f.read().splitlines()

# 创建输出文件夹
if not os.path.exists('outputHtml'):
    os.makedirs('outputHtml')

# 创建图片输出文件夹
if not os.path.exists('outputUrl'):
    os.makedirs('outputUrl')

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
        time.sleep(5)

    # 此时，页面应该已经滚动到了适当的位置，你可以获取页面内容
    page_source = driver.page_source

    # 保存页面源码到文件
    with open(f'outputHtml/{file_num}.html', 'w', encoding='utf-8') as f:
        f.write(page_source)

    # 使用BeautifulSoup解析页面并提取所有图片链接
    soup = BeautifulSoup(page_source, 'html.parser')
    img_tags = soup.find_all('img')
    img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]

    # 保存图片链接到文件
    with open(f'outputUrl/{file_num}.txt', 'w', encoding='utf-8') as f:
        for img_url in img_urls:
            f.write(img_url + '\n')

    file_num += 1

# 不要忘记关闭浏览器
driver.quit()
