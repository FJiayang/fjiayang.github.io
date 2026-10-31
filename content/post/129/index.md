{
  "title": "班级订书系统",
  "date": "2018-03-02T10:00:00+08:00",
  "lastmod": "2023-09-07T10:05:59+08:00",
  "typecho_cid": 129,
  "url": "/archives/129/",
  "comments": false,
  "draft": false,
  "slug": "129",
  "categories": [
    "开发"
  ],
  "tags": [],
  "math": true
}

## 订书系统介绍 ##
[订书系统（点击访问）][1]
访问后使用学号+姓名即可登录
![orderbook.png][2]

登录后能够查看全班订书情况，总价为服务器自动计算
![orderbook1.png][3]

点击添加/修改即可为自己增加或修改订书信息
![orderbook2.png][4]

![orderbook3.png][5]

同时每位同学可查看后台提供的书籍价格和对应的课程名
![orderbook4.png][6]

也可查看实时公告信息
![orderbook5.png][7]

后台人员登录后可以修改价格，查看各类订书总数，对订书时间进行控制，当时间超过所设定日期后则不允许订书
![orderbook6.png][8]

后台也可以查看所有IP登录日志和设备信息，用于判断异地登录和系统审计，顺带一提，后面真有一次有人盗用账号进行登录修改，通过IP审计的方式找出登录地点和操作人，成功解决非法修改信息的问题
![orderbook7.png][9]

经过两个版本的更新后，系统增加了支付信息，后台可以根据支付宝记录更改支付状态
![orderbook8.png][10]

![orderbook9.png][11]

用户通过点击价格表，扫描其中的支付宝二维码即可支付书费，支付一段时间后经过确认会更新支付状态
![orderbook10.png][12]

## 开发进度 ##
经过最后两次更新后，因多种原因，开发人员打算放弃开发和维护，愿有意接手维护和开发的人员与作者联系

## 已知BUG ##
价格计算页面因二进制移位问题，导致其中一位同学的价格产生多位小数的错误
![orderbook11.png][13]


  [1]:http://orderbook.thresh.xin
  [2]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ytn3K.png
  [3]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2JpJkT.png
  [4]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ytesN.png
  [5]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ytZgX.png
  [6]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ytwHG.png
  [7]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ytkRg.png
  [8]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2yt6dj.png
  [9]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2JpgSt.png
  [10]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2JjoW7.png
  [11]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2Jpyx6.png
  [12]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2JpVrM.png
  [13]:https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2ytvru.png
