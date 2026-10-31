{
  "title": "GraphQL实践2——Spring-GraphQL集成JPA与MySQL",
  "date": "2021-11-15T15:38:00+08:00",
  "lastmod": "2024-08-04T19:32:55+08:00",
  "typecho_cid": 275,
  "url": "/archives/275/",
  "comments": false,
  "draft": false,
  "slug": "275",
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

上一篇介绍到用第三方库集成`GraphQL`，目前spring-graphql项目已经出到`1.0.0-M3`版本，属于内部预览版，此处尝鲜验证

[相关文章](/archives/274/)

## 集成过程

### 引入依赖

由于`SpringBoot 2.6.0`还未发布，因此需要引入较多依赖

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
    <dependency>
        <groupId>org.springframework.experimental</groupId>
        <artifactId>graphql-spring-boot-starter</artifactId>
        <version>1.0.0-M3</version>
    </dependency>
    <!--升级到Spring Boot 2.6后可以移除-->
    <dependency>
        <groupId>org.springframework.data</groupId>
        <artifactId>spring-data-commons</artifactId>
        <version>2.6.0-RC1</version>
    </dependency>
    <dependency>
        <groupId>org.springframework.data</groupId>
        <artifactId>spring-data-jpa</artifactId>
        <version>2.6.0-RC1</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/org.hibernate.javax.persistence/hibernate-jpa-2.1-api -->
    <dependency>
        <groupId>org.hibernate.javax.persistence</groupId>
        <artifactId>hibernate-jpa-2.1-api</artifactId>
        <version>1.0.2.Final</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/com.querydsl/querydsl-jpa -->
    <dependency>
        <groupId>com.querydsl</groupId>
        <artifactId>querydsl-jpa</artifactId>
        <version>4.4.0</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/com.querydsl/querydsl-apt -->
    <dependency>
        <groupId>com.querydsl</groupId>
        <artifactId>querydsl-apt</artifactId>
        <version>4.4.0</version>
    </dependency>
    <!-- https://mvnrepository.com/artifact/javax.annotation/javax.annotation-api -->
    <dependency>
        <groupId>javax.annotation</groupId>
        <artifactId>javax.annotation-api</artifactId>
    </dependency>
    <dependency>
        <groupId>com.querydsl</groupId>
        <artifactId>querydsl-core</artifactId>
    </dependency>
    <dependency>
        <groupId>com.querydsl</groupId>
        <artifactId>querydsl-jpa</artifactId>
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



### 引入里程碑仓库

由于还没有GA，所以要引入里程碑仓库

```xml
<repositories>
    <repository>
        <id>spring-milestones</id>
        <name>Spring Milestones</name>
        <url>https://repo.spring.io/milestone</url>
    </repository>
    <repository>
        <id>spring-snapshots</id>
        <name>Spring Snapshots</name>
        <url>https://repo.spring.io/snapshot</url>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```



### 引入插件

由于使用了dsl动态生成，还要引入注解处理器

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <excludes>
                    <exclude>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                    </exclude>
                </excludes>
            </configuration>
        </plugin>
        <!-- added for QueryDsl-->
        <plugin>
            <groupId>com.mysema.maven</groupId>
            <artifactId>apt-maven-plugin</artifactId>
            <version>1.1.3</version>
            <executions>
                <execution>
                    <goals>
                        <goal>process</goal>
                    </goals>
                    <configuration>
                        <outputDirectory>target/generated-sources/java</outputDirectory>
                        <processor>com.querydsl.apt.jpa.JPAAnnotationProcessor</processor>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```



### SpringBoot 配置

编写配置文件

```yaml
spring:
  datasource:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: root
      password: "****"
      url: jdbc:mysql://localhost:3306/sakila?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
  jpa:
    hibernate:
      ddl-auto: none
    show-sql: true
    database-platform: org.hibernate.dialect.MySQL55Dialect
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
  graphql:
    path: /graphql
    schema:
      locations: classpath:graphql/
      fileExtensions: .graphqls, .gqls
      printer:
        enabled: true
server:
  port: 8080
```



### 实体类

```java
package top.fjy8018.graphsqldemo.entity;

import lombok.Data;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.Objects;

/**
 * 演员表实体类
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
    private Date lastUpdate;

}
```



### DAO

DAO直接继承dsl相关处理器，可自动配对增删改查方法，相比第三方库更加简便

```java
package top.fjy8018.graphsqldemo.repository;

import org.springframework.data.querydsl.QuerydslPredicateExecutor;
import org.springframework.data.repository.CrudRepository;
import org.springframework.graphql.data.GraphQlRepository;
import top.fjy8018.graphsqldemo.entity.ActorEntity;

/**
 * 演员表DAO
 *
 * @author F嘉阳
 * @date 2021/11/5 10:35
 */
@GraphQlRepository
public interface ActorEntityRepository extends
        CrudRepository<ActorEntity, Integer>, QuerydslPredicateExecutor<ActorEntity> {
}
```



### Graphql资源定义

在`resources/graphql`下定义接口和实体文件

接口声明和实体定义`schema.graphqls`

```
type Query {
    findOneActor(actorId : ID!): ActorEntity
    actorList: [ActorEntity]
}

type ActorEntity {
    actorId: ID!
    firstName: String!
    lastName: String!
    lastUpdate: String
}
```



接口定义`acotrEntity.graphql`

```
query findOneActor($id: ID!) {
    findOneActor(actorId: $id) {
        actorId
        firstName
        lastName
        lastUpdate
    }
}

query actorList {
    actorList{
        actorId
    }
}
```



## 启动测试

`Spring-Graphql`默认不包含可视化界面，此处使用postman进行测试

### 唯一查询

![image-20211115151701244](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211115151701244.png)



### 列表查询

![image-20211115151810849](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20211115151810849.png)



## 总结

使用Spring官方组件好处在于和Spring生态集成度很高，如果本身就采用Jpa方式进行业务开发，迁移更加方便，需要开发的代码也很少。



## 样例源码地址
[FJiayang/graphql-demo](https://github.com/FJiayang/graphql-demo/tree/spring-graphql)
