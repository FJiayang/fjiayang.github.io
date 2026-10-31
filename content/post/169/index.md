{
  "title": "Docker部署中遇到的坑",
  "date": "2018-07-05T14:21:00+08:00",
  "lastmod": "2018-08-31T21:54:22+08:00",
  "typecho_cid": 169,
  "url": "/archives/169/",
  "comments": false,
  "draft": false,
  "slug": "169",
  "categories": [
    "开发"
  ],
  "tags": [
    "docker"
  ],
  "math": false
}

## 镜像无法删除 ##
### 问题复现 ###
当前的镜像

    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                               TAG                 IMAGE ID            CREATED             SIZE
    orderbook                                latest              6514a4df3367        7 seconds ago       300MB
    hub.c.163.com/fjy8018/mysql-orderbooks   latest              37a82bac5f71        About an hour ago   407MB
    hub.c.163.com/library/tomcat             latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql              latest              9e64176cd8a2        14 months ago       407MB
    
运行一个镜像

    PS D:\JAVA WORKSPACE\dockerTemp> docker run -d -p 8888:8080 orderbook:latest
    678dcf28c1c3206cd78a824aab51cc5d1f6c333ed85f48d4c364a51526049f20
    
查看进程，发现进程没有出现（3306是已经启动的MySQL容器），由于容器制作过程出现问题导致进程无法成功启动
    
    PS D:\JAVA WORKSPACE\dockerTemp> docker ps
    CONTAINER ID        IMAGE                                COMMAND                  CREATED             STATUS              PORTS                    NAMES
    43146ddfc771        hub.c.163.com/library/mysql:latest   "docker-entrypoint.s…"   2 hours ago         Up 2 hours          0.0.0.0:8006->3306/tcp   hopeful_euclid

检查镜像
    
    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                               TAG                 IMAGE ID            CREATED             SIZE
    orderbook                                latest              6514a4df3367        44 seconds ago      300MB
    hub.c.163.com/fjy8018/mysql-orderbooks   latest              37a82bac5f71        About an hour ago   407MB
    hub.c.163.com/library/tomcat             latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql              latest              9e64176cd8a2        14 months ago       407MB

删除没有成功运行的镜像报错，报该容器已经被占用 
    
    PS D:\JAVA WORKSPACE\dockerTemp> docker rmi 6514a4df3367
    Error response from daemon: conflict: unable to delete 6514a4df3367 (must be forced) - image is being used by stopped container 678dcf28c1c3
    
删除报错中提示的容器ID
    
    PS D:\JAVA WORKSPACE\dockerTemp> docker rmi 678dcf28c1c3
    Error: No such image: 678dcf28c1c3
    
报无该镜像

    
### 解决 ### 
官方对rm与rmi的解释：
    rm        Remove one or more containers
    rmi       Remove one or more images
可知rm删除的是容器，rmi删除的是镜像，两者的区别如下：

> 容器（container）的定义和镜像（image）几乎一模一样，也是一堆层的统一视角，唯一区别在于容器的最上面那一层是可读可写的。
> 镜像（Image）就是一堆只读层（read-only layer）的统一视角
> 要点：容器 = 镜像 + 可读层。并且容器的定义并没有提及是否要运行容器。

故对于不在镜像列表的ID，要删除的是容器，使用`rm`命令
    PS D:\JAVA WORKSPACE\dockerTemp> docker rm 678dcf28c1c3
    678dcf28c1c3

列出所有的镜像

    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                               TAG                 IMAGE ID            CREATED             SIZE
    orderbook                                latest              6514a4df3367        2 minutes ago       300MB
    hub.c.163.com/fjy8018/mysql-orderbooks   latest              37a82bac5f71        About an hour ago   407MB
    hub.c.163.com/library/tomcat             latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql              latest              9e64176cd8a2        14 months ago       407MB
    
再删除目标镜像
    PS D:\JAVA WORKSPACE\dockerTemp> docker rmi 6514a4df3367
    Untagged: orderbook:latest
    Deleted: sha256:6514a4df33678bd98e32b5738150c88c5d72b9a3a4d86d1c370406f0f7f18788
    Deleted: sha256:68a70a0ac20590c8412286b3c34ab2bc5c5b7c8845088536f03702185ac34105
    Deleted: sha256:bf15e37a31e4266bc8a962a2b11fc3223c07de328ff85b17c70a15653c71061b
    Deleted: sha256:b447a606517609703f1efe4c560c42b9aeeaee669d22f12a65d2d2929d8ecc20
    
删除成功    
    PS D:\JAVA WORKSPACE\dockerTemp> docker images
    REPOSITORY                               TAG                 IMAGE ID            CREATED             SIZE
    hub.c.163.com/fjy8018/mysql-orderbooks   latest              37a82bac5f71        About an hour ago   407MB
    hub.c.163.com/library/tomcat             latest              72d2be374029        10 months ago       292MB
    hub.c.163.com/library/mysql              latest              9e64176cd8a2        14 months ago       407MB
## 停止并删除所有容器 ##
批处理命令
```
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
```
