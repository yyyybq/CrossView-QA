import json
import os
import glob
from utils import get_image_order

label_dic = r'D:\data\image_annotation\label_anno\around\0314_self_anno'
save_root = r"C:\Users\FS139\Desktop\qa_release\around_new"
os.makedirs(save_root, exist_ok=True)

img_dic = r'D:\data\image_annotation\other_all_image\around'

def generate_options(items):
    # 定义字母表（A-Z）
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # 初始化结果字符串
    result = []
    
    # 遍历列表中的每个元素
    for index, item in enumerate(items):
        if index >= len(alphabet):
            raise ValueError("列表长度超过26个元素，无法生成选项！")
        # 获取对应的字母
        letter = alphabet[index]
        # 格式化选项
        result.append(f"{letter}. {item}")
    
    # 将所有选项用空格连接成一个字符串
    return " ".join(result)
def is_only_first_upper(s):
    return s[0].isupper() and s[1:].islower() if len(s) > 1 else s.isupper()

all_result = []
for root, dirs, files in os.walk(label_dic):
    for j, file in enumerate(sorted(files)):  #
        id = str(j).zfill(3)
        # print(file)
        q1_1 = q1_2 = q1_3 = q1_4 = q2_1 = q2_2 = q2_3 = q2_4 = q2_5 = q2_6 = q3_1 = q3_2 = q3_3 = q3_4 = q4_1 =q4_2 =q3_5 =q3_6 =None
        a1_1 = a1_2 = a1_3 = a1_4 = a2_1 = a2_2 = a2_3 = a2_4 = a2_5 = a2_6 = a3_1 = a3_2 = a3_3 = a3_4 = a4_1 = a4_2 = a3_5 = a3_6 = None
        if file.endswith(".json"):#and os.path.splitext(file)[0] not in exist_file_names:
            json_file_path = os.path.join(root, file)
            # print(f"Processing file: {json_file_path}")

        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as file_data:
            data = json.load(file_data)
        image_paths = []
        img_folder_path = os.path.join(img_dic, os.path.splitext(file)[0])


        extensions=['*.jpg', '*.jpeg', '*.png', '*.gif']
        for extension in extensions:
            for file_path in glob.glob(os.path.join(img_folder_path, extension), recursive=True):
                image_paths.append(file_path)
        # print(image_paths)
        questions_and_answers = {
                "image_paths": {f"image{i+1}_path": image for i, image in enumerate(image_paths)},
                "questions_1": {},
                "questions_2": {},
                "questions_3": {},
                "questions_4": {},
                "answer_1": {},
                "answer_2": {},
                "answer_3": {},
                "answer_4": {}
            }
        # 逐个读取字典的键值对并存储为变量
        group_info = data.get("group_info")
        answers = data.get("question_answers")
        object_annotations = data.get("object_annotations")
        other_obj = data.get("other_obj")
        image_metadata = data.get("image_metadata")
        
        total_images = group_info.get("total_images")
        group_name = group_info.get("group_name")
        Num_right = answers.get("Num_right")
        Special = answers.get("Special")

        obj_num = len(object_annotations)
        other_obj_list = other_obj.split(";") if other_obj!=None else None

# 初始化一个空列表来存储所有name
        main_obj = []
        for obj in data["object_annotations"].values():
            # 提取每个对象的name属性并添加到列表中
            main_obj.append(obj["name"])

        other_obj_list = [item.lower() if  is_only_first_upper(item) else item for item in other_obj_list]
        main_obj = [item.lower() if  is_only_first_upper(item) else item for item in main_obj]

        other_obj_list = [s.replace('mental', 'metal') if 'mental' in s else s for s in other_obj_list]
        main_obj = [s.replace('mental', 'metal') if 'mental' in s else s for s in main_obj]
        
        if Num_right!='Yes':
            print('Wrong_{}'.format(file))
            continue

 ##### q1 self+PP
        base_q1 = 'Give two images of a scene captured from different viewpoints, please determine which direction did you move? A. Left-front B. Right-front.'
        q1_1 = "<image1><image2>"+base_q1
        q1_2 = "<image1><image3>"+base_q1
        a1_1 = 'A'
        a1_2 = 'B'
        if total_images==5:
            q1_3 = "<image1><image4>"+base_q1
            a1_3 = 'A'
            q1_4 = "<image1><image5>" +base_q1
            a1_4 = 'B'
        elif total_images==4: 
            q1_3 = "<image4><image2>"+base_q1
            a1_3 = 'B'
            q1_4 = "<image4><image3>"+base_q1
            a1_4 = 'A'

        # 检测变量名并保存到字典
        for var_name in locals().copy():
            if locals()[var_name] != None:

                if var_name.startswith('q1'):  # 只处理以 'q' 开头的变量
                    # 提取键值，例如 q1_1 对应键为 '1_1'
                    key = var_name[1:]  # 去掉变量名的第一个字符 'q'
                    questions_and_answers['questions_1'][key] = locals()[var_name]  # 将变量值保存到字典中
                if var_name.startswith('a1'):  # 只处理以 'q' 开头的变量
                    # 提取键值，例如 q1_1 对应键为 '1_1'
                    key = var_name[1:]  # 去掉变量名的第一个字符 'q'
                    questions_and_answers['answer_1'][key] = locals()[var_name]  # 将变量值保存到字典中


