{
  "title": "从零开始部署Rancher",
  "date": "2018-08-11T11:41:00+08:00",
  "lastmod": "2018-08-11T19:41:16+08:00",
  "typecho_cid": 174,
  "url": "/archives/174/",
  "comments": false,
  "draft": false,
  "slug": "174",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "CentOS",
    "docker",
    "Rancher"
  ],
  "math": false
}

## 基础环境部署 ##
基础环境使用CentOS 7，版本号为1804，部署在本地虚拟机VM上

### 安装CentOS+docker ###
[CentOS下载地址][1]

使用最小安装，ISO镜像大小为906MB，在VM中导入镜像，给4G内存（Rancher2.0最低要求），安装过程系统配置均为默认配置

安装好后为纯净环境，使用`ip addr`即可查看ip，使用外部远程连接工具连接虚拟机ip
![rancher1.png](https://i.loli.net/2018/08/11/5b6ec998439f2.png)

使用`yum install docker`安装docker环境
![rancher2.png](https://i.loli.net/2018/08/11/5b6ec9984435d.png)

安装好后使用命令`systemctl start docker`启动docker
使用` docker info`或者`docker version`查看版本

    [root@localhost ~]# docker version
    Client:
     Version:         1.13.1
     API version:     1.26
     Package version: docker-1.13.1-68.gitdded712.el7.centos.x86_64
     Go version:      go1.9.4
     Git commit:      dded712/1.13.1
     Built:           Tue Jul 17 18:34:48 2018
     OS/Arch:         linux/amd64
    
    Server:
     Version:         1.13.1
     API version:     1.26 (minimum version 1.12)
     Package version: docker-1.13.1-68.gitdded712.el7.centos.x86_64
     Go version:      go1.9.4
     Git commit:      dded712/1.13.1
     Built:           Tue Jul 17 18:34:48 2018
     OS/Arch:         linux/amd64
     Experimental:    false

### 安装Rancher ###
为了加速Rancher下载速度，需要配置docker镜像下载地址，此处提供一个阿里云的镜像地址

    {
      "registry-mirrors": ["https://fy707np5.mirror.aliyuncs.com"]
    }

使用命令编辑docker镜像地址` vi /etc/docker/daemon.json`
保存后重载配置`systemctl daemon-reload`
重启docker服务`systemctl restart docker`
镜像地址配置完成

访问Rancher官网查看docker命令
[Rancher英文官网][4]

[Rancher中文官网][5]

访问quickstart查看docker命令

目前Rancher官方开始推荐2.0版本，首次使用推荐使用1.6稳定版
![rancher3.png](https://i.loli.net/2018/08/11/5b6ec99849aaa.png)

在下方找到1.6文档，使用命令在虚拟机中安装Rancher1.6
![rancher4.png](https://i.loli.net/2018/08/11/5b6ec998470c0.png)

![rancher5.png](https://i.loli.net/2018/08/11/5b6ec9984c5c3.png)

    sudo docker run -d --restart=unless-stopped -p 8080:8080 rancher/server:stable

![rancher6.png](https://i.loli.net/2018/08/11/5b6ec998464fd.png)

### 配置防火墙 ###
安装后若没有打开8080端口则会报错，配置CentOS防火墙
来源：[莫小安-CentOS7使用firewalld打开关闭防火墙与端口][10]
>1、firewalld的基本使用
>启动： systemctl start firewalld
>关闭： systemctl stop firewalld
>查看状态： systemctl status firewalld 
>开机禁用  ： systemctl disable firewalld
>开机启用  ： systemctl enable firewalld
![rancher7.png](https://i.loli.net/2018/08/11/5b6ec99845fbf.png)

>2.systemctl是CentOS7的服务管理工具中主要的工具，它融合之前service和chkconfig的功能于一体。
>启动一个服务：systemctl start firewalld.service
>关闭一个服务：systemctl stop firewalld.service
>重启一个服务：systemctl restart firewalld.service
>显示一个服务的状态：systemctl status firewalld.service
>在开机时启用一个服务：systemctl enable firewalld.service
>在开机时禁用一个服务：systemctl disable firewalld.service
>查看服务是否开机启动：systemctl is-enabled firewalld.service
>查看已启动的服务列表：systemctl list-unit-files|grep enabled
>查看启动失败的服务列表：systemctl --failed
>
>3.配置firewalld-cmd
>
>查看版本： firewall-cmd --version
>查看帮助： firewall-cmd --help
>显示状态： firewall-cmd --state
>查看所有打开的端口： firewall-cmd --zone=public --list-ports
>更新防火墙规则： firewall-cmd --reload
>查看区域信息:  firewall-cmd --get-active-zones
>查看指定接口所属区域： firewall-cmd --get-zone-of-interface=eth0
>拒绝所有包：firewall-cmd --panic-on
>取消拒绝状态： firewall-cmd --panic-off
>查看是否拒绝： firewall-cmd --query-panic
> 
>那怎么开启一个端口呢
>添加
>firewall-cmd --zone=public --add-port=80/tcp --permanent    （--permanent永久生效，没有此参数重启后失效）
>重新载入
>firewall-cmd --reload
>查看
>firewall-cmd --zone= public --query-port=80/tcp
>删除
>firewall-cmd --zone= public --remove-port=80/tcp --permanent

通过命令放行8080端口

    firewall-cmd --zone=public --add-port=8080/tcp --permanent

![rancher8.png](https://i.loli.net/2018/08/11/5b6ec968aa407.png)

重载防火墙

    firewall-cmd --reload

查看端口放行情况

     firewall-cmd --zone=public --list-ports

![rancher9.png](https://i.loli.net/2018/08/11/5b6ec968b1579.png)

## 设置Rancher ##
### 设置Rancher界面语言 ###
通过虚拟机ip+端口号访问Rancher：`http://192.168.79.142:8080`
![rancher10.png](https://i.loli.net/2018/08/11/5b6ec968b93b4.png)

默认为英文界面，Rancher官方有中文支持
修改右下方语言选项即可
![rancher11.png](https://i.loli.net/2018/08/11/5b6ec968ba0d8.png)

![rancher12.png](https://i.loli.net/2018/08/11/5b6ec968b5a50.png)

### 设置Rancher主机 ###
首次访问需要设置主机
![rancher13.png](https://i.loli.net/2018/08/11/5b6ec968b61be.png)

按照默认识别的IP即可，点击保存
![rancher14.png](https://i.loli.net/2018/08/11/5b6ec968b66c3.png)

选择主机类型，包含自定义主机、亚马逊主机等，此处选择自定义主机
![rancher15.png](https://i.loli.net/2018/08/11/5b6ec968b99b7.png)

依照指示操作，为了确保通信测试，暂时关闭防火墙
![rancher16.png](https://i.loli.net/2018/08/11/5b6ec968b76b2.png)

为了测试多台Rancher Server和agent服务，使用VM保存快照并复制一份虚拟机启动
目前测试：128为server，129为agent，注意此处填的是客户端的地址，非主机地址
![rancher26.png](https://i.loli.net/2018/08/11/5b6ec7c4c89c0.png)

### 设置Rancher客户端 ###
复制Server的配置命令，在agent服务器上运行，等待下载
![rancher19.png](https://i.loli.net/2018/08/11/5b6ec7c4c36aa.png)

![rancher20.png](https://i.loli.net/2018/08/11/5b6ec7c4c47a2.png)

![rancher21.png](https://i.loli.net/2018/08/11/5b6ec7c4c1a63.png)


按照指示，运行后关闭Server主机配置
查看主机列表
![rancher22.png](https://i.loli.net/2018/08/11/5b6ec7c4c28e2.png)

![rancher23.png](https://i.loli.net/2018/08/11/5b6ec7c4bd914.png)

也可以添加环境、测试环境、生产环境等
![rancher24.png](https://i.loli.net/2018/08/11/5b6ec7c4bdb11.png)

![rancher25.png](https://i.loli.net/2018/08/11/5b6ec968b71ce.png)


  [1]: http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1804.iso
  [4]: https://rancher.com/
  [5]: https://www.cnrancher.com/
