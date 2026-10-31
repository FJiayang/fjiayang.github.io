{
  "title": "Redis分布式锁在高并发情况下偶然突然失效",
  "date": "2018-06-11T12:40:00+08:00",
  "lastmod": "2023-09-07T14:57:13+08:00",
  "typecho_cid": 158,
  "url": "/archives/158/",
  "comments": false,
  "draft": false,
  "slug": "158",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "Redis",
    "SpringBoot"
  ],
  "math": true
}

## 背景 ##
### 原理 ###
在学习Redis分布式锁时编写Service类，其中包含加锁和解锁两个方法，通过调用Redis的SETNX和GETSET方法加锁
![请输入图片描述][1]

![请输入图片描述][2]

### 源码 ###
为便于查看，加了logback进行日志打印
![请输入图片描述][3]

![请输入图片描述][4]

需要加锁的方法，该方法为模拟抢购场景的实现
![请输入图片描述][5]

交由SpringBoot自动注入写好的`RedisLock`包（其实问题出在这里，本应该是`10*1000`，手误写成`10*000`结果为`0`，故所有超时为`0`）
![请输入图片描述][6]

访问Controller，一个为抢购地址，抢购地址访问一次则数量减一，一个为查询地址
![请输入图片描述][7]

### 压测工具 ###
使用Apache AB模拟高并发访问

## 并发测试 ##
### 手动测试 ###
手动访问，测试功能是否正常
查询
![请输入图片描述][8]

订购
![请输入图片描述][9]

### 压测 ###
10个请求，单线程发起测试
![请输入图片描述][10]

数量正常
![请输入图片描述][11]

50个请求，2个线程发起测试
![请输入图片描述][12]

### 出错 ###
数量显然不对
![请输入图片描述][13]

查看日志，发现后续请求都从判断锁是否过期的方法获得的锁，但执行上数值一致，逻辑也没问题
![请输入图片描述][14]

### 原因 ###
后来发现在高并发情况下超时时间如果设置过小，多个线程可能获得的时间戳一致，导致加锁无效，即每个线程都在判断时间戳时可以获得锁，导致“超售”
![请输入图片描述][15]

### 再次压测 ###
数量正常
![请输入图片描述][16]

提高并发量
![请输入图片描述][17]

数量正常，问题解决
![请输入图片描述][18]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRtVF.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRZGr.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRivd.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRIu1.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRwpJ.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRgPt.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRfY0.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRruR.png
  [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RR8sg.png
  [10]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RR538.png
  [11]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RR4pW.png
  [12]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRGdw.png
  [13]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RR1GL.png
  [14]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRmgi.png
  [15]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRuMD.png
  [16]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRl6u.png
  [17]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRCPv.png
  [18]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2RRnUa.png
