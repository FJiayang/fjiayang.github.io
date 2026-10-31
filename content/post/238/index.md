{
  "title": "设计模式学习——创建型",
  "date": "2020-02-28T15:26:43+08:00",
  "lastmod": "2020-02-28T15:26:43+08:00",
  "typecho_cid": 238,
  "url": "/archives/238/",
  "comments": false,
  "draft": false,
  "slug": "238",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "设计模式"
  ],
  "math": false
}

## 简单工厂

### 介绍

定义由一个工厂对象决定创建出哪一种产品类的实例

类型：创建型,但不属于GOF23种设计模式



- 工厂类负责创建的对象比较少
- 客户端(应用层)只知道传入工厂类的参数，对于如何创建对象(逻辑)不关心
- 只需要传入一个正确的参数,就可以获取你所需要的对象  而无须知道其创建细节



缺点

- 工厂类的职责相对过重，增加新的产品需要修改工厂类的判断逻辑，违背开闭原则



### 代码样例

类图

![image-20200120153714633](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200120153714633.png)

```java
package top.fjy8018.designpattern.pattern.creational.simplefactory;

import ch.qos.logback.classic.LoggerContext;

import java.util.Calendar;

/**
 * 简单工厂
 * JDK样例 {@link Calendar#getInstance()} 其调用的 {@link Calendar#createCalendar} 就是简单工厂的体现
 * 日志框架样例 {@link org.slf4j.LoggerFactory#getLogger(String)} -> {@link LoggerContext#getLogger(String)}
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
public abstract class AbstractVideo {
    public abstract void produce();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.simplefactory;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
@Slf4j
public class JavaAbstractVideo extends AbstractVideo {
    @Override
    public void produce() {
        log.info("生产Java视频");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.simplefactory;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-09-23 16:14
 */
@Slf4j
public class PythonAbstractVideo extends AbstractVideo {
    @Override
    public void produce() {
        log.info("生产Python视频");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.simplefactory;

/**
 * @author F嘉阳
 * @date 2018-09-23 16:16
 */
public class VideoFactory {

    /**
     * 由工厂负责创建类，业务层无需关心具体实现
     * 其缺点是不符合开闭原则，即如果具体实现类扩展后，工厂类也必须修改
     *
     * @param type
     * @return
     */
    public AbstractVideo getVideo(String type) {
        switch (type) {
            case "Java":
                return new JavaAbstractVideo();
            case "Python":
                return new PythonAbstractVideo();
            default:
                return null;
        }
    }

    /**
     * 通过反射在一定程度弥补简单工厂不足（开闭原则）
     *
     * @param c
     * @return
     */
    public AbstractVideo getVideo(Class c) {
        AbstractVideo video = null;
        try {
            video = (AbstractVideo) Class.forName(c.getName()).newInstance();
        } catch (ClassNotFoundException | IllegalAccessException | InstantiationException e) {
            e.printStackTrace();
        }
        return video;
    }
}
```



测试类

```java
package top.fjy8018.designpattern.pattern.creational.simplefactory;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class AbstractVideoTest {

    /**
     * 不使用简单工厂，则业务层需要引入具体的实现类
     */
    @Test
    void before() {
        AbstractVideo video = new JavaAbstractVideo();
        video.produce();
    }

    /**
     * 使用简单工厂后业务层无需导入具体的实现类，即不关心具体实现过程
     */
    @Test
    void after() {
        VideoFactory factory = new VideoFactory();
        AbstractVideo video = factory.getVideo("Java");
        video.produce();
    }

    /**
     * 通过传递类名方式改进扩展性问题
     */
    @Test
    void improve() {
        VideoFactory factory = new VideoFactory();
        AbstractVideo video = factory.getVideo(JavaAbstractVideo.class);
        video.produce();
    }
}
```



## 工厂方法

### 介绍

定义：定义一个创建对象的接口，但让实现这个接口的类来决定实例化哪个类工厂方法让类的实例化推迟到子类中进行

类型：创建型



特点：

- 创建对象需要大量重复的代码
- 客户端(应用层)不依赖于产品类实例如何被创建、实现等细节
- 一个类通过其子类来指定创建哪个对象

优点：

- 用户只需要关心所需产品对应的工厂,无须关心创建细节
- 加入新产品符合开闭原则,提高可扩展性

缺点：

- 类的个数容易过多,增加复杂度
- 增加了系统的抽象性和理解难度

### 代码样例

类图

![image-20200120160434335](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200120160434335.png)

```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

/**
 * 工厂方法
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
public abstract class AbstractVideo {
    public abstract void produce();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

import sun.misc.Launcher;

import java.util.Collection;

/**
 * 定义一个创建产品对象的工厂接口，将实际创建工作推迟到子类当中
 * 工厂方法抽象类，只提供契约，对于已知的逻辑可以提供默认实现
 * <p>
 * 提高产品与产品族的拓展性
 * <p>
 * JDK源码样例1：{@link java.net.URLStreamHandlerFactory#createURLStreamHandler(String)} -> {@link Launcher.Factory#createURLStreamHandler(String)}
 * JDK源码样例2：{@link Collection#iterator()}
 *
 * @author F嘉阳
 * @date 2018-09-23 16:16
 */
public abstract class AbstractVideoFactory {
    public abstract AbstractVideo getVideo();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

/**
 * @author F嘉阳
 * @date 2018-09-23 20:11
 */
public class JavaAbstractVideoFactory extends AbstractVideoFactory {
    @Override
    public AbstractVideo getVideo() {
        return new JavaVideo();
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体的产品
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
@Slf4j
public class JavaVideo extends AbstractVideo {
    @Override
    public void produce() {
        log.info("生产Java视频");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

/**
 * @author F嘉阳
 * @date 2018-09-23 20:11
 */
public class PythonAbstractVideoFactory extends AbstractVideoFactory {
    @Override
    public AbstractVideo getVideo() {
        return new PythonVideo();
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体的产品
 *
 * @author F嘉阳
 * @date 2018-09-23 16:14
 */
@Slf4j
public class PythonVideo extends AbstractVideo {
    @Override
    public void produce() {
        log.info("生产Python视频");
    }
}
```



测试类

```java
package top.fjy8018.designpattern.pattern.creational.factorymethod;

import org.junit.jupiter.api.Test;

class AbstractVideoFactoryTest {

    @Test
    void getVideo() {
        AbstractVideoFactory factory = new JavaAbstractVideoFactory();
        factory.getVideo().produce();
    }
}
```

## 抽象工厂

### 介绍

定义:抽象工厂模式提供一个创建一系列相关或相互依赖对象的接口

无须指定它们具体的类 

类型：创建型



适用场景

- 客户端（应用层）不依赖于产品类实例如何被创建、实现等细节
- 强调一系列相关的产品对象（属于同一产品族）一起使用创建对象需要大量重复的代码
- 提供一个产品类的库，所有的产品以同样的接口出现，从而使客户端不依赖于具体实现

优点：

- 具体产品在应用层代码隔离,无须关心创建细节
- 将一个系列的产品族统一到一起创建

缺点：

- 规定了所有可能被创建的产品集合，产品族中扩展新的产品困难，需要修改抽象工厂的接口
- 增加了系统的抽象性和理解难度



#### 抽象工程与普通工厂区分

使用抽象工厂易于扩展产品族

![image-20200120161033050](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200120161033050.png)

其与工厂方法区别为：抽象工厂关心产品族，工厂方法关系产品等级

![image-20200120161115607](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200120161115607.png)



### 代码样例

类图

![image-20200120161151908](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200120161151908.png)

