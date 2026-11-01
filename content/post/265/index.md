{
  "title": "GitHub DevOps工作流构建Java项目并上传到DockerHub",
  "date": "2021-02-07T11:58:43+08:00",
  "lastmod": "2021-02-07T11:58:43+08:00",
  "typecho_cid": 265,
  "url": "/archives/265/",
  "comments": false,
  "draft": false,
  "slug": "265",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "docker",
    "CICD",
    "DevOps",
    "GitHub",
    "Sentinel"
  ],
  "math": false
}

## 工程准备

此处使用fork自`alibaba/Sentinel`的`FJiayang/Sentinel`项目实践

工程地址

[Sentinel](https://github.com/FJiayang/Sentinel) — Sentinel仓库源码



## 准备Dockerfile

该工程为标准Java项目，故准备好的`Dockerfile`文件如下

```dockerfile
FROM anapsix/alpine-java:8_server-jre_unlimited

MAINTAINER fjy8018@gmail.com

ENV PARAM ""
ENV VERSION 1.8.0

RUN mkdir -p /sentinel

WORKDIR /sentinel

ADD ./sentinel-dashboard/target/sentinel-dashboard.jar ./app-${VERSION}.jar

# 设置时区，默认为UTC
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone

ENTRYPOINT ["java", "${PARAM}", "-jar", "app-${VERSION}.jar"]
```



## 编写GitHub工作流

GitHub DevOps工作流又叫GitHub Actions 是2019年末推出的自动化CICD持续集成工作流，有详细的样例文档

此处参考以下文档编写

[使用 Maven 构建和测试 Java](https://docs.github.com/cn/actions/guides/building-and-testing-java-with-maven) — GitHub Actions  指南

### 安全配置

由于需要建构建后的制品推送到DockerHub中，但又不能在工作流中直接使用用户名和密码登陆，故还需要配置环境变量

在DockerHub中新增秘钥

![1612612278354](/images/recovered/33766ffbac339a643bd2.png)

在构建工程的设置中新增用户名和密码变量

![1612612340227](/images/recovered/031c3219312febd8cb3a.png)



编写后的工作流如下

```yaml
name: Publish Docker image

on: [push]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - name: Set up Maven Central Repository
        uses: actions/setup-java@v1
        with:
          java-version: 1.8

      - name: Publish package
        run: mvn --batch-mode clean package -Dmaven.test.skip=true

      - name: Push to Docker Hub
        uses: docker/build-push-action@v1
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          repository: fjy8018/sentinel
          tag_with_ref: true

```



## 触发构建

当前的触发方式配置为`PUSH`，修改好文件后会自动触发流水线工作

![1612612585264](/images/recovered/df6d278c50da560c3017.png)

Maven打包，速度很快

![1612612545382](/images/recovered/89ed6a417a58fb26b780.png)

打包完成

![1612612706399](/images/recovered/b90ea2761e169aa045fe.png)

## 检查结果

登录到DockerHub中检查推送结果，可见成功推送

![1612612761551](/images/recovered/4c8392f4f79174eae42e.png)



## 总结

整体来看，GitHub工作流效率高，文档齐全，编码上手速度快，相比GitLab CICD和DockerHub CICD来说，GitHub CICD配置更加简单、友好和高效。
