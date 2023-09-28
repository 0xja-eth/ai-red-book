
# 缩放图片
def resize_image(image, target_width, target_height):
    # 获取原始图片的宽度和高度
    width, height = image.size

    # 计算缩放比例
    width_ratio = target_width / width
    height_ratio = target_height / height
    ratio = max(width_ratio, height_ratio)

    # 计算调整后的图片尺寸
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # 缩放图片
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # 裁剪图片到目标尺寸
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    resized_image = resized_image.crop((left, top, right, bottom))

    return resized_image


# 生成九宫格
def generate_9_pic(files):
    images = [Image.open(file) for file in files]

    # 获取图片的宽高（第一张图为准）
    image_width, image_height = images[0].size

    # 创建新图片，尺寸为3倍的宽度和高度
    result_width = image_width * 3
    result_height = image_height * 3
    result_image = Image.new('RGB', (result_width, result_height))

    # 将九张图片按照九宫格排列拼接到新图片上
    for i in range(3):
        for j in range(3):
            resized_image = resize_image(images[i * 3 + j], image_width, image_height)
            result_image.paste(resized_image, (j * image_width, i * image_height))

    return result_image


# 生成四宫格
def generate_4_pic(files):
    images = [Image.open(file) for file in files]

    # 获取图片的宽高（第一张图为准）
    image_width, image_height = images[0].size

    # 创建新图片，尺寸为3倍的宽度和高度
    result_width = image_width * 2
    result_height = image_height * 2
    result_image = Image.new('RGB', (result_width, result_height))

    # 将九张图片按照九宫格排列拼接到新图片上
    for i in range(2):
        for j in range(2):
            resized_image = resize_image(images[i * 2 + j], image_width, image_height)
            result_image.paste(resized_image, (j * image_width, i * image_height))

    return result_image


# 生成图片标题
def add_pic_title(image):
    width, height = image.size

    title_img = Image.open(TITLE_PIC_FILE)
    title_width, title_height = title_img.size

    title_x, title_y = (width - title_width) // 2, (height - title_height) // 2

    image.paste(title_img, (title_x, title_y), mask=title_img)

    return image