####### q2 self+OO

        image_desc123 = '<image1><image2><image3>Given 3 orthogonal perspectives of a scene, they are the front view, left view and right view. '

        if obj_num==2:
            obj_list = [main_obj[0],main_obj[1]]
            if Special==2:
                q2_1 = image_desc123+"In the second image, is there a {0} behind of the {1} from your ego-centirc view? A. Yes B. No.".format(obj_list[1],obj_list[0])
                q2_2 = image_desc123+"In the third image, is there a {0} behind of the {1} from your ego-centirc view? A. Yes B. No.".format(obj_list[0],obj_list[1])
            else:
                items1 = [obj_list[1]] + other_obj_list
                options1 = generate_options(items1)                
                items2 = [obj_list[0]] + other_obj_list
                options2 = generate_options(items2)

                q2_1 = image_desc123+"In the second image, what is behind of the {0}. ".format(obj_list[0]) + options1 
                q2_2 = image_desc123+"In the third image, what is behind of the {0}. ".format(obj_list[1]) + options2 

                if Special==3:
                    q2_1 = q2_1.replace("what is", "what is " + "the nearest object")


        elif obj_num==3:
            obj_list = [main_obj[0],main_obj[1],main_obj[2]]
            if Special==2:
                q2_1 = image_desc123+"In the second image, is there a {0} behind of the {1} from your ego-centirc view? A. Yes B. No.".format(obj_list[1],obj_list[0])
                q2_2 = image_desc123+"In the third image, is there a {0} behind of the {1} from your ego-centirc view? A. Yes B. No.".format(obj_list[1],obj_list[2])
            else:
                items1 = [obj_list[1], obj_list[2]] + other_obj_list
                options1 = generate_options(items1)                
                items2 = [obj_list[1], obj_list[0]] + other_obj_list
                options2 = generate_options(items2)

                q2_1 = image_desc123+"In the second image, what is behind of the {0}. ".format(obj_list[0]) + options1 
                q2_2 = image_desc123+"In the third image, what is behind of the {0}. ".format(obj_list[2]) + options2

                if Special==3:
                    q2_1 = q2_1.replace("what is", "what is " + "the nearest object")


        elif obj_num==4:
            obj_list = [main_obj[0],main_obj[1],main_obj[2],main_obj[3]]
            if Special==2:
                q2_1 = image_desc123+"In the second image, is there a {0} behind of the {1} from your ego-centirc view? A. Yes B. No.".format(obj_list[1],obj_list[0])
                q2_2 = image_desc123+"In the third image, is there a {0} behind of the {1} from your ego-centirc view? A. Yes B. No.".format(obj_list[2],obj_list[3])
            else:
                items1 = [obj_list[0], obj_list[1], obj_list[2]] + other_obj_list
                options1 = generate_options(items1)                
                items2 = [obj_list[2], obj_list[1], obj_list[0]] + other_obj_list
                options2 = generate_options(items2)

                q2_1 = image_desc123+"In the second image, what is behind of the {0}. ".format(obj_list[0]) + options1 
                q2_2 = image_desc123+"In the third image, what is behind of the {0}. ".format(obj_list[3]) + options2

        else:
            print('Wrong_{}'.format(file))
        
        if Special==3:
            q2_1 = q2_1.replace("what is", "what is " + "the nearest object")
            q2_2 = q2_2.replace("what is", "what is " + "the nearest object")

####### q3 self+PO

        q3_1 = image_desc123+"If you are at the view of the second image now, then you turn right and go straight, is the {0} be closer to you? A. Yes B. No".format(main_obj[1])
        q3_2 = image_desc123+"If you are at the view of the third image now, then you turn left and go straight, is the {0} be closer to you? A. Yes B. No".format(main_obj[-2])
        
        a2_1 = 'A'
        a2_2 = 'A'
        a3_1 = "B"
        a3_2 = "B"
