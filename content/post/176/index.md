{
  "title": "gitlab-ce安装配置",
  "date": "2018-08-19T16:39:00+08:00",
  "lastmod": "2018-08-19T20:29:15+08:00",
  "typecho_cid": 176,
  "url": "/archives/176/",
  "comments": false,
  "draft": false,
  "slug": "176",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [],
  "math": false
}

## 系统预配置 ##
关闭防火墙

    [root@localhost ~]# systemctl stop firewalld

关闭防火墙开机启动

    [root@localhost ~]# systemctl disable firewalld
    Removed symlink /etc/systemd/system/multi-user.target.wants/firewalld.service.
    Removed symlink /etc/systemd/system/dbus-org.fedoraproject.FirewallD1.service.

关闭强制访问控制安全策略

    vi /etc/sysconfig/selinux

    # This file controls the state of SELinux on the system.
    # SELINUX= can take one of these three values:
    #     enforcing - SELinux security policy is enforced.
    #     permissive - SELinux prints warnings instead of enforcing.
    #     disabled - No SELinux policy is loaded. SELINUX=enforcing
    # SELINUXTYPE= can take one of three two values:
    #     targeted - Targeted processes are protected,
    #     minimum - Modification of targeted policy. Only selected processes are protected.
    #     mls - Multi Level Security protection. SELINUXTYPE=targeted

`SELINUX=enforcing`改成`SELINUX=disabled`

reboot使禁用操作生效

查看操作是否生效

    [root@localhost ~]# getenforce
    Disabled

## 安装Gitlab依赖 ## 

    yum install curl policycoreutils openssh-server openssh-clients postfixs

    [root@localhost ~]# yum install curl policycoreutils openssh-server openssh-clients postfixs
    已加载插件：fastestmirror
    Determining fastest mirrors
     * base: mirrors.aliyun.com
     * extras: mirrors.aliyun.com
     * updates: mirrors.aliyun.com
    base                                                                                         | 3.6 kB  00:00:00
    extras                                                                                       | 3.4 kB  00:00:00
    updates                                                                                      | 3.4 kB  00:00:00
    (1/4): base/7/x86_64/group_gz                                                                | 166 kB  00:00:00
    (2/4): extras/7/x86_64/primary_db                                                            | 174 kB  00:00:00
    (3/4): base/7/x86_64/primary_db                                                              | 5.9 MB  00:00:01
    (4/4): updates/7/x86_64/primary_db                                                           | 5.0 MB  00:00:02
    软件包 curl-7.29.0-46.el7.x86_64 已安装并且是最新版本
    软件包 policycoreutils-2.5-22.el7.x86_64 已安装并且是最新版本
    软件包 openssh-server-7.4p1-16.el7.x86_64 已安装并且是最新版本
    软件包 openssh-clients-7.4p1-16.el7.x86_64 已安装并且是最新版本
    没有可用软件包 postfixs。
    无须任何处理

下载gitlab仓库源

    curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash

[![gitlab-ce1.png](/images/recovered/e40f23554740ec90a275.png)](/images/recovered/e40f23554740ec90a275.png)

## 启动邮件服务 ## 

    [root@localhost ~]# systemctl start postfix

配置开机启动

    [root@localhost ~]# systemctl enable postfix

## 安装gitlab ## 

    yum -y install gitlab-ce

[![gitlab-ce2.png](/images/recovered/c3a4c7a22b6efcd68eef.png)](/images/recovered/c3a4c7a22b6efcd68eef.png)
## 配置SSL证书 ##

    mkdir -p /etc/gitlab/ssl

### 创建本地私有秘钥 ### 

    [root@localhost ~]# openssl genrsa -out "/etc/gitlab/ssl/gitlab.fjy8018.top.key" 2048
    Generating RSA private key, 2048 bit long modulus
    ..................................................+++
    ......................+++
    e is 65537 (0x10001)

