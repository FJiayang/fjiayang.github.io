{
  "title": "HDFS伪分布式单节点搭建",
  "date": "2018-04-07T13:01:00+08:00",
  "lastmod": "2023-09-07T14:58:37+08:00",
  "typecho_cid": 141,
  "url": "/archives/141/",
  "comments": false,
  "draft": false,
  "slug": "141",
  "categories": [
    "默认分类",
    "开发"
  ],
  "tags": [
    "hadoop"
  ],
  "math": true
}

## 环境 ##
系统：CentOS Linux 7.4.1708 (Core)
客户端：putty
服务器：虚拟机1core、2G RAM
同时搭建了宝塔面板（自动配置了java8）
## Hadoop下载 ##
[CDH版本Hadoop下载][1]

为了统一版本，全部使用`hadoop-2.6.0-cdh5.7.0`
![请输入图片描述][2]

点击可进入官方推荐配置页
![请输入图片描述][3]

## 解压并配置 ##
将下载好的文件通过宝塔上传到服务器，这里选择上传到`/www/hadoop`目录
![请输入图片描述][4]

解压tar包
![请输入图片描述][5]

### 配置 ###
#### 新建用户 ####
新建hadoop用户，忽略密码强度提示
```bash
    adduser hadoop
    passwd hadoop
```
![请输入图片描述][6]

为方便远程连接和学习，同时授予root权限，输入`whereis sudoers`查看权限控制文件位置
```bash
    [root@fjy ~]# whereis sudoers
    sudoers: /etc/sudoers /etc/sudoers.d /usr/libexec/sudoers.so /usr/share/man/man5/sudoers.5.gz
```
使用宝塔找到并修改/etc/sudoers文件
![请输入图片描述][7]

![请输入图片描述][8]

#### 配置新用户免密码远程登录 ####
切换至`hadoop`用户，使用 `ssh-keygen -t rsa`生成私钥信息，位置在`/home/hadoop/`，并且忽略所有提示输入的信息
![请输入图片描述][9]

查看生成的文件，该SSH文件夹为隐藏文件夹，故用`ls -a`查看，可见自动生成了`.ssh`目录和`id_rsa`,`id_rsa.pub`两个文件
![请输入图片描述][10]

复制公钥到.ssh目录
```bash
    cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys
```
![请输入图片描述][11]

#### 查看JAVA目录 ####
因为是宝塔自动配置的java8，所以要首先查看当前java环境变量位置，使用如下命令
```bash
     update-alternatives --config java
```
![请输入图片描述][12]

此时宝塔自动将java配置到`/usr/java/jdk1.8.0_121/jre/bin/java`目录
即`/usr/java/jdk1.8.0_121`为java环境变量的目录

#### 配置hadoop的java目录 ####
使用宝塔进入hadoop目录下的`etc/hadoop/hadoop-env.sh`，对应此处的绝对路径应为`/www/hadoop/hadoop-2.6.0-cdh5.7.0/etc/hadoop`
使用宝塔编辑文件，加入java环境变量位置
![请输入图片描述][13]

![请输入图片描述][14]

#### 配置分布式文件参数 ####
打开`core-site.xml`，配置如下
```xml
    <configuration>
        <property>
            <name>fs.defaultFS</name>
            <!-- 配置主机IP-->
            <value>hdfs://192.168.79.129:8020</value>
        </property>
    
        <!-- 配置临时文件位置-->
        <property>
            <name>hadoop.tmp.dir</name>
            <value>/www/hadoop/tmp</value>
        </property>
    </configuration>
```
![请输入图片描述][15]

打开`hdfs-site.xml`，配置如下
```xml
    <configuration>
        <property>
            <name>dfs.replication</name>
            <!-- 配置副本数量-->
            <value>1</value>
        </property>
    </configuration>
```
![请输入图片描述][16]

