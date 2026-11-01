{
  "title": "Linux面板APPNODE与宝塔横评",
  "date": "2018-12-09T16:35:04+08:00",
  "lastmod": "2018-12-09T16:35:04+08:00",
  "typecho_cid": 188,
  "url": "/archives/188/",
  "comments": false,
  "draft": false,
  "slug": "188",
  "categories": [
    "服务器"
  ],
  "tags": [
    "宝塔",
    "APPNODE",
    "测评"
  ],
  "math": false
}

## 宝塔

宝塔从2017年底开始接触并全面在自己服务器上推广使用，到目前为止手上的服务器需要建站数据库之类的都部署了宝塔，同时开发测试环境的服务器为了方便管理也部署了宝塔，可以说用了也算比较长时间了，宝塔的优势也比较明显

### 1. 界面简单，逻辑明确

系统信息一目了然

![appnode13.png](/images/recovered/55e6317bfbc958410d45.png)

### 2. 软件安装简单

基本都是无脑安装，之前在开发测试环境搭建Redis和MySQL就是通过宝塔快速安装的，5分钟内搭建完毕快速测试，而且卸载的比较干净，特别是如果小白自己下载MySQL编译包安装很容易出现卸载残留导致无法安装新的MySQL

![appnode14.png](/images/recovered/52c788c5e6362ea235aa.png)

### 3. 快捷的防火墙管理

宝塔提供的防火墙管理基本满足需求，比使用防火墙命令逐个放行便捷

![appnode15.png](/images/recovered/897822976b1ecb191d9d.png)

### 总结

总的来说宝塔适合建站管理，快速应用部署，但对于复杂的操作还是需要自行通过终端解决，而且防火墙功能有限，抗CC攻击等都需要付费或者搭建其他软件

## APPNODE

在最近看到APPNODE这个管理面板，在虚拟机跑了一下发现其功能强大，还是有点意思的。

以下逐一说明（无广告费）

### 1. 简单安装

其实APPNODE和宝塔都是一键安装，自选服务器环境这些共同点，从这点上来说没什么差别，两者甚至连默认端口号都是一样的。。![appnode.png](/images/recovered/3b391a5eda8b7ee8c2a9.png)

![appnode1.png](/images/recovered/0d5368691c75b5ee2bef.png)

装好后的首页，默认展示建站指引（好评，第一次在宝塔建站还是摸索了一会的）

![appnode2.png](/images/recovered/d753cd9fe248408eefe1.png)

### 更详细的服务器信息

展示的服务器信息比宝塔详细很多，各项指标都有展示

![appnode3.png](/images/recovered/2665dbbea0de5ef5ea7c.png)

![appnode4.png](/images/recovered/64775e0ba7b860f373df.png)

![appnode5.png](/images/recovered/fe4b307d63e31589af03.png)

### 更多的系统软件

可以安装许多软件目前都是免费的，软件也和宝塔类型类似，但有一些特别的，比如frp内网穿透之类还是不错的，比自己部署简单不少，不知道以后会不会收费

![appnode6.png](/images/recovered/43202ce8cb0691067e26.png)

网络测试软件看看就好

![appnode7.png](/images/recovered/ab891f2c0305b090120b.png)

### 更丰富的软件市场

和宝塔类似的软件市场，同样种类更多，有些2017年才兴起的小众软件也在里面，也有不少刚需平台例如owncloud、nextcloud，而同样用宝塔搭建私有云还是挺折腾的

![appnode8.png](/images/recovered/d74cc9b4056caa57329f.png)

### 功能完备的防火墙管理（重点）

在我看来这个是与宝塔最大的不同，前面那些只要宝塔想加入其实也不难，但这个支持自己配置的防火墙规则，其实内部实现应该是通过nginx代理配置实现，但比宝塔收费的要良心，通过简单设置参数即可抵抗简单的DDOS攻击

![appnode9.png](/images/recovered/62c0fb3525e3bb606207.png)

攻击测试，通过Apache ab压测进行DDOS攻击

未开启之前所有请求顺利通过


![appnode10.png](/images/recovered/b8fe1684cb0e468ce31f.png)

在配置1秒内最大访问次数后成功拦截，1000个请求只有70个有效，说明DDOS流量劫持被成功拦截

![appnode11.png](/images/recovered/bae0f801dbb31f1fb6a3.png)

### 更灵活的网站控制

日志、SSL、负载情况、网站更新自动提醒重载nginx等

另外还提供免费SSL证书自动续租，十分好评

![appnode12.png](/images/recovered/7815249cee3deb123fb8.png)

### 总结

APPNODE适合对服务器操作熟悉，需要更大灵活度的定制服务器功能的用户，对于建站灵活度也非常高，而缺点也比较明显，功能多必然带来操作复杂，许多功能小白可能没听过，乱操作一波可能会翻车。。
