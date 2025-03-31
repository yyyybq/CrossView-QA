import os
import base64
import json
from PIL import Image
import torch
from tqdm import tqdm
from transformers import AutoProcessor, AutoModelForVision2Seq
from modelscope import AutoConfig, AutoModel, AutoTokenizer
from anthropic import Anthropic
from openai import OpenAI


from utils import replace_old_root,load_images,find_json_files,encode_image
# 全局变量
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"



def process_json_files(input_root, output_root, model_name, model_client, model_params, new_root):
    """
    处理 JSON 文件，调用指定模型回答问题，并保存结果
    """
    setting_name = os.path.basename(input_root)
    print(f"Processing files in input root: {input_root}")

    json_files = find_json_files(input_root)

    for file_path in json_files:
        fine_name = os.path.basename(file_path)
        output_folder = os.path.join(output_root, setting_name)
        os.makedirs(output_folder, exist_ok=True)

        output_path = os.path.join(output_folder, fine_name.replace(".jsonl", "_answers.jsonl"))

        # 判断输出文件是否存在
        if os.path.exists(output_path):
            print(f"Skipping {file_path}, as the output file {output_path} already exists.")
            continue  # 跳过当前文件的处理

        results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"Processing answers in {output_path}")

            for line in f:
                data = json.loads(line.strip())
                question = data.get("question")
                image_paths = data.get("images", [])

                image_paths = replace_old_root(image_paths, new_root)
                images = load_images(image_paths)

                # 构建问题提示
                question_prompt = 'Answer the following question based on this rule: You only need to provide *ONE* correct letter like A,B,C selecting from the options listed below. The Question is: ' + question.replace("A.", " Choices: A.")

                # 根据模型类型构建消息内容
                if model_name == "claude":
                    message_content = [
                        {
                            "type": "text",
                            "text": question_prompt
                        }
                    ]
                    for img_path in image_paths:
                        with Image.open(img_path) as img:
                            format = img.format.lower()
                            media_type = f"image/{format}"
                        with open(img_path, "rb") as image_file:
                            image_data = base64.b64encode(image_file.read()).decode("utf-8")
                            message_content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            })
                    response = model_client.messages.create(
                        model=model_params["model"],
                        max_tokens=model_params["max_tokens"],
                        messages=[
                            {
                                "role": "user",
                                "content": message_content
                            }
                        ]
                    )
                    model_answer = response.content[0].text
                elif model_name == "gpt4":
                    base64_images = [encode_image(image) for image in image_paths]
                    user_content = [{"type": "text", "text": question_prompt}]
                    base64_images = [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high",
                            },
                        }
                        for base64_image in base64_images
                    ]
                    user_content.extend(base64_images)
                    messages = [{"role": "user", "content": user_content}]
                    completion = model_client.chat.completions.create(
                        model=model_params["model"],
                        messages=messages
                    )
                    model_answer = completion.choices[0].message.content
                elif model_name == "idefics":
                    processor = AutoProcessor.from_pretrained(model_params["model_name"])
                    model = AutoModelForVision2Seq.from_pretrained(model_params["model_name"]).to(DEVICE)
                    messages = [{
                        "role": "user",
                        "content": [
                            *[{"type": "image"} for _ in images],
                            {"type": "text", "text": question_prompt}
                        ]
                    }]
                    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
                    inputs = processor(text=prompt, images=images, return_tensors="pt").to(DEVICE)
                    generated_ids = model.generate(**inputs, max_new_tokens=model_params["max_new_tokens"])
                    model_answer = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                elif model_name == "mPLUG":
                    config = AutoConfig.from_pretrained(model_params["model_path"], trust_remote_code=True)
                    model = AutoModel.from_pretrained(model_params["model_path"], attn_implementation='flash_attention_2', torch_dtype=torch.bfloat16, trust_remote_code=True).eval().to(DEVICE)
                    tokenizer = AutoTokenizer.from_pretrained(model_params["model_path"])
                    processor = model.init_processor(tokenizer)
                    messages = [{
                        "role": "user",
                        "content": """<|image|> """ * len(images) + question_prompt
                    },
                    {
                        "role": "assistant",
                        "content": ""
                    }]
                    inputs = processor(messages, images=images, videos=None)
                    inputs.to('cuda')
                    inputs.update({
                        'tokenizer': tokenizer,
                        'max_new_tokens': model_params["max_new_tokens"],
                        'decode_text': True,
                    })
                    model_answer = model.generate(**inputs)

                print(f'{model_name.capitalize()}: {model_answer}')
                data["model_answer"] = model_answer
                results.append(data)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            for item in results:
                json.dump(item, output_file, ensure_ascii=False)
                output_file.write('\n')

# 定义模型配置
models = {
    "claude": {
        "client": Anthropic(api_key="YOUR_CLAUDE_API_KEY"),
        "params": {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000
        }
    },
    "gpt4": {
        "client": OpenAI(api_key="YOUR_GPT4_API_KEY"),
        "params": {
            "model": "gpt-4o",
        }
    },
    "idefics": {
        "client": None,
        "params": {
            "model_name": "HuggingFaceM4/idefics2-8b",
            "max_new_tokens": 500
        }
    },
    "mPLUG": {
        "client": None,
        "params": {
            "model_path": 'iic/mPLUG-Owl3-7B-240728',
            "max_new_tokens": 100
        }
    }
}

# 输入和输出目录
input_roots = [
    "/home/baiqiao/MVSR/other_all_image/qa_new/among",
    "/home/baiqiao/MVSR/other_all_image/qa_new/around",
    "/home/baiqiao/MVSR/other_all_image/qa_new/around_new",
    "/home/baiqiao/MVSR/other_all_image/qa_new/linear",
    "/home/baiqiao/MVSR/other_all_image/qa_new/rotation"
]

output_roots = {
    "claude": "/home/baiqiao/MVSR/exp/Claude3_0326",
    "gpt4": "/home/baiqiao/MVSR/exp/GPT4o_0323",
    "idefics": "/home/baiqiao/MVSR/exp/idefics2",
    "mPLUG": "/home/baiqiao/MVSR/exp/mPLUG"
}

# 新的根目录
new_root = "/root"

# 处理每个模型
for model_name, model_info in models.items():
    print(f"Processing with model: {model_name}")
    for input_root in input_roots:
        process_json_files(input_root, output_roots[model_name], model_name, model_info["client"], model_info["params"], new_root)