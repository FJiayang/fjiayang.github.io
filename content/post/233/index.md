{
  "title": "PXC系列学习笔记（四）——搭建双机热备的MyCat集群",
  "date": "2019-12-30T08:46:37+08:00",
  "lastmod": "2019-12-30T08:46:37+08:00",
  "typecho_cid": 233,
  "url": "/archives/233/",
  "comments": false,
  "draft": false,
  "slug": "233",
  "categories": [
    "学习"
  ],
  "tags": [
    "MySQL",
    "Percona",
    "PXC",
    "MyCat",
    "HAProxy",
    "Keepalived"
  ],
  "image": "/images/recovered/de47efcb191c722de4a9.png",
  "math": false
}

## 一、介绍

目前已经搭建好了2套PXC集群，使用了单台mycat进行数据路由，在数据库层实现了高可用，但若mycat宕机，后端数据库依然无法使用，故还需要搭建多一台mycat，结合HAProxy和Keepalived实现负载均衡、双机热备。



## 二、集群架构

![image-20191227152159478](/images/recovered/5d19b9cec9176c1c4a1d.png)

## 三、搭建

服务器资源规划如下

| 名称 | IP           | CPU  | 内存 | 磁盘 | 服务                |
| ---- | ------------ | ---- | ---- | ---- | ------------------- |
| pxc3 | 192.168.1.33 | 1    | 2G   | 40G  | mycat               |
| pxc4 | 192.168.1.35 | 1    | 2G   | 40G  | haproxy、Keepalived |
| pxc5 | 192.168.1.36 | 1    | 2G   | 40G  | mycat               |
| pxc6 | 192.168.1.37 | 1    | 2G   | 40G  | haproxy、Keepalived |

### 1. 安装mycat集群

用两个虚拟机实例，各自部署`MyCat`，采用相同配置

### 2. 安装Haproxy集群

用一个虚拟机实例部署`Haproxy`

- 安装Haproxy，需要开放两个端口，3306（TCP转发），4001（监控界面）

  ```shell
  $ yum install -y haproxy
  ```

- 编辑配置文件

  ```shell
  $ vi /etc/haproxy/haproxy.cfg
  ```

  由于该节点同时也运行了PXC数据库，3306端口已经占用，故使用13306端口

  ```
  global
      log         127.0.0.1 local2
  
      chroot      /var/lib/haproxy
      pidfile     /var/run/haproxy.pid
      maxconn     4000
      user        haproxy
      group       haproxy
      daemon
  
      stats socket /var/lib/haproxy/stats
  
  defaults
      mode                    http
      log                     global
      option                  httplog
      option                  dontlognull
      option http-server-close
      option forwardfor       except 127.0.0.0/8
      option                  redispatch
      retries                 3
      timeout http-request    10s
      timeout queue           1m
      timeout connect         10s
      timeout client          1m
      timeout server          1m
      timeout http-keep-alive 10s
      timeout check           10s
      maxconn                 3000
  
  listen   admin_stats  
      bind    0.0.0.0:4001
      mode  http
      stats uri       /dbs
      stats realm  Global\ statistics
      stats auth    admin:Abc%6870
  
  listen   proxy_mysql
      bind    0.0.0.0:13306  
      mode  tcp 
      balance  roundrobin
      option  tcplog
      server   mycat_1  192.168.1.33:8066  check  port  8066 weight 1 maxconn  2000  
      server   mycat_2  192.168.1.36:8066  check  port  8066 weight 1 maxconn  2000  
      option  tcpka
  ```

- 启动Haproxy

  ```shell
  $ service haproxy start
  ```

- 访问Haproxy监控画面

  http://192.168.1.35:4001/dbs

  ![image-20191227172147428](/images/recovered/38626c060bfd45f736c9.png)
  
  用另外一个虚拟机同样按照上述操作安装`Haproxy`



### 3. 安装Keepalived集群

在某个`Haproxy`虚拟机实例上部署`Keepalived`

   - 开启防火墙的`VRRP`协议

     ```shell
     #开启VRRP
     firewall-cmd --direct --permanent --add-rule ipv4 filter INPUT 0 --protocol  vrrp -j ACCEPT
     # iptable配置
     iptables -I INPUT -p vrrp -j ACCEPT
     
     #应用设置
     firewall-cmd --reload
     ```

   - 安装Keepalived

     ```shell
     yum install -y keepalived
     ```

   - 编辑配置文件

     ```shell
     vi /etc/keepalived/keepalived.conf
     ```

     ```bash
     vrrp_instance  VI_1 {
         state  MASTER # 争抢虚拟IP，若不争抢，则设置为slave
         interface  ens192
         virtual_router_id  51 # 唯一ID，范围0-255
         priority  100 # 抢占权重
         advert_int  1 # 心跳检测间隔时间
         authentication { # 心跳检测账户和密码
             auth_type  PASS
             auth_pass  123456
         }
         virtual_ipaddress {
             192.168.1.9 # 新虚拟IP
         }
     }
     ```

   - 启动`Keepalived`

     ```shell
     $ systemctl start keepalived
     ```

   - 在两台`Keepalived`节点上`ping`虚拟IP，看是否已经创建并可以访问

     ```bash
     $ ping 192.168.1.9
     ```

2. 在另外一个`Haproxy`虚拟机上，按照上述方法部署`Keepalived`

3. 使用MySQL客户端连接`192.168.1.9`，执行增删改查数据
