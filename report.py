import os.path

from reportlab.pdfbase import pdfmetrics   # 注册字体
from reportlab.pdfbase.ttfonts import TTFont # 字体类
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph, Image  # 报告内容相关类
from reportlab.lib.pagesizes import letter  # 页面的标志尺寸(8.5*inch, 11*inch)
from reportlab.lib.styles import getSampleStyleSheet  # 文本样式
from reportlab.lib import colors  # 颜色模块
from reportlab.graphics.charts.barcharts import VerticalBarChart  # 图表类
from reportlab.graphics.charts.legends import Legend  # 图例类
from reportlab.graphics.shapes import Drawing  # 绘图工具
from reportlab.lib.units import cm  # 单位：cm
from huggingface import PaperAbstract
from qr_code import generate_logo_qr_code
from PIL import Image as PImage

content_font_name = "SimSun"
title_font_name = "Arial Rounded Bold"
sub_title_font_name = title_font_name


# 注册字体(提前准备好字体文件, 如果同一个文件需要多种字体可以注册多个)
pdfmetrics.registerFont(TTFont(sub_title_font_name, sub_title_font_name+'.ttf'))
pdfmetrics.registerFont(TTFont(content_font_name, content_font_name + '.ttf'))
pdfmetrics.registerFont(TTFont("SimSun", 'SimSun.ttf'))
pdfmetrics.registerFont(TTFont(title_font_name, 'Arial Rounded Bold.ttf'))


class Graphs:
    # 绘制标题
    @staticmethod
    def draw_title(title: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 拿到标题样式
        ct = style['Heading1']
        # 单独设置样式相关属性
        ct.spaceBefore = 0.5 * cm
        ct.fontName = 'Arial Rounded Bold'  # 字体名
        ct.fontSize = 18  # 字体大小
        ct.leading = 20  # 行间距
        # ct.textColor = colors.plum  # 字体颜色
        ct.alignment = 0  # 居左
        ct.bold = True
        # 创建标题对应的段落，并且返回
        return Paragraph(title, ct)

    # 绘制小标题
    @staticmethod
    def draw_little_title(title: str):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 拿到标题样式
        ct = style['Normal']
        # 单独设置样式相关属性
        ct.fontName = 'SimSun'  # 字体名
        ct.fontSize = 15  # 字体大小
        ct.leading = 30  # 行间距
        ct.textColor = colors.grey  # 字体颜色
        # 创建标题对应的段落，并且返回
        return Paragraph(title, ct)

    # 绘制普通段落内容
    @staticmethod
    def draw_text(text: str, alignment=0):
        # 获取所有样式表
        style = getSampleStyleSheet()
        # 获取普通样式
        ct = style['Normal']
        ct.fontName = content_font_name
        ct.fontSize = 14
        ct.spaceBefore = 0.3*cm # 和前面间隔多远
        ct.wordWrap = 'CJK'  # 设置自动换行
        ct.alignment = alignment  # 左对齐
        # ct.leading = 5  # 行间距
        # ct.firstLineIndent = 32  # 第一行开头空格
        ct.leading = 14 * 1.5
        return Paragraph(text, ct)

    # 绘制表格
    @staticmethod
    def draw_table(*args):
        # 列宽度
        col_width = 120
        style = [
            ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),  # 字体
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # 第一行的字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # 第二行到最后一行的字体大小
            ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'),  # 设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 第一行水平居中
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # 第二行到最后一行左右左对齐
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有表格上下居中对齐
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
            # ('SPAN', (0, 1), (0, 2)),  # 合并第一列二三行
            # ('SPAN', (0, 3), (0, 4)),  # 合并第一列三四行
            # ('SPAN', (0, 5), (0, 6)),  # 合并第一列五六行
            # ('SPAN', (0, 7), (0, 8)),  # 合并第一列五六行
        ]
        table = Table(args, colWidths=col_width, style=style)
        return table

    # 创建图表
    @staticmethod
    def draw_bar(bar_data: list, ax: list, items: list):
        drawing = Drawing(500, 250)
        bc = VerticalBarChart()
        bc.x = 45  # 整个图表的x坐标
        bc.y = 45  # 整个图表的y坐标
        bc.height = 200  # 图表的高度
        bc.width = 350  # 图表的宽度
        bc.data = bar_data
        bc.strokeColor = colors.black  # 顶部和右边轴线的颜色
        bc.valueAxis.valueMin = 5000  # 设置y坐标的最小值
        bc.valueAxis.valueMax = 26000  # 设置y坐标的最大值
        bc.valueAxis.valueStep = 2000  # 设置y坐标的步长
        bc.categoryAxis.labels.dx = 2
        bc.categoryAxis.labels.dy = -8
        bc.categoryAxis.labels.angle = 20
        bc.categoryAxis.categoryNames = ax

        # 图示
        leg = Legend()
        leg.fontName = 'SimSun'
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 475  # 图例的x坐标
        leg.y = 240
        leg.dxTextSpace = 10
        leg.columnMaximum = 3
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(bc)
        return drawing


    @staticmethod
    def image_cm_size(image_path):
        # 打开图片文件
        image = PImage.open(image_path)
        # 获取图片的像素尺寸
        width_px, height_px = image.size
        # 假设的DPI值（例如，96 DPI是网页常用的分辨率）
        dpi = 96

        # 将像素转换为英寸
        width_in = width_px / dpi
        height_in = height_px / dpi

        # 将英寸转换为厘米（1英寸 = 2.54厘米）
        width_cm = width_in * 2.54
        height_cm = height_in * 2.54
        return width_cm/3.0, height_cm/3.0

    # 绘制图片
    @staticmethod
    def draw_img(path):
        # 获取图片的尺寸
        width, height = Graphs.image_cm_size(path)
        img = Image(path)  # 读取指定路径下的图片
        img.drawWidth = width * cm  # 设置图片的宽度
        img.drawHeight = height * cm # 设置图片的高度
        return img

    @staticmethod
    def draw_qr_code(path):
        img = Image(path)  # 读取指定路径下的图片
        img.drawWidth = 3 * cm  # 设置图片的宽度
        img.drawHeight = 3 * cm  # 设置图片的高度
        img.alignment = 1
        return img

