{
  "title": "typecho添加文章计数和评论微信提醒",
  "date": "2018-04-07T23:04:00+08:00",
  "lastmod": "2023-09-07T14:56:49+08:00",
  "typecho_cid": 142,
  "url": "/archives/142/",
  "comments": false,
  "draft": false,
  "slug": "142",
  "categories": [
    "默认分类"
  ],
  "tags": [],
  "math": true
}

## 下载相关插件 ##
文章计数：[下载地址][1]
评论微信提醒：[下载地址][2]

## 上传插件到服务器 ##
将下载好的插件上传到`typecho`下的`usr/plugins`目录并解压，将解压后的评论微信提醒文件夹目录名改为`Comment2Wechat`
![请输入图片描述][3]

使用admin账号登录typecho控制台，启用刚刚添加的插件
![请输入图片描述][4]

![请输入图片描述][5]

## 文章计数 ##
### 设置需要显示计数的地方 ###
进入外观设置，配置当前外观代码
![请输入图片描述][6]

![请输入图片描述][7]

根据官方文档说明，`post.php`	为日志页面文件，故配置`post.php`
![请输入图片描述][8]

在文件中搜索`Published on `，找到该行代码，在`</div>`前加入`&nbsp;<?php Views_Plugin::theViews(); ?>`用于显示浏览计数，该文件共用4处地方需要增加代码，自行搜索即可
![请输入图片描述][9]

### 查看效果 ###
进入文章页面，可见在日志末尾已加入浏览计数
![请输入图片描述][10]

## 评论微信提示 ##
[官方指引地址][11]
![请输入图片描述][12]

根据提示登录GitHub账号即可得到一个KEY，此时还不能接收消息
![请输入图片描述][13]

继续按指引绑定微信账号，此时在KEY页面发送消息微信已经可以接收了
![请输入图片描述][14]

进入typecho插件设置，将获得的KEY绑定到插件
![请输入图片描述][15]

此时评论后马上就可以收到消息
![请输入图片描述][16]


  [1]: https://www.boke8.net/typecho-views-plugin.html/comment-page-1/
  [2]: https://github.com/YianAndCode/Comment2Wechat
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crlfW.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crwju.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crfKD.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crZ4a.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crtJd.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crVA0.png
  [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cryLr.png
  [10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cHohF.png
  [11]: http://sc.ftqq.com/3.version
  [12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crgF1.png
  [13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cHzJ7.png
  [14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2crJfJ.png
  [15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cHdlt.png
  [16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cHKKM.png
