{
  "title": "HBase伪分布式安装",
  "date": "2018-12-15T19:18:00+08:00",
  "lastmod": "2019-01-03T21:24:13+08:00",
  "typecho_cid": 195,
  "url": "/archives/195/",
  "comments": false,
  "draft": false,
  "slug": "195",
  "categories": [
    "开发"
  ],
  "tags": [
    "hadoop",
    "HBase"
  ],
  "math": false
}

## Hadoop伪分布式安装

### 基础环境

1. Hadoop：版本2.7.3，[下载地址](https://archive.apache.org/dist/hadoop/core/hadoop-2.7.3/hadoop-2.7.3.tar.gz)
2. HBase：版本1.2.4，[下载地址](http://archive.apache.org/dist/hbase/1.2.4/hbase-1.2.4-bin.tar.gz)
3. JDK8

jdk 安装命令

```bash
$ yum -y install java-devel java
```

查看当前系统jre和jdk路径，输入`update-alternatives --config java`和`update-alternatives --config javac`

```bash
$ update-alternatives --config java

共有 1 个提供“java”的程序。

  选项    命令
-----------------------------------------------
*+ 1           java-1.8.0-openjdk.x86_64 (/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64/jre/bin/java)

$ update-alternatives --config javac

共有 1 个提供“javac”的程序。

  选项    命令
-----------------------------------------------
*+ 1           java-1.8.0-openjdk.x86_64 (/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64/bin/javac)


```

查看环境

```bash
$ ll
总用量 311132
-rw-------. 1 root root      1241 8月  11 10:53 anaconda-ks.cfg
-rw-r--r--. 1 root root 214092195 8月  26 2016 hadoop-2.7.3.tar.gz
-rw-r--r--. 1 root root 104497899 10月 26 2016 hbase-1.2.4-bin.tar.gz
$ java -version
openjdk version "1.8.0_191"
OpenJDK Runtime Environment (build 1.8.0_191-b12)
OpenJDK 64-Bit Server VM (build 25.191-b12, mixed mode)
$ javac -version
javac 1.8.0_191
```

### 免密登录

新建hadoop用户，忽略密码强度提示

```bash
$ adduser hadoop
$ passwd hadoop
```

为方便远程连接和学习，同时授予root权限，输入`whereis sudoers`查看权限控制文件位置

```bash
$ whereis sudoers
sudoers: /etc/sudoers /etc/sudoers.d /usr/libexec/sudoers.so /usr/share/man/man5/sudoers.5.gz
```
`vi /etc/sudoers`修改内容为

```
root    ALL=(ALL)       ALL
hadoop  ALL=(ALL)       ALL
```

切换至`hadoop`用户，使用 `ssh-keygen -t rsa`生成私钥信息，位置在`/home/hadoop/`，并且忽略所有提示输入的信息

查看生成的文件，该SSH文件夹为隐藏文件夹，故用`ls -a`查看，可见自动生成了`.ssh`目录和`id_rsa`,`id_rsa.pub`两个文件

```bash
$ ls /home/hadoop/.ssh/
id_rsa  id_rsa.pub
```

复制公钥到.ssh目录

```bash
$ cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys
```

免密测试

```bash
$ ssh localhost
The authenticity of host 'localhost (::1)' can't be established.
ECDSA key fingerprint is SHA256:3UEr3lx2jznmN3FL3SflViR05IZe6AWweb3TeSsfX0M.
ECDSA key fingerprint is MD5:0f:31:c1:cc:54:69:7f:d8:8d:7c:8c:22:95:2e:03:4e.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'localhost' (ECDSA) to the list of known hosts.
Last login: Sat Dec 15 11:14:27 2018
$ exit
登出
Connection to localhost closed.
```

### 安装Hadoop

解压文件

```bash
$ tar -zxvf hadoop-2.7.3.tar.gz
```

修改配置文件

```bash
$ vi /hadoop-2.7.3/etc/hadoop/hadoop-env.sh
```

配置Java路径

```
# The java implementation to use.
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64
```

修改HDFS配置

```bash
$ vi /hadoop-2.7.3/etc/hadoop/hdfs-site.xml
```

配置内容

```xml
<configuration>
	<property>
	    <name>dfs.replication</name>
	    <!-- 配置副本数量-->
	    <value>1</value>
	</property>
	<property>
	    <name>dfs.namenode.name.dir</name>
	    <value>file:/home/hadoop/hadoop_data/dfs/name</value>
	</property>
	<property>
	    <name>dfs.namenode.data.dir</name>
	    <value>file:/home/hadoop/hadoop_data/dfs/data</value>
	</property>
</configuration>
```

手动创建相关目录

```bash
$ mkdir -p /home/hadoop/hadoop_data/dfs/name
$ mkdir -p /home/hadoop/hadoop_data/dfs/data
```

配置`core-site.xml`，内容为

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <!-- 配置主机IP-->
        <value>hdfs://0.0.0.0:8020</value>
    </property>

    <!-- 配置临时文件位置-->
    <property>
        <name>hadoop.tmp.dir</name>
        <value>file:/home/hadoop/hadoop_data</value>
    </property>
</configuration>
```

放行端口并重载

```bash
$ firewall-cmd --zone=public --add-port=8020/tcp --add-port=50070/tcp --permanent
$ firewall-cmd --reload
```

### 启动Hadoop

#### 初始化 ###
进入`/hadoop-2.7.3/bin`目录，使用如下语句初始化Hadoop，该操作仅执行一次即可，以后使用无需重复执行，否则执行后会删除当前hadoop上的所有文件

```bash
$ hadoop namenode -format
```

滚动均为`info`级别的日志并且`status 0`表示已初始化成功

```
...
18/12/15 17:07:32 INFO namenode.FSImage: Allocated new BlockPoolId: BP-99731851-127.0.0.1-1544864852133
18/12/15 17:07:32 INFO common.Storage: Storage directory /home/hadoop/hadoop_data/dfs/name has been successfully formatted.
18/12/15 17:07:32 INFO namenode.FSImageFormatProtobuf: Saving image file /home/hadoop/hadoop_data/dfs/name/current/fsimage.ckpt_0000000000000000000 using no compression
18/12/15 17:07:32 INFO namenode.FSImageFormatProtobuf: Image file /home/hadoop/hadoop_data/dfs/name/current/fsimage.ckpt_0000000000000000000 of size 353 bytes saved in 0 seconds.
18/12/15 17:07:32 INFO namenode.NNStorageRetentionManager: Going to retain 1 images with txid >= 0
18/12/15 17:07:32 INFO util.ExitUtil: Exiting with status 0
18/12/15 17:07:32 INFO namenode.NameNode: SHUTDOWN_MSG: 
/************************************************************
SHUTDOWN_MSG: Shutting down NameNode at localhost/127.0.0.1
************************************************************/
```

#### 启动HDFS

进入`/hadoop-2.7.3/sbin`目录输入`./start-dfs.sh`启动HDFS服务

```bash
$ ./start-dfs.sh
Starting namenodes on [0.0.0.0]
The authenticity of host '0.0.0.0 (0.0.0.0)' can't be established.
ECDSA key fingerprint is SHA256:3UEr3lx2jznmN3FL3SflViR05IZe6AWweb3TeSsfX0M.
ECDSA key fingerprint is MD5:0f:31:c1:cc:54:69:7f:d8:8d:7c:8c:22:95:2e:03:4e.
Are you sure you want to continue connecting (yes/no)? yes
0.0.0.0: Warning: Permanently added '0.0.0.0' (ECDSA) to the list of known hosts.
0.0.0.0: starting namenode, logging to /home/hadoop/hadoop-2.7.3/logs/hadoop-hadoop-namenode-localhost.localdomain.out
localhost: starting datanode, logging to /home/hadoop/hadoop-2.7.3/logs/hadoop-hadoop-datanode-localhost.localdomain.out
Starting secondary namenodes [0.0.0.0]
0.0.0.0: starting secondarynamenode, logging to /home/hadoop/hadoop-2.7.3/logs/hadoop-hadoop-secondarynamenode-localhost.localdomain.out
```

进程验证，若出现如下四个进程表示HDFS服务启动成功

```bash
$ jps
28930 Jps
28821 SecondaryNameNode
28663 DataNode
28541 NameNode
```

### 配置hdfs命令 ###
使用`vi ~/.bash_profile`进入配置文件，按如下配置

```bash
export HADOOP_HOME=/home/hadoop/hadoop-2.7.3
export PATH=$HADOOP_HOME/bin:$PATH
```
使配置文件生效`source  ~/.bash_profile`
输入`hdfs`回车测试命令是否生效，若出现如下画面则表示命令已经生效

```bash
$ hdfs
Usage: hdfs [--config confdir] [--loglevel loglevel] COMMAND
       where COMMAND is one of:
  dfs                  run a filesystem command on the file systems supported in Hadoop.
  classpath            prints the classpath
  namenode -format     format the DFS filesystem
  secondarynamenode    run the DFS secondary namenode
  namenode             run the DFS namenode
  journalnode          run the DFS journalnode
  zkfc                 run the ZK Failover Co
  ...
```

#### 命令测试

```bash
$ hadoop fs -mkdir /test
$ hadoop fs -ls /
Found 1 items
drwxr-xr-x   - hadoop supergroup          0 2018-12-15 17:14 /test
```

## HBase伪分布式搭建

### HBase安装

解压安装包，目录如下

```bash
$ ll
总用量 320
drwxr-xr-x.  4 hadoop hadoop   4096 1月  29 2016 bin
-rw-r--r--.  1 hadoop hadoop 122439 10月 26 2016 CHANGES.txt
drwxr-xr-x.  2 hadoop hadoop    178 1月  29 2016 conf
drwxr-xr-x. 12 hadoop hadoop   4096 10月 26 2016 docs
drwxr-xr-x.  7 hadoop hadoop     80 10月 26 2016 hbase-webapps
-rw-rw-r--.  1 hadoop hadoop    261 10月 26 2016 LEGAL
drwxrwxr-x.  3 hadoop hadoop   8192 12月 15 11:24 lib
-rw-rw-r--.  1 hadoop hadoop 130696 10月 26 2016 LICENSE.txt
-rw-rw-r--.  1 hadoop hadoop  42025 10月 26 2016 NOTICE.txt
-rw-r--r--.  1 hadoop hadoop   1477 12月 27 2015 README.txt
```

拷贝Hadoop配置文件到`/conf`目录

```bash
$ cp /home/hadoop/hadoop-2.7.3/etc/hadoop/hdfs-site.xml .
$ cp /home/hadoop/hadoop-2.7.3/etc/hadoop/core-site.xml .
```

修改`hbase-env.sh`文件，增加JDK路径

```bash
# The java implementation to use.  Java 1.7+ required.
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64
```

由于使用的是jdk8，主要注释内存配置

```bash
# Configure PermSize. Only needed in JDK7. You can safely remove it for JDK8+
#export HBASE_MASTER_OPTS="$HBASE_MASTER_OPTS -XX:PermSize=128m -XX:MaxPermSize=128m"
#export HBASE_REGIONSERVER_OPTS="$HBASE_REGIONSERVER_OPTS -XX:PermSize=128m -XX:MaxPermSize=128m"
```

另外打开文件最后zookeeper配置，设置为使用内置的zookeeper

```bash
# Tell HBase whether it should manage it's own instance of Zookeeper or not.
export HBASE_MANAGES_ZK=true
```

修改`hbase-site.xml`文件，内容如下

```xml
<configuration>
	<property>
		<name>hbase.rootdir</name>
        <!-- 配置文件根目录-->
		<value>hdfs://localhost:8020/hbase</value>
	</property>
	<property>
		<name>hbase.zookeeper.property.dataDir</name>
		<value>/home/hadoop/hadoop_data/zookeeper</value>
	</property>
	<property>
		<name>hbase.cluster.distributed</name>
        <!-- 配置以集群方式运行-->
		<value>true</value>
	</property>
</configuration>
```

[参考文档](https://hbase.apache.org/book.html)

### 启动HBase

在`/bin`目录下执行`./start-hbase.sh`启动HBase

```bash
$ ./start-hbase.sh 
OpenJDK 64-Bit Server VM warning: If the number of processors is expected to increase from one, then you should configure the number of parallel GC threads appropriately using -XX:ParallelGCThreads=N
OpenJDK 64-Bit Server VM warning: If the number of processors is expected to increase from one, then you should configure the number of parallel GC threads appropriately using -XX:ParallelGCThreads=N
localhost: starting zookeeper, logging to /home/hadoop/hbase-1.2.4/bin/../logs/hbase-hadoop-zookeeper-localhost.localdomain.out
localhost: OpenJDK 64-Bit Server VM warning: If the number of processors is expected to increase from one, then you should configure the number of parallel GC threads appropriately using -XX:ParallelGCThreads=N
starting master, logging to /home/hadoop/hbase-1.2.4/bin/../logs/hbase-hadoop-master-localhost.localdomain.out
OpenJDK 64-Bit Server VM warning: If the number of processors is expected to increase from one, then you should configure the number of parallel GC threads appropriately using -XX:ParallelGCThreads=N
starting regionserver, logging to /home/hadoop/hbase-1.2.4/bin/../logs/hbase-hadoop-1-regionserver-localhost.localdomain.out
```

由于虚拟机只分配了单核单线程，GC警告暂时忽略

进程验证，确认启动成功

```bash
$ jps
28821 SecondaryNameNode
28663 DataNode
29911 HRegionServer
29785 HMaster
29724 HQuorumPeer
28541 NameNode
30303 Jps
```

进入HBase命令行测试

```bash
$ ./hbase shell
OpenJDK 64-Bit Server VM warning: If the number of processors is expected to increase from one, then you should configure the number of parallel GC threads appropriately using -XX:ParallelGCThreads=N
SLF4J: Class path contains multiple SLF4J bindings.
SLF4J: Found binding in [jar:file:/home/hadoop/hbase-1.2.4/lib/slf4j-log4j12-1.7.5.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: Found binding in [jar:file:/home/hadoop/hadoop-2.7.3/share/hadoop/common/lib/slf4j-log4j12-1.7.10.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
SLF4J: Actual binding is of type [org.slf4j.impl.Log4jLoggerFactory]
HBase Shell; enter 'help<RETURN>' for list of supported commands.
Type "exit<RETURN>" to leave the HBase Shell
Version 1.2.4, r67592f3d062743907f8c5ae00dbbe1ae4f69e5af, Tue Oct 25 18:10:20 CDT 2016

hbase(main):001:0> status
1 active master, 0 backup masters, 1 servers, 0 dead, 2.0000 average load

hbase(main):002:0> 
```

查看其是否自动在HDFS上创建目录`/hbase`

```bash
$ hadoop fs -ls /
Found 2 items
drwxr-xr-x   - hadoop supergroup          0 2018-12-15 18:43 /hbase
drwxr-xr-x   - hadoop supergroup          0 2018-12-15 17:14 /test
```
