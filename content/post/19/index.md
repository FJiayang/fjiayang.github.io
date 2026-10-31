{
  "title": "使用宝塔运维Ubuntu 16.04",
  "date": "2018-01-23T13:11:00+08:00",
  "lastmod": "2023-09-07T10:12:38+08:00",
  "typecho_cid": 19,
  "url": "/archives/19/",
  "comments": false,
  "draft": false,
  "slug": "19",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [],
  "math": true
}

## 系统环境 ##
硬件：树莓派3
![pi.png][1]

CPU：四核1.2GHz Broadcom BCM2837 x64
RAM：1GB
TF容量：32G U1速度
操作系统：ubuntu-mate-16.04.2-desktop-armhf-raspberry-pi
通过简单的方法可烧录TF卡，系统自动安装配置
![diskimage.png][2]

终端输入```sudo raspi-config```启动树莓派配置工具，启动ssh服务并开机启动
操作步骤参考：[玩转树莓派之Ubuntu MATE for the Raspberry 系统安装][3]


<!--more-->

安装宝塔
----
官方安装要求
    安装要求：
    内存：128M以上，推荐512M以上（纯面板约占系统10M内存）
    硬盘：100M以上可用硬盘空间（纯面板约占20M磁盘空间）
    系统：暂时只对 CentOS 6.x / 7.x /Ubuntu/Debian
    确保是干净的操作系统，没有安装过其它环境带的Apache/Nginx/php/MySQL

下面使用putty登录PI，安装宝塔

![pi-bt1.png][4]