class PaperReport:

    def __init__(self, paper: PaperAbstract):
        self.paper = paper

    def report_path(self):
        return os.path.join(self.paper.paper_dir, self.paper.title_zh + '.pdf')

    def pic_report_path(self):

        return os.path.join(self.paper.paper_dir, self.paper.title_zh + ".png")

    def generate(self, file_name):
        # 创建内容对应的空列表
        content = list()

        # 添加图片
        content.append(Graphs.draw_img(self.paper.cover_local_path()))

        # 添加论文标题
        content.append(Graphs.draw_title(self.paper.title))
        # 添加论文副标题
        content.append(Graphs.draw_little_title(self.paper.title_zh))
        # 添加正文
        content.append(Graphs.draw_text(self.paper.abstract_zh))
        # 添加二维码
        generate_logo_qr_code(self.paper.arxiv_url, os.path.join(self.paper.get_images_dir(), "qrCode"))

        # 生成pdf文件
        doc = SimpleDocTemplate(self.report_path(), pagesize=letter)
        doc.build(content)
        return self.report_path()


if __name__ == '__main__':
    # 创建内容对应的空列表

    demo_paper = PaperAbstract("files/result/2024-03-08/SaulLM-7B: A pioneering Large Language Model for Law/")
    demo_paper.title = 'Panda-70M: Captioning 70M Videos with Multiple Cross-Modality Teachers'
    demo_paper.title_zh = "Panda-70M：使用多个跨模态教师为70M视频添加字幕"
    demo_paper.abstract_zh = "我们将现实世界的人形机器人控制问题视为下一个标记预测问题，类似于在语言中预测下一个单词。我们的模型是一种因果变压器，通过自回归预测感知运动轨迹进行训练。为了考虑到数据的多元模态特性，我们以模态对齐的方式进行预测，对于每个输入标记，预测来自同一模态的下一个标记。这种通用公式使我们能够利用缺失模态的数据，例如没有动作的视频轨迹。我们在一组来自先前神经网络策略、基于模型的控制器、动作捕捉数据以及YouTube上人类视频的模拟轨迹上训练我们的模型。我们展示了我们的模型能够让一个全尺寸的人形机器人在无需预训练的情况下直接在旧金山行走。即使只在27小时的行走数据上进行训练，我们的模型也能转移到现实世界，并且能够泛化到训练期间未见过的命令，如后退走。这些发现表明，通过感知运动轨迹的生成建模，为学习具有挑战性的现实世界控制任务提供了一条有前景的道路。"
    demo_paper.arxiv_url = "https://arxiv.org/abs/2402.19469.pdf"
    pr = PaperReport(demo_paper)
    pr.generate(demo_paper.title)
