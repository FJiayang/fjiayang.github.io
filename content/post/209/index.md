{
  "title": "SpringBoot 2.x quartz多数据定时任务源配置",
  "date": "2019-07-29T15:04:00+08:00",
  "lastmod": "2020-12-26T12:40:05+08:00",
  "typecho_cid": 209,
  "url": "/archives/209/",
  "comments": false,
  "draft": false,
  "slug": "209",
  "categories": [
    "开发"
  ],
  "tags": [
    "SpringBoot",
    "Quartz"
  ],
  "math": false
}

## 基础环境

`SpringBoot` 2.0 开始官方提供了对`quartz`定时任务的自动配置支持依赖`spring-boot-starter-quartz`组件，无需自行集成

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-quartz</artifactId>
</dependency>
```

环境版本：

1. SpringBoot 2.1.6.RELEASE
2. Java 8



## 定时任务配置

### 添加依赖

在pom.xml中添加quartz、Jpa、mysql驱动、lombok依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <optional>true</optional>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-quartz</artifactId>
</dependency>
```

### 添加配置文件

添加数据库配置

```yaml
spring:
  datasource:
    primary:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: root
      password: hmdt
      url: jdbc:mysql://db/bussines_db?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
    quartz:
      url: jdbc:mysql://db/bussines_quartz?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: root
      password: hmdt

  quartz:
    #相关属性配置
    properties:
      org:
        quartz:
          scheduler:
            instanceName: clusteredScheduler
            instanceId: AUTO
          jobStore:
            # 数据源名称
            dataSource: quartzDataSource
            class: org.quartz.impl.jdbcjobstore.JobStoreTX
            driverDelegateClass: org.quartz.impl.jdbcjobstore.StdJDBCDelegate
            tablePrefix: QRTZ_
            isClustered: true
            clusterCheckinInterval: 1000
            useProperties: false
          threadPool:
            class: org.quartz.simpl.SimpleThreadPool
            threadCount: 10
            threadPriority: 5
            threadsInheritContextClassLoaderOfInitializingThread: true
    job-store-type: jdbc
    #初始化表结构
    jdbc:
      initialize-schema: never
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    database-platform: org.hibernate.dialect.MySQL55Dialect
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
```

数据库配置也有样例配在`spring.quartz.properties`中，但亲测配置无效，并且由于还需要指定连接池等信息，此处配置在spring的连接池中更容易管理

###  下载官网建表语句

尽管使用了`JPA`，但由于没有实体关联，`spring`并不会帮我们自动建表，还需要去官网下载`sql`脚本

[quartz官网](http://www.quartz-scheduler.org/downloads/)

官网压缩包路径`quartz-2.3.0-SNAPSHOT\src\org\quartz\impl\jdbcjobstore`中支持大量数据库建表语句，选择对应的使用即可

![1564406464554.png](https://i.loli.net/2019/07/29/5d3ef2d5f182d76181.png)



### 配置多数据源

多配置源之前在文章中详细说过配置样例和原因，这里不再赘述

[相关文章](/archives/202/)

编写数据库配置，统一使用`HikariCP`连接池

```java
package com.gcb.invest.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.autoconfigure.quartz.QuartzDataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

/**
 * 定时任务数据源配置
 *
 * @author F嘉阳
 * @date 2019-07-28 21:52
 */
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.primary")
    public DataSourceProperties primaryDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.primary.configuration")
    public HikariDataSource firstDataSource() {
        return primaryDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.quartz")
    public DataSourceProperties quartzDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @QuartzDataSource
    @ConfigurationProperties("spring.datasource.quartz.configuration")
    public HikariDataSource quartzDataSource() {
        return quartzDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }
}
```



### 定时任务配置

#### 配置样例1——Bean注入

编写定时任务，由于经过Spring的封装，使用变得更加方便

此处通过内部类配置定时任务，并使用`@DisallowConcurrentExecution`注解指定其在分布式环境下不可并发执行

```java
import lombok.extern.slf4j.Slf4j;
import org.quartz.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.quartz.QuartzJobBean;

/**
 * 定时任务配置
 *
 * @author ：F嘉阳
 * @date ：2019/7/29 9:16
 */
@Slf4j
@Configuration
public class QuartzConfig {

    /**
     * 测试定时任务构建
     *
     * @return
     */
    @Bean
    public JobDetail testTaskJobDetail() {
        return JobBuilder.newJob(TestTask.class)
                .withIdentity(TestTask.class.getName())
                .storeDurably(true)
                .build();
    }

    /**
     * 测试定时任务配置
     *
     * @return
     */
    @Bean
    public Trigger testTaskTrigger() {
        CronScheduleBuilder scheduleBuilder = CronScheduleBuilder.cronSchedule("0/2 * * * * ?");
        return TriggerBuilder.newTrigger()
                .forJob(testTaskJobDetail())
                .withIdentity(TestTask.class.getName())
                .withSchedule(scheduleBuilder)
                .build();
    }

    @DisallowConcurrentExecution
    private class TestTask extends QuartzJobBean {
        @Override
        protected void executeInternal(JobExecutionContext jobExecutionContext) throws JobExecutionException {
            log.debug("执行测试定时任务");
        }
    }
}
```



#### 配置样例2——调度器注入

另一种方式可使用注入调度器手动构建任务，不过需要**调用该方法**之后调度器才会被创建

```java
import org.quartz.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.UUID;

/**
 * @author ：F嘉阳
 * @date ：2019/7/29 8:59
 */
@Service
@Transactional(rollbackFor = Exception.class)
public class QuartzTimerService {

    @Autowired
    private Scheduler scheduler;

    public void buildGoodStockTimer() throws Exception {
        //任务名称
        String name = UUID.randomUUID().toString();
        //任务所属分组
        String group = CustomQuartzJob.class.getName();

        CronScheduleBuilder scheduleBuilder = CronScheduleBuilder.cronSchedule("0/1 * * * * ?");
        //创建任务
        JobDetail jobDetail = JobBuilder.newJob(CustomQuartzJob.class).withIdentity(name,group).build();
        //创建任务触发器
        Trigger trigger = TriggerBuilder.newTrigger().withIdentity(name,group).withSchedule(scheduleBuilder).build();
        //将触发器与任务绑定到调度器内
        scheduler.scheduleJob(jobDetail, trigger);
    }
}
```

定时任务类

```java
import lombok.extern.slf4j.Slf4j;
import org.quartz.DisallowConcurrentExecution;
import org.quartz.JobExecutionContext;
import org.quartz.JobExecutionException;
import org.springframework.scheduling.quartz.QuartzJobBean;

/**
 * @author ：F嘉阳
 * @date ：2019/7/29 8:55
 */
@Slf4j
@DisallowConcurrentExecution
public class CustomQuartzJob extends QuartzJobBean {
    @Override
    protected void executeInternal(JobExecutionContext jobExecutionContext) throws JobExecutionException {
        log.info("执行定时任务");
    }
}
```

## 执行结果

执行成功

![1564383676571.png](https://i.loli.net/2019/07/29/5d3e9a29728e424620.png)

在分布式环境下自动进行作业节点迁移

![1564383705389.png](https://i.loli.net/2019/07/29/5d3e9a29782f691650.png)
