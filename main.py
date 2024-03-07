# 1. 爬取huggingface的每日paper，获取每日论文的title, abstract, arxiv url
# 2. 用智谱将摘要翻译成英文
# 3. 生成arxiv url二维码
# 4. 生成论文摘要pdf
# 5. pdf转png保存在本地
import os
from report import PaperReport
import time

from huggingface import PaperGetter
import datetime
from tran2pdf import pdf_to_long_image, add_qr_code

base_output_dir = "files/result"
format_date = datetime.datetime.today().strftime("%Y-%m-%d")
date_output_dir = os.path.join(base_output_dir, format_date)
if not os.path.exists(date_output_dir):
    os.makedirs(date_output_dir)
print("今天是：", format_date)

# 获取每日论文
pg = PaperGetter(date_output_dir)
pg.run()

start = time.time()
# 生成报告
for paper in pg.today_papers:
    pr = PaperReport(paper)
    pr.generate(pr.paper.title)
    output_img_path = pdf_to_long_image(pr.report_path(), pr.pic_report_path())
    add_qr_code(output_img_path, os.path.join(pr.paper.paper_dir, "images/qrCode.png"))
end = time.time()
print("耗时：", end - start)



