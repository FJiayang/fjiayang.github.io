{
  "title": "GraphQL实践3——Spring-Graphql集成Mybatis Plus",
  "date": "2022-10-27T15:37:00+08:00",
  "lastmod": "2022-10-28T16:01:56+08:00",
  "typecho_cid": 276,
  "url": "/archives/276/",
  "comments": false,
  "draft": false,
  "slug": "276",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "MyBatis",
    "GraphQL"
  ],
  "math": true
}

## 介绍

考虑到国内大部分场景对接的是Mybatis或者Mybatis Plus生态，而不是JPA，同时`Graphql`版本也进一步迭代，故计划使用Mybatis Plus对接`Graphql`



## 集成过程

### 引入依赖

- 由于JDK已经发展到19，目前最新的LTS为17，我所在的公司也将生产升级到了JDK 17，未来更多新应用会直接基于17构建，故此处直接基于JDK17对接
- SpringBoot版本为2.7.1，目前已知3.0.0 RC1还不兼容第三方graphql
- 此处不使用spring官方的starter，改为使用graphql-java-kickstart的starter，编写更加简单

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

        <!-- graphql-spring-boot-starter -->
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
        <!-- mybatis-plus-boot-starter -->
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-boot-starter</artifactId>
            <version>3.5.2</version>
        </dependency>
        <!-- querydsl-core -->
        <dependency>
            <groupId>com.querydsl</groupId>
            <artifactId>querydsl-core</artifactId>
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
graphql:
  tools:
    schema-location-pattern: graphql/*.graphqls
  graphiql:
    # 开启可交互页面，用于调试
    enabled: true
logging:
  level:
    top.fjy8018.graphsqldemo.mapper: DEBUG
```



### Mybatis Plus配置

#### 扫描配置

```java
@Configuration
@MapperScan("top.fjy8018.graphsqldemo.mapper")
public class MybatisPlusConfig {
}
```



#### 实体

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
@Component
@AllArgsConstructor
public class ActorGraphQLQueryResolver implements GraphQLQueryResolver {

    private final ActorRepository actorRepository;

    public Collection<Actor> actorList() {
        return actorRepository.list();
    }

    public Actor findOneActor(Integer id) {
        return actorRepository.getById(id);
    }
}
```



查询文件定义在`resources/graphql/actor.graphqls`

```json
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



## 测试

访问http://localhost:8080/graphiql即可看到在线查询页面

![image-20221027214859637](/images/recovered/4a1329e3cbae24b5919f.png)





## 总结

依托Mybatis Plus强大的自带CRUD方法，可以实现和JPA类似的快速对接
