{
  "title": "RocketMQ学习笔记1——初探",
  "date": "2020-12-23T19:04:00+08:00",
  "lastmod": "2023-09-07T15:06:32+08:00",
  "typecho_cid": 251,
  "url": "/archives/251/",
  "comments": false,
  "draft": false,
  "slug": "251",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "Linux",
    "源码学习",
    "RocketMQ"
  ],
  "math": true
}

## RocketMQ整体认知

优势

- 支持集群模型、负载均衡、水平扩展能力    
- 亿级别的消息堆积能力    
- 采用零拷贝的原理、顺序写盘、随机读
- 丰富的API使用
- 代码优秀，底层通信框架采用Netty NIO框架
- NameServer代替Zookeeper
- 强调集群无单点，可扩展，任意一点高可用，水平可扩展
- 消息失败重试机制，消息可查询
- 开源社区活跃，成熟度高（经过双十一考验）



## 核心概念模型

### 基本概念

- 消息生产者（Producer）： 负责生产消息，一般由业务系统负责生产消息。 
- 消息消费者（Consumer）： 负责消费消息，一般是后台系统负责异步消费。 
- 推动式消费（Push Consumer）： Consumer消费的一种类型，该模式下Broker收到数据后会主动推送给消费端。 
- 拉取式消费（Pull Consumer）： Consumer消费的一种类型，应用通常主动调用Consumer的拉消息方法从Broker服务器拉消息。
- 生产者组（Producer Group）： 同一类Producer的集合，这类Producer发送同一类消息且发送逻辑一致。 
- 消费者组（Consumer Group）： 同一类Consumer的集合，这类Consumer通常消费同一类消息且消费逻辑一致。 
- Broker：MQ消息服务（中转角色，用于消息存储于生产消息转发）

## 源码结构

源码分析以4.4.0为例

源码地址： https://github.com/apache/rocketmq 

结构：

![image-20200709155308594](/images/recovered/3995ca35bf98137a9bf3.png)

结构解析：

- rocketmq-common：公用数据结构
- rocketmq-distribution：编译模块，编译输出
- rocketmq-filter：进行Broker过滤的不感兴趣的消息传输，减小带宽压力
- rocketmq-logappender、rocketmq-logging：日志服务
- rocketmq-namesrv：Namesrv服务，用于服务协调
- rocketmq-openmessaging：对外提供服务
- rocketmq-remoting：远程调用接口，封装Netty底层通信
- rocketmq-srvutil：提供一些公用的工具方法，比如命令行解析参数
- rocketmq-store：消息存储
- rocketmq-test、rocketmq-example
- rocketmq-tools：管理工具，比如有名的mqadmin工具

## 编译部署&环境搭建

选择1台服务器进行部署验证

| IP               | IP           |
| ---------------- | ------------ |
| GY11-SyOCM33-101 | 10.139.12.52 |



### 编译部署

在源码目录执行一下命令编译工程

```bash
$ mvn -Prelease-all -DskipTests clean package
```



编译成功后在`rocketmq\distribution\target`目录下生成`apache-rocketmq.tar.gz`包，使用该包解压与从官网下载一致，其他步骤参考二进制部署。



### 二进制包部署（单点）

此处从官网下载4.4.0版本并上传至服务器解压

