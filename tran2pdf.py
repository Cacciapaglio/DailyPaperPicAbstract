import fitz  # PyMuPDF
from PIL import Image


def pdf_to_long_image(pdf_path, output_image_path, zoom=1.0):
    # 打开PDF文件
    pdf = fitz.open(pdf_path)

    # 初始化图像列表
    images = []

    # 遍历PDF的每一页
    for page_number in range(len(pdf)):
        page = pdf[page_number]
        # 渲染页面为图像
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), dpi=200)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(image)

    # 关闭PDF文件
    pdf.close()

    # 只有一张图片，直接保存
    if len(images) == 1:
        images[0].save(output_image_path)
        return output_image_path

    top = 220

    # 将图像列表转换为长图
    long_image = Image.new('RGB', (images[0].size[0], sum(image.size[1] for image in images) - len(images)*top*2 ))

    # 将每一页的图像粘贴到长图上
    y_offset = 0
    for index, image in enumerate(images):
        t = top if index != 0 else 0
        image = image.crop((0, t, image.size[0], image.size[1]-top))
        long_image.paste(image, (0, y_offset))
        y_offset += image.size[1]

    # 保存长图
    long_image.save(output_image_path)
    return output_image_path


def pdf_to_png(pdf_path, output_folder, zoom=1.0):
    # 打开PDF文件
    pdf = fitz.open(pdf_path)
    for page_number in range(len(pdf)):
        # 获取页面
        page = pdf[page_number]
        # 获取页面的像素图
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), dpi=200)
        # 保存为PNG
        output_image_path = f"{output_folder}/page_{page_number + 1}.png"
        pix.save(output_image_path)
    pdf.close()
    return f"{output_folder}/page_1.png"

def add_qr_code(source_img, qr_code_img):
    from PIL import Image

    # 打开第一张图片
    image = Image.open(source_img)

    # 打开二维码图片
    qrcode = Image.open(qr_code_img)
    # 获取二维码图片的尺寸
    qrcode_width, qrcode_height = qrcode.size

    # 如果需要将二维码图片改为固定大小，可以这样做
    new_qrcode_width = 200  # 假设我们想要的宽度是100像素
    new_qrcode_height = int(new_qrcode_width * (qrcode_height / qrcode_width))
    qrcode = qrcode.resize((new_qrcode_width, new_qrcode_height), Image.Resampling.LANCZOS)
    # 创建一个新的图片，用于存放最终结果
    result_image = Image.new("RGB", (image.width, image.height))

    # 将第一张图片粘贴到结果图片上
    result_image.paste(image, (0, 0))

    new_qrcode_left = image.width - new_qrcode_width
    new_qrcode_top = image.height - new_qrcode_height
    # 将调整大小后的二维码图片粘贴到结果图片的右下角
    result_image.paste(qrcode, (new_qrcode_left-220, new_qrcode_top-40))
    # 保存新的图片
    result_image.save(source_img)


if __name__ == '__main__':
    # 使用函数
    pdf_to_long_image("files/result/2024-03-08/Backtracing: Retrieving the Cause of the QueryAbstract.pdf", "long.png")