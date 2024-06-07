import base64
import io
import json
import os

import dotenv
import gradio as gr
import requests
import retrying
from PIL import Image


# 图生图
@retrying.retry(stop_max_attempt_number=2, wait_fixed=1000)
def sdxl_img2img(image, inference_steps, guidance_scale, image_size):
    # 获取图像的宽度和高度
    image_size = {
        '1:1': '1024x1024',
        '1:2': '1024x2048',
        '3:2': '1536x1024',
        '3:4': '1536x2048',
        '16:9': '2048x1152',
        '9:16': '1152x2048',
    }[image_size]
    # 将 PIL 图像保存到内存中的字节流
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    base64_string = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # 设置请求头
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + os.getenv('SILICONFLOW_API_KEY'),
    }
    # 设置请求参数
    data = {
        "prompt": "Transform all objects in the scene into a highly detailed and realistic anime style. Ensure that all characters have perfectly proportioned features including complete and natural-looking hands and fingers, and symmetrical, well-defined facial features with no distortions or anomalies. All objects should be rendered with vibrant and colorful details, smooth shading, and dynamic compositions. The style should resemble the works of Studio Ghibli or Makoto Shinkai, with meticulous attention to detail in every aspect, including backgrounds, clothing, and accessories. The overall image should be cohesive, with a harmonious blend of all elements.",
        "image": base64_string,
        "image_size": image_size,
        "batch_size": 1,
        "num_inference_steps": inference_steps,
        "guidance_scale": guidance_scale
    }

    url = "https://api.siliconflow.cn/v1/stabilityai/stable-diffusion-xl-base-1.0/image-to-image"
    with requests.post(url, data=json.dumps(data), headers=headers) as response:
        res = response.json()
        image_url = res['images'][0]['url']
        with requests.get(image_url) as image_response:
            img = Image.open(io.BytesIO(image_response.content))
            return img


def dosomething(image, inference_steps, guidance_scale, image_size):
    return sdxl_img2img(image, inference_steps, guidance_scale, image_size)


# 这里是主程序的代码
if __name__ == "__main__":
    # 加载配置
    dotenv.load_dotenv()
    iis = [
        gr.Image(label='选择原图', type='pil'),
        gr.Number(minimum=1, maximum=50, value=20),
        gr.Slider(minimum=0, maximum=20, value=7.5, step=0.1),
        gr.Dropdown(['1:1', '1:2', '3:2', '3:4', '16:9', '9:16', ], label='生成图片比例', value='1:1')
    ]
    oo = gr.Image(label='生成的图片')

    demo = gr.Interface(dosomething, inputs=iis, outputs=oo, title='图片动漫化（基于Stable Diffusion模型）')

    demo.launch(server_port=7861)
