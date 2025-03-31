import json
import os
import glob
#"mode: 1.lmr; 2.rml; 3.mlr 4.lm; 5.rm; 8.all; 9.mb",
import re
from utils import get_image_order
img_dic = r'D:\data\image_annotation\other_all_image\rotation'
save_root = r"D:\data\image_annotation\other_all_image\qa\rotation"
json_file_path = r'C:\Users\FS139\Desktop\code\spatial\rotation_relation.json'

viewpoint_names = {1: "first", 2: "second", 3: "third", 4: "fourth"}

def generate_questions1(viewpoint, obj_pool, all_scene_img_desc2, directions, positions, answers):
    questions = {}

    viewpoint_name = viewpoint_names[viewpoint]
    question_index = 1
    for direction in directions:
        for position in positions:
            if direction not in answers or position not in answers[direction]:
                continue
            if direction == "none":
                question = f"{all_scene_img_desc2}if you are positioned at the {viewpoint_name} viewpoint, what is to your {position}? A. {obj_pool[0]} B. {obj_pool[1]} C. {obj_pool[2]}"
            else:
                question = f"{all_scene_img_desc2}if you are positioned at the {viewpoint_name} viewpoint and turn {direction}, what is to your {position}? A. {obj_pool[0]} B. {obj_pool[1]} C. {obj_pool[2]}"
            answer = answers[direction][position]
            questions[f"{viewpoint}_{question_index}"] = (question, answer)
            question_index += 1

    return questions

def generate_questions45(viewpoint, obj_pool, all_scene_img_desc1, directions, positions, answers):
    questions = {}
    viewpoint_name = viewpoint_names[viewpoint]
    question_index = 1

    for direction in directions:
        for position in positions:
            if direction not in answers or position not in answers[direction]:
                continue
            if direction == "none":
                question = f"{all_scene_img_desc1}if you are positioned at the {viewpoint_name} viewpoint, what is to your {position}? A. {obj_pool[0]} B. {obj_pool[1]}"
            else:
                question = f"{all_scene_img_desc1}if you are positioned at the {viewpoint_name} viewpoint and turn {direction}, what is to your {position}? A. {obj_pool[0]} B. {obj_pool[1]}"
            answer = answers[direction][position]
            questions[f"{viewpoint_name}_{question_index}"] = (question, answer)
            question_index += 1

    return questions

def generate_questions8(viewpoint, obj_pool, all_scene_img_desc3, directions, positions, answers):
    
    viewpoint_name = viewpoint_names[viewpoint]
    questions = {}
    question_index = 1
    for direction in directions:
        for i, position in enumerate(positions):
            if direction not in answers or position not in answers[direction]:
                continue
            question_key = f"{viewpoint}_{question_index}"
            question = f"{all_scene_img_desc3}if you are positioned at the {viewpoint_name} viewpoint and turn {direction}, what is to your {position}? A. {obj_pool[0]} B. {obj_pool[1]} C. {obj_pool[2]} D. {obj_pool[3]}"
            answer = answers[direction][i]
            questions[question_key] = (question, answer)
            question_index += 1
    return questions
def generate_questions9(viewpoint, obj_pool, all_scene_img_desc1, directions, positions, answers):
    questions = {}
    viewpoint_name = viewpoint_names[viewpoint]
    question_index = 1
    for direction in directions:
        for i, position in enumerate(positions):
            if direction not in answers or position not in answers[direction]:
                continue
            question_key = f"{viewpoint}_{question_index}"
            if direction == "none":
                question = f"{all_scene_img_desc1}if you are positioned at the {viewpoint_name} viewpoint, what is {position} you? A. {obj_pool[0]} B. {obj_pool[1]}"
            else:
                question = f"{all_scene_img_desc1}if you are positioned at the {viewpoint_name} viewpoint and turn {direction}, what is to your {position}? A. {obj_pool[0]} B. {obj_pool[1]}"
            answer = answers[direction][position]
            questions[question_key] = (question, answer)
            question_index += 1
    return questions

