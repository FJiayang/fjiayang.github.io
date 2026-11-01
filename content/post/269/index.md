{
  "title": "SpringCloudStream函数式编程模型",
  "date": "2021-02-21T12:22:00+08:00",
  "lastmod": "2021-02-21T12:28:16+08:00",
  "typecho_cid": 269,
  "url": "/archives/269/",
  "comments": false,
  "draft": false,
  "slug": "269",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "SpringCloud",
    "RabbitMQ"
  ],
  "math": false
}

## 背景

SpringCloud 3.1版本之后，`@EnableBinding`、`@Output`等StreamApi注解都标记为废弃

```java
/**
 * Indicates that an output binding target will be created by the framework.
 *
 * @author Dave Syer
 * @author Marius Bogoevici
 * @author Artem Bilan
 *
 * @deprecated as of 3.1 in favor of functional programming model
 */

@Qualifier
@Target({ ElementType.FIELD, ElementType.METHOD, ElementType.ANNOTATION_TYPE,
		ElementType.PARAMETER })
@Retention(RetentionPolicy.RUNTIME)
@Inherited
@Documented
@Deprecated
public @interface Output {

	/**
	 * Specify the binding target name; used as a bean name for binding target and as a
	 * destination name by default.
	 * @return the binding target name
	 */
	String value() default "";

}
```

```java
/**
 * Enables the binding of targets annotated with {@link Input} and {@link Output} to a
 * broker, according to the list of interfaces passed as value to the annotation.
 *
 * @author Dave Syer
 * @author Marius Bogoevici
 * @author David Turanski
 * @author Soby Chacko
 *
 * @deprecated as of 3.1 in favor of functional programming model
 */
@Target({ ElementType.TYPE, ElementType.ANNOTATION_TYPE })
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@Configuration
@Import({ BindingBeansRegistrar.class, BinderFactoryAutoConfiguration.class })
@EnableIntegration
@Deprecated
public @interface EnableBinding {

	/**
	 * A list of interfaces having methods annotated with {@link Input} and/or
	 * {@link Output} to indicate binding targets.
	 * @return list of interfaces
	 */
	Class<?>[] value() default {};

}
```

相关文章

