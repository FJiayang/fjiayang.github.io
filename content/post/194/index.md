{
  "title": "HBase 学习笔记",
  "date": "2018-12-15T12:06:00+08:00",
  "lastmod": "2019-12-05T15:34:10+08:00",
  "typecho_cid": 194,
  "url": "/archives/194/",
  "comments": false,
  "draft": false,
  "slug": "194",
  "categories": [
    "学习"
  ],
  "tags": [
    "hadoop",
    "HBase"
  ],
  "math": false
}

## 概述

### HBase 简介

- Hbase是一个分布式的、面向列的开源数据库
  - 列式数据库：将列值统一存储
  - 行式数据库：关系型数据库，将每一行值统一存储
- Hbase在Hadoop之上提供了类似于Bigtable的能力
  - Bigtable是压缩、高性能、高可扩展性的基于Google GFS文件系统的数据库，用于存储大规模的结构化数据，在扩展性和性能上有很大的优势
- Hbase不同于一般的关系数据库，它适合非结构化数据存储
  - 非结构化数据：不能用二维表进行存储的数据，例如图片、文档等

### Hbase地位

- Apache基金会顶级项目
- 基于Hadoop核心HDFS系统进行数据存储，类似于Hive
- 可以存储超大数据并适合用来进行大数据的的**实时查询**

### Hbase与HDFS

- Hbase建立在Hadoop文件系统上，利用了Hadoop文件系统的容错能力
- Hbase提供对数据**随机实时读/写**访问功能
- Hbase内部使用**哈希表**存储索引，可将HDFS文件中的数据进行快速查找

### 适用场景

- 瞬间写入量很大，常用数据库不好支持或者需要很高的成本支撑
- 数据需要长久保存，且数据量会持久增长到比较大的场景
- Hbase不适合用于有join、多级索引、表关系复杂的数据模型

## 存储模型与原理

### CAP定理

分布式系统的CAP理论：理论首先把分布式系统中的三个特性进行了如下归纳：

- 一致性（C）：所有节点在同一时间具有相同的数据

- 可用性（A）：保证每个请求不管成功或者失败（包含节点宕机）都有响应，但不保证获取数据的正确性

- 分区容错性（P）：系统中任意信息的丢失或失败不会影响系统的继续运作。系统如果不能在时限内达成数据一致性，必须就当前操作在C和A之间做出选择。



Hbase为CP特性

### ACID

ACID的定义：

- **Atomic原子性**:所有的步骤要么全部完成要么一个也不会完成
- **Consistent一致性**: 通过各种途径包括外键约束等任何写入数据库的数据都是有效的，不能发生表与表之间存在外键约束
- **Isolated**隔离性: 一个未完成事务不会影响另外一个未完成事务
- **Durable**持久性: 一旦一个事务被提交，它应该持久保存



HBase非强ACID

### HBase概念

| 字段                         | 概念                                                         | 备注                                                         |
| ---------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| NameSpace                    | 类似RDBMS的“数据库”                                          |                                                              |
| Table                        | 表名必须是能用在文件路径里的合法名字                         | 原因：每个表都会映射为HDFS的文件                             |
| Row                          | 在表里，每一行代表一个数据对象，每一行都以一个行键（Row Key）来唯一标识的，行键没有特定的数据类型，以二进制的字节进行存储 |                                                              |
| Row Key                      | 唯一标识一行记录，不可改变，只能删除                         |                                                              |
| Column                       | 由Column family和Column qualifier组成，由（：）进行分隔      | 例如：family：qualifier                                      |
| Column family                | 在定义HBase表的时候需要提前设置好列族，表中所有的列都需要组织在列族里面 | 同一个列族的成员有相同的前缀，物理上，一个列族的成员都是储存在一起，用于存储优化 |
| Column qualifier（列限定符） | 列族中的数据通过列标识来进行映射，可以理解为一个键值对，Column qualifier就是Key | 类似具体的列名                                               |
| Cell                         | 每一个行键，列族和列标识共同组成的一个单元                   | 无特定的数据类型，以二进制字节存储                           |
| Timestamp                    | 每个值都有一个Timestamp，作为该值特定版本的标识符            | 读未指定版本则返回最新版，写未指定时间则使用当前时间，HBase默认保留3个版本数据 |

