{
  "title": "OpenVZ安装BBR加速",
  "date": "2018-09-15T22:45:00+08:00",
  "lastmod": "2018-09-15T22:47:33+08:00",
  "typecho_cid": 183,
  "url": "/archives/183/",
  "comments": false,
  "draft": false,
  "slug": "183",
  "categories": [
    "服务器"
  ],
  "tags": [
    "bbr",
    "vps",
    "superbench"
  ],
  "math": false
}

## 服务器信息

### 服务商

VPS为hiformance廉价VPS，OpenVZ虚拟化方式，可以通过`virt-what`命令查询，CentOS安装命令

```bash
yum install -y virt-what
```

查询虚拟化方式

```bash
[root@iYdQ3O-server ~]# virt-what
openvz
```

### 硬件信息

- 内存：8G（连续买3年）
- CPU：2核
- 硬盘：20G SSD
- 流量：4T/月
- 带宽：1Gbps
- IPv4：1个
- 优惠价：8.99美元/年（QN网络）

另外补充一点，hiformance运营商比较迷的是，如果购买的是CN2网络，即亚洲优化网络，则有两个虚拟化同时并存的情况

```bash
[root@BYr3tC-server ~]# virt-what
openvz
lxc
```

而两种虚拟化并存就导致其既不能装OpenVZ平台的BBR加速方式，又因为不是KVM虚拟化，没有系统内核，无法通过升级内核的方式安装KVM平台的BBR加速，所以目前建议购买hiformance的还是买QN网络比较好

## 加速方式

目前（2018-09-15）OpenVZ平台上有5种可选方案

[参考链接](https://www.cokemine.com/openvzbbr.html)

### 方案简单分析

本人并没有尝试全部方案，从方案实现上大致分析下

 - UML

   其`Alpine linux` 小内存版对低内存机器较为友好，但UML是装完 ssr 和 bbr 就已经运行了，不确定SSR账号的安全性，以及安装的SSR不清楚是否是原版，故有安全隐患

 - LKL

   LKL是比较多人使用的解决方案，但亲自尝试了几次，发现并不容易安装成功，而且安装失败没有友好的报错提示

 - Rinetd

   `Rinetd`原版通过全配置文件配置，使用`Rinetd`可以不用开启服务器的`TUN/TAP`功能，更为友好，但不支持端口号段配置

 - NanQinLang

   NanQinLang有两个分支，一个是基于`Rinetd`修改版，一个是基于`haproxy`修改版，本次采用其`Rinetd`修改版，由于`haproxy`修改版虽然支持端口号段，并且加速也没问题，但存在`haproxy`经常挂掉的问题，而根据其作者在`GitHub`上的回复，换用 `rinetd` 没有这些毛病

## BBR安装

本次采用方案为NanQinLang基于`Rinetd`修改版，[官方开源地址](https://github.com/tcp-nanqinlang/wiki/wiki/lkl-rinetd)

### 系统环境

系统版本为最新版

```bash
[root@BYr3tC-server ~]# cat /etc/redhat-release
CentOS Linux release 7.5.1804 (Core)
```

### 安装

傻瓜式命令安装，中文引导

```bash
wget https://github.com/tcp-nanqinlang/lkl-rinetd/releases/download/1.1.0/tcp_nanqinlang-rinetd-centos.sh
bash tcp_nanqinlang-rinetd-centos.sh
```

安装好后可以通过配置文件增加端口，配置文件在目录`/home/tcp_nanqinlang`

```bash
[root@iYdQ3O-server ~]# cd /home/tcp_nanqinlang
[root@iYdQ3O-server tcp_nanqinlang]# ls
config-port.conf  config-rinetd.sh  nohup.out  rinetd  rinetd.1
[root@iYdQ3O-server tcp_nanqinlang]# vi config-port.conf
```

端口配置文件`config-port.conf`

```
0.0.0.0 8001 0.0.0.0 8001
0.0.0.0 8888 0.0.0.0 8888
0.0.0.0 8080 0.0.0.0 8080
0.0.0.0 8085 0.0.0.0 8085
0.0.0.0 8086 0.0.0.0 8086
0.0.0.0 8087 0.0.0.0 8087
0.0.0.0 8088 0.0.0.0 8088
0.0.0.0 8089 0.0.0.0 8089
0.0.0.0 9000 0.0.0.0 9000
```

### 速度测试

使用`superbench`进行网速测试

#### 使用前

如下可见，启用前国内的速度平均在4Mbps左右，十足的小水管，而国外基本有百兆以上的性能

[![vps4.png](https://i.loli.net/2018/09/13/5b99ebdd050a0.png)](https://i.loli.net/2018/09/13/5b99ebdd050a0.png)

#### 使用后

加速后提升明显，国内速度平均45Mbps，对于大多数家庭20M宽带来说已经稳定跑满

[![vps9.png](https://i.loli.net/2018/09/15/5b9d19a58a1b5.png)](https://i.loli.net/2018/09/15/5b9d19a58a1b5.png)
