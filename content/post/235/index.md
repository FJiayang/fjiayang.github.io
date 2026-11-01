{
  "title": "PXC系列学习笔记（六）——Java千万数据量导入和查询优化 ",
  "date": "2019-12-30T08:49:04+08:00",
  "lastmod": "2019-12-30T08:49:04+08:00",
  "typecho_cid": 235,
  "url": "/archives/235/",
  "comments": false,
  "draft": false,
  "slug": "235",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "SpringBoot",
    "JPA",
    "MySQL",
    "Percona",
    "PXC"
  ],
  "image": "/images/recovered/de47efcb191c722de4a9.png",
  "math": false
}

## 一、介绍

通用导入方法：数据量大应当使用load data方式导入，而不是使用source sql文件的方式

此处为了验证PXC集群性能，需要创造一千万条数据进行SQL语句性能测试



## 二、数据生成

若对数据内容无要求，则可使用通用工具生成随机数据，此处面向具体业务场景，故使用Java应用程序生成数据

### 1. 创建SpringBoot工程

使用SpringBoot快速创建数据导入工程，引入jdbc和jpa依赖

```xml
...
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.2.2.RELEASE</version>
    <relativePath/> <!-- lookup parent from repository -->
</parent>
...
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <scope>runtime</scope>
    </dependency>
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
        <exclusions>
            <exclusion>
                <groupId>org.junit.vintage</groupId>
                <artifactId>junit-vintage-engine</artifactId>
            </exclusion>
        </exclusions>
    </dependency>
</dependencies>
```



### 2. 编写实体类

```java
package top.fjy8018.jdbcbench;

/**
 * @author F嘉阳
 * @date 2019-12-28 13:08
 */
@Entity(name = "tb_test")
@Data
public class DBTest {

    @Id
    private Integer id;

    private String name;
}
```

实现JPA接口

```java
package top.fjy8018.jdbcbench;

/**
 * @author F嘉阳
 * @date 2019-12-28 13:09
 */
public interface DBTestRepository extends JpaRepository<DBTest,Integer> {}
```



### 3. 配置JDBC连接

此处有个重要配置，就是`rewriteBatchedStatements=true`，加上该配置，批量写入数据的性能能提升数百倍。

