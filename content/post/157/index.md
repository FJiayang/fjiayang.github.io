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



  [1]: /images/recovered/af830953d966c1b73732.png
  [2]: /images/recovered/35718dc111a171347458.png
  [3]: /images/recovered/734b5684f7427682679f.png
  [4]: /images/recovered/7ce34ecc419ff8a3ec6a.png
  [5]: /images/recovered/2e820c4df43ce390f87a.png
  [6]: /images/recovered/8682030f401f2fecf58c.png
  [7]: /images/recovered/28d9d173ab273b86f3d8.png
