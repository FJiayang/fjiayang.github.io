{
  "title": "GitLab汉化",
  "date": "2018-06-12T22:30:00+08:00",
  "lastmod": "2023-09-07T14:49:32+08:00",
  "typecho_cid": 160,
  "url": "/archives/160/",
  "comments": false,
  "draft": false,
  "slug": "160",
  "categories": [
    "服务器"
  ],
  "tags": [
    "GitLab"
  ],
  "math": true
}

## 准备文件 ##
目前GitLab汉化由[xhang][1]维护，故直接克隆其工程到本地目录即可

    git clone https://gitlab.com/xhang/gitlab.git

当前GitLab最新版为`10.8.4`，其他版本自行看`release`切换到对应的分支或者下载对应的发布版本即可
下载完毕为文件夹
![请输入图片描述][2]

## 修改系统名称别名 ##
CentOS 7中出于安全考虑，设置了部分别名，防止误操作，但在此会导致复制文件需要反复输入`y`，故将其关闭
通过`alias`查看当前的别名设置，若有`alias cp='cp -i'`，则说明每次复制文件都会出现提示信息
![请输入图片描述][3]

使用`vi ~/.bashrc`修改配置文件
![请输入图片描述][4]

`source ~/.bashrc`使配置文件生效，但还需要重启会话，否则修改的命令可能依旧无效
再次查看，此时别名配置修改成功
![请输入图片描述][5]

## 配置汉化 ##
此处为初次安装汉化，故与补丁方式汉化不同，直接覆盖文件即可
覆盖前备份一下

    cp -r /opt/gitlab/embedded/service/gitlab-rails{,.ori}

覆盖文件

    cp gitlab/*  /opt/gitlab/embedded/service/gitlab-rails/ -rf

重启GitLab

    gitlab-ctl restart

![请输入图片描述][6]

## 成功 ##
**英文**
![请输入图片描述][7]

**中文**
![请输入图片描述][8]


  [1]: https://gitlab.com/xhang/gitlab
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xHppe.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xH0Ys.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xHbVK.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xHQPc.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xHjGN.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xHK3a.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2xHEud.png
