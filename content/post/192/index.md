{
  "title": "Spring Data JPA 知识记录",
  "date": "2018-12-09T17:04:00+08:00",
  "lastmod": "2020-03-13T14:14:06+08:00",
  "typecho_cid": 192,
  "url": "/archives/192/",
  "comments": false,
  "draft": false,
  "slug": "192",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "JPA",
    "Spring",
    "MySQL"
  ],
  "math": false
}

## jpa方法命名规则

关键字 | 方法命名 | sql where字句
---|--- |---
And | findByNameAndPwd | where name= ? and pwd =?
Or | findByNameOrSex | where name= ? or sex=?
Is,Equals | findById,findByIdEquals | where id= ?
Between | findByIdBetween | where id between ? and ?
LessThan | findByIdLessThan | where id < ?
LessThanEquals | findByIdLessThanEquals | where id <= ?
GreaterThan | findByIdGreaterThan | where id > ?
GreaterThanEquals | findByIdGreaterThanEquals | where id > = ?
After | findByIdAfter | where id > ?
Before | findByIdBefore | where id < ?
IsNull | findByNameIsNull | where name is null
isNotNull,NotNull | findByNameNotNull | where name is not null
Like | findByNameLike | where name like ?
NotLike | findByNameNotLike | where name not like ?
StartingWith | findByNameStartingWith | where name like '?%'
EndingWith | findByNameEndingWith | where name like '%?'
Containing | findByNameContaining | where name like '%?%'
OrderBy | findByIdOrderByXDesc | where id=? order by x desc
Not | findByNameNot | where name <> ?
In | findByIdIn(Collection<?> c) | where id in (?)
NotIn | findByIdNotIn(Collection<?> c) | where id not  in (?)
TRUE | findByAaaTue | where aaa = true
FALSE | findByAaaFalse | where aaa = false
IgnoreCase | findByNameIgnoreCase | where UPPER(name)=UPPER(?)

## 常用注解
### 自动生成时间和修改者
@CreatedDate、@CreatedBy、@LastModifiedDate、@LastModifiedBy

在spring jpa中，支持在字段或者方法上进行注解@CreatedDate、@CreatedBy、@LastModifiedDate、@LastModifiedBy，从字面意思可以很清楚的了解，这几个注解的用处。

@CreatedDate
表示该字段为创建时间时间字段，在这个实体被insert的时候，会设置值

@CreatedBy
表示该字段为创建人，在这个实体被insert的时候，会设置值

@LastModifiedDate、@LastModifiedBy同理。

## 自动建表引擎设置

使用SpringDataJpa自动建表默认为MyISAM，而主流大多数场景都需要使用InnoDB，可通过配置文件配置即可

```yaml
spring:
  jpa:
    database-platform: org.hibernate.dialect.MySQL55Dialect
```

**注意：类名有所变化**

早期通过网上搜索的类名都说为`org.hibernate.dialect.MySQL5InnoDBDialect`，当实际测试时发现引擎依然为MyISAM，通过进一步查询源码发现早期类名已经弃用

```java
/*
 * Hibernate, Relational Persistence for Idiomatic Java
 *
 * License: GNU Lesser General Public License (LGPL), version 2.1 or later.
 * See the lgpl.txt file in the root directory or <http://www.gnu.org/licenses/lgpl-2.1.html>.
 */
package org.hibernate.dialect;

/** A Dialect for MySQL 5 using InnoDB engine
 *
 * @author Gavin King,
 * @author Scott Marlow
 * @deprecated Use "hibernate.dialect.storage_engine=innodb" environment variable or JVM system property instead.
 */
@Deprecated
public class MySQL5InnoDBDialect extends MySQL5Dialect {

	@Override
	protected MySQLStorageEngine getDefaultMySQLStorageEngine() {
		return InnoDBStorageEngine.INSTANCE;
	}
}

```

但注释里并没有指明新的替代类名，而是建议通过配置实现，但SpringDataJpa自动装配的类里没有支持该配置，故如果不单独引入hibernate依赖是无法使用该配置的

最后在`stackoverflow`上看到解决方案：[where to put hibernate.dialect.storage_engine property](https://stackoverflow.com/questions/48062256/where-to-put-hibernate-dialect-storage-engine-property)

即使用新的类名`org.hibernate.dialect.MySQL55Dialect`替换即可，尽管两个类名初看没差别，实际上差了一个数字`5`，影响比较大

## MySQL驱动变化

在使用了新版的驱动类后，不管是MyBatis还是Jpa，都会报时区不一致和报错信息乱码的错误需要将连接URL更新

新配置

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 
    url: jdbc:mysql://localhost/pw_manager?useSSL=false&useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC
```

原配置

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.jdbc.Driver
    username: cmsspringcloud
    password: cmsdbadmin
    url: jdbc:mysql://localhost:3306/cms_springcloud?characterEncoding=utf-8&useSSL=false
```
