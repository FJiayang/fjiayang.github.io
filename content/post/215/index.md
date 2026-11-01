{
  "title": "基于Mesos+Marathon的DevOps分布式环境搭建",
  "date": "2019-08-18T22:01:00+08:00",
  "lastmod": "2020-12-26T12:40:56+08:00",
  "typecho_cid": 215,
  "url": "/archives/215/",
  "comments": false,
  "draft": false,
  "slug": "215",
  "categories": [
    "服务器",
    "学习"
  ],
  "tags": [
    "docker",
    "mesos",
    "DevOps",
    "marathon",
    "vmware",
    "zookeeper"
  ],
  "math": false
}

## 基础环境

本地准备了4台虚拟机配置如下

| 虚拟机名称 | IP              | CPU  | 内存 | 磁盘 |
| ---------- | --------------- | ---- | ---- | ---- |
| 129        | 192.168.133.129 | 1    | 2G   | 20G  |
| 130        | 192.168.133.130 | 1    | 2G   | 20G  |
| 131        | 192.168.133.131 | 1    | 2G   | 20G  |
| 132        | 192.168.133.132 | 1    | 2G   | 20G  |



## 部署架构

部署架构图如下

![devops](/images/recovered/48c5dd8a7195d0d6b35e.png)

各服务详细部署情况

### Zookeeper

| 服务器 | 节点        | 端口 | 版本   |
| ------ | ----------- | ---- | ------ |
| 129    | zk-1-docker | 2181 | 3.4.14 |
| 131    | zk-2-docker | 2181 | 3.4.14 |
| 132    | zk-3-docker | 2181 | 3.4.14 |


### MesosMaster

| 服务器 | 节点   | 端口 | 版本  |
| ------ | ------ | ---- | ----- |
| 132    | master | 5050 | 1.7.0 |
| 130    | master | 5050 | 1.7.0 |
| 131    | master | 5050 | 1.7.0 |

### MesosSlave

| 服务器 | 节点   | 端口 | 版本  |
| ------ | ------ | ---- | ----- |
| 131    | slave2 | 5051 | 1.7.0 |
| 130    | slave1 | 5051 | 1.7.0 |


### marathon

| 服务器 | 服务           | 端口 | 版本     |
| ------ | -------------- | ---- | -------- |
| 132    | marathonMaster | 8080 | v1.6.496 |

### marathon-lb

| 服务器 | 服务        | 端口 | 版本    |
| ------ | ----------- | ---- | ------- |
| 129    | marathon-lb | 9090 | v1.14.0 |



## 环境准备

### 开放防火墙

本次服务各主机将可能使用到以下端口

- 8080
- 9090
- 2181
- 2888
- 3888
- 5050
- 5051



逐台登陆服务器执行放行防火墙脚本

```bash
firewall-cmd --zone=public --add-port=8080/tcp --permanent
firewall-cmd --zone=public --add-port=2181/tcp --permanent
firewall-cmd --zone=public --add-port=5050/tcp --permanent
firewall-cmd --zone=public --add-port=5051/tcp --permanent
firewall-cmd --zone=public --add-port=9090/tcp --permanent
firewall-cmd --zone=public --add-port=2888/tcp --permanent
firewall-cmd --zone=public --add-port=3888/tcp --permanent
firewall-cmd --reload
```



### 安装Docker

本次所有服务均采用Docker方式部署，服务调度通过`Docker in Docker`的方式进行

由于Docker有可能出现版本影响环境问题，参考文章
[相关文章](/archives/208/)

故建议安装时指定版本

```bash
$ yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
$ yum install docker-ce-19.03.1 docker-ce-cli-19.03.1 containerd.io
```



设置开机启动并运行服务

```bash
$ systemctl enable docker
$ systemctl start docker
```



