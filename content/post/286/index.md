{
  "title": "基于 ChatGLM2-6B 搭建个人知识库",
  "date": "2023-09-06T22:43:00+08:00",
  "lastmod": "2025-03-30T16:20:10+08:00",
  "typecho_cid": 286,
  "url": "/archives/286/",
  "comments": false,
  "draft": false,
  "slug": "286",
  "categories": [
    "学习"
  ],
  "tags": [
    "ChatGLM",
    "AI",
    "LLM"
  ],
  "math": true
}

## 背景

ChatGLM2-6B 是开源中英双语对话模型 ChatGLM-6B的第二代版本，提升了性能和推理能力，可结合Langchain-Chatchat和Embedding 可实现基于本地知识库的推理能力



## 准备环境

由于需要构建强大的知识库而非通过prompt组装问答方式，故需要更大的显存和内存，此处直接使用阿里云提供的A10显卡，可免费试用3个月

### 申请机器

![1](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/1.png)

### 创建工作空间

![2](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/2.png)



### 创建实例

![3](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/3.png)

启动机器后进入工作台

![4](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/4.png)



## 部署ChatGLM2-6B

### 下载仓库

参考[官方仓库](https://github.com/THUDM/ChatGLM2-6B)的部署指南

```bash
$ git clone https://github.com/THUDM/ChatGLM2-6B
$ cd ChatGLM2-6B
```



然后使用 pip 安装依赖：

```bash
$ pip install -r requirements.txt
```

![5](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/5.png)

### 安装git lfs

阿里云的git源直接安装lfs会存在问题，需要安装前置依赖

```bash
$ apt -y install build-essential nghttp2 libnghttp2-dev libssl-dev
$ git lfs install --skip-smudge
```



### 下载模型

```bash
$ git clone https://huggingface.co/THUDM/chatglm2-6b /mnt/workspace/model/chatglm2-6b
$ git lfs fetch
$ git lfs checkout
```

![6](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/6.png)



### 修改启动配置

此处只使用webUI模式验证，修改 web_demo.py

```python
tokenizer= AutoTokenizer.from_pretrained("/mnt/workspace/model/chatglm2-6b", trust_remote_code=True)
model= AutoModel.from_pretrained("/mnt/workspace/model/chatglm2-6b", trust_remote_code=True).half().cuda()

# 要暴露在公网上
demo.queue().launch(share=True, inbrowser=True, server_name='0.0.0.0', server_port=7860)
```



安装启动依赖

```bash
$ pip install gradio
```



### 启动WebUI

```bash
$ python web_demo.py
```

![7](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/7.png)

启动成功

![8](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/8.png)

使用非量化模型，显存占用12G

![9](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/9.png)



### 问答验证

![10](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/10.png)

基于A10显卡推理，运算速度非常快，对问题的理解能力也比之前体验的chatglm-6b更加准确，但依然有不少文字错误

![chatglm2-6b问答1](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/chatglm2-6b问答1.gif)

## 部署Langchain知识库应用

### 介绍

> Langchain-Chatchat是一种利用 [langchain](https://github.com/hwchase17/langchain) 思想实现的基于本地知识库的问答应用，目标期望建立一套对中文场景与开源模型支持友好、可离线运行的知识库问答解决方案。



原理示意图

![langchain+chatglm](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/langchain+chatglm.png)



更多介绍参考[官方仓库](https://github.com/chatchat-space/Langchain-Chatchat)

### 下载仓库

Langchain依赖的python包有些许差别，需要先升级python依赖版本

```bash
$ pip3 install --upgrade pip
$ pip uninstall accelerate
$ pip install accelerate>=0.20.3

# 拉取仓库
$ git clone https://github.com/chatchat-space/Langchain-Chatchat.git

# 进入目录
$ cd Langchain-Chatchat

# 安装全部依赖
$ pip install -r requirements.txt
```

![11](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/11.png)



### 下载Embedding模型

此处使用官方推荐的`m3e-base`模型为例

```bash
$ git clone https://huggingface.co/moka-ai/m3e-base
$ git lfs fetch
$ git lfs checkout
```

![12](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/12.png)



### 修改配置

修改Langchain模型引用配置

```bash
$ cd Langchain-Chatchat
```



复制样例文件，创建新配置`configs/model_config.py` 和 `configs/server_config.py`

本地的 LLM 模型本地存储路径写在 `llm_model_dict` 对应模型的 `local_model_path` 属性中

```python
llm_model_dict={
                "chatglm2-6b": {
                        "local_model_path": "/mnt/workspace/model/chatglm2-6b",
                        "api_base_url": "http://127.0.0.1:9090/v1",  # "name"修改为 FastChat 服务中的"api_base_url"
                        "api_key": "EMPTY"
                    },
                }
```



本地的 Embedding 模型本地存储路径写在 `embedding_model_dict` 对应模型位置

```python
embedding_model_dict = {
                         "m3e-base": "/mnt/workspace/model/m3e-base",
                       }
```

![13](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/13.png)



### 重建知识库

首次使用模型需要重建知识库

```bash
$ python init_database.py --recreate-vs
```

![14](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/14.png)



### 启动知识库

一键启动所有 Fastchat 服务、API 服务、WebUI 服务

```bash
$ python startup.py -a
```

![15](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/15.png)

![16](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/16.png)

### 问答验证

LLM模型验证，连接本地ChatGLM2-6B成功

![17](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/17.png)



工程自带样例知识库，可以使用内置知识库验证，此处跳过，直接使用个人知识库验证

![18](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/18.png)



## 构建知识库

### 基金研报知识库

从天天基金拉取研报：[中信证券：把握宏观政策接连发力下电商板块估值修复机会_天天基金网 (eastmoney.com)](https://fund.eastmoney.com/a/202309062838610791.html)

将内容存储为txt上传到知识库

![19](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/19.png)



基于基金研报知识库问答，总结准确，速度非常快

![20](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/20.png)



推理过程日志，显存占用14G

![21](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/21.png)



### 个人面试知识库

将Java并发知识点转为txt类型知识库上传并创建新的知识库空间

![22](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/22.png)

不使用知识库情况下回答

![23](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/23.png)



使用知识库情况下回答

![24](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/基于ChatGLM2-6B搭建个人知识库/24.png)



显然使用知识库回答更加准确