```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

/**
 * 工厂方法
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
public abstract class AbstractVideo {
    public abstract void produce();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

/**
 * 工厂方法
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
public abstract class AbstractArticle {
    public abstract void produce();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

/**
 * 抽象工厂：抽象工厂模式可以向客户端提供一个接口，使客户端在不必指定产品的具体的情况下，创建多个<strong>产品族</strong>中的产品对象
 * 使用抽象工厂易于扩展产品族
 * 但抽象工厂不适于新增产品等级，即新增video同级的产品
 * 其与工厂方法区别为：抽象工厂关心产品族，工厂方法关系产品等级
 *
 * JDK源码样例：{@link java.sql.Connection} 该类的实现类都属于同一个产品族
 *
 * @author F嘉阳
 * @date 2018-09-23 22:43
 */
public interface CourseFactory {
    AbstractVideo video();

    AbstractArticle article();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体的产品
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
@Slf4j
public class JavaArticle extends AbstractArticle {
    @Override
    public void produce() {
        log.info("生产Java文章");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体的产品
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
@Slf4j
public class JavaVideo extends AbstractVideo {
    @Override
    public void produce() {
        log.info("生产Java视频");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体的产品
 *
 * @author F嘉阳
 * @date 2018-09-23 16:13
 */
@Slf4j
public class PythonArticle extends AbstractArticle {
    @Override
    public void produce() {
        log.info("生产Python文章");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体的产品
 *
 * @author F嘉阳
 * @date 2018-09-23 16:14
 */
@Slf4j
public class PythonVideo extends AbstractVideo {
    @Override
    public void produce() {
        log.info("生产Python视频");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

/**
 * 从一个产品工厂生产出来的产品一定属于同一个族
 *
 * @author F嘉阳
 * @date 2018-09-23 22:46
 */
public class JavaCourseFactory implements CourseFactory {
    @Override
    public AbstractVideo video() {
        return new JavaVideo();
    }

    @Override
    public AbstractArticle article() {
        return new JavaArticle();
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

/**
 * 从一个产品工厂生产出来的产品一定属于同一个族
 *
 * @author F嘉阳
 * @date 2018-09-23 22:46
 */
public class PythonCourseFactory implements CourseFactory {
    @Override
    public AbstractVideo video() {
        return new PythonVideo();
    }

    @Override
    public AbstractArticle article() {
        return new PythonArticle();
    }
}
```



测试类

```java
package top.fjy8018.designpattern.pattern.creational.abstractfactory;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CourseFactoryTest {

    @Test
    void test() {
        CourseFactory factory = new JavaCourseFactory();
        factory.article().produce();
        factory.video().produce();
    }
}
```



## 建造者

### 介绍

定义:将一个复杂对象的构建与它的表示分离,使得同样的构建过程可以创建不同的表示

用户只需指定需要建造的类型就可以得到它们,建造过程及细节不需要知道

类型：创建型



适用场景

- 如果一个对象有非常复杂的内部结构(很多属性)      
- 想把复杂对象的创建和使用分离

优点：

- 封装性好,刨建和使用分离
- 扩展性好、建造类之间独立、一定程度上解耦

缺点：

- 产生多余的 Builder对象
- 产品内部发生变化,建造者都要修改,成本较大

### 代码样例

类图

![image-20200120164102333](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200120164102333.png)

```java
package top.fjy8018.designpattern.pattern.creational.builder;

/**
 * 建造者抽象类
 *
 * @author F嘉阳
 * @date 2018-09-25 17:15
 */
public abstract class AbstractCourseBuilder {
    public abstract void courseName(String courseName);

    public abstract void coursePPT(String coursePPT);

    public abstract void courseVideo(String courseVideo);

    /**
     * question & answer
     */
    public abstract void courseQA(String courseQA);

    public abstract BCourse build();
}
```



```java
package top.fjy8018.designpattern.pattern.creational.builder;

/**
 * 实体类
 *
 * @author F嘉阳
 * @date 2018-09-25 17:13
 */
public class BCourse {
    private String courseName;
    private String coursePPT;
    private String courseVideo;
    /**
     * question & answer
     */
    private String courseQA;

    public String getCourseName() {
        return courseName;
    }

    public void setCourseName(String courseName) {
        this.courseName = courseName;
    }

    public String getCoursePPT() {
        return coursePPT;
    }

    public void setCoursePPT(String coursePPT) {
        this.coursePPT = coursePPT;
    }

    public String getCourseVideo() {
        return courseVideo;
    }

    public void setCourseVideo(String courseVideo) {
        this.courseVideo = courseVideo;
    }

    public String getCourseQA() {
        return courseQA;
    }

    public void setCourseQA(String courseQA) {
        this.courseQA = courseQA;
    }

    @Override
    public String toString() {
        return "BCourse{" +
                "courseName='" + courseName + '\'' +
                ", coursePPT='" + coursePPT + '\'' +
                ", courseVideo='" + courseVideo + '\'' +
                ", courseQA='" + courseQA + '\'' +
                '}';
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.builder;

/**
 * 教练->建造课程
 *
 * @author F嘉阳
 * @date 2018-09-25 18:54
 */
public class Coach {

    private AbstractCourseBuilder builder;

    public Coach(AbstractCourseBuilder builder) {
        this.builder = builder;
    }

    public BCourse createCourse(String courseName, String coursePPT, String courseVideo, String courseQA) {
        builder.courseName(courseName);
        builder.coursePPT(coursePPT);
        builder.courseVideo(courseVideo);
        builder.courseQA(courseQA);
        return builder.build();
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.builder;

/**
 * 建造者实现类
 *
 * @author F嘉阳
 * @date 2018-09-25 17:17
 */
public class CourseBuilder extends AbstractCourseBuilder {

    private BCourse course = new BCourse();

    @Override
    public void courseName(String courseName) {
        course.setCourseName(courseName);
    }

    @Override
    public void coursePPT(String coursePPT) {
        course.setCoursePPT(coursePPT);
    }

    @Override
    public void courseVideo(String courseVideo) {
        course.setCourseVideo(courseVideo);
    }

    @Override
    public void courseQA(String courseQA) {
        course.setCourseQA(courseQA);
    }

    @Override
    public BCourse build() {
        return course;
    }
}
```



#### 链式调用

```java
package top.fjy8018.designpattern.pattern.creational.builder.chain;

import com.google.common.collect.ImmutableSet;
import org.apache.ibatis.builder.xml.XMLConfigBuilder;
import org.apache.ibatis.parsing.XNode;

import java.io.Reader;

/**
 * 实体类
 * 当只需要构建一个对象时，可以使用建造者，如果构建多个对象或者一类对象，则使用工厂方法或者抽象工厂
 *
 * 用静态内部类建造者，实现链式调用（推荐）
 *
 * JDK源码样例：{@link StringBuilder#append(int)} 和 {@link StringBuffer#append(int)} 区别在于后者对所有append方法加上同步关键字
 * guava源码样例：不可变集合 {@link ImmutableSet.Builder#build()}
 * Spring源码样例：{@link org.springframework.beans.factory.support.BeanDefinitionBuilder}
 * mybatis源码样例：{@link org.apache.ibatis.session.SqlSessionFactoryBuilder#build(Reader)} 封装了读XML的操作
 * 实际调用的是{@link XMLConfigBuilder#parseConfiguration(XNode)} 解析XML节点，将复杂的XML解析过程一次建造完成
 *
 *
 * @author F嘉阳
 * @date 2018-09-25 17:13
 */
public class BuCourse {
    private String courseName;
    private String coursePPT;
    private String courseVideo;
    /**
     * question & answer
     */
    private String courseQA;

    /**
     * 构造器接受静态内部类
     *
     * @param builder
     */
    public BuCourse(BuCourseBuilder builder) {
        this.courseName = builder.courseName;
        this.coursePPT = builder.coursePPT;
        this.courseVideo = builder.courseVideo;
        this.courseQA = builder.courseQA;

    }

    @Override
    public String toString() {
        return "BCourse{" +
                "courseName='" + courseName + '\'' +
                ", coursePPT='" + coursePPT + '\'' +
                ", courseVideo='" + courseVideo + '\'' +
                ", courseQA='" + courseQA + '\'' +
                '}';
    }

    public static class BuCourseBuilder {
        private String courseName;
        private String coursePPT;
        private String courseVideo;
        private String courseQA;

        public BuCourseBuilder courseName(String courseName) {
            this.courseName = courseName;
            return this;
        }

        public BuCourseBuilder coursePPT(String coursePPT) {
            this.coursePPT = coursePPT;
            return this;
        }

        public BuCourseBuilder courseVideo(String courseVideo) {
            this.courseVideo = courseVideo;
            return this;
        }

        public BuCourseBuilder courseQA(String courseQA) {
            this.courseQA = courseQA;
            return this;
        }

        /**
         * 传递静态内部类返回目标对象
         *
         * @return
         */
        public BuCourse build() {
            return new BuCourse(this);
        }

    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.builder;

import com.google.common.collect.ImmutableSet;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.pattern.creational.builder.chain.BuCourse;

import java.util.Set;

@Slf4j
class CourseBuilderTest {

    @Test
    void coachBuild() {
        Coach coach = new Coach(new CourseBuilder());
        BCourse course = coach.createCourse("Java课程", "课程PPT", "课程视频", "课程问答");
        log.info(course.toString());
    }

    @Test
    void chainBuild() {
        BuCourse course = new BuCourse.BuCourseBuilder()
                .courseName("Java课程")
                .coursePPT("课程PPT")
                .courseVideo("课程视频")
                .courseQA("课程问答")
                .build();
        log.info(course.toString());
    }

    /**
     * 不可变集合源码测试
     */
    @Test
    void ImmutableSetBuild() {
        Set<String> set = ImmutableSet.<String>builder().add("f").add("j").add("y").build();
        log.info(set.toString());
    }
}
```

