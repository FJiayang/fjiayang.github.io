{
  "title": "GraphQL实践4——Netflix Dgs Graphql集成Mybatis Plus",
  "date": "2022-10-28T16:03:00+08:00",
  "lastmod": "2022-10-28T16:04:59+08:00",
  "typecho_cid": 277,
  "url": "/archives/277/",
  "comments": false,
  "draft": false,
  "slug": "277",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "MyBatis",
    "GraphQL"
  ],
  "math": true
}

## 介绍

通过JPA或者Mybatis Plus集成Graphql框架已经很简便，但其实使用`graphql-java`集成过于底层，很多扩展内容实现并不方便，例如：

- 分页查询
- 资源懒加载
- N+1问题

Netflix 基于长期的Graphql实践，2020年开源了DGS Framework，让解决上述问题更加简单，大量开源系统集成Graphql也是通过集成DGS组件

> The DGS framework project started at Netflix in 2019 as internal teams began developing multiple GraphQL services. As 2020 wrapped up, Netflix decided to open source the framework and build a community around it.

## 集成Netflix DGS

官网：[Home - DGS Framework (netflix.github.io)](https://netflix.github.io/dgs/)



### 引入依赖

技术栈：

- SpringBoot 2.7.1
- Mybatis Plus
- JDK 17
- Dgs SpringBoot

本次和上一篇文章一样，选择原因不在赘述

```xml
	<dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.netflix.graphql.dgs</groupId>
                <artifactId>graphql-dgs-platform-dependencies</artifactId>
                <!-- The DGS BOM/platform dependency. This is the only place you set version of DGS -->
                <version>4.9.16</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <dependency>
            <groupId>com.netflix.graphql.dgs</groupId>
            <artifactId>graphql-dgs-spring-boot-starter</artifactId>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>
        <!-- mybatis-plus-boot-starter -->
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-boot-starter</artifactId>
            <version>3.5.2</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

```



### 配置文件

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: ****
    url: jdbc:mysql://localhost:3306/sakila?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai
server:
  port: 8080
logging:
  level:
    top.fjy8018.graphsqldemo.mapper: DEBUG

dgs:
  graphql:
    schema-locations:
      - classpath*:graphql/*.graphqls
```

由于DGS默认扫描路径为`classpath*:schema/**/*.graphql*`，本次基于上一篇文章的工程配置，需要手动指定一下扫描文件目录



### Mybatis Plus配置

#### 扫描配置

```java
@Configuration
@MapperScan("top.fjy8018.graphsqldemo.mapper")
public class MybatisPlusConfig {
}
```



#### 实体

表结构还是使用`sakila`样例数据库的表

```java
@Data
public class Actor implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    /**
     * 联系人ID
     */
    @TableId(type = IdType.AUTO)
    private Integer actorId;

    private String firstName;

    private String lastName;

    private Date lastUpdate;

}
```



#### Mapper

```java
public interface ActorMapper extends BaseMapper<Actor> {
}
```



#### DAO

从分层模型定义上，MP自带的CRUD接口本质上还是一个DAO，故定义为Repository更加合适，不与业务逻辑Serice冲突

同时也建议QueryWrapper仅在对应的Repository使用，防止查询条件散落在各处

```java
public interface ActorRepository extends IService<Actor> {
}
```

```java
@Validated
@Repository
@RequiredArgsConstructor
public class ActorRepositoryImpl extends ServiceImpl<ActorMapper, Actor> implements ActorRepository {
}
```



### Graphql 查询解析器

```java
@DgsComponent
@RequiredArgsConstructor
public class ActorDataFetcher {

	private final ActorRepository actorRepository;

	@DgsQuery
	public Collection<Actor> actorList() {
		return actorRepository.list();
	}

	@DgsQuery
	public Actor findOneActor(@InputArgument Integer id) {
		return actorRepository.getById(id);
	}
}
```



```yaml
type Query {
    actorList: [Actor]
    findOneActor(id : Int!): Actor
}

type Actor {
    actorId: Int!
    firstName: String!
    lastName: String!
    lastUpdate: String
}
```



此处集成和`graphql-java-kickstart`类似，也是十分简便，不指定别名默认将方法名映射到文件方法名



## 测试

访问http://localhost:8080/graphiql即可看到在线查询页面

![image-20221027220330451](/images/recovered/2585730d2ba894f25ecc.png)



## 总结

此处还看不出DGS与其他`graphql-java`组件的区别，都是集成简便，可以和任何数据源、ORM框架集成，后续将会逐步实践DGS特性，包括懒加载、N+1问题、分页组件等