[下载地址](http://rocketmq.apache.org/dowloading/releases/)

解压到`~/rocketmq-test/rocketmq-all-4.4.0-bin-release/`如下

```bash
$ ll
total 36
drwxr-xr-x 2 ocmuser gpocm    83 Jan 17  2019 benchmark
drwxr-xr-x 2 ocmuser gpocm  4096 Jan 17  2019 bin
drwxr-xr-x 5 ocmuser gpocm   196 Jan 17  2019 conf
drwxr-xr-x 2 ocmuser gpocm  4096 Jan 17  2019 lib
-rw-r--r-- 1 ocmuser gpocm 17336 Jan 17  2019 LICENSE
-rw-r--r-- 1 ocmuser gpocm  1337 Jan 17  2019 NOTICE
-rw-r--r-- 1 ocmuser gpocm  2481 Jan 17  2019 README.md
```



#### 创建存储目录

```bash
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store 
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/commitlog 
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/consumequeue 
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/index
```



#### RocketMQ 配置文件

进入提供好的样例配置文件目录，其中包含双主双从异步复制、双主双从同步复制和双主集群配置文件，此处选择双主双从异步复制作为配置模板

```bash
[ocmuser@GY11-SyOCM33-101 ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/conf]$ll
total 36
drwxr-xr-x 2 ocmuser gpocm   118 Jan 17  2019 2m-2s-async
drwxr-xr-x 2 ocmuser gpocm   118 Jan 17  2019 2m-2s-sync
drwxr-xr-x 2 ocmuser gpocm    91 Jan 17  2019 2m-noslave
-rw-r--r-- 1 ocmuser gpocm   949 Jan 17  2019 broker.conf
-rw-r--r-- 1 ocmuser gpocm 14978 Jan 17  2019 logback_broker.xml
-rw-r--r-- 1 ocmuser gpocm  3836 Jan 17  2019 logback_namesrv.xml
-rw-r--r-- 1 ocmuser gpocm  3761 Jan 17  2019 logback_tools.xml
-rw-r--r-- 1 ocmuser gpocm  1277 Jan 17  2019 plain_acl.yml
-rw-r--r-- 1 ocmuser gpocm   833 Jan 17  2019 tools.yml
```

选择`broker-a`配置文件

```bash
[ocmuser@GY11-SyOCM33-101 ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/conf/2m-2s-async]$ll
total 16
-rw-r--r-- 1 ocmuser gpocm 929 Jan 17  2019 broker-a.properties
-rw-r--r-- 1 ocmuser gpocm 922 Jan 17  2019 broker-a-s.properties
-rw-r--r-- 1 ocmuser gpocm 929 Jan 17  2019 broker-b.properties
-rw-r--r-- 1 ocmuser gpocm 922 Jan 17  2019 broker-b-s.properties
```

删除原有配置，加入如下配置（单点）

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样
brokerName=broker-a
#0 表示 Master，>0 表示 Slave
brokerId=0
#nameServer 地址，分号分割
namesrvAddr=10.139.12.52:9876
#在发送消息时，自动创建服务器不存在的 topic，默认创建的队列数
defaultTopicQueueNums=4
#是否允许 Broker 自动创建 Topic，建议线下开启，线上关闭
autoCreateTopicEnable=true
#是否允许 Broker 自动创建订阅组，建议线下开启，线上关闭
autoCreateSubscriptionGroup=true
#Broker 对外服务的监听端口
listenPort=10911
#删除文件时间点，默认凌晨 4 点
deleteWhen=04
#文件保留时间，默认 48 小时
fileReservedTime=120
#commitLog 每个文件的大小默认 1G
mapedFileSizeCommitLog=1073741824
#ConsumeQueue 每个文件默认存 30W 条，根据业务情况调整
mapedFileSizeConsumeQueue=300000
#destroyMapedFileIntervalForcibly=120000
#redeleteHangedFileInterval=120000
#检测物理文件磁盘空间
diskMaxUsedSpaceRatio=88
#存储路径
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/abort
#限制的消息大小
maxMessageSize=65536

#flushCommitLogLeastPages=4
#flushConsumeQueueLeastPages=2
#flushCommitLogThoroughInterval=10000
#flushConsumeQueueThoroughInterval=60000

#Broker 的角色
#- ASYNC_MASTER 异步复制 Master
#- SYNC_MASTER 同步双写 Master
#- SLAVE
brokerRole=ASYNC_MASTER

#刷盘方式
#- ASYNC_FLUSH 异步刷盘
#- SYNC_FLUSH 同步刷盘
flushDiskType=ASYNC_FLUSH

#checkTransactionMessageEnable=false
#发消息线程池数量
#sendMessageThreadPoolNums=128
#拉消息线程池数量
#pullMessageThreadPoolNums=128
```



#### 修改日志配置文件

执行命令替换默认日志目录为指定日志目录

```bash
$ mkdir -p /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/logs 
$ cd /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/conf && sed -i 's#${user.home}#/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release#g' *.xml 
```



#### 修改启动脚本参数

将默认8g的内存配置改成1g

```bash
$ vim /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin/runbroker.sh
```

`runbroker.sh`

```sh
#===========================================================================================
# JVM Configuration
#===========================================================================================
JAVA_OPT="${JAVA_OPT} -server -Xms1g -Xmx1g -Xmn512m -XX:PermSize=128m -XX:MaxPermSize=320m"
...
```

同理

```bash
$ vim /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin/runserver.sh
```

`runserver.sh `

```sh
#===========================================================================================
# JVM Configuration
#===========================================================================================
JAVA_OPT="${JAVA_OPT} -server -Xms1g -Xmx1g -Xmn512m -XX:PermSize=128m -XX:MaxPermSize=320m"
...
```



#### 启动 NameServer

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin 
$ nohup sh mqnamesrv &
```

检查进程

```bash
[ocmuser@GY11-SyOCM33-101 ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin]$jps
65322 NamesrvStartup
65534 Jps
```



#### 启动 BrokerServer A

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin 
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/conf/2m-2s-async/broker-a.properties >/dev/null 2>&1 & 
```



```bash
$ netstat -ntlp 
$ jps 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/logs/rocketmqlogs/broker.log 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/logs/rocketmqlogs/namesrv.log
```



![image-20200710094505851](/images/recovered/b87bf7f911a2b7d1f5ba.png)

![image-20200710094538126](/images/recovered/0d7fa72b29c552ff1400.png)



#### 停止与数据清理

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin 
$ sh mqshutdown broker 
$ sh mqshutdown namesrv 
# --等待停止 
$ rm -rf /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store 
$ mkdir /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store 
$ mkdir /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/commitlog 
$ mkdir /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/consumequeue 
$ mkdir /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/index 
# --按照上面步骤重启 NameServer 与 BrokerServer 
```



## SpringBoot 控制台讲解

克隆工程：https://github.com/apache/rocketmq-externals.git

进入控制台配置文件`rocketmq-externals\rocketmq-console\src\main\resources\application.properties`修改配置

```properties
server.contextPath=
server.port=9090

## SSL setting
#server.ssl.key-store=classpath:rmqcngkeystore.jks
#server.ssl.key-store-password=rocketmq
#server.ssl.keyStoreType=PKCS12
#server.ssl.keyAlias=rmqcngkey

#spring.application.index=true
spring.application.name=rocketmq-console
spring.http.encoding.charset=UTF-8
spring.http.encoding.enabled=true
spring.http.encoding.force=true
logging.config=classpath:logback.xml
#if this value is empty,use env value rocketmq.config.namesrvAddr  NAMESRV_ADDR | now, you can set it in ops page.default localhost:9876
rocketmq.config.namesrvAddr=10.139.12.52:9876
#if you use rocketmq version < 3.5.8, rocketmq.config.isVIPChannel should be false.default true
rocketmq.config.isVIPChannel=
#rocketmq-console's data path:dashboard/monitor
rocketmq.config.dataPath=./data
#set it false if you don't want use dashboard.default true
rocketmq.config.enableDashBoardCollect=true
#set the message track trace topic if you don't want use the default one
