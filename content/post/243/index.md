{
  "title": "微服务平台开发总结（1）——第一代密码管理系统",
  "date": "2020-05-07T21:34:00+08:00",
  "lastmod": "2020-05-08T14:52:07+08:00",
  "typecho_cid": 243,
  "url": "/archives/243/",
  "comments": false,
  "draft": false,
  "slug": "243",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "Vue",
    "Element"
  ],
  "math": false
}

## 背景

随着网站、工作使用需要，对密码存储的需求越来越大，初期采用本地数据库进行存储，但不适合多地访问，一旦离开了本地电脑，就无法查询密码信息，故计划搭建个人使用的密码信息管理系统



## 概要

### 时间线

- 密码管理信息系统于2018年12月立项，2019年1月9日开始第一次提交
- 2019年2月7日第一个版本上线试运行
- 2019年4月7日进入维护阶段，不再支持新功能
- 2019年11月16日停止维护

### 架构

#### 后端

- `JDK8`
- `SpringBoot 2.1.1.RELEASE`
- `Jetty`
- `SpringData Jpa`
- `MySQL 5.7`
- `Docker`
- `Kuberneties 1.14`
- `Redis`
- `Graylog`
- `GitLab CICD`

#### 前端

- `Vue 2.5`
- `element 2.4.11`
- `vuex 3`
- `vue-axios 2.1.4`
- `eslint 5.8.0`
- `nodejs`
- `nginx`
- `https`
- `Docker`
- `GitLab CICD`

### 原理

1. 后端存储密码数据字段和网站相关信息
2. 采用SQL全字段模糊查询匹配结果
3. 密码字段存储采用AES128结合SHA随机盐值加密存储，即使数据库被破解也无法查看对应的密码信息
4. 密码加密秘钥不由服务端存储，只在用户登陆时录入并临时通过AES128加密后存储在Redis中，用户登出或者登陆超时后销毁

### 优势

- 单体项目，部署简单
- 容器化部署，迁移便利
- Kuberneties云平台部署，支持灰度发布
- 无状态后端服务，支持集群化部署

### 安全审计

支持简单的安全审计

- 登陆日志记录
- 登陆归属地记录

### 安全问题

- 通过实现的Spring拦截器进行登陆拦截，安全性不高
- 没有采用session会话方式，故多地登陆账号且加密秘钥未过期则不需要再次录入
- 支持所有跨域行为，没有对客户端进行识别

### 其他问题

- 独立用户控制，扩展性不高
- 没有基于RBAC模型的权限控制
- 没有管理后台
- 单模块、单体项目，不利于扩展

## 界面演示

登陆页

![image-20200506161528778](/images/recovered/9e71ca63890518528c74.png)

若用户不存在则自动新增

![image-20200506161607742](/images/recovered/1db533bd6488d11b374b.png)

录入加密秘钥

![image-20200506161628599](/images/recovered/95145821594004259d26.png)

主页

![image-20200506161724845](/images/recovered/c0c56411b631d8319d38.png)

信息录入

![image-20200506161803334](/images/recovered/a7e345375886e71e359e.png)

![image-20200506161813699](/images/recovered/d82886dbe011ada2c480.png)

支持全字段模糊检索

![image-20200506161844739](/images/recovered/0520fbf9dfc2c7084eaf.png)

支持Excel模板信息导入

![image-20200506161917039](/images/recovered/a973a91984a9f7c33199.png)

登出

![image-20200506162827488](/images/recovered/c1157615bbbdcf1b0585.png)

## 效果

- 系统稳定运行一年，符合系统初期设计目的
- 同时兼容移动端渲染
