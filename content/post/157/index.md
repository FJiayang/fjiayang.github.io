{
  "title": "GitLab修改配置后nginx无法启动",
  "date": "2018-06-11T12:30:00+08:00",
  "lastmod": "2023-09-07T14:51:08+08:00",
  "typecho_cid": 157,
  "url": "/archives/157/",
  "comments": false,
  "draft": false,
  "slug": "157",
  "categories": [
    "服务器"
  ],
  "tags": [
    "GitLab",
    "Linux"
  ],
  "math": true
}

## 起因 ##
在服务器上通过宝塔搭建了GitLab之后一直没修改GitLab的clone域名和IP配置，今天通过命令自定义域名
```bash
    vim  /etc/gitlab/gitlab.rb
```
![请输入图片描述][1]

重启配置
```bash
    sudo gitlab-ctl reconfigure
```
![请输入图片描述][2]

显示启动成功，但网页访问无显示

![请输入图片描述][3]

重启整个GitLab服务
```bash
    sudo gitlab-ctl restart
```
Nginx报错无法启动
![请输入图片描述][4]

## 查找原因 ##
既然报错，那就只能爬日志看看问题在哪里
```bash
    gitlab-ctl tail
```
报文件存在
```
    chpst: fatal: unable to run: /opt/gitlab/embedded/sbin/nginx: file does not exist
```
![请输入图片描述][5]

网上查了查，似乎是宝塔的问题， 原因应该是为了防止nginx冲突, 把gitlab的nginx启动文件名改成了gitlab-web, 但有个配置文件没改造成的
## 解决 ##
修改nginx启动文件
```bash
    vi /opt/gitlab/sv/nginx/run
```
把
```bash
    exec chpst -P /opt/gitlab/embedded/sbin/nginx -p /var/opt/gitlab/nginx
```
改为
```bash
    exec chpst -P /opt/gitlab/embedded/sbin/gitlab-web -p /var/opt/gitlab/nginx
```
![请输入图片描述][6]

重启nginx服务，启动成功，问题解决
![请输入图片描述][7]



  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RPEjN.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RPD4K.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RPLMy.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RPUFj.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RPzVc.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RP9fG.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RPxLX.png
