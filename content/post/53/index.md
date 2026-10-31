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

 [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykrLR.png
 [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yknwd.png
 [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygYhe.png
 [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygd9s.png
 [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ygKeN.png
 [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykJBT.png
 [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykyw7.png
 [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yk2A6.png
 [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykgJM.png
 [10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykk4t.png
 [11]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yktbF.png
 [12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykZKr.png
 [13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykflJ.png
 [14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yk6h0.png
 [15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykIL1.png
 [16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykeAa.png
 [17]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykCJD.png
 [18]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yklFu.png
 [19]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykc4v.png
 [20]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yk1KL.png
 [21]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykmji.png
 [22]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykAMg.png
 [23]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykHvw.png
 [24]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykGlW.png
 [25]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yk8f8.png
