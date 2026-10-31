{
  "title": "GraphQL实践9——Netflix Dgs Graphql数据更新",
  "date": "2022-10-28T21:58:54+08:00",
  "lastmod": "2022-10-28T21:58:54+08:00",
  "typecho_cid": 282,
  "url": "/archives/282/",
  "comments": false,
  "draft": false,
  "slug": "282",
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

## 功能介绍

`graphql-java`提供了`Mutations`类型支持数据更新

## NGS Mutations

### 类型定义

```yaml
type Mutation {
    addActor(actor: SubmitActor!): Actor
}

type Subscription {
    actorAdded: Actor
}

input SubmitActor {
    firstName: String!
    lastName: String!
}
```

SubmitActor类型可以交给代码生成器自动生成

![image-20221028214119439](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221028214119439.png)

### 类型转换器

```java
@Mapper(componentModel = SPRING)
public interface ActorAssembler {

	Actor convert(SubmitActor submit);
}
```



### 定义解析器

```java
	@DgsMutation
	public Actor addActor(@InputArgument SubmitActor actor) {
		Actor actorEntity = actorAssembler.convert(actor);
		actorEntity.setActorId(10);
		actorEntity.setLastUpdate(new Date());
		return actorEntity;
	}
```



## 测试

访问http://localhost:8080/graphiql即可看到在线查询页面

![image-20221028213607156](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20221028213607156.png)
