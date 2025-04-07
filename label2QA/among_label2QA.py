import json
import os
import re
from utils import get_image_order

def is_only_first_upper(s):
    return s[0].isupper() and s[1:].islower() if len(s) > 1 else s.isupper()

def extract_id(s):
    # 使用正则表达式查找字符串中的数字
    match = re.search(r'\d+', s)
    if match:
        # 如果找到数字，返回第一个匹配的数字
        return int(match.group())
    else:
        # 如果没有找到数字，返回 None
        return None
    
# 定义一个函数将数字转换为序数词
def number_to_ordinal(n):
    ordinal_words = ["first", "second", "third", "fourth"]
    return ordinal_words[n]
def generate_questions(i, obj_pool,all_scene_img_desc):

    move_two_q = 'Based on these two views, which direction did you move from the first view to the second view?'
    move_two_a = ' A. forward-left  B. forward-right.'
# 定义图像组合
    image_pairs = [
        ("<image1><image2>", "<image1><image4>"),
        ("<image2><image3>", "<image2><image1>"),
        ("<image3><image2>", "<image3><image4>"),
        ("<image4><image1>", "<image4><image3>")
    ]
    q1_1 = image_pairs[i][0] + move_two_q + move_two_a
    q1_2 = image_pairs[i][1] + move_two_q + move_two_a

    # 定义问题模板
    q2_template = all_scene_img_desc + ', if you are positioned at the {viewpoint} viewpoint, what is behind you? A. {0} B. {1} C. {2} D. {3}'
    q2_1 = q2_template.format(obj_pool[1], obj_pool[2], obj_pool[3], obj_pool[4], viewpoint=number_to_ordinal(i))
    a2_1 = chr(ord('A') + i)  # 根据 i 的值动态生成答案

    q2_2_template = all_scene_img_desc + ', if you are positioned at the {viewpoint} viewpoint, then you turn left and move forward, will you get closer to the {}? A. Yes B. No'
    q2_2 = q2_2_template.format(obj_pool[(i + 2) % 4], viewpoint=number_to_ordinal(i))

    q2_3_template = all_scene_img_desc + ', if you are positioned at the {viewpoint} viewpoint, then you turn right and move forward, will you get closer to the {}? A. Yes B. No'
    q2_3 = q2_3_template.format(obj_pool[(i + 4) % 4], viewpoint=number_to_ordinal(i))

    q5_template = all_scene_img_desc + ', if you are positioned at the {viewpoint} viewpoint, what is to the {direction} of the {0} from your ego centric view? A. {1} B. {2} C. {3} D. {4}'
    q5_1 = q5_template.format(obj_pool[0], obj_pool[1], obj_pool[2], obj_pool[3], obj_pool[4], viewpoint=number_to_ordinal(i), direction="left")
    a5_1 = chr(ord('A') + (i + 1) % 4)  # 根据 i 的值动态生成答案

    q5_2 = q5_template.format(obj_pool[0], obj_pool[1], obj_pool[2], obj_pool[3], obj_pool[4], viewpoint=number_to_ordinal(i), direction="right")
    a5_2 = chr(ord('A') + (i + 3) % 4)  # 根据 i 的值动态生成答案

    return q1_1, q1_2, q2_1, a2_1, q2_2, q2_3, q5_1, a5_1, q5_2, a5_2
# 定义一个函数来生成问题
def generate_question3(all_scene_img_desc, obj_pool, obj_index, direction):
        return all_scene_img_desc + ', if you were positioned where the {0} is and facing the same direction, would you be able to see the {1}? A. Yes B. No'.format(obj_pool[0], obj_pool[obj_index])

                # 定义一个函数来生成方向问题
def generate_main_direction_question(all_scene_img_desc, obj_pool, direction):
        return all_scene_img_desc + ', if you were positioned where the {0} is and facing the same direction, what would be to your {1}? A. {2} B. {3} C. {4} D. {5}'.format(obj_pool[0], direction, obj_pool[1], obj_pool[2], obj_pool[3], obj_pool[4])