### HBase与传统关系数据库的区别

|            | Hbase                 | RDBMS          |
| ---------- | --------------------- | -------------- |
| 数据库大小 | PB                    | GB、TB         |
| 数据类型   | Bytes                 | 丰富的数据类型 |
| 事务支持   | ACID只支持单个Row级别 | 全面的ACID支持 |
| 索引       | 只支持Row-Key         | 支持           |
| 吞吐量     | 百万查询/每秒         | 数千查询/每秒  |
## HBase基础架构

[![hbase1.jpg](https://i.loli.net/2018/12/15/5c14dd85593e5.jpg)](https://i.loli.net/2018/12/15/5c14dd85593e5.jpg)

### HBase分布式系统简介

- HMaster
  - HBase主/从集群架构中的中央节点
  - 负责将region（HBase中存储最小单元，表格的基本单位）分配给RegionServer，协调RegionServer的负载并维护集群状态
  - 维护表和Region的元数据，不参与数据的输入/输出过程
- RegionServer
  - 维护HMaster分配给他的region，处理对这些region的IO请求
  - 负责切分正在运行过程中变得过大的region
- Zookeeper
  - 集群协调器，保证至少一个节点出于active状态
  - HMaster启动将系统表加载到ZK（用于服务发现）
  - 提供HBase RegionServer状态信息
## HBase原理

### HBase写流程

[![hbase2.jpg](https://i.loli.net/2018/12/15/5c14eab0b66f1.jpg)](https://i.loli.net/2018/12/15/5c14eab0b66f1.jpg)

1. Client先访问zookeeper，得到对应的RegionServer地址
2. Client对RegionServer发起写请求，RegionServer接受数据写入内存
3. 当MemStore的大小达到一定值后，flush到StoreFile并存储到HDFS



[![hbase3.jpg](https://i.loli.net/2018/12/15/5c14f18fb8065.jpg)](https://i.loli.net/2018/12/15/5c14f18fb8065.jpg)

HBase特殊点在于其先写内存再写日志，通过类似MySQL中MVCC机制保证一致性

### HBase读流程

[![hbase4.jpg](https://i.loli.net/2018/12/15/5c14f377038f9.jpg)](https://i.loli.net/2018/12/15/5c14f377038f9.jpg)

1. Client先访问zookeeper，得到对应的RegionServer地址
2. Client对RegionServer发起读请求
3. 当RegionServer收到client的读请求后，先扫描自己的Memstore，再扫描BlockCache（加速读内容缓存区）如果还没找到则从StoreFile中读取数据，然后将数据返回给Client

#### 读特点

- 读过程与HMaster无关，只和ZK有关，有效的减小HMaster负载

### HBase模块协作

有关HBase的三个问题

1. HBase启动时发生了什么
2. 当RegionServer失效后会发生什么
3. 当HMaster失效后会发生什么

#### HBase启动

1. HBase启动，注册到zookeeper，等待RegionServer汇报
2. RegionServer注册到zookeeper，并向HMaster汇报
3. 对各个RegionServer（包括失效的）的数据进行整理，分配Region和meta信息（所有表的索引）

#### RegionServer失效

1. HMaster将失效RegionServer上的Region分配到其他节点
2. HMaster更新HBase：meta表保证数据正常访问

#### HMaster失效

配置高可用后

1. 出于Backup状态的其他HMaster节点选举出一个转为Active状态

未配置高可用

1. 数据能正常读写，但不能创建删除表，也不能更改表结构，因为涉及meta表更新
