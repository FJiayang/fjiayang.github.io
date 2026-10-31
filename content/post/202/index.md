{
  "title": "SpringBoot2.x Data JPA 多数据源爬坑",
  "date": "2019-03-30T10:44:00+08:00",
  "lastmod": "2019-03-30T19:23:28+08:00",
  "typecho_cid": 202,
  "url": "/archives/202/",
  "comments": false,
  "draft": false,
  "slug": "202",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "SpringBoot",
    "JPA",
    "源码学习"
  ],
  "math": false
}

## JPA 官方文档

[官方文档](https://docs.spring.io/spring-data/jpa/docs/2.1.5.RELEASE/reference/html/#jpa.java-config)

> #### 5.1.2. Annotation-based Configuration
>
> The Spring Data JPA repositories support can be activated not only through an XML namespace but also by using an annotation through JavaConfig, as shown in the following example:
>
> Example 51. Spring Data JPA repositories using JavaConfig
>
> ```java
> @Configuration
> @EnableJpaRepositories
> @EnableTransactionManagement
> class ApplicationConfig {
> 
>   @Bean
>   public DataSource dataSource() {
> 
>     EmbeddedDatabaseBuilder builder = new EmbeddedDatabaseBuilder();
>     return builder.setType(EmbeddedDatabaseType.HSQL).build();
>   }
> 
>   @Bean
>   public LocalContainerEntityManagerFactoryBean entityManagerFactory() {
> 
>     HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
>     vendorAdapter.setGenerateDdl(true);
> 
>     LocalContainerEntityManagerFactoryBean factory = new LocalContainerEntityManagerFactoryBean();
>     factory.setJpaVendorAdapter(vendorAdapter);
>     factory.setPackagesToScan("com.acme.domain");
>     factory.setDataSource(dataSource());
>     return factory;
>   }
> 
>   @Bean
>   public PlatformTransactionManager transactionManager(EntityManagerFactory entityManagerFactory) {
> 
>     JpaTransactionManager txManager = new JpaTransactionManager();
>     txManager.setEntityManagerFactory(entityManagerFactory);
>     return txManager;
>   }
> }
> ```

文档中说明，基于注解的配置包含三个关键Bean：

- `PlatformTransactionManager`——事务管理
- `LocalContainerEntityManagerFactoryBean`——实体类管理
- `DataSource`——数据源

同时还有一个关键注解`@EnableJpaRepositories`



## SpringBoot官方文档

[官方文档](https://docs.spring.io/spring-boot/docs/2.1.3.RELEASE/reference/htmlsingle/#howto-configure-a-datasource)

多数据源使用`@Primary`指明优先级

> You can even go further by leveraging what `DataSourceProperties` does for you — that is, by providing a default embedded database with a sensible username and password if no URL is provided. You can easily initialize a `DataSourceBuilder` from the state of any `DataSourceProperties` object, so you could also inject the DataSource that Spring Boot creates automatically. However, that would split your configuration into two namespaces: `url`, `username`, `password`, `type`, and `driver` on `spring.datasource` and the rest on your custom namespace (`app.datasource`). To avoid that, you can redefine a custom `DataSourceProperties` on your custom namespace, as shown in the following example:
>
> ```java
> @Bean
> @Primary
> @ConfigurationProperties("app.datasource")
> public DataSourceProperties dataSourceProperties() {
> 	return new DataSourceProperties();
> }
> 
> @Bean
> @ConfigurationProperties("app.datasource.configuration")
> public HikariDataSource dataSource(DataSourceProperties properties) {
> 	return properties.initializeDataSourceBuilder().type(HikariDataSource.class)
> 			.build();
> }
> ```
>
> ## 84.2 Configure Two DataSources
>
> If you need to configure multiple data sources, you can apply the same tricks that are described in the previous section. You must, however, mark one of the `DataSource` instances as `@Primary`, because various auto-configurations down the road expect to be able to get one by type.
>
> If you create your own `DataSource`, the auto-configuration backs off. In the following example, we provide the *exact* same feature set as the auto-configuration provides on the primary data source:
>
> ```java
> @Bean
> @Primary
> @ConfigurationProperties("app.datasource.first")
> public DataSourceProperties firstDataSourceProperties() {
> 	return new DataSourceProperties();
> }
> 
> @Bean
> @Primary
> @ConfigurationProperties("app.datasource.first.configuration")
> public HikariDataSource firstDataSource() {
> 	return firstDataSourceProperties().initializeDataSourceBuilder()
> 			.type(HikariDataSource.class).build();
> }
> 
> @Bean
> @ConfigurationProperties("app.datasource.second")
> public BasicDataSource secondDataSource() {
> 	return DataSourceBuilder.create().type(BasicDataSource.class).build();
> }
> ```



或者使用两个`EntityManagers`，并结合`@EnableJpaRepositories`进行配置

> ## 84.10 Use Two EntityManagers
>
> Even if the default `EntityManagerFactory` works fine, you need to define a new one. Otherwise, the presence of the second bean of that type switches off the default. To make it easy to do, you can use the convenient `EntityManagerBuilder` provided by Spring Boot. Alternatively, you can just the`LocalContainerEntityManagerFactoryBean` directly from Spring ORM, as shown in the following example:
>
> ```java
> // add two data sources configured as above
> 
> @Bean
> public LocalContainerEntityManagerFactoryBean customerEntityManagerFactory(
> 		EntityManagerFactoryBuilder builder) {
> 	return builder
> 			.dataSource(customerDataSource())
> 			.packages(Customer.class)
> 			.persistenceUnit("customers")
> 			.build();
> }
> 
> @Bean
> public LocalContainerEntityManagerFactoryBean orderEntityManagerFactory(
> 		EntityManagerFactoryBuilder builder) {
> 	return builder
> 			.dataSource(orderDataSource())
> 			.packages(Order.class)
> 			.persistenceUnit("orders")
> 			.build();
> }
> ```
>
> The configuration above almost works on its own. To complete the picture, you need to configure `TransactionManagers` for the two `EntityManagers` as well. If you mark one of them as `@Primary`, it could be picked up by the default `JpaTransactionManager` in Spring Boot. The other would have to be explicitly injected into a new instance. Alternatively, you might be able to use a JTA transaction manager that spans both.
>
> If you use Spring Data, you need to configure `@EnableJpaRepositories` accordingly, as shown in the following example:
>
> ```java
> @Configuration
> @EnableJpaRepositories(basePackageClasses = Customer.class,
> 		entityManagerFactoryRef = "customerEntityManagerFactory")
> public class CustomerConfiguration {
> 	...
> }
> 
> @Configuration
> @EnableJpaRepositories(basePackageClasses = Order.class,
> 		entityManagerFactoryRef = "orderEntityManagerFactory")
> public class OrderConfiguration {
> 	...
> }
> ```



## 源码分析



自动装配类中声明了配置Bean和条件装配顺序

```java
package org.springframework.boot.autoconfigure.data.jpa;

/**
 * {@link EnableAutoConfiguration Auto-configuration} for Spring Data's JPA Repositories.
 * <p>
 * Activates when there is a bean of type {@link javax.sql.DataSource} configured in the
 * context, the Spring Data JPA
 * {@link org.springframework.data.jpa.repository.JpaRepository} type is on the classpath,
 * and there is no other, existing
 * {@link org.springframework.data.jpa.repository.JpaRepository} configured.
 * <p>
 * Once in effect, the auto-configuration is the equivalent of enabling JPA repositories
 * using the {@link org.springframework.data.jpa.repository.config.EnableJpaRepositories}
 * annotation.
 * <p>
 * This configuration class will activate <em>after</em> the Hibernate auto-configuration.
 *
 * @author Phillip Webb
 * @author Josh Long
 * @see EnableJpaRepositories
 */
@Configuration
@ConditionalOnBean(DataSource.class)
@ConditionalOnClass(JpaRepository.class)
@ConditionalOnMissingBean({ JpaRepositoryFactoryBean.class,
		JpaRepositoryConfigExtension.class })
@ConditionalOnProperty(prefix = "spring.data.jpa.repositories", name = "enabled", havingValue = "true", matchIfMissing = true)
@Import(JpaRepositoriesAutoConfigureRegistrar.class)
@AutoConfigureAfter({ HibernateJpaAutoConfiguration.class,
		TaskExecutionAutoConfiguration.class })
public class JpaRepositoriesAutoConfiguration {

	@Bean
	@Conditional(BootstrapExecutorCondition.class)
	public EntityManagerFactoryBuilderCustomizer entityManagerFactoryBootstrapExecutorCustomizer(
			Map<String, AsyncTaskExecutor> taskExecutors) {
		return (builder) -> {
			AsyncTaskExecutor bootstrapExecutor = determineBootstrapExecutor(
					taskExecutors);
			if (bootstrapExecutor != null) {
				builder.setBootstrapExecutor(bootstrapExecutor);
			}
		};
	}

	private AsyncTaskExecutor determineBootstrapExecutor(
			Map<String, AsyncTaskExecutor> taskExecutors) {
		if (taskExecutors.size() == 1) {
			return taskExecutors.values().iterator().next();
		}
		return taskExecutors
				.get(TaskExecutionAutoConfiguration.APPLICATION_TASK_EXECUTOR_BEAN_NAME);
	}

	private static final class BootstrapExecutorCondition extends AnyNestedCondition {

		BootstrapExecutorCondition() {
			super(ConfigurationPhase.REGISTER_BEAN);
		}

		@ConditionalOnProperty(prefix = "spring.data.jpa.repositories", name = "bootstrap-mode", havingValue = "deferred", matchIfMissing = false)
		static class DeferredBootstrapMode {

		}

		@ConditionalOnProperty(prefix = "spring.data.jpa.repositories", name = "bootstrap-mode", havingValue = "lazy", matchIfMissing = false)
		static class LazyBootstrapMode {

		}

	}
}
```



引入的配置类中声明了`EnableJpaRepositories`注解

```java
package org.springframework.boot.autoconfigure.data.jpa;

class JpaRepositoriesAutoConfigureRegistrar
		extends AbstractRepositoryConfigurationSourceSupport {

	private BootstrapMode bootstrapMode = null;

	@Override
	protected Class<? extends Annotation> getAnnotation() {
		return EnableJpaRepositories.class;
	}

	@Override
	protected Class<?> getConfiguration() {
		return EnableJpaRepositoriesConfiguration.class;
	}

	@Override
	protected RepositoryConfigurationExtension getRepositoryConfigurationExtension() {
		return new JpaRepositoryConfigExtension();
	}

	@Override
	protected BootstrapMode getBootstrapMode() {
		return (this.bootstrapMode == null) ? super.getBootstrapMode()
				: this.bootstrapMode;
	}

	@Override
	public void setEnvironment(Environment environment) {
		super.setEnvironment(environment);
		configureBootstrapMode(environment);
	}

	private void configureBootstrapMode(Environment environment) {
		String property = environment
				.getProperty("spring.data.jpa.repositories.bootstrap-mode");
		if (StringUtils.hasText(property)) {
			this.bootstrapMode = BootstrapMode
					.valueOf(property.toUpperCase(Locale.ENGLISH));
		}
	}
    
	@EnableJpaRepositories
	private static class EnableJpaRepositoriesConfiguration {}
}
```



`EnableJpaRepositories`注解定义

```java
package org.springframework.data.jpa.repository.config;

/**
 * Annotation to enable JPA repositories. Will scan the package of the annotated configuration class for Spring Data
 * repositories by default.
 *
 * @author Oliver Gierke
 * @author Thomas Darimont
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@Import(JpaRepositoriesRegistrar.class)
public @interface EnableJpaRepositories {

	String[] value() default {};

	String[] basePackages() default {};

	Class<?>[] basePackageClasses() default {};

	Filter[] includeFilters() default {};

	Filter[] excludeFilters() default {};

	String repositoryImplementationPostfix() default "Impl";

	String namedQueriesLocation() default "";

	Key queryLookupStrategy() default Key.CREATE_IF_NOT_FOUND;

	Class<?> repositoryFactoryBeanClass() default JpaRepositoryFactoryBean.class;

	Class<?> repositoryBaseClass() default DefaultRepositoryBaseClass.class;

	/**
	 * 实体管理工厂
	 * @return
	 */
	String entityManagerFactoryRef() default "entityManagerFactory";

	/**
	 * 事务管理
	 * @return
	 */
	String transactionManagerRef() default "transactionManager";

	boolean considerNestedRepositories() default false;

	boolean enableDefaultTransactions() default true;

	/**
	 * Configures when the repositories are initialized in the bootstrap lifecycle. {@link BootstrapMode#DEFAULT}
	 * (default) means eager initialization except all repository interfaces annotated with {@link Lazy},
	 * {@link BootstrapMode#LAZY} means lazy by default including injection of lazy-initialization proxies into client
	 * beans so that those can be instantiated but will only trigger the initialization upon first repository usage (i.e a
	 * method invocation on it). This means repositories can still be uninitialized when the application context has
	 * completed its bootstrap. {@link BootstrapMode#DEFERRED} is fundamentally the same as {@link BootstrapMode#LAZY},
	 * but triggers repository initialization when the application context finishes its bootstrap.
	 * 
	 * @return
	 * @since 2.1
	 */
	BootstrapMode bootstrapMode() default BootstrapMode.DEFAULT;
}
```



查找关键Bean的注册时机

```java
package org.springframework.boot.autoconfigure.orm.jpa;

@Configuration
@ConditionalOnClass({ LocalContainerEntityManagerFactoryBean.class, EntityManager.class })
@Conditional(HibernateEntityManagerCondition.class)
@EnableConfigurationProperties(JpaProperties.class)
@AutoConfigureAfter({ DataSourceAutoConfiguration.class })
@Import(HibernateJpaConfiguration.class)
public class HibernateJpaAutoConfiguration {}
```



进入配置Bean

```java
package org.springframework.boot.autoconfigure.orm.jpa;

@Configuration
@EnableConfigurationProperties(HibernateProperties.class)
@ConditionalOnSingleCandidate(DataSource.class)
class HibernateJpaConfiguration extends JpaBaseConfiguration {}
```



在其父类`JpaBaseConfiguration`中声明了装配时机和条件

```java
package org.springframework.boot.autoconfigure.orm.jpa;

/**
 * 该类在2.0版本进行了重构
 * @since 2.0.0
 */
@Configuration
@EnableConfigurationProperties(JpaProperties.class)
@Import(DataSourceInitializedPublisher.Registrar.class)
public abstract class JpaBaseConfiguration implements BeanFactoryAware {
    
    @Bean
	@ConditionalOnMissingBean
	public PlatformTransactionManager transactionManager() {
		JpaTransactionManager transactionManager = new JpaTransactionManager();
		if (this.transactionManagerCustomizers != null) {
            // 默认使用方法名称
			this.transactionManagerCustomizers.customize(transactionManager);
		}
		return transactionManager;
	}

	@Bean
	@ConditionalOnMissingBean
	public JpaVendorAdapter jpaVendorAdapter() {
		AbstractJpaVendorAdapter adapter = createJpaVendorAdapter();
		adapter.setShowSql(this.properties.isShowSql());
		adapter.setDatabase(this.properties.determineDatabase(this.dataSource));
		adapter.setDatabasePlatform(this.properties.getDatabasePlatform());
		adapter.setGenerateDdl(this.properties.isGenerateDdl());
		return adapter;
	}

	@Bean
	@ConditionalOnMissingBean
	public EntityManagerFactoryBuilder entityManagerFactoryBuilder(
			JpaVendorAdapter jpaVendorAdapter,
			ObjectProvider<PersistenceUnitManager> persistenceUnitManager,
			ObjectProvider<EntityManagerFactoryBuilderCustomizer> customizers) {
		EntityManagerFactoryBuilder builder = new EntityManagerFactoryBuilder(
				jpaVendorAdapter, this.properties.getProperties(),
				persistenceUnitManager.getIfAvailable());
		customizers.orderedStream()
				.forEach((customizer) -> customizer.customize(builder));
		return builder;
	}

	@Bean
	@Primary
	@ConditionalOnMissingBean({ LocalContainerEntityManagerFactoryBean.class,
			EntityManagerFactory.class })
	public LocalContainerEntityManagerFactoryBean entityManagerFactory(
			EntityManagerFactoryBuilder factoryBuilder) {
		Map<String, Object> vendorProperties = getVendorProperties();
		customizeVendorProperties(vendorProperties);
		return factoryBuilder.dataSource(this.dataSource).packages(getPackagesToScan())
				.properties(vendorProperties).mappingResources(getMappingResources())
				.jta(isJta()).build();
	}
}
```



## 测试

爬完文档和源码，对需要配置Bean有了基本了解，新建工程进行多数据源测试

以当前最新版本SpringBoot进行测试



### maven

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.1.3.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>top.fjy8018</groupId>
    <artifactId>jpadatasource</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>jpadatasource</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>1.8</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <scope>runtime</scope>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

### 实体类

通过包路径区分主库和备份库

主库实体类

```java
package top.fjy8018.jpadatasource.entity.primary;

import lombok.Data;

import javax.persistence.Entity;
import javax.persistence.Id;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:11
 */
@Data
@Entity
public class Product {

    @Id
    private Integer id;

    private String name;

    private Integer price;
}
```



备份库实体类

```java
package top.fjy8018.jpadatasource.entity.backup;

import lombok.Data;

import javax.persistence.Entity;
import javax.persistence.Id;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:36
 */
@Data
@Entity(name = "tb_order")
public class Order {

    @Id
    private Integer id;

    private String orderName;

    private Integer price;
}
```

#### 坑一：表名关键字冲突

若此处不指定表名为`tb_order`则会与MySQL关键字冲突导致建表失败

报错：

```
org.hibernate.tool.schema.spi.CommandAcceptanceException: Error executing DDL "
    create table Order (
       id integer not null,
        orderName varchar(255),
        price integer,
        primary key (id)
    ) engine=InnoDB" via JDBC Statement
    ...
```



### DAO

```java
package top.fjy8018.jpadatasource.repository.backup;

import org.springframework.data.jpa.repository.JpaRepository;
import top.fjy8018.jpadatasource.entity.backup.Order;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:12
 */
public interface OrderRepository extends JpaRepository<Order, Integer> {
}
```



```java
package top.fjy8018.jpadatasource.repository.primary;

import org.springframework.data.jpa.repository.JpaRepository;
import top.fjy8018.jpadatasource.entity.primary.Product;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:12
 */
public interface ProductRepository extends JpaRepository<Product, Integer> {
}
```



### 配置Bean

> 官方配置样例：
>
> Both data sources are also bound for advanced customizations. For instance, you could configure them as follows:
>
> ```properties
> app.datasource.first.url=jdbc:mysql://localhost/first
> app.datasource.first.username=dbuser
> app.datasource.first.password=dbpass
> app.datasource.first.configuration.maximum-pool-size=30
> 
> app.datasource.second.url=jdbc:mysql://localhost/second
> app.datasource.second.username=dbuser
> app.datasource.second.password=dbpass
> app.datasource.second.max-total=30
> ```
>
> You can apply the same concept to the secondary `DataSource` as well, as shown in the following example:
>
> ```java
> @Bean
> @Primary
> @ConfigurationProperties("app.datasource.first")
> public DataSourceProperties firstDataSourceProperties() {
> 	return new DataSourceProperties();
> }
> 
> @Bean
> @Primary
> @ConfigurationProperties("app.datasource.first.configuration")
> public HikariDataSource firstDataSource() {
> 	return firstDataSourceProperties().initializeDataSourceBuilder()
> 			.type(HikariDataSource.class).build();
> }
> 
> @Bean
> @ConfigurationProperties("app.datasource.second")
> public DataSourceProperties secondDataSourceProperties() {
> 	return new DataSourceProperties();
> }
> 
> @Bean
> @ConfigurationProperties("app.datasource.second.configuration")
> public BasicDataSource secondDataSource() {
> 	return secondDataSourceProperties().initializeDataSourceBuilder()
> 			.type(BasicDataSource.class).build();
> }
> ```
>
> The preceding example configures two data sources on custom namespaces with the same logic as Spring Boot would use in auto-configuration. Note that each `configuration` sub namespace provides advanced settings based on the chosen implementation.



参照编写配置文件，**此处注意SpringBoot 2.x的驱动变化**

#### 坑二：mysql驱动类名变化

```yaml
spring:
  datasource:
    first:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: financial_adminer
      password: financial_adminer_pass
      url: jdbc:mysql://localhost/jpa_test?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC
      configuration:
        maximum-pool-size: 30
    second:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: financial_adminer
      password: financial_adminer_pass
      url: jdbc:mysql://localhost/jpa_test_bak?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC
      configuration:
        maximum-pool-size: 20

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    database-platform: org.hibernate.dialect.MySQL55Dialect
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
```



配置类

```java
package top.fjy8018.jpadatasource.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:24
 */
@Configuration
public class DataAccessConfig {
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first")
    public DataSourceProperties firstDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first.configuration")
    public HikariDataSource firstDataSource() {
        return firstDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second")
    public DataSourceProperties secondDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second.configuration")
    public HikariDataSource secondDataSource() {
        return secondDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }
}
```



配置完成后发现只在主库自动建表，备份库无变化，属于预期情况，因为目前仅配置了三个必须Bean的其中一个

继续配置实体管理和事务管理Bean

官方文档样例

> ## 84.10 Use Two EntityManagers
>
> Even if the default `EntityManagerFactory` works fine, you need to define a new one. Otherwise, the presence of the second bean of that type switches off the default. To make it easy to do, you can use the convenient `EntityManagerBuilder` provided by Spring Boot. Alternatively, you can just the`LocalContainerEntityManagerFactoryBean` directly from Spring ORM, as shown in the following example:
>
> ```java
> // add two data sources configured as above
> 
> @Bean
> public LocalContainerEntityManagerFactoryBean customerEntityManagerFactory(
> 		EntityManagerFactoryBuilder builder) {
> 	return builder
> 			.dataSource(customerDataSource())
> 			.packages(Customer.class)
> 			.persistenceUnit("customers")
> 			.build();
> }
> 
> @Bean
> public LocalContainerEntityManagerFactoryBean orderEntityManagerFactory(
> 		EntityManagerFactoryBuilder builder) {
> 	return builder
> 			.dataSource(orderDataSource())
> 			.packages(Order.class)
> 			.persistenceUnit("orders")
> 			.build();
> }
> ```
>
> The configuration above almost works on its own. To complete the picture, you need to configure `TransactionManagers` for the two `EntityManagers` as well. If you mark one of them as `@Primary`, it could be picked up by the default `JpaTransactionManager` in Spring Boot. The other would have to be explicitly injected into a new instance. Alternatively, you might be able to use a JTA transaction manager that spans both.
>
> If you use Spring Data, you need to configure `@EnableJpaRepositories` accordingly, as shown in the following example:
>
> ```java
> @Configuration
> @EnableJpaRepositories(basePackageClasses = Customer.class,
> 		entityManagerFactoryRef = "customerEntityManagerFactory")
> public class CustomerConfiguration {
> 	...
> }
> 
> @Configuration
> @EnableJpaRepositories(basePackageClasses = Order.class,
> 		entityManagerFactoryRef = "orderEntityManagerFactory")
> public class OrderConfiguration {
> 	...
> }
> ```



工程配置

```java
package top.fjy8018.jpadatasource.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import top.fjy8018.jpadatasource.entity.backup.Order;
import top.fjy8018.jpadatasource.entity.primary.Product;
import top.fjy8018.jpadatasource.repository.backup.OrderRepository;
import top.fjy8018.jpadatasource.repository.primary.ProductRepository;

import javax.sql.DataSource;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:24
 */
@Configuration
public class DataAccessConfig {
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first")
    public DataSourceProperties firstDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first.configuration")
    public HikariDataSource firstDataSource() {
        return firstDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second")
    public DataSourceProperties secondDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second.configuration")
    public HikariDataSource secondDataSource() {
        return secondDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean firstEntityManagerFactory(
            EntityManagerFactoryBuilder builder, @Qualifier("firstDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages(Product.class)
                .persistenceUnit("first")
                .build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean secondEntityManagerFactory(
            EntityManagerFactoryBuilder builder, @Qualifier("secondDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages(Order.class)
                .persistenceUnit("second")
                .build();
    }

    @Bean
    public PlatformTransactionManager primaryTransactionManager(
            @Qualifier("firstEntityManagerFactory") LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory.getObject());
    }

    @Bean
    public PlatformTransactionManager backupTransactionManager(
            @Qualifier("secondEntityManagerFactory") LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory.getObject());
    }

    @EnableJpaRepositories(basePackageClasses = ProductRepository.class,
            entityManagerFactoryRef = "firstEntityManagerFactory")
    @Primary
    public class PrimaryConfiguration {
    }

    @EnableJpaRepositories(basePackageClasses = OrderRepository.class,
            entityManagerFactoryRef = "secondEntityManagerFactory")
    public class secondConfiguration {
    }
}
```



#### 坑三：官方文档样例有误

此时配置直接启动会报错

```
Method requestMappingHandlerMapping in org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration$EnableWebMvcConfiguration required a single bean, but 2 were found:
	- firstEntityManagerFactory: defined by method 'firstEntityManagerFactory' in class path resource [top/fjy8018/jpadatasource/config/DataAccessConfig.class]
	- secondEntityManagerFactory: defined by method 'secondEntityManagerFactory' in class path resource [top/fjy8018/jpadatasource/config/DataAccessConfig.class]


Action:

Consider marking one of the beans as @Primary, updating the consumer to accept multiple beans, or using @Qualifier to identify the bean that should be consumed

```

意思是自动装配时发现两个类型一致的Bean，主要指定优先级，而官方文档对此处可能出现的问题并未提示

指定`firstEntityManagerFactory`为优先Bean，同时文档样例创建了事务管理器但未配置到`@EnableJpaRepositories`注解中，此处也一并配置

最终配置类如下

```java
package top.fjy8018.jpadatasource.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import top.fjy8018.jpadatasource.entity.backup.Order;
import top.fjy8018.jpadatasource.entity.primary.Product;
import top.fjy8018.jpadatasource.repository.backup.OrderRepository;
import top.fjy8018.jpadatasource.repository.primary.ProductRepository;

import javax.sql.DataSource;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:24
 */
@Configuration
public class DataAccessConfig {
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first")
    public DataSourceProperties firstDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first.configuration")
    public HikariDataSource firstDataSource() {
        return firstDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second")
    public DataSourceProperties secondDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second.configuration")
    public HikariDataSource secondDataSource() {
        return secondDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean firstEntityManagerFactory(
            EntityManagerFactoryBuilder builder, @Qualifier("firstDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages(Product.class)
                .persistenceUnit("first")
                .build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean secondEntityManagerFactory(
            EntityManagerFactoryBuilder builder, @Qualifier("secondDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .packages(Order.class)
                .persistenceUnit("second")
                .build();
    }

    @Bean
    public PlatformTransactionManager primaryTransactionManager(
            @Qualifier("firstEntityManagerFactory") LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory.getObject());
    }

    @Bean
    public PlatformTransactionManager backupTransactionManager(
            @Qualifier("secondEntityManagerFactory") LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory.getObject());
    }

    @EnableJpaRepositories(basePackageClasses = ProductRepository.class,
            entityManagerFactoryRef = "firstEntityManagerFactory", transactionManagerRef = "primaryTransactionManager")
    @Primary
    public class PrimaryConfiguration {
    }

    @EnableJpaRepositories(basePackageClasses = OrderRepository.class,
            entityManagerFactoryRef = "secondEntityManagerFactory", transactionManagerRef = "backupTransactionManager")
    public class secondConfiguration {
    }
}
```



#### 坑四：JPA不会自动建表

配置完成后启动

[![Snipaste_2019-03-30_10-32-35.png](https://i.loli.net/2019/03/30/5c9ed56325a01.png)](https://i.loli.net/2019/03/30/5c9ed56325a01.png)

发现日志中建表SQL没有输出，同时查看数据库，确认表未创建

但官方文档对多数据源的配置说明已经结束，令人疑惑


自动建表语句没生成猜想可能由于与ddl相关的属性未配置导致

进入配置文件查看ddl配置，发现默认为false

[![1553913435794.png](https://i.loli.net/2019/03/30/5c9ed66fb8481.png)](https://i.loli.net/2019/03/30/5c9ed66fb8481.png)

将其配置为true后总配置文件如下

```yaml
spring:
  datasource:
    first:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: financial_adminer
      password: financial_adminer_pass
      url: jdbc:mysql://120.79.226.26/jpa_test?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC
      configuration:
        maximum-pool-size: 30
    second:
      driver-class-name: com.mysql.cj.jdbc.Driver
      username: financial_adminer
      password: financial_adminer_pass
      url: jdbc:mysql://120.79.226.26/jpa_test_bak?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC
      configuration:
        maximum-pool-size: 20

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    database-platform: org.hibernate.dialect.MySQL55Dialect
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
    generate-ddl: true
```

启动工程发现自动建表生效

[![1553913556405.png](https://i.loli.net/2019/03/30/5c9ed6dba2070.png)](https://i.loli.net/2019/03/30/5c9ed6dba2070.png)

查看数据库情况，与预期一致，主库只包含主库的表，备份库只包含备份库的表，多数据配置完成

[![1553913636212.png](https://i.loli.net/2019/03/30/5c9ed727864e4.png)](https://i.loli.net/2019/03/30/5c9ed727864e4.png)







#### 坑五：hibernate默认配置被覆盖

若在单数据源配置下应当无需配置该项，同时发现本应该默认将驼峰属性名映射为`_`拼接名称策略也失效，说明自定义配置源时覆盖了默认配置或者导致默认配置失效

[![1553944509394.png](https://i.loli.net/2019/03/30/5c9f4fca79187.png)](https://i.loli.net/2019/03/30/5c9f4fca79187.png)

查询源码分析原因，发现`hibernate`相关配置均在`HibernateProperties`配置类中

```java
package org.springframework.boot.autoconfigure.orm.jpa;

/**
 * Configuration properties for Hibernate.
 *
 * @author Stephane Nicoll
 * @since 2.1.0
 * @see JpaProperties
 */
@ConfigurationProperties("spring.jpa.hibernate")
public class HibernateProperties {}
```



而该类在`HibernateJpaConfiguration`中进行注入，但配置类中进行了条件装配注解`@ConditionalOnSingleCandidate`标注，导致在多数据源情况下不满足该配置，类没有被装配到Spring Bean中

```java
package org.springframework.boot.autoconfigure.orm.jpa;

/**
 * {@link JpaBaseConfiguration} implementation for Hibernate.
 * @since 2.0.0
 */
@Configuration
@EnableConfigurationProperties(HibernateProperties.class)
@ConditionalOnSingleCandidate(DataSource.class)
class HibernateJpaConfiguration extends JpaBaseConfiguration {

	private final HibernateProperties hibernateProperties;

	HibernateJpaConfiguration(DataSource dataSource, JpaProperties jpaProperties,
			ConfigurableListableBeanFactory beanFactory,
			ObjectProvider<JtaTransactionManager> jtaTransactionManager,
			ObjectProvider<TransactionManagerCustomizers> transactionManagerCustomizers,
			HibernateProperties hibernateProperties,
			ObjectProvider<Collection<DataSourcePoolMetadataProvider>> metadataProviders,
			ObjectProvider<SchemaManagementProvider> providers,
			ObjectProvider<PhysicalNamingStrategy> physicalNamingStrategy,
			ObjectProvider<ImplicitNamingStrategy> implicitNamingStrategy,
			ObjectProvider<HibernatePropertiesCustomizer> hibernatePropertiesCustomizers) {
		super(dataSource, jpaProperties, jtaTransactionManager,
				transactionManagerCustomizers);
		this.hibernateProperties = hibernateProperties;
		this.defaultDdlAutoProvider = new HibernateDefaultDdlAutoProvider(providers);
		this.poolMetadataProvider = new CompositeDataSourcePoolMetadataProvider(
				metadataProviders.getIfAvailable());
		this.hibernatePropertiesCustomizers = determineHibernatePropertiesCustomizers(
				physicalNamingStrategy.getIfAvailable(),
				implicitNamingStrategy.getIfAvailable(), beanFactory,
				hibernatePropertiesCustomizers.orderedStream()
						.collect(Collectors.toList()));
	}
    ...
}
```



解决方法就只能自己工程内实现该类的配置，**注意，Spring 2.x版本自动装配变化较大，当前配置基于最新版2.1.3有效，并不代表对后续版本一定兼容**

工程配置

```java
package top.fjy8018.jpadatasource.config;

import com.zaxxer.hikari.HikariDataSource;
import org.hibernate.boot.model.naming.ImplicitNamingStrategy;
import org.hibernate.boot.model.naming.PhysicalNamingStrategy;
import org.hibernate.cfg.AvailableSettings;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateProperties;
import org.springframework.boot.autoconfigure.orm.jpa.HibernatePropertiesCustomizer;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateSettings;
import org.springframework.boot.autoconfigure.orm.jpa.JpaProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.EmbeddedDatabaseConnection;
import org.springframework.boot.jdbc.SchemaManagement;
import org.springframework.boot.jdbc.SchemaManagementProvider;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.hibernate5.SpringBeanContainer;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.util.ClassUtils;
import top.fjy8018.jpadatasource.entity.backup.Order;
import top.fjy8018.jpadatasource.entity.primary.Product;
import top.fjy8018.jpadatasource.repository.backup.OrderRepository;
import top.fjy8018.jpadatasource.repository.primary.ProductRepository;

import javax.sql.DataSource;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

/**
 * @author F嘉阳
 * @date 2019-03-30 9:24
 */
@Configuration
public class DataAccessConfig {

    private final ObjectProvider<SchemaManagementProvider> providers;

    private final HibernateProperties hibernateProperties;

    private final JpaProperties properties;

    private final ObjectProvider<PhysicalNamingStrategy> physicalNamingStrategy;

    private final ObjectProvider<ImplicitNamingStrategy> implicitNamingStrategy;

    private final ConfigurableListableBeanFactory beanFactory;

    private final ObjectProvider<HibernatePropertiesCustomizer> hibernatePropertiesCustomizers;

    @Autowired
    public DataAccessConfig(ObjectProvider<SchemaManagementProvider> providers, HibernateProperties hibernateProperties, JpaProperties properties, ObjectProvider<PhysicalNamingStrategy> physicalNamingStrategy, ObjectProvider<ImplicitNamingStrategy> implicitNamingStrategy, ConfigurableListableBeanFactory beanFactory, ObjectProvider<HibernatePropertiesCustomizer> hibernatePropertiesCustomizers) {
        this.providers = providers;
        this.hibernateProperties = hibernateProperties;
        this.properties = properties;
        this.physicalNamingStrategy = physicalNamingStrategy;
        this.implicitNamingStrategy = implicitNamingStrategy;
        this.beanFactory = beanFactory;
        this.hibernatePropertiesCustomizers = hibernatePropertiesCustomizers;
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first")
    public DataSourceProperties firstDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.first.configuration")
    public HikariDataSource firstDataSource() {
        return firstDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second")
    public DataSourceProperties secondDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.second.configuration")
    public HikariDataSource secondDataSource() {
        return secondDataSourceProperties().initializeDataSourceBuilder()
                .type(HikariDataSource.class).build();
    }

    @Bean
    @Primary
    public LocalContainerEntityManagerFactoryBean firstEntityManagerFactory(
            EntityManagerFactoryBuilder builder, @Qualifier("firstDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                // 加入规约配置
                .properties(getVendorProperties(dataSource))
                .packages(Product.class)
                .persistenceUnit("first")
                .build();
    }

    @Bean
    public LocalContainerEntityManagerFactoryBean secondEntityManagerFactory(
            EntityManagerFactoryBuilder builder, @Qualifier("secondDataSource") DataSource dataSource) {
        return builder
                .dataSource(dataSource)
                .properties(getVendorProperties(dataSource))
                .packages(Order.class)
                .persistenceUnit("second")
                .build();
    }

    @Bean
    public PlatformTransactionManager primaryTransactionManager(
            @Qualifier("firstEntityManagerFactory") LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory.getObject());
    }

    @Bean
    public PlatformTransactionManager backupTransactionManager(
            @Qualifier("secondEntityManagerFactory") LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory.getObject());
    }

    @EnableJpaRepositories(basePackageClasses = ProductRepository.class,
            entityManagerFactoryRef = "firstEntityManagerFactory", transactionManagerRef = "primaryTransactionManager")
    @Primary
    public class PrimaryConfiguration {
    }

    @EnableJpaRepositories(basePackageClasses = OrderRepository.class,
            entityManagerFactoryRef = "secondEntityManagerFactory", transactionManagerRef = "backupTransactionManager")
    public class secondConfiguration {
    }

    /**
     * 获取配置文件信息
     *
     * @param dataSource
     * @return
     */
    private Map<String, Object> getVendorProperties(DataSource dataSource) {
        List<HibernatePropertiesCustomizer> hibernatePropertiesCustomizers = determineHibernatePropertiesCustomizers(
                physicalNamingStrategy.getIfAvailable(),
                implicitNamingStrategy.getIfAvailable(), beanFactory,
                this.hibernatePropertiesCustomizers.orderedStream()
                        .collect(Collectors.toList()));
        Supplier<String> defaultDdlMode = () -> new HibernateDefaultDdlAutoProvider(providers)
                .getDefaultDdlAuto(dataSource);
        return new LinkedHashMap<>(this.hibernateProperties.determineHibernateProperties(
                properties.getProperties(),
                new HibernateSettings().ddlAuto(defaultDdlMode)
                        .hibernatePropertiesCustomizers(
                                hibernatePropertiesCustomizers)));
    }

    /**
     * 命名策略自动判断
     *
     * @param physicalNamingStrategy
     * @param implicitNamingStrategy
     * @param beanFactory
     * @param hibernatePropertiesCustomizers
     * @return
     */
    private List<HibernatePropertiesCustomizer> determineHibernatePropertiesCustomizers(
            PhysicalNamingStrategy physicalNamingStrategy,
            ImplicitNamingStrategy implicitNamingStrategy,
            ConfigurableListableBeanFactory beanFactory,
            List<HibernatePropertiesCustomizer> hibernatePropertiesCustomizers) {
        List<HibernatePropertiesCustomizer> customizers = new ArrayList<>();
        if (ClassUtils.isPresent(
                "org.hibernate.resource.beans.container.spi.BeanContainer",
                getClass().getClassLoader())) {
            customizers
                    .add((properties) -> properties.put(AvailableSettings.BEAN_CONTAINER,
                            new SpringBeanContainer(beanFactory)));
        }
        if (physicalNamingStrategy != null || implicitNamingStrategy != null) {
            customizers.add(new NamingStrategiesHibernatePropertiesCustomizer(
                    physicalNamingStrategy, implicitNamingStrategy));
        }
        customizers.addAll(hibernatePropertiesCustomizers);
        return customizers;
    }

    /**
     * 自动进行建表操作
     */
    class HibernateDefaultDdlAutoProvider implements SchemaManagementProvider {

        private final Iterable<SchemaManagementProvider> providers;

        HibernateDefaultDdlAutoProvider(Iterable<SchemaManagementProvider> providers) {
            this.providers = providers;
        }

        public String getDefaultDdlAuto(DataSource dataSource) {
            if (!EmbeddedDatabaseConnection.isEmbedded(dataSource)) {
                return "none";
            }
            SchemaManagement schemaManagement = getSchemaManagement(dataSource);
            if (SchemaManagement.MANAGED.equals(schemaManagement)) {
                return "none";
            }
            return "create-drop";

        }

        @Override
        public SchemaManagement getSchemaManagement(DataSource dataSource) {
            return StreamSupport.stream(this.providers.spliterator(), false)
                    .map((provider) -> provider.getSchemaManagement(dataSource))
                    .filter(SchemaManagement.MANAGED::equals).findFirst()
                    .orElse(SchemaManagement.UNMANAGED);
        }

    }

    private static class NamingStrategiesHibernatePropertiesCustomizer
            implements HibernatePropertiesCustomizer {

        private final PhysicalNamingStrategy physicalNamingStrategy;

        private final ImplicitNamingStrategy implicitNamingStrategy;

        NamingStrategiesHibernatePropertiesCustomizer(
                PhysicalNamingStrategy physicalNamingStrategy,
                ImplicitNamingStrategy implicitNamingStrategy) {
            this.physicalNamingStrategy = physicalNamingStrategy;
            this.implicitNamingStrategy = implicitNamingStrategy;
        }

        /**
         * 数据库命名映射策略
         *
         * @param hibernateProperties the JPA vendor properties to customize
         */
        @Override
        public void customize(Map<String, Object> hibernateProperties) {
            if (this.physicalNamingStrategy != null) {
                hibernateProperties.put("hibernate.physical_naming_strategy",
                        this.physicalNamingStrategy);
            }
            if (this.implicitNamingStrategy != null) {
                hibernateProperties.put("hibernate.implicit_naming_strategy",
                        this.implicitNamingStrategy);
            }
        }
    }
}
```



配置Bean完成后则规约配置会生效，便**无需**在配置文件显示配置DDL语句执行开关

启动日志也可看出结果符合预期

[![1553944717550.png](https://i.loli.net/2019/03/30/5c9f50b8df2ea.png)](https://i.loli.net/2019/03/30/5c9f50b8df2ea.png)



[![1553944734003.png](https://i.loli.net/2019/03/30/5c9f50b8d148c.png)](https://i.loli.net/2019/03/30/5c9f50b8d148c.png)



## 总结

由此发现，在SpringBoot版本迁移过程中不一定互相兼容，同时官方文档尽管全面，但随着版本变化文档也有不准确情况。而如果完全依靠爬源码复制源码配置也是无法实现最简单化的配置，需要结合文档、源码、日志逐一分析



工程源码已开放，注意配置自己的数据库连接地址，工程内的连接地址已经失效

[GitHub源码](https://github.com/FJiayang/SpringBoot-Two-DataSources-Demo)