[Producing and Consuming Messages](https://docs.spring.io/spring-cloud-stream/docs/current/reference/html/spring-cloud-stream.html#spring-cloud-stream-overview-producing-consuming-messages) — SpringCloud 官方文档

[@EnableBinding @deprecated as of 3.1 in favor of functional programming model](https://stackoverflow.com/questions/65576021/enablebinding-deprecated-as-of-3-1-in-favor-of-functional-programming-model) — stackoverflow



[The type EnableBinding is deprecated](https://stackoverflow.com/questions/65752826/the-type-enablebinding-is-deprecated-the-type-streamlistener-is-deprecated-sp) — stackoverflow



因此，所有采用命令式编程的API，在升级到新版本时，官方推荐使用更加简单的函数式编程API

完整代码样例

[FJiayang/spring-cloud-stream-rabbit-example](https://github.com/FJiayang/spring-cloud-stream-rabbit-example) — GitHub项目地址


## 升级方式

### 命令式编程模型

以简单多Topic消息为例，原本的编程方式如下

#### 生产者

```java
@SpringBootApplication
public class ProducerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ProducerApplication.class, args);
    }
}

/**
 * @author F嘉阳
 * @date 2018-10-08 17:57
 */
@RestController
@EnableBinding(MySource.class)
public class Producer {

    @Autowired
    private MySource channel;

    @RequestMapping("/send")
    public String send() {
        channel.output().send(MessageBuilder.withPayload(new Date()).build());
        return "success";
    }
}

/**
 * @author F嘉阳
 * @date 2018-10-08 18:01
 */
public interface MySource {
    String OUTPUT = "output";

    @Output(MySource.OUTPUT)
    MessageChannel output();
}
```

配置文件

```yaml
spring:
  rabbitmq:
    host: 192.168.163.128
    username: cms
    password: cms-mq-admin
  cloud:
    stream:
      bindings:
        output:
          destination: my-test-channel
server:
  port: 8082
```



#### 消费者

```java
@SpringBootApplication
public class ConsumerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConsumerApplication.class, args);
    }
}

/**
 * @author F嘉阳
 * @date 2018-10-08 18:10
 */
@EnableBinding(MySink.class)
public class Consumer {
    @StreamListener(MySink.INPUT)
    public void receive(Message<String> message) {
        System.out.println("接收到MQ消息:" + message.getPayload());
    }
}

/**
 * @author F嘉阳
 * @date 2018-10-08 18:07
 */
public interface MySink {
    String INPUT = "input";

    @Input(MySink.INPUT)
    SubscribableChannel input();
}
```

配置文件

```yaml
spring:
  rabbitmq:
    host: 192.168.163.128
    username: cms
    password: cms-mq-admin
  cloud:
    stream:
      bindings:
        input:
          destination: my-test-channel
server:
  port: 8081
```

### 函数式编程模型

从命令式升级到函数式编程，首先需要升级SpringCloud版本至3.1以上，此处升级到最新版2020.0.1

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>top.fjy8018</groupId>
    <artifactId>cloud-stream</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>pom</packaging>

    <name>cloud-stream</name>
    <description>Demo project for Spring Boot</description>

    <modules>
        <module>producer</module>
        <module>consumer</module>
    </modules>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.4.2</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>

    <properties>
        <spring-cloud.version>2020.0.1</spring-cloud.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

目前国内有清晰的升级指引的还比较少，目前只能参考官方文档材料

[Programming Model](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_programming_model) — SpringCloud官方文档



#### 模型1——系统定时驱动的消息队列

官方文档描述

> ##### [Suppliers (Sources)](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_suppliers_sources)
>
> `Function` and `Consumer` are pretty straightforward when it comes to how their invocation is triggered. They are triggered based on data (events) sent to the destination they are bound to. In other words, they are classic event-driven components.
>
> However, `Supplier` is in its own category when it comes to triggering. Since it is, by definition, the source (the origin) of the data, it does not subscribe to any in-bound destination and, therefore, has to be triggered by some other mechanism(s). There is also a question of `Supplier` implementation, which could be *imperative* or *reactive* and which directly relates to the triggering of such suppliers.
>
> Consider the following sample:
>
> ```java
> @SpringBootApplication
> public static class SupplierConfiguration {
> 
> 	@Bean
> 	public Supplier<String> stringSupplier() {
> 		return () -> "Hello from Supplier";
> 	}
> }
> ```
>
> The preceding `Supplier` bean produces a string whenever its `get()` method is invoked. However, who invokes this method and how often? The framework provides a default polling mechanism (answering the question of "Who?") that will trigger the invocation of the supplier and by default it will do so every second (answering the question of "How often?"). In other words, the above configuration produces a single message every second and each message is sent to an `output` destination that is exposed by the binder. 

其大意为，若采用默认的函数式编程模型，会每秒钟发送一条消息到消费者，定时发送参数可以配置

按照文档升级后如下

##### 生产者

```java
@SpringBootApplication
public class ProducerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ProducerApplication.class, args);
    }

    @Bean
    public Supplier<Date> source1() {
        return () -> new Date();
    }
}
```

函数式编程不需要在代码中定义监听队列，只需要按照约定写在配置文件中即可

官方文档描述

> ##### [Functional binding names](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_functional_binding_names)
>
> Unlike the explicit naming required by annotation-based support (legacy) used in the previous versions of spring-cloud-stream, the functional programming model defaults to a simple convention when it comes to binding names, thus greatly simplifying application configuration. Let’s look at the first example:
>
> ```java
> @SpringBootApplication
> public class SampleApplication {
> 
> 	@Bean
> 	public Function<String, String> uppercase() {
> 	    return value -> value.toUpperCase();
> 	}
> }
> ```
>
> In the preceding example we have an application with a single function which acts as message handler. As a `Function` it has an input and output. The naming convention used to name input and output bindings is as follows:
>
> - input - `<functionName> + -in- + <index>`
> - output - `<functionName> + -out- + <index>`
>
> The `in` and `out` corresponds to the type of binding (such as *input* or *output*). The `index` is the index of the input or output binding. It is always 0 for typical single input/output function, so it’s only relevant for [Functions with multiple input and output arguments](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_functions_with_multiple_input_and_output_arguments).
>
> So if for example you would want to map the input of this function to a remote destination (e.g., topic, queue etc) called "my-topic" you would do so with the following property:
>
> ```
> --spring.cloud.stream.bindings.uppercase-in-0.destination=my-topic
> ```
>
> Note how `uppercase-in-0` is used as a segment in property name. The same goes for `uppercase-out-0`.



配置文件

```yaml
spring:
  rabbitmq:
    host: 192.168.163.128
    username: cms
    password: cms-mq-admin

  cloud:
    stream:
      bindings:
        source1-out-0:
          destination: test1
    function:
      definition: source1

server:
  port: 8083
```

由此可见，整体配置简化了很多，多为`规约大于配置`的方式进行定义，特别注意`function`配置的位置，是在`stream`配置的同级



##### 消费者

```java
@SpringBootApplication
public class ConsumerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConsumerApplication.class, args);
    }

    @Bean
    public Consumer<Date> sink1() {
        return System.out::println;
    }
}
```

配置文件同理

```yaml
spring:
  rabbitmq:
    host: 192.168.163.128
    username: cms
    password: cms-mq-admin

  cloud:
    stream:
      bindings:
        sink1-in-0:
          destination: test1
    function:
      definition: sink1


server:
  port: 8081
```

##### 运行结果

生产者每隔一秒发送一次消息

![1613880363469](/images/recovered/b7d363b0d67c373d682f.png)



#### 模型2——`StreamBridge`

但实际生产中，更多是由业务场景触发，故不能使用该模式进行配置，SpringCloud还提供了另外一种`StreamBridge`模式

官方文档介绍

> ##### [Sending arbitrary data to an output (e.g. Foreign event-driven sources)](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_sending_arbitrary_data_to_an_output_e_g_foreign_event_driven_sources)
>
> There are cases where the actual source of data may be coming from the external (foreign) system that is not a binder. For example, the source of the data may be a classic REST endpoint. How do we bridge such source with the functional mechanism used by spring-cloud-stream?
>
> Spring Cloud Stream provides two mechanisms, so let’s look at them in more details
>
> Here, for both samples we’ll use a standard MVC endpoint method called `delegateToSupplier` bound to the root web context, delegating incoming requests to stream via two different mechanisms - imperative (via StreamBridge) and reactive (via EmitterProcessor).

大意是，实际的数据源可以是外部事件驱动，例如通过Rest接口

官方样例

> ###### [Using StreamBridge](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_using_streambridge)
>
> ```java
> @SpringBootApplication
> @Controller
> public class WebSourceApplication {
> 
> 	public static void main(String[] args) {
> 		SpringApplication.run(WebSourceApplication.class, "--spring.cloud.stream.source=toStream");
> 	}
> 
> 	@Autowired
> 	private StreamBridge streamBridge;
> 
> 	@RequestMapping
> 	@ResponseStatus(HttpStatus.ACCEPTED)
> 	public void delegateToSupplier(@RequestBody String body) {
> 		System.out.println("Sending " + body);
> 		streamBridge.send("toStream-out-0", body);
> 	}
> }
> ```
>
> Here we autowire a `StreamBridge` bean which allows us to send data to an output binding effectively bridging non-stream application with spring-cloud-stream. Note that preceding example does not have any source functions defined (e.g., Supplier bean) leaving the framework with no trigger to create source bindings, which would be typical for cases where configuration contains function beans. So to trigger the creation of source binding we use `spring.cloud.stream.source` property where you can declare the name of your sources. The provided name will be used as a trigger to create a source binding. So in the preceding example the name of the output binding will be `toStream-out-0` which is consistent with the binding naming convention used by functions (see [Binding and Binding names](https://docs.spring.io/spring-cloud-stream/docs/3.1.0/reference/html/spring-cloud-stream.html#_binding_and_binding_names)). You can use `;` to signify multiple sources (e.g., `--spring.cloud.stream.source=foo;bar`)

参考官方文档改造后

##### 生产者

这里直接贴出多主题的消费模式，实际生产中多数也是订阅多个主题

```java
@SpringBootApplication
public class ProducerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ProducerApplication.class, args);
    }
}

/**
 * @author F嘉阳
 * @date 2018-10-08 17:57
 */
@RestController
public class Producer {

    @Autowired
    private StreamBridge streamBridge;

    @RequestMapping("/send1")
    public String send1() {
        streamBridge.send("source1-out-0", new Date());
        return "success1";
    }

    @RequestMapping("/send2")
    public String send2() {
        streamBridge.send("source2-out-0", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        return "success2";
    }

}
```

配置文件

```yaml
spring:
  rabbitmq:
    host: 192.168.133.128
    username: dev-user
    password: devpassword

  cloud:
    stream:
      bindings:
        source1-out-0:
          destination: test2
        source2-out-0:
          destination: test3
    function:
      definition: source1;source2


server:
  port: 8083
```

##### 消费者

```java
@SpringBootApplication
public class ConsumerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ConsumerApplication.class, args);
    }

    @Bean
    public Consumer<Date> sink1() {
        return System.out::println;
    }

    @Bean
    public Consumer<String> sink2() {
        return System.out::println;
    }
}
```

配置文件

```yaml
spring:
  rabbitmq:
    host: 192.168.133.128
    username: dev-user
    password: devpassword

  cloud:
    stream:
      bindings:
        sink1-in-0:
          destination: test2
        sink2-in-0:
          destination: test3
    function:
      definition: sink1;sink2

server:
  port: 8081
```

##### 运行结果



![1613881049845](/images/recovered/a1f5ec22f0ee3a6f72c4.png)

触发`/send1`

![1613881012552](/images/recovered/99acd313e5fdee55d1cf.png)



触发`/send2`

![1613881021809](/images/recovered/6f500f762b8ce5faf8e6.png)

可见消息被正确的路由



## 总结

整体来看，函数式编程比命令式编程更加简洁，而且加上SpringCloud规约大于配置的特点，可以明显减少配置的代码量，是未来发展的趋势。
