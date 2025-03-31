import os
import base64
from PIL import Image

# 共性函数
def replace_old_root(image_paths, new_root):
    """
    替换图片路径的根目录
    """
    updated_path = [os.path.join(new_root, os.path.basename(image_path)) for image_path in image_paths]
    return updated_path

def load_images(image_paths):
    """
    加载图片，将 RGBA 模式转换为 RGB
    """
    images = []
    for path in image_paths:
        if os.path.exists(path):
            image = Image.open(path)
            if image.mode == 'RGBA':
                image = image.convert("RGB")
            images.append(image)
        else:
            print(f"Warning: Image path {path} does not exist.")
    return images

def find_json_files(input_root):
    """
    遍历指定目录及其子目录，查找所有 .jsonl 文件
    """
    json_files = []
    for root, dirs, files in os.walk(input_root):
        for file in files:
            if file.endswith(".jsonl"):
                json_files.append(os.path.join(root, file))
    return json_files

def encode_image(image_path):
    """
    将图片编码为 Base64 格式
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')