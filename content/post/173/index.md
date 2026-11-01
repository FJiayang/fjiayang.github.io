{
  "title": "maven构建多模块SpringBoot项目遇到的坑",
  "date": "2018-08-07T21:22:00+08:00",
  "lastmod": "2023-09-07T14:29:46+08:00",
  "typecho_cid": 173,
  "url": "/archives/173/",
  "comments": false,
  "draft": false,
  "slug": "173",
  "categories": [
    "默认分类"
  ],
  "tags": [],
  "math": true
}

## 依赖模块报错：程序包不存在 ##
### 问题描述 ###
使用SprinCloud构建的多模块项目，各应用使用Springboot构建，工程编写完毕，在模块中添加构建配置
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
![请输入图片描述][1]

使用maven命令构建应用`mvn install package -DskipTests`
maven报错如下
![请输入图片描述][2]

### 问题分析 ###

 1. 通过报错看出，只要有依赖外部模块的均报“程序包不存在”或者“找不到符号”的错误，而通过IDEA运行工程均正常，故排除代码错误，猜测为构建错误
 2. 查询到公共模块要先打包，故对公共包执行了一次install，再打包子模块，失败
 3. 百度查找问题解决办法，做了如下尝试
    （1）配置maven中的jdk版本，确保小版本号也是一致的，无果
    （2）更换构建配置如下，无效
        <build>
        	<plugins>
        		<plugin>
        			<groupId>org.apache.maven.plugins</groupId>
        			<artifactId>maven-compiler-plugin</artifactId>
        		</plugin>
        		<plugin>
        			<groupId>org.springframework.boot</groupId>
        			<artifactId>spring-boot-maven-plugin</artifactId>
        		</plugin>
        	</plugins>
        </build>
    （3）使用不同的maven命令构建，包括clean、package、install等，报错信息相同
 4. 突然发现有人的博客说明了公共包不应该加入构建配置，否则会二次构建，导致找不到包
[来源][3]
> 注意！注意！这里有一个巨坑，我已经义无反顾的跳进去一次了，大家一定不要再往里面跳了：Common打包出来的应该是不可执行的jar包，所以不要在Common的pom中定义spring-boot-maven-plugin插件，因为这个SpringBoot插件会在Maven的package后进行二次打包，目的为了生成可执行jar包，如果C中定义了这个插件，会报错提示没有找到main函数。这时你就可以去打包front项目了，当然打包的时候可能还是不行，这里还有一个小坑，如果还是不能进行打包的话，那么就install一下root项目，也就是总目录下的pom文件对应的install操作，这样再打包front项目基本上就没有问题了，老铁，都是经验呀，希望对你们有帮助
根据博客说法去除了公共包的构建配置，依然报错
## 解决方法 ##
根据博客说法思考了一下，考虑到父工程也没有主类，无需运行，故去除父工程的构建配置，最后添加了构建模块只有带启动类的模块，再次对整个父工程执行clean->install，构建成功
![请输入图片描述][4]


  [1]: /images/recovered/cc91cdde749517d2568a.png
  [2]: /images/recovered/e7af7f2448909fdc2288.png
  [3]: https://blog.csdn.net/liqi_q/article/details/80557157
  [4]: /images/recovered/1b062d122899b871d034.png
