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


[1]: /images/recovered/d4d76b582fd3b78efe2e.png
[2]: /images/recovered/3a3458dc75ce73a8904e.png
[3]: /images/recovered/1ab934bc7c1a4d47fd6e.png
[4]: /images/recovered/ee0095bddcbc18f02c79.png
[5]: /images/recovered/fad3f0be3ca4ce6bdf01.png
[6]: /images/recovered/6c06ed82030176758630.png
[7]: /images/recovered/043d11bd49bab350061f.png
[8]: /images/recovered/38e61dbfe40003b8f556.png
[9]: /images/recovered/3a1d4b78d23b890ceae2.png
[10]: /images/recovered/5546abbe8786c0c9c24c.png
[11]: /images/recovered/974b607065eabebc4af2.png
[12]: /images/recovered/68185ea5c714f9bc6f52.png
[13]: /images/recovered/df685e09565cf211f323.png
[14]: /images/recovered/292c1f315e75591078f2.png
[15]: /images/recovered/29712d86653c88dd2711.png
[16]: /images/recovered/1c3eda3a23fd333a072f.png
[17]: /images/recovered/a82c488ecc46e0da4254.png