#### 





## 单例模式

### 介绍

定义:保证一个类仅有一个实例,并提供一个全局访问点

适用场景

- 想确保任何情况下都绝对只有一个实例

优点

- 在內存里只有一个实例,减少了内存开销
- 可以避免对资源的多重占用
- 设置全局访问点,严格控制访问

缺点

- 没有接口，扩展困难

重点

- 私有构造器
- 线程安全
- 延迟加载
- 序列化和反序列化安全
- 反射



### 分类

1. 恶汉单例
2. 懒汉单例
3. 双重校验锁
4. 静态内部类
5. 枚举
6. 容器单例
7. ThreadLocal单例



### 代码样例

#### 懒汉单例——线程不安全

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉式单例：延迟加载（线程不安全）
 *
 * @author F嘉阳
 * @date 2018-09-24 10:29
 */
@Slf4j
public class LazySingleton {
    private static LazySingleton lazySingleton = null;

    /**
     * 单例模式构造器必须是屏蔽的
     */
    private LazySingleton() {
    }

    /**
     * 线程不安全
     *
     * @return
     */
    public static LazySingleton getInstance() {
        if (lazySingleton == null) {
            log.debug("LazySingleton实例化");
            lazySingleton = new LazySingleton();
        }
        return lazySingleton;
    }