# 读取 JSON 文件
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
all_result = []
for (idx,lists) in enumerate(data):
    image_paths = []
    img_folder_path = os.path.join(img_dic, lists[0])
    output_file_path = os.path.join(save_root, lists[0]) +'.json'

    extensions=['*.jpg', '*.jpeg', '*.png', '*.gif']
    for extension in extensions:
        for file_path in glob.glob(os.path.join(img_folder_path, extension), recursive=True):
            image_paths.append(file_path)
    questions_and_answers = {
                "questions_1": {},
                "questions_2": {},
                "answer_1": {},
                "answer_2": {}
            }
    type = lists[1]

    #### Baiqiao, please double check the description, I think it's wrong, as we are having rotation
    all_scene_img_desc1 = "<image1><image2>Based on these two sequential orthogonal views of the same scene captured during rotation, " 
    all_scene_img_desc2 = "<image1><image2><image3>Based on these three sequential orthogonal views of the same scene captured during rotation, "
    all_scene_img_desc3 = "<image1><image2><image3><image4>Based on these four sequential orthogonal views of the same scene captured during rotation, "

    if type == '1':
        obj_pool = [lists[2], lists[3], lists[4]]
        questions_and_answers = {}

        directions = ["none", "90 degrees to the left", "90 degrees to the right", "180 degrees around"]
        positions = ["right", "left", "behind"]

        answers = {
            "none": {"right": "B", "behind": "C"},
            "90 degrees to the left": {"right": "A", "left": "C", "behind": "B"},
            "90 degrees to the right": {"right": "C", "left": "A", "behind": "B"},
            "180 degrees around": {"right": "B", "left": "C", "behind": "A"}
        }

        viewpoints = [1, 2, 3]
        for viewpoint in viewpoints:
            questions_and_answers.update(generate_questions1(viewpoint, obj_pool, all_scene_img_desc2, directions, positions, answers))

    if type == '4':
        obj_pool = [lists[2], lists[3]]
        questions_and_answers = {}

        directions = ["none", "90 degrees to the left", "90 degrees to the right", "180 degrees around"]
        positions = ["right", "left", "behind"]

        answers = {
            "none": {"right": "B"},
            "90 degrees to the left": {"right": "A", "behind": "B"},
            "90 degrees to the right": {"left": "B", "behind": "A"},
            "180 degrees around": {"behind": "A", "left": "B", "right": "B"}
        }

        viewpoints = [1, 2]
        for viewpoint in viewpoints:
           questions_and_answers.update(generate_questions45(viewpoint, obj_pool, all_scene_img_desc1, directions, positions, answers))

    if type == '5':
        obj_pool = [lists[2], lists[3]]
        questions_and_answers = {}

        directions = ["none", "90 degrees to the right", "90 degrees to the left", "180 degrees around"]
        positions = ["left", "right", "behind"]

        answers = {
            "none": {"left": "B"},
            "90 degrees to the right": {"left": "A", "behind": "B"},
            "90 degrees to the left": {"right": "B", "behind": "A"},
            "180 degrees around": {"behind": "A", "right": "B", "left": "A"}
        }

        viewpoints = [1, 2]
        for viewpoint in viewpoints:
            questions_and_answers.update(generate_questions45(viewpoint, obj_pool, all_scene_img_desc1, directions, positions, answers))
    if type == '9':
        obj_pool = [lists[2], lists[3]]

        questions_and_answers = {}

        directions = ["none", "90 degrees to the right", "90 degrees to the left", "180 degrees around"]
        positions = ["behind", "left", "right"]

        answers = {
            "none": {"behind": "B"},
            "90 degrees to the right": {"left": "A", "right": "B"},
            "90 degrees to the left": {"left": "B", "right": "A"},
            "180 degrees around": {"behind": "A"}
        }

        viewpoints = [1, 2]
        for viewpoint in viewpoints:
            questions_and_answers.update(generate_questions9(viewpoint, obj_pool, all_scene_img_desc1, directions, positions, answers))
    if type == '8':
        questions_and_answers = {}

        obj_pool = [lists[2], lists[3], lists[4], lists[5]]
        directions = ["90 degrees to the left", "90 degrees to the right", "180 degrees around"]
        positions = ["right", "left", "behind", "front"]
        answers = {
            "90 degrees to the left": ["A", "C", "B", "D"],
            "90 degrees to the right": ["C", "A", "D", "B"],
            "180 degrees around": ["D", "B", "A", "C"]
        }
    
        
        for viewpoint in range(1, 5):
   
            questions_and_answers.update(generate_questions8(viewpoint, obj_pool, all_scene_img_desc1, directions, positions, answers))

#####################
# 查找匹配的元数据信息
    meta_info = lists[2:]
    idx= str(idx).zfill(3)



    if type=='1':
        types = 'three_view'
    elif type=='4':
        types = 'two_view_clockwise'    
    if type=='5':
        types = 'two_view_counterclockwise'
    if type=='9':
        types = 'two_view_opposite'
    if type=='8':
        types = 'four_view'
    # 创建结果列表
    results = []
    
    # print(questions_and_answers)
    for q_key in questions_and_answers:
        category = ['perpendicular','PP','rotation','self']

        question = questions_and_answers[q_key][0]
        answer = questions_and_answers[q_key][1]
        # print(question)
        
        image_order = get_image_order(question)

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
        new_entry = {
            "id": f"rotation_group{idx}_q{q_key}",
            "category": category,
            "type": types,
            "meta_info": meta_info,
            "question": cleaned_question,
            "images": relative_images,
            "gt_answer": answer
        }
        
        results.append(new_entry)
        all_result.append(new_entry)

        output_dir = r'C:\Users\FS139\Desktop\qa_release\rotation'
        # 创建输出目录(如果不存在)'
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'rotation_group{idx}.jsonl')
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     json.dump(results, f, ensure_ascii=False, indent=4)
        with open(output_path, 'w', encoding='utf-8') as output_file:
                for item in results:
                    json.dump(item, output_file, ensure_ascii=False)
                    output_file.write('\n')  # 每个 JSON 对象后添加换行符
        
        print(f"Converted {file} to {output_path}")

with open( r"C:\Users\FS139\Desktop\qa_release\rotation.jsonl", 'w', encoding='utf-8') as output_file:
            for item in all_result:
                json.dump(item, output_file, ensure_ascii=False)
                output_file.write('\n')  # 每个 JSON 对象后添加换行符