{
  "title": "Typecho  Pinghsu 主题加入备案信息",
  "date": "2018-03-17T00:01:00+08:00",
  "lastmod": "2023-09-07T14:33:44+08:00",
  "typecho_cid": 136,
  "url": "/archives/136/",
  "comments": false,
  "draft": false,
  "slug": "136",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "备案",
    "typecho",
    "服务器",
    "php"
  ],
  "math": true
}

## 修改前 ##
一般安装好typecho和主题后默认的底部信息如下，此时发现没有显示ICP备案信息
![默认的底部信息][1]

## 修改目的 ##
根据国家法律法规要求备案后，是需要在页面底部增加ICP备案信息和链接的，否则将可能会面临相应的处罚
![国家法律法规][2]

## 修改教程 ##
首先以admin账号登录控制台，选择修改外观
![登录][3]

![修改外观][4]

选择编辑当前外观，打开`footer.php`
![编辑当前外观][5]

找到大约位于32行的`info-text`div标签，在`&copy; `后加入如下代码，备案号换成自己的备案号即可

    <p>ICP<a href="http://www.miitbeian.gov.cn/" target="_blank"> 粤ICP备18026XXX号</a></p>

![备案号][6]

最后点击保存即可
![保存][7]

## 最终效果 ##
访问有ICP备案号的[博客链接][8]
![最终效果][9]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5XvL.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5RMR.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5pYv.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5jjD.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5BUW.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5Sui.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2J5P6w.png
  [8]: https://www.fjy8018.xin/
  [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2Jari7.png