自动运行如下
>    root@fjy-desktop:/# wget -O install.sh http://download.bt.cn/install/install-ubuntu.sh && sudo bash install.sh
>    --2018-01-23 13:13:41--  http://download.bt.cn/install/install-ubuntu.sh
>    Resolving download.bt.cn (download.bt.cn)... 103.224.251.67
>    Connecting to download.bt.cn (download.bt.cn)|103.224.251.67|:80... connected.
>    HTTP request sent, awaiting response... 200 OK
>    Length: 13572 (13K) [application/octet-stream]
>    Saving to: ‘install.sh’
>
>    install.sh          100%[===================>]  13.25K  --.-KB/s    in 0s
>
>    2018-01-23 13:13:41 (52.5 MB/s) - ‘install.sh’ saved [13572/13572]
>    
>    +----------------------------------------------------------------------
>    | Bt-WebPanel 5.x FOR Ubuntu/Debian
>    +----------------------------------------------------------------------
>    | Copyright © 2015-2017 BT-SOFT(http://www.bt.cn) All rights reserved.
>    +----------------------------------------------------------------------
>    | The WebPanel URL will be http://SERVER_IP:8888 when installed.
>    +----------------------------------------------------------------------
下面选择确定，输入小写y
>   Do you want to install Bt-Panel to the /www directory now?(y/n): y
然后等待系统自动安装依赖

安装完成后会显示如下信息，提供了出事登录用户名和IP地址
    ==================================================================
    Congratulations! Install succeeded!
    ==================================================================
    Bt-Panel: http://113.83.XX.XXX:8888
    username: admin
    password: 0df18173
    Warning:
    If you cannot access the panel,
    release the following port (8888|888|80|443|20|21) in the security group
    ==================================================================
    Time consumed: 12 Minute!

**但ip地址一般都是不对的，请自行输入```ip addr```查询主机的ip地址**

>      root@fjy-desktop:/# ip addr
>     1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1
>        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
>        inet 127.0.0.1/8 scope host lo
>           valid_lft forever preferred_lft forever
>        inet6 ::1/128 scope host
>           valid_lft forever preferred_lft forever
>     2: enxb827eb9e1f8b: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN group default qlen 1000
>     link/ether b8:27:eb:9e:1f:8b brd ff:ff:ff:ff:ff:ff
>     3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
>        link/ether b8:27:eb:cb:4a:de brd ff:ff:ff:ff:ff:ff
>        inet 192.168.31.9/24 brd 192.168.31.255 scope global dynamic wlan0
>           valid_lft 30658sec preferred_lft 30658sec
>        inet6 fe80::ab44:81:1f49:ce98/64 scope link
>           valid_lft forever preferred_lft forever
由上可知```192.168.31.9```就是我树莓派的局域网地址，因此在浏览器登录的地址为```http://192.168.31.9:8888```
![pi-bt3.png][5]

输入默认账号密码即可登录，登录后进入如下页面，提示安装全套web服务组件

![pi-bt4.png][6]

这里选择安装LAMP组件套装，因为后面打算安装私有云服务（nextcloud），nextcloud对nginx支持并不友好，需要负载均衡的可以安装LNMP
![pi-bt6.png][7]

点击一键安装即可
安装状态可以点击左上角的标号查看
![pi-bt7.png][8]

![pi-bt8.png][9]

点击监软件管理，可以安装其他软件，包括Tomcat、gitlab等，安装Tomcat还会自动配置java和javac环境，可以说是非常的方便
![pi-bt9.png][10]

以后要搭建java web服务，因此这里选择安装Tomcat，版本选择8

![pi-bt10.png][11]

![pi-bt11.png][12]

最后点击监控面板，打开服务器状态监控
![pi-bt12.png][13]

![pi-bt13.png][14]

一段时间后可查看服务器状态曲线图
![pi-bt14.png][15]


----------
有时候安装完成后发现MySQL服务无法被宝塔安装，那么可以到putty中使用命令行自行安装，输入```sudo apt-get install mysql-server```
>root@fjy-desktop:/home/fjy# apt-get install mysql-server
>正在读取软件包列表... 完成
>正在分析软件包的依赖关系树
>正在读取状态信息... 完成
>将会同时安装下列软件：
>  libaio1 libcgi-fast-perl libcgi-pm-perl libevent-core-2.0-5 libfcgi-perl
>  libhtml-template-perl mysql-client-5.7 mysql-client-core-5.7 mysql-common
>  mysql-server-5.7 mysql-server-core-5.7
>建议安装：
>  libipc-sharedcache-perl mailx tinyca
>下列【新】软件包将被安装：
>  libaio1 libcgi-fast-perl libcgi-pm-perl libevent-core-2.0-5 libfcgi-perl
>  libhtml-template-perl mysql-client-5.7 mysql-client-core-5.7 mysql-common
>  mysql-server mysql-server-5.7 mysql-server-core-5.7
>升级了 0 个软件包，新安装了 12 个软件包，要卸载 0 个软件包，有 249 个软件包未被升级。
>需要下载 17.7 MB 的归档。
>解压缩后会消耗 140 MB 的额外空间。
>您希望继续执行吗？ [Y/n] Y
**之后会弹出如下对话框，输入默认数据库管理员密码即可**
![mysql.png][16]


----------
有时候安装后会发现Tomcat无法正常启动，进入putty用命令```javac```，发现未安装jdk
>root@fjy-desktop:/var/lib/mysql# javac
>The program 'javac' can be found in the following packages:
> * default-jdk
> * ecj
> * gcj-5-jdk
> * openjdk-8-jdk-headless
> * gcj-4.8-jdk
> * gcj-4.9-jdk
>Try: apt install <selected package>
>root@fjy-desktop:/var/lib/mysql# java -version
>openjdk version "1.8.0_151"
>OpenJDK Runtime Environment (build 1.8.0_151-8u151-b12-0ubuntu0.16.04.2-b12)
>OpenJDK Client VM (build 25.151-b12, mixed mode)

则输入```sudo apt-get install openjdk-8-jdk```安装jdk环境

>root@fjy-desktop:/var/lib/mysql# apt-get install openjdk-8-jdk
>正在读取软件包列表... 完成
>正在分析软件包的依赖关系树
>正在读取状态信息... 完成
>将会同时安装下列软件：
>  fonts-dejavu-extra libgif7 libice-dev libpthread-stubs0-dev libsm-dev
>  libx11-dev libx11-doc libxau-dev libxcb1-dev libxdmcp-dev libxt-dev
>  openjdk-8-jdk-headless openjdk-8-jre x11proto-core-dev x11proto-input-dev
>  x11proto-kb-dev xorg-sgml-doctools xtrans-dev
>建议安装：
>  libice-doc libsm-doc libxcb-doc libxt-doc openjdk-8-demo openjdk-8-source
>  visualvm icedtea-8-plugin
>下列【新】软件包将被安装：
>  fonts-dejavu-extra libgif7 libice-dev libpthread-stubs0-dev libsm-dev
>  libx11-dev libx11-doc libxau-dev libxcb1-dev libxdmcp-dev libxt-dev
>  openjdk-8-jdk openjdk-8-jdk-headless openjdk-8-jre x11proto-core-dev
>  x11proto-input-dev x11proto-kb-dev xorg-sgml-doctools xtrans-dev
>升级了 0 个软件包，新安装了 19 个软件包，要卸载 0 个软件包，有 249 个软件包未被升级。
>需要下载 11.8 MB 的归档。
>解压缩后会消耗 61.9 MB 的额外空间。
>您希望继续执行吗？ [Y/n] Y


----------
手动安装JDK后应去Tomcat配置文件中更改JAVA_HOME的路径以确保Tomcat正常运行
查看当前系统jre和jdk路径，输入```update-alternatives --config java```和```update-alternatives --config javac```
>root@fjy-desktop:/etc# update-alternatives --config java
>链接组 java (提供 /usr/bin/java)中只有一个候选项：/usr/lib/jvm/java-8-openjdk-ar                                                                                                                                                                                                                                             mhf/jre/bin/java
>无需配置。
>root@fjy-desktop:/etc# update-alternatives --config javac
>链接组 javac (提供 /usr/bin/javac)中只有一个候选项：/usr/lib/jvm/java-8-openjdk-                                                                                                                                                                                                                                             armhf/bin/javac
>无需配置。
输入```root@fjy-desktop:/etc# vi /etc/init.d/tomcat```进入Tomcat配置文件
找到JAVA_HOME，修改为系统配置的jdk路径
默认为
>JAVA_HOME=/usr/java/jdk
>CATALINA_HOME=/www/server/tomcat
改成
>JAVA_HOME=JAVA_HOME=/usr/lib/jvm/java-8-openjdk-armhf/jre
>CATALINA_HOME=/www/server/tomcat
保存退出即可


[1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykUMd.png
[2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykL61.png
[3]: https://9sb.org/722
[4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykFYF.png
[5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykRur.png
[6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykTU0.png
[7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykSVT.png
[8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykjM7.png
[9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykbfs.png
[10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykQUe.png
[11]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykpP6.png
[12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykqGy.png
[13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykhYc.png
[14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yk3lK.png
[15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ykNvN.png
[16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yk7jj.png
