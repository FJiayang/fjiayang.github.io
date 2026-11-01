{
  "title": "Jenkins 安装配置",
  "date": "2018-08-26T11:32:00+08:00",
  "lastmod": "2018-08-26T19:34:59+08:00",
  "typecho_cid": 179,
  "url": "/archives/179/",
  "comments": false,
  "draft": false,
  "slug": "179",
  "categories": [
    "开发"
  ],
  "tags": [
    "Jenkins"
  ],
  "math": false
}

# 使用Docker安装
## 基础环境
docker环境
查看docker版本
```
[root@localhost ~]# docker -v
Docker version 18.06.0-ce, build 0ffa825
```
新建用户目录，用户挂载容器存储
```
useradd jenkins-docker

```
运行docker命令
```
docker run -p 8081:8080 -p 50001:50000  -v /home/jenkins-docker:/var/jenkins_home hub.c.163.com/library/jenkins:latest
```
[![Jenkins40.png](/images/recovered/ce6a0b24ea8588369f4a.png)](/images/recovered/ce6a0b24ea8588369f4a.png)

命令中没有使用后台启动为了查看输出的管理员密码
[![Jenkins41.png](/images/recovered/3e99fd6f0d8484c3a631.png)](/images/recovered/3e99fd6f0d8484c3a631.png)

若使用了挂载目录也可以在挂载的目录下查看
[![Jenkins43.png](/images/recovered/75c05be9a5819682b2fa.png)](/images/recovered/75c05be9a5819682b2fa.png)

访问web界面，输入密码即可
[![Jenkins42.png](/images/recovered/ad9abf861ecf9e9a628b.png)](/images/recovered/ad9abf861ecf9e9a628b.png)

# 使用原生系统安装
## 基础环境
CentOS7 1804最小安装

安装基础wget工具`yum install -y wget`
[![Jenkins1.png](/images/recovered/ff745be6e29d01de49ed.png)](/images/recovered/ff745be6e29d01de49ed.png)

### 导入仓库源
```
wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins.io/redhat-stable/jenkins.repo
```
[![Jenkins2.png](/images/recovered/ac7d487972b37a4c5945.png)](/images/recovered/ac7d487972b37a4c5945.png)

下载并导入仓库的key，用于验证仓库安全性
```
rpm --import http://pkg.jenkins.io/redhat-stable/jenkins.io.key
```
### 安装java8
```
yum -y install java
```
验证java版本
```
[root@localhost ~]# java -version
openjdk version "1.8.0_181"
OpenJDK Runtime Environment (build 1.8.0_181-b13)
OpenJDK 64-Bit Server VM (build 25.181-b13, mixed mode)
```
### 关闭防火墙
```
[root@localhost ~]# systemctl stop firewalld
```
关闭防火墙开机启动
```
[root@localhost ~]# systemctl disable firewalld
Removed symlink /etc/systemd/system/multi-user.target.wants/firewalld.service.
Removed symlink /etc/systemd/system/dbus-org.fedoraproject.FirewallD1.service.
```
### 关闭强制访问控制安全策略
```
vi /etc/sysconfig/selinux
```
```
# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=enforcing
# SELINUXTYPE= can take one of three two values:
#     targeted - Targeted processes are protected,
#     minimum - Modification of targeted policy. Only selected processes are protected.
#     mls - Multi Level Security protection.
SELINUXTYPE=targeted
```
```
SELINUX=enforcing
```
改成
```
SELINUX=disabled
```
reboot使禁用操作生效

查看操作是否生效
```
[root@localhost ~]# getenforce
Disabled
```
## 安装jenkins
### 直接安装
```
yum -y install jenkins
```
[![Jenkins3.png](/images/recovered/000726f7d2b37caf2f7b.png)](/images/recovered/000726f7d2b37caf2f7b.png)
安装后会自动添加jenkins，此时可以自定义发布用户
```
[root@localhost ~]# useradd jenkins
useradd：用户“jenkins”已存在
[root@localhost ~]# useradd deploy
```
### 配置
编辑配置文件
```
[root@localhost ~]# vi /etc/sysconfig/jenkins 
```
将用户改为新建的用户`JENKINS_USER="deploy"`，端口号默认为8080
[![Jenkins4.png](/images/recovered/7be7ece92d283e3cff9f.png)](/images/recovered/7be7ece92d283e3cff9f.png)

修改log目录和权限
```
[root@localhost ~]# chown -R deploy:deploy /var/lib/jenkins
[root@localhost ~]# chown -R deploy:deploy /var/log/jenkins
[root@localhost ~]# chown -R deploy:deploy /var/cache/jenkins
```
### 启动jenkins
```
[root@localhost ~]# systemctl start jenkins
```

查看服务是否启动
```
[root@localhost ~]# ps -ef | grep jenkins
root       1445   1311  0 19:06 pts/0    00:00:00 grep --color=auto jenkins
```
或者使用lsof（需要额外安装）
```
[root@localhost jenkins]# lsof -i:8080
COMMAND  PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
java    1683 deploy  161u  IPv6  24353      0t0  TCP *:webcache (LISTEN)
```
### 访问web界面
地址为ip:8080
[![Jenkins5.png](/images/recovered/cf398b153e1b5256f105.png)](/images/recovered/cf398b153e1b5256f105.png)

去提示的目录下查找密码
[![Jenkins6.png](/images/recovered/f0cd75e6d05cc0bda1e5.png)](/images/recovered/f0cd75e6d05cc0bda1e5.png)

安装推荐配置插件
[![Jenkins7.png](/images/recovered/1600db1f07ec35bb9d97.png)](/images/recovered/1600db1f07ec35bb9d97.png)

新建管理员用户
[![Jenkins8.png](/images/recovered/d133383c5bd3ef0650f5.png)](/images/recovered/d133383c5bd3ef0650f5.png)

安装成功
[![Jenkins9.png](/images/recovered/41756cf978d17b335e36.png)](/images/recovered/41756cf978d17b335e36.png)
