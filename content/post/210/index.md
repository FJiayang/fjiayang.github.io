{
  "title": "使用GitHub和DockerHub自动构建镜像",
  "date": "2019-07-31T22:36:41+08:00",
  "lastmod": "2019-07-31T22:36:41+08:00",
  "typecho_cid": 210,
  "url": "/archives/210/",
  "comments": false,
  "draft": false,
  "slug": "210",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "docker",
    "CICD",
    "GitHub"
  ],
  "math": false
}

## 环境

`DockerHub`账号、`GitHub`账号

## 步骤

### 构建脚本

此处以构建`mycat`的`docker`镜像为例，在本地准备好可以运行的构建脚本`Dockerfile`，尽可能不使用准备好的配置文件，保证镜像的安全、纯净，并且利用环境变量配置精简构建脚本

```dockerfile
FROM openjdk:8-jre
MAINTAINER fjy8018 fjy8018@gmail.com

# Mycat 版本
ENV MYCAT_VERSION 1.6-RELEASE
ENV MYCAT_PKG Mycat-server-1.6-RELEASE-20161028204710-linux.tar.gz

WORKDIR /usr/local

# 缓存层
RUN wget http://dl.mycat.io/$MYCAT_VERSION/$MYCAT_PKG
RUN apt-get update && \
    apt-get install -y procps && \
    apt-get clean && \
    tar -zxf /usr/local/$MYCAT_PKG && \
    rm -rf /usr/local/$MYCAT_PKG

VOLUME /usr/local/mycat/conf

EXPOSE 8066 9066

ENTRYPOINT /usr/local/mycat/bin/mycat console
```



### 创建GitHub仓库

在`GitHub`上创建对应的仓库，并推送`Dockerfile`

![1564572008865.png](/images/recovered/6390fa3989548d96de64.png)



### 链接DockerHub与GitHub

登陆`DockerHub`选择`repository`新建仓库

![1564572101153.png](/images/recovered/e008bec8c75cb0bac738.png)


首次链接可以参照[指引](https://docs.docker.com/docker-hub/builds/link-source/)操作，主要是做`OAuth `授权

![1564572489753.png](/images/recovered/a2b92162be7cd65bae45.png)



### 创建构建分支和标签

连接`GitHub`后可以选择需要构建的仓库，同时展开构建选项，可以指定不同分支构建出的标签，默认`master`分支构建为`latest`版本

![1564580799275.png](/images/recovered/d729c0ff376b8fb94466.png)

### 触发构建

第一次会自动触发构建，随后代码推送都会触发构建

![1564572890867.png](/images/recovered/43195a15c659a8ad29bb.png)



### 构建结果

在管理页面可以查看构建时长和构建结果

![1564573686044.png](/images/recovered/ebde8d898cf020b8b007.png)



## 结果

### 用户视角

用户视角可以看到构建的GitHub仓库

![1564583383061.png](/images/recovered/910642fa1b428c2ae701.png)

自动构建产生的分支

![1564583424202.png](/images/recovered/40947f6a874ad607c27b.png)

构建历史记录

![1564583451660.png](/images/recovered/a945c16c9cc176e3c2c7.png)
