{
  "title": "SpringBoot源码分析1——总览",
  "date": "2020-12-10T17:11:00+08:00",
  "lastmod": "2023-09-07T15:06:43+08:00",
  "typecho_cid": 248,
  "url": "/archives/248/",
  "comments": false,
  "draft": false,
  "slug": "248",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "源码学习"
  ],
  "math": true
}

## SpringBoot 2.0 特点

### 组件自动装配

规约大于配置,专注核心业务

模式注解、@ Enable模块、条件装配、加载机制



### 外部化配置

一次构建、按需调配,到处运行

Environment抽象、生命周期、破坏性变更



### 嵌入式容器

内置容器、无需部署、独立运行

Servlet Web容器、 Reactive Web容器



### Spring Boot Starter

简化依赖、按需装配、自我包含

依赖管理、装配条件、装配顺序



### Production-Ready

一站式运维、生态无缝整合

健康检査、数据指标、@ Endpoint管控



## SpringBoot 与Java EE规范

- Web: Servlet( JSR-315, JSR-340）
- SQL: JDBC(SR-221)
- 数据校验: Bean validation(JSR303、JSR-349)
- 缓存: Java Caching API(JSR-107)
- Web Sockets: Java api for Web Socket(JSR-356
- Web services: JAX-WS( JSR-224）
- Java管理:JMX(JSR3)
- 消息:JMS(JSR-914)



## 核心特性介绍



## 三大特性

- 组件自动装配: Web mvc、 Web flux、JDBC等
- 嵌入式Web容器: Tomcat、 Jetty以及 Undertow
- 生产准备特性:指标、健康检査、外部化配置等



## 组件自动装配

激活： `@EnableAutoConfiguration`
配置：` /META-INF/spring.factories` 实质为key-value形式
实现： `XXXAutoConfiguration`



[官方文档样例](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#boot-features-spring-mvc-auto-configuration)

```java
import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.*;
import org.springframework.web.bind.annotation.*;

@RestController
@EnableAutoConfiguration
public class Example {

  @RequestMapping("/")
  String home() {
    return "Hello World!";
  }

  public static void main(String[] args) throws Exception {
    SpringApplication.run(Example.class, args);
  }

}
```



实际上`@SpringBootApplication`已经包含该注解

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = {
    @Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
    @Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {
}
```



在IDEA中使用`ctrl+shift+n`可查看Spring源码中包含大量`spring.factories`文件

![1552445154381](/images/recovered/6e6176bcf59dbfc0f66c.png)

样例文件：

`org/springframework/boot/spring-boot-autoconfigure/2.0.4.RELEASE/spring-boot-autoconfigure-2.0.4.RELEASE.jar!/META-INF/spring.factories`

```properties
# Initializers
org.springframework.context.ApplicationContextInitializer=\
org.springframework.boot.autoconfigure.SharedMetadataReaderFactoryContextInitializer,\
org.springframework.boot.autoconfigure.logging.ConditionEvaluationReportLoggingListener

# Application Listeners
org.springframework.context.ApplicationListener=\
org.springframework.boot.autoconfigure.BackgroundPreinitializer

# Auto Configuration Import Listeners
org.springframework.boot.autoconfigure.AutoConfigurationImportListener=\
org.springframework.boot.autoconfigure.condition.ConditionEvaluationReportAutoConfigurationImportListener

# Auto Configuration Import Filters
org.springframework.boot.autoconfigure.AutoConfigurationImportFilter=\
org.springframework.boot.autoconfigure.condition.OnClassCondition

# 自动装配配置，自动装载Bean列表
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
org.springframework.boot.autoconfigure.admin.SpringApplicationAdminJmxAutoConfiguration,\
org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration,\
...
```



`WebMvcAutoConfiguration`源码，其包含大量条件装配，若未检测到该类的依赖，则不会被装配

```java
@Configuration
@ConditionalOnWebApplication(type = Type.SERVLET)
@ConditionalOnClass({ Servlet.class, DispatcherServlet.class, WebMvcConfigurer.class })
@ConditionalOnMissingBean(WebMvcConfigurationSupport.class)
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE + 10)
@AutoConfigureAfter({ DispatcherServletAutoConfiguration.class,
    ValidationAutoConfiguration.class })
public class WebMvcAutoConfiguration {
...
```



## 嵌入式Web容器

- Web servlet: Tomcat、 Jetty和 Undertow
- Web reactive Netty Web Server



## 生产准备特性
- 指标:/ actuator/ metrics
- 健康检查:/ actuator/ health
- 外部化配置:/ actuator/ configprops



## Web应用介绍

## 传统 Servlet应用概览
- Servlet组件: Servlet、 Filter、 Listener
- Servlet注册: Servlet注解、 Spring Bean、 RegistrationBean
- 异步非阻塞:异步 Servlet、非阻塞 Servlet



## 传统 Servelt 应用

加入springboot应用通用依赖前缀多为`spring-boot-starter-xxx`

加入Web依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

Maven依赖变化

![1552446944990](/images/recovered/1fd04d44b5f19ca41c9d.png)

由此可看出默认的Web容器为Tomcat（内嵌Servlet容器）

## Servlet 组件 
- Servlet
  - 实现
    - `@WebServlet`
    - HttpServlet
    - 注册
  - URL 映射
      - `@WebServlet(urlPatterns = "/my/servlet")`
  - 注册
      `@ServletComponentScan(basePackages = "top.fjy8018.springboot.web.servlet")`

- Filter

- Listener



### Servlet 注册
### Servlet 注解 
- `@ServletComponentScan` +
  - `@WebServlet`
  - `@WebFilter`
  - `@WebListener`

### Spring Bean 

- `@Bean` +
    - Servlet
    - Filter
    - Listener

- RegistrationBean 
    - ServletRegistrationBean
    - FilterRegistrationBean
    - ServletListenerRegistrationBean

## Servlet 实现

参考源码包位置，由于出现了Reactive Web容器，SpringBoot 1.x的包路径与2.x有所不同，2.x包路径变更为`org.springframework.boot.autoconfigure.web.servlet`



### HttpServlet

```java
package top.fjy8018.springboot.web.servlet;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * 结合servlet规范注册
 *
 * @author F嘉阳
 * @date 2018-09-08 19:17
 */
@WebServlet(urlPatterns = "/myservlet")
public class MyServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        resp.getWriter().print("hello world");
    }
}

```



1. Servlet 3.0规范要求必须实现`HttpServlet`

2. 其内部提供多种方法实现（ctrl+F12）![1552447475522](/images/recovered/b843c866b455c328a35e.png)
3. `urlPatterns = "/myservlet"`指明浏览器映射



### 注册

在主类中注册（包扫描）

```java
package top.fjy8018.springboot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.ServletComponentScan;

@SpringBootApplication
@ServletComponentScan(basePackages = "top.fjy8018.springboot.web.servlet")
public class OverviewApplication {

    public static void main(String[] args) {
        SpringApplication.run(OverviewApplication.class, args);
    }
}
```



启动后从控制台可看出映射已经成功

![1552469521146](/images/recovered/535c8471d00672d27e22.png)

## 异步非阻塞 Servlet 



## 异步 Servlet 
- `javax.servlet.ServletRequest#startAsync()`
- `javax.servlet.AsyncContext`


## 非阻塞 Servlet 

- `javax.servlet.ServletInputStream#setReadListener`
  - `javax.servlet.ReadListener`
- `javax.servlet.ServletOutputStream#setWriteListener`
  - `javax.servlet.WriteListener`




### 异步非阻塞Servlet实现

```java
package top.fjy8018.springboot.web.servlet;

import javax.servlet.AsyncContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * 结合servlet规范注册
 * asyncSupported指定异步servlet，默认false
 *
 * @author F嘉阳
 * @date 2018-09-08 19:17
 */
@WebServlet(urlPatterns = "/myservlet", asyncSupported = true)
public class MyServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        AsyncContext asyncContext = req.startAsync();

        // 执行任务
        asyncContext.start(() -> {
            try {
                resp.getWriter().print("hello world");

                // 触发完成，必须步骤，否则客户端发生超时
                asyncContext.complete();
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
    }
}
```

1. `asyncSupported = true` 启用异步支持，否则报500错误

## Spring Web MVC 应用介绍

- Web mvo视图:模板引擎、内容协商、异常处理等
- Web mVc rest:资源服务、资源跨域、服务发现等



## Web MVC 视图 
- ViewResolver
- View

源码

```java
package org.springframework.web.servlet;

import java.util.Locale;
import org.springframework.lang.Nullable;

public interface ViewResolver {
   @Nullable
   View resolveViewName(String viewName, Locale locale) throws Exception;

}
```

通过指定名称和路径加载视图



视图渲染`View`

```java
package org.springframework.web.servlet;

public interface View {
    ...

   void render(@Nullable Map<String, ?> model, HttpServletRequest request, HttpServletResponse response)
         throws Exception;

}
```

提供接口供不同的模板引擎实现`ViewResolver`



### 模板引擎 

- Thymeleaf
- Freemarker
- JSP



若同时有多种模板引擎，则需要内容协商

### 内容协商 

- `ContentNegotiationConfigurer`
- `ContentNegotiationStrategy`
- `ContentNegotiatingViewResolver`

### 异常处理 
- `@ExceptionHandler`
- `HandlerExceptionResolver`
  - `ExceptionHandlerExceptionResolver`
- `BasicErrorController` (Spring Boot默认白页404)



源码

```java
@Controller
@RequestMapping("${server.error.path:${error.path:/error}}")
public class BasicErrorController extends AbstractErrorController {
    
  @RequestMapping(produces = "text/html")
  public ModelAndView errorHtml(HttpServletRequest request,
      HttpServletResponse response) {
    HttpStatus status = getStatus(request);
    Map<String, Object> model = Collections.unmodifiableMap(getErrorAttributes(
        request, isIncludeStackTrace(request, MediaType.TEXT_HTML)));
    response.setStatus(status.value());
    ModelAndView modelAndView = resolveErrorView(request, response, status, model);
    return (modelAndView != null) ? modelAndView : new ModelAndView("error", model);
  }
    
  @RequestMapping
  @ResponseBody
  public ResponseEntity<Map<String, Object>> error(HttpServletRequest request) {
    Map<String, Object> body = getErrorAttributes(request,
        isIncludeStackTrace(request, MediaType.ALL));
    HttpStatus status = getStatus(request);
    return new ResponseEntity<>(body, status);
  }
}
```

其根据浏览器类型提供两种方式渲染，分别为html和json



![1552452404369](/images/recovered/777d760110b57ef3a65f.png)



```json
{
    "timestamp": "2019-03-13T04:47:18.445+0000",
    "status": 404,
    "error": "Not Found",
    "message": "Not Found",
    "path": "/hello"
}
```



## Web MVC REST 



### 资源服务 
- `@RequestMapping`
- `@GetMapping`
- `@ResponseBody`
- `@RequestBody`



从源码分析可知`@GetMapping`是从`@RequestMapping`变化而来，通过委派（别名）方式实现，并且在SpringMVC 4.3后引入

```java
package org.springframework.web.bind.annotation;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

import org.springframework.core.annotation.AliasFor;

/**
 * Annotation for mapping HTTP {@code GET} requests onto specific handler
 * methods.
 *
 * <p>Specifically, {@code @GetMapping} is a <em>composed annotation</em> that
 * acts as a shortcut for {@code @RequestMapping(method = RequestMethod.GET)}.
 *
 *
 * @author Sam Brannen
 * @since 4.3
 * @see PostMapping
 * @see PutMapping
 * @see DeleteMapping
 * @see PatchMapping
 * @see RequestMapping
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@RequestMapping(method = RequestMethod.GET)
public @interface GetMapping {
    /**
   * 委派目标 {@link RequestMapping#name}.
   */
  @AliasFor(annotation = RequestMapping.class)
  String name() default "";
    ...
}
```



### 资源跨域 

- `CrossOrigin`
- `WebMvcConfigurer#addCorsMappings`
- 传统解决方案
  - IFrame
  - JSONP



源码

```java
package org.springframework.web.servlet.config.annotation;

/**
 * @since 3.1
 */
public interface WebMvcConfigurer {
  /**
   * 跨域配置
   * @since 4.2
   */
  default void addCorsMappings(CorsRegistry registry) {
  }
}
```



注解实现方式

```java
package org.springframework.web.bind.annotation;

/**
 * @since 4.2
 */
@Target({ ElementType.METHOD, ElementType.TYPE })
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface CrossOrigin {...}
```



两者均来自`springframework`，属于不同的实现维度（接口编程 / 注解驱动）



### 服务发现 

- HATEOS

![1552483929211](/images/recovered/ced477005eef760e1c72.png)

### 核心组件

- `DispatcherServlet`——Servlet实现请求转发到映射URL
- `HandlerMapping`——处理映射URL方法
- `HandlerAdapter`——方法处理
- `ViewResolver`——交由视图处理
- ...



## Spring WebFlux （Spring 5+）



## Reactor 基础 
- Java Lambda —— Reactive Stream实现（JDK 9 flow api、RxJava）
- Mono 
- Flux 

 

 

## Web Flux 核心 



### Web MVC 注解兼容 
- `@Controller`
- `@RequestMapping`
- `@ResponseBody`
- `@RequestBody`
- ...



### 函数式声明 
- `RouterFunction`



### 异步非阻塞 

- Servlet 3.1 +

- Netty Reactor

 

 

## 使用场景 

- 页面渲染 
- REST 应用 

 

## 性能测试 

[国外博客](http://blog.ippon.tech/spring-5-webflux-performance-tests/)

结论：Webflux 性能不会显著提升，但Webflux提升**吞吐量**



## Web Server 应用

- 切换 Web server
- 自定义 Servlet Web server
- 自定义 Reactive Web server



 

## 切换 Web Server 

###  切换其他 Servlet 容器 
Tomcat -> Jetty

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <!-- tomcat加载优先级高于jetty，若不加排除，则仍然加载tomcat -->
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- 使用 Jetty 容器 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

![1552469589005](/images/recovered/71457cb5fc17e1fe53bb.png)



### 替换 Servlet 容器 
- WebFlux

```xml
<!--使用webflux必须注释web依赖，当web和flux共存时，web优先级更高-->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>
```



注释后相关类和的注解也已经失效，需要删除

```java
@SpringBootApplication
//@ServletComponentScan(basePackages = "top.fjy8018.springboot.web.servlet")
public class SpringbootApplication {

  public static void main(String[] args) {
    SpringApplication.run(SpringbootApplication.class, args);
  }
}
```



依赖变化

![1552470767813](/images/recovered/a20d097b14406878cf17.png)



启动后变为Netty容器

![1552469817525](/images/recovered/bc3cbc6505e1ad5b6371.png)



### 自定义 Servlet Web Server 
- `WebServerFactoryCustomizer`

 

SpringBoot 2.0 新增支持接口

```java
package org.springframework.boot.web.server;

/**
 * @since 2.0.0
 * @see WebServerFactoryCustomizerBeanPostProcessor
 */
@FunctionalInterface
public interface WebServerFactoryCustomizer<T extends WebServerFactory> {
    
  void customize(T factory);
}
```



该接口为主接口，其下有大量实现，IDEA通过ctrl+alt+B或者ctrl+alt+左键点击查看

![1552470119786](/images/recovered/a9f6f5fa88999acd572d.png)



其中`TomcatServletWebServerFactoryCustomizer`就是实现类之一，但在启用Webflux后该类无效

```java
package org.springframework.boot.autoconfigure.web.servlet;

/**
 * {@link WebServerFactoryCustomizer} to apply {@link ServerProperties} to Tomcat web
 * servers.
 *
 * @author Brian Clozel
 * @author Phillip Webb
 * @since 2.0.0
 */
public class TomcatServletWebServerFactoryCustomizer
    implements WebServerFactoryCustomizer<TomcatServletWebServerFactory>, Ordered {
  @Override
  public void customize(TomcatServletWebServerFactory factory) {
    ServerProperties.Tomcat tomcatProperties = this.serverProperties.getTomcat();
    if (!ObjectUtils.isEmpty(tomcatProperties.getAdditionalTldSkipPatterns())) {
      factory.getTldSkipPatterns()
          .addAll(tomcatProperties.getAdditionalTldSkipPatterns());
    }
    if (tomcatProperties.getRedirectContextRoot() != null) {
      customizeRedirectContextRoot(factory,
          tomcatProperties.getRedirectContextRoot());
    }
    if (tomcatProperties.getUseRelativeRedirects() != null) {
      customizeUseRelativeRedirects(factory,
          tomcatProperties.getUseRelativeRedirects());
    }
  }
    ...
}
```





### 自定义 Reactive Web Server 
- `ReactiveWebServerFactoryCustomizer`

 

其源码显示提供了最基础的实现，包括端口、SSL等，允许自行扩展实现

```java
package org.springframework.boot.autoconfigure.web.reactive;

/**
 * {@link WebServerFactoryCustomizer} to apply {@link ServerProperties} to reactive
 * servers.
 * @since 2.0.0
 */
public class ReactiveWebServerFactoryCustomizer implements
    WebServerFactoryCustomizer<ConfigurableReactiveWebServerFactory>, Ordered {

  private final ServerProperties serverProperties;

  public ReactiveWebServerFactoryCustomizer(ServerProperties serverProperties) {
    this.serverProperties = serverProperties;
  }

  @Override
  public int getOrder() {
    return 0;
  }

  @Override
  public void customize(ConfigurableReactiveWebServerFactory factory) {
    PropertyMapper map = PropertyMapper.get().alwaysApplyingWhenNonNull();
    map.from(this.serverProperties::getPort).to(factory::setPort);
    map.from(this.serverProperties::getAddress).to(factory::setAddress);
    map.from(this.serverProperties::getSsl).to(factory::setSsl);
    map.from(this.serverProperties::getCompression).to(factory::setCompression);
    map.from(this.serverProperties::getHttp2).to(factory::setHttp2);
  }
}
```



## 数据相关介绍



## 关系型数据 

- JDBC:数据源、 JdbcTemplate、自动装配
- JPA:实体映射关系、实体操作、自动装配
- 事务∶ Spring事务抽象、JDBC事务处理、自动装配



### JDBC 

#### 依赖 

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
```



依赖变化，在SpringBoot2.0 后依赖新的连接池 HikariCP

![1552470792077](/images/recovered/98774e31af55c68ebde4.png)





#### 数据源 
- `javax.sql.DataSource`
- `JdbcTemplate `
- 自动装配 
- `DataSourceAutoConfiguration`



##### DataSource

连接池多数实现是对`DataSource`的二次封装，提高执行效率

```java
package javax.sql;

/**
 * @since 1.4
 */

public interface DataSource  extends CommonDataSource, Wrapper {
    Connection getConnection() throws SQLException;
    
    Connection getConnection(String username, String password)
    throws SQLException;
}
```



##### 自动装配

`JdbcTemplate`自动装配，其依赖数据源配置项，故有`@AutoConfigureAfter`注解标识，该类执行于`DataSourceAutoConfiguration`之后，额外还有多个条件装配的标识

```java
package org.springframework.boot.autoconfigure.jdbc;

/**
 * {@link EnableAutoConfiguration Auto-configuration} for {@link JdbcTemplate} and
 * {@link NamedParameterJdbcTemplate}.
 * @since 1.4.0
 */
@Configuration
@ConditionalOnClass({ DataSource.class, JdbcTemplate.class })
@ConditionalOnSingleCandidate(DataSource.class)
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
@EnableConfigurationProperties(JdbcProperties.class)
public class JdbcTemplateAutoConfiguration {...}
```



`DataSourceAutoConfiguration`

```java
package org.springframework.boot.autoconfigure.jdbc;

/**
 * {@link EnableAutoConfiguration Auto-configuration} for {@link DataSource}.
 */
@Configuration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@EnableConfigurationProperties(DataSourceProperties.class)
@Import({ DataSourcePoolMetadataProvidersConfiguration.class,
    DataSourceInitializationConfiguration.class })
public class DataSourceAutoConfiguration {...}
```



该类属于自动装配，故必然在`spring.factories`中，而数据源下即`JdbcTemplateAutoConfiguration`

![1552475892031](/images/recovered/bb4252c9049c8dde04cf.png)



此时直接启动会得到缺少数据源的错误报告

```bash
***************************
APPLICATION FAILED TO START
***************************

Description:

Failed to configure a DataSource: 'url' attribute is not specified and no embedded datasource could be configured.

Reason: Failed to determine a suitable driver class


Action:

Consider the following:
  If you want an embedded database (H2, HSQL or Derby), please put it on the classpath.
  If you have database settings to be loaded from a particular profile you may need to activate it (no profiles are currently active).
```







### JPA 

#### 依赖 

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
```



其属于SpringData项目，基于hibernate实现，同时也自动依赖JDBC

![1552476271433](/images/recovered/24695ede286e0d249019.png)



#### 实体映射关系 
- `@javax.persistence.OneToOne`
- `@javax.persistence.OneToMany`
- `@javax.persistence.ManyToOne`
- `@javax.persistence.ManyToMany`
- ...





#### 实体操作 

- `javax.persistence.EntityManager`



属于Java类库的API

```java
package javax.persistence;

public interface EntityManager {

    /**
     * 存
     */
    public void persist(Object entity);

    /**
     * 更新
     */
    public <T> T merge(T entity);

    /**
     * 删除
     */
    public void remove(Object entity);

    /**
     * 查询以及多个重载方法
     */
    public <T> T find(Class<T> entityClass, Object primaryKey);

    public <T> T find(Class<T> entityClass, Object primaryKey,
                      Map<String, Object> properties);
    ...
}
```





#### 自动装配 

- `HibernateJpaAutoConfiguration`

 

该类也同属于自动装配，且需要JDBC提供数据源，故其加载顺序标识为`DataSourceAutoConfiguration`之后

```java
package org.springframework.boot.autoconfigure.orm.jpa;

/**
 * {@link EnableAutoConfiguration Auto-configuration} for Hibernate JPA.
 */
@Configuration
@ConditionalOnClass({ LocalContainerEntityManagerFactoryBean.class, EntityManager.class })
@Conditional(HibernateEntityManagerCondition.class)
@EnableConfigurationProperties(JpaProperties.class)
@AutoConfigureAfter({ DataSourceAutoConfiguration.class })
@Import(HibernateJpaConfiguration.class)
public class HibernateJpaAutoConfiguration {...}
```





### 事务（Transaction） 
#### 依赖 

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-tx</artifactId>
</dependency>
```





#### Spring 事务抽象 

- `PlatformTransactionManager`



该接口属于事务根接口，不仅限于数据库事务，默认实现包含分布式事务`JtaTransactionManager`和数据库事务`DataSourceTransactionManager`

```java
package org.springframework.transaction;

import org.springframework.lang.Nullable;

/**
 * <p>The default implementations of this strategy interface are
 * {@link org.springframework.transaction.jta.JtaTransactionManager} and
 * {@link org.springframework.jdbc.datasource.DataSourceTransactionManager}

 * @see org.springframework.transaction.support.TransactionTemplate
 * @see org.springframework.transaction.interceptor.TransactionInterceptor
 * @see org.springframework.transaction.interceptor.TransactionProxyFactoryBean
 */
public interface PlatformTransactionManager {...}
```





### JDBC 事务处理 
- `DataSourceTransactionManager`



内部通过IOC自动注入数据源接口

```java
package org.springframework.jdbc.datasource;

@SuppressWarnings("serial")
public class DataSourceTransactionManager extends AbstractPlatformTransactionManager
    implements ResourceTransactionManager, InitializingBean {

  @Nullable
  private DataSource dataSource;
  ...
}
```



### 自动装配 
- `TransactionAutoConfiguration`



自动装配的条件是Spring事务依赖存在`PlatformTransactionManager`

```java
package org.springframework.boot.autoconfigure.transaction;

/**
 * {@link org.springframework.boot.autoconfigure.EnableAutoConfiguration
 * Auto-configuration} for Spring transaction.
 * @since 1.3.0
 */
@Configuration
@ConditionalOnClass(PlatformTransactionManager.class)
@AutoConfigureAfter({ JtaAutoConfiguration.class, HibernateJpaAutoConfiguration.class,
    DataSourceTransactionManagerAutoConfiguration.class,
    Neo4jDataAutoConfiguration.class })
@EnableConfigurationProperties(TransactionProperties.class)
public class TransactionAutoConfiguration {...}
```



## 功能扩展介绍



## Spring Boot 应用 

- Spring Application:失败分析、应用特性、事件监听等
- Spring Boot配置:外部化配置、 Profile、配置属性
- Spring Boot starter: Starter开发、最佳实践



### SpringApplication 



#### 失败分析 

- `FailureAnalysisReporter`



该类在Spring Boot 1.4后开始支持

```java
package org.springframework.boot.diagnostics;

/**
 * Reports a {@code FailureAnalysis} to the user.
 * @since 1.4.0
 */
@FunctionalInterface
public interface FailureAnalysisReporter {...}
```



#### 应用特性 

- SpringApplication Fluent API



原始默认启动方法为`SpringApplication.run(SpringbootApplication.class, args)`其实际返回可配置上下文对象`ConfigurableApplicationContext`，可通过Builder模式重写

```java
package top.fjy8018.springboot;

@SpringBootApplication
public class SpringbootApplication {

  public static void main(String[] args) {
      // Fluent API
      // 等价建造者设计模式调用方法
      new SpringApplicationBuilder(SpringbootApplication.class)
                // 不使用web模式
                .web(WebApplicationType.NONE)
                // 自定义参数
                .properties("name=fjy")
                .run(args);
  }
}
```



2.0 版本下提供3种WEB容器类型

```java
package org.springframework.boot;

/**
 * @since 2.0.0
 */
public enum WebApplicationType {
  NONE,
  SERVLET,
  REACTIVE
}
```



### Spring Boot 配置 

#### 外部化配置
- `ConfigurationProperty`
- `@Profile`



从SpringBoot 2.0 后引入，`Origin`类型支持其他配资源引入，非传统仅支持键值对，由此支持多数据源

```java
package org.springframework.boot.context.properties.source;

/**
 * @since 2.0.0
 */
public final class ConfigurationProperty
    implements OriginProvider, Comparable<ConfigurationProperty> {
    
    private final ConfigurationPropertyName name;

  private final Object value;

  private final Origin origin;
    ...
}
```



[官方文档](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#boot-features-external-config)

此处官方文档存在一定疏漏，部分场景配置无法实现



> Spring Boot uses a very particular `PropertySource` order that is designed to allow sensible overriding of values. Properties are considered in the following order:
>
> 1. [Devtools global settings properties](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#using-boot-devtools-globalsettings) on your home directory (`~/.spring-boot-devtools.properties` when devtools is active).
> 2. [`@TestPropertySource`](https://docs.spring.io/spring/docs/5.0.5.RELEASE/javadoc-api/org/springframework/test/context/TestPropertySource.html) annotations on your tests.
> 3. [`@SpringBootTest#properties`](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/api/org/springframework/boot/test/context/SpringBootTest.html) annotation attribute on your tests.
> 4. Command line arguments.
> 5. Properties from `SPRING_APPLICATION_JSON` (inline JSON embedded in an environment variable or system property).
> 6. `ServletConfig` init parameters.
> 7. `ServletContext` init parameters.
> 8. JNDI attributes from `java:comp/env`.
> 9. Java System properties (`System.getProperties()`).
> 10. OS environment variables.
> 11. A `RandomValuePropertySource` that has properties only in `random.*`.
> 12. [Profile-specific application properties](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#boot-features-external-config-profile-specific-properties) outside of your packaged jar (`application-{profile}.properties` and YAML variants).
> 13. [Profile-specific application properties](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#boot-features-external-config-profile-specific-properties) packaged inside your jar (`application-{profile}.properties` and YAML variants).
> 14. Application properties outside of your packaged jar (`application.properties` and YAML variants).
> 15. Application properties packaged inside your jar (`application.properties` and YAML variants).
> 16. [`@PropertySource`](https://docs.spring.io/spring/docs/5.0.5.RELEASE/javadoc-api/org/springframework/context/annotation/PropertySource.html) annotations on your `@Configuration` classes.
> 17. Default properties (specified by setting `SpringApplication.setDefaultProperties`).



`Profile`支持以注解方式条件开启配置，用于区分开发环境和生产环境等

```java
package org.springframework.context.annotation;

/**
 * @since 3.1
 */
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Conditional(ProfileCondition.class)
public @interface Profile {
  
    String[] value();
}
```





#### 配置属性

- `PropertySources`

 

提供两种编程方式：接口、注解，支持保存多个配置，按照17种顺序排列，该接口在SpringBoot中重新设计变为`ConfigurationProperty`

```java
package org.springframework.core.env;

/**
 * @since 3.1
 * @see PropertySource
 */
public interface PropertySources extends Iterable<PropertySource<?>> {...}
```



## 运维管理介绍

[官方文档](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#production-ready)

## Spring Boot Actuator 

### 端点（Endpoints） 
- Web Endpoints 
- JMX Endpoints 



### 依赖

```xml
<!--运维监控-->
<dependency>
    <groupId>org.springframework.boot</groupId> 
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```



启动效果

![1552484479402](/images/recovered/b70f90664805b64899df.png)



访问健康检查接口`/actuator/health`返回应用状态

```json
{
    "status": "UP"
}
```



访问根路径

```json
{
    "_links": {
        "self": {
            "href": "http://localhost:8080/actuator",
            "templated": false
        },
        "health": {
            "href": "http://localhost:8080/actuator/health",
            "templated": false
        },
        "info": {
            "href": "http://localhost:8080/actuator/info",
            "templated": false
        }
    }
}
```



依据SpringBoot打印的进程号或者依据应用名称使用Jconsole监控，该操作使用的为JMX端点

![1552484208529](/images/recovered/70d229158ba5e50f9e9c.png)



![1552484239522](/images/recovered/0b8a5dd11ce9e76f6ddc.png)

 

### 健康检查（Health Checks） 

- Health 
- HealthIndicator 

 

使用JMX在默认情况下能获取比Web端点更多的信息，原因是JMX支持使用安全连接，具有更好的安全性

![1552484354776](/images/recovered/3f3491babacbb79ad651.png)



[官方文档](https://docs.spring.io/spring-boot/docs/2.0.1.RELEASE/reference/htmlsingle/#boot-features-security-actuator)指出默认状态只暴露health和info，可通过配置文件调整

> ## 28.4 Actuator Security
>
> For security purposes, all actuators other than `/health` and `/info` are disabled by default. The `management.endpoints.web.exposure.include` property can be used to enable the actuators.



在`application.properties`文件中加入配置重启应用

```properties
# 暴露所有健康监控点
management.endpoints.web.exposure.include=*
```



从日志输出可知增加了更多的URL映射

![1552463624541](/images/recovered/7f39921eba90f042c77f.png)



但尽管配置后，JMX显示的信息仍然比Web端更丰富，例如在JMX中不仅看到状态，还能看到磁盘、内存等信息，而Web端仅看到状态

![1552484871890](/images/recovered/2cfbbecdf644e80ec08d.png)



### 指标（Metrics） 

- 内建 Metrics 
- Web Endpoint : `/actuator/metrics`
- 自定义 Metrics 



Web端点列举支持指标

```json
{
    "names": [
        "jvm.memory.max",
        "jvm.gc.memory.promoted",
        "jvm.memory.used",
        "jvm.gc.max.data.size",
        "jvm.gc.pause",
        "jvm.memory.committed",
        "system.cpu.count",
        "logback.events",
        "jvm.buffer.memory.used",
        "jvm.threads.daemon",
        "system.cpu.usage",
        "jvm.gc.memory.allocated",
        "jvm.threads.live",
        "jvm.threads.peak",
        "process.uptime",
        "http.server.requests",
        "process.cpu.usage",
        "jvm.classes.loaded",
        "jvm.classes.unloaded",
        "jvm.gc.live.data.size",
        "jvm.buffer.count",
        "jvm.buffer.total.capacity",
        "process.start.time"
    ]
}
```



访问`/actuator/metrics/jvm.memory.max`可查看相关指标，转换后可知最大内存为5.2G

```json
{
    "name": "jvm.memory.max",
    "description": "The maximum amount of memory in bytes that can be used for memory management",
    "baseUnit": "bytes",
    "measurements": [
        {
            "statistic": "VALUE",
            "value": 5595725823
        }
    ],
    "availableTags": [
        {
            "tag": "area",
            "values": [
                "heap",
                "nonheap"
            ]
        },
        {
            "tag": "id",
            "values": [
                "Compressed Class Space",
                "PS Survivor Space",
                "PS Old Gen",
                "Metaspace",
                "PS Eden Space",
                "Code Cache"
            ]
        }
    ]
}
```
