import base64
import io
import json
import os

import dotenv
import gradio as gr
import requests
import retrying
from PIL import Image


@retrying.retry(stop_max_attempt_number=2, wait_fixed=1000)
def translate(text):
    with requests.get('https://lingva.thedaviddelta.com/api/v1/auto/en/' + text) as response:
        text = ''
        if response.status_code == 200:
            data = response.json()
            text = data['translation']
        return text


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


# 图生图
@retrying.retry(stop_max_attempt_number=2, wait_fixed=1000)
def flux_schnell(prompt, inference_steps, image_size):
    # 获取图像的宽度和高度
    image_size = {
        '1:1': '1024x1024',
        '1:2': '512x1024',
        '3:2': '768x512',
        '3:4': '768x1024',
        '16:9': '1024x576',
        '9:16': '576x1024',
    }[image_size]

    # 设置请求头
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        'Authorization': 'Bearer ' + os.getenv('SILICONFLOW_API_KEY'),
    }
    # 设置请求参数
    data = {
        "prompt": prompt,
        "image_size": image_size,
        "num_inference_steps": inference_steps,
    }

    url = "https://api.siliconflow.cn/v1/black-forest-labs/FLUX.1-schnell/text-to-image"
    with requests.post(url, data=json.dumps(data), headers=headers) as response:
        res = response.json()
        image_url = res['images'][0]['url']
        with requests.get(image_url) as image_response:
            img = Image.open(io.BytesIO(image_response.content))
            return img


def dosomething1(image, inference_steps, guidance_scale, image_size):
    return sdxl_img2img(image, inference_steps, guidance_scale, image_size)


def dosomething2(prompt, inference_steps, image_size):
    return flux_schnell(translate(prompt), inference_steps, image_size)


# 这里是主程序的代码
if __name__ == "__main__":
    # 加载配置
    dotenv.load_dotenv()

    visible_tab = os.getenv('VISIBLE_TAB')
    # 定义每个选项卡中的内容
    with gr.Blocks() as demo:
        with gr.Tab("图片动漫化", visible=True if visible_tab == '' or visible_tab == 'tab1' else False):
            gr.Markdown(
                "<h2 style='text-align: center;'>图片动漫化（基于Stable Diffusion模型）</h2>")  # Title for Tab 1
            with gr.Row():
                with gr.Column():
                    input_1_1 = gr.Image(label='选择原图', type='pil')
                    input_1_2 = gr.Number(minimum=1, maximum=50, value=20)
                    input_1_3 = gr.Slider(minimum=0, maximum=20, value=7.5, step=0.1)
                    input_1_4 = gr.Dropdown(['1:1', '1:2', '3:2', '3:4', '16:9', '9:16', ], label='生成图片比例',
                                            value='1:1')
                    submit_btn_1 = gr.Button("提交", variant="primary")
                with gr.Column():
                    output_image_1 = gr.Image(label="生成的图片")

            submit_btn_1.click(dosomething1, inputs=[input_1_1, input_1_2, input_1_3, input_1_4, ],
                               outputs=output_image_1)
        with gr.Tab("FLUX.1-schnell(trial)", visible=True if visible_tab == '' or visible_tab == 'tab2' else False):
            gr.Markdown("<h2 style='text-align: center;'>图片生成（基于FLUX.1-schnell模型）</h2>")  # Title for Tab 1
            with gr.Row():
                with gr.Column():
                    input_2_1 = gr.Textbox(label='图片描述')
                    input_2_2 = gr.Number(label='num_inference_steps', minimum=1, maximum=100, value=20)
                    input_2_3 = gr.Dropdown(label='生成图片比例',
                                            choices=['1:1', '1:2', '3:2', '3:4', '16:9', '9:16', ],
                                            value='1:1')
                    submit_btn_2 = gr.Button("提交", variant="primary")
                with gr.Column():
                    output_image_2 = gr.Image(label="生成的图片")

            submit_btn_2.click(dosomething2, inputs=[input_2_1, input_2_2, input_2_3, ],
                               outputs=output_image_2)

    demo.launch(server_name='0.0.0.0', server_port=7861)