### 创建CSR证书 ### 

    [root@localhost ~]# openssl req -new -key "/etc/gitlab/ssl/gitlab.fjy8018.top.key" -out "/etc/gitlab/ssl/gitlab.fjy8018.top.csr"
    You are about to be asked to enter information that will be incorporated
    into your certificate request.
    What you are about to enter is what is called a Distinguished Name or a DN.
    There are quite a few fields but you can leave some blank
    For some fields there will be a default value,
    If you enter '.', the field will be left blank.
    -----
    Country Name (2 letter code) [XX]:cn
    State or Province Name (full name) []:gd
    Locality Name (eg, city) [Default City]:gz
    Organization Name (eg, company) [Default Company Ltd]:
    Organizational Unit Name (eg, section) []:
    Common Name (eg, your name or your server's hostname) []:gitlab.fjy8018.top
    Email Address []:admin@example.com
    
    Please enter the following 'extra' attributes
    to be sent with your certificate request
    A challenge password []:12345678
    An optional company name []:

查看证书是否成功创建

    [root@localhost ~]# cd /etc/gitlab/ssl
    [root@localhost ssl]# ll
    总用量 8
    -rw-r--r-- 1 root root 1070 8月  18 11:11 gitlab.fjy8018.top.csr
    -rw-r--r-- 1 root root 1675 8月  18 11:08 gitlab.fjy8018.top.key

### 创建签署证书 ### 
利用秘钥和csr证书创建签署证书
X.509为证书格式 365为有效期

    [root@localhost ssl]# openssl x509 -req -days 365 -in "/etc/gitlab/ssl/gitlab.fjy8018.top.csr" -signkey "/etc/gitlab/ssl/gitlab.fjy8018.top.key" -out "/etc/gitlab/ssl/gitlab.fjy8018.top.crt"
    Signature ok
    subject=/C=cn/ST=gd/L=gz/O= /OU= /CN=gitlab.fjy8018.top/emailAddress=admin@example.com
    Getting Private key

查看证书目录

    [root@localhost ssl]# ll
    总用量 12
    -rw-r--r-- 1 root root 1265 8月  18 11:14 gitlab.fjy8018.top.crt
    -rw-r--r-- 1 root root 1070 8月  18 11:11 gitlab.fjy8018.top.csr
    -rw-r--r-- 1 root root 1675 8月  18 11:08 gitlab.fjy8018.top.key

### 输出pem证书 ### 

    openssl dhparam -out /etc/gitlab/ssl/dhparams.pem 2048
[![gitlab-ce3.png](/images/recovered/3230f49ec2f010e5511b.png)](/images/recovered/3230f49ec2f010e5511b.png)

    [root@localhost ssl]# ll
    总用量 16
    -rw-r--r-- 1 root root  424 8月  18 11:17 dhparams.pem
    -rw-r--r-- 1 root root 1265 8月  18 11:14 gitlab.fjy8018.top.crt
    -rw-r--r-- 1 root root 1070 8月  18 11:11 gitlab.fjy8018.top.csr
    -rw-r--r-- 1 root root 1675 8月  18 11:08 gitlab.fjy8018.top.key

证书创建完成
修改证书权限

    [root@localhost ssl]# chmod 700 *

查看权限

    [root@localhost ssl]# ll
    总用量 16
    -rw------- 1 root root  424 8月  18 11:17 dhparams.pem
    -rw------- 1 root root 1265 8月  18 11:14 gitlab.fjy8018.top.crt
    -rw------- 1 root root 1070 8月  18 11:11 gitlab.fjy8018.top.csr
    -rw------- 1 root root 1675 8月  18 11:08 gitlab.fjy8018.top.key

### 配置gitlab证书文件 ### 

    vi /etc/gitlab/gitlab.rb

修改external_url为https的域名

    external_url 'https://gitlab.fjy8018.top'

检索重定向配置，启用重定向
[![gitlab-ce4.png](/images/recovered/3915f8c9ed0f3461e5ea.png)](/images/recovered/3915f8c9ed0f3461e5ea.png)

    # nginx['client_max_body_size'] = '250m'
      nginx['redirect_http_to_https'] = true
    # nginx['redirect_http_to_https_port'] = 80

修改下方crt配置
原始为`# nginx['ssl_certificate'] = "/etc/gitlab/ssl/#{node['fqdn']}.crt"`
修改为`nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.fjy8018.top.crt"`
key、ssl_dhparam同样配置

    nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.fjy8018.top.key"
    nginx['ssl_dhparam'] = "/etc/gitlab/ssl/dhparams.pem" # Path to dhparams.pem, eg. /etc/gitlab/ssl/dhparams.pem

初始化配置文件

    gitlab-ctl reconfigure

[![gitlab-ce5.png](/images/recovered/85479ac3efc37c88d235.png)](/images/recovered/85479ac3efc37c88d235.png)
修改gitlab的nginx配置文件

    vi /var/opt/gitlab/nginx/conf/gitlab-http.conf

搜索server_name

     server_name gitlab.fjy8018.top;

并在下方添加重定向HTTP请求

     rewrite ^(.*)$ https://$hosst1 permanent;

使nginx配置生效

    [root@localhost ssl]# gitlab-ctl restart

所有服务启动成功
[![gitlab-ce6.png](/images/recovered/1563f85f12a0d28dea0b.png)](/images/recovered/1563f85f12a0d28dea0b.png)

访问成功
[![gitlab-ce7.png](/images/recovered/5c5dbd3c2f4390a845d5.png)](/images/recovered/5c5dbd3c2f4390a845d5.png)
