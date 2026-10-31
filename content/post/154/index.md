{
  "title": "elasticsearch分布式环境搭建和插件安装",
  "date": "2018-05-17T18:01:00+08:00",
  "lastmod": "2023-09-07T14:52:43+08:00",
  "typecho_cid": 154,
  "url": "/archives/154/",
  "comments": false,
  "draft": false,
  "slug": "154",
  "categories": [
    "开发"
  ],
  "tags": [
    "分布式",
    "elasticsearch",
    "全文搜索"
  ],
  "math": true
}

## 环境搭建 ##
### 安装包和插件下载 ###
#### 下载elasticsearch ####
通过官网下载`elasticsearch`
[官网下载页面][1]
此处下载的为`elasticsearch-6.2.4.tar.gz`
#### 下载elasticsearch-head插件 ####
下载elasticsearch-head插件可以在浏览器中以图形化的方式显示下载elasticsearch中的数据
[GitHub下载页面][2]

#### 安装node环境 ####
elasticsearch-head插件依赖node环境来启动，可以通过官方node.js安装包安装，也可以通过宝塔自带的PM2管理器安装，此处安装宝塔的PM2管理器
![请输入图片描述](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2a5GKN.png)

安装后检查当前环境中的node版本，若装好后node命令无法使用可以尝试重启服务器或者让配置环境变量生效
```bash
    [root@localhost elasticsearch]# node -v
    v8.11.2
```
将两个下载好的文件用宝塔上传到CentOS 7环境中并解压
![请输入图片描述](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2a5mJj.png)

## 单节点环境配置 ##
### elasticsearch单节点配置 ###
配置文件目录为`elasticsearch-6.2.4/config`
修改`elasticsearch.yml`
```yaml
    #虚拟机IP
    network.host: 192.168.79.138
    #es端口
    http.port: 9200
    
    #防止跨源请求阻塞
    http.cors.enabled: true
    http.cors.allow-origin: "*"
    
    #主节点名称
    cluster.name: Fjiayang
    #节点名称
    node.name: master
    #是否为主节点
    node.master: true
```
若虚拟机或者服务器内存较小，则还要配置`jvm.options`，将默认1g内存设置为512m或者更小
```
    -Xms512m
    -Xmx512m
```
### elasticsearch-head插件安装 ###
进入`elasticsearch-head`安装目录，执行node的安装命令
```bash
    [root@localhost elasticsearch]# cd elasticsearch-head-master
    [root@localhost elasticsearch-head-master]# npm install
```
## 集群环境配置 ##
集群环境只需要解压多份es压缩包，并按如下对`elasticsearch.yml`配置文件进行简单配置即可，此处搭建了一个主节点，两个从节点
从节点1
```yaml
    #子节点IP
    network.host: 192.168.79.138
    #子节点端口
    http.port: 8200
    #主节点IP
    discovery.zen.ping.unicast.hosts: ["192.168.79.138"]
    #主节点名称
    cluster.name: Fjiayang
    #子节点名称
    node.name: slave1
```

从节点2
```yaml
    #子节点IP
    network.host: 192.168.79.138
    #子节点端口
    http.port: 8300
    #主节点IP
    discovery.zen.ping.unicast.hosts: ["192.168.79.138"]
    #主节点名称
    cluster.name: Fjiayang
    #子节点名称
    node.name: slave2
```

## 服务启动 ##
### elasticsearch启动 ###
elasticsearch默认不支持root用户启动，故要新建用户并对运行目录授予权限才能启动es
```bash
    [root@localhost elasticsearch]# adduser es
    [root@localhost elasticsearch]# passwd es
    更改用户 es 的密码 。
    新的 密码：
    无效的密码： 密码未通过字典检查 - 过于简单化/系统化
    重新输入新的 密码：
    passwd：所有的身份验证令牌已经成功更新。
```
在root用户下对es目录所有权进行更改
```bash
    [root@localhost www]# chown -R es /www/elasticsearch
    [root@localhost www]# ll
    总用量 4
    drwxrwxrwx   5 es   www   151 5月  16 21:10 elasticsearch
    drwxr-xr-x   6 root root 4096 5月   7 09:01 Recycle_bin
    drwxr-xr-x. 14 root root  179 5月   7 09:20 server
    drwxrwxrwx.  3 root root  116 5月   6 15:41 wwwlogs
    drwxr-xr-x.  4 root root   38 5月   6 15:41 wwwroot
```
切换到新建的用户es，用`/bin/elasticsearch`启动es服务，若加上`-d`则为后台启动，即`/bin/elasticsearch -d`
```bash
    [root@localhost www]# su es
    [es@localhost elasticsearch]$ cd elasticsearch/elasticsearch-6.2.4
    [es@localhost elasticsearch-6.2.4]$ ls
    bin  config  data  hs_err_pid4546.log  lib  LICENSE.txt  logs  modules  NOTICE.txt  plugins  README.textile
    [es@localhost elasticsearch-6.2.4]$ ./bin/elasticsearch -d
```
如果配置了集群则继续对每个从节点逐一启动即可

### elasticsearch-head插件启动 ###
进入`elasticsearch-head`目录，使用`npm run start`启动node服务即可
![请输入图片描述](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2a514c.png)

## 服务检验 ##
首先使用宝塔开放相关防火墙端口，

![请输入图片描述](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2a54bK.png)

直接访问es服务，浏览器默认显示为原生json格式，此处使用chrome浏览器的`JSON viewer`进行了美化
![请输入图片描述](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2a5Mf6.png)

访问elasticsearch-head插件，此处截图为配置好集群后的截图
![请输入图片描述](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2a5OAT.png)

elasticsearch环境搭建完成！


  [1]: http://www.elastic.co/downloads/elasticsearch
  [2]: https://github.com/mobz/elasticsearch-head
