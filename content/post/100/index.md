{
  "title": "作业提交系统介绍",
  "date": "2018-02-27T19:50:00+08:00",
  "lastmod": "2023-09-07T10:13:30+08:00",
  "typecho_cid": 100,
  "url": "/archives/100/",
  "comments": false,
  "draft": false,
  "slug": "100",
  "categories": [
    "开发"
  ],
  "tags": [],
  "math": true
}

## 起因 ##
在2017年下半学年收集作业的过程中，遇到经常需要统一命名格式的情况，十分繁琐，也有出现许多深夜、凌晨提交作业的情况，同时也有不少要求找回以往提交的作业的情况，故考虑开发作业提交系统，满足作业收集需求

## 系统成品 ##
[作业提交系统正式版（点击访问正式版网站本体）][1]

[作业提交系统测试服务器版本（点击访问测试服务器网站本体）][2]

[系统使用说明（点击访问）][3]

## 系统优点 ##
系统主要解决以下几大核心问题

 1. 全天候接受作业提交并及时作出响应
 2. 作业自动按学号+姓名命名
 3. 作业按列表进行展示
 4. 用户可下载以往提交的作业和模板
 5. 后台自动获取所有未提交人员名单

## 系统延迟和访问速度 ##
在购买了阿里云CDN加速后，通过在线网络测试工具得到如下结果
全球的平均延迟在50ms以内
![CDN][4]

同时进行国内多地访问时的下载速度能稳定在100K以上，若遇到打开缓慢请稍等片刻或者刷新页面
![cmsintro19.png][5]


<!--more-->

----------


## 开发准备 ##
确定立项后首先对所需架构进行选型，考虑范围包括：

> 传统Java MVC、Struct、SpringMVC、SpringBoot、Mybatis、Hibernate
> bootstrap4.0、Vue、ElementUI、jQuery、原生ajax、axios、vue-resource
> thymeleaf、JSP

最后根据各方优缺点决定使用Java开发
Java版本（使用了java8 的新特性，故不对低版本的jdk兼容）

> Java 8或以上

后台使用

> Spring Boot2.0RC2

数据库层使用

> SpringJpa

前端界面组件使用

> ElementUI

前端底层数据响应式框架

> Vue
ajax使用Vue官方推荐的库
> axios

## 开发过程 ##
开发系统生命周期选型采用**螺旋模型**，通过反复迭代的方式进行持续改进
由于切换新的架构（以前订书系统是纯jsp处理所有业务，Java MVC对于注解使用十分少），同时注重对数据库的范式设计（3NF），因此在开发准备花了不少时间，以及在后续开发遇到不少问题，耗时极大，根据私人Git仓库GitLab的记录，2018年1月29号开始代码编写V0.1，直到2018年2月27号 版本号V2.2 RC1网站正式上线公测持续接近1个月时间，目前（2018年2月28日）仍在对bug进行测试和修复
GitLab截图
![cmsintro0.png][6]


## 后台部分代码截图 ##
所有工程文件使用Git进行版本配置管理，并上传到私人代码仓库
![cmsintro12.png][7]

所有jar包使用maven进行统一管理
![cmsintro10.png][8]

![cmsintro11.png][9]

下载的Controller
![cmsintro1.png][10]

所有Controller
![cmsintro2.png][11]

通过使用枚举对异常统一处理，并编写自定义异常类
![cmsintro3.png][12]

![cmsintro4.png][13]

对日志进行科学管理，使用SLF4j、Logback 日志框架对所有info和error日志进行每天一个文件的日志输出
![cmsintro7.png][14]

单元测试
![cmsintro8.png][15]

## 前端部分代码截图 ##
使用Spring Boot官方推荐的thymeleaf模板引擎，其性能比JSP更优，而且也有与JSTL类似的语法，可以轻松实现组件化和动态更新数据，并能够保证前端所有页面统一为纯HTML
![cmsintro9.png][16]

axios异步获取后台传来的json数据，并使用Vue做数据绑定
![cmsintro5.png][17]

前端使用饿了么的ElementUI组件进行快速开发，遗憾的是未使用ES6和Webpack
![cmsintro6.png][18]

## 访问权限控制 ##
通过使用Spring Boot拦截器，实现访问控制列表（Access Control List，ACL）与强制访问控制(Mandatory Access Control——MAC)结合的访问控制机制，对所有非注册用户和非管理员用户进行分辨和拦截
![20][19]

![21][20]


## 开发文档截图 ##
### 后台提供的API文档 ###
Restful风格的API由后台提供，前端可直接使用，实现前后端分离开发
![cmsintro13.png][21]

### 后台提供的错误码文档 ###
![cmsintro14.png][22]

### 数据字典 ###
![cmsintro15.png][23]

### 数据库ER图 ###
按照3NF规范进行开发，充分使用数据库视图作为外模式进行访问
![cmsintro16.png][24]

## 服务器配置 ##
### 硬件服务器 ###
服务器采用由阿里云购买的轻量应用服务器，配置如下

    1核CPU Intel Xeon E5-2682 v4
    2G DDR4 内存
    1M上行带宽
    VPC专有网络 
    40GB系统盘 SSD云盘
#### 硬件服务器评价 ####
整体配置基本满足系统运行需求，根据Beta测试阶段的数据，**高并发时单核CPU瓶颈会显现**，内存维持50%左右的水平，磁盘读写也令人满意，上行带宽略有不足，但由于为了保证系统高并发下的稳定性优先，以及系统主要用于用户上传，服务器下载速度没有瓶颈即可
![cmsintro25.png][25]

