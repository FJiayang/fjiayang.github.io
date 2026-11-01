{
  "title": "DeepSeek 本地部署开启联网搜索",
  "date": "2025-02-09T17:28:00+08:00",
  "lastmod": "2025-03-30T11:42:22+08:00",
  "typecho_cid": 289,
  "url": "/archives/289/",
  "comments": false,
  "draft": false,
  "slug": "289",
  "categories": [
    "开发"
  ],
  "tags": [
    "AI",
    "DeepSeek",
    "LLM"
  ],
  "math": true
}

## 背景
由于官方DeepSeek频繁不可用，第三方API站点部署的全量模型无法联网，因此有需要联网推理的场景只能使用本地部署解决。

## 环境
CPU：12700
内存：32G DDR4 3200
显卡：RTX 2060 Super

## 模型准备
受显存限制，使用ollama只能下载8b和14b模型。
- 8b模型可以完全加载到显存中，使用cuda推理。
- 14b模型需要利用CPU+GPU混合推理。
![file-20250209141718762.png](/images/recovered/98ccd7f0295a200a3fbf.png)

本地下载开源docker镜像open-webui
```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```
该镜像下载困难可以手动传到阿里云镜像仓库做一次代理，本次使用我同步的代理镜像启动
```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --rm registry.cn-guangzhou.aliyuncs.com/fjy8018_proxy/open-webui:main
```
首次启动耗时较长，耐心等待，显示如下画面表示启动完成
![file-20250209142407547.png](/images/recovered/b3dabb81423cc8bc32bf.png)

## 联网API
进入http://localhost:3000/admin/settings 点击联网搜索配置搜索引擎
![file-20250209142632172.png](/images/recovered/fae0dfe307462432b210.png)

目前有3种免费的联网搜索API，各有优劣

### Duckduckgo

优点：免费，无需API配置
缺点：网络无法直接访问。

### Bing Search

优点：免费，国内网络可直连。
缺点：需要微软账户+信用卡认证。

### Google Search

优点：免费，搜索内容可靠。
缺点：需要配置，网络无法直连。

此处为保障最好的搜索质量，使用Google搜索API接入。

#### 申请API和密钥

进入谷歌可编程搜索引擎官网：[Programmable Search Engine  |  Google for Developers](https://developers.google.com/custom-search?hl=zh-cn) 创建搜索引擎
![file-20250209143003526.png](/images/recovered/b739c4c62c30de18c5a7.png)

点击控制面板
![file-20250209143022106.png](/images/recovered/a57cfc860c56392b0c5f.png)

创建搜索引擎，名称任意
![file-20250209143108637.png](/images/recovered/9b8c140d95ed6c7f0a07.png)

创建后得到搜索引擎ID
![file-20250209143200907.png](/images/recovered/1bf9fbd72327fcbdf3c5.png)

选择程序化访问
![file-20250209143216062.png](/images/recovered/0b53f6056d86672f23b8.png)

获取密钥
![file-20250209143244278.png](/images/recovered/e93f44de19e056297f6d.png)

#### 配置联网搜索

选择google pse，填写密钥和搜索ID
![file-20250209143347970.png](/images/recovered/3c4fee9eebf56ef41f69.png)

## 验证

### 8b + 联网搜索
使用8b+联网搜索验证
![file-20250209145225878.gif](/images/recovered/57dd520b810eb73609a7.gif)

容器日志可以看到搜索到的文本内容
![file-20250209145333195.png](/images/recovered/7060181e74d37ad22764.png)

8b联网+推理显存沾满，显卡满载，但不需要CPU参与推理，32token/s，速度较快。
![file-20250209144633904.png](/images/recovered/57dd87e5c848f182ab12.png)

### 14b+联网搜索
![file-20250209151556837.png](/images/recovered/613753ddaffd4761283a.png)
改成14b后，token速度下降到7token/s，勉强可用。

由于显存不足，需要CPU+GPU混合推理，显卡cuda性能无法完全利用，CPU占用率高。
![file-20250209151543095.png](/images/recovered/a339d8b45479c221132c.png)
