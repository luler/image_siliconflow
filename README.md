# 图片动漫化（基于Stable Diffusion模型）

本项目是基于siliconflow.cn提供的开放接口搭建的，只做学习测试使用

## 获取配置

前往：https://cloud.siliconflow.cn/keys ，注册并获取到api token（注册赠送免费额度，可以满足个人基本使用）
获取到token后，创建.env文件，输入并替换下面配置

```
SILICONFLOW_API_KEY=api token
```

## 安装

### 方式一：本地python环境启动

安装所需软件包

``` 
pip install -i https://mirror.baidu.com/pypi/simple -r requirements.txt
```

启动

``` 
python main.py
```

### 方式二：docker-compose一键安装

```
docker-compose up -d
```

## 访问：http://127.0.0.1:7861/