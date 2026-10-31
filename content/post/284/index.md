{
  "title": "Java 17 生产实践",
  "date": "2022-05-06T11:04:00+08:00",
  "lastmod": "2022-10-31T11:04:48+08:00",
  "typecho_cid": 284,
  "url": "/archives/284/",
  "comments": false,
  "draft": false,
  "slug": "284",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "Java"
  ],
  "math": true
}

## 背景

### 版本发布

2021年3月16日 Java 17 作为继Java 11的下一个LTS版本正式发布，JDK 17 作为下一代 LTS 将提供至少到 2026 年的支持。

### 同业动态

2022年ThoughtWorks 26期技术雷达也提到，建议各个组织将Java 17纳入评估。

> **评估** **82. Java 17**
>
> 我们通常不会专门介绍某一语言的新版本，但我们还是想关注一下 Java 新的长期支持（LTS）版本——Java 17。尽管出现了前景不错的新特性，比如**模式匹配**等预览特性，但其实向新 LTS 版本升级的方案更应该吸引各个组织的兴趣。我们建议各个组织在 Java 有新的发布时对其进行评估，确保能够恰当地适配这些新特性和版本。尽管定期更新有利于简化开发并且方便管理，但许多组织却意外地并不经常更新语言的版本。希望通过 LTS 版本的升级以及开发团队对语言的定期更新，能够使生产软件免于因为“更新成本太高”而一直困在 Java 的过时版本上。

### 框架发展情况

Spring Framework 6和SpringBoot 3.0 将在2022年底正式发布，将基于Java 17构建。

[Spring Boot 3.0.0 M1 Release Notes · spring-projects/spring-boot Wiki (github.com)](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0.0-M1-Release-Notes)

> ### Minimum Requirements Changes
>
> Spring Boot 3.0 makes the following changes to its minimum supported versions:
>
> - Gradle 7.3
> - Jakarta EE 9
> - Java 17
> - Kotlin 1.6
> - Spring Framework 6

### 其他团队落地情况

在此之前，我所在的团队使用的Java版本一直停留在Java8，今年经过其他开发团队的尝试，我们团队在4月份也正式决定在生产环境使用Java 17。

###### 

## 实践情况

### 开发组件版本

本次计划在内部运营管理系统重构中使用Java 17作为基础版本，其他核心组件版本如下

- SpringBoot 2.6.6
- mapstruct 1.4.2.Final
- mybatis-plus 3.5.1
- jdk 17.0.1



开发时SpringBoot 3.0还处于M2里程碑阶段，暂时不适合带入生产环境，等未来3.0 GA后再考虑升级



### 基础镜像

原本使用的基于jdk8 的Docker image也需要替换成基于jdk 17的image



带来的问题：

原本基于jdk8构建并注入到镜像中的opentelemetry-javaagent暂时不可用，等待后续基于jdk17 构建后才能重新启用



### JVM参数

由于从Java11开始G1替代CMS作为默认的垃圾收集器，Java14开始移除了CMS GC。

故团队内定义的系统框架配置的GC调优参数基本废弃，并且可以使用Java 14新引入的JVM参数，例如`-XX:+ShowCodeDetailsInExceptionMessages`

#### 开启前

```java
Exception in thread "main" java.lang.NullPointerException
    at Book.main(Book.java:5)
```



#### 开启后

```java
Exception in thread "main" java.lang.NullPointerException: 
        Cannot assign field "book" because "shoopingcart.buy" is null
    at Book.main(Book.java:5)
```



### 语法特性

从Java8到Java17期间新增的语法特性很多，此处提及几个比较常用的

#### 快速创建不可变集合

不可变对象具有许多优点，包括：

- 可安全使用不受信任的库。
- 线程安全。
- 不需要支持变化判断，所有不可变的集合实现都比其可变的同级实现更节省内存。



Java9开始新增List、Map、Set等of方法快速创建不可变集合

```java
List.of(prodStrategy, instStrategy)
```

实现源码

```java
    static <E> List<E> of(E e1, E e2) {
        return new ImmutableCollections.List12<>(e1, e2);
    }
```



Java16开始，Stream类中也新增`toList()`方法，快速将流转成不可变集合

```java
List<Long> ids = idList.stream().map(ContactId::id).toList();
```

实现源码

```java
    default List<T> toList() {
        return (List<T>) Collections.unmodifiableList(new ArrayList<>(Arrays.asList(this.toArray())));
    }
```

注意：如果需要将流转成可变集合，还是需要使用`collect(Collectors.toList())`方法





#### record类型

Java14开始新增record类型，用于表示不可变class，实践中可以方便的表示值对象，无需使用`@Value`注解

```java
public record ContactId(@NotNull(message = "ID不能为空") Long id) {
}
```



#### instanceof模式匹配

Java14开始支持模式匹配，无需做强制类型转换

```java
	private void configMessageConverters(List<HttpMessageConverter<?>> converters) {
		converters.removeIf(x -> x instanceof StringHttpMessageConverter || x instanceof MappingJackson2HttpMessageConverter);
		converters.add(new StringHttpMessageConverter(Charsets.UTF_8));
		converters.add(new MappingJackson2HttpMessageConverter(objectMapper));
	}
```



#### 创建类型安全的流

Java9 开始，新增`ofNullable`方法创建类型安全的流对象，避免在调用`stream`方法时报NPE

```java
// query.getDescColumns()可能为null
List<OrderItem> descItems = Stream.ofNullable(query.getDescColumns())
				.flatMap(Collection::stream)
				.map(OrderItem::desc)
				.toList();
```



### 性能和安全提升

从同一段功能逻辑中测试发现，Java8和Java17在并发场景下性能差距达到2倍以上

并且同样的逻辑（使用了并发安全的工具）在并发量达到50000的时候在Java8中依然有线程安全问题，而Java17中不会有线程安全问题



外部测评结果

> 从规划调度引擎 OptaPlanner 项目（[原文  (opens new window)](https://www.optaplanner.org/blog/2021/09/15/HowMuchFasterIsJava17.html)）对 JDK 17和 JDK 11 的性能基准测试进行了对比来看：
>
> 1. 对于 G1GC（默认），Java 17 比 Java 11 快 8.66%；
> 2. 对于 ParallelGC，Java 17 比 Java 11 快 6.54%；
> 3. Parallel GC 整体比 G1 GC 快 16.39%
>
> 简而言之，JDK17 更快，高吞吐量垃圾回收器比低延迟垃圾回收器更快。
