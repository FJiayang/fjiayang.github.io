{
  "title": "PXC系列学习笔记（一）——PXC单节点安装配置",
  "date": "2019-12-29T20:03:00+08:00",
  "lastmod": "2020-12-26T14:11:06+08:00",
  "typecho_cid": 230,
  "url": "/archives/230/",
  "comments": false,
  "draft": false,
  "slug": "230",
  "categories": [
    "学习"
  ],
  "tags": [
    "MySQL",
    "Percona",
    "PXC"
  ],
  "image": "https://fjy8018.gitee.io/images/img/logo_0_1.png",
  "math": false
}

本系列笔记是对慕课网课程的学习与总结[MySQL数据库集群-PXC方案](https://coding.imooc.com/class/274.html)

![1577620098597](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1577620098597.png)



## Percona数据库介绍

[官网](https://www.percona.com/)
[Percona官网](https://www.percona.com/)

![Percona官网](https://learn.percona.com/hs-fs/hubfs/Images/Logos/P%20-%20Percona.png)

![1577620169318](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1577620169318.png)

Percona数据库提供MySQL、MongoDB等衍生版本，在大数据、同步性能上做了大量优化



## 安装

Percona官方也有提供docker镜像，但为了方便学习，全使用云服务器安装Percona数据库，本次使用的机器配置为

- CPU：1C
- RAM：1G
- DISK：40G

### 1. 离线安装Percona

安装前置环境

```bash
$ yum install https://repo.percona.com/yum/percona-release-latest.noarch.rpm -y
$ yum install qpress
```

进入[官网](https://www.percona.com/downloads/)下载5.7版本的Percona，注意，此处下载的是单机版本

![1577621418297](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1577621418297.png)

- 进入RPM安装文件目录，执行下面的脚本

  ```bash
  $ yum localinstall *.rpm
  ```

- 管理MySQL服务

  ```shell
  $ systemctl enable mysqld
  $ systemctl start mysqld
  $ systemctl stop mysqld
  $ systemctl restart mysqld
  ```

### 2. 在线安装Percona（不推荐）

在线安装不便于统一版本和多节点分发

- 使用yum命令安装

  ```shell
  $ yum install https://repo.percona.com/yum/percona-release-latest.noarch.rpm
  $ yum  install  Percona-Server-server-57
  ```

- 管理MySQL服务

  ```shell
  $ service mysql start
  $ service mysql stop
  $ service mysql restart
  ```

### 3. 开放防火墙端口

```shell
$ firewall-cmd --zone=public --add-port=3306/tcp --permanent
$ firewall-cmd --reload
```

### 4. 修改MySQL配置文件

```shell
vi /etc/my.cnf
```

```ini
[mysqld]
character_set_server = utf8
bind-address = 0.0.0.0
#跳过DNS解析
skip-name-resolve
```

```shell
$ service mysql restart 
```

### 5. 禁止开机启动MySQL

若某一节点宕机，其自动启动后会开始自动同步，若宕机时间过长，PXC集群会限制其他节点的写入操作，直到所有数据同步成功

宕机后科学做法：手动从其他节点中拷贝数据库文件，再启动，减少同步数据

```shell
$ chkconfig mysqld off
```

注意，关闭了开机启动后无法使用`service mysql restart `命令启动数据库，需要使用下面的命令启动

```bash
$ service mysqld restart 
```



### 6. 初始化MySQL数据库

- 查看MySQL初始密码

  ```shell
  cat /var/log/mysqld.log | grep "A temporary password"
  ```

- 修改MySQL密码

  ```shell
  mysql_secure_installation
  ```

  修改过程全输入y，并录入密码

- 创建远程管理员账户

  ```shell
  mysql -u root -p
  ```

  ```sql
  CREATE USER 'admin'@'%' IDENTIFIED BY 'password';
  GRANT all privileges ON *.* TO 'admin'@'%';
  FLUSH PRIVILEGES;
  ```
