{
  "title": "GraphQL实践7——Netflix Dgs Graphql分页查询",
  "date": "2022-10-28T16:06:31+08:00",
  "lastmod": "2022-10-28T16:06:31+08:00",
  "typecho_cid": 280,
  "url": "/archives/280/",
  "comments": false,
  "draft": false,
  "slug": "280",
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

## 问题背景

上一篇文章提到，使用List查询每次都返回全量数据，而实际场景更多使用分页查询，`graphql-java`提供`Connection`实现游标分页，在Dgs也有对应功能扩展Relay Pagination



## 集成Relay Pagination

### 新增依赖

```xml
        <dependency>
            <groupId>com.netflix.graphql.dgs</groupId>
            <artifactId>graphql-dgs-pagination</artifactId>
        </dependency>
```



### Mybatis Plus 配置分页插件

```java
@Configuration
@MapperScan("top.fjy8018.graphsqldemo.mapper")
public class MybatisPlusConfig {

    /**
     * 分页插件配置
     *
     * @return
     */
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        PaginationInnerInterceptor pageConfig = new PaginationInnerInterceptor(DbType.MYSQL);
        interceptor.addInnerInterceptor(pageConfig);
        return interceptor;
    }
}
```





### Relay Pagination配置

```yaml
type Query {
    actorList: [Actor]
    findOneActor(id : Int!): Actor
    filmList(current: Int!,size: Int!): FilmConnection
    findOneFilm(id : Int!): Film
}

type Actor {
    actorId: Int!
    firstName: String!
    lastName: String!
    lastUpdate: String
}

type Film @connection {
    filmId: Int!
    title: String!
    description: String
    releaseYear: Int
    languageId: Int!
    originalLanguageId: Int
    rentalDuration: Int
    rentalRate: Float
    length: Int
    replacementCost: Float
    rating: String
    specialFeatures: String
    lastUpdate: String
    actors: [Actor]
}
```

`@connection`和`XXXConection`已经由`graphql-java`底层框架自动生成，无需手动定义



### 类型转换器

```java
public interface ConnectionAssembler {

    /**
     * mybatis plus分页对象转为Connection
     *
     * @param page 分页对象
     * @param <T>  泛型
     * @return Connection
     */
    static <T> Connection<T> convert(IPage<T> page) {
        AtomicInteger index = new AtomicInteger();
        List<Edge<T>> defaultEdges = Stream.ofNullable(page.getRecords())
                .flatMap(Collection::stream)
                .map(e -> (Edge<T>) new DefaultEdge<>(e, new DefaultConnectionCursor(String.valueOf(index.incrementAndGet()))))
                .toList();
        return new DefaultConnection<>(defaultEdges,
                new DefaultPageInfo(new DefaultConnectionCursor(String.valueOf(page.getCurrent())),
                        new DefaultConnectionCursor(String.valueOf(page.getPages())),
                        page.getCurrent() > 1,
                        page.getCurrent() < page.getPages()));
    }
}
```





### Graphql解析配置

```java
	@DgsQuery
	public Connection<Film> filmList(@InputArgument("current") Integer current,
									 @InputArgument("size") Integer size,
									 DgsDataFetchingEnvironment dfe) {
		IPage<Film> page = new PageDTO<>(current, size);
		IPage<Film> pageResult = filmRepository.page(page);
		return ConnectionAssembler.convert(pageResult);
	}
```

将`List`查询改为返回`Connection`即可



## 测试

访问http://localhost:8080/graphiql即可看到在线查询页面

![image-20221027224826034](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221027224826034.png)

查看查询数量，确认是按照分页查询

![image-20221027224859609](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221027224859609.png)



## 总结

到此，DSG核心功能尝试基本完成，基本实现常用的Rest功能，同时集成方便，而且官方文档清晰，但目前开源社区还没有太多的基于DSG的系统集成样例，还需要在实践中评估摸索。

thoughtworks也从2016年开始关注graphql，目前给出的建议也是“评估”，可以进行小规模尝试并在合适的时候推广

> We've seen many successful **[GraphQL](https://github.com/facebook/graphql)** implementations on our projects. We've seen some interesting patterns of use too, including [GraphQL for server-side resource aggregation](https://www.thoughtworks.com/radar/techniques/graphql-for-server-side-resource-aggregation). That said, we've concerns about misuse of this framework and some of the problems that can occur. Examples include performance gotchas around N+1 queries and lots of boilerplate code needed when adding new models, leading to complexity. There are workarounds to these gotchas such as query caching. Even though it's not a silver bullet, we still think it's worth assessing as part of your architecture.