############### more image, different situations
        a3_3 = a3_1
        a3_4 = a3_2
        a2_3 = a2_1
        a2_4 = a2_2
        if total_images==4:
                q2_3 = q2_1.replace("<image1>", "<image4>").replace("front", "behind")
                q2_4 = q2_2.replace("<image1>", "<image4>").replace("front", "behind")
                q3_3 = q3_1.replace("<image1>", "<image4>").replace("front", "behind")
                q3_4 = q3_2.replace("<image1>", "<image4>").replace("front", "behind")

        if total_images==5:
                q2_3 = q2_1.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                q2_4 = q2_2.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                q3_3 = q3_1.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                q3_4 = q3_2.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
              
        if total_images==6:
                q2_3 = q2_1.replace("<image1>", "<image6>").replace("front", "behind")
                q2_4 = q2_2.replace("<image1>", "<image6>").replace("front", "behind")
                q3_3 = q3_1.replace("<image1>", "<image6>").replace("front", "behind")
                q3_4 = q3_2.replace("<image1>", "<image6>").replace("front", "behind")


                q2_5 = q2_1.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                q2_6 = q2_2.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                a2_5 = a2_1
                a2_6 = a2_2
                q3_5 = q3_1.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                q3_6 = q3_2.replace("<image2>", "<image4>").replace("<image3>", "<image5>")
                a3_5 = a3_1
                a3_6 = a3_2
