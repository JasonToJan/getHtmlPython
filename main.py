import tkinter
import tkinter as tk
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os
from bs4 import BeautifulSoup
import urllib.request
from PIL import Image
import shutil
import zipfile
from tkinter import filedialog
import tempfile
import threading
import tkinter.messagebox
import re
import codecs
from tkinter import ttk
from functools import partial
from tkinter import messagebox
import importlib.util


class App:
    def __init__(self, root):
        self.modules = {}  # 用于跟踪已经加载的模块

        self.root = root
        self.root.title("网页内容提取")

        left_frame = tk.Frame(self.root, width=350)
        left_frame.pack(side='left', fill='y')

        self.url_entry = tk.Text(left_frame, width=100, height=5)  # 使用Text组件并设置高度为5
        self.url_entry.pack(padx=16, pady=16)
        self.url_entry.bind('<Return>', self.on_return)

        self.upload_button = tk.Button(left_frame, text="上传文件", command=self.upload_file)
        self.upload_button.pack(padx=16, pady=4)

        self.confirm_button = tk.Button(left_frame, text="第一步：获取所有链接html", command=self.get_html)
        self.confirm_button.pack(padx=16, pady=4)

        self.export_button = tk.Button(left_frame, text="导出：所有html", command=self.export_html)
        self.export_button.pack(padx=16, pady=4)

        self.clear_button = tk.Button(left_frame, text="清空数据", command=self.clear_urls)
        self.clear_button.pack(padx=16, pady=4)

        # 创建一个水平滚动条
        xscrollbar = tk.Scrollbar(left_frame, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')

        # 创建一个Listbox，并设置水平滚动条
        self.url_list = tk.Listbox(left_frame, xscrollcommand=xscrollbar.set, height=30)
        self.url_list.pack(side='left', fill='both', expand=True)
        self.url_list.pack(fill='both', padx=16, pady=16)
        self.url_list.bind('<<ListboxSelect>>', self.on_list_select)

        # 将滚动条的移动与Listbox的水平视图的移动关联起来
        xscrollbar.config(command=self.url_list.xview)

        # self.url_list = tk.Listbox(left_frame, height=30)

        right_frame = tk.Frame(self.root)
        right_frame.pack(side='right', fill='both', expand=True)

        self.result_text = tk.Text(right_frame)
        self.result_text.pack(fill='both', expand=True)

        left_frame.pack_propagate(False)

        self.urls = []  # Store the urls
        self.htmls = {}  # Store the htmls

        lower_right_frame = tk.Frame(right_frame)
        lower_right_frame.pack(side='bottom', fill='both', expand=True)

        # 创建一个新的Frame来替代原来的text1
        text1_frame = tk.Frame(lower_right_frame)

        # 创建一个新的Frame来容纳按钮
        button_frame = tk.Frame(text1_frame)

        # 在新的Frame的顶部添加两个按钮
        button1 = tk.Button(button_frame, text='新建解析规则（GPT4）', command=self.handle_button1_click)
        button2 = tk.Button(button_frame, text='编辑域名映射关系', command=self.handle_button2_click)
        button3 = tk.Button(button_frame, text='自动匹配现有规则', command=self.handle_button3_click)
        button4 = tk.Button(button_frame, text="导出图片", command=self.start_export_images)
        # 创建一个用于显示loading信息的标签
        self.loading_label = tk.Label(button_frame)

        button1.pack(side='left', padx=5, pady=5)  # padx和pady参数用于设置按钮的外边距
        button2.pack(side='left', padx=5, pady=5)
        button3.pack(side='left', padx=5, pady=5)
        button4.pack(side='left', padx=5, pady=5)
        self.loading_label.pack(side='left', padx=5, pady=5)

        button_frame.pack(side='top', fill='x')

        # 在新的Frame的底部添加一个文本框
        text = tk.Text(text1_frame)
        text.pack(padx=5, pady=5, fill='both', expand=True)  # fill和expand参数用于设置文本框的大小和是否随窗口大小改变而改变

        self.tree = ttk.Treeview(text)
        # 添加两个列
        self.tree["columns"] = ("one", "two")
        # 设置每一个列的宽度和标题
        self.tree.column("#0", width=80)
        self.tree.column("one", width=320)
        # self.tree.column("two", width=100)
        self.tree.heading("one", text="链接")
        self.tree.heading("two", text="解析方式")

        for i, url in enumerate(self.urls):
            # 在 "two" 列中插入 "Button" 文本
            self.tree.insert("", i, text="第" + str(i+1) + "个链接", values=(url, "选择规则文件"))
        # for i in range(10):
        #     # 在 "two" 列中插入 "Button" 文本
        #     self.tree.insert("", i, text="第" + str(i) +"个链接", values=("https://", "选择规则文件"))
        # 绑定 <Button-1> 事件
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.pack(side='top', fill='both', expand=True)

        text1_frame.grid(row=1, column=0, sticky='nsew')  # 使用'nsew'使得text1_frame填充其所在的单元格

        # 创建第二个文本框
        text2 = tk.Text(lower_right_frame)
        text2.grid(row=1, column=1, sticky='ew')

        # 配置列的权重
        lower_right_frame.grid_columnconfigure(0, weight=1)
        lower_right_frame.grid_columnconfigure(1, weight=1)

        # 配置行的权重，使得text1_frame和text2能够随着窗口大小的改变而改变大小
        lower_right_frame.grid_rowconfigure(1, weight=1)

    def handle_button1_click(self):
        # 创建新窗口
        new_window = tk.Toplevel()

        # 创建大编辑框
        text_box = tk.Text(new_window, width=100, height=30)
        text_box.pack()

        # 创建Label和小编辑框
        label = tk.Label(new_window, text="文件命名:")
        label.pack()
        entry = tk.Entry(new_window)
        entry.pack()

        def save_file():
            filename = entry.get()
            content = text_box.get("1.0", "end-1c")  # 从开始到结束获取文本框中的内容

            # 给文件名加上 .py 后缀
            filename += ".py"

            # 检查 python 目录是否存在，如果不存在，就创建这个目录
            if not os.path.exists("python"):
                os.mkdir("python")

            # 将文件保存到 python 目录中
            filename = os.path.join("python", filename)

            if filename:  # 如果文件名非空
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Success", "File saved successfully")
                    new_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            else:
                messagebox.showerror("Error", "Filename cannot be empty")

        save_button = tk.Button(new_window, text='保存', command=save_file)
        save_button.pack()

    def handle_button2_click(self):
        # 读取当前目录下mapper文件夹中的map.txt文件，如果不存在这个文件夹或者这个文件，则新建这个文件夹或文件。
        if not os.path.exists('mapper'):
            os.makedirs('mapper')

        if not os.path.isfile('mapper/map.txt'):
            with open('mapper/map.txt', 'w') as f:
                pass

        # 显示在一个 new_window = tk.Toplevel() 这个窗口中
        new_window = tk.Toplevel()
        new_window.title("Map.txt Editor")
        new_window.geometry("800x600")

        # 窗口顶部是一个 text_box = tk.Text(new_window, width=100, height=30)
        text_box = tk.Text(new_window, width=100, height=30)
        text_box.pack()

        # 显示map.txt中的数据
        with open('mapper/map.txt', 'r') as f:
            data = f.read()
            text_box.insert('1.0', data)

        # 下方是一个保存按钮，点击保存后，会更新这个文件，并关闭这个窗口。
        save_button = tk.Button(new_window, text="保存", command=lambda: self.save_text(text_box, new_window))
        save_button.pack(padx=5, pady=10)

    def save_text(self, text_box, window):
        data = text_box.get('1.0', 'end-1c')
        with open('mapper/map.txt', 'w') as f:
            f.write(data)
        messagebox.showinfo("Saved", "Data has been saved to map.txt")
        window.destroy()

    def handle_button3_click(self):
        # 你的处理代码
        print("Button 3 clicked")
        # 使用函数
        mapper = self.create_dict_from_file('mapper/map.txt')
        print(mapper)
        # 遍历字典
        for key in mapper:
            # 遍历Treeview的每一行
            for item in self.tree.get_children():
                # 获取当前行的URL
                url = self.tree.item(item)['values'][0]
                # 如果URL包含字典的键
                if key in url:
                    # 更新该行的第二个值为字典的值
                    self.tree.item(item, values=(url, mapper[key]))

    def on_tree_click(self, event):
        # 获取点击的 item 的 id 和列
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        # 如果点击的是 "two" 列
        if column == "#2":
            # 获取 item 的 text
            item_text = self.tree.item(item_id, "text")
            # 打印 item 的 text
            print(item_text)

    def on_return(self, event):
        text_box_content = self.url_entry.get('1.0', 'end-1c').splitlines()
        for line in text_box_content:
            stripped_line = line.strip()
            if stripped_line:
                self.urls.append(stripped_line)
                self.url_list.insert(tk.END, stripped_line)
        for i, url in enumerate(self.urls):
            # 在 "two" 列中插入 "Button" 文本
            self.tree.insert("", i, text="第" + str(i+1) + "个链接", values=(url, "选择规则文件"))

    def upload_file(self):
        filename = filedialog.askopenfilename()
        with codecs.open(filename, 'r', encoding='utf-8-sig') as file:
            content = file.read()
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        for url in urls:
            self.urls.append(url)
            self.url_list.insert(tk.END, url)
        for i, url in enumerate(self.urls):
            # 在 "two" 列中插入 "Button" 文本
            self.tree.insert("", i, text="第" + str(i+1) + "个链接", values=(url, "选择规则文件"))

    def get_html(self):
        # Check if output directory exists, if not, create it
        # if not os.path.exists('output'):
        #     os.makedirs('output')

        # for i, url in enumerate(self.urls):
        #     response = requests.get(url)
        #     soup = BeautifulSoup(response.text, 'html.parser')
        #     self.htmls[url] = soup.prettify()
        #     # Save html to file
        #     with open(f'output/{i + 1}.html', 'w', encoding='utf-8') as file:
        #         file.write(soup.prettify())
        # Display the first html

        self.get_html_by_firefox()

        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, self.htmls[self.urls[0]])

    def get_html_by_firefox(self):

        # 创建一个新的浏览器实例
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')

        # 如果你已经将geckodriver添加到了你的PATH环境变量，那么你可以省略executable_path参数。
        driver = webdriver.Firefox(options=options)

        # 创建输出文件夹
        if not os.path.exists('outputHtml'):
            os.makedirs('outputHtml')

        # 创建图片url输出文件夹
        if not os.path.exists('outputUrl'):
            os.makedirs('outputUrl')

        # 创建图片输出文件夹
        if not os.path.exists('outputImage'):
            os.makedirs('outputImage')

        # file_num = 1
        for url in self.urls:
            driver.get(url)

            time.sleep(4)

            # 滚动5次，每次滚动500px
            for times in range(3):
                print("尝试滚动....", times)
                # 执行JavaScript代码进行滚动
                driver.execute_script("window.scrollBy(0,500);")

                # 等待2秒
                time.sleep(8)

            # 此时，页面应该已经滚动到了适当的位置，你可以获取页面内容
            page_source = driver.page_source

            self.htmls[url] = page_source

            # 保存页面源码到文件
            print("开始保存页面源码到文件...")
            with open(f'outputHtml/{self.format_url(url)}.txt', 'w', encoding='utf-8') as f:
                f.write(page_source)

            # # 使用BeautifulSoup解析页面并提取所有图片链接
            # soup = BeautifulSoup(page_source, 'html.parser')
            # img_tags = soup.find_all('img')
            # img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]

            # soup = BeautifulSoup(page_source, 'html.parser')
            # img_tags = soup.find_all('img')
            # img_urls = []
            # for img in img_tags:
            #     if 'src' in img.attrs and img['src'].startswith('http') and not re.search(r'\.(svg|gif)',
            #                                                                               img['src']) and not img[
            #         'src'].endswith('1x1.png'):
            #         url = img['src']
            #         img_urls.append(url)
            #
            # # Find all 'source' tags
            # sources = soup.find_all('source')
            #
            # # Iterate over all 'source' tags
            # for source in sources:
            #     # Check if the tag has a 'srcset' attribute
            #     if 'srcset' in source.attrs:
            #         # Extract the value of the 'srcset' attribute
            #         srcset_value = source['srcset']
            #         # Split the 'srcset' attribute value
            #         srcset_parts = srcset_value.split(', ')
            #         # If the 'srcset' attribute value contains at least two parts, then extract the second URL
            #         if len(srcset_parts) >= 2:
            #             url = srcset_parts[1].split(' ')[0]
            #             # Check if the URL ends with .png, .jpg or .jpeg
            #             img_urls.append(url)
            #
            # # 只获取前50张图片的链接
            # img_urls = img_urls[:50]
            #
            # # 保存图片链接到文件
            # print("开始保存图片链接到文件...")
            # with open(f'outputUrl/{file_num}.txt', 'w', encoding='utf-8') as f:
            #     for img_url in img_urls:
            #         f.write(img_url + '\n')
            #
            # # print("开始下载图片了哦...")
            # # # 从文件中读取图片链接
            # # with open(f'outputUrl/{file_num}.txt', 'r', encoding='utf-8') as f:
            # #     img_urls = [line.strip() for line in f]
            # #
            # # if not os.path.exists(f'outputImage/{file_num}'):
            # #     os.makedirs(f'outputImage/{file_num}')
            # #
            # # for i, img_url in enumerate(img_urls):
            # #     # 下载图片
            # #     response = requests.get(img_url, stream=True)
            # #     response.raise_for_status()
            # #
            # #     # 将图片保存到本地
            # #     img_path = f'outputImage/{file_num}/img_{i}.jpg'
            # #     with open(img_path, 'wb') as out_file:
            # #         out_file.write(response.content)
            # #
            # #     # 使用PIL库打开图片并获取尺寸
            # #     img = Image.open(img_path)
            # #     width, height = img.size
            # #
            # #     # 关闭打开的图片
            # #     img.close()
            # #
            # #     # 如果图片尺寸小于100*150，删除图片
            # #     if width < 100 or height < 150:
            # #         os.remove(img_path)

            # 继续下一个链接
            # file_num += 1

        # 不要忘记关闭浏览器
        driver.quit()

    def on_list_select(self, event):
        # Get selected url
        selected_url = self.url_list.get(self.url_list.curselection())
        # Clear the text
        self.result_text.delete('1.0', tk.END)
        # Insert the html of selected url
        self.result_text.insert(tk.END, self.htmls[selected_url])

    def export_html(self):
        # 创建一个临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, (url, html) in enumerate(self.htmls.items()):
                filename = os.path.join(temp_dir, f'{self.format_url(url)}.txt')
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(html)

            # 选择保存的压缩文件路径
            zip_filename = filedialog.asksaveasfilename(defaultextension=".zip")
            # 创建一个新的zip文件，然后将临时目录中的所有文件添加到这个zip文件中
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)

    def start_export_images(self):
        # 启动一个新的线程来执行图片导出任务
        threading.Thread(target=self.export_images).start()

        # 更新按钮和标签的状态
        self.export_button['state'] = 'disabled'
        self.loading_label['text'] = '正在导出图片，请稍等...'

    def finish_export_images(self):
        # 更新按钮和标签的状态
        self.export_button['state'] = 'normal'
        self.loading_label['text'] = ''

        # 显示一个消息框来告知用户任务已经完成
        tkinter.messagebox.showinfo("导出完成", "所有图片已经成功导出并打包成zip文件。")

    def export_images(self):
        mapper = self.create_dict_from_file('mapper/map.txt')

        # 遍历outputUrl目录中的所有文件
        for filename in os.listdir('outputHtml'):
            html_file_path = os.path.join('outputHtml', filename)  # 连接目录名和文件名
            basename = os.path.splitext(filename)[0]
            match, value = self.match_basename_with_mapper(mapper, basename)
            if match:
                print(f'Successfully matched with value: {value}')
                if not value.endswith('.py'):  # 检查文件名是否以'.py'结尾
                    value += '.py'  # 如果不是，添加'.py'
                current_dir = os.getcwd()  # 获取当前目录
                file_dir = os.path.join(current_dir, 'python')  # 连接当前目录和'python'文件夹
                file_path = os.path.join(file_dir, value)  # 连接'python'文件夹和文件名
                print('目标解析文件：' + file_path)
                self.some_function(file_path, html_file_path)

            else:
                print('No match found')

        # 让用户选择zip文件的保存位置
        zip_file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".zip")

        # 创建一个zip文件并将所有的图片添加进去
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk('outputImage'):
                for file in files:
                    zipf.write(os.path.join(root, file))

        print('图片导出完毕，已打包成zip文件.')
        # 当所有图片都已经导出，调用finish_export_images方法
        self.finish_export_images()

    def match_basename_with_mapper(self, mapper, basename):
        for key, value in mapper.items():
            modified_key = key.replace('http://', '').replace('https://', '').replace('/', '_').replace('.', '_').replace('&', '_').replace('?', '_')
            if modified_key in basename:
                return True, value
        return False, None

    def clear_urls(self):
        self.urls.clear()
        self.url_list.delete(0, tk.END)
        self.result_text.delete('1.0', tk.END)  # 清空文本框内容

        # 删除文件夹
        outputHtml_folder = 'outputHtml'
        outputUrl_folder = 'outputImage'
        if os.path.exists(outputHtml_folder):
            shutil.rmtree(outputHtml_folder)
        if os.path.exists(outputUrl_folder):
            shutil.rmtree(outputUrl_folder)

        # 清空htmls列表
        self.htmls.clear()

    def create_dict_from_file(self, filepath):
        mapper = {}
        with open(filepath, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:  # Ignore empty lines
                    continue
                parts = re.split(r'\s+', stripped_line, maxsplit=1)
                if len(parts) < 2:
                    print(f"Warning: Skipping line without space: {stripped_line}")
                    continue
                key, value = parts
                mapper[key] = value
        return mapper

    def format_url(self, url):
        url = url.replace('https://', '').replace('http://', '')
        url = url.replace('/', '_').replace('?', '_').replace('.', '_').replace('&', '_')
        return url

    # 动态加载外部python文件
    def some_function(self, module_path, html_file_path):
        print("module_path=" + module_path + " html_path=" + html_file_path)
        # 检查模块是否已经在字典中
        if module_path in self.modules:
            module = self.modules[module_path]
            print("加载已存在的" + module_path + "成功")
        else:
            # 从文件路径中提取文件名（不包括扩展名）
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 将模块添加到字典中
            self.modules[module_path] = module
            print("动态加载" + module_path + "成功")

        # 创建类的实例并调用方法
        downloader = module.ImageDownloader()
        downloader.getImage(html_file_path)


if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(1200, 800)  # 设置最小大小为宽度1200和高度800
    App(root)
    root.mainloop()
