import os.path

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import time
from zhipuai import ZhipuAI
import fitz


zp_api_key = os.getenv("zp_api_key", "")
client = ZhipuAI(api_key=zp_api_key)

def translate_abstract(abstract):
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {
                "role": "user",
                "content": "你是一名专业的AI领域的翻译，请将这个论文标题或这段论文摘要翻译成中文：" + abstract
            }
        ],
        top_p=0.7,
        temperature=0.95,
        max_tokens=1024,
        stream=False,
    )

    return response.choices[0].message.content


class PaperAbstract:

    def __init__(self, paper_dir):
        self.paper_dir = paper_dir
        if not os.path.exists(self.paper_dir):
            os.makedirs(self.paper_dir)
        self.title = None
        self.title_zh = None
        self.abstract = None
        self.abstract_zh = None
        self.arxiv_url = None
        self.arxiv_pdf_url = None
        self.cover_img_url = None
        self.paper_index = None
        self.__images_dir__ = None

    def get_pdf_local_path(self):
        return os.path.join(self.paper_dir, self.title_zh + ".pdf")

    def get_images_dir(self):
        if self.__images_dir__:
            return self.__images_dir__

        dir = os.path.join(self.paper_dir, "images")
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.__images_dir__ = dir
        return dir

    def cover_local_path(self):
        img_dir = os.path.join(self.paper_dir, "images")
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        file_name = os.path.join(img_dir, "cover.png")
        return file_name

    def download_cover_img(self):
        response = requests.get(self.cover_img_url)
        # 检查请求是否成功
        if response.status_code == 200:
            file_name = self.cover_local_path()
            # 将图片内容写入文件
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"图片已下载到本地：{file_name}")
            return True
        else:
            print("图片下载失败，状态码：", response.status_code)
            return False

    def get_pdf(self):
        # 下载PDF
        print("开始下载pdf：", self.arxiv_pdf_url)
        response = requests.get(self.arxiv_pdf_url)

        if response.status_code == 200:
            print("保存pdf至：", self.get_pdf_local_path())
            # 保存PDF文件
            with open(self.get_pdf_local_path(), 'wb') as f:
                f.write(response.content)
            print("pdf下载完毕")
        else:
            print("pdf下载失败")

    def get_images(self):
        # 打开PDF文件
        print("开始保存图片")
        pdf = fitz.open(self.get_pdf_local_path())
        for page_number in range(len(pdf)):
            page = pdf[page_number]
            images = page.get_images(full=True)  # 获取页面中所有图片
            for img_index, img in enumerate(images):
                print("保存第", img_index, "张")
                xref = img[0]  # 图片的xref
                img_bytes = pdf.extract_image(xref)["image"]  # 获取图片的二进制数据
                img_filename = f"image_{img_index}.png"  # 图片文件名
                img_path = os.path.join(self.get_images_dir(), img_filename)
                with open(img_path, 'wb') as f:
                    f.write(img_bytes)  # 保存图片
        print("保存图片完毕")


class PaperGetter:

    def __init__(self, date_str):
        self.home_url = "https://huggingface.co/papers"
        self.today_papers = []
        self.date_str = date_str

    @staticmethod
    def parse_papers(page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        paper_links = []
        for a_tag in soup.find_all('a', class_='cursor-pointer'):
            href = a_tag.get('href')
            if href and href.startswith('/papers'):
                paper_links.append(f"https://huggingface.co{href}")
        return paper_links

    def parse_paper_details(self, page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        title = soup.find('h1').text.strip().replace("\n", '')
        paper_dir = os.path.join(self.date_str, title)
        paper = PaperAbstract(paper_dir)
        paper.title = soup.find('h1').text.strip()
        paper.abstract = soup.find('p').text.strip()
        for a_tag in soup.find_all('a', class_='btn inline-flex h-9 items-center'):
            href = a_tag.get("href")
            if href and href.startswith("https://arxiv.org/abs"):
                paper.arxiv_url = href
            if href and href.startswith("https://arxiv.org/pdf"):
                paper.arxiv_pdf_url = href
            if href and href.startswith("https://arxiv.org/"):
                paper.paper_index = href.split("/")[-1]
                paper.cover_img_url = "https://arxiv.org/html/" + paper.paper_index + "v1/x1.png"
        return paper

    def construct_paper_details(self, hf_paper_list):
        detail_list = []
        for paper_url in hf_paper_list:
            paper_detail = requests.get(paper_url)
            paper = self.parse_paper_details(paper_detail.text)
            paper.title_zh = translate_abstract(paper.title).replace('"','')
            paper.abstract_zh = translate_abstract(paper.abstract)
            print(paper.title)
            print(paper.title_zh)
            print(paper.abstract_zh)
            flag = paper.download_cover_img()
            if flag:
                detail_list.append(paper)
                print("")
            time.sleep(5)
        return detail_list

    def search_daily_papers(self):
        resp = requests.get(self.home_url)
        hf_paper_list = PaperGetter.parse_papers(resp.text)
        hf_paper_list = list(set(hf_paper_list))
        return hf_paper_list

    def run(self):
        hf_paper_list = self.search_daily_papers()
        self.today_papers = self.construct_paper_details(hf_paper_list)

