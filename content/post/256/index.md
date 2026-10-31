{
  "title": "RocketMQ学习笔记6——集群实战",
  "date": "2020-12-23T19:15:00+08:00",
  "lastmod": "2020-12-26T14:14:53+08:00",
  "typecho_cid": 256,
  "url": "/archives/256/",
  "comments": false,
  "draft": false,
  "slug": "256",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "CentOS",
    "Linux",
    "RocketMQ"
  ],
  "math": false
}

## 组建高性能MQ服务

- 双主双从模式
- 保障无单点故障问题的高可用集群



## 集群拓扑图

![1608468950654](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1608468950654.png)

| IP           | 资源         | 服务                                         |
| ------------ | ------------ | -------------------------------------------- |
| 10.139.12.52 | 1C2G20GB | rocketmq-nameserver1、rocketmq-master1       |
| 10.139.12.53 | 1C2G20GB | rocketmq-nameserver2、rocketmq-master2       |
| 10.139.12.54 | 1C2G20GB | rocketmq-nameserver3、rocketmq-master1-slave |
| 10.139.12.55 | 1C2G20GB | rocketmq-nameserver4、rocketmqmaster2-slave  |

## 配置文件最优设置解析

### 修改host文件映射

```
10.139.12.52 rocketmq-nameserver1 rocketmq-master1
10.139.12.53 rocketmq-nameserver2 rocketmq-master2
10.139.12.54 rocketmq-nameserver3 rocketmq-master1-slave
10.139.12.55 rocketmq-nameserver4 rocketmq-master2-slave
```

将4个节点的hosts均改为如上内容，并将4.4.0版本包放入环境中解压

![image-20201221151014840](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201221151014840.png)



### 创建存储目录

```bash
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store 
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/commitlog 
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/consumequeue 
$ mkdir -p ~/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/index
```



### 建立软连接

```bash
$ cd ~/rocketmq-test
$ ln -s rocketmq-all-4.4.0-bin-release rocketmq
```



### 修改配置文件

解压后默认的配置文件如下

```bash
[user@301 ~/rocketmq-test/rocketmq/conf]$ll
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

若想保障生产环境高可用，推荐使用**双主双从同步双写**模式，可以让一个主节点对应多个从节点，但从节点越多，同步效率越慢

本次采用**双主双从同步双写**模式，一个主节点对应一个从节点

```bash
[user@301 ~/rocketmq-test/rocketmq/conf/2m-2s-sync]$ll
total 16
-rw-r--r-- 1 ocmuser gpocm 928 Jan 17  2019 broker-a.properties
-rw-r--r-- 1 ocmuser gpocm 922 Jan 17  2019 broker-a-s.properties
-rw-r--r-- 1 ocmuser gpocm 928 Jan 17  2019 broker-b.properties
-rw-r--r-- 1 ocmuser gpocm 922 Jan 17  2019 broker-b-s.properties
```

用途如下

| IP           | 资源         | 服务                                   | 配置文件              |
| ------------ | ------------ | -------------------------------------- | --------------------- |
| 10.139.12.52 | 1C2G20GB | rocketmq-nameserver1、rocketmq-master1 | broker-a.properties   |
| 10.139.12.53 | 1C2G20GB | rocketmq-nameserver2、rocketmq-master2 | broker-b.properties   |
| 10.139.12.54 | 1C2G20GB | rocketmq-nameserver3、rocketmq-slave1  | broker-a-s.properties |
| 10.139.12.55 | 1C2G20GB | rocketmq-nameserver4、rocketmq-slave2  | broker-b-s.properties |

#### `broker-a.properties` 配置 

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样
brokerName=broker-a
#0 表示 Master，>0 表示 Slave
brokerId=0
#nameServer 地址，分号分割
namesrvAddr=rocketmq-nameserver1:9876;rocketmq-nameserver2:9876;rocketmq-nameserver3:9876;rocketmq-nameserver4:9876
#在发送消息时，自动创建服务器不存在的 topic，默认创建的队列数
defaultTopicQueueNums=4
#是否允许 Broker 自动创建 Topic，建议线下开启，线上关闭
autoCreateTopicEnable=false
#是否允许 Broker 自动创建订阅组，建议线下开启，线上关闭
autoCreateSubscriptionGroup=false
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
#检测物理文件磁盘空间，最大100%
diskMaxUsedSpaceRatio=88
#存储路径
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq/store/abort
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
brokerRole=SYNC_MASTER
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

#### `broker-b.properties` 配置

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样
brokerName=broker-b
#0 表示 Master，>0 表示 Slave
brokerId=0
#nameServer 地址，分号分割
namesrvAddr=rocketmq-nameserver1:9876;rocketmq-nameserver2:9876;rocketmq-nameserver3:9876;rocketmq-nameserver4:9876
#在发送消息时，自动创建服务器不存在的 topic，默认创建的队列数
defaultTopicQueueNums=4
#是否允许 Broker 自动创建 Topic，建议线下开启，线上关闭
autoCreateTopicEnable=false
#是否允许 Broker 自动创建订阅组，建议线下开启，线上关闭
autoCreateSubscriptionGroup=false
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
#检测物理文件磁盘空间，最大100%
diskMaxUsedSpaceRatio=88
#存储路径
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq/store/abort
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

#### `broker-a-s.properties` 配置

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样，与 Master 通过 brokerName 来配对
brokerName=broker-a
#0 表示 Master，>0 表示 Slave
brokerId=1
#nameServer 地址，分号分割
namesrvAddr=rocketmq-nameserver1:9876;rocketmq-nameserver2:9876;rocketmq-nameserver3:9876;rocketmq-nameserver4:9876
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
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq/store/abort
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
brokerRole=SLAVE
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

#### `broker-b-s.properties` 配置

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样，与 Master 通过 brokerName 来配对
brokerName=broker-b
#0 表示 Master，>0 表示 Slave
brokerId=1
#nameServer 地址，分号分割
namesrvAddr=rocketmq-nameserver1:9876;rocketmq-nameserver2:9876;rocketmq-nameserver3:9876;rocketmq-nameserver4:9876
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
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq/store/abort
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
brokerRole=SLAVE
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


<aside class="legacy-note">

注意：RocketMQ对配置文件行尾空格敏感，注意不要有行尾空格

</aside>


分发配置文件

```bash
$ scp broker-* ocmuser@rocketmq-master2-slave:/home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync
$ scp broker-* ocmuser@rocketmq-master2:/home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync
$ scp broker-* ocmuser@rocketmq-master1-slave:/home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync
```

### 修改日志配置文件

```bash
$ mkdir -p /home/ocmuser/rocketmq-test/rocketmq/logs
$ cd /home/ocmuser/rocketmq-test/rocketmq/conf && sed -i 's#${user.home}#/home/ocmuser/rocketmq-test/#g' *.xml
```



### 修改脚本启动参数

`/home/ocmuser/rocketmq-test/rocketmq/bin/runbroker.sh`内容如下，至少保障1g内存

```bash
#======================================================================================
# 开发环境JVM Configuration
#======================================================================================
JAVA_OPT="${JAVA_OPT} -server -Xms1g -Xmx1g -Xmn512m"

