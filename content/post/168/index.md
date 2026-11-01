{
  "title": "自定义docker容器",
  "date": "2018-07-04T17:06:00+08:00",
  "lastmod": "2018-08-29T15:48:10+08:00",
  "typecho_cid": 168,
  "url": "/archives/168/",
  "comments": false,
  "draft": false,
  "slug": "168",
  "categories": [
    "开发"
  ],
  "tags": [
    "docker"
  ],
  "math": false
}

## 准备docker环境 ##
去官网下载docker环境，此处使用win10的docker环境，若早期版本的windows要安装额外的工具
[![docker1.png](/images/recovered/01c0e22974569dc4593d.png)](/images/recovered/01c0e22974569dc4593d.png)

检查docker版本
[![docker2.png](/images/recovered/830925c3ab37c2d7e438.png)](/images/recovered/830925c3ab37c2d7e438.png)

## 下载基础环境 ##
本次决定搭建的docker为订书系统，其基于jsp编写，运行在tomcat上，数据库依赖MySQL，故需要一个MySQL和tomcat环境（tomcat环境自带Java）
去[网易镜像中心][3]下载镜像，网易镜像中心与[官方镜像中心][4]保持同步更新，而且对于国内来说速度更快
### 部署MySQL镜像 ###
#### 下载 ####
[![docker3.png](/images/recovered/1a632f713ad5421aa19b.png)](/images/recovered/1a632f713ad5421aa19b.png)

复制下载地址
[![docker4.png](/images/recovered/0fdefff2ae879531d1ad.png)](/images/recovered/0fdefff2ae879531d1ad.png)

mysql镜像下方也有使用说明
[![docker5.png](/images/recovered/aab719749e500dbeb6a9.png)](/images/recovered/aab719749e500dbeb6a9.png)

以及环境变量的描述，是否需要在创建时建立数据库等
[![docker6.png](/images/recovered/0aa26421840a98775868.png)](/images/recovered/0aa26421840a98775868.png)

#### 启动 ####
使用命令启动mysql的docker，指定本机`8006`端口映射到docker的`3306`端口，同时设置数据库`root`用户密码为root `-d`指定为后台运行

    docker run -d -p 8006:3306 -e MYSQL_ROOT_PASSWORD=root  hub.c.163.com/library/mysql:latest

使用命令查看当前运行的docker

    docker ps

[![docker7.png](/images/recovered/a7d1b05a1e66a1b707b8.png)](/images/recovered/a7d1b05a1e66a1b707b8.png)

#### 测试 ####
使用Navicat连接docker的数据库
[![docker18.png](/images/recovered/ff2ead1b06b11f6f212f.png)](/images/recovered/ff2ead1b06b11f6f212f.png)

建立相关数据库，不使用环境变量创建是为了设置字符集
[![docker19.png](/images/recovered/ecbad3febfecb9b854dd.png)](/images/recovered/ecbad3febfecb9b854dd.png)

启用命令行界面创建相关用户并授权
[![docker20.jpg](/images/recovered/7b341d926cee9248fb55.jpg)](/images/recovered/7b341d926cee9248fb55.jpg)

[![docker21.png](/images/recovered/adb89014d00ed3a70b84.png)](/images/recovered/adb89014d00ed3a70b84.png)

导入数据库文件
[![docker22.png](/images/recovered/9ba6c88e333a55f2db33.png)](/images/recovered/9ba6c88e333a55f2db33.png)

[![docker23.png](/images/recovered/6bda2598479bce2e2807.png)](/images/recovered/6bda2598479bce2e2807.png)

### 部署Tomcat镜像 ###
查看本机的ip
[![docker8.png](/images/recovered/8021a0d857fd6b001226.png)](/images/recovered/8021a0d857fd6b001226.png)

#### 下载 ####
从镜像中心下载tomcat
[![docker9.png](/images/recovered/b28b1bcbb0e82d020769.png)](/images/recovered/b28b1bcbb0e82d020769.png)

[![docker10.png](/images/recovered/12fe96b6de3acfef0ef8.png)](/images/recovered/12fe96b6de3acfef0ef8.png)

查看镜像中配置的tomcat目录
[![docker11.png](/images/recovered/75e86f031fb7d34311b6.png)](/images/recovered/75e86f031fb7d34311b6.png)

查看当前已经下载的镜像

    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                     TAG                 IMAGE ID            CREATED             SIZE
    hub.c.163.com/library/tomcat   latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql    latest              9e64176cd8a2        14 months ago       407MB

