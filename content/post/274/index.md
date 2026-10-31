{
  "title": "GraphQL实践1——集成JPA与MySQL",
  "date": "2021-11-05T17:41:00+08:00",
  "lastmod": "2024-08-04T19:32:12+08:00",
  "typecho_cid": 274,
  "url": "/archives/274/",
  "comments": false,
  "draft": false,
  "slug": "274",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "JPA",
    "MySQL",
    "GraphQL"
  ],
  "math": true
}

## 介绍

官方定义：

> GraphQL 既是一种用于 API 的查询语言也是一个满足你数据查询的运行时。 GraphQL 对你的 API 中的数据提供了一套易于理解的完整描述，使得客户端能够准确地获得它需要的数据，而且没有任何冗余，也让 API 更容易地随着时间推移而演进，还能用于构建强大的开发者工具。

中文官网：

[GraphQL](https://graphql.cn/) — A query language for your API

## 集成方案选择

GraphQL经过近几年的发展，SpringBoot官方、第三方都提供了`starter`

SpringBoot官方提供的`starter`

[Spring GraphQL](https://spring.io/projects/spring-graphql/)

第三方提供的`starter`

[graphql-spring-boot](https://github.com/graphql-java-kickstart/graphql-spring-boot)


两者活跃度都还不错，但考虑到SpringBoot官方的依赖库还未GA，而且使用起来与Spring家族耦合过大，最终决定采用第三方的`starter`



## 集成过程

### 数据库配置

此处采用MySQL数据库，数据内容采用MySQL官方样例`sakila`数据，表结构和数据地址如下

[sakila database下载地址](https://downloads.mysql.com/docs/sakila-db.zip)

导入后如下

![image-20211105170603665](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211105170603665.png)



### 工程配置

引入最新的SpringBoot框架，依赖如下

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>

    <!-- https://mvnrepository.com/artifact/com.graphql-java-kickstart/graphql-spring-boot-starter -->
    <dependency>
        <groupId>com.graphql-java-kickstart</groupId>
        <artifactId>graphql-spring-boot-starter</artifactId>
        <version>12.0.0</version>
    </dependency>

    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

增加数据库配置

```yaml
spring:
  datasource:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: root
      password: "****"
      url: jdbc:mysql://localhost:3306/sakila?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    database-platform: org.hibernate.dialect.MySQL55Dialect
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
server:
  port: 8080
graphql:
  tools:
    schema-location-pattern: graphql/*.graphqls
  graphiql:
    # 开启可交互页面，用于调试
    enabled: true
```



### 实体映射

新增实体映射，此处只映射`Actor`表作为样例

```java
package top.fjy8018.graphsqldemo.entity;

import lombok.Data;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.Objects;

/**
 * 演员表实体映射
 *
 * @author F嘉阳
 * @date 2021/11/5 10:34
 */
@Data
@Entity
@Table(name = "actor", schema = "sakila")
public class ActorEntity {
    @Id
    @Column(name = "actor_id", nullable = false)
    private Integer actorId;

    @Column(name = "first_name", nullable = false, length = 45)
    private String firstName;

    @Column(name = "last_name", nullable = false, length = 45)
    private String lastName;

    @Column(name = "last_update", nullable = false)
    private Timestamp lastUpdate;
}
```



### 新增DAO

```java
package top.fjy8018.graphsqldemo.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import top.fjy8018.graphsqldemo.entity.ActorEntity;

/**
 * 演员表DAO
 *
 * @author F嘉阳
 * @date 2021/11/5 10:35
 */
public interface ActorEntityRepository extends JpaRepository<ActorEntity, Integer> {
}
```



### 新增查询接口配置

在`resources/graphql`下新增文件`actor.graphqls`

```
type Query {
    actorList: [ActorEntity]
    findOneActor(id : ID!): ActorEntity
}

type ActorEntity {
    actorId: ID!
    firstName: String!
    lastName: String!
    lastUpdate: String
}
```



新增查询解析器

```java
package top.fjy8018.graphsqldemo.resolver;

import graphql.kickstart.tools.GraphQLQueryResolver;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Component;
import top.fjy8018.graphsqldemo.entity.ActorEntity;
import top.fjy8018.graphsqldemo.repository.ActorEntityRepository;

import java.util.Collection;

/**
 * 演员表GraphQL查询解析器
 *
 * @author F嘉阳
 * @date 2021/11/5 16:27
 */
@Component
@AllArgsConstructor
public class ActorGraphQLQueryResolver implements GraphQLQueryResolver {

    private final ActorEntityRepository actorRepository;

    public Collection<ActorEntity> actorList() {
        return actorRepository.findAll();
    }

    public ActorEntity findOneActor(Integer id) {
        return actorRepository.findById(id).orElse(null);
    }
}
```



## 启动验证

启动工程后，浏览器打开`http://localhost:8080/graphiql`

![image-20211105172013228](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211105172013228.png)



### 列表查询

![image-20211105172501790](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211105172501790.png)



由于采用交互式页面，输入也会有语法提示，比较方便

![image-20211105172405147](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211105172405147.png)

### 唯一查询

![image-20211105172219520](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211105172219520.png)



## 优缺点分析

### 优点

1. 接口定义清晰，配置即接口
2. 前端按需获取字段，减少数据传输量
3. 接口整合、演进更加便利



### 缺点

1. 减少字段个数对后端实现没有变化，并不能提升数据库性能



## 样例源码地址

[FJiayang/graphql-demo](https://github.com/FJiayang/graphql-demo)
