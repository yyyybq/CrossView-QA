from PIL import Image, ImageDraw, ImageFont
import json
import os
import re
# =================配置区=================
# input_json_path = "/home/baiqiao/MVSR/exp/reasoning/InternVL2_5-8B__answers.jsonl"  # 你的JSON文件路径
input_json_path = r"C:\Users\FS139\Desktop\qa_release\rotation.jsonl"
image_base_dir = r'D:\data\image_annotation'  # 图像基础目录
# output_dir = "/home/baiqiao/MVSR/exp/reasoning/output_visuals_intern/"       # 输出目录
output_dir = r"C:\Users\FS139\Desktop\exp_Chat"       # 输出目录
# font_path = "/usr/share/fonts/truetype/arial.ttf"              # linux
font_path = r"C:\Windows\Fonts\arial.ttf"              #window
# ========================================

def create_visualization(data_entry):
    # if 'gen_6_1' in data_entry["id"]:
    if 'q2_1' in data_entry["id"]:
        # 创建画布 (宽度1200，高度根据内容自适应)
        canvas = Image.new('RGB', (750, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        # ========== 上半部分：图像展示 ==========
        image_row = []
        max_height = 0
        
        # 加载所有图像
        for img_path in data_entry["images"]:
            full_path = os.path.join(image_base_dir, img_path)
            try:
                img = Image.open(full_path)
                img = img.resize((180, 140))  # 统一图像尺寸
                image_row.append(img)
                max_height = max(max_height, img.height)
            except Exception as e:
                print(f"无法加载图像 {full_path}: {str(e)}")
                continue

        # 水平拼接图像
        if image_row:
            combined_width = sum(img.width for img in image_row)
            combined_img = Image.new('RGB', (combined_width, max_height))
            x_offset = 0
            for img in image_row:
                combined_img.paste(img, (x_offset, 0))
                x_offset += img.width
            canvas.paste(combined_img, (50, 50))

        # ========== 下半部分：文本展示 ==========
        y_position = 200  # 从图像下方开始
        
        # 设置字体
        try:
            font = ImageFont.truetype(font_path, 20)
            bold_font = ImageFont.truetype(font_path, 22)
        except:
            font = ImageFont.load_default()
            bold_font = ImageFont.load_default()

        # 绘制问题文本（自动换行）
        question = data_entry["question"]
        lines = []
        current_line = []
        max_width = 600  # 留出边距
        
        for word in question.split():
            test_line = ' '.join(current_line + [word])
            width = draw.textlength(test_line, font=font)
            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        # 绘制问题
        for line in lines:
            draw.text((50, y_position), line, font=bold_font, fill=(0, 0, 0))
            y_position += 30

        # 绘制答案对比
        answer_info = [
            ("正确答案", data_entry["gt_answer"], (0, 128, 0)),
            # ("模型回答", data_entry["model_answer"].split("Therefore")[0].strip(), (255, 0, 0))
            ("模型回答", data_entry["gt_answer"], (255, 0, 0))
        ]
        
        for label, text, color in answer_info:
            y_position += 20  # 段间距
            draw.text((50, y_position), f"{label}:", font=bold_font, fill=color)
            y_position += 30
            
            text_lines = []
            current_line = []
            for word in text.split():
                test_line = ' '.join(current_line + [word])
                width = draw.textlength(test_line, font=font)
                if width <= max_width:
                    current_line.append(word)
                else:
                    text_lines.append(' '.join(current_line))
                    current_line = [word]
            text_lines.append(' '.join(current_line))
            
            for line in text_lines:
                draw.text((70, y_position), line, font=font, fill=color)
                y_position += 25

        # 保存结果
        output_path = os.path.join(output_dir, f"{data_entry['id']}.jpg")
        canvas.save(output_path)
        print(f"已生成：{output_path}")

# ========== 主流程 ==========
if __name__ == "__main__":
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取JSON数据
    with open(input_json_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                match = re.search(r"group(\d+)", data["id"])
                group_id = int(match.group(1))
               
                # if (group_id>220 and group_id<240) or (group_id>262 and group_id<280):
                create_visualization(data)
            except json.JSONDecodeError:
                print("JSON解析错误，跳过当前行")