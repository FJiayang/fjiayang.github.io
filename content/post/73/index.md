{
  "title": "使用宝塔部署Java Web服务",
  "date": "2018-01-24T20:30:00+08:00",
  "lastmod": "2023-09-07T10:11:33+08:00",
  "typecho_cid": 73,
  "url": "/archives/73/",
  "comments": false,
  "draft": false,
  "slug": "73",
  "categories": [
    "服务器"
  ],
  "tags": [],
  "math": true
}

## 环境准备 ##
之前的文章讲到使用宝塔搭建树莓派运维环境，搭建nextcloud应用，现在在原有基础上搭建小型Java web服务

## 工程准备 ##
以下是在Windows环境中用myeclipse编写好的```java web```工程，将其打包为`zip`文件
![javaweb1.png][1]

![javaweb2.png][2]

![javaweb3.png][3]
### 上传工程文件 ###
进入宝塔面板，选择文件，进入Tomcat文件目录```/www/server/tomcat/webapps```
![javaweb4.png][4]

上传压缩好的工程文件
![javaweb5.png][5]

![javaweb6.png][6]

点击命令行按钮，输入解压命令```unzip OrderBooks.zip```
![javaweb7.png][7]

![javaweb8.png][8]

解压完成后修改权限为```777```，所有者为```www```
![javaweb9.png][9]

![javaweb10.png][10]

### 修改Tomcat工程配置文件 ###
进入Tomcat下的```conf```目录，找到``server.xml```文件，配置工程的实际路径和地址栏显示路径，```path```后为显示路径，```docBase```为实际路径，修改后保存
![javaweb10-1.png][11]

![javaweb10-2.png][12]

### 开放防火墙端口 ###
进入安全面板，在防火墙中放行```8080```端口
![javaweb14.png][13]

### 启动Tomcat服务 ###
进入软件管理面板，找到```Tomcat 8``` ，点击```设置```，选择```重启```
![javaweb11.png][14]

![javaweb12.png][15]

![javaweb13.png][16]

## 完成 ##
浏览器中打开树莓派IP+8080端口号+server.xml配置的路径名即可看到Java web服务已正常运行
![javaweb15.png][17]


[1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygNZa.png
[2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yg7n0.png
[3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygWEJ.png
[4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygvTd.png
[5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygh71.png
[6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygQ8u.png
[7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygaXD.png
[8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yg0aL.png
[9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygj2v.png
[10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygp1i.png
[11]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygF7R.png
[12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygSEW.png
[13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygBew.png
[14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygP98.png
[15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygxwg.png
[16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygT8X.png
[17]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yg9BG.png
