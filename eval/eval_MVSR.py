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
import yaml
import argparse

from utils import replace_old_root,load_images,find_json_files,encode_image
# 全局变量
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
Q_PREFIX = "Based on these images, answer the question based on this rule: You only need to provide *ONE* correct answer selecting from the options listed below. For example, if you think the correct answer is 'A. above' from ' A. above B. under C. front D. behind.', your response should only be 'A. above'.\nThe Question is: "



def process_images(image_paths, model_type):
    """统一处理不同模型的图像输入"""
    processors = {
        "claude": lambda paths: [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{Image.open(p).format.lower()}",
                    "data": base64.b64encode(open(p, 'rb').read()).decode()
                }
            } for p in paths
        ],
        
        "gpt4": lambda paths: [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encode_image(p)}",
                    "detail": "high"
                }
            } for p in paths
        ],
        
        "idefics": lambda paths, processor: processor(
            text=processor.apply_chat_template(
                [{"role": "user", "content": [{"type": "image"} for _ in paths]}],
                add_generation_prompt=True
            ),
            images=paths,
            return_tensors="pt"
        ).to(DEVICE),
        
        "mPLUG": lambda paths, tokenizer: tokenizer(
            [{"role": "user", "content": "<|image|> " * len(paths)}],
            images=paths,
            videos=None
        ).to('cuda')
    }
    
    return processors[model_type](image_paths)

def process_question(question, images, model_name, model_params):
    """处理问题并获取模型回答"""
    question_prompt = Q_PREFIX  + question.replace("A.", " Choices: A.")
    
    model_handlers = {
        "claude": lambda: model_params["client"].messages.create(
            model=model_params["model"],
            max_tokens=model_params["max_tokens"],
            messages=[{
                "role": "user",
                "content": [{"type": "text", "text": question_prompt}] + process_images(images, "claude")
            }]
        ).content[0].text,
        
        "gpt4": lambda: model_params["client"].chat.completions.create(
            model=model_params["model"],
            messages=[{
                "role": "user",
                "content": [{"type": "text", "text": question_prompt}] + process_images(images, "gpt4")
            }]
        ).choices[0].message.content,
        
        "idefics": lambda: (
            lambda processor, model: processor.batch_decode(
                model.generate(
                    **process_images(images, "idefics", processor),
                    max_new_tokens=model_params["max_new_tokens"]
                ),
                skip_special_tokens=True
            )[0]
        )(
            AutoProcessor.from_pretrained(model_params["model_name"]),
            AutoModelForVision2Seq.from_pretrained(model_params["model_name"]).to(DEVICE)
        ),
        
        "mPLUG": lambda: AutoModel.from_pretrained(
            model_params["model_path"],
            config=AutoConfig.from_pretrained(model_params["model_path"], trust_remote_code=True),
            attn_implementation='flash_attention_2',
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        ).eval().to(DEVICE).generate(
            **{**process_images(images, "mPLUG", AutoTokenizer.from_pretrained(model_params["model_path"])),
               'tokenizer': AutoTokenizer.from_pretrained(model_params["model_path"]),
               'max_new_tokens': model_params["max_new_tokens"],
               'decode_text': True}
        )
    }
    
    return model_handlers[model_name]()

def process_batch(question_file, output_dir, model_name, model_params, image_folder):
    """
    处理 JSON 文件，调用指定模型回答问题，并保存结果
    """
    output_path = os.path.join(output_dir, f"{model_name}_answers.jsonl")
    results = []
    with open(question_file, 'r', encoding='utf-8') as f:

        for line in f:
            data = json.loads(line.strip())
            question = data.get("question")
            image_paths = data.get("images", [])

            image_paths = replace_old_root(image_paths, image_folder)
            images = load_images(image_paths)

            # 调用统一的处理问题函数
            model_answer = process_question(question, images, model_name, model_params)

            print(f'{model_name.capitalize()}: {model_answer}')
            data["model_answer"] = model_answer
            results.append(data)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        for item in results:
            json.dump(item, output_file, ensure_ascii=False)
            output_file.write('\n')


# 加载模型配置
def load_model_configs(model_name):
    config_file = f"{model_name}.yaml"
    with open(config_file, 'r') as f:
        model_params = yaml.safe_load(f)
    return model_params


def main():
    # 默认参数
    default_question_file = ""
    default_output_dir = "results"
    default_image_folder = ''

    parser = argparse.ArgumentParser(description="Process questions and generate answers.")
    parser.add_argument('--model', type=str, required=True, help="Name of the model (e.g., claude, gpt4, idefics, mPLUG).")
    parser.add_argument('--question_file', type=str, default=default_question_file, help="Path to the input JSONL files.")
    parser.add_argument('--output_dir', type=str, default=default_output_dir, help="Path to the output directory.")
    parser.add_argument('--image_folder', type=str, default=default_image_folder, help="New root directory for image paths.")

    args = parser.parse_args()

    model_name = args.model
    question_file = args.question_file
    output_dir = args.output_dir
    image_folder = args.image_folder

    # 加载模型配置
    model_params = load_model_configs(model_name)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # 处理 JSON 文件
    process_batch(question_file, output_dir, model_name, model_params, image_folder)


if __name__ == "__main__":
    main()