    /**
     * 线程不安全验证
     *
     * @return
     */
    public static LazySingleton getInstance2() throws InterruptedException {
        if (lazySingleton == null) {
            // 使用线程等待模拟复杂实例化过程，让多线程同时进入该方法
            Thread.sleep(1000);
            log.debug("LazySingleton实例化");
            lazySingleton = new LazySingleton();
        }
        return lazySingleton;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@Slf4j
class LazySingletonTest {

    /**
     * 懒汉式注重延迟加载，当使用时才实例化
     * 可以使用多线程测试方法或者通过多线程Debug方式测试
     */
    @Test
    void getInstanceOneThread() {
        LazySingleton lazySingleton = LazySingleton.getInstance();

    }

    @Test
    void getInstanceMutilThread() throws InterruptedException {

        Thread thread1 = new Thread(new MyRunnable());
        Thread thread2 = new Thread(new MyRunnable());

        thread1.start();
        thread2.start();

        Thread.sleep(3000);
        log.debug("finish");

    }

    private class MyRunnable implements Runnable {
        @Override
        public void run() {
            LazySingleton lazySingleton = null;
            try {
                lazySingleton = LazySingleton.getInstance2();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            log.info(" " + lazySingleton);
        }
    }
}
```



#### 懒汉单例——线程安全

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉式单例：延迟加载（线程安全）
 *
 * @author F嘉阳
 * @date 2018-09-24 10:29
 */
@Slf4j
public class LazySingletonSynchronized {
    private static LazySingletonSynchronized lazySingleton = null;

    /**
     * 单例模式构造器必须是屏蔽的
     */
    private LazySingletonSynchronized() {
        log.debug(LazySingletonSynchronized.class.getSimpleName() + "构造器实例化");
    }

    /**
     * synchronized确保线程安全
     * synchronized用于静态方法是对class文件加锁，用于普通方法则是对堆内存中的实例方法加锁
     * synchronized(LazySingletonSynchronized.class)与在方法名上加锁效果一致
     *
     * @return
     */
    public static LazySingletonSynchronized getInstance() {
        synchronized (LazySingletonSynchronized.class) {
            if (lazySingleton == null) {
                log.debug("LazySingletonSynchronized实例化");
                lazySingleton = new LazySingletonSynchronized();
            }
        }
        return lazySingleton;
    }

    /**
     * 线程安全验证
     *
     * @return
     */
    public synchronized static LazySingletonSynchronized getInstance2() throws InterruptedException {
        if (lazySingleton == null) {
            // 使用线程等待模拟复杂实例化过程，让多线程同时进入该方法
            Thread.sleep(1000);
            log.debug("LazySingletonSynchronized实例化");
            lazySingleton = new LazySingletonSynchronized();
        }
        return lazySingleton;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@Slf4j
class LazySingletonSynchronizedTest {

    @Test
    void getInstance() {
        LazySingletonSynchronized.getInstance();
    }

    @Test
    void getInstance2() throws InterruptedException {
        Thread thread1 = new Thread(new LazySingletonSynchronizedTest.MyRunnable());
        Thread thread2 = new Thread(new LazySingletonSynchronizedTest.MyRunnable());

        thread1.start();
        thread2.start();

        Thread.sleep(3000);
        log.debug("finish");
    }

    private class MyRunnable implements Runnable {
        @Override
        public void run() {
            LazySingletonSynchronized lazySingleton = null;
            try {
                lazySingleton = LazySingletonSynchronized.getInstance2();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            log.info(" " + lazySingleton);
        }
    }
}
```

#### 懒汉单例——双重校验锁（线程安全）

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉式单例：延迟加载（双重校验锁保证线程安全）
 *
 * @author F嘉阳
 * @date 2018-09-24 10:29
 */
@Slf4j
public class LazyDoubleCheckSingleton {
    /**
     * volatile确保内存可见性，同时禁止指令重排
     * volatile会增加一定的汇编代码：
     * 1. 将当前处理器缓存行的数据写回系统内存
     * 2. 写回系统内存后使其他处理器缓存的地址无效，迫使其他处理器从共享内存中同步最新数据
     */
    private volatile static LazyDoubleCheckSingleton lazySingleton = null;

    /**
     * 单例模式构造器必须是屏蔽的
     */
    private LazyDoubleCheckSingleton() {
    }

    /**
     * 双重校验锁确保线程安全
     * 存在指令重排序导致的隐患
     *
     * @return
     */
    public static LazyDoubleCheckSingleton getInstance() {
        // 首次检查
        if (lazySingleton == null) {
            synchronized (LazyDoubleCheckSingleton.class) {
                // 再次检查，在此处加锁比对方法加锁开销更小，因为如果首次检查不为空则直接返回
                if (lazySingleton == null) {
                    log.debug("LazyDoubleCheckSingleton实例化");
                    lazySingleton = new LazyDoubleCheckSingleton();
                    // 实例化包含三个过程，这三个过程可能由于指令重排序导致执行顺序打乱
                    // 但Java底层只保证三个过程在单线程内顺序一致
                    // 1.分配内存
                    // 2.初始化
                    // 3.LazyDoubleCheckSingleton对象指向刚分配的内存地址
                }
            }
        }
        return lazySingleton;
    }

    /**
     * 线程安全验证
     *
     * @return
     */
    public static LazyDoubleCheckSingleton getInstance2() throws InterruptedException {
        if (lazySingleton == null) {
            // 使用线程等待模拟复杂实例化过程，让多线程同时进入该方法
            Thread.sleep(1000);
            synchronized (LazyDoubleCheckSingleton.class) {
                // 再次检查，在此处加锁比对方法加锁开销更小，因为如果首次检查不为空则直接返回
                if (lazySingleton == null) {
                    log.debug("LazyDoubleCheckSingleton实例化");
                    lazySingleton = new LazyDoubleCheckSingleton();
                }
            }
        }
        return lazySingleton;
    }
}
```

#### 静态内部类——延迟加载

##### 原理

JVM在类初始化时会加锁，使用初始化锁可以同步多个线程对一个类的初始化，确保了线程安全类初始化时机

##### 一. 主动引用

虚拟机规范中并没有强制约束何时进行加载，但是规范严格规定了有且只有下列五种情况必须对类进行初始化（加载、验证、准备都会随之发生）：

1. 遇到 `new`、`getstatic`、`putstatic`、`invokestatic` 这四条字节码指令时，如果类没有进行过初始化，则必须先触发其初始化。
最常见的生成这 4 条指令的场景是：
(1) 使用 `new` 关键字实例化对象的时候；
(2) 读取或赋值一个类的静态字段（被 `final` 修饰、已在编译期把结果放入常量池的静态字段除外）的时候；
(3) 以及调用一个类的静态方法的时候。
(4) 使用一个类的非常量静态成员
(5) 若一个类是顶级类，且该类有嵌套的断言语句（少见）

2. 使用`java.lang.reflect`包的方法对类进行反射调用的时候，如果类没有进行初始化，则需要先触发其初始化。
3. 当初始化一个类的时候，如果发现其父类还没有进行过初始化，则需要先触发其父类的初始化。
4. 当虚拟机启动时，用户需要指定一个要执行的主类（包含` main() `方法的那个类），虚拟机会先初始化这个主类；
5. 当使用`JDK 1.7 `的动态语言支持时，如果一个`java.lang.invoke.MethodHandle`
实例最后的解析结果为 `REF_getStatic`, `REF_putStatic`, `REF_invokeStatic `的方法句柄，并且这个方法句柄所对应的类没有进行过初始化，则需要先触发其初始化；

##### 二. 被动引用

以上 5 种场景中的行为称为对一个类进行主动引用。除此之外，所有引用类的方式都不会触发初始化，称为被动引用。被动引用的常见例子包括：

1. 通过子类引用父类的静态字段，不会导致子类初始化。
`System.out.println(SubClass.value);  // value 字段在 SuperClass 中定义`
2. 通过数组定义来引用类，不会触发此类的初始化。该过程会对数组类进行初始化，数组类是一个由虚拟机自动生成的、直接继承自 `Object`的子类，其中包含了数组的属性和方法。
`SuperClass[] sca = new SuperClass[10];`
3. 常量在编译阶段会存入调用类的常量池中，本质上并没有直接引用到定义常量的类，因此不会触发定义常量的类的初始化。
`System.out.println(ConstClass.HELLOWORLD);`

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉单例：静态内部类实现（线程安全）
 * 使用静态内部类可以屏蔽类实例化的重排序,因为非构造线程不允许看到指令重排序
 *
 * @author F嘉阳
 * @date 2018-09-24 13:11
 */
@Slf4j
public class StaticInnerClassSingleton {
    /**
     * 私有构造器是单例必须的
     */
    private StaticInnerClassSingleton() {
        log.debug(StaticInnerClassSingleton.class.getSimpleName() + "构造器实例化");
    }

    /**
     * 开发单例入口
     *
     * @return
     */
    public static StaticInnerClassSingleton getInstance() {
        log.debug(StaticInnerClassSingleton.class.getSimpleName() + "内部类实例化");
        return InnerClass.staticInnerClassSingleton;
    }

    /**
     * 静态内部类
     */
    private static class InnerClass {
        private static StaticInnerClassSingleton staticInnerClassSingleton = new StaticInnerClassSingleton();
    }
}
```



#### 恶汉单例

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

import java.io.Serializable;

/**
 * 单例模式：饿汉式（类加载时初始化）
 * 优点：写法简单，类加载时初始化，线程安全
 * 缺点：若类不被使用则会造成内存浪费
 *
 * JDK源码样例：{@link Runtime} 其实例在类加载时实例化并通过{@link Runtime#getRuntime()} 获取
 *
 * @author F嘉阳
 * @date 2018-09-24 15:38
 */
@Slf4j
public class HungrySingleton implements Serializable {
    /**
     * 类加载时初始化
     * 声明final（可选），只有在类加载时初始化才能声明为final，故懒汉式不能声明为final
     */
    private static final HungrySingleton HUNGRYSINGLETON;

    static {
        log.debug(HungrySingleton.class.getSimpleName() + "静态块实例化");
        HUNGRYSINGLETON = new HungrySingleton();
    }

    /**
     * 该构造器会在反射攻击时调用
     */
    private HungrySingleton() {
        log.debug(HungrySingleton.class.getSimpleName() + "构造器实例化");
    }

    public static HungrySingleton getInstance() {
        return HUNGRYSINGLETON;
    }
}
```

#### 恶汉单例——克隆攻击防御

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

import java.io.Serializable;

/**
 * 单例模式：饿汉式
 * 克隆攻击改进
 * 要么不要实现克隆接口，要么不要调用父类的克隆实现，转而自己实现克隆方法
 *
 * @author F嘉阳
 * @date 2018-09-24 15:38
 */
@Slf4j
public class HungrySingletonCloneableImprove implements Serializable, Cloneable {

    private static final HungrySingletonCloneableImprove HUNGRYSINGLETON;

    static {
        log.debug(HungrySingletonCloneableImprove.class.getSimpleName() + "静态块实例化");
        HUNGRYSINGLETON = new HungrySingletonCloneableImprove();
    }

    private HungrySingletonCloneableImprove() {
        if (HUNGRYSINGLETON != null) {
            throw new RuntimeException("单例模式禁止反射调用");
        }
        log.debug(HungrySingletonCloneableImprove.class.getSimpleName() + "构造器实例化");
    }

    public static HungrySingletonCloneableImprove getInstance() {
        return HUNGRYSINGLETON;
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return HUNGRYSINGLETON;
    }

    /**
     * 解决序列化攻击问题
     *
     * @return
     */
    private Object readResolve() {
        log.debug("序列化获取对象");
        return HUNGRYSINGLETON;
    }
}
```



测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Method;

/**
 * 单例模式克隆攻击
 *
 * @author F嘉阳
 * @date 2018-09-25 22:40
 */
@Slf4j
class SingletonCloneAttack {

    /**
     * 改进前
     */
    @Test
    void before() throws Exception {
        // 正常方式获取单例
        HungrySingletonReflectImprove instance = HungrySingletonReflectImprove.getInstance();
        Method method = instance.getClass().getDeclaredMethod("clone");
        // 由于原本的访问权限为protect，故要改变访问权限
        method.setAccessible(true);
        // 克隆实例
        HungrySingletonReflectImprove instance2 = (HungrySingletonReflectImprove) method.invoke(instance);
        // 验证
        log.info(Integer.toHexString(instance.hashCode()));
        log.info(Integer.toHexString(instance2.hashCode()));
        // 返回false，克隆攻击成功
        log.info(String.valueOf(instance == instance2));
    }

    /**
     * 改进后
     */
    @Test
    void after() throws Exception {
        // 正常方式获取单例
        HungrySingletonCloneableImprove instance = HungrySingletonCloneableImprove.getInstance();
        Method method = instance.getClass().getDeclaredMethod("clone");
        // 由于原本的访问权限为protect，故要改变访问权限
        method.setAccessible(true);
        // 克隆实例
        HungrySingletonCloneableImprove instance2 = (HungrySingletonCloneableImprove) method.invoke(instance);
        // 验证
        log.info(Integer.toHexString(instance.hashCode()));
        log.info(Integer.toHexString(instance2.hashCode()));
        // 返回false，克隆攻击成功
        log.info(String.valueOf(instance == instance2));
    }
}
```



#### 单例模式序列化攻击

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.*;

/**
 * 单例模式序列化攻击
 */
@Slf4j
class SingletonSerializableAttackTest {

    private static final String FILE_NAME = "tmp/singleton_obj.dat";

    @BeforeEach
    void init() {
        File dir = new File("tmp");
        boolean mkdir = false;
        if (!dir.exists()) {
            mkdir = dir.mkdir();
            if (mkdir) {
                log.debug("文件夹新建成功");
            } else {
                log.error("文件夹新建失败");
            }
        }

        File file = new File(FILE_NAME);
        file.deleteOnExit();
    }

    /**
     * 枚举类序列化攻击
     * 原因：{@link ObjectInputStream#readEnum(boolean)} 中对枚举的执行过程是2000 - 2007行
     * 通过枚举的类和名称来获取对象实例，因为枚举的名称在枚举中唯一，所以没有实例化的动作，保证了单例可靠性
     *
     * @throws IOException
     */
    @Test
    void EnumInstanceGetInstance() throws Exception {

        EnumInstance singleton = EnumInstance.getInstance();
        singleton.setData(new Object());

        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(FILE_NAME));
        oos.writeObject(singleton);

        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(FILE_NAME));
        EnumInstance newInstance = (EnumInstance) ois.readObject();

        log.info("写入前：" + singleton.getData());
        log.info("读出后：" + newInstance.getData());
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(newInstance.getData() == singleton.getData()));

        oos.close();
        ois.close();
    }

    /**
     * 通过序列化测试写入和读出后是否属于同一个对象
     * 根据单例模式原则，永远只有一个实例化的对象
     *
     * @throws IOException
     */
    @Test
    void getInstanceBefore() throws IOException, ClassNotFoundException {

        HungrySingleton hungrySingleton = HungrySingleton.getInstance();
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(FILE_NAME));
        oos.writeObject(hungrySingleton);

        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(FILE_NAME));
        HungrySingleton newInstance = (HungrySingleton) ois.readObject();

        log.info("写入前：" + hungrySingleton);
        log.info("读出后：" + newInstance);
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(newInstance == hungrySingleton));

        oos.close();
        ois.close();
    }

    @Test
    void getInstanceAfter() throws IOException, ClassNotFoundException {
        HungrySingletonSerializableImprove before = HungrySingletonSerializableImprove.getInstance();
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(FILE_NAME));
        oos.writeObject(before);

        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(FILE_NAME));
        HungrySingletonSerializableImprove after = (HungrySingletonSerializableImprove) ois.readObject();

        log.info("写入前：" + before);
        log.info("读出后：" + after);
        // 此处结果为true，说明是同一个对象
        log.info(String.valueOf(before == after));

        oos.close();
        ois.close();
    }
}
```



#### 懒汉单例——反射攻击

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

/**
 * 单例模式反射攻击
 */
@Slf4j
class SingletonReflectAttack {
   /**
     * 修复前懒汉式反射攻击
     * 由于反射攻击足够强大，对于非类加载时实例化的单例模式，是无法彻底防止反射攻击的
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void lazySingletonGetInstanceBefore() throws Exception {
        Class clazz = LazySingletonSynchronized.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例
        LazySingletonSynchronized reflectInstance = (LazySingletonSynchronized) constructor.newInstance();
        // 通过正常方式获取
        LazySingletonSynchronized instance = LazySingletonSynchronized.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(reflectInstance == instance));
    }
}
```

