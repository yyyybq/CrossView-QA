import re

def get_image_order(question):
    # 使用正则表达式找到所有的 <imageX> 标签
    pattern = r"<image(\d+)>"
    matches = re.findall(pattern, question)
    # print(matches)
    # print(map(int, matches))
    # 将找到的标签转换为整数，并排序
    # image_order = sorted(map(int, matches))
    image_order = list(map(int, matches))
    return image_order