编写Dockerfile文件将工程移到tomcat的webapps目录下

    from hub.c.163.com/library/tomcat
    
    MAINTAINER fjy8018 fjy8018@gmail.com
    
    COPY /OrderBooks /usr/local/tomcat/webapps/OrderBooks

[![docker14.png](/images/recovered/d799a55bd512ea97c807.png)](/images/recovered/d799a55bd512ea97c807.png)

修改工程中的数据库地址，地址为ip+暴露的docker端口
[![docker15.png](/images/recovered/48c4ec0c316c59bbe563.png)](/images/recovered/48c4ec0c316c59bbe563.png)

[![docker16.png](/images/recovered/55b8f8fda9dba9733c50.png)](/images/recovered/55b8f8fda9dba9733c50.png)

使用`docker build -t orderbook .`命令将docker打包成镜像
[![docker13.png](/images/recovered/0ce5fbe0f3cce67dde58.png)](/images/recovered/0ce5fbe0f3cce67dde58.png)

#### 启动 ####
使用命令启动带工程的tomcat，指定访问端口为8888

    docker run -d -p 8888:8080 orderbook:latest

[![docker24.png](/images/recovered/f1c1037528c6b4701a3e.png)](/images/recovered/f1c1037528c6b4701a3e.png)

#### 配置 ####
由于使用了jsp+jdbc作为数据库连接，故需要进入容器内部将jdbc的jar复制到tomcat的lib目录下，否则tomcat会报无法加载驱动，使用命令进入容器内部

    docker exec -it {容器ID} /bin/sh

使用exec命令比attach优势在于，exec进入容器后再使用exit命令不会令容器停止
进入容器将工程的lib复制到tomcat中的lib

    PS D:\JAVA WORKSPACE\dockerTemp> docker exec -it 6fe288a25be0 /bin/sh
    # cp /usr/local/tomcat/webapps/OrderBooks/WebRoot/WEB-INF/lib/mysql-connector-java-5.1.45-bin.jar /usr/local/tomcat/lib
    # exit
    PS D:\JAVA WORKSPACE\dockerTemp> docker restart 6fe288a25be0
    6fe288a25be0

## 测试 ##
外部浏览器访问工程
[![docker25.png](/images/recovered/86877faf729f9132095f.png)](/images/recovered/86877faf729f9132095f.png)

工程正常访问
[![docker26.png](/images/recovered/3350459c15eb826039b8.png)](/images/recovered/3350459c15eb826039b8.png)

## 提交到网易镜像仓库 ##
[官方推送指南][27]
### 提交修改的镜像 ###
`docker commit`提交修改的镜像

    PS D:\JAVA WORKSPACE\dockerTemp> docker commit 6fe288a25be0 orderbooks
    sha256:30c6a878adc80f54118f5c67c39c271baa5dc68006aa26b64ef5281832fb4b37
    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                     TAG                 IMAGE ID            CREATED             SIZE
    orderbooks                     latest              30c6a878adc8        5 seconds ago       301MB
    orderbook                      latest              a57e26354272        10 minutes ago      300MB
    hub.c.163.com/library/tomcat   latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql    latest              9e64176cd8a2        14 months ago       407MB

提交mysql容器的修改
    PS D:\JAVA WORKSPACE\dockerTemp> docker commit 43146ddfc771 hub.c.163.com/fjy8018/mysql-orderbooks
    sha256:37a82bac5f71d54e3ff31b0ddd795604e46d4f2e4dde8a6a73d556cc5f26411a
    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                                TAG                 IMAGE ID            CREATED             SIZE
    hub.c.163.com/fjy8018/mysql-orderbooks    latest              37a82bac5f71        3 seconds ago       407MB
    orderbooks                                latest              30c6a878adc8        13 minutes ago      301MB
    hub.c.163.com/fjy8018/tomcat-orderbooks   latest              30c6a878adc8        13 minutes ago      301MB
    orderbook                                 latest              a57e26354272        23 minutes ago      300MB
    hub.c.163.com/library/tomcat              latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql               latest              9e64176cd8a2        14 months ago       407MB

### 推送镜像 ###
将镜像推送到网易仓库
[![docker27.png](/images/recovered/8cd331a04ec140feb67c.png)](/images/recovered/8cd331a04ec140feb67c.png)

登录到网易镜像仓库查看，默认推送会设置为private，推送完成
[![docker28.png](/images/recovered/9a17c004e7409263453d.png)](/images/recovered/9a17c004e7409263453d.png)


  [3]: https://c.163yun.com/hub#/m/home/
  [4]: https://hub.docker.com/
  [27]: https://www.163yun.com/help/documents/15587826830438400
