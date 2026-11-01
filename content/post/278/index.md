{
  "title": "GraphQL实践5——Netflix Dgs Graphql懒加载",
  "date": "2022-10-28T16:04:43+08:00",
  "lastmod": "2022-10-28T16:04:43+08:00",
  "typecho_cid": 278,
  "url": "/archives/278/",
  "comments": false,
  "draft": false,
  "slug": "278",
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

在graphql中，需要查询的字段由调用方传递，如果此时存在关联表才能获取的字段，但前端不需要该字段的时候，默认查询所有字段会带来较大开销

例如

```yaml
type Actor {
    actorId: Int!
    firstName: String!
    lastName: String!
    lastUpdate: String
}

type Film {
    filmId: Int!
    title: String!
    description: String
    actors: [Actor]
}

type Query {
    filmList: [Film]
}
```



## 解决方案——懒加载

DGS框架中支持配置调用方传递了指定字段才读取对应的数据





## 配置懒加载

增加实体定义，模拟嵌套实体

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

@Data
public class Film implements Serializable {

	@Serial
	private static final long serialVersionUID = 1L;

	/**
	 * 联系人ID
	 */
	@TableId(type = IdType.AUTO)
	private Integer filmId;

	private String title;

	private String description;

	private Integer releaseYear;

	private Integer languageId;

	private Integer originalLanguageId;

	private Integer rentalDuration;

	private BigDecimal rentalRate;

	private Integer length;

	private BigDecimal replacementCost;

	private String rating;

	private String specialFeatures;

	private Date lastUpdate;
}

@Data
public class FilmActor implements Serializable {

	@Serial
	private static final long serialVersionUID = 1L;

	/**
	 * 联系人ID
	 */
	@TableId(type = IdType.AUTO)
	private Integer actorId;

	private Integer filmId;

	private Date lastUpdate;
}
```



#### Mapper

```java
public interface ActorMapper extends BaseMapper<Actor> {}
public interface FilmActorMapper extends BaseMapper<FilmActor> {}
public interface FilmMapper extends BaseMapper<Film> {}
```



#### DAO

```java
public interface ActorRepository extends IService<Actor> {
}
public interface FilmActorRepository extends IService<FilmActor> {
	List<FilmActor> listByFilmId(@Size.List({@Size(min = 1, message = "至少要有一个元素")}) List<Integer> filmIds);
}
public interface FilmRepository extends IService<Film> {
}
```

```java
@Validated
@Repository
@RequiredArgsConstructor
public class ActorRepositoryImpl extends ServiceImpl<ActorMapper, Actor> implements ActorRepository {
}
@Validated
@Repository
@RequiredArgsConstructor
public class FilmActorRepositoryImpl extends ServiceImpl<FilmActorMapper, FilmActor> implements FilmActorRepository {
	@Override
	public List<FilmActor> listByFilmId(List<Integer> filmIds) {
		return lambdaQuery().in(FilmActor::getFilmId, filmIds).list();
	}
}
@Validated
@Repository
@RequiredArgsConstructor
public class FilmRepositoryImpl extends ServiceImpl<FilmMapper, Film> implements FilmRepository {
}

```



### Service

多表查询聚合逻辑

```java
public interface ActorService {
	List<Actor> listByFilmId(Integer filmId);
}

@Slf4j
@Service
@RequiredArgsConstructor
public class ActorServiceImpl implements ActorService {

	private final ActorRepository actorRepository;

	private final FilmActorRepository filmActorRepository;

	@Override
	public List<Actor> listByFilmId(Integer filmId) {
		List<FilmActor> filmActors = filmActorRepository.listByFilmId(List.of(filmId));
		if (CollectionUtils.isEmpty(filmActors)) {
			return Collections.emptyList();
		}
		List<Integer> actorIds = filmActors.stream().map(FilmActor::getActorId).toList();
		return actorRepository.listByIds(actorIds);
	}
}
```



### Graphql 查询解析器

```java
@DgsComponent
@RequiredArgsConstructor
public class FilmDataFetcher {

	private final FilmRepository filmRepository;

	private final ActorService actorService;

	@DgsQuery
	public Collection<Film> filmList() {
		return filmRepository.list();
	}

	@DgsData(parentType = "Film")
	public List<Actor> actors(DgsDataFetchingEnvironment dfe) {
		Film film = dfe.getSource();
		return actorService.listByFilmId(film.getFilmId());
	}

	@DgsQuery
	public Film findOneFilm(@InputArgument Integer id) {
		return filmRepository.getById(id);
	}
}
```

增加`DgsDataFetchingEnvironment`入参，DGS会自动获取请求上下文参数

此处定义即为传入了`actors`参数才执行该方法获取对应的`Actor`集合，实现懒加载



## 测试

访问http://localhost:8080/graphiql即可看到在线查询页面

### 不访问Actor

![image-20221027222611945](/images/recovered/e0a617a602bcf420d34f.png)

此时可以看到日志输出，没有查询Actor表

![image-20221027222636357](/images/recovered/e04ff9b75412aaf0de3d.png)



### 访问Actor

![image-20221027222705715](/images/recovered/5ff450ecdb9753703994.png)

此时DSG会执行N+1查询Actor表，性能损耗非常大

![image-20221027222731234](/images/recovered/e3c81522d228f1da62e6.png)



## 总结

对于表关联，开销较大字段，都可以使用DSG懒加载实现性能优化，但此时还是存在N+1查询性能问题，将在后面使用DataLoader优化
