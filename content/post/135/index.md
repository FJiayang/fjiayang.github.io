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


  [1]: /images/recovered/534d298e5144ab842b2e.png
  [2]: /images/recovered/95a35679975c70bb6c6b.png
  [3]: /images/recovered/1620f7d092fbbc616164.png
  [4]: /images/recovered/471b4e5b90b2d67b8a6d.png
  [5]: /images/recovered/2f9e683eaad0e8bbac40.png
  [6]: /images/recovered/c0e0967e2a8f304c3302.png
  [7]: /images/recovered/2c63776a3c3a775c8f2d.png
  [8]: /images/recovered/e391f7c205a50a635e79.png
  [9]: /images/recovered/cc4d4fd9524efab323da.png
  [10]: /images/recovered/4b10482a74069c89705c.png
  [11]: /images/recovered/18e20363d9597e39e944.png
  [12]: /images/recovered/713fec9042b19bc85dfd.png
  [13]: /images/recovered/8c68a452030234a2501f.png
  [14]: /images/recovered/97e622c3b26d9f73e58d.png
  [15]: /images/recovered/cde3de201fd5b068b277.png
  [16]: /images/recovered/7e52eea8cd4cb60329b7.png