#### 懒汉单例——线程安全、反射攻击防御1

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉式单例：延迟加载（线程安全）
 *
 * @author F嘉阳
 * @date 2018-09-24 10:29
 */
@Slf4j
public class LazySingletonSynchronizedReflectImprove1 {
    private static LazySingletonSynchronizedReflectImprove1 lazySingleton = null;

    /**
     * 单例模式构造器必须是屏蔽的
     * 对于非类加载时实例化的单例该方法防止反射攻击无效
     * 因为当反射先执行，则会实例化一个或者N个对象
     * 当正常方式获取单例时，又会实例化多一个对象
     */
    private LazySingletonSynchronizedReflectImprove1() {
        if (lazySingleton != null) {
            throw new RuntimeException("单例模式禁止反射调用");
        }
        log.debug(LazySingletonSynchronizedReflectImprove1.class.getSimpleName() + "构造器实例化");
    }

    /**
     * synchronized确保线程安全
     * synchronized用于静态方法是对class文件加锁，用于普通方法则是对堆内存中的实例方法加锁
     * synchronized(LazySingletonSynchronized.class)与在方法名上加锁效果一致
     *
     * @return
     */
    public static LazySingletonSynchronizedReflectImprove1 getInstance() {
        synchronized (LazySingletonSynchronizedReflectImprove1.class) {
            if (lazySingleton == null) {
                log.debug(LazySingletonSynchronizedReflectImprove1.class.getSimpleName() + "实例化");
                lazySingleton = new LazySingletonSynchronizedReflectImprove1();
            }
        }
        return lazySingleton;
    }

