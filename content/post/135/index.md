{
  "title": "阿里云CDN加速使用方法",
  "date": "2018-03-16T23:52:00+08:00",
  "lastmod": "2023-09-07T09:28:56+08:00",
  "typecho_cid": 135,
  "url": "/archives/135/",
  "comments": false,
  "draft": false,
  "slug": "135",
  "categories": [
    "服务器"
  ],
  "tags": [],
  "math": true
}

## 前提条件 ##
使用国内CDN加速服务前提条件几乎都是：**网站必须已经备案**

## CDN作用 ##
CDN（云分发）可以结合优质的网络节点资源、传输路由技术优势，有效降低用户访问延迟，提升可用性。具有按需计费，资源弹性扩容等特点。
说白了就是能加快访问速度

## 教程 ##
### 开启阿里云CDN服务 ###
在阿里云处购买CDN服务，考虑到仅仅为了学习和测试，因此本人的CDN服务购买流量为20G，开通后会有邮件提醒
![开启阿里云CDN服务][1]

### 配置阿里云CDN ###
在阿里云首页登录控制台，进入CDN控制台
![登录控制台][2]

选择域名管理，添加需要加速的域名
![进入CDN控制台][3]

![添加需要加速的域名][4]

逐步配置
![逐步配置][5]

![图片加速][6]

![协议][7]

配置HTTPS，上传SSL证书
![配置HTTPS][8]

配置好后等待1-2分钟会生成CDN加速的域名
![生成CDN加速的域名][9]

复制加速域名，登录自己的域名控制台，设置加速域名的解析
![域名控制台][10]

### 配置加速域名解析 ###
解析为CNAME，即解析到另一域名
![解析为CNAME][11]

![解析到另一域名][12]


**配置好后等待20-30分钟才会生效**

### 检查加速域名解析是否生效 ###
这里使用`Windows powershell`命令行工具`ping`目标地址，若解析到`**.kunluncan.com`则已经生效
![检查加速域名解析是否生效][13]

### 监控 ###
在多次访问后查看监控才会有流量显示，包含命中率和流量信息
![监控][14]

![流量显示][15]

## 多地访问测试 ##
使用第三方网站进行全国多地的ping测试，可看到原本只有一个固定ip的博客网站已经被加速为34+个CDN加速IP地址，国内访问速度均在50ms以内
![多地访问测试][16]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J53M1.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J57UJ.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5vf0.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5qvr.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5WlF.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J54fe.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5Clc.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5mLN.png
  [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5MYt.png
  [10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5AjM.png
  [11]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J55V6.png
  [12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J584T.png
  [13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5chK.png
  [14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5HF7.png
  [15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5GAs.png
  [16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5bGu.png
