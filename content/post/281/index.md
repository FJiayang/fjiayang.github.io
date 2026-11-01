{
  "title": "GraphQL实践8——Netflix Dgs Graphql代码生成",
  "date": "2022-10-28T21:57:00+08:00",
  "lastmod": "2022-10-28T21:58:06+08:00",
  "typecho_cid": 281,
  "url": "/archives/281/",
  "comments": false,
  "draft": false,
  "slug": "281",
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
DGS官方开发了识别`schema`配置生成对应类型、测试类的代码生成器，而Maven插件则由社区维护

## Maven代码生成插件

### 新增依赖
```xml
<dependency>  
    <groupId>com.netflix.graphql.dgs.codegen</groupId>  
    <artifactId>graphql-dgs-codegen-client-core</artifactId>  
    <version>5.1.17</version>  
</dependency>
```

还需要新增构建插件
```xml
	    <plugin>
                <groupId>io.github.deweyjose</groupId>
                <artifactId>graphqlcodegen-maven-plugin</artifactId>
                <version>1.24</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>generate</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <addGeneratedAnnotation>true</addGeneratedAnnotation>
                    <packageName>top.fjy8018.graphsqldemo.generated</packageName>
                    <schemaPaths>
                        <param>src/main/resources/graphql/actor.graphqls</param>
                    </schemaPaths>
                    <!-- 生成测试客户端 -->
                    <generateClient>true</generateClient>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>build-helper-maven-plugin</artifactId>
                <executions>
                    <execution>
                        <phase>generate-sources</phase>
                        <goals>
                            <goal>add-source</goal>
                        </goals>
                        <configuration>
                            <sources>
                                <source>${project.build.directory}/generated-sources</source>
                            </sources>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
```

插件配置指引：[deweyjose/graphqlcodegen: Maven port of the Netflix Gradle code generation plugin for graphql.](https://github.com/deweyjose/graphqlcodegen)



### 编译

执行

```shell
mvn clean package
```
即可生成对应的类

![image-20221028212820748](/images/recovered/5977b035d674171ca4f4.png)



### 存在问题

IDEA默认不识别target目录下的资源文件，生成后会导致无法引用

![image-20221028213042840](/images/recovered/a230791d358e4659c26c.png)



#### 解决方法

需要手动将对应的生成目录配置为Source Root即可

![image-20221028213010859](/images/recovered/584b1a4fd7700822ea89.png)

![image-20221028213109840](/images/recovered/62ba92c91ac00fa2819e.png)



## 总结

DGS官方推荐开发者优先使用代码生成器生成标准类库后再开发，可以减少开发量
