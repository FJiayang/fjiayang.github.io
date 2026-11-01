{
  "title": "Sentinel持久化存储和镜像构建",
  "date": "2021-02-07T12:06:58+08:00",
  "lastmod": "2021-02-07T12:06:58+08:00",
  "typecho_cid": 266,
  "url": "/archives/266/",
  "comments": false,
  "draft": false,
  "slug": "266",
  "categories": [
    "开发"
  ],
  "tags": [
    "docker",
    "GitHub",
    "Sentinel"
  ],
  "math": false
}

## 背景

Sentinel默认只能对限流规则存储到内存中

[在生产环境中使用 Sentinel](https://github.com/alibaba/Sentinel/wiki/%E5%9C%A8%E7%94%9F%E4%BA%A7%E7%8E%AF%E5%A2%83%E4%B8%AD%E4%BD%BF%E7%94%A8-Sentinel) — Sentinel中文文档

官方文档对于数据持久化描述如下

> 我们提供了 ZooKeeper, Apollo, Nacos 等的动态数据源实现。以 ZooKeeper 为例子，如果要使用第三方的配置中心作为配置管理，您需要做下面的几件事情:
>
> 1. 实现一个公共的 ZooKeeper 客户端用于推送规则，在 Sentinel 控制台配置项中需要指定 ZooKeeper 的地址，启动时即创建 ZooKeeper Client。
> 2. 我们需要针对每个应用（appName），每种规则设置不同的 path（可随时修改）；或者约定大于配置（如 path 的模式统一为 `/sentinel_rules/{appName}/{ruleType}`，e.g. `sentinel_rules/appA/flowRule`）。
> 3. 规则配置页需要进行相应的改造，直接针对**应用维度**进行规则配置；修改同个应用多个资源的规则时可以批量进行推送，也可以分别推送。Sentinel 控制台将规则缓存在内存中（如 `InMemFlowRuleStore`），可以对其进行改造使其支持应用维度的规则缓存（key 为 appName），每次添加/修改/删除规则都先更新内存中的规则缓存，然后需要推送的时候从规则缓存中获取全量规则，然后通过上面实现的 Client 将规则推送到 ZooKeeper 即可。
> 4. 应用客户端需要注册对应的读数据源以监听变更，可以参考 [相关文档](https://github.com/alibaba/Sentinel/wiki/动态规则扩展)。

由于`alibaba/Sentinel`官方并没有实现对具体数据源的写入支持，只提供的实现的接口，故无法做到开箱即用



## 解决方法

已经有贡献者提供了对三种动态数据源的实现PR，但还没合并进主版本中

[ 添加持久化支持，可选持久化选项](https://github.com/alibaba/Sentinel/pull/1711) — Fixes Issues #1696 添加持久化支持，可选持久化选项：nacos、apollo、zookeeper ; 修改 README.md 说明文档

![1612669905332](/images/recovered/cb49475bf045ff44f19c.png)



## 进一步完善

本次基于`jiajiangnan/Sentinel`fork出自己的工程`FJiayang/Sentinel`，实现`docker`镜像打包，并基于`GitHub Actions`完成自动化构建和上传制品。

[jiajiangnan/Sentinel](https://github.com/jiajiangnan/Sentinel) — jiajiangnan的Sentinel仓库源码

[FJiayang/Sentinel](https://github.com/FJiayang/Sentinel) — FJiayang的Sentinel仓库源码



### 添加Dockerfile

基于最小jdk镜像制作

```dockerfile
FROM openjdk:8-jdk-alpine3.7

MAINTAINER fjy8018@gmail.com

ENV VERSION 1.8.0

RUN mkdir -p /sentinel

WORKDIR /sentinel

ADD ./sentinel-dashboard/target/sentinel-dashboard.jar ./app-${VERSION}.jar

# 设置时区，默认为UTC
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone

CMD java ${PARAM} -jar app-${VERSION}.jar
```

添加`GitHub`流水线配置文件

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

具体的流水线编写可参考文章

[相关文章](/archives/265/)



## 使用方法

具体参数文档

| 项                                                  | 类型    | 默认值                                            | 最小值 | 描述                                                         |
| --------------------------------------------------- | ------- | ------------------------------------------------- | ------ | ------------------------------------------------------------ |
| sentinel.dashboard.auth.username                    | String  | sentinel                                          | 无     | 登录控制台的用户名，默认为 `sentinel`                        |
| sentinel.dashboard.auth.password                    | String  | sentinel                                          | 无     | 登录控制台的密码，默认为 `sentinel`                          |
| sentinel.dashboard.app.hideAppNoMachineMillis       | Integer | 0                                                 | 60000  | 是否隐藏无健康节点的应用，距离最近一次主机心跳时间的毫秒数，默认关闭 |
| sentinel.dashboard.removeAppNoMachineMillis         | Integer | 0                                                 | 120000 | 是否自动删除无健康节点的应用，距离最近一次其下节点的心跳时间毫秒数，默认关闭 |
| sentinel.dashboard.unhealthyMachineMillis           | Integer | 60000                                             | 30000  | 主机失联判定，不可关闭                                       |
| sentinel.dashboard.autoRemoveMachineMillis          | Integer | 0                                                 | 300000 | 距离最近心跳时间超过指定时间是否自动删除失联节点，默认关闭   |
| datasource.provider                                 | String  | memory                                            | 无     | 默认为 `memory`, 可选持久化配置 `nacos`、`apollo`、`zookeeper` |
| datasource.provider.nacos.server-addr               | String  | localhost:8848                                    | 无     | nacos 注册中心地址                                           |
| datasource.provider.nacos.username                  | String  |                                                   | 无     | nacos 用户名，默认为空                                       |
| datasource.provider.nacos.password                  | String  |                                                   | 无     | nacos 密码，默认为空                                         |
| datasource.provider.nacos.namespace                 | String  |                                                   | 无     | nacos 名臣空间，默认为空                                     |
| datasource.provider.nacos.group-id                  | String  | SENTINEL_GROUP                                    | 无     | nacos 分组，默认为 `SENTINEL_GROUP`                          |
| datasource.provider.apollo.server-addr              | String  | [http://localhost:10034](http://localhost:10034/) | 无     | apollo 注册中心地址，必须有前缀 `http://` 或 `https://`      |
| datasource.provider.apollo.token                    | String  | token                                             | 无     | apollo 登录 token，默认为 `token`                            |
| datasource.provider.zookeeper.server-addr           | String  | localhost:2181                                    | 无     | zookeeper 注册中心地址                                       |
| datasource.provider.zookeeper.session-timeout       | Integer | 60000                                             | 0      | zookeeper session超时时间，默认 `60000`                      |
| datasource.provider.zookeeper.connection-timeout    | Integer | 15000                                             | 0      | zookeeper connection超时时间，默认 `15000`                   |
| datasource.provider.zookeeper.retry.max-retries     | Integer | 3                                                 | 0      | zookeeper 最大重试次数， 默认 `3`                            |
| datasource.provider.zookeeper.retry.base-sleep-time | Integer | 1000                                              | 1000   | zookeeper 重试间隔最小时长，默认 `1000`                      |
| datasource.provider.zookeeper.retry.max-sleep-time  | Integer | 2147483647                                        | 0      | zookeeper 重试间隔最大时长，默认 `2147483647`                |

对于单条Docker命令启动

```bash
$ docker run --rm -e PARAM="-Dserver.port=8858 -Dcsp.sentinel.dashboard.server=localhost:8858 -Dproject.name=sentinel-dashboard -Ddatasource.provider=nacos -Ddatasource.provider.nacos.server-addr=192.168.133.128:8848 -Ddatasource.provider.nacos.username=nacos -Ddatasource.provider.nacos.password=nacos -Ddatasource.provider.nacos.group-id=SENTINEL_GROUP" fjy8018/sentinel:1.8.0
```

对于`docker-compose`启动，此处结合`nacos`与`mysql`基础设施给出示例，mysql需要提前写入nacos相关初始化表结构

```yaml
version: '3.7'
services:

  mysql57:
    image: mysql:5.7.29
    restart: always
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    ports:
      - 3306:3306
    networks:
      - dev
    volumes:
      - ./mysql57/data:/var/lib/mysql
      - ./mysql57/custom-master.cnf:/etc/mysql/conf.d/custom.cnf
      - ./mysql57/log:/var/log/mysql
    environment:
      MYSQL_ROOT_PASSWORD: root

  nacos-standalone:
    image: nacos/nacos-server:1.1.4
    networks:
      - dev
    environment:
      - PREFER_HOST_MODE=hostname
      - MODE=standalone
      - SPRING_DATASOURCE_PLATFORM=mysql
      - MYSQL_MASTER_SERVICE_HOST=mysql57
      - MYSQL_MASTER_SERVICE_DB_NAME=nacos
      - MYSQL_MASTER_SERVICE_PORT=3306
      - MYSQL_SLAVE_SERVICE_HOST=mysql57
      - MYSQL_SLAVE_SERVICE_PORT=3306
      - MYSQL_MASTER_SERVICE_USER=root
      - MYSQL_MASTER_SERVICE_PASSWORD=root
    ports:
      - 8848:8848
    depends_on:
      - mysql57
    volumes:
      - ./standalone-logs/:/home/nacos/logs

  sentinel:
    image: fjy8018/sentinel:1.8.0
    environment:
      - PARAM=-Dserver.port=8858 -Dcsp.sentinel.dashboard.server=localhost:8858 -Dproject.name=sentinel-dashboard -Ddatasource.provider=nacos -Ddatasource.provider.nacos.server-addr=nacos-standalone:8848 -Ddatasource.provider.nacos.username=nacos -Ddatasource.provider.nacos.password=nacos -Ddatasource.provider.nacos.group-id=SENTINEL_GROUP
    networks:
      - dev
    ports:
      - 8858:8858
    restart: on-failure

networks:
  dev:
```

启动成功后可以看到`nacos`上成功注册了`sentinel-dashboard`

![1612670651663](/images/recovered/23fbc0e5e0031c2977fb.png)
