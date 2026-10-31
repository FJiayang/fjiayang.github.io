{
  "title": "阿里云CDN加速的一些经历",
  "date": "2018-04-09T22:54:00+08:00",
  "lastmod": "2023-09-07T09:29:38+08:00",
  "typecho_cid": 145,
  "url": "/archives/145/",
  "comments": false,
  "draft": false,
  "slug": "145",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "阿里云",
    "CDN"
  ],
  "math": true
}

## 问题产生 ##
最近有一个新的业务系统上线运行，源站使用8085端口，通过Nginx反向代理到80和443端口，为了保证全国的延迟在50ms以内，故启用CDN加速，仅对js和css等静态文件加速，其余文件自动回源，然而一旦开启了静态文件CDN后，网页便无法渲染（Vue），通过控制台查看，报重定向（301）过多的错误
![请输入图片描述][1]

一旦关闭CDN对js和css的加速后再清除浏览器缓存就立刻可以访问
![请输入图片描述][2]

## 寻找解决办法 ##
经过网上查阅资料无果后向阿里云提交工单咨询
![请输入图片描述][3]

过程十分曲折，在阿里云工程师的指引下反复修改CDN各种配置，从上午一直修改到晚上10点，更换了3个工程师（从工号判断），其中还包括阿里工程师直接打电话询问问题情况（好评）
测试途径包括但不限于：跟随回源协议、抓包等
![请输入图片描述][4]

![请输入图片描述][5]

![请输入图片描述][6]

![请输入图片描述][7]

## 目前折衷方案 ##
根据阿里的建议，现在只能暂停对静态文件的加速，全部回源到源站
![请输入图片描述][8]

## 造成的影响 ##
2018年4月9日全天整个业务系统通过域名访问处于崩溃状态，对所有需要访问的客户重定向到IP+端口号的地址，并且该地址还一直被微信拦截（微信拦截非80端口的网址）


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mKrru.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mKHka.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mKJCc.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mYX1D.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mEdHG.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mEYgX.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mEo0y.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mKydj.png