def generate_question6(found_index, all_scene_img_desc, obj_pool, question_index):
        q_template = all_scene_img_desc + ', if you were positioned where the {0} is and facing the same direction, what would be to the {direction} of the {1} from this view? A. {2} B. {3} C. {4}'
        # a_template = ['A','B','C','A']

        q_left = q_template.format(*([obj_pool[found_index],obj_pool[0]] + [obj_pool[(found_index + 1 + i) % len(obj_pool)] for i in range(0,len(obj_pool)) if (found_index + 1 + i) % len(obj_pool) != found_index and ((found_index + 1 + i) % len(obj_pool) != 0)]),  direction="left")
        a_left = 'A'

        q_right = q_template.format(*([obj_pool[found_index],obj_pool[0]] + [obj_pool[(found_index + 1 + i) % len(obj_pool)] for i in range(0,len(obj_pool)) if (found_index + 1 + i) % len(obj_pool) != found_index and ((found_index + 1 + i) % len(obj_pool) != 0)]), direction="right")
        # a_right = a_template[(found_index -1 + 2) % 4]  # 右边的答案是左边答案的下一个
        a_right = "C" # 右边的答案是左边答案的下一个

        return q_left, a_left, q_right, a_right

label_dic = r'D:\data\image_annotation\label_anno\among\merge_anno_trans-需重新翻译bottoel_deter'
save_root = r"D:\data\image_annotation\other_all_image\qa\among"
all_result= []
pass_id = []
# for root, dirs, files in os.walk(label_dic):
#     for idx, file in enumerate(sorted(files)):
for i in range (743):
    if i!=298 and i!=730:
        json_file_path = os.path.join(label_dic , f'translated_group_{i}.json')
        # id = extract_id(file)
        id = i+1

        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        ####标注的顺序是按首字母拍的，不是按照前左右后或者前左后右，现在转为前左后右

        # 逐个读取字典的键值对并存储为变量
        user_id = data.get("user_id")
        image_group_idx = data.get("image_group_idx")
        image_group_folder = data.get("image_group_folder")
        main_image_idx = data.get("main_image_idx")
        main_image_caption = data.get("main_image_caption")
        objects = data.get("objects")
        arrangement = data.get("arrangement")
        semantic_front = data.get("semantic_front")
        visibility = data.get("visibility")

        category = (image_group_folder.split('\\')[-1]).split('_')[0]
        


        # if image_group_folder.split("\\")[-1] not in all_ids or category=='backpack':
        if 1>0:
            temp = objects[0]
            objects[0] = objects[1]
            objects[1] = objects[2]
            objects[2] = temp


            obj_num = [len(objects[i]) for i in range(4)]
            image_views = ['front', 'left', 'back', 'right']
            image_files = [os.path.join(image_group_folder, view) for view in image_views]

            # 初始化问题和答案字典
            questions_and_answers = {
                f"questions_{i}": {} for i in range(1, 5)
            }
            questions_and_answers["questions_gen"] = {}
            for i in range(1, 5):
                questions_and_answers[f"answer_{i}"] = {}
            questions_and_answers["answer_gen"] = {}
            # 将第一个子列表转换为集合
            common_elements = set(objects[0])
            # 遍历剩余的子列表，更新common_elements集合
            for sublist in objects[1:]:
                common_elements.intersection_update(sublist)
            main_object = list(common_elements)[0]
            main_toward = None
         

            # if  (any('Range hood' in item for item in sublist) for sublist in objects):
            if id in (55, 206, 207, 235, 236, 261, 262, 302, 303, 304, 305, 306, 307, 308, 309, 417, 418, 425, 426, 442, 443, 444, 445, 481, 510, 521, 522, 523, 708,731) or 318<id<361:
               
                continue
            if 376<id<402  or 445<id<456 or 498<id<510 or 543<id<558 or 561<id<580 or 590<id<645 or id in (538,539):
                pass_id.append(id)
                continue

            # if id>8 and id < 41:
            elif id>40 and id < 222:
                if (id%2!=0 and id<54) or (id%2==0 and 55<id ):
                    if id in (41, 62, 64, 66, 70, 74, 80, 148, 150, 208, 212) or 115<id<137:#sofa
                        obj_pool = [main_object,'dark brown sofa', 'school bag and TV cabinet','white-red cabinet', 'Light-colored sofa']

                    elif id in (43, 56, 60, 88, 98, 100, 102, 106):#bed
                        obj_pool = [main_object,'white-red cabinet', 'Light-colored sofa', 'dark brown sofa', 'school bag and TV cabinet']
                        
                    elif id==96:
                        obj_pool = [main_object,'Light-colored sofa','dark brown sofa', 'school bag and TV cabinet', 'white-red cabinet' ]
                    else:#bag
                        obj_pool = [main_object,'school bag and TV cabinet', 'white-red cabinet','Light-colored sofa','dark brown sofa'  ]

                else:
                    if id in (42, 44 , 46 ,48):
                        obj_pool = [main_object,'wall','smoking machine','window','cardboard-covered sliding door' ]
                    else:
                        obj_pool = [main_object,'cardboard-covered sliding door','wall','smoking machine','window' ]
            elif 222<id < 302:
                if (id%3==2 and 222<id<235) or (id%3==1 and 236<id<261)or (id%3==0 and 262<id) :
                    obj_pool = [main_object,'wall','sliding door','open space','grey chairs' ]
                elif (id%3==1 and 222<id<235) or (id%3==0 and  236<id<261) or (id%3==2 and 262<id) :
                    if 222<id<238 or  id==284 or 292<id<300: 
                        obj_pool = [main_object,'white-red cabinet', 'light-colored sofa', 'dark brown sofa', 'school bag and TV cabinet']
                    elif 262<id<279: #sofa
                        obj_pool = [main_object,'dark brown sofa', 'school bag and TV cabinet','white-red cabinet', 'Light-colored sofa']
                    else:
                        obj_pool = [main_object,'school bag and TV cabinet', 'white-red cabinet','Light-colored sofa','dark brown sofa'  ]
                else:
                    if id==239:
                        obj_pool = [main_object,'wall','smoking machine','window','cardboard-covered glass door' ]
                    else:
                        obj_pool = [main_object,'cardboard-covered glass door','smoking machine','window','wall' ]

            elif id>309 and id < 319:
                    obj_pool = [main_object,'window','lots of toys','wall','printed glass door' ]
            elif id>360 and id < 377:
                    obj_pool = [main_object,'bed sheet','white bedside','clothes rack','table with cups on it']
            elif 539<id<544 or 582<id<589 or id==590:
                    obj_pool = [main_object,'white bedside','clothes rack','table with cups on it','bed sheet']
               
            elif id>401 and id < 442:####################################### 412
                if (id%3==2 and id < 417) or (id%3==1 and 418 < id <425 ) or (id%3==0 and 426 < id ):
                    obj_pool = [main_object,'boxes and bottles','black chair', 'window with fencing' ,'wall']
                elif (id%3==1 and id < 417) or (id%3==0 and 418 < id < 425) or (id%3==2 and 426 < id ):
                    obj_pool = [main_object,'red wrought iron bedside','White wall and windows', 'black cabinet' ,'table and broom']
                else:
                    obj_pool = [main_object,'wooden sofa', 'White walls and windows', 'bicycle and TV' ,'Table and broom']
            elif id>455 and id < 481:
                    if id in (461,467,469,471,473,479):
                        obj_pool = [main_object,'bedside','closet and door','white wall','window and blue curtain']
                    else:
                        obj_pool = [main_object,'closet and door','white wall','window and blue curtain','bedside']
            elif 481<id<499 or 557<id<562 :
                if id == 559:
                    obj_pool = [main_object,'gate','stone fountain','decorated wall','light brown wall']

                else:
                    obj_pool = [main_object,'light brown wall','gate','stone fountain','decorated wall']
            # elif 498<id<511:
            elif id>510 and id<521:
                if id in (511,516, 520):
                    obj_pool = [main_object,'red stool','cabinet and potted plant','light-colored sofa','dark brown sofa']
                elif id==515:
                    obj_pool = [main_object,'light-colored sofa','dark brown sofa','red stool','cabinet and potted plant']
                elif id in (512 , 519):
                    obj_pool = [main_object,'cabinet and potted plant','light-colored sofa','dark brown sofa','red stool']
                else:
                    obj_pool = [main_object,'dark brown sofa','red stool','cabinet and potted plant','light-colored sofa']
                    
            elif id>522 and id<538:
                if id<533:
                    if id<528 or id==530:
                        obj_pool = [main_object,'grey sofa','cabinet desk','office area','corridor']
                    elif id in (528 ,529):
                        obj_pool = [main_object,'office area','corridor','grey sofa','cabinet desk']
                    elif id==531:
                        obj_pool = [main_object,'cabinet desk','office area','corridor','grey sofa']
                    else:
                        obj_pool = [main_object,'corridor','grey sofa','cabinet desk','office area']
                    if id in (524 , 530):
                        main_toward = 'left'
                    else:
                        main_toward = 'same'


                else:
                    if id == 533:
                        obj_pool = [main_object,'glass door','yellow wall','black wheelchair','mineral water bottle']
                    
                    else:
                        obj_pool = [main_object,'mineral water bottle','glass door','yellow wall','black wheelchair']
                    main_toward = 'opposite'

            elif id>643 and id<662:
                if id in (651,652):
                    obj_pool = [main_object,'lots of toys','wall','cardboard-covered glass door','window' ]
                else:
                    obj_pool = [main_object,'window','lots of toys','wall','cardboard-covered glass door' ]
            elif id>661 and id<669:
                obj_pool = [main_object,'railing','white bedside','blue doraemon pattern bed sheet','wall']
            elif id>668 and id<690:
                obj_pool = [main_object,'washing machine','white + gray curtains','white wood rack','white wall and window']
                main_toward = 'right'
            elif id>689 and id<730:
                obj_pool = [main_object,'light purple sofa','brown curtains and windows','white TV cabinet','wooden dining table']
                if id in (701, 708, 712, 716, 730):
                    main_toward = 'right'
                else:
                    main_toward = 'left'
            elif id==731:
                obj_pool = ['toy train','wooden podium','white board','metal lockers','TV']
            elif 579<id<583:
                obj_pool = ['cup','wooden podium','white board','metal lockers','TV']
            elif id>731:
                if id<741:
                    obj_pool = ['toy train','black table','wall','printed glass door','window']
                    if id in (732 , 733 , 736):
                        main_toward = 'opposite'
                    if id==740:
                        main_toward = 'left'
                else:
                    obj_pool = ['toy train','window','black table','wall','printed glass door']

            # elif all(len(sublist) == 2 for sublist in objects):
            else:
                # obj_pool = [main_object,objects[2][1] if objects[2][1]!=main_object else objects[2][0], objects[3][1] if objects[3][1]!=main_object else objects[3][0] ,objects[0][1] if objects[0][1]!=main_object else objects[0][0] ,objects[1][1] if objects[1][1]!=main_object else objects[1][0] ]
                    print(id)
                    continue
          
            obj_pool = [item.lower() if  is_only_first_upper(item) else item for item in obj_pool]
            obj_pool = [s.replace('mental', 'metal') if 'mental' in s else s for s in obj_pool]
            all_scene_img_desc = "<image1><image2><image3><image4>Based on these four different viewpoints (front, left, back, and right)"
            ###视图特殊的问题
            for i,object_group in enumerate(objects):
                a1_1 = a2_3 =  a2_2 = 'A'
                a1_2 = 'B'
                q1_1, q1_2, q2_1, a2_1, q2_2, q2_3, q5_1, a5_1, q5_2, a5_2 = generate_questions(i,obj_pool,all_scene_img_desc)
               
                question_keys = ['1_1', '1_2', '2_1', '2_2', '2_3', '5_1', '5_2']
                answer_keys = ['1_1', '1_2', '2_1', '2_2', '2_3', '5_1', '5_2']
                    #image循环结束
                for q_key, a_key in zip(question_keys, answer_keys):
                        questions_and_answers[f"questions_{i+1}"][q_key] = globals()[f'q{q_key}']
                        questions_and_answers[f"answer_{i+1}"][a_key] = globals()[f'a{a_key}']

            #### 视图无关的问题
            q3_1 = a3_1 = q3_2 = a3_2 = q4_1 = a4_1 = q4_2 = a4_2 = None
            # if category=='chair' :
            #     if image_group_idx>532:
            if main_toward!=None:
                
                # 定义一个字典，将 main_toward 的值映射到对应的索引和答案
                toward_mapping = {
                    'left': {'q3_1_obj': 2, 'q3_2_obj': 4, 'a3_1': 'A', 'a3_2': 'B', 'a4_1': 'A', 'a4_2': 'C'},
                    'right': {'q3_1_obj': 4, 'q3_2_obj': 2, 'a3_1': 'A', 'a3_2': 'B', 'a4_1': 'C', 'a4_2': 'A'},
                    'same': {'q3_1_obj': 3, 'q3_2_obj': 1, 'a3_1': 'A', 'a3_2': 'B', 'a4_1': 'B', 'a4_2': 'D'},
                    'opposite': {'q3_1_obj': 1, 'q3_2_obj': 3, 'a3_1': 'A', 'a3_2': 'B', 'a4_1': 'D', 'a4_2': 'B'}
                }

                # 获取 main_toward 对应的映射信息
                toward_info = toward_mapping.get(main_toward, toward_mapping['opposite'])

                # 生成问题和答案
                q3_1 = generate_question3(all_scene_img_desc, obj_pool, toward_info['q3_1_obj'], 'left')
                a3_1 = toward_info['a3_1']

                q3_2 = generate_question3(all_scene_img_desc, obj_pool, toward_info['q3_2_obj'], 'right')
                a3_2 = toward_info['a3_2']

                q4_1 = generate_main_direction_question(all_scene_img_desc, obj_pool, 'left')
                a4_1 = toward_info['a4_1']

                q4_2 = generate_main_direction_question(all_scene_img_desc, obj_pool, 'right')
                a4_2 = toward_info['a4_2']

            sofa_time = 0
            q6_1 = a6_1 = q6_2 = a6_2 = q6_3 = a6_3 = q6_4 = a6_4 = None


            for index, s in enumerate(obj_pool):
                if 'sofa' in s:
                    if sofa_time == 0:
                        q6_1, a6_1, q6_2, a6_2 = generate_question6(index, all_scene_img_desc, obj_pool, 1)
                        sofa_time += 1
                    elif sofa_time == 1:
                        q6_3, a6_3, q6_4, a6_4 = generate_question6(index, all_scene_img_desc, obj_pool, 3)
                        sofa_time += 1
                    if sofa_time == 2:
                        break  # 如果已经找到两个 sofa，提前退出循环
            question_keys = ['3_1', '3_2', '4_1', '4_2', '6_1', '6_2', '6_3', '6_4']
            answer_keys = ['3_1', '3_2', '4_1', '4_2', '6_1', '6_2', '6_3', '6_4']

            # 使用循环动态赋值
            for q_key, a_key in zip(question_keys, answer_keys):
                questions_and_answers["questions_gen"][q_key] = globals()[f'q{q_key}']
                questions_and_answers["answer_gen"][a_key] = globals()[f'a{a_key}']
        
        meta_info = obj_pool
        results = []
        idx= str(id).zfill(3)

        updated_image_files = []
        for path in image_files:
            path = path.replace("D:\\data\\image_annotation\\output_image_task4", "D:\\data\\image_annotation\\other_all_image\\among")
        
            directory, filename = os.path.split(path)
            directory_path = os.path.dirname(path)

            if filename.startswith("front"):
                prefix = "front"
            elif filename.startswith("left"):
                prefix = "left"
            elif filename.startswith("back"):
                prefix = "back"
            elif filename.startswith("right"):
                prefix = "right"

            for img_file in os.listdir(directory_path):
                    if img_file.startswith(prefix) and img_file.endswith(".jpg"):
                        updated_image_files.append(os.path.join(directory_path, img_file))
                        break
        base_path = "D:\\data\\image_annotation\\"
                    # 转换为相对路径
        image_files = [path.replace(base_path, "").replace("\\", "/") for path in updated_image_files]
        for i,item in enumerate([[questions_and_answers['questions_1'],questions_and_answers['answer_1']],[questions_and_answers['questions_2'],questions_and_answers['answer_2']],[questions_and_answers['questions_3'],questions_and_answers['answer_3']],[questions_and_answers['questions_4'],questions_and_answers['answer_4']]]):
           
            for q_key in item[0]:
                types = '{}_frame'.format(i)
                # print(types)

                question =item[0][q_key]
                answer = item[1][q_key]
                image_order = get_image_order(question)
                required_images = []
                for j in image_order:
                        required_images.append(image_files[j-1])
                # 替换问题中的<image1><image2>为空格
                cleaned_question = re.sub(r'<image\d+>', '', question)
                if "1_" in q_key:
                    category = ['perpendicular','P-P','meanwhile','self']
                if "2_1" in q_key:
                    category = ['perpendicular','P-O','meanwhile','self']
                elif "2_" in q_key:
                    category = ['perpendicular','P-O','sequence','self']
                if "5_" in q_key:
                    category = ['perpendicular','O-O','meanwhile','self']

                new_entry = {
                    "id": f"among_group{idx}_q{i}_{q_key}",
                    "category": category,
                    "type": types,
                    "meta_info": meta_info,
                    "question": cleaned_question,
                    "images": required_images,
                    "gt_answer": answer
                }
                
                results.append(new_entry)
        
        # 处理第二组问题和答案
        for q_key in questions_and_answers['questions_gen']:
            types = 'general'
            question = questions_and_answers['questions_gen'][q_key]
            answer = questions_and_answers['answer_gen'][q_key]
            if question==None:
                continue
            image_order = get_image_order(question)
            required_images = []
            for j in image_order:
                # if i in range(0, img_num) :
                    required_images.append(image_files[j-1]) 
            # 替换问题中的<image1><image2>为空格
            cleaned_question = re.sub(r'<image\d+>', '', question)

            if "3_" in q_key:
                    category = ['perpendicular','PO','meanwhile','level1']
            if "4_" in q_key:
                category = ['perpendicular','PO','meanwhile','level2']
            if "6_" in q_key:
                category = ['perpendicular','OO','meanwhile','level2']

  

            # 创建新的数据结构
            new_entry = {
                "id": f"among_group{idx}_gen_{q_key}",
                "category": category,
                "type": types,
                "meta_info": meta_info,
                "question": cleaned_question,
                "images": required_images,
                "gt_answer": answer
            }
            
            results.append(new_entry)
        all_result += results
        output_dir = r'C:\Users\FS139\Desktop\qa_release\among'
        # 创建输出目录(如果不存在)'
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'among_group{idx}.jsonl')
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     json.dump(results, f, ensure_ascii=False, indent=4)
#         with open(output_path, 'w', encoding='utf-8') as output_file:
#                 for item in results:
#                     json.dump(item, output_file, ensure_ascii=False)
#                     output_file.write('\n')  # 每个 JSON 对象后添加换行符
        
#         print(f"Converted {file} to {output_path}")

# with open( r"C:\Users\FS139\Desktop\qa_release\among.jsonl", 'w', encoding='utf-8') as output_file:
#             for item in all_result:
#                 json.dump(item, output_file, ensure_ascii=False)
#                 output_file.write('\n')  # 每个 JSON 对象后添加换行符

print(pass_id)
print(len(pass_id))