################# q4 perspecyive taking
        if obj_num>2:
            for i in range (1,obj_num+1):
                if object_annotations["object_{}".format(i)]["direction"] !="None":
                    if i==1:
                        options = generate_options(main_obj[1:])
                        
                        # 创建一个字典来映射方向和对应的描述
                        direction_descriptions = {
                            'face': "what is the nearest object on the left of it? ",
                            'back': "what is the nearest object on the right of it? ",
                            'left': "what is the nearest object behind it? ",
                            'right': "what is the nearest object in front of it? "
                        }
                        # 获取当前对象的方向
                        direction = object_annotations["object_{}".format(i)]["direction"]
                        # 根据方向生成问题
                        q4_1 = image_desc123 + "In the second image, from the perspective of the {0}, {1}".format(main_obj[0], direction_descriptions.get(direction, "unknown direction")) + options     
                        a4_1 = 'A'
                        print(q4_1)
                        
                    if i==obj_num-1:
                        options = generate_options(main_obj[:-1])
                        
                      # 创建一个字典来映射方向和对应的描述
                        direction_descriptions = {
                            'face': "what is the nearest object on the right of it? ",
                            'back': "what is the nearest object on the left of it? ",
                            'left': "what is the nearest object in front of it? ",
                            'right': "what is the nearest object behind it? "
                        }
                        # 获取当前对象的方向
                        direction = object_annotations["object_{}".format(i)]["direction"]
                        # 根据方向生成问题
                        base_question = image_desc123 +"In the third image, from the perspective of the {0}, {1}".format(main_obj[-1], direction_descriptions.get(direction, "unknown direction"))
                        q4_2 = base_question + options
                        a4_2 = 'B' if obj_num==3 else 'C'
                        print(q4_2)

        # else:
        #     for i in range (1,3):
        #         if object_annotations["object_{}".format(i)]["direction"] !="None":
        #             if i==0:
                        
        #                 # 创建一个字典来映射方向和对应的描述
        #                 direction_descriptions = {
        #                     'face': "what is the nearest object on the left of it?",
        #                     'back': "what is the nearest object on the right of it?",
        #                     'left': "what is the nearest object behind it?",
        #                     'right': "what is the nearest object in front of it?"
        #                 }
        #                 # 获取当前对象的方向
        #                 direction = object_annotations["object_{}".format(i)]["direction"]
        #                 # 根据方向生成问题
        #                 q4_1 = image_desc123 + "In the second image, from the perspective of the {0}, {1}".format(main_obj[0], direction_descriptions.get(direction, "unknown direction")) + options     
        #                 a4_1 = 'A'
           
                        
        #             if i==obj_num-1:
        #                 options = generate_options(main_obj[:-1])
                        
        #               # 创建一个字典来映射方向和对应的描述
        #                 direction_descriptions = {
        #                     'face': "what is the nearest object on the right of it?",
        #                     'back': "what is the nearest object on the left of it?",
        #                     'left': "what is the nearest object in front of it?",
        #                     'right': "what is the nearest object behind it?"
        #                 }
        #                 # 获取当前对象的方向
        #                 direction = object_annotations["object_{}".format(i)]["direction"]
        #                 # 根据方向生成问题
        #                 base_question = image_desc123 +"In the third image, from the perspective of the {0}, {1}".format(main_obj[-1], direction_descriptions.get(direction, "unknown direction"))
        #                 q4_2 = base_question + options
        #                 a4_2 = 'B' if obj_num==3 else 'C'
   

                    

        # 检测变量名并保存到字典
        for var_name in locals().copy():
            if locals()[var_name] != None:
                # print(var_name)
                if var_name.startswith('q2'):  # 只处理以 'q' 开头的变量
                    key = var_name[1:]  # 去掉变量名的第一个字符 'q'
                    questions_and_answers['questions_2'][key] = locals()[var_name]  # 将变量值保存到字典中
                if var_name.startswith('a2'): 
                    key = var_name[1:]  
                    questions_and_answers['answer_2'][key] = locals()[var_name]  
                if var_name.startswith('q3'): 
                    key = var_name[1:]  
                    questions_and_answers['questions_3'][key] = locals()[var_name] 
                if var_name.startswith('a3'):  
                    key = var_name[1:]  
                    questions_and_answers['answer_3'][key] = locals()[var_name] 
                if var_name.startswith('q4'):  
                    key = var_name[1:]  
                    questions_and_answers['questions_4'][key] = locals()[var_name]  
                if var_name.startswith('a4'):  
                    key = var_name[1:]  
                    questions_and_answers['answer_4'][key] = locals()[var_name]  
        # print(questions_and_answers)

        metadata = []
        img_info = []
        obj_info = []
        img_info.append(total_images)
        for meta in data["image_metadata"].values():
            # 提取每个对象的name属性并添加到列表中
            img_info.append(meta["occlusion_level"])
        obj_info.append(obj_num)
        obj_info.append(main_obj)
        obj_info.append(other_obj_list)
        metadata.append(img_info)
        metadata.append(obj_info)
        # # 提取图片路径
        # image_files = []
        # for img_path_key in data['image_paths']:
        #     img_path = data['image_paths'][img_path_key]
        #     img_file = os.path.basename(img_path)
        #     image_files.append(img_file)      
        # 替换问题中的<image1><image2>为空格
        import re



        results = []
    # 处理第一组问题和答案
        for i,item in enumerate([[questions_and_answers['questions_1'],questions_and_answers['answer_1']],[questions_and_answers['questions_2'],questions_and_answers['answer_2']],[questions_and_answers['questions_3'],questions_and_answers['answer_3']],[questions_and_answers['questions_4'],questions_and_answers['answer_4']]]):
            for q_key in item[0]:
                if '1_' in q_key:
                    category = ['linear','P-P','meanwhile','self']
                if '2_' in q_key:
                    category = ['linear','O-O','meanwhile','self']                
                if '3_' in q_key:
                    category = ['linear','P-O','sequence','self']
                if '4_' in q_key:
                    if obj_num>2:
                        category = ['linear','P-O','meanwhile','level2']
                    else:
                        category = ['linear','P-O','meanwhile','level1']

                question = item[0][q_key]

                answer = item[1][q_key]
                image_order = get_image_order(question)

                required_images = []
                for i in image_order:
                    required_images.append(image_paths[i-1])
                cleaned_question = re.sub(r'<image\d+>', '', question)

                # 基准路径
                base_path = "D:\\data\\image_annotation\\"

                # 转换为相对路径
                relative_images = [path.replace(base_path, "").replace("\\", "/") for path in required_images]
                # 创建新的数据结构
                new_entry = {
                    "id": f"aroundnew_group{id}_q{q_key}",
                    "category": category,
                    "type": Special,
                    "meta_info": metadata,
                    "question": cleaned_question,
                    "images": relative_images,
                    "gt_answer": answer
                }
                
                results.append(new_entry)
        
        output_file_path = os.path.join(save_root, file+'l')  
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for item in results:
                json.dump(item, output_file, ensure_ascii=False)
                output_file.write('\n')  # 每个 JSON 对象后添加换行符
        print(f"Converted {file_path} to {output_file_path}")
        all_result += results


with open( r"C:\Users\FS139\Desktop\qa_release\around_new.jsonl", 'w', encoding='utf-8') as output_file:
            for item in all_result:
                json.dump(item, output_file, ensure_ascii=False)
                output_file.write('\n')  # 每个 JSON 对象后添加换行符