```

`/home/ocmuser/rocketmq-test/rocketmq/bin/runserver.sh`内容如下

```bash
#======================================================================================
# JVM Configuration
#======================================================================================
JAVA_OPT="${JAVA_OPT} -server -Xms1g -Xmx1g -Xmn512m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m"
```



### 启动 NameServer

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq/bin
$ nohup sh mqnamesrv &
```



### 启动 Master1:BrokerServerA

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq/bin 
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync/broker-a.properties >/dev/null 2>&1 & 
$ netstat -ntlp 
$ jps 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/logs/rocketmqlogs/broker.log 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/logs/rocketmqlogs/namesrv.log
```



### 启动 Master2:BrokerServerB

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq/bin 
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync/broker-b.properties >/dev/null 2>&1 & 
$ netstat -ntlp 
$ jps 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/logs/rocketmqlogs/broker.log 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/logs/rocketmqlogs/namesrv.log 
```



### 启动 Master1-Slave:BrokerServerC

```bash
$ cd cd /home/ocmuser/rocketmq-test/rocketmq/bin 
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync/broker-a-s.properties >/dev/null 2>&1 & 
$ netstat -ntlp 
$ jps 
$ tail -f -n 500 cd /home/ocmuser/rocketmq-test/logs/rocketmqlogs/broker.log 
$ tail -f -n 500 cd /home/ocmuser/rocketmq-test/logs/rocketmqlogs/namesrv.log 
```



### 启动 Master2-Slave:BrokerServerD

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq/bin 
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq/conf/2m-2s-sync/broker-b-s.properties >/dev/null 2>&1 & 
$ netstat -ntlp 
$ jps 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/logs/rocketmqlogs/broker.log 
$ tail -f -n 500 /home/ocmuser/rocketmq-test/logs/rocketmqlogs/namesrv.log 
```

查看进程和日志，可见部署完成

![image-20201223142210826](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201223142210826.png)

角色为同步双写，异步刷盘，4个节点通信正常

![image-20201223172428307](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201223172428307.png)

![image-20201223172525074](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201223172525074.png)



### 控制台监控验证

修改连接配置

```properties
rocketmq.config.namesrvAddr=10.139.12.51:9876;10.139.12.52:9876;10.139.12.53:9876;10.139.12.54:9876
```



连接正常

![image-20201223172027458](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201223172027458.png)

查看各节点角色和状态

![image-20201223172105913](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201223172105913.png)



### 服务停止

首先关闭 4 个 BrokerServer，再关闭 4 个 NameServer

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq/bin 
$ sh mqshutdown broker 
$ sh mqshutdown namesrv 
```



## 双主双从环境构建与调优

1. 为取得可靠性与效率的平衡，建议采用同步双写，异步刷盘的模式
