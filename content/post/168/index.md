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
[![docker1.png](https://i.loli.net/2018/08/29/5b85f90c1c85d.png)](https://i.loli.net/2018/08/29/5b85f90c1c85d.png)

检查docker版本
[![docker2.png](https://i.loli.net/2018/08/29/5b85f90c196dc.png)](https://i.loli.net/2018/08/29/5b85f90c196dc.png)

## 下载基础环境 ##
本次决定搭建的docker为订书系统，其基于jsp编写，运行在tomcat上，数据库依赖MySQL，故需要一个MySQL和tomcat环境（tomcat环境自带Java）
去[网易镜像中心][3]下载镜像，网易镜像中心与[官方镜像中心][4]保持同步更新，而且对于国内来说速度更快
### 部署MySQL镜像 ###
#### 下载 ####
[![docker3.png](https://i.loli.net/2018/08/29/5b85f90c20a75.png)](https://i.loli.net/2018/08/29/5b85f90c20a75.png)

复制下载地址
[![docker4.png](https://i.loli.net/2018/08/29/5b85f90c2441c.png)](https://i.loli.net/2018/08/29/5b85f90c2441c.png)

mysql镜像下方也有使用说明
[![docker5.png](https://i.loli.net/2018/08/29/5b85f90c21d70.png)](https://i.loli.net/2018/08/29/5b85f90c21d70.png)

以及环境变量的描述，是否需要在创建时建立数据库等
[![docker6.png](https://i.loli.net/2018/08/29/5b85f90c2b7ab.png)](https://i.loli.net/2018/08/29/5b85f90c2b7ab.png)

#### 启动 ####
使用命令启动mysql的docker，指定本机`8006`端口映射到docker的`3306`端口，同时设置数据库`root`用户密码为root `-d`指定为后台运行

    docker run -d -p 8006:3306 -e MYSQL_ROOT_PASSWORD=root  hub.c.163.com/library/mysql:latest

使用命令查看当前运行的docker

    docker ps

[![docker7.png](https://i.loli.net/2018/08/29/5b85f90c21df0.png)](https://i.loli.net/2018/08/29/5b85f90c21df0.png)

#### 测试 ####
使用Navicat连接docker的数据库
[![docker18.png](https://i.loli.net/2018/08/29/5b85f9157d4de.png)](https://i.loli.net/2018/08/29/5b85f9157d4de.png)

建立相关数据库，不使用环境变量创建是为了设置字符集
[![docker19.png](https://i.loli.net/2018/08/29/5b85f91580611.png)](https://i.loli.net/2018/08/29/5b85f91580611.png)

启用命令行界面创建相关用户并授权
[![docker20.jpg](https://i.loli.net/2018/08/29/5b85f91584d58.jpg)](https://i.loli.net/2018/08/29/5b85f91584d58.jpg)

[![docker21.png](https://i.loli.net/2018/08/29/5b85f91e84f85.png)](https://i.loli.net/2018/08/29/5b85f91e84f85.png)

导入数据库文件
[![docker22.png](https://i.loli.net/2018/08/29/5b85f91e8a9e4.png)](https://i.loli.net/2018/08/29/5b85f91e8a9e4.png)

[![docker23.png](https://i.loli.net/2018/08/29/5b85f91e88ea1.png)](https://i.loli.net/2018/08/29/5b85f91e88ea1.png)

### 部署Tomcat镜像 ###
查看本机的ip
[![docker8.png](https://i.loli.net/2018/08/29/5b85f90c28afb.png)](https://i.loli.net/2018/08/29/5b85f90c28afb.png)

#### 下载 ####
从镜像中心下载tomcat
[![docker9.png](https://i.loli.net/2018/08/29/5b85f90c27237.png)](https://i.loli.net/2018/08/29/5b85f90c27237.png)

[![docker10.png](https://i.loli.net/2018/08/29/5b85f90c159bd.png)](https://i.loli.net/2018/08/29/5b85f90c159bd.png)

查看镜像中配置的tomcat目录
[![docker11.png](https://i.loli.net/2018/08/29/5b85f91587f8f.png)](https://i.loli.net/2018/08/29/5b85f91587f8f.png)

查看当前已经下载的镜像

    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                     TAG                 IMAGE ID            CREATED             SIZE
    hub.c.163.com/library/tomcat   latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql    latest              9e64176cd8a2        14 months ago       407MB

编写Dockerfile文件将工程移到tomcat的webapps目录下

    from hub.c.163.com/library/tomcat
    
    MAINTAINER fjy8018 fjy8018@gmail.com
    
    COPY /OrderBooks /usr/local/tomcat/webapps/OrderBooks

[![docker14.png](https://i.loli.net/2018/08/29/5b85f91568e5e.png)](https://i.loli.net/2018/08/29/5b85f91568e5e.png)

修改工程中的数据库地址，地址为ip+暴露的docker端口
[![docker15.png](https://i.loli.net/2018/08/29/5b85f9156e16d.png)](https://i.loli.net/2018/08/29/5b85f9156e16d.png)

[![docker16.png](https://i.loli.net/2018/08/29/5b85f915717ec.png)](https://i.loli.net/2018/08/29/5b85f915717ec.png)

使用`docker build -t orderbook .`命令将docker打包成镜像
[![docker13.png](https://i.loli.net/2018/08/29/5b85f9156a807.png)](https://i.loli.net/2018/08/29/5b85f9156a807.png)

#### 启动 ####
使用命令启动带工程的tomcat，指定访问端口为8888

    docker run -d -p 8888:8080 orderbook:latest

[![docker24.png](https://i.loli.net/2018/08/29/5b85f91e8c2dc.png)](https://i.loli.net/2018/08/29/5b85f91e8c2dc.png)

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
[![docker25.png](https://i.loli.net/2018/08/29/5b85f91e8db65.png)](https://i.loli.net/2018/08/29/5b85f91e8db65.png)

工程正常访问
[![docker26.png](https://i.loli.net/2018/08/29/5b85f91e90b4e.png)](https://i.loli.net/2018/08/29/5b85f91e90b4e.png)

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
[![docker27.png](https://i.loli.net/2018/08/29/5b85f91e92344.png)](https://i.loli.net/2018/08/29/5b85f91e92344.png)

登录到网易镜像仓库查看，默认推送会设置为private，推送完成
[![docker28.png](https://i.loli.net/2018/08/29/5b85f91e8f137.png)](https://i.loli.net/2018/08/29/5b85f91e8f137.png)


  [3]: https://c.163yun.com/hub#/m/home/
  [4]: https://hub.docker.com/
  [27]: https://www.163yun.com/help/documents/15587826830438400
