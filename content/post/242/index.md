{
  "title": "Docker MySQL主从复制方案",
  "date": "2020-04-17T15:37:02+08:00",
  "lastmod": "2020-04-17T15:37:02+08:00",
  "typecho_cid": 242,
  "url": "/archives/242/",
  "comments": false,
  "draft": false,
  "slug": "242",
  "categories": [
    "开发"
  ],
  "tags": [
    "docker",
    "MySQL",
    "高可用"
  ],
  "math": false
}

## 背景

现有网上很多教程都是修改了源MySQL镜像，因此会存在安全隐患，也不容易提升版本。此处给出不修改源镜像的主从复制配置方案。



## 现状

现有一台生产上运行的MySQL5.7服务器，由docker镜像提供支持

原docker-compose文件

```yaml
version: '3.7'
services:

  mysql57:
    image: mysql:5.7
    restart: always
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    ports:
      - 3306:3306
    networks:
      - prod
    volumes:
      - ./mysql57/data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
networks:
  prod:
```





## 改造过程

### 配置主服务器

#### 新增同步用户并授权

```mysql
##创建slave1用户
CREATE USER 'slave1'@'%' IDENTIFIED BY 'slavepass';

##为slave1赋予REPLICATION SLAVE权限。
GRANT REPLICATION SLAVE ON *.* TO 'slave1'@'%';
```



#### 开启binlog日志

由于原主服务器没有开启binlog日志，故需要挂载配置文件并开启binlog日志

新增配置文件`custom-master.cnf`

```bash
[mysqld]
log-bin         = mysql-bin
log-bin-index   = mysql-bin.index
binlog_format   = mixed
server-id       = 1
sync-binlog     = 1
character-set-server = utf8
```

修改docker-compose文件为

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
      - prod
    volumes:
      - ./mysql57/data:/var/lib/mysql
      - ./mysql57/custom-master.cnf:/etc/mysql/conf.d/custom.cnf
      - ./mysql57/log:/var/log/mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
networks:
  prod:
```

更新服务（会短暂停机）

```bash
$ docker-compose up -d
```



配置内容解释

```bash
log-bin：设置二进制日志文件的基本名；
log-bin-index：设置二进制日志索引文件名；
binlog_format：控制二进制日志格式，进而控制了复制类型，三个可选值
    -STATEMENT：语句复制
    -ROW：行复制
    -MIXED：混和复制，默认选项
server-id：服务器设置唯一ID，默认为1，推荐取IP最后部分；
sync-binlog：默认为0，为保证不会丢失数据，需设置为1，用于强制每次提交事务时，同步二进制日志到磁盘上。
```



#### 备份主数据库数据

**该步骤可以等到两台从服务器的docker环境都配置完毕后操作，以减少停机时间**

1. 获取一个一致性的快照，需对所有表设置读锁：

```mysql
flush tables with read lock;
```



2. 获取二进制日志的坐标：

```mysql
show master status;
```

| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
| ---------------- | -------- | ------------ | ---------------- | ----------------- |
| mysql-bin.000003 | 6165     |              |                  |                   |

3. 备份数据 

```mysql
# 针对事务性引擎
mysqldump -u root -p --all-databases -e --single-transaction --flush-logs --max_allowed_packet=1048576 --net_buffer_length=16384 > /var/log/mysql/all_db.sql
# 针对 MyISAM 引擎，或多引擎混合的数据库
mysqldump -uroot --all-databases -e -l --flush-logs --max_allowed_packet=1048576 --net_buffer_length=16384 > /var/log/mysql/all_db.sql
```

由于挂载了日志目录，故在容器外部可以看到该备份的数据文件



### 配置从服务器

1. 新增两台CentOS 7服务器，并安装docker和docker-compose服务
2. 由于主从复制要求所有机器版本号包括小版本号都必须一致，故此处拉取`mysql:5.7.29`镜像
3. 从主库拷贝数据文件`all_db.sql`到两台从库上

```bash
$ scp /root/mysql/log/all_db.sql root@192.168.1.33:/root/mysql/log/
```

4. 新增配置文件`custom-slave1.cnf`

```bash
[mysqld]
log-bin             = mysql-bin
binlog_format       = mixed
log-slave-updates   = 0
server-id           = 2
relay-log           = mysql-relay-bin
relay-log-index     = mysql-relay-bin.index
read-only           = 1
slave_net_timeout   = 10
```

5. 新增docker-compose文件

```yaml
version: '3'
services:

  mysql57-master:
    image: mysql:5.7.29
    restart: always
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    ports:
      - 3306:3306
    networks:
      - mysql-net
    volumes:
      - ./data:/var/lib/mysql
      - ./custom-slave1.cnf:/etc/mysql/conf.d/custom.cnf
      - ./log:/var/log/mysql
    environment:
      MYSQL_ROOT_PASSWORD: root

