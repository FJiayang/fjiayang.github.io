{
  "title": "mybatis中遇到的坑",
  "date": "2018-12-27T12:37:00+08:00",
  "lastmod": "2020-03-13T14:15:00+08:00",
  "typecho_cid": 198,
  "url": "/archives/198/",
  "comments": false,
  "draft": false,
  "slug": "198",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "SpringBoot",
    "Spring",
    "MyBatis"
  ],
  "math": false
}

## mysql驱动问题

### 问题描述

问题发生时间（2018-12-27）

环境版本：

- SpringBoot 2.1.1
- Mybatis 1.3.2

原始配置

```yaml
spring:
  datasource:
    driver-class-name:  com.mysql.jdbc.Driver
    username: hikaricp
    password: hikaricp
    url: jdbc:mysql://localhost:3306/db_test?characterEncoding=utf-8&useSSL=false
```

报错信息

```
Registered driver with driverClassName=com.mysql.jdbc.Driver was not found,
```

报错提示

```
Loading class `com.mysql.jdbc.Driver'. This is deprecated. The new driver class is `com.mysql.cj.jdbc.Driver'. The driver is automatically registered via the SPI and manual loading of the driver class is generally unnecessary.
```

### 解决办法

从提示中可看出，驱动名称有变，更正驱动名称即可

更正后配置

```yaml
spring:
  datasource:
    driver-class-name:  com.mysql.cj.jdbc.Driver
    username: hikaricp
    password: hikaricp
    url: jdbc:mysql://localhost:3306/db_test?characterEncoding=utf-8&useSSL=false
```

同时若使用IDEA自带提示也可看出问题，有两种驱动都存在的问题，希望后续修复

[![mybatis1.jpg](/images/recovered/a25e2fbf090b20512aeb.jpg)](/images/recovered/a25e2fbf090b20512aeb.jpg)

另一种解决方案，从SpringBoot2.0之后连接池使用hikari，可根据url自动识别驱动，即如下配置也可成功运行

```yaml
spring:
  datasource:
    username: hikaricp
    password: hikaricp
    url: jdbc:mysql://localhost:3306/db_test?characterEncoding=utf-8&useSSL=false
```

## 注解使用简化

### 前景提要

进入SpringBoot时代后“注解驱动开发”就已经成为趋势，mybatis官方也提供注解替代xml配置的方案

### 问题描述

问题发现时间（2018-12-27）

环境版本：

- SpringBoot 2.1.1
- Mybatis 1.3.2

在早期版本的mybatis-starter还需要进行实体映射xml文件配置，这次在使用1.3.2版本时再次查了下官方源码，发现已经无需使用映射文件，其底层会自动通过反射识别对象属性类型，并且去除了不少早期版本使用的注解（当前仍可以使用，但不使用功能正常）

#### 

#### 无需手动创建SqlSession或DataSource

官方文档说明：

> As you may already know, to use MyBatis with Spring you need at least an `SqlSessionFactory` and at least one mapper interface.
>
> MyBatis-Spring-Boot-Starter will:
>
> - Autodetect an existing `DataSource`.
> - Will create and register an instance of a `SqlSessionFactory` passing that `DataSource` as an input using the `SqlSessionFactoryBean`.
> - Will create and register an instance of a `SqlSessionTemplate` got out of the `SqlSessionFactory`.
> - Autoscan your mappers, link them to the `SqlSessionTemplate` and register them to Spring context so they can be injected into your beans.

支持版本为Spring 4.3+

> You just need to create a normal Spring boot application and let the mapper be injected like follows(available on Spring 4.3+):

#### @MapperScan -> @Mapper

早期版本需要在启动类上加上`@MapperScan(basePackages = "xxx")`注解扫描mapper类，新版本可直接在mapper包上使用`@Mapper`注解即可

> The MyBatis-Spring-Boot-Starter will search, by default, for mappers marked with the `@Mapper` annotation.

除非需要自定义注解或者不使用@Mapper才需要加上@MapperScan

> You may want to specify a custom annotation or a marker interface for scanning. If so, you must use the `@MapperScan` annotation. 



#### @Results与Mapper.xml

早期版本需要手动指定类型映射，并在resources目录下进行xml配置，新版本自动通过反射识别属性类型，无需进行xml配置
