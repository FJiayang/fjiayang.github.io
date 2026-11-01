{
  "title": "PXC系列学习笔记（五）——Sysbench基准测试 ",
  "date": "2019-12-30T08:48:05+08:00",
  "lastmod": "2019-12-30T08:48:05+08:00",
  "typecho_cid": 234,
  "url": "/archives/234/",
  "comments": false,
  "draft": false,
  "slug": "234",
  "categories": [
    "学习"
  ],
  "tags": [
    "MySQL",
    "Percona",
    "PXC"
  ],
  "image": "/images/recovered/de47efcb191c722de4a9.png",
  "math": false
}

## 一、介绍

为了检测当前搭建的PXC集群性能，需要执行基准测试，看是否符合性能指标，并对sql进行针对性优化



## 二、安装Sysbench

选择集群以外的节点安装测试工具，保证测试的准确性，并且能与集群在网络上互通。

本次选择的机器配置如下，且位于同一内网网段，网络影响因素几乎忽略不计

| 名称     | IP           | CPU  | 内存 | 磁盘 |
| -------- | ------------ | ---- | ---- | ---- |
| Sysbench | 192.168.1.24 | 2    | 12G  | 20G  |

- 在线安装

  ```shell
  curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.rpm.sh | sudo bash 
  ```

```shell
  yum -y install sysbench
```

- 本地安装

  - 下载压缩文件

    [https://](https://codeload.github.com/akopytov/sysbench/zip/1.0)[codeload.github.com/akopytov/sysbench/zip/1.0](https://codeload.github.com/akopytov/sysbench/zip/1.0)

  - 安装依赖包

    ```shell
    yum install -y automake libtool
    yum install -y mysql-devel
    ```

  - 执行安装

    ```shell
    #cd sysbench
    ./autogen.sh 
    ./configure 
    make
    make install
    sysbench --version
    ```

## 执行测试

参数介绍

| 参数名称            | 功能意义                                                    |
| ------------------- | ----------------------------------------------------------- |
| \-oltp-test-mode    | 执行模式(simple只测试查询、nontrx无事务、**complex有事务**) |
| \-oltp-tables-count | 测试表的数量                                                |
| \-oltp-table-size   | 测试表的记录数                                              |
| \-threads           | 并发连接数                                                  |
| \-time              | 测试执行时间（秒）                                          |
| \-report-interval   | 生成报告单的间隔时间（秒）                                  |

COMMAND 命令

| 参数名称 | 功能意义     |
| -------- | ------------ |
| prepare  | 准备测试数据 |
| run      | 执行测试     |
| cleanUD  | 清除测试数据 |

- 准备测试库，手动连接到pxc集群，创建名为sbtest的测试库

  ```shell
  sysbench  /usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --mysql-host=192.168.1.9 --mysql-port=3306 --mysql-user=admin --mysql-password=Abc_123456 --oltp-tables-count=10 --oltp-table-size=100000 prepare
  ```

  ![1577453015988](/images/recovered/eaf5d428c9a2a65609a5.png)

- 执行测试

  ```shell
  sysbench  /usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --mysql-host=192.168.1.9 --mysql-port=3306 --mysql-user=admin --mysql-password=Abc_123456 --oltp-test-mode=complex --threads=10 --time=300 --report-interval=10 run >> /home/mysysbench.log
  ```

  ![1577453381678](/images/recovered/176f224d65e5cd3ca11f.png)

  5分钟压测结果

  ```ini
  SQL statistics:
      queries performed:
          read:                            1122604
          write:                           307573
          other:                           160792
          total:                           1590969
      transactions:                        72545  (241.79 per sec.)
      queries:                             1590969 (5302.59 per sec.)
      ignored errors:                      7641   (25.47 per sec.)
      reconnects:                          0      (0.00 per sec.)
  
  General statistics:
      total time:                          300.0339s
      total number of events:              72545
  
  Latency (ms):
           min:                                   10.26
           avg:                                   41.35
           max:                                 2246.45
           95th percentile:                       78.60
           sum:                              2999916.73
  
  Threads fairness:
      events (avg/stddev):           7254.5000/602.52
      execution time (avg/stddev):   299.9917/0.01
  ```

  

- 清理数据

  ```shell
  sysbench /usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --mysql-host=192.168.1.9 --mysql-port=3306 --mysql-user=admin --mysql-password=Abc_123456 --oltp-tables-count=10 cleanup
  ```

修改haproxy，跳过mycat，直接对pxc集群进行测试

```
listen   proxy_mysql
    bind    0.0.0.0:13306
    mode  tcp
    balance  roundrobin
    option  tcplog
    server   pxc_1  192.168.1.32:3306  check  port  3306 weight 1 maxconn  2000
    server   pxc_2  192.168.1.33:3306  check  port  3306 weight 1 maxconn  2000
    server   pxc_3  192.168.1.35:3306  check  port  3306 weight 1 maxconn  2000
    option  tcpka
```

结果

![1577452516683](/images/recovered/15bf28c9411842548b5f.png)

推荐测试配置：

- 数据表建议不低于10个,单表数据量不低于500万行。如果是配备了SSD或者 PCIE SSD的话,则建议单表数据量最少不低于1亿行，测试时间应当在24小时以上
