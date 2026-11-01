{
  "title": "使用宝塔安装nextcloud私有云服务",
  "date": "2018-01-24T16:49:00+08:00",
  "lastmod": "2023-09-07T10:11:14+08:00",
  "typecho_cid": 53,
  "url": "/archives/53/",
  "comments": false,
  "draft": false,
  "slug": "53",
  "categories": [
    "服务器"
  ],
  "tags": [],
  "math": true
}

## 最终效果 ##
![nextcloud0.png][1]

## 步骤 ##
之前的文章讲到使用宝塔运维树莓派Ubuntu16.04系统，现在在原有基础上搭建个人私有云服务nextcloud，与owncloud搭建方法几乎一致

### 下载 ###
百度搜索```nextcloud```即可找到官方下载地址，选择```download```，下载```zip```版本文件

![nextcloud1.png][2]

![nextcloud2.png][3]

![nextcloud3.png][4]

![nextcloud4.png][5]

### 准备站点 ###
进入宝塔面板，选择```网站```，点击```添加站点```
![nextcloud5.png][6]

![nextcloud5.5.png][7]

输入树莓派的局域网地址或域名，根目录为```wwwroot```
![nextcloud6.png][8]

点击```文件```
![nextcloud7.png][9]

默认打开的根目录即```wwwroot```,此处可见自动生成的站点文件
![nextcloud8.png][10]

在浏览器中打开树莓派地址加```/index.html```可见站点创建成功
![nextcloud9.png][11]

### 上传nextcloud ###
回到宝塔，点击```上传```，选择下载好的```nextcloud```文件，点击上传，直到显示```已上传成功```
![nextcloud10.png][12]

![nextcloud11.png][13]

![nextcloud12.png][14]

点击```命令行```按钮
![nextcloud13.png][15]

输入解压命令```unzip nextcloud-12.0.4.zip```，等待其自动解压
![nextcloud14.png][16]

刷新根目录可见解压好的文件夹，右边显示所有者为```root```，显然是错误的
![nextcloud15.png][17]

点击```权限```，对```nextcloud```文件夹授予```775```权限
![nextcloud16.png][18]

![nextcloud17.png][19]

### 准备数据库 ###
点击```数据库```，查看数据库密码，**若不是通过宝塔安装MySQL服务者无法在此查看密码**
![nextcloud18.png][20]

![nextcloud19.png][21]

使用命令```mysql -u root -p```，输入密码进入数据库

>root@fjy-desktop:/home/fjy# mysql -u root -p
>Enter password:
>Welcome to the MySQL monitor.  Commands end with ; or \g.
>Your MySQL connection id is 4
>Server version: 5.7.21-0ubuntu0.16.04.1 (Ubuntu)
>
>Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.
>
>Oracle is a registered trademark of Oracle Corporation and/or its
>affiliates. Other names may be trademarks of their respective
>owners.
>
>Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
>
>mysql>

输入如下命令创建```nextcloud```数据库和数据库用户
```CREATE DATABASE nextclouddb;```
```GRANT ALL ON nextclouddb.* TO nextclouddbuser@localhost IDENTIFIED BY 'nextcloud';```
```flush privileges;```

>mysql> CREATE DATABASE nextclouddb;
>Query OK, 1 row affected (0.00 sec)
>
>mysql> GRANT ALL ON nextclouddb.* TO nextclouddbuser@localhost IDENTIFIED BY >'nextcloud';
>Query OK, 0 rows affected, 1 warning (0.00 sec)
>
>mysql> flush privileges;
>Query OK, 0 rows affected (0.00 sec)


### 准备php扩展环境 ###
nextcloud还需其他的PHP扩展环境，运行命令```apt-get  install php-mysql php-json php-xml php-mbstring php-zip php-gd curl php-curl >php-pdo```自动安装扩展
>root@fjy-desktop:/home/fjy# apt-get  install php-mysql php-json php-xml php-mbstring php-zip php-gd curl php-curl >php-pdo
>正在读取软件包列表... 完成
>正在分析软件包的依赖关系树
>正在读取状态信息... 完成
>注意，选中 'php7.0-common' 而非 'php-pdo'
>curl 已经是最新版 (7.47.0-1ubuntu2.5)。
>将会同时安装下列软件：
>  php-common php7.0-curl php7.0-gd php7.0-json php7.0-mbstring php7.0-mysql
>  php7.0-xml php7.0-zip
>下列【新】软件包将被安装：
>  php-common php-curl php-gd php-json php-mbstring php-mysql php-xml php-zip
>  php7.0-common php7.0-curl php7.0-gd php7.0-json php7.0-mbstring php7.0-mysql
>  php7.0-xml php7.0-zip
>升级了 0 个软件包，新安装了 16 个软件包，要卸载 0 个软件包，有 249 个软件包未被升级。
>需要下载 1,508 kB 的归档。
>解压缩后会消耗 6,490 kB 的额外空间。
选择Y
>您希望继续执行吗？ [Y/n] Y
### 安装nextcloud ###
地址栏输入树莓派IP+文件地址即可打开nextcloud页面，此处打开```http://192.168.1.187/nextcloud```
![nextcloud20.png][22]

按照之前设置的信息进行配置，**注意，若报```SQLSTATE[HY000] [2002]```错误，则将```localhost```改为```127.0.0.1```**
![nextcloud21.png][23]

配置后若不会自动跳转则自行输入```http://192.168.1.187/nextcloud```进行登录
![nextcloud22.png][24]

登陆后nextcloud安装完成！
![nextcloud23.png][25]

 [1]: /images/recovered/105114d1832cde042c55.png
 [2]: /images/recovered/59e081402b983d81bef7.png
 [3]: /images/recovered/e6f0d50d0edcb945e1bb.png
 [4]: /images/recovered/cd8c0bed844ad2b1416c.png
 [5]: /images/recovered/1afa3bb193b45d4cb084.png
 [6]: /images/recovered/05fe83fef07308816e5f.png
 [7]: /images/recovered/0a556186253b773cc071.png
 [8]: /images/recovered/9284ef0e4e90cf5b130d.png
 [9]: /images/recovered/d8f584d67b75215be799.png
 [10]: /images/recovered/b21cfc58084573a7cd27.png
 [11]: /images/recovered/749e728bf5d925de7481.png
 [12]: /images/recovered/d857a52f094f9e9c7fdf.png
 [13]: /images/recovered/55a1d58ec348df35d4cb.png
 [14]: /images/recovered/7a8504a4326e00a1d7c7.png
 [15]: /images/recovered/e9b215ab12654e5c4fd0.png
 [16]: /images/recovered/079c8838bf10db7354cf.png
 [17]: /images/recovered/0436f48fea8da3727b8a.png
 [18]: /images/recovered/4097d19ee3dd9205b0a6.png
 [19]: /images/recovered/cc287e3af62ebaa896ef.png
 [20]: /images/recovered/326584abee4bfe33c859.png
 [21]: /images/recovered/09a51d091ebf62e6c77c.png
 [22]: /images/recovered/31df481befd24dd07644.png
 [23]: /images/recovered/c077cb22b3a6f435cd44.png
 [24]: /images/recovered/bc32fe50ebc22e684641.png
 [25]: /images/recovered/927ab954b160a4adc75a.png
