{
  "title": "SpringCloud中遇到的坑",
  "date": "2018-07-24T21:34:00+08:00",
  "lastmod": "2023-09-07T14:43:56+08:00",
  "typecho_cid": 172,
  "url": "/archives/172/",
  "comments": false,
  "draft": false,
  "slug": "172",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "SpringCloud"
  ],
  "math": true
}

## SpringCloud Config
### 配置无法读取
#### 问题描述
配置中心的配置文件如下

```
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
spring:
  application:
    name: config
  cloud:
    config:
      server:
        git:
          uri: http://XXX/fjy8018/config-repo
          username: 1186032234@qq.com
          password: XXX
          basedir: spring-cloud\config\basedir
server:
  port: 8084
```
已经通过网页测试该账号和密码可以访问该仓库，并有权限，启动配置中心后通过页面访问提示`Cannot clone or checkout repository`
![请输入图片描述][1]

#### 解决方法
SpringCloud正式版的配置中心路径必须是带.git结尾的全路径，将配置改为全路径即可

```
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
spring:
  application:
    name: config
  cloud:
    config:
      server:
        git:
          uri: http://XXX/fjy8018/config-repo.git
          username: 1186032234@qq.com
          password: XXX
          basedir: spring-cloud\config\basedir
server:
server:
  port: 8084
```
![请输入图片描述][2]


  [1]: /images/recovered/8c1332eac187ab1677c2.png
  [2]: /images/recovered/e7e5c9f6cf08d84d06d2.png