安装docker-compose，脚本参考[官方文档](https://docs.docker.com/compose/install/)

```bash
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```



## 安装Zookeeper

鉴于zk `3.4`和`3.5`版本的配置有一定差别，编写脚本时注意版本，此处使用的是`3.4.14`，以下配置文件注意`hosts`的微小差别

`docker-compose-zoo-129.yml`

```yaml
version: '3.1'

services:
  zoo1:
    image: zookeeper:3.4.14
    restart: always
    network_mode: host
    extra_hosts:
      - "zoo2: 192.168.133.131"
      - "zoo3: 192.168.133.132"
    ports:
      - 2181:2181
      - 2888:2888
      - 3888:3888
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=0.0.0.0:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
```



`docker-compose-zoo-131.yml`

```yaml
version: '3.1'

services:

  zoo2:
    image: zookeeper:3.4.14
    restart: always
    network_mode: host
    extra_hosts:
      - "zoo1: 192.168.133.129"
      - "zoo3: 192.168.133.132"
    ports:
      - 2181:2181
      - 2888:2888
      - 3888:3888
    environment:
      ZOO_MY_ID: 2
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=0.0.0.0:2888:3888 server.3=zoo3:2888:3888
```



`docker-compose-zoo-132.yml`

```yaml
version: '3.1'

services:

  zoo3:
    image: zookeeper:3.4.14
    restart: always
    network_mode: host
    extra_hosts:
      - "zoo1: 192.168.133.129"
      - "zoo2: 192.168.133.131"
    ports:
      - 2181:2181
      - 2888:2888
      - 3888:3888
    environment:
      ZOO_MY_ID: 3
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=0.0.0.0:2888:3888
```



## 安装MesosMaster

MesosMaster也采用3节点高可用方案，由于要在各台机器上配置hosts过于麻烦，此处选择使用非hosts注册方式，故需要配置**各自**的`IP`地址



`docker-compose-mesos-master-130.yml`

```yaml
version: '3.1'

services:

  mesos-master:
    image: mesosphere/mesos-master:1.7.0
    restart: always
    network_mode: host
    hostname: master
    command: --no-hostname_lookup --ip=192.168.133.130
    ports:
      - 5050:5050
    environment:
      MESOS_PORT: 5050
      MESOS_ZK: zk://192.168.133.129:2181/mesos
      MESOS_QUORUM: 1
      MESOS_REGISTRY: in_memory
      MESOS_LOG_DIR: /var/log/mesos
      MESOS_WORK_DIR: /var/tmp/mesos
```



`docker-compose-mesos-master-131.yml`

```yaml
version: '3.1'

services:

  mesos-master:
    image: mesosphere/mesos-master:1.7.0
    restart: always
    network_mode: host
    hostname: master
    command: --no-hostname_lookup --ip=192.168.133.131
    ports:
      - 5050:5050
    environment:
      MESOS_PORT: 5050
      MESOS_ZK: zk://192.168.133.129:2181/mesos
      MESOS_QUORUM: 1
      MESOS_REGISTRY: in_memory
      MESOS_LOG_DIR: /var/log/mesos
      MESOS_WORK_DIR: /var/tmp/mesos
```



`docker-compose-mesos-master-132.yml`

```yaml
version: '3.1'

services:

  mesos-master:
    image: mesosphere/mesos-master:1.7.0
    restart: always
    network_mode: host
    hostname: master
    command: --no-hostname_lookup --ip=192.168.133.132
    ports:
      - 5050:5050
    environment:
      MESOS_PORT: 5050
      MESOS_ZK: zk://192.168.133.129:2181/mesos
      MESOS_QUORUM: 1
      MESOS_REGISTRY: in_memory
      MESOS_LOG_DIR: /var/log/mesos
      MESOS_WORK_DIR: /var/tmp/mesos
```



## 安装MesosSlave

需要选择与master对应的版本号，同时也使用`IP`注册的方式

`docker-compose-mesos-slave1.yml`

```yaml
version: '3.1'

services:

  mesos-slave1:
    image: mesosphere/mesos-slave:1.7.0
    restart: always
    network_mode: host
    hostname: slave1
    command: --no-systemd_enable_support --no-hostname_lookup --ip=192.168.133.131
    ports:
      - 5051:5051
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /cgroup:/cgroup
      - /sys:/sys
      - /usr/bin/docker:/usr/local/bin/docker
    environment:
      MESOS_PORT: 5051
      MESOS_MASTER: zk://192.168.133.129:2181/mesos
      MESOS_SWITCH_USER: 0
      MESOS_CONTAINERIZERS: docker,mesos
      MESOS_LOG_DIR: /var/log/mesos
      MESOS_WORK_DIR: /var/tmp/mesos
    privileged: true
```



`docker-compose-mesos-slave2.yml`

```yaml
version: '3.1'

services:

  mesos-slave2:
    image: mesosphere/mesos-slave:1.7.0
    restart: always
    network_mode: host
    hostname: slave2
    command: --no-systemd_enable_support --no-hostname_lookup --ip=192.168.133.130
    ports:
      - 5051:5051
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /cgroup:/cgroup
      - /sys:/sys
      - /usr/bin/docker:/usr/local/bin/docker
    environment:
      MESOS_PORT: 5051
      MESOS_MASTER: zk://192.168.133.129:2181/mesos
      MESOS_SWITCH_USER: 0
      MESOS_CONTAINERIZERS: docker,mesos
      MESOS_LOG_DIR: /var/log/mesos
      MESOS_WORK_DIR: /var/tmp/mesos
    privileged: true
```



## Marathon

`marathon`在高版本会出现收不到`mesos`心跳自动停止的问题，暂时没找到可以配置的方式，故使用`1.6`的版本，问题链接如下

[Missing heartbeats from Mesos, eventually disconnecting and dying](https://jira.mesosphere.com/browse/MARATHON-8345)



`docker-compose-marathon.yml`

```yaml
version: '3.1'

services:

  marathon:
    image: mesosphere/marathon:v1.6.496
    hostname: marathon
    restart: always
    command: --master zk://192.168.133.129:2181/mesos --zk zk://192.168.133.129:2181/marathon
    ports:
      - 8080:8080
```



## 安装marathon-lb

marathon-lb 与marathon没有版本的对应关系，故使用当前最新的版本`1.14`，新版和旧版的配置也有所不同，在早期版本无需指定端口的环境变量，翻阅官网也指出其应该是自动配置的，但如果使用Docker默认运行脚本则需要手动指定

> if you use the built-in `run` script, you'll need to pass an env var that contains a comma separated list of the ports HAProxy binds to

参考ISSUES：

[unbound variable PORTS v1.1.0](https://github.com/mesosphere/marathon-lb/issues/59)



`docker-compose-marathon-lb.yml`

```yaml
version: '3.1'

services:

  marathon-lb:
    image: mesosphere/marathon-lb:v1.14.0
    network_mode: host
    hostname: marathon-lb
    restart: always
    command: sse --group external --marathon http://192.168.133.132:8080
    environment:
      PORTS: 9090
    ports:
      - 9090:9090
```



## 启动

启动顺序：

1. zookeeper
2. mesosMaster
3. mesosSlave
4. marathon
5. marathon-lb



由于全使用docker-compose脚本编写，启动时只需指定文件名即可

```bash
$ docker-compose -f xx.yml up -d
```



查看日志命令，`-f`表示跟踪最新的日志

```bash
$ docker-compose -f xx.yml logs [-f]
```



## 效果

随便打开一个节点的mesos端口，可看到当前的服务注册数量和当前的leader，其采用与ZK类似的选举算法来选出leader实现高可用

![](/images/recovered/af93ef3a9425fb7b1a8d.png)

slave信息

![](/images/recovered/f6365d398811895a5f8a.png)

查看框架注册情况

![1566124680011](/images/recovered/33cfdb5b32513dbd2f58.png)

查看marathon-lb情况

![1566124772689](/images/recovered/ac51f1dd372df50e4997.png)



marathon面板

![1566123387054](/images/recovered/c2c64b042e74eee05118.png)

marathon支持通过面板创建任务和通过rest接口创建任务

使用postman创建任务测试

请求路径http://192.168.133.132:8080/v2/apps

内容

```json
{
    "id": "basic-0", 
    "cmd": "while [ true ] ; do echo 'Hello Marathon' ; sleep 5 ; done",
    "cpus": 0.1,
    "mem": 10.0,
    "instances": 1
}
```

结果

![1566123482678](/images/recovered/127e90173afc61b24409.png)

面板同步显示

![1566123506660](/images/recovered/812987a98f9ad01a5aa3.png)

运行状态正常

![1566124822675](/images/recovered/f5a60de93f4ee97df72c.png)

查看详情可知其运行在130服务器上

![1566124853340](/images/recovered/50d8f32a87e387e3ed28.png)

通过面板创建

![1566124949525](/images/recovered/a99be09d68c4564e44ce.png)

切换为json格式可以编辑更多内容

```json
{
  "id": "demo-springboot",
  "cmd": null,
  "cpus": 0.3,
  "mem": 128,
  "disk": 0,
  "instances": 1,
  "container": {
    "docker": {
      "image": "fjy8018/demo-springboot:2.1.6.RELEASE",
      "forcePullImage": true
    },
    "type": "DOCKER",
    "portMappings": [
      {
        "containerPort": 8080,
        "protocol": "tcp",
        "servicePort": 18080
      }
    ]
  },
  "networks": [
    {
      "mode": "container/bridge"
    }
  ]
}
```



![1566125064780](/images/recovered/bdb23559f4d9e1b92e1f.png)



运行成功

![1566125104507](/images/recovered/04b2a8385b9bee3d238e.png)

访问成功

![1566125318702](/images/recovered/c2aed763f366925bf376.png)

查看资源调度情况

![1566125350396](/images/recovered/3011a935da57faf94452.png)



![1566125370134](/images/recovered/1625e8af5a5c4bdc12e3.png)

配置扩缩容

![1566125437096](/images/recovered/def5290923cd27138be3.png)

配置成功

![1566125461566](/images/recovered/78e5b237a952b1efac3c.png)



两个实例被分别调度到不同的机器上

![1566125537165](/images/recovered/094837ffb3a048251ee6.png)



![1566125544430](/images/recovered/c454d4fe5bd3682017e7.png)



配置健康检查

![1566125749835](/images/recovered/4188df80226c1e0ec54a.png)

自动轮询接口

![1566125738241](/images/recovered/543fe8e14971c46d14ff.png)



错误告警

![1566125926856](/images/recovered/6c2ff8976a530414e94a.png)
