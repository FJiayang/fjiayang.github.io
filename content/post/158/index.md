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


  [1]: /images/recovered/ce5901f28a3ae1ed4717.png
  [2]: /images/recovered/f178398c3d8f57340a24.png
  [3]: /images/recovered/255af471980b5d95924a.png
  [4]: /images/recovered/03a06862780ae815180d.png
  [5]: /images/recovered/9f841614e07329f24a2a.png
  [6]: /images/recovered/37df7dad5f7830a88b9a.png
  [7]: /images/recovered/aee3cf4814e1b7116bf7.png
  [8]: /images/recovered/c66d7b568ae8a6b8381b.png
  [9]: /images/recovered/4b41c122e1586343c210.png
  [10]: /images/recovered/e888235f4b06abe7246e.png
  [11]: /images/recovered/2df680f9d0165a263701.png
  [12]: /images/recovered/8929c729e6c947b007fa.png
  [13]: /images/recovered/efe1cc1b18214299a79f.png
  [14]: /images/recovered/7f02485c149773846bcc.png
  [15]: /images/recovered/3bb6b56de3de8f5888d0.png
  [16]: /images/recovered/deaa462efb390c8243fa.png
  [17]: /images/recovered/277df4ceff74e38ab89b.png
  [18]: /images/recovered/eea3b16349b428d1bf06.png
