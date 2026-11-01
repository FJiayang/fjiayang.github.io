{
  "title": "GitLab跨版本升级",
  "date": "2018-06-12T21:50:00+08:00",
  "lastmod": "2023-09-07T17:07:47+08:00",
  "typecho_cid": 159,
  "url": "/archives/159/",
  "comments": false,
  "draft": false,
  "slug": "159",
  "categories": [
    "服务器"
  ],
  "tags": [
    "GitLab"
  ],
  "math": true
}

## 当前版本 ##
当前GitLab版本由宝塔自动安装的8.8.5,但截止至2018-06-12,CentOS的GitLab官方最新版本为10.8.4,显然版本相差较大,故打算跨版本升级至最新版
![请输入图片描述][1]

## 步骤 ##
### 升级指南 ###
GitLab社区版不支持直接跨版本升级，需按照[官方指南][2]一步步向上升级，若版本越旧，需要跨的版本就越多
![请输入图片描述][3]

### 下载相关安装包 ###
安装包国内选择[清华镜像站][4]速度较快，教育网还有蜜汁加成

![请输入图片描述][5]

若升级其他版本也可自行`Ctrl+F`
![请输入图片描述][6]

    wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-8.17.7-ce.0.el7.x86_64.rpm
    wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-9.5.8-ce.0.el7.x86_64.rpm
    wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-10.1.4-ce.0.el7.x86_64.rpm
    wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-10.8.4-ce.0.el7.x86_64.rpm

![请输入图片描述][7]


### 升级 ###
关闭GitLab核心服务

    gitlab-ctl stop unicorn
    gitlab-ctl stop sidekiq
    gitlab-ctl stop nginx

![请输入图片描述][8]

安装8.17.7

    rpm -Uvh gitlab-ce-8.17.7-ce.0.el7.x86_64.rpm

![请输入图片描述][9]

### 重启服务 ###
若之前从宝塔安装后未配置GitLab的Nginx启动命令则需要自行配置后才能正常启动，操作见文章[GitLab修改配置后nginx无法启动][10]
重启服务

    [root@localhost ~]# gitlab-ctl restart
    /opt/gitlab/embedded/lib/ruby/gems/2.3.0/gems/omnibus-ctl-0.3.6/lib/omnibus-ctl.rb:533: warning: Insecure world writable dir /www/server/nvm/versions/node/v8.11.2/bin in PATH, mode 040777
    ok: run: gitlab-workhorse: (pid 39809) 1s
    ok: run: logrotate: (pid 39821) 0s
    ok: run: nginx: (pid 39828) 0s
    ok: run: postgresql: (pid 39835) 0s
    ok: run: redis: (pid 39844) 0s
    ok: run: sidekiq: (pid 39849) 1s
    ok: run: unicorn: (pid 39854) 0s

重启后稍等片刻即可访问，查看版本号，已经更新为8.17.7，后续步骤同上
![请输入图片描述][11]

### 可能的报错 ###
部分CentOS版本较低未自带`policycoreutils-python`组件可能无法升级至10.x,需要手动

    yum -y install policycoreutils-python

### 完成 ###
![请输入图片描述][12]

更新到10.x后明显启动项都变多了
    [root@localhost ~]# gitlab-ctl restart
    /opt/gitlab/embedded/lib/ruby/gems/2.3.0/gems/omnibus-ctl-0.5.0/lib/omnibus-ctl.rb:684: warning: Insecure world writable dir /www/server/nvm/versions/node/v8.11.2/bin in PATH, mode 040777
    ok: run: alertmanager: (pid 45330) 1s
    ok: run: gitaly: (pid 45336) 0s
    ok: run: gitlab-monitor: (pid 45346) 1s
    ok: run: gitlab-workhorse: (pid 45362) 0s
    ok: run: logrotate: (pid 45369) 1s
    ok: run: nginx: (pid 45378) 0s
    ok: run: node-exporter: (pid 45383) 0s
    ok: run: postgres-exporter: (pid 45387) 1s
    ok: run: postgresql: (pid 45394) 0s
    ok: run: prometheus: (pid 45476) 1s
    ok: run: redis: (pid 45484) 0s
    ok: run: redis-exporter: (pid 45488) 1s
    ok: run: sidekiq: (pid 45493) 0s
    ok: run: unicorn: (pid 45503) 1s

查看版本号，成功
![请输入图片描述][13]

[1]: /images/recovered/b4efd88df4990401d09a.png
[2]: https://docs.gitlab.com/ee/policy/maintenance.html#upgrade-recommendations
[3]: /images/recovered/9ff9db22492237bc68f0.png
[4]: https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/
[5]: /images/recovered/30f0a6e4744d4ad94f16.png
[6]: /images/recovered/2eea46fe9290f5240d42.png
[7]: /images/recovered/f7380e13d8b030dd5d5d.png
[8]: /images/recovered/c1532a5c65b610bf37e2.png
[9]: /images/recovered/41a65a0d584df7b3eb6a.png
[10]: /archives/157/
[11]: /images/recovered/31f8ee01d2ff09e1c3ad.png
[12]: /images/recovered/001535dd97424e73572b.png
[13]: /images/recovered/f9ead2c1315b24ef51a6.png
