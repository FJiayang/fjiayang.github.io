{
  "title": "Jenkins 与Maven集成",
  "date": "2018-08-26T17:15:00+08:00",
  "lastmod": "2018-08-26T19:30:48+08:00",
  "typecho_cid": 180,
  "url": "/archives/180/",
  "comments": false,
  "draft": false,
  "slug": "180",
  "categories": [
    "开发"
  ],
  "tags": [
    "Jenkins",
    "Maven"
  ],
  "math": false
}

## 环境准备
### 安装jdk
```
yum -y install java-devel java
```
检测安装结果
```
[root@localhost maven-freestyle-job]# javac -version
javac 1.8.0_181
[root@localhost maven-freestyle-job]# java -version
openjdk version "1.8.0_181"
OpenJDK Runtime Environment (build 1.8.0_181-b13)
OpenJDK 64-Bit Server VM (build 25.181-b13, mixed mode)
```
### 安装maven环境
```
wget http://apache.osuosl.org/maven/maven-3/3.5.4/binaries/apache-maven-3.5.4-bin.tar.gz
```
解压，并指定解压路径
```
tar -zxvf apache-maven-3.5.4-bin.tar.gz -C /opt
```
查看安装结果

```
[root@localhost ~]# cd /opt/
[root@localhost opt]# cd apache-maven-3.5.4/
[root@localhost apache-maven-3.5.4]# cd bin/
[root@localhost bin]# ./mvn -v
Apache Maven 3.5.4 (1edded0938998edf8bf061f1ceb3cfdeccf443fe; 2018-06-18T02:33:14+08:00)
Maven home: /opt/apache-maven-3.5.4
Java version: 1.8.0_181, vendor: Oracle Corporation, runtime: /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.181-3.b13.el7_5.x86_64/jre
Default locale: zh_CN, platform encoding: UTF-8
OS name: "linux", version: "3.10.0-862.el7.x86_64", arch: "amd64", family: "unix"
[root@localhost bin]# pwd
/opt/apache-maven-3.5.4/bin
```
[![Jenkins49.png](/images/recovered/649401dfd001cb9b488f.png)](/images/recovered/649401dfd001cb9b488f.png)

## 配置环境
进入Jenkins系统管理中的全局工具配置，配置本地的maven地址
[![Jenkins54.png](/images/recovered/1f5c43740949f682b6cd.png)](/images/recovered/1f5c43740949f682b6cd.png)

此处的jdk报错正常，若不配置则会自动调用系统环境里的jdk
[![Jenkins55.png](/images/recovered/40e3b3bb23e880170ec4.png)](/images/recovered/40e3b3bb23e880170ec4.png)

指定maven名称和路径
[![Jenkins56.png](/images/recovered/299a186150fc9be27ac2.png)](/images/recovered/299a186150fc9be27ac2.png)

## 准备maven工程
提前在gitlab中装备一个简单的Springboot web工程，通过springboot脚手架快速生成，`pom`文件如下
[![Jenkins50.png](/images/recovered/ffaa3c14852ab9aa78cb.png)](/images/recovered/ffaa3c14852ab9aa78cb.png)

### 新建构建
新建构建并填写目标仓库地址
[![Jenkins51.png](/images/recovered/54177efb633d29481f2c.png)](/images/recovered/54177efb633d29481f2c.png)

添加构建设置为maven构建
[![Jenkins52.png](/images/recovered/7870b80cd3b59bd96d4f.png)](/images/recovered/7870b80cd3b59bd96d4f.png)

添加构建参数，即在命令行`mvn`之后的参数
[![Jenkins53.png](/images/recovered/e183a1082a7571c8eebc.png)](/images/recovered/e183a1082a7571c8eebc.png)

选择maven版本
[![Jenkins57.png](/images/recovered/a86687a061e41b13cc8e.png)](/images/recovered/a86687a061e41b13cc8e.png)

### 构建
构建成功
[![Jenkins58.png](/images/recovered/fdfacc8629f35bc8738c.png)](/images/recovered/fdfacc8629f35bc8738c.png)