## 启动 ##
### 初始化 ###
进入`/www/hadoop/hadoop-2.6.0-cdh5.7.0/bin`目录，使用如下语句初始化Hadoop，该操作仅执行一次即可，以后使用无需重复执行，否则执行后会删除当前hadoop上的所有文件
```bash
    hadoop namenode -format
```
![请输入图片描述][17]

滚动均为`info`级别的日志
![请输入图片描述][18]

可看到已初始化成功
![请输入图片描述][19]

### 启动HDFS ###
切换到hadoop用户，进入`/www/hadoop/hadoop-2.6.0-cdh5.7.0/sbin`目录
![请输入图片描述][20]

输入`./start-dfs.sh`启动HDFS服务
![请输入图片描述][21]


**【注意】，要提前在root用户下对`/www/hadoop`授予hadoop用户读写权限，否则无法启动**
![请输入图片描述][22]

使用`jps`查看当前的java进程，若出现如下四个进程表示HDFS服务启动成功

![请输入图片描述][23]

### 外部访问浏览器客户端 ###
首先使用宝塔开放50070端口
![请输入图片描述][24]

使用外部浏览器访问ip:50070可查看如下页面，则表示HDFS已成功启动
![请输入图片描述][25]

## hdfs命令 ##
### 配置hdfs命令 ###
使用`vi ~/.bash_profile`进入配置文件，按如下配置
```bash
    export HADOOP_HOME=/www/hadoop/hadoop-2.6.0-cdh5.7.0
    export PATH=$HADOOP_HOME/bin:$PATH
```
使配置文件生效`source  ~/.bash_profile`
输入`hdfs`回车测试命令是否生效，若出现如下画面则表示命令已经生效
![请输入图片描述][26]

### 命令测试 ###
先在本地创建`hello.txt`文件，使用` hadoop fs -put hello.txt /`命令将文件推送到hdfs根目录下
![请输入图片描述][27]

查看服务器根目录`hadoop fs -ls /`，已经有该文件，hadoop伪分布式配置完成
![请输入图片描述][28]


  [1]: http://archive.cloudera.com/cdh5/cdh/5/
  [2]: /images/recovered/f5de2ada002d8dec85d7.png
  [3]: /images/recovered/89bf745beee819f7ce0d.png
  [4]: /images/recovered/ead0890a13f3964ce712.png
  [5]: /images/recovered/756a3f03aafd1bbfe0aa.png
  [6]: /images/recovered/b2ca820410019d9a8f25.png
  [7]: /images/recovered/a20954bd5bc91ae81978.png
  [8]: /images/recovered/0e30f9421a064b51ae09.png
  [9]: /images/recovered/a400caac8bd822fdc12f.png
  [10]: /images/recovered/186baa7a5df3958fda7c.png
  [11]: /images/recovered/caa8ab27f75027b22477.png
  [12]: /images/recovered/7c07421ec0bd647d1bbb.png
  [13]: /images/recovered/078b972320540cba4f7b.png
  [14]: /images/recovered/8ae76a823edf8746de22.png
  [15]: /images/recovered/ab49bce316237f2be130.png
  [16]: /images/recovered/9827aff2904f27363117.png
  [17]: /images/recovered/41f1d7b6f77a2e05ea46.png
  [18]: /images/recovered/0c4512a9270377ba8457.png
  [19]: /images/recovered/ac4f8b222429b5262fd8.png
  [20]: /images/recovered/9b872b6c57dc823fa858.png
  [21]: /images/recovered/20c8a20731e342ef0d79.png
  [22]: /images/recovered/0ea1de23b35547ad2102.png
  [23]: /images/recovered/6d69cc1065110789a6e9.png
  [24]: /images/recovered/bf8265eedd9e34e8b254.png
  [25]: /images/recovered/3a9580ba44418cf190d6.png
  [26]: /images/recovered/d2d8c5b34b10d6de4d42.png
  [27]: /images/recovered/cfc12db82f216981e16e.png
  [28]: /images/recovered/69f1fea002d2c4c36ac6.png
