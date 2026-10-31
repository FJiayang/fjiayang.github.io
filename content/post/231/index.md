{
  "title": "PXC系列学习笔记（二）——PXC集群安装配置",
  "date": "2019-12-30T08:42:07+08:00",
  "lastmod": "2019-12-30T08:42:07+08:00",
  "typecho_cid": 231,
  "url": "/archives/231/",
  "comments": false,
  "draft": false,
  "slug": "231",
  "categories": [
    "学习"
  ],
  "tags": [
    "集群",
    "MySQL",
    "Percona",
    "PXC"
  ],
  "image": "/images/recovered/de47efcb191c722de4a9.png",
  "math": false
}

## 1. 介绍

PXC集群具有强一致性特点，用于需要多节点一致性的业务，例如金融系统、交易、支付系统、库存系统等

本次计划搭建PXC集群使用两个分片，每个分片3个节点组成一个PXC集群

| 名称 | IP           | CPU  | 内存 | 磁盘 |
| ---- | ------------ | ---- | ---- | ---- |
| pxc2 | 192.168.1.32 | 1    | 2G   | 40G  |
| pxc3 | 192.168.1.33 | 1    | 2G   | 40G  |
| pxc4 | 192.168.1.35 | 1    | 2G   | 40G  |
| pxc5 | 192.168.1.36 | 1    | 2G   | 40G  |
| pxc6 | 192.168.1.37 | 1    | 2G   | 40G  |
| pxc7 | 192.168.1.38 | 1    | 2G   | 40G  |

## 2. 删除MariaDB程序包

```shell
$ yum -y remove mari*
```

## 3. 开放防火墙端口

```shell
$ firewall-cmd --zone=public --add-port=3306/tcp --permanent
$ firewall-cmd --zone=public --add-port=4444/tcp --permanent
$ firewall-cmd --zone=public --add-port=4567/tcp --permanent
$ firewall-cmd --zone=public --add-port=4568/tcp --permanent
```

## 4. 关闭SELINUX

```shell
vi /etc/selinux/config
```

把`SELINUX`属性值设置成`disabled`

```shell
reboot
```

## 5. 离线安装PXC（推荐）

进入[官网](https://www.percona.com/downloads/)下载5.7版本的Percona，注意，此处下载的是集群版本，下载后分发到所有集群节点执行相同的安装和配置操作

![1577621346428](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1577621346428.png)

- 进入RPM文件目录，执行安装命令

  ```shell
  $ yum localinstall *.rpm
  ```

- 参考前一篇内容，修改MySQL配置文件、创建账户等操作

## 6. 创建PXC集群

- 停止MySQL服务

- 修改每个PXC节点的`/etc/my.cnf`文件（在不同节点上，注意调整文件内容）

  ```ini
  server-id=1  #PXC集群中MySQL实例的唯一ID，不能重复，必须是数字
  wsrep_provider=/usr/lib64/galera3/libgalera_smm.so
  wsrep_cluster_name=pxc-cluster  #PXC集群的名称
  wsrep_cluster_address=gcomm://pxc2,pxc3,pxc4
  wsrep_node_name=pxc2  #当前节点的名称
  wsrep_node_address=pxc2  #当前节点的IP
  wsrep_sst_method=xtrabackup-v2  #同步方法（mysqldump、rsync、xtrabackup）
  wsrep_sst_auth= admin:password #同步使用的帐户
  pxc_strict_mode=ENFORCING  #同步严厉模式
  binlog_format=ROW  #基于ROW复制（安全可靠）
  default_storage_engine=InnoDB  #默认引擎
  innodb_autoinc_lock_mode=2  #主键自增长不锁表
  ```

- 主节点的管理命令（第一个启动的PXC节点）

  ```shell
  $ systemctl start mysql@bootstrap.service
  $ systemctl stop mysql@bootstrap.service
  $ systemctl restart mysql@bootstrap.service
  ```

- 非主节点的管理命令（非第一个启动的PXC节点）

  ```shell
  $ systemctl start mysql
  $ systemctl stop mysql
  $ systemctl restart mysql
  ```

- 查看PXC集群状态信息

  ```mysql
  show status like 'wsrep_cluster%' ;
  ```

- **按照上述配置方法，创建两组PXC集群**

## 7. PXC节点启动与关闭

- 如果最后关闭的PXC节点是安全退出的，那么下次启动要最先启动这个节点，而且要以主节点启动
- 如果最后关闭的PXC节点不是安全退出的，那么要先修改`/var/lib/mysql/grastate.dat` 文件，把其中的`safe_to_bootstrap`属性值设置为1，再安装主节点启动
