import json
import os
import glob
from utils import get_image_order
import re
img_dic = r'D:\data\image_annotation\other_all_image\linear'
save_root = r"D:\data\image_annotation\other_all_image\qa\linear"
json_file_path = r'C:\Users\FS139\Desktop\code\spatial\linear_relation.json'

# 读取 JSON 文件
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
all_results = []
for group_id,list in enumerate(data):
    
    image_paths = []
    img_folder_path = os.path.join(img_dic, list[0])
    output_file_path = os.path.join(save_root, list[0]) +'.json'

    extensions=['*.jpg', '*.jpeg', '*.png', '*.gif']
    for extension in extensions:
        for file_path in glob.glob(os.path.join(img_folder_path, extension), recursive=True):
            image_paths.append(file_path)
    # print(image_paths)
    questions_and_answers = {

                "questions_1": {},
                "questions_2": {},
                "answer_1": {},
                "answer_2": {}
            }
    
    obj_list = [list[2],list[3],list[4]]
    sr = [list[1].split(',')[0],list[1].split(',')[1]] if ',' in list[1] else list[1]
            
    all_scene_img_desc1 = "Based on these two sequential views of the same scene <image1><image2>,"
    all_scene_img_desc2 = "Based on these two sequential views of the same scene <image2><image1>,"
    choice1 = ' A. Above B. Below C. Left D. Right'
    choice2 = ' A. Above B. Below C. In front D. Behind'

    # 换一下图像顺序，A->B,B->C & B->C,A->B
    q1_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice1
    q1_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice1
    if isinstance(sr, str):
        if sr=='left':
            a1_1 = "C"
            a1_2 = "C"
        elif sr=='right':
            a1_1 = "D"
            a1_2 = "D"
        elif sr=='on':
            a1_1 = "A"
            a1_2 = "A"        
        elif sr=='down':
            a1_1 = "B"
            a1_2 = "B"
        elif sr=='front':
            q1_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice2
            q1_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice2
            a1_1 = "C"
            a1_2 = "C"
    else:
        if 'front' in sr:
            q1_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice2
            q1_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice2

        elif 'left' in sr or 'right' in sr:
            q1_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice1
            q1_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[0],obj_list[2]) + choice1
        a1_1 = "B"
        a1_2 = "B"

    ### 接下来变成反义词
    q2_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice1
    q2_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice1
    if isinstance(sr, str):
        if sr=='left':
            a2_1 = "D"
            a2_2 = "D"
        elif sr=='right':
            a2_1 = "C"
            a2_2 = "C"
        elif sr=='on':
            a2_1 = "B"
            a2_2 = "B"        
        elif sr=='down':
            a2_1 = "A"
            a2_2 = "A"
        elif sr=='front':
            q2_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice2
            q2_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice2
            a2_1 = "D"
            a2_2 = "D"
    else:
        if 'front' in sr:
            q2_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice2
            q2_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice2

        elif 'left' in sr or 'right' in sr:
            q2_1 = all_scene_img_desc1 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice1
            q2_2 = all_scene_img_desc2 + ' which direction is the {0} relative to the {1}?'.format(obj_list[2],obj_list[0]) + choice1
        a2_1 = "A"
        a2_2 = "A"

    qa_pairs = [[q1_1,a1_1],[q1_2,a1_2],[q2_1,a2_1],[q2_2,a2_2]]

    category = ['linear','OO','translation','self']
    # 查找匹配的元数据信息

    meta_info = list[1:]  # 获取除了文件名之外的所有信息
         
    
    # 如果没找到匹配的元数据，使用默认选项
    if meta_info is None:
        meta_info = ["A", "B", "C", "D"]
    # 创建结果列表
    results = []
    
    # 处理第一组问题和答案
    for id, qa in enumerate(qa_pairs):
        question = qa[0]
        answer = qa[1]   
        reason_type = "forward reasoning" if id%2==0 else "inverse reasoning"


        image_order = get_image_order(question)
        img_num = len(image_paths)
        required_images = []
        for i in image_order:
                required_images.append(image_paths[i-1])
        
        # 替换问题中的<image1><image2>为空格
        cleaned_question = re.sub(r'<image\d+>', '', question)
                                        # 基准路径
        base_path = "D:\\data\\image_annotation\\"

                # 转换为相对路径
        relative_images = [path.replace(base_path, "").replace("\\", "/") for path in required_images]
        # 创建新的数据结构
        group_id = str(group_id).zfill(3)

        new_entry = {
            "id": f"translation_group{group_id}_q{id+1}",
    
            "category": category,
            "type": reason_type,
            "meta_info": meta_info,
            "question": cleaned_question,
            "images": relative_images,
            "gt_answer": answer
        }
        
        results.append(new_entry)
        all_results.append(new_entry)
        output_dir = r'C:\Users\FS139\Desktop\qa_release\translation'
        # 创建输出目录(如果不存在)'
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'translation_group{group_id}.jsonl')
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     json.dump(results, f, ensure_ascii=False, indent=4)
        with open(output_path, 'w', encoding='utf-8') as output_file:
                for item in results:
                    json.dump(item, output_file, ensure_ascii=False)
                    output_file.write('\n')  # 每个 JSON 对象后添加换行符
        
        print(f"Converted {file} to {output_path}")

with open( r"C:\Users\FS139\Desktop\qa_release\translation.jsonl", 'w', encoding='utf-8') as output_file:
            for item in all_results:
                json.dump(item, output_file, ensure_ascii=False)
                output_file.write('\n')  # 每个 JSON 对象后添加换行符