参考资料：[jdbcTemplate.batchUpdate在批量执行的时候，性能差没有效果，看看怎么解决的。](https://blog.csdn.net/shushugood/article/details/81005718)

![1577623991663](/images/recovered/570ce8f60a535dc9494a.png)

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: admin
    password: password
    url: jdbc:mysql://192.168.1.9:13306/test?useSSL=false&useUnicode=true&characterEncoding=UTF-8&rewriteBatchedStatements=true&serverTimezone=Asia/Shanghai
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 10000
        order_inserts: true
        generate_statistics: true
```



### 4.准备数据库

- 每个PXC分片只开启一个节点，导入一个节点中则不会产生限流，导入完成后拷贝数据文件到其他节点再启动即可

- 修改PXC节点文件，然后重启PXC服务

  ```ini
  ## 不等待事务提交先写入硬盘
  innodb_flush_log_at_trx_commit = 0
  ## 日志数据直接写入磁盘，不进入日志缓冲区
  innodb_flush_method = O_DIRECT
  ## 缓存越大越好
  innodb_buffer_pool_size = 200M
  ```

- 创建t_test数据表

  ```mysql
  CREATE TABLE tb_test(
  	id INT UNSIGNED PRIMARY KEY,
      name VARCHAR(200) NOT NULL
  );
  ```

- 配置MyCat

  ```xml
  <table name="t_test" dataNode="dn1,dn2" rule="mod-long" />
  ```

  ```xml
  <?xml version="1.0"?>
  <!DOCTYPE mycat:schema SYSTEM "schema.dtd">
  <mycat:schema xmlns:mycat="http://io.mycat/">
          <!--配置虚拟逻辑数据表-->
          <schema name="test" checkSQLschema="false" sqlMaxLimit="100">
                  <table name="t_user" dataNode="dn1,dn2" rule="mod-long" />
                  <table name="tb_test" dataNode="dn1,dn2" rule="mod-long" />
                  <table name="t_customer" dataNode="dn1,dn2" rule="sharding-customer">
                       <childTable name="t_orders" primaryKey="ID" joinKey="customer_id" parentKey="id"/>
                  </table>
          </schema>
          <!--配置分片关系-->
          <dataNode name="dn1" dataHost="cluster1" database="test" />
          <dataNode name="dn2" dataHost="cluster2" database="test" />
          <!--配置连接信息-->
          <dataHost name="cluster1" maxCon="1000" minCon="10" balance="0"
                  writeType="0" dbType="mysql" dbDriver="native" switchType="1"
                  slaveThreshold="100">
                  <heartbeat>select user()</heartbeat>
                  <!--多数情况 读多写少-->
                  <writeHost host="W1" url="pxc4:3306" user="admin"
                       password="admin">
                  </writeHost>
          </dataHost>
          <dataHost name="cluster2" maxCon="1000" minCon="10" balance="0"
                  writeType="0" dbType="mysql" dbDriver="native" switchType="1"
                  slaveThreshold="100">
                  <heartbeat>select user()</heartbeat>
                  <!--多数情况 读多写少-->
                  <writeHost host="W1" url="pxc7:3306" user="admin"
                       password="admin">
                  </writeHost>
          </dataHost>
  </mycat:schema>
  
  ```



### 5.编写单元测试

```java
package top.fjy8018.jdbcbench;

@Slf4j
@Component
class JdbcBenchTest extends JdbcBenchApplicationTests{

    @Autowired
    private DBTestRepository repository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    public void insertTest(){
        DBTest t = new DBTest();
        t.setId(1);
        t.setName(1+"，测试实体");
        DBTest save = repository.save(t);
        Assert.notNull(save,"保存测试失败");
    }

    @Test
    public void insertData() throws Exception {
        for (int i = 1; i <= 10000000;) {
            List<DBTest> tests = new LinkedList<>();
            for (int j = 1; j <= 50000; j++) {
                DBTest t = new DBTest();
                t.setId(j+i);
                t.setName(j+i+"，测试实体");
                tests.add(t);
            }
            i = i+50000;
            log.info("插入{}条数据",i);
            batchInsert(tests);
            tests.clear();
        }
    }

    @Transactional
    public void batchInsert(List<DBTest> dbTestList) {
        String sql = "insert into tb_test(id,name) values(?,?)";
        log.info("批次大小：{}",dbTestList.size());
        jdbcTemplate.batchUpdate(sql, new BatchPreparedStatementSetter() {
            public void setValues(PreparedStatement ps, int i) throws SQLException {
                String name = dbTestList.get(i).getName();
                int id = dbTestList.get(i).getId();
                ps.setInt(1, id);
                ps.setString(2, name);
            }
            public int getBatchSize() {
                return dbTestList.size();
            }
        });
    }
}
```

执行单元测试，大约1小时写入完成，不同服务器配置写入性能差距明显，应当以实际为准

## 三、数据导入后的操作

1. 关闭PXC节点(还原配置文件)  
2. 拷贝数据文件到其他PXC节点
3. 关闭 MyCat(还原配置文件) 
4. 启动PC和 MyCat



## 四、大数据性能测试——limit关键字

```sql
SELECT id, name FROM tb_test LIMIT 100, 100;
SELECT id, name FROM tb_test LIMIT 10000, 100;
SELECT id, name FROM tb_test LIMIT 1000000, 100;
SELECT id, name From tb_test LIMIT 5000000, 100;
```

现象：执行最后一条sql语句时速度慢，且cpu和内存占用率极大，**主要对mycat节点内存占用一直居高不下**

分析索引使用情况，rows字段显示其操作了4746302条数据，走全表扫描

| id   | select_type | table   | partitions | type | possible_keys | key  | key_len | ref  | rows    | filtered | Extra |
| ---- | ----------- | ------- | ---------- | ---- | ------------- | ---- | ------- | ---- | ------- | -------- | ----- |
| 1    | SIMPLE      | tb_test |            | ALL  |               |      |         |      | 4746302 | 100      |       |

原因：

- 全表扫描,速度极慢    
- limit语句的查询时间与起始记录的位置成正比  
- mysql limit的语句是很方便,但是对记录很多的表并不适合直接使用
