{
  "title": "GraphQL实践10——Netflix Dgs Graphql异步订阅",
  "date": "2022-10-28T21:59:23+08:00",
  "lastmod": "2022-10-28T21:59:23+08:00",
  "typecho_cid": 283,
  "url": "/archives/283/",
  "comments": false,
  "draft": false,
  "slug": "283",
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

## 介绍

`GraphQL`订阅模式支持服务端主动向客户端推送数据通知，避免客户端轮训



## DGS Subscriptions

### 新增依赖

此处使用的是`SpringBoot Web`组件，故引入`websockets`依赖

如果使用的是`WebFlux`则要引入对应的`dgs-webflux`

```xml
		  <dependency>
            <groupId>com.netflix.graphql.dgs</groupId>
            <artifactId>graphql-dgs-subscriptions-websockets-autoconfigure</artifactId>
        </dependency>
```



### 异步通知解析

此处定义为当新增一个Actor就给所有订阅者发异步通知

```java
@Slf4j
@DgsComponent
@RequiredArgsConstructor
public class ActorDataFetcher {

	private final ActorAssembler actorAssembler;

	private FluxSink<Actor> actorStream;

	private ConnectableFlux<Actor> actorPublisher;

	@PostConstruct
	private void createActorPublisher() {
		Flux<Actor> publisher = Flux.create(emitter -> {
			actorStream = emitter;
		});

		actorPublisher = publisher.publish();
		actorPublisher.connect();
	}

	@DgsMutation
	public Actor addActor(@InputArgument SubmitActor actor) {
		Actor actorEntity = actorAssembler.convert(actor);
		actorEntity.setActorId(10);
		actorEntity.setLastUpdate(DateUtil.format(new Date(), DatePattern.NORM_DATETIME_PATTERN));
		actorStream.next(actorEntity);
		log.info("服务端创建演员：{}", actor);
		return actorEntity;
	}

	/**
	 * 异步通知
	 *
	 * @return
	 */
	@DgsSubscription
	public Publisher<Actor> actorAdded() {
		return actorPublisher;
	}
}
```



## 单元测试

由于异步通知无法用浏览器自带的控制台测试，只能通过GraphQL客户端订阅后接收异步通知，此处参考官方最佳实践，使用单元测试模拟

```java
@Slf4j
@SpringBootTest
class ActorDataFetcherTest {

	@Autowired
	private DgsQueryExecutor dgsQueryExecutor;

	@Test
	void addActor() {

		GraphQLQueryRequest graphQLQueryRequest = new GraphQLQueryRequest(
				AddActorGraphQLQuery.newRequest()
						.actor(
								SubmitActor.newBuilder()
										.firstName("fu")
										.lastName("jiayang")
										.build())
						.build(),
				new AddActorProjectionRoot()
						.actorId()
						.firstName()
						.lastUpdate());
		dgsQueryExecutor.execute(graphQLQueryRequest.serialize());
	}

	@Test
	void actorAdded() {
		ExecutionResult executionResult = dgsQueryExecutor.execute("""
				subscription {
				  actorAdded {
				    actorId
				    firstName
				    lastName
				    lastUpdate
				  }
				}
				""");
		Publisher<ExecutionResult> reviewPublisher = executionResult.getData();
		List<Actor> actors = new CopyOnWriteArrayList<>();

		reviewPublisher.subscribe(new Subscriber<>() {
			@Override
			public void onSubscribe(Subscription s) {
				s.request(2);
			}

			@Override
			public void onNext(ExecutionResult executionResult) {
				if (executionResult.getErrors().size() > 0) {
					executionResult.getErrors().forEach(error -> log.error(error.toString()));
				}
				Map<String, Object> actorResult = executionResult.getData();
				Actor actor = new ObjectMapper().convertValue(actorResult.get("actorAdded"), Actor.class);
             log.info("客户端监听到演员新增：{}",actor);
				actors.add(actor);
			}

			@Override
			public void onError(Throwable t) {
				t.printStackTrace();
			}

			@Override
			public void onComplete() {
			}
		});

		addActor();
		addActor();

		assertThat(actors.size()).isEqualTo(2);
	}
}
```



从日志输出可以看到客户端成功接收异步通知

![image-20221028214837298](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221028214837298.png)



## 总结

订阅模式属于`GraphQL`特色功能，类似消息队列实现方式，减少客户端对普通查询接口轮训性能开销
