{
  "title": "GraphQL实践6——Netflix Dgs Graphql N+1问题",
  "date": "2022-10-28T16:05:51+08:00",
  "lastmod": "2022-10-28T16:05:51+08:00",
  "typecho_cid": 279,
  "url": "/archives/279/",
  "comments": false,
  "draft": false,
  "slug": "279",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "GraphQL"
  ],
  "math": true
}

## N+1问题介绍

对于上一篇文章样例，如果要获取每个电影的演员名单，要执行如下动作

- 查询所有电影清单
- 遍历N个电影，查询对应电影的演员名单

总查询开销为N+1次查询，代价非常大，效率低



## 优化方案 DataLoader

对于一对一表关联的情况且每个关联对象只有一个值，可以直接使用`BatchLoader`

但实际上，对于大部分表关联情况，通常为一对多或者多对多，不保证每个关联都有值，此时需要使用`MappedBatchLoader`维护关联关系



### 维护多对多实体关系Map

```java
public interface ActorService {
	Map<Integer, List<Actor>> listByFilmId(Collection<Integer> filmIds);
}
```

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class ActorServiceImpl implements ActorService {

	private final ActorRepository actorRepository;

	private final FilmActorRepository filmActorRepository;

	@Override
	public Map<Integer, List<Actor>> listByFilmId(Collection<Integer> filmIds) {
		List<FilmActor> filmActors = filmActorRepository.listByFilmId(filmIds);
		if (CollectionUtils.isEmpty(filmActors)) {
			return Collections.emptyMap();
		}
		Map<Integer, List<FilmActor>> filmActorMap = filmActors.stream().collect(Collectors.groupingBy(FilmActor::getFilmId));
		List<Integer> actorIds = filmActors.stream().map(FilmActor::getActorId).distinct().toList();
		List<Actor> actors = actorRepository.listByIds(actorIds);
		Map<Integer, Actor> actorsMap = Stream.ofNullable(actors).flatMap(Collection::stream).collect(Collectors.toMap(Actor::getActorId, Function.identity(), (e1, e2) -> e1));
		Map<Integer, List<Actor>> result = Maps.newHashMapWithExpectedSize(filmIds.size());
		filmActorMap.forEach((k, v) -> {
			List<Actor> actorList = Stream.ofNullable(filmActorMap.get(k)).flatMap(Collection::stream).map(e -> actorsMap.get(e.getActorId())).toList();
			result.put(k, actorList);
		});
		return result;
	}
}
```



### Dgs MappedBatchLoader 配置

```java
@DgsDataLoader(name = "actors")
@RequiredArgsConstructor
public class FilmActorsDataLoader implements MappedBatchLoader<Integer, List<Actor>> {

	private final ActorService actorService;

	@Override
	public CompletionStage<Map<Integer, List<Actor>>> load(Set<Integer> keys) {
		return CompletableFuture.supplyAsync(() -> actorService.listByFilmId(keys));
	}
}
```



## 测试

访问http://localhost:8080/graphiql即可看到在线查询页面

![image-20221027223715143](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221027223715143.png)

此时执行嵌套查询只会查询2次，一次查电影列表，一次查所有电影的Actor列表，非常快速

![image-20221027223756097](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221027223756097.png)



## 总结

使用`BatchLoader`实现对N+1问题优化，但还有一个潜在问题，即大数据分页，该样例中，有1000个电影，对应5000+演员，查询一次获取全量数据，对数据库压力较大，也不符合实际场景，还需要进行分页优化
