import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import GappedSquareModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SquareGradiantColorMask
from PIL import Image, ImageDraw

def generate_pure_qr_code(content, file_name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(image_factory=StyledPilImage, color_mask=RadialGradiantColorMask(), module_drawer=GappedSquareModuleDrawer())
    img.save(file_name + '_pure.png')
    return img

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def generate_logo_qr_code(content, file_name):
    qr_img = generate_pure_qr_code(content, file_name)
    icon = Image.open('files/source/WX20240303-210530@2x.png')
    icon = add_corners(icon, 100)
    # 获取图片的宽高
    img_w, img_h = qr_img.size
    # 参数设置logo的大小
    factor = 6
    size_w = int(img_w / factor)
    size_h = int(img_h / factor)
    icon_w, icon_h = icon.size
    if icon_w > size_w:
        icon_w = size_w
    if icon_h > size_h:
        icon_h = size_h
    # 重新设置logo的尺寸
    icon = icon.resize((icon_w, icon_h), Image.LANCZOS)
    # 得到画图的x，y坐标，居中显示
    w = int((img_w - icon_w) / 2)
    h = int((img_h - icon_h) / 2)
    # 黏贴logo照
    qr_img.paste(icon, (w, h), mask=None)  # 把前景图粘进背景图中
    qr_img.save(file_name + ".png")
    return qr_img

if __name__ == '__main__':
    generate_logo_qr_code("https://kimi.moonshot.cn/chat/cnku52maofoh2m4o938g","qqqqq")