{
  "title": "Mapstruct爬坑记录",
  "date": "2021-02-20T22:45:11+08:00",
  "lastmod": "2021-02-20T22:45:11+08:00",
  "typecho_cid": 267,
  "url": "/archives/267/",
  "comments": false,
  "draft": false,
  "slug": "267",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "MapStruct"
  ],
  "math": false
}

## 背景

众所周知，Spring框架提供了著名的类拷贝工具`BeanUtils`，其使用简单、方便。

但是其内部实现基于运行时反射进行同名属性拷贝，对于需要进行字段映射和高性能运行时场景都无法满足要求，因此，开源社区衍生出了以下的类拷贝框架

- [MapStruct (编译期生成 Mapper 实现)](http://mapstruct.org/)
- [Selma (编译期生成 Mapper 实现)](http://www.selma-java.org/)
- [yangtu222 - BeanUtils (第一次生成 copy 实现字节码)](https://github.com/yangtu222/BeanUtils)
- [mica (第一次生成 copy 实现字节码)](https://github.com/lets-mica/mica)
- [hutool (反射)](https://gitee.com/loolly/hutool)

## 使用

目前第二代密码管理平台采用的是`mica`重写后的`BeanUtil`类拷贝方法，整体来说性能可以满足要求，但为了进一步提升查询时类转换性能，同时考虑到应用中本身就包含了`swagger`依赖，而`swagger`中本身就引入了`mapstruct`依赖包，故无需引入新依赖。

因此，最终考虑将业务场景下的类拷贝改成`Mapstruct`实现，由此开始`mapstruct`爬坑之路。。



### 软件包版本

SpringBoot:2.4.2

SpringCloud:2020.0.1

lombok: 1.18.16

mapstruct: 1.3.1.Final



### 新增依赖

由于需要由mapstruct根据定义的接口自动生成类转换实现，故需要引入mapstruct接口处理包，有两种方式，一种通过maven插件的形式，一种通过maven依赖的形式

maven插件的形式（官方推荐）

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.5.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
                <annotationProcessorPaths>
                    <path>
                        <groupId>org.mapstruct</groupId>
                        <artifactId>mapstruct-processor</artifactId>
                        <version>${org.mapstruct.version}</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

maven依赖的形式

```xml
<dependency>
    <groupId>org.mapstruct</groupId>
    <artifactId>mapstruct-processor</artifactId>
    <version>${mapstruct.version}</version>
</dependency>
```



考虑到平台的maven模块数量较大，互相依赖关系比较复杂，遗漏插件依赖容易导致难以排查的bug，最终采用第二种方式，减少编码量。



### 新增映射类

```java
/**
 * @author F嘉阳
 * @date 2021/2/18 12:06
 */
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.IGNORE)
public interface OssEntityMapper {

	OssVO ossToOssVO(Oss oss);

	OssDTO ossToOssDto(Oss oss);

	/**
	 * bladeFile转Oss
	 *
	 * @param bladeFile
	 * @return
	 */
	@Mapping(target = "fileName", source = "name")
	Oss bladeFileToOss(BladeFile bladeFile);
}
```



### 新增单元测试

由于首次使用mapstruct，编写单元测试检测代码是否成功

```java
/**
 * @author F嘉阳
 * @date 2021/2/18 14:23
 */
@Slf4j
@ExtendWith(BladeSpringExtension.class)
@SpringBootTest(classes = ResourceApplication.class)
@BladeBootTest(appName = AppConstant.APPLICATION_RESOURCE_NAME, profile = "test", enableLoader = true)
class OssEntityMapperTest {

	@Autowired
	private OssEntityMapper mapper;

	@Test
	void ossToOssVO() {
		Oss oss = new Oss();
		oss.setFileName("filename");
		oss.setLink("link");
		oss.setOriginalName("origin");
		oss.setOssType(OssType.QI_NIU_OSS);
		oss.setIsDeleted(BladeConstant.DB_NOT_DELETED);
		OssVO ossVO = mapper.ossToOssVO(oss);
		assertEquals("filename", ossVO.getFileName());
		assertEquals("link", ossVO.getLink());
		assertEquals("origin", ossVO.getOriginalName());
	}

	@Test
	void ossToOssDto() {
		Oss oss = new Oss();
		oss.setFileName("filename");
		oss.setLink("link");
		oss.setOriginalName("origin");
		oss.setOssType(OssType.QI_NIU_OSS);
		oss.setIsDeleted(BladeConstant.DB_NOT_DELETED);
		OssDTO ossDTO = mapper.ossToOssDto(oss);
		assertEquals("filename", ossDTO.getFileName());
		assertEquals("link", ossDTO.getLink());
		assertEquals("origin", ossDTO.getOriginalName());
	}

	@Test
	void bladeFileToOss() {
		BladeFile file = new BladeFile();
		file.setName("file");
		file.setLink("link");
		file.setOriginalName("origin");
		Oss oss = mapper.bladeFileToOss(file);
		assertEquals("file", oss.getFileName());
		assertEquals("link", oss.getLink());
		assertEquals("origin", oss.getOriginalName());
	}
}
```



### 编译结果

编译结果，报错

![1613831019363](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1613831019363.png)



这就很奇怪了，这是按官网最简单的方式写的，而且IDEA也安装了mapstruct插件，也没报错，能正确识别属性，怎么编译就不通过了

查看生成的代码，确实没有属性映射

## 爬坑之路

由于编译报错，考虑以下方法解决

1. 移除`spring`容器依赖，采用类引用的方式编写。——无效

2. 移除属性映射，尝试编译，可以编译通过，但生成的代码没有同名属性映射，只会返回空值。——无效

   ```java
   @Override
   public Oss bladeFileToOss(BladeFile bladeFile) {
       if ( bladeFile == null ) {
           return null;
       }
   
       Oss oss = new Oss();
   
       return oss;
   }
   ```

3. 更换类名后测试通过，多次测试仍然有不通过的情况。——可能和编译环境有关？

4. 相同代码放在单独的工程（非`maven`多模块）测试通过。——可能和`maven`多模块依赖有关？

5. 根据网上检索的结果，普遍反映的`lombok`版本太低导致的，经过检查，当前的`lombok`版本应该是满足最低版本要求的。——无效

6. 考虑是否和`spring`某些组件冲突，单独新开[maven多模块工程](https://github.com/FJiayang/mapstruct-test)测试，依然测试不通过。——果然和maven有关？



## 解决方法

最终通过给官方仓库提交[issue](https://github.com/mapstruct/mapstruct/issues/2361)咨询得到答案

![1613831616294](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1613831616294.png)

原来是`lombok`版本太高导致的。。

最终降低`lombok`版本问题解决。