    /**
     * 线程安全验证
     *
     * @return
     */
    public synchronized static LazySingletonSynchronizedReflectImprove1 getInstance2() throws InterruptedException {
        if (lazySingleton == null) {
            // 使用线程等待模拟复杂实例化过程，让多线程同时进入该方法
            Thread.sleep(1000);
            log.debug(LazySingletonSynchronizedReflectImprove1.class.getSimpleName() + "实例化");
            lazySingleton = new LazySingletonSynchronizedReflectImprove1();
        }
        return lazySingleton;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

/**
 * 单例模式反射攻击
 */
@Slf4j
class SingletonReflectAttack {
    /**
     * 用构造器防止单例模式被反射攻击
     * 失败！
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void lazySingletonGetInstanceAfter1() throws Exception {
        Class clazz = LazySingletonSynchronizedReflectImprove1.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例
        LazySingletonSynchronizedReflectImprove1 reflectInstance = (LazySingletonSynchronizedReflectImprove1) constructor.newInstance();
        // 通过正常方式获取
        LazySingletonSynchronizedReflectImprove1 instance = LazySingletonSynchronizedReflectImprove1.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(reflectInstance == instance));
    }
}
```



#### 懒汉单例——线程安全、反射攻击防御2

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉式单例：延迟加载（线程安全）
 *
 * @author F嘉阳
 * @date 2018-09-24 10:29
 */
@Slf4j
public class LazySingletonSynchronizedReflectImprove2 {
    private static LazySingletonSynchronizedReflectImprove2 lazySingleton = null;

    /**
     * 是否能实例化标志
     * 若能实例化，则为{@code true}
     */
    private static boolean flag = true;

    /**
     * 单例模式构造器必须是屏蔽的
     */
    private LazySingletonSynchronizedReflectImprove2() {
        if (!flag) {
            throw new RuntimeException("单例模式禁止反射调用");
        }
        flag = false;
        log.debug(LazySingletonSynchronizedReflectImprove2.class.getSimpleName() + "构造器实例化");
    }

    /**
     * synchronized确保线程安全
     * synchronized用于静态方法是对class文件加锁，用于普通方法则是对堆内存中的实例方法加锁
     * synchronized(LazySingletonSynchronized.class)与在方法名上加锁效果一致
     *
     * @return
     */
    public static LazySingletonSynchronizedReflectImprove2 getInstance() {
        synchronized (LazySingletonSynchronizedReflectImprove2.class) {
            if (lazySingleton == null) {
                log.debug(LazySingletonSynchronizedReflectImprove2.class.getSimpleName() + "实例化");
                lazySingleton = new LazySingletonSynchronizedReflectImprove2();
            }
        }
        return lazySingleton;
    }

    /**
     * 线程安全验证
     *
     * @return
     */
    public synchronized static LazySingletonSynchronizedReflectImprove2 getInstance2() throws InterruptedException {
        if (lazySingleton == null) {
            // 使用线程等待模拟复杂实例化过程，让多线程同时进入该方法
            Thread.sleep(1000);
            log.debug(LazySingletonSynchronizedReflectImprove2.class.getSimpleName() + "实例化");
            lazySingleton = new LazySingletonSynchronizedReflectImprove2();
        }
        return lazySingleton;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

/**
 * 单例模式反射攻击
 */
@Slf4j
class SingletonReflectAttack {
    /**
     * 用标识位防止单例模式被反射攻击
     * 失败！
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void lazySingletonGetInstanceAfter2() throws Exception {
        Class clazz = LazySingletonSynchronizedReflectImprove2.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);

        // 首先通过正常方式获取
        LazySingletonSynchronizedReflectImprove2 instance = LazySingletonSynchronizedReflectImprove2.getInstance();

        // 通过反射修改成员变量
        Field flag = clazz.getDeclaredField("flag");
        // 修改访问权限
        flag.setAccessible(true);
        flag.set(clazz, true);

        // 通过反射获取实例
        LazySingletonSynchronizedReflectImprove2 reflectInstance = (LazySingletonSynchronizedReflectImprove2) constructor.newInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(reflectInstance == instance));
    }
}
```



#### 恶汉单例——反射攻击防御

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

import java.io.Serializable;

/**
 * 单例模式：饿汉式
 * 反射攻击改进
 * 对于在类加载时进行初始化的单例，可以用该方法解决反射攻击问题
 *
 * @author F嘉阳
 * @date 2018-09-24 15:38
 */
@Slf4j
public class HungrySingletonReflectImprove implements Serializable, Cloneable {

    private static final HungrySingletonReflectImprove HUNGRYSINGLETON;

    static {
        log.debug(HungrySingletonReflectImprove.class.getSimpleName() + "静态块实例化");
        HUNGRYSINGLETON = new HungrySingletonReflectImprove();
    }

    private HungrySingletonReflectImprove() {
        if (HUNGRYSINGLETON != null) {
            throw new RuntimeException("单例模式禁止反射调用");
        }
        log.debug(HungrySingletonReflectImprove.class.getSimpleName() + "构造器实例化");
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }

    public static HungrySingletonReflectImprove getInstance() {
        return HUNGRYSINGLETON;
    }

    /**
     * 解决序列化攻击问题
     *
     * @return
     */
    private Object readResolve() {
        log.debug("序列化获取对象");
        return HUNGRYSINGLETON;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

/**
单例模式反射攻击
 */
@Slf4j
class SingletonReflectAttack {

    /**
     * 修复前饿汉式攻击
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void hungrySingletonGetInstanceBefore() throws Exception {
        Class clazz = HungrySingletonSerializableImprove.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例
        HungrySingletonSerializableImprove reflectInstance = (HungrySingletonSerializableImprove) constructor.newInstance();
        // 通过正常方式获取
        HungrySingletonSerializableImprove instance = HungrySingletonSerializableImprove.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(reflectInstance == instance));
    }

    /**
     * 修复后饿汉式攻击
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void hungrySingletonGetInstanceAfter() throws Exception {
        Class clazz = HungrySingletonReflectImprove.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例，此处抛出异常
        HungrySingletonReflectImprove reflectInstance = (HungrySingletonReflectImprove) constructor.newInstance();
        // 通过正常方式获取
        HungrySingletonReflectImprove instance = HungrySingletonReflectImprove.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        log.info(String.valueOf(reflectInstance == instance));
    }
}
```



#### 静态内部类——反射攻击防御

```java
package top.fjy8018.designpattern.pattern.creational.singleton;


import lombok.extern.slf4j.Slf4j;

/**
 * 懒汉单例：静态内部类实现（线程安全）
 * 反射攻击改进
 *
 * @author F嘉阳
 * @date 2018-09-24 13:11
 */
@Slf4j
public class StaticInnerClassSingletonReflectImprove {
    /**
     * 私有构造器是单例必须的
     */
    private StaticInnerClassSingletonReflectImprove() {
        if (InnerClass.staticInnerClassSingleton != null) {
            throw new RuntimeException("单例模式禁止反射调用");
        }
        log.debug(StaticInnerClassSingletonReflectImprove.class.getSimpleName() + "构造器实例化");
    }

    /**
     * 开发单例入口
     *
     * @return
     */
    public static StaticInnerClassSingletonReflectImprove getInstance() {
        log.debug(StaticInnerClassSingletonReflectImprove.class.getSimpleName() + "内部类实例化");
        return InnerClass.staticInnerClassSingleton;
    }

    /**
     * 静态内部类
     * <p>
     * 原理：
     * <strong>JVM在类初始化时会加锁，使用初始化锁可以同步多个线程对一个类的初始化，确保了线程安全</strong>
     * 类初始化时机
     * 一. 主动引用
     * 虚拟机规范中并没有强制约束何时进行加载，但是规范严格规定了有且只有下列五种情况必须对类进行初始化（加载、验证、准备都会随之发生）：
     * 1. 遇到 new、getstatic、putstatic、invokestatic 这四条字节码指令时，如果类没有进行过初始化，则必须先触发其初始化。
     * 最常见的生成这 4 条指令的场景是：
     * (1) 使用 new 关键字实例化对象的时候；
     * (2) 读取或赋值一个类的静态字段（被 final 修饰、已在编译期把结果放入常量池的静态字段除外）的时候；
     * (3) 以及调用一个类的静态方法的时候。
     * (4) 使用一个类的非常量静态成员
     * (5) 若一个类是顶级类，且该类有嵌套的断言语句（少见）
     * <p>
     * 2. 使用 {@link java.lang.reflect} 包的方法对类进行反射调用的时候，如果类没有进行初始化，则需要先触发其初始化。
     * 3. 当初始化一个类的时候，如果发现其父类还没有进行过初始化，则需要先触发其父类的初始化。
     * 4. 当虚拟机启动时，用户需要指定一个要执行的主类（包含 main() 方法的那个类），虚拟机会先初始化这个主类；
     * 5. 当使用 JDK 1.7 的动态语言支持时，如果一个 {@link java.lang.invoke.MethodHandle}
     * 实例最后的解析结果为 REF_getStatic, REF_putStatic, REF_invokeStatic 的方法句柄，并且这个方法句柄所对应的类没有进行过初始化，则需要先触发其初始化；
     * <p>
     * 二. 被动引用
     * 以上 5 种场景中的行为称为对一个类进行主动引用。除此之外，所有引用类的方式都不会触发初始化，称为被动引用。被动引用的常见例子包括：
     * <p>
     * 1. 通过子类引用父类的静态字段，不会导致子类初始化。
     * System.out.println(SubClass.value);  // value 字段在 SuperClass 中定义
     * 2. 通过数组定义来引用类，不会触发此类的初始化。该过程会对数组类进行初始化，数组类是一个由虚拟机自动生成的、直接继承自 {@link Object} 的子类，其中包含了数组的属性和方法。
     * SuperClass[] sca = new SuperClass[10];
     * 3. 常量在编译阶段会存入调用类的常量池中，本质上并没有直接引用到定义常量的类，因此不会触发定义常量的类的初始化。
     * System.out.println(ConstClass.HELLOWORLD);
     */
    private static class InnerClass {
        private static StaticInnerClassSingletonReflectImprove staticInnerClassSingleton = new StaticInnerClassSingletonReflectImprove();
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

/**
单例模式反射攻击
 */
@Slf4j
class SingletonReflectAttack {

    /**
     * 修复前懒汉式攻击
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void staticInnerClassSingletonGetInstanceBefore() throws Exception {
        Class clazz = StaticInnerClassSingleton.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例
        StaticInnerClassSingleton reflectInstance = (StaticInnerClassSingleton) constructor.newInstance();
        // 通过正常方式获取
        StaticInnerClassSingleton instance = StaticInnerClassSingleton.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(reflectInstance == instance));
    }

    /**
     * 修复后懒汉式攻击
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void staticInnerClassSingletonGetInstanceAfter() throws Exception {
        Class clazz = StaticInnerClassSingletonReflectImprove.class;
        Constructor constructor = clazz.getDeclaredConstructor();
        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例
        StaticInnerClassSingletonReflectImprove reflectInstance = (StaticInnerClassSingletonReflectImprove) constructor.newInstance();
        // 通过正常方式获取
        StaticInnerClassSingletonReflectImprove instance = StaticInnerClassSingletonReflectImprove.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance);
        log.info("正常方式：" + instance);
        log.info(String.valueOf(reflectInstance == instance));
    }
}
```





#### 枚举单例（effective java最佳实践）

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;

/**
 * 枚举单例模式（effective Java推荐）
 * 枚举类天生可序列化，有效防止序列化攻击
 * <p>
 * 通过反编译可知：
 * 1. 枚举类的通过final修饰，不能被继承
 * 2. 其构造器私有，不能被调用，如果通过反射强制调用，在newInstance方法中会抛出异常
 * 3. 枚举变量声明为final和static
 * 4. 枚举变量通过静态块实例化（类似饿汉式），所以线程安全
 *
 * @author F嘉阳
 * @date 2018-09-24 20:30
 */
@Slf4j
public enum EnumInstance {
    /**
     * 单例枚举
     */
    INSTANCE {
        @Override
        protected void logTest() {
            log.info(EnumInstance.class.getSimpleName() + "打印输出");
        }
    };

    public static EnumInstance getInstance() {
        return INSTANCE;
    }

    /**
     * 目标实例化对象
     */
    private Object data;

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }

    // 提供外部访问方法入口
    protected abstract void logTest();
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EnumInstanceTest {

    @Test
    void logTest() {
        EnumInstance instance = EnumInstance.getInstance();
        instance.logTest();
    }
}
```

反射攻击测试

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;

/**
单例模式反射攻击
 */
@Slf4j
class SingletonReflectAttack {

    /**
     * 枚举单例反射攻击
     * 枚举类只有一个构造器 {@link Enum#Enum(String, int)}
     * 由于{@link Constructor#newInstance(Object...)} 416行指明枚举类不允许反射实例化，强制实例化会抛{@link IllegalArgumentException}
     * 从底层保证了枚举类无法被反射攻击
     *
     * @throws NoSuchMethodException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     * @throws InstantiationException
     */
    @Test
    void enumInstanceGetInstance() throws Exception {
        Class clazz = EnumInstance.class;
        // 由于枚举类没有无参构造器，需要指定参数
        Constructor constructor = clazz.getDeclaredConstructor(String.class, int.class);

        // 打开访问权限
        constructor.setAccessible(true);
        // 通过反射获取实例
        EnumInstance reflectInstance = (EnumInstance) constructor.newInstance("fjy", 123);
        // 通过正常方式获取
        EnumInstance instance = EnumInstance.getInstance();

        // 判断是否同一个对象
        log.info("反射方式：" + reflectInstance.getData());
        log.info("正常方式：" + instance.getData());
        // 此处结果为false，说明是两个不同的对象
        log.info(String.valueOf(reflectInstance.getData() == instance.getData()));
    }
}
```



#### 容器单例——HashMap

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.config.AbstractFactoryBean;

import java.awt.*;
import java.util.HashMap;
import java.util.Map;

/**
 * 基于容器（集合）实现单例
 * 适用于类加载时有多个对象需要实例化场景
 *
 * JDK源码样例：{@link Desktop#getDesktop()}
 * 其{@link sun.awt.AppContext} 通过{@link HashMap}实现，使用同步保证单例线程安全
 * Spring 源码样例：{@link AbstractFactoryBean#getObject()} 在156行判断当前类是否已经实例化
 * 若没有实例化则在{@link AbstractFactoryBean#getEarlySingletonInstance()}中通过代理方式实例化对象
 *
 * @author F嘉阳
 * @date 2018-09-24 22:31
 */
@Slf4j
public class ContainerSingleton {
    private static Map<String, Object> instancesMap = new HashMap<>();

    private ContainerSingleton() {
    }

    public static void putInstance(String key, Object instance) {
        if (StringUtils.isNotBlank(key) && instance != null) {
            if (!instancesMap.containsKey(key)) {
                instancesMap.put(key, instance);
            }
        }
    }

    public static Object getInstance(String key) {
        return instancesMap.get(key);
    }

    /**
     * 线程安全测试
     *
     * @param key
     * @param instance
     */
    public static void putInstance2(String key, Object instance) throws InterruptedException {
        if (StringUtils.isNotBlank(key) && instance != null) {
            if (!instancesMap.containsKey(key)) {
                Thread.sleep(1000);
                log.debug("放入实例：" + instance);
                instancesMap.put(key, instance);
            }
        }
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

@Slf4j
class ContainerSingletonTest {

    /**
     * 直接使用{@link java.util.HashMap} 只会放入一个值，但后面放的值会覆盖首次放入的值
     *
     * @throws InterruptedException
     */
    @Test
    void getInstanceHashMapUnsafe() throws InterruptedException {
        Thread thread1 = new Thread(new MyHashMapRunnable());
        Thread thread2 = new Thread(new MyHashMapRunnable());

        thread1.start();
        thread2.start();

        Thread.sleep(2000);
        log.debug("finish");
    }

    private class MyHashMapRunnable implements Runnable {
        @Override
        public void run() {
            try {
                ContainerSingleton.putInstance2("object", new Object());
                // 等待其他线程放入对象后取值
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            Object singleton = ContainerSingleton.getInstance("object");
            log.info(" " + singleton);
        }
    }

    private class MyHashtableRunnable implements Runnable {
        @Override
        public void run() {
            try {
                ContainerSingletonHashtable.putInstance2("object", new Object());
                // 等待其他线程放入对象后取值
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            Object singleton = ContainerSingletonHashtable.getInstance("object");
            log.info(" " + singleton);
        }
    }
}
```



#### 容器单例——Hashtable（不推荐）

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.util.Hashtable;
import java.util.Map;

/**
 * 基于容器（集合）实现单例（线程不安全）
 * {@link Hashtable} 实现（不建议）
 *
 * @author F嘉阳
 * @date 2018-09-24 22:31
 */
@Slf4j
public class ContainerSingletonHashtable {
    private static Map<String, Object> instancesMap = new Hashtable<>();

    private ContainerSingletonHashtable() {
    }

    public static void putInstance(String key, Object instance) {
        if (StringUtils.isNotBlank(key) && instance != null) {
            if (!instancesMap.containsKey(key)) {
                instancesMap.put(key, instance);
            }
        }
    }

    public static Object getInstance(String key) {
        return instancesMap.get(key);
    }

    /**
     * 线程安全测试
     *
     * @param key
     * @param instance
     */
    public static void putInstance2(String key, Object instance) throws InterruptedException {
        if (StringUtils.isNotBlank(key) && instance != null) {
            if (!instancesMap.containsKey(key)) {
                Thread.sleep(1000);
                log.debug("放入实例：" + instance);
                instancesMap.put(key, instance);
            }
        }
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

@Slf4j
class ContainerSingletonTest {
    /**
     * 使用{@link java.util.Hashtable} {@link java.util.concurrent.ConcurrentHashMap}可以控制并发，只会放入一个值，但后面放的值会覆盖首次放入的值，效果实际同{@link java.util.HashMap}
     * 对于Hashtable，在一定程度保证线程安全，但影响了性能
     * 对于ConcurrentHashMap，由于使用了静态的ConcurrentHashMap，并直接操作了map，也不是绝对线程安全
     *
     * @throws InterruptedException
     */
    @Test
    void getInstanceHashtableUnsafe() throws InterruptedException {
        Thread thread1 = new Thread(new MyHashtableRunnable());
        Thread thread2 = new Thread(new MyHashtableRunnable());

        thread1.start();
        thread2.start();

        Thread.sleep(2000);
        log.debug("finish");
    }

    private class MyHashMapRunnable implements Runnable {
        @Override
        public void run() {
            try {
                ContainerSingleton.putInstance2("object", new Object());
                // 等待其他线程放入对象后取值
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            Object singleton = ContainerSingleton.getInstance("object");
            log.info(" " + singleton);
        }
    }

    private class MyHashtableRunnable implements Runnable {
        @Override
        public void run() {
            try {
                ContainerSingletonHashtable.putInstance2("object", new Object());
                // 等待其他线程放入对象后取值
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            Object singleton = ContainerSingletonHashtable.getInstance("object");
            log.info(" " + singleton);
        }
    }
}
```



#### ThreadLocal（伪）单例

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import org.apache.ibatis.executor.ErrorContext;

/**
 * 基于{@link ThreadLocalInstance} 的（伪）单例模式，只能保证线程内单例唯一（空间换时间思想）
 *
 * mybatis源码样例：{@link ErrorContext#instance()} 返回通过ThreadLocal实现的单例对象LOCAL
 *
 * @author F嘉阳
 * @date 2018-09-25 16:24
 */
public class ThreadLocalInstance {
    private static ThreadLocal<ThreadLocalInstance> instanceThreadLocal = new ThreadLocal<ThreadLocalInstance>() {
        @Override
        protected ThreadLocalInstance initialValue() {
            return new ThreadLocalInstance();
        }
    };

    private ThreadLocalInstance() {
    }

    /**
     * 其基于{@link java.lang.ThreadLocal.ThreadLocalMap}实现，维护线程隔离，故不用指定key
     *
     * @return
     */
    public static ThreadLocalInstance getInstance() {
        return instanceThreadLocal.get();
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.creational.singleton;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@Slf4j
class ThreadLocalInstanceTest {

    /**
     * {@link ThreadLocal} 只能保证在同一个线程中单例安全
     *
     * @throws InterruptedException
     */
    @Test
    void getInstance() throws InterruptedException {
        // 在主线程中取
        for (int i = 0; i < 5; i++) {
            ThreadLocalInstance instance = ThreadLocalInstance.getInstance();
            log.info(" " + instance);
        }

        Thread thread1 = new Thread(new ThreadLocalInstanceTest.MyRunnable());
        Thread thread2 = new Thread(new ThreadLocalInstanceTest.MyRunnable());

        thread1.start();
        thread2.start();

        Thread.sleep(2000);
        log.debug("finish");
    }

    private class MyRunnable implements Runnable {
        @Override
        public void run() {
            ThreadLocalInstance instance = null;
            try {
                instance = ThreadLocalInstance.getInstance();
            } catch (Exception e) {
                e.printStackTrace();
            }
            log.info(" " + instance);
        }
    }
}
```



## 原型模式

### 介绍

定义：指原型实例指定创建对象的种类，并且通过拷贝这些原型创建新的对象

不需要知道任何创建的细节，不调用构造函数

类型：创建型



适用场景

- 类初始化消耗较多资源
- new产生的一个对象需要非常繁琐的过程（数据准备、访问权限等)
- 构造函数比较复杂
- 循环体中生产大量对象时



优点

- 原型模式性能比直接new一个对象性能高
- 简化创建过程

缺点

- 必须配备克隆方法
- 对克隆复杂对象或对克隆出的对象进行复杂改造时，容易引入风险
- 深拷贝、浅拷贝要运用得当



### 代码样例

#### 改进前

类图

![image-20200121103805342](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200121103805342.png)

```java
package top.fjy8018.designpattern.pattern.creational.prototype.before;

import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;

/**
 * 原型模式：使用原型实例指定待创建对象的类型，并且通过<strong>复制</strong>这个原型来创建新的对象
 * 适用于初始化对象复杂的场景
 * <p>
 * 邮件
 *
 * @author F嘉阳
 * @date 2018-09-25 20:39
 */
@Slf4j
@Getter
@Setter
public class BMail {

    private String name;
    private String emailAddress;
    private String content;

    public BMail() throws InterruptedException {
        // 模拟调用构造器需要复杂过程
        Thread.sleep(100);
        log.debug(this.getClass().getSimpleName() + "构造器调用");
    }

    @Override
    public String toString() {
        return "AMail{" +
                "name='" + name + '\'' +
                ", emailAddress='" + emailAddress + '\'' +
                ", content='" + content + '\'' +
                '}';
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.prototype.before;

import lombok.extern.slf4j.Slf4j;
import top.fjy8018.designpattern.pattern.creational.prototype.before.BMail;

import java.text.MessageFormat;

/**
 * 邮件发送类
 *
 * @author F嘉阳
 * @date 2018-09-25 20:42
 */
@Slf4j
public class BMailUtil {
    public static void sendEmail(BMail mail) {
        String content = "向{0}同学,邮件地址:{1},邮件内容:{2}发送邮件成功";
        log.info(MessageFormat.format(content, mail.getName(), mail.getEmailAddress(), mail.getContent()));
    }

    public static void saveOriginMail(BMail mail) {
        log.info("存储Mail记录，originMailContent：{}", mail.getContent());
    }
}
```





#### 改进后

类图

![image-20200122170719439](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200122170719439.png)



```java
package top.fjy8018.designpattern.pattern.creational.prototype.after;

import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;

/**
 * 原型模式：使用原型实例指定待创建对象的类型，并且通过<strong>复制</strong>这个原型来创建新的对象
 * 适用于初始化对象复杂的场景
 * <p>
 * 邮件
 *
 * @author F嘉阳
 * @date 2018-09-25 20:39
 */
@Slf4j
@Getter
@Setter
public class AMail implements Cloneable {

    private String name;
    private String emailAddress;
    private String content;

    public AMail() throws InterruptedException {
        // 模拟调用构造器需要复杂过程
        Thread.sleep(100);
        log.debug(this.getClass().getSimpleName() + "构造器调用");
    }

    /**
     * 带上父类toString方法查看是否为同一个对象
     *
     * @return
     */
    @Override
    public String toString() {
        return "AMail{" +
                "name='" + name + '\'' +
                ", emailAddress='" + emailAddress + '\'' +
                ", content='" + content + '\'' +
                '}';
    }

    /**
     * 调用克隆函数不需要调用构造器以此加快实例化速度
     *
     * @return
     * @throws CloneNotSupportedException
     */
    @Override
    public Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```



```java
package top.fjy8018.designpattern.pattern.creational.prototype.after;

import lombok.extern.slf4j.Slf4j;

import java.text.MessageFormat;

/**
 * 邮件发送类
 *
 * @author F嘉阳
 * @date 2018-09-25 20:42
 */
@Slf4j
public class AMailUtil {
    public static void sendEmail(AMail mail) {
        String content = "向{0}同学,邮件地址:{1},邮件内容:{2}发送邮件成功";
        log.info(MessageFormat.format(content, mail.getName(), mail.getEmailAddress(), mail.getContent()));
    }

    public static void saveOriginMail(AMail mail) {
        log.info("存储Mail记录，originMailContent：{}", mail.getContent());
    }
}
```



测试类

```java
package top.fjy8018.designpattern.pattern.creational.prototype.before;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.pattern.creational.prototype.after.AMail;
import top.fjy8018.designpattern.pattern.creational.prototype.after.AMailUtil;

import java.util.Date;

@Slf4j
class BMailTest {

    private long start;

    @BeforeEach
    void init() {
        start = System.currentTimeMillis();
    }

    @AfterEach
    void destory() {
        log.debug("耗时{}ms", System.currentTimeMillis() - start);
    }

    /**
     * 每次实例化对象，耗时长——耗时613ms
     *
     * @throws Exception
     */
    @Test
    void before() throws Exception {
        BMail mail = new BMail();
        mail.setContent("原始正文");
        for (int i = 0; i < 5; i++) {
            // 初始化临时发送邮件对象，防止原始正文被最后一个对象覆盖
            BMail tempMail = new BMail();
            tempMail.setName("学员" + i);
            tempMail.setContent("正文" + i);
            tempMail.setEmailAddress("地址" + i);
            BMailUtil.sendEmail(tempMail);
        }
        // 本意希望在发送完所有邮件后保存开始的正文
        BMailUtil.saveOriginMail(mail);

    }

    /**
     * 调用克隆方法（浅拷贝，因为没有对每个属性实现克隆方法），显然速度更快——耗时110ms
     *
     * @throws Exception
     */
    @Test
    void after() throws Exception {
        AMail mail = new AMail();
        mail.setContent("原始正文");
        // 通过hashCode查看是否为同一个对象
        log.debug(Integer.toHexString(mail.hashCode()));
        for (int i = 0; i < 5; i++) {
            // 初始化临时发送邮件对象，防止原始正文被最后一个对象覆盖
            AMail tempMail = (AMail) mail.clone();
            tempMail.setName("学员" + i);
            tempMail.setContent("正文" + i);
            tempMail.setEmailAddress("地址" + i);
            AMailUtil.sendEmail(tempMail);
            log.debug(Integer.toHexString(tempMail.hashCode()));
        }
        // 本意希望在发送完所有邮件后保存开始的正文
        AMailUtil.saveOriginMail(mail);
    }
}
```



### 深克隆实现

#### 改进前

```java
package top.fjy8018.designpattern.pattern.creational.prototype.clone;

import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;

import java.util.Date;

/**
 * 原型模式：使用原型实例指定待创建对象的类型，并且通过<strong>复制</strong>这个原型来创建新的对象
 * 适用于初始化对象复杂的场景
 * <p>
 * 邮件
 *
 * @author F嘉阳
 * @date 2018-09-25 20:39
 */
@Slf4j
@Getter
@Setter
public class CMailBefore implements Cloneable {

    private String name;
    private Date date;
    private String content;

    public CMailBefore() throws InterruptedException {
        // 模拟调用构造器需要复杂过程
        Thread.sleep(100);
        log.debug(this.getClass().getSimpleName() + "构造器调用");
    }

    /**
     * 带上父类toString方法查看是否为同一个对象
     *
     * @return
     */
    @Override
    public String toString() {
        return "CMailBefore{" +
                "name='" + name + '\'' +
                ", date=" + date +
                ", content='" + content + '\'' +
                '}';
    }

    /**
     * 调用克隆函数不需要调用构造器以此加快实例化速度
     * 通过调用每个属性的克隆方法实现深克隆
     *
     * @return
     * @throws CloneNotSupportedException
     */
    @Override
    public Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```



#### 改进后

```java
package top.fjy8018.designpattern.pattern.creational.prototype.clone;

import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.cache.CacheKey;

import java.util.ArrayList;
import java.util.Date;

/**
 * 原型模式：使用原型实例指定待创建对象的类型，并且通过<strong>复制</strong>这个原型来创建新的对象
 * 适用于初始化对象复杂的场景
 * <p>
 * 邮件——深克隆实现
 *
 * JDK源码样例：{@link ArrayList#clone()} 通过元素拷贝实现
 * mybatis源码样例：{@link CacheKey#clone()} 通过重新初始化一个对象再进行数组拷贝实现
 *
 * @author F嘉阳
 * @date 2018-09-25 20:39
 */
@Slf4j
@Getter
@Setter
public class CMailAfter implements Cloneable {

    private String name;
    /**
     * String类型本身是不可变，不需要重新实现深克隆
     */
    private Date date;
    private String content;

    public CMailAfter() throws InterruptedException {
        // 模拟调用构造器需要复杂过程
        Thread.sleep(100);
        log.debug(this.getClass().getSimpleName() + "构造器调用");
    }

    /**
     * 带上父类toString方法查看是否为同一个对象
     *
     * @return
     */
    @Override
    public String toString() {
        return "CMailAfter{" +
                "name='" + name + '\'' +
                ", date=" + date +
                ", content='" + content + '\'' +
                '}';
    }

    /**
     * 调用克隆函数不需要调用构造器以此加快实例化速度
     * 通过调用每个属性的克隆方法实现深克隆
     *
     * @return
     * @throws CloneNotSupportedException
     */
    @Override
    public Object clone() throws CloneNotSupportedException {
        CMailAfter mail = (CMailAfter) super.clone();
        // 单独对Date进行克隆
        mail.date = (Date) date.clone();
        return mail;
    }
}
```



### 集合类实现

#### 改进前

```java
package top.fjy8018.designpattern.pattern.creational.prototype.clone;

import lombok.Getter;
import lombok.Setter;

import java.util.Date;
import java.util.List;

/**
 * 对集合类原型模式实现
 *
 * @author F嘉阳
 * @date 2018-09-25 22:59
 */
@Getter
@Setter
public class ListCloneBefore implements Cloneable {
    private String name;
    private List<Date> dateList;

    @Override
    public String toString() {
        return "ListCloneBefore{" +
                "name='" + name + '\'' +
                ", dateList=" + dateList +
                '}';
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```



#### 改进后

```java
package top.fjy8018.designpattern.pattern.creational.prototype.clone;

import lombok.Getter;
import lombok.Setter;
import org.apache.ibatis.cache.CacheKey;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * 对集合类原型模式实现
 *
 * @author F嘉阳
 * @date 2018-09-25 22:59
 */
@Getter
@Setter
public class ListCloneAfter implements Cloneable {
    private String name;
    private List<Date> dateList;

    @Override
    public String toString() {
        return "ListCloneBefore{" +
                "name='" + name + '\'' +
                ", dateList=" + dateList +
                '}';
    }

    /**
     * 重新实现集合类属性值拷贝方法，模仿{@link CacheKey#clone()}
     *
     * @return
     * @throws CloneNotSupportedException
     */
    @Override
    protected Object clone() throws CloneNotSupportedException {
        ListCloneAfter newInstance = (ListCloneAfter) super.clone();
        newInstance.setDateList(new ArrayList<>(this.dateList));
        return newInstance;
    }
}
```
