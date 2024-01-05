import os

import dotenv
import gradio as gr
import io
import json
import requests
from PIL import Image


# 上传文件
def get_file_path(image):
    image = Image.fromarray(image)
    image_stream = io.BytesIO()
    image.save(image_stream, format='JPEG')
    image_stream.seek(0)
    files = {"pfile": ('filename.jpg', image_stream)}
    headers = {
        'Authorization': 'Bearer ' + os.getenv('MYSTICAI_API_KEY'),
    }
    response = requests.post('https://www.mystic.ai/v3/pipeline_files', files=files, headers=headers)
    data = response.json()
    return data['path']


# 图生图
def sdxl_img2img(image, num_inference_steps, strength):
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + os.getenv('MYSTICAI_API_KEY'),
    }
    data = {
        "pipeline_id_or_pointer": "stabilityai/sdxl-img2img:v1",
        "input_data": [
            {
                "type": "string",
                "value": "fantastic anime style"
            },
            {
                "type": "file",
                "value": None,
                "file_path": get_file_path(image)
            },
            {
                "type": "dictionary",
                "value": {
                    "num_inference_steps": num_inference_steps,
                    "strength": strength
                }
            }
        ],
        "async_run": False
    }
    response = requests.post('https://www.mystic.ai/v3/runs', data=json.dumps(data), headers=headers)
    res = response.json()
    image_url = res['result']['outputs'][0]['value'][0]['file']['url']
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content))
    return img


def dosomething(image, num_inference_steps, strength):
    return sdxl_img2img(image, num_inference_steps, strength)


# 这里是主程序的代码
if __name__ == "__main__":
    # 加载配置
    dotenv.load_dotenv()
    iis = [
        gr.Image(label='选择原图'),
        gr.Number(minimum=1, value=50),
        gr.Slider(minimum=0, maximum=1, value=0.8)
    ]
    oo = gr.Image(label='生成的图片')

    demo = gr.Interface(dosomething, inputs=iis, outputs=oo, title='图片动漫化（基于Stable Diffusion模型）')

    demo.launch(server_name='0.0.0.0', server_port=7861)