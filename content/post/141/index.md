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
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cfh4e.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cfvbs.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cfPj1.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cfF40.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cu6Ht.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuIpF.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuidr.png
  [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cul30.png
  [10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuus1.png
  [11]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cueCJ.png
  [12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cfTla.png
  [13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2c6JvX.png
  [14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2c6tMj.png
  [15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2c6k6y.png
  [16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cldpc.png
  [17]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cufgM.png
  [18]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuZPT.png
  [19]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cutO6.png
  [20]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuJ3e.png
  [21]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuVUs.png
  [22]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuk67.png
  [23]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cu2uN.png
  [24]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cu1Ru.png
  [25]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuGgD.png
  [26]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cumOa.png
  [27]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cur0i.png
  [28]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cuHHv.png