### 服务器的安全策略 ###
服务器的安全策略为
服务器每天凌晨自动备份网站存储的文件和数据库到阿里云OSS和又拍云FTP存储空间，确保收到攻击后能以最快速度恢复所有用户文件和数据

    ★[2018/03/14 04:31:01] 数据库[db_imis2]已成功备份到阿里云OSS,用时[0.21]秒
    |---保留最新的[3]份备份
    |---文件名:Db_db_imis2_20180314_043101.sql.gz
    |---已清理过期备份文件：Db_db_imis2_20180311_043102.sql.gz
    ★[2018/03/15 04:31:02] 数据库[db_imis2]已成功备份到阿里云OSS,用时[0.21]秒
    |---保留最新的[3]份备份
    |---文件名:Db_db_imis2_20180315_043101.sql.gz
    |---已清理过期备份文件：Db_db_imis2_20180312_043101.sql.gz
    
    ★[2018/03/12 04:30:01] 网站[cms.fjy8018.xin]已成功备份到阿里云OSS,用时[0.23]秒
    |---保留最新的[2]份备份
    |---文件名:Web_cms.fjy8018.xin_20180312_043001.tar.gz
![cmsintro21.png][26]

![cmsintro21.png][27]

### Web服务器 ###
考虑到业务需要轻量级，占有内存少，并发能力强的软件平台，故服务器使用nginx1.12作为Web服务器，并通过配置实现**反向代理**和**负载均衡**
![cmsintro20.png][28]

    upstream  cms-host{
    server  cms.fjy8018.xin:8085; #负载均衡
    }
    
        server {
            listen       80;
            listen 443 ssl;
            server_name  cms.fjy8018.xin; #域名
            index index.html;  #指定的server的root的访问页面
            root /index; #指定的server的root目录
    
        if ($server_port !~ 443){
            rewrite ^(/.*)$ https://$host$1 permanent;
        } 
            location /cms {
                    proxy_pass http://cms.fjy8018.xin:8085;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                    proxy_set_header X-Forwarded-Port $server_port;
            #    root   html;
            #    index  index.html index.htm;
            }
        }

但由于没有使用分布式文件系统，故实际负载仍然为一台阿里云服务器

### 域名备案 ###
为了保证微信能够直接访问，故通过购买万网域名fjy8018.xin，在通信管理局进行ICP备案，经过6天的等待，终于获得ICP备案和备案号
![cmsintro22.png][29]

### 启用HTTPS ###
通过免费获取TrustAsia证书，并在nginx中加入pem文件路径配置，让网址成功启用HTTPS安全协议
        #HTTP_TO_HTTPS_END
        ssl_certificate    XXX/cms/full_chain.pem;
        ssl_certificate_key    XXX/cms/private.key;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        error_page 497  https://$host$request_uri;
    
    
        #SSL-END
![cmsintro21.png][30]

## 开源想法 ##
暂无对外公开源码的想法，若本班有感兴趣的可以一同交流学习，如有兴趣接手维护或者开发新的网页端、安卓端和IOS端的也可以和本人联系，本人将提供后台API文档。


  [1]: https://cms.fjy8018.xin/cms/index
  [2]: http://s2.fjy8018.top:8085/cms/index
  [3]: http://home.fjy8018.top:8090/blog/index.php/archives/99/
  [4]: /images/recovered/dc1045e6a35625842aa4.png
  [5]: /images/recovered/659e14fe35d1a271bc63.png
  [6]: /images/recovered/928a4bb4fb6e356dea94.png
  [7]: /images/recovered/a4ad40f5dbd5af94d19d.png
  [8]: /images/recovered/5754fc7930690ff57294.png
  [9]: /images/recovered/1c8bb0479e903dc5176b.png
  [10]: /images/recovered/659e76f59151ed1c257c.png
  [11]: /images/recovered/57d8cb024aa67ba914d3.png
  [12]: /images/recovered/a819f13b7d2b1ea9aa45.png
  [13]: /images/recovered/c50a91a371b4922931ae.png
  [14]: /images/recovered/5316f6a56b54ef99eda7.png
  [15]: /images/recovered/5c51c79210a6aa614dfb.png
  [16]: /images/recovered/e6482c505d014c042906.png
  [17]: /images/recovered/ec6ab706f893d4ac1518.png
  [18]: /images/recovered/dc4f36db4dab0b7565f8.png
  [19]: /images/recovered/4c026a6d07a3796caa9c.png
  [20]: /images/recovered/ee3bfbb63032c32bce86.png
  [21]: /images/recovered/15789b9cdab028a93998.png
  [22]: /images/recovered/5707cc441c9d7ac41e86.png
  [23]: /images/recovered/2ba9ff0c61a98e3efa70.png
  [24]: /images/recovered/4bf9f84db23d9e89ec2d.png
  [25]: /images/recovered/38c408c06a1272d723c5.png
  [26]: /images/recovered/c04a42b52b2935c3559f.png
  [27]: /images/recovered/599741677a751dd89fc4.png
  [28]: /images/recovered/369388a58bb023d0d94b.png
  [29]: /images/recovered/c05c16103a52e01935a9.png
  [30]: /images/recovered/15717e228725735068c5.png
  [31]: https://github.com/FJiayang/cms
