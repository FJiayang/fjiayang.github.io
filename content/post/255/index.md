{
  "title": "RocketMQ学习笔记5——原理解析",
  "date": "2020-12-23T19:13:00+08:00",
  "lastmod": "2023-09-07T15:06:12+08:00",
  "typecho_cid": 255,
  "url": "/archives/255/",
  "comments": false,
  "draft": false,
  "slug": "255",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "源码学习",
    "RocketMQ"
  ],
  "math": true
}

## 消息存储结构

![img](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/rocketmq_design_1.png)

1. CommitLog：消息主体以及元数据的存储主体，存储Producer端写入的消息主体内容,消息内容不是定长的。消息主要是顺序写入日志文件，当文件满了，写入下一个文件；其日志信息科用于数据恢复，作为MQ数据保障兜底策略。
2. ConsumerQueue：消息消费队列，存储消息在commit log 中所在的这个位置，也可以说是一个偏移量.引入的目的主要是提高消息消费的性能。
3. IndexFile：IndexFile（索引文件）提供了一种可以通过key或时间区间来查询消息的方法。
4. 每一个topic下的每一个message queue都对应一个ConsumerQueue文件，具体存储位置通过配置文件配置。
5. RocketMQ采用的是混合型的存储结构，即为Broker单个实例下所有的队列（ConsumerQueue）共用一个日志数据文件（即为CommitLog）来存储。
6. 刷盘采用顺序写随机读的模式。
7. 消费端采用“0拷贝”模式提升性能。



## 同步\异步刷盘

- 消息存储：内存+磁盘存储，两种刷盘方式

![img](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/rocketmq_design_2.png)

### 异步刷盘

- 能够充分利用OS的PageCache的优势，只要消息写入PageCache（内存）即可将成功的ACK（成功信息）返回给Producer端。
- 消息堆积到一定量才触发刷盘。
- 消息刷盘采用后台异步线程提交的方式进行，降低了读写延迟，提高了MQ的性能和吞吐量。



### 同步刷盘

- 只有在消息真正持久化至磁盘后RocketMQ的Broker端才会真正返回给Producer端一个成功的ACK响应。
- 同步刷盘对MQ消息可靠性来说是一种不错的保障，但是性能上会有较大影响，一般适用于金融业务应用该模式较多。





##  同步\异步复制

- 针对集群模式设计，同一组Broker有Master-Slave角色
- 推荐采用**同步双写，异步复制**的模式保持性能与可靠性的平衡

### 同步复制

- Master与Slave都成功才返回ACK（成功信息）给Producer



### 异步复制

- Master节点刷盘成功后立即返回ACK（成功信息）给Producer
- 再通过异步线程将信息同步给其他Slave节点
- 高性能，但存在数据丢失风险



### 同步双写

每个Master配置一个Slave，有多对Master-Slave，HA采用同步双写方式，即只有主备都写成功，才向应用返回成功，这种模式的优缺点如下：

- 优点：数据与服务都无单点故障，Master宕机情况下，消息无延迟，服务可用性与数据可用性都非常高；
- 缺点：性能比异步复制模式略低（大约低10%左右），发送单个消息的RT会略高，且目前版本在主节点宕机后，备机不能自动切换为主机。



## 高可用机制

- Master-Slave搭配实现高可用机制
- 通过BrokerId区分节点
- Master支持读写，Slave只读
- 当Master繁忙或者不可用时，可以自动切换到Slave读取消息



### 最佳实践

1. 创建Topic时，将Topic的Message Queue创建到多个Broker组中，使得逻辑上高可用
2. 由于RocketMQ不支持主从切换，故可以考虑使用监控程序监听主节点的有效性，若连接超时，则将Slave节点的配置改为Master并重启，升级为主节点，实现高可用。



## NameServer协调者

- NameServer是一个非常简单的Topic路由注册中心，其角色类似Dubbo中的zookeeper，**支持Broker的动态注册与发现**，是整个集群的状态服务器。
- 主要包括两个功能：
  - Broker管理，NameServer接受Broker集群的注册信息并且保存下来作为**路由信息**的基本数据。然后提供心跳检测机制，检查Broker是否还存活；
  - 路由信息管理，每个NameServer将保存关于Broker集群的整个路由信息和用于客户端查询的队列信息。然后Producer和Conumser通过NameServer就可以知道整个Broker集群的路由信息，从而进行消息的投递和消费。
- NameServer通常也是**集群**的方式部署，各实例间相互不进行信息通讯。Broker是向**每一台**NameServer注册自己的路由信息，所以每一个NameServer实例上面都保存一份完整的路由信息。
- 当某个NameServer因某种原因下线了，Broker仍然可以向其它NameServer同步其路由信息，Producer,Consumer仍然可以动态感知Broker的路由的信息。

### 为什么不用zookeeper

- RocketMQ 3.x以前使用zookeeper实现，后来改为nameserver实现
- zookeeper提供主从选举，广播原子性等特性在MQ中用不上，功能冗余
- zk使用主从自动切换提供高可用保障，nameserver使用多副本节点保障高可用
- nameserver只提供路由等基本状态信息维护，代码量小，更加轻量，便于维护。

NameServer信息维护源码

```java
package org.apache.rocketmq.namesrv.routeinfo;

public class RouteInfoManager {
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    private final HashMap<String/* topic */, List<QueueData>> topicQueueTable;
    private final HashMap<String/* brokerName */, BrokerData> brokerAddrTable;
    private final HashMap<String/* clusterName */, Set<String/* brokerName */>> clusterAddrTable;
    private final HashMap<String/* brokerAddr */, BrokerLiveInfo> brokerLiveTable;
    private final HashMap<String/* brokerAddr */, List<String>/* Filter Server */> filterServerTable;
}
```