networks:
  mysql-net:
```

6. 由于也挂载了log目录，启动后容器内就已经有从主库同步过来的数据文件
7. 数据恢复

```mysql
mysql -u root -p < /var/log/mysql/all_db.sql
```

8. 使用工具连接数据库，配置主从连接

```mysql
CHANGE MASTER TO
MASTER_HOST='10.168.1.30',
MASTER_USER='slave1',
MASTER_PASSWORD='slavepass',
MASTER_LOG_FILE='mysql-bin.000003',
MASTER_LOG_POS=6165;
```

9. 启动slave同步进程

```mysql
start slave;
```

10. 关闭主服务器全局读锁

```mysql
UNLOCK TABLES;
```

11. 查看从服务器同步状态，主要是`Slave_IO_Running`，` Slave_SQL_Running`状态必须为`Yes`

| Slave_IO_State                   | Master_Host  | Master_User | Master_Port | Connect_Retry | Master_Log_File  | Read_Master_Log_Pos | Relay_Log_File         | Relay_Log_Pos | Relay_Master_Log_File | Slave_IO_Running | Slave_SQL_Running | Replicate_Do_DB | Replicate_Ignore_DB | Replicate_Do_Table | Replicate_Ignore_Table | Replicate_Wild_Do_Table | Replicate_Wild_Ignore_Table | Last_Errno | Last_Error | Skip_Counter | Exec_Master_Log_Pos | Relay_Log_Space | Until_Condition | Until_Log_File | Until_Log_Pos | Master_SSL_Allowed | Master_SSL_CA_File | Master_SSL_CA_Path | Master_SSL_Cert | Master_SSL_Cipher | Master_SSL_Key | Seconds_Behind_Master | Master_SSL_Verify_Server_Cert | Last_IO_Errno | Last_IO_Error | Last_SQL_Errno | Last_SQL_Error | Replicate_Ignore_Server_Ids | Master_Server_Id | Master_UUID                          | Master_Info_File           | SQL_Delay | SQL_Remaining_Delay | Slave_SQL_Running_State                                | Master_Retry_Count | Master_Bind | Last_IO_Error_Timestamp | Last_SQL_Error_Timestamp | Master_SSL_Crl | Master_SSL_Crlpath | Retrieved_Gtid_Set | Executed_Gtid_Set | Auto_Position | Replicate_Rewrite_DB | Channel_Name | Master_TLS_Version |
| -------------------------------- | ------------ | ----------- | ----------- | ------------- | ---------------- | ------------------- | ---------------------- | ------------- | --------------------- | ---------------- | ----------------- | --------------- | ------------------- | ------------------ | ---------------------- | ----------------------- | --------------------------- | ---------- | ---------- | ------------ | ------------------- | --------------- | --------------- | -------------- | ------------- | ------------------ | ------------------ | ------------------ | --------------- | ----------------- | -------------- | --------------------- | ----------------------------- | ------------- | ------------- | -------------- | -------------- | --------------------------- | ---------------- | ------------------------------------ | -------------------------- | --------- | ------------------- | ------------------------------------------------------ | ------------------ | ----------- | ----------------------- | ------------------------ | -------------- | ------------------ | ------------------ | ----------------- | ------------- | -------------------- | ------------ | ------------------ |
| Waiting for master to send event | 192.168.1.30 | slave1      | 3306        | 60            | mysql-bin.000003 | 3722724             | mysql-relay-bin.000002 | 3717604       | mysql-bin.000003      | Yes              | Yes               |                 |                     |                    |                        |                         |                             | 0          |            | 0            | 3722724             | 3717811         | None            |                | 0             | No                 |                    |                    |                 |                   |                | 0                     | No                            | 0             |               | 0              |                |                             | 1                | 4c99130f-e664-11e9-987b-0242ac120003 | /var/lib/mysql/master.info | 0         |                     | Slave has read all relay log; waiting for more updates | 86400              |             |                         |                          |                |                    |                    |                   | 0             |                      |              |                    |



## 可能出现的问题

### 死锁——waiting for global read lock

 原因在于flush tables with read lock语句和事务执行的过程都涉及到连个锁，而且不是原子的，再加上并行复制以及设置了从库`binlog`的顺序提交，最终导致多个线程形成死锁 

解决方法：

- 重启主数据库
- 查看所有连接线程，分析死锁的原因，杀掉执行`flush tables with read lock`的线程



参考资料：

- [MySQL备份导致的waiting for global read lock](https://blog.51cto.com/aklaus/1657055)
- [由FTWRL导致的MySQL从库死锁分析及参数深究](https://dbaplus.cn/news-11-1874-1.html)
