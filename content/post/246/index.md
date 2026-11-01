{
  "title": "设计模式学习——行为型",
  "date": "2020-07-22T16:50:17+08:00",
  "lastmod": "2020-07-22T16:50:17+08:00",
  "typecho_cid": 246,
  "url": "/archives/246/",
  "comments": false,
  "draft": false,
  "slug": "246",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "源码学习",
    "设计模式"
  ],
  "math": false
}

## 模板方法模式

### 介绍

定义:定义了一个算法的骨架,并允许子类为一个或多个步骤提供实现    

模板方法使得子类可以在不改变算法结构的情况下,重新定义算法的某些步骤    

类型：行为型



适用场景

- 一次性实现一个算法的不变的部分,并将可变的行为留给子类来实现          
- 各子类中公共的行为被提取出来并集中到一个公共父类中,  从而避免代码重复



优点

- 提高复用性
- 提高扩展性
- 符合开闭原则



缺点

- 类数目增加      
- 增加了系统实现的复杂度
- 继承关系自身缺点,如果父类添加新的抽象方法,所有子类都要改一遍



分类和扩展

- 钩子方法
  - 提供了默认的行为，子类可以在必要时进行扩展



相关设计模式

- 模板方法模式和工厂方法模式
  - 工厂方法是模板方法的一种特殊实现
- 模板方法模式和策略模式
  - 策略模式在于实现算法可以互相替换而不影响应用层，不改变算法流程
  - 模板方法定义了一个算法的骨架，不明确的交给子类实现，可以改变算法流程

### 代码样例

类图

![image-20200304112909684](/images/recovered/0b8dfe205550cb6b28bd.png)

抽象课程

```java
package top.fjy8018.designpattern.pattern.behavior.templatemethod;

import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.mapping.MappedStatement;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Collection;

/**
 * 抽象课程
 * <p>
 * {@link java.util.AbstractList} 提供抽象List实现
 * 例如 {@link java.util.AbstractList#addAll(int, Collection)} 定义通过模板
 * {@link java.util.AbstractMap} 同理
 * <p>
 * {@link javax.servlet.http.HttpServlet#doGet(HttpServletRequest, HttpServletResponse)} 也是模板定义
 * {@link org.apache.ibatis.executor.BaseExecutor#doUpdate(MappedStatement, Object)} 等方法交由子类实现
 * 例如 {@link org.apache.ibatis.executor.SimpleExecutor#doUpdate(MappedStatement, Object)}
 *
 * @author F嘉阳
 * @date 2020/3/4 10:59
 */
@Slf4j
public abstract class ACourse {

    /**
     * 固定不变的行为
     * 定义模板，不允许子类覆盖，防止影响流程执行顺序
     */
    protected final void makeCourse() {
        this.makePPT();
        this.makeVideo();
        // 调用可选方法
        if (needWriteArticle()) {
            this.writeArticle();
        }
        this.packageCourse();
    }

    /**
     * 固定不变的行为
     * 满足所有子类需求
     */
    final void makePPT() {
        log.info("制作PPT");
    }

    final void makeVideo() {
        log.info("制作视频");
    }

    /**
     * 可选行为
     * <p>
     * 手记可写可不写，但写的手记的流程还是一致的，故也声明为final
     * 通过定义钩子方法，允许子类覆盖
     */
    final void writeArticle() {
        log.info("编写手记");
    }

    /**
     * 钩子方法，提供默认实现
     *
     * @return
     */
    protected boolean needWriteArticle() {
        return false;
    }

    /**
     * 必须实现的行为
     * 课程内容打包
     */
    abstract void packageCourse();
}
```

具体课程实现

```java
package top.fjy8018.designpattern.pattern.behavior.templatemethod;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体课程实现
 *
 * @author F嘉阳
 * @date 2020/3/4 11:05
 */
@Slf4j
public class JavaCourse extends ACourse {
    /**
     * 必须实现的行为
     * 课程内容打包
     */
    @Override
    void packageCourse() {
        log.info("提供Java学习课程源码");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.behavior.templatemethod;

import lombok.extern.slf4j.Slf4j;

/**
 * 具体课程实现
 * @author F嘉阳
 * @date 2020/3/4 11:06
 */
@Slf4j
public class VueCourse extends ACourse {

    private boolean needWriteArticleFlag = false;

    /**
     * 通过构造器开放给实例决定
     * @param needWriteArticleFlag
     */
    public VueCourse(boolean needWriteArticleFlag) {
        this.needWriteArticleFlag = needWriteArticleFlag;
    }

    /**
     * 必须实现的行为
     * 课程内容打包
     */
    @Override
    void packageCourse() {
        log.info("提供Vue学习课程源码");
        log.info("提供Vue学习课程多媒体素材");
    }

    /**
     * 钩子方法，提供默认实现
     *
     * @return
     */
    @Override
    protected boolean needWriteArticle() {
        return this.needWriteArticleFlag;
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.behavior.templatemethod;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/3/4 11:08
 */
@Slf4j
class ACourseTest {

    @Test
    void makeJavaCourse() {
        ACourse javaCourse = new JavaCourse();
        javaCourse.makeCourse();
    }

    @Test
    void makeVueCourse() {
        ACourse vueCourse = new VueCourse(true);
        vueCourse.makeCourse();
    }
}
```



输出

```
11:27:56.942 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.ACourse - 制作PPT
11:27:56.957 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.ACourse - 制作视频
11:27:56.957 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.JavaCourse - 提供Java学习课程源码


11:27:56.969 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.ACourse - 制作PPT
11:27:56.969 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.ACourse - 制作视频
11:27:56.969 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.ACourse - 编写手记
11:27:56.969 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.VueCourse - 提供Vue学习课程源码
11:27:56.969 [main] INFO top.fjy8018.designpattern.pattern.behavior.templatemethod.VueCourse - 提供Vue学习课程多媒体素材
```



## 迭代器模式

### 介绍

定义提供一种方法,顺序访问一个集合对象中的各个元素,而又不暴露  该对象的内部表示

类型：行为型



适用场景

- 访问一个集合对象的内容而无需暴露它的内部表示          
- 为遍历不同的集合结构提供一个统一的接口



优点

- 分离了集合对象的遍历行为



缺点

- 类的个数成对增加



相关设计模式

- 迭代器模式和访问者模式
  - 访问者模式扩展开放的部分，再作用于对象的操作上
  - 迭代器模式扩展开放的部分，再作用于对象的种类上



### 代码样例

迭代器一般使用现成的，而不会自己实现

类图

![image-20200304151240323](/images/recovered/146b9aba85ee3b088a72.png)

课程接口

```java
package top.fjy8018.designpattern.pattern.behavior.iterator;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * @author F嘉阳
 * @date 2020/3/4 14:49
 */
@AllArgsConstructor
@Getter
public class Course {

    private String name;

}
```



迭代器

```java
package top.fjy8018.designpattern.pattern.behavior.iterator;

import java.util.ArrayList;

/**
 * JDK迭代器
 * {@link java.util.Iterator}
 * 集合内部类实现 {@link ArrayList.Itr#hasNext()}
 * 同时做了进一步扩展 {@link ArrayList.ListItr}
 *
 * mybatis中 {@link org.apache.ibatis.cursor.defaults.DefaultCursor}
 * 其持有游标迭代器对象 {@link org.apache.ibatis.cursor.defaults.DefaultCursor.CursorIterator}
 *
 * @author F嘉阳
 * @date 2020/3/4 14:49
 */
public interface CourseIterator {

    /**
     * 获取下一个课程
     *
     * @return
     */
    Course nextCourse();

    /**
     * 是否是最后一个课程
     * @return
     */
    boolean isLastCourse();
}
```



迭代器实现

```java
package top.fjy8018.designpattern.pattern.behavior.iterator;

import lombok.extern.slf4j.Slf4j;

import java.util.List;

/**
 * @author F嘉阳
 * @date 2020/3/4 14:50
 */
@Slf4j
public class CourseIteratorImpl implements CourseIterator {

    private List courseList;

    private int position;

    private Course course;

    public CourseIteratorImpl(List courseList){
        this.courseList=courseList;
    }

    @Override
    public Course nextCourse() {
        log.info("返回课程,位置是: {}",position);
        course=(Course)courseList.get(position);
        position++;
        return course;
    }

    @Override
    public boolean isLastCourse(){
        if(position< courseList.size()){
            return false;
        }
        return true;
    }
}
```





对课程进行处理

```java
package top.fjy8018.designpattern.pattern.behavior.iterator;

/**
 * 对课程进行处理
 *
 * @author F嘉阳
 * @date 2020/3/4 14:48
 */
public interface CourseAggregate {

    void addCourse(Course course);

    void removeCourse(Course course);

    /**
     * 获取课程迭代器
     * @return
     */
    CourseIterator getCourseIterator();
}
```

实现

```java
package top.fjy8018.designpattern.pattern.behavior.iterator;

import java.util.ArrayList;
import java.util.List;

/**
 * @author F嘉阳
 * @date 2020/3/4 14:50
 */
public class CourseAggregateImpl implements CourseAggregate {

    private List courseList;

    public CourseAggregateImpl() {
        this.courseList = new ArrayList();
    }

    @Override
    public void addCourse(Course course) {
        courseList.add(course);
    }

    @Override
    public void removeCourse(Course course) {
        courseList.remove(course);
    }

    @Override
    public CourseIterator getCourseIterator() {
        return new CourseIteratorImpl(courseList);
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.behavior.iterator;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/3/4 14:52
 */
@Slf4j
class CourseIteratorTest {

    @Test
    void nextCourse() {
        Course course1 = new Course("Java电商一期");
        Course course2 = new Course("Java电商二期");
        Course course3 = new Course("Java设计模式精讲");
        Course course4 = new Course("Python课程");
        Course course5 = new Course("算法课程");
        Course course6 = new Course("前端课程");


        CourseAggregate courseAggregate = new CourseAggregateImpl();

        courseAggregate.addCourse(course1);
        courseAggregate.addCourse(course2);
        courseAggregate.addCourse(course3);
        courseAggregate.addCourse(course4);
        courseAggregate.addCourse(course5);
        courseAggregate.addCourse(course6);

        log.info("-----课程列表-----");
        printCourses(courseAggregate);

        courseAggregate.removeCourse(course4);
        courseAggregate.removeCourse(course5);

        log.info("-----删除操作之后的课程列表-----");
        printCourses(courseAggregate);
    }

    public static void printCourses(CourseAggregate courseAggregate){
        CourseIterator courseIterator= courseAggregate.getCourseIterator();
        while(!courseIterator.isLastCourse()){
            Course course=courseIterator.nextCourse();
            log.info(course.getName());
        }
    }
}
```



输出

```
15:18:23.089 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - -----课程列表-----
15:18:23.124 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 0
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Java分布式
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 1
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Java系统设计
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 2
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Java设计模式精讲
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 3
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Python课程
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 4
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - 算法课程
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 5
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - 前端课程
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - -----删除操作之后的课程列表-----
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 0
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Java分布式
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 1
15:18:23.126 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Java系统设计
15:18:23.127 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 2
15:18:23.127 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - Java设计模式精讲
15:18:23.132 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorImpl - 返回课程,位置是: 3
15:18:23.132 [main] INFO top.fjy8018.designpattern.pattern.behavior.iterator.CourseIteratorTest - 前端课程
```



## 策略模式

### 介绍

定义：定义了算法家族,分别封装起来,让它们之间可以互相替换,  此模式让算法的变化不会影响到使用算法的用户。    

例如有大量if…else的情况

类型：行为型



适用场景

- 系统有很多类，而他们的区别仅仅在于他们的行为不同
- 一个系统需要动态地在几种算法中选择一种



优点

- 开闭原则
- 避免使用多重条件转移语句
- 提高算法的保密性和安全性



缺点

- 客户端必须知道所有的策略类,并自行决定使用哪一个策略类。              
- 产生很多策略类



相关设计模式

- 策略模式和工厂模式
- 策略模式和状态模式



### 代码样例

#### 改造前——初级策略模式

无法避免if…else

类图

![image-20200304160526066](/images/recovered/410ac72bfcf946b959aa.png)

促销接口

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

/**
 * 促销接口
 *
 * @author F嘉阳
 * @date 2020/3/4 15:37
 */
public interface PromotionStrategy {

    void doPromotion();
}
```



满减促销策略

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import lombok.extern.slf4j.Slf4j;

/**
 * 满减促销策略
 *
 * @author F嘉阳
 * @date 2020/3/4 15:38
 */
@Slf4j
public class ManJianPromotionStrategy implements PromotionStrategy {
    @Override
    public void doPromotion() {
        log.info("满减促销，满200-20");
    }
}
```

立减促销策略

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import lombok.extern.slf4j.Slf4j;

/**
 * 立减促销策略
 *
 * @author F嘉阳
 * @date 2020/3/4 15:39
 */
@Slf4j
public class LiJianPromotionStrategy implements PromotionStrategy{
    @Override
    public void doPromotion() {
        log.info("立减促销，课程价格直接减去配置的价格");
    }
}
```

返现促销策略

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import lombok.extern.slf4j.Slf4j;

/**
 * 返现促销策略
 *
 * @author F嘉阳
 * @date 2020/3/4 15:38
 */
@Slf4j
public class FanXianPromotionStrategy implements PromotionStrategy{
    @Override
    public void doPromotion() {
        log.info("返现促销，返回金额存放到用户余额中");
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/3/4 15:46
 */
@Slf4j
class PromotionStrategyTest {

    @Test
    void existIfElse() {
        String promotionKey = "LIJIAN";
        PromotionActivity activity = null;
        if (StringUtils.equals(promotionKey,"LIJIAN")){
            // 方法和类本身线程安全
            activity= new PromotionActivity(new LiJianPromotionStrategy());
        }else if(StringUtils.equals(promotionKey,"MANJIAN")){
            activity = new PromotionActivity(new FanXianPromotionStrategy());
        }

        activity.executePromotionStrategy();
    }
}
```

输出

```
16:08:28.582 [main] INFO top.fjy8018.designpattern.pattern.behavior.strategy.LiJianPromotionStrategy - 立减促销，课程价格直接减去配置的价格
```



#### 改造后——结合工厂和策略模式

类图

![image-20200304170326421](/images/recovered/87c00fd83735f267bacc.png)

空促销策略

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import lombok.extern.slf4j.Slf4j;

/**
 * 空策略
 *
 * @author F嘉阳
 * @date 2020/3/4 16:16
 */
@Slf4j
public class EmptyPromotionStrategy implements PromotionStrategy {
    @Override
    public void doPromotion() {
        log.info("空促销策略");
    }
}
```



促销策略工厂

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory;
import org.springframework.beans.factory.support.CglibSubclassingInstantiationStrategy;
import org.springframework.beans.factory.support.SimpleInstantiationStrategy;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.PathResource;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 促销策略工厂
 * <p>
 * {@link java.util.Comparator} 比较器，类似于抽象策略，有大量实现类，所有具体策略都要实现定义好的接口方法
 * 例如 {@link com.google.common.collect.ExplicitOrdering}
 * 应用层可以逐级传递比较器 {@link Arrays#sort(Object[], Comparator)}
 * {@link java.util.TreeMap#compare(Object, Object)} 利用内部的比较器处理
 * <p>
 * Spring资源策略抽象 {@link org.springframework.core.io.Resource}
 * 提供大量策略实现 {@link PathResource} {@link FileSystemResource}
 * <p>
 * {@link org.springframework.beans.factory.support.InstantiationStrategy} 初始化策略接口
 * 初始化具体策略实现 {@link SimpleInstantiationStrategy} {@link CglibSubclassingInstantiationStrategy}
 * 初始化策略在 {@link AbstractAutowireCapableBeanFactory} 中被使用
 *
 * @author F嘉阳
 * @date 2020/3/4 16:09
 */
public class PromotionStrategyFactory {

    private static Map<String, PromotionStrategy> STRATEGY_MAP = new ConcurrentHashMap<>();

    /**
     * 无促销
     */
    private static final PromotionStrategy NON_PROMOTION = new EmptyPromotionStrategy();

    static {
        STRATEGY_MAP.put(PromotionKey.FANXIAN, new FanXianPromotionStrategy());
        STRATEGY_MAP.put(PromotionKey.MANJIAN, new ManJianPromotionStrategy());
        STRATEGY_MAP.put(PromotionKey.LIJIAN, new LiJianPromotionStrategy());
    }

    /**
     * 禁止实例化
     */
    private PromotionStrategyFactory() {
    }

    /**
     * 开放获取策略的方法
     *
     * @param promotionKey
     * @return
     */
    public static PromotionStrategy getPromotionStrategy(String promotionKey) {
        PromotionStrategy strategy = STRATEGY_MAP.get(promotionKey);
        return strategy == null ? NON_PROMOTION : strategy;
    }

    /**
     * 常量定义
     */
    private interface PromotionKey {
        String LIJIAN = "LIJIAN";
        String FANXIAN = "FANXIAN";
        String MANJIAN = "MANJIAN";
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.behavior.strategy;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.junit.jupiter.api.Test;

/**
 * @author F嘉阳
 * @date 2020/3/4 15:46
 */
@Slf4j
class PromotionStrategyTest {

    @Test
    void nonIfElse() {
        String promotionKey = "LIJIAN";
        PromotionActivity activity = new PromotionActivity(PromotionStrategyFactory.getPromotionStrategy(promotionKey));
        activity.executePromotionStrategy();
    }
}
```

输出

```
16:08:28.582 [main] INFO top.fjy8018.designpattern.pattern.behavior.strategy.LiJianPromotionStrategy - 立减促销，课程价格直接减去配置的价格
```



## 解释器模式

### 介绍

- 定义：给定一个语言，定义它的文法的一种表示，并定义一个解释器，这个解释器使用该表示来解释语言中的句子。
- 为了解释一种语言，而为语言创建的解释器
- 类型：行为型



适用场景（较少）

- 某个特定类型问题发生频率足够高



优点

- 语法由很多类表示,容易改变及扩展此语言



缺点

- 当语法规则数目太多时,增加了系统复杂度



相关设计模式

- 解释器模式和适配器模式



### 代码样例

类图

![image-20200305151426324](/images/recovered/308c611331535c5d99b4.png)

解释器

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

/**
 * 解释器
 * <p>
 * JDK 源码
 * {@link java.util.regex.Pattern} 正则解释器
 * {@link org.springframework.expression.spel.standard.SpelExpressionParser} Spring解释器
 *
 * @author F嘉阳
 * @date 2020/3/5 14:45
 */
public interface Interpreter {
    int interpret();
}
```

加法解释器

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

/**
 * 加法解释器
 *
 * @author F嘉阳
 * @date 2020/3/5 14:46
 */
public class AddInterpreter implements Interpreter {

    /**
     * 定义两个表达式
     */
    private Interpreter firstExpression, secondExpression;

    public AddInterpreter(Interpreter firstExpression, Interpreter secondExpression) {
        this.firstExpression = firstExpression;
        this.secondExpression = secondExpression;
    }

    @Override
    public int interpret() {
        // 此时传入为NumberInterpreter类型，调interpret方法转int类型
        return this.firstExpression.interpret() + this.secondExpression.interpret();
    }

    @Override
    public String toString() {
        return "+";
    }
}
```

乘法解释器

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

/**
 * 乘法解释器
 *
 * @author F嘉阳
 * @date 2020/3/5 14:47
 */
public class MultiInterpreter implements Interpreter {

    private Interpreter firstExpression, secondExpression;

    public MultiInterpreter(Interpreter firstExpression, Interpreter secondExpression) {
        this.firstExpression = firstExpression;
        this.secondExpression = secondExpression;
    }

    @Override
    public int interpret() {
        return this.firstExpression.interpret() * this.secondExpression.interpret();
    }

    @Override
    public String toString() {
        return "*";
    }
}
```

类型解释器

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

/**
 * @author F嘉阳
 * @date 2020/3/5 14:47
 */
public class NumberInterpreter implements Interpreter {
    private int number;

    public NumberInterpreter(int number) {
        this.number = number;
    }

    public NumberInterpreter(String number) {
        this.number = Integer.parseInt(number);
    }

    @Override
    public int interpret() {
        return this.number;
    }
}
```

操作工具类

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

/**
 * @author F嘉阳
 * @date 2020/3/5 14:47
 */
public class OperatorUtil {
    public static boolean isOperator(String symbol) {
        return (symbol.equals("+") || symbol.equals("*"));

    }

    public static Interpreter getExpressionObject(Interpreter firstExpression, Interpreter secondExpression, String symbol) {
        if (symbol.equals("+")) {
            return new AddInterpreter(firstExpression, secondExpression);
        } else if (symbol.equals("*")) {
            return new MultiInterpreter(firstExpression, secondExpression);
        }
        return null;
    }
}
```

自定义解释器实现

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

import lombok.extern.slf4j.Slf4j;

import java.util.Stack;

/**
 * @author F嘉阳
 * @date 2020/3/5 14:48
 */
@Slf4j
public class CustomExpressionParser {
    private Stack<Interpreter> stack = new Stack<Interpreter>();

    public int parse(String str) {
        String[] strItemArray = str.split(" ");
        for (String symbol : strItemArray) {
            if (!OperatorUtil.isOperator(symbol)) {
                Interpreter numberExpression = new NumberInterpreter(symbol);
                stack.push(numberExpression);
                log.info(String.format("入栈: %d", numberExpression.interpret()));
            } else {
                //是运算符号，可以计算
                Interpreter firstExpression = stack.pop();
                Interpreter secondExpression = stack.pop();
                log.info(String.format("出栈: %d 和 %d",
                        firstExpression.interpret(), secondExpression.interpret()));
                Interpreter operator = OperatorUtil.getExpressionObject(firstExpression, secondExpression, symbol);
                log.info(String.format("应用运算符: %s", operator));
                int result = operator.interpret();
                NumberInterpreter resultExpression = new NumberInterpreter(result);
                stack.push(resultExpression);
                log.info(String.format("阶段结果入栈: %d", resultExpression.interpret()));
            }
        }
        int result = stack.pop().interpret();
        return result;

    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.interpreter;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.springframework.expression.Expression;
import org.springframework.expression.spel.standard.SpelExpressionParser;

/**
 * @author F嘉阳
 * @date 2020/3/5 14:48
 */
@Slf4j
class InterpreterTest {

    @Test
    void interpret() {
        String myInterpreter = "6 100 11 + *";
        CustomExpressionParser expressionParser = new CustomExpressionParser();
        int result = expressionParser.parse(myInterpreter);
        log.info("解释器计算结果: " + result);
    }

    @Test
    void springTest() {
        org.springframework.expression.ExpressionParser parser = new SpelExpressionParser();
        Expression expression = parser.parseExpression("100 * 2 + 400 * 1 + 66");
        int result = (Integer) expression.getValue();
        log.info(String.valueOf(result));
    }
}
```

输出

```
14:52:28.086 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 入栈: 6
14:52:28.089 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 入栈: 100
14:52:28.089 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 入栈: 11
14:52:28.089 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 出栈: 11 和 100
14:52:28.090 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 应用运算符: +
14:52:28.090 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 阶段结果入栈: 111
14:52:28.090 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 出栈: 111 和 6
14:52:28.090 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 应用运算符: *
14:52:28.091 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.GeelyExpressionParser - 阶段结果入栈: 666
14:52:28.091 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.InterpreterTest - 解释器计算结果: 666


14:52:28.550 [main] INFO top.fjy8018.designpattern.pattern.behavior.interpreter.InterpreterTest - 666
```



## 观察者模式

### 介绍

定义：定义了对象之间的一对多依赖，让多个观察者对象同时监听某一个主题对象，当主题对象发生变化时，它的所有依赖者（观察者）都会收到通知并更新

类型：行为型



适用场景

- 关联行为场景，建立一套触发机制



优点

- 观察者模式支持广播通信
- 观察者和被观察者之间建立一个抽象的耦合



缺点

- 使用要得当,要避免循环调用
- 观察者之间有过多的细节依赖、提高时间消耗及程序复杂度





### 代码样例——JDK观察者

类图

![image-20200305155223638](/images/recovered/04876253e78ff638a809.png)

课程问题

```java
package top.fjy8018.designpattern.pattern.behavior.observer;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 课程问题
 *
 * @author F嘉阳
 * @date 2020/3/5 15:23
 */
@Getter
@AllArgsConstructor
public class Question {

    private String username;

    private String content;

}
```



课程（被观察者）

```java
package top.fjy8018.designpattern.pattern.behavior.observer;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;

import java.util.EventListener;
import java.util.Observable;
import java.util.Vector;

/**
 * 课程
 * 被观察者类
 *
 * {@link Observable} 使用 {@link Vector} 保证线程安全
 *
 * JDK源码
 * {@link java.awt.Event} 事件监听器
 * {@link javax.servlet.ServletRequestListener} HTTP请求事件监听器
 * 继承 {@link EventListener}，有大量实现，例如{@link org.springframework.beans.factory.parsing.ReaderEventListener}
 *
 * @author F嘉阳
 * @date 2020/3/5 15:23
 */
@Slf4j
@Getter
@AllArgsConstructor
public class Course extends Observable {

    private String courseName;

    /**
     * 产生问题
     * @param course
     * @param question
     */
    public void produceQuestion(Course course,Question question){
        log.info("{}在{}提交了一个问题",question.getUsername(),course.getCourseName());
        // 状态变化
        setChanged();
        // 通知观察者
        notifyObservers(question);
    }
}
```



老师实体（观察者）

```java
package top.fjy8018.designpattern.pattern.behavior.observer;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;

import java.util.Observable;
import java.util.Observer;

/**
 * 老师实体
 *
 * 老师观察课程是否产生了新的问题
 * @author F嘉阳
 * @date 2020/3/5 15:24
 */
@Slf4j
@Getter
@AllArgsConstructor
public class Teacher implements Observer {

    private String teacherName;

    /**
     * This method is called whenever the observed object is changed. An
     * application calls an <tt>Observable</tt> object's
     * <code>notifyObservers</code> method to have all the object's
     * observers notified of the change.
     *
     * @param o   the observable object.
     * @param arg an argument passed to the <code>notifyObservers</code>
     */
    @Override
    public void update(Observable o, Object arg) {
        Course course = (Course) o;
        Question question = (Question) arg;
        log.info("{}老师的{}课程接收到一个{}提交的问题，内容为：{}",
                teacherName,course.getCourseName(),question.getUsername(),question.getContent());
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.observer;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/3/5 15:36
 */
@Slf4j
class TeacherTest {

    @Test
    void update() {
        Course course = new Course("Java设计模式");
        Teacher teacher = new Teacher("fjy8018");

        course.addObserver(teacher);

        // 业务逻辑
        Question question = new Question("fjy","问题内容XXX");

        course.produceQuestion(course,question);
    }
}
```

输出

```java
15:38:34.437 [main] INFO top.fjy8018.designpattern.pattern.behavior.observer.Course - fjy在Java设计模式提交了一个问题
15:38:34.444 [main] INFO top.fjy8018.designpattern.pattern.behavior.observer.Teacher - fjy8018老师的Java设计模式课程接收到一个fjy提交的问题，内容为：问题内容XXX
```



### 代码样例——Guava监听器



```java
package top.fjy8018.designpattern.pattern.behavior.observer.guava;

import com.google.common.eventbus.Subscribe;
import lombok.extern.slf4j.Slf4j;

import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.CopyOnWriteArraySet;

/**
 * Guava事件监听器
 * {@link EventBus} 使用内部对象 {@link SubscriberRegistry} 内部使用 {@link ConcurrentMap} 存储订阅者
 * 同时使用 {@link CopyOnWriteArraySet} 保证线程安全和订阅者唯一
 * 故{@link com.google.common.eventbus.Subscriber}
 * 重写了 {@link com.google.common.eventbus.Subscriber#equals(Object)}
 * 和 {@link com.google.common.eventbus.Subscriber#hashCode()} 方法
 *
 * @author F嘉阳
 * @date 2020/3/5 15:56
 */
@Slf4j
public class GuavaEvent {

    @Subscribe
    public void subscribe(String str) {
        // 业务逻辑
        log.info("执行订阅方法，传入参数是：{}", str);
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.behavior.observer;

import com.google.common.eventbus.EventBus;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.pattern.behavior.observer.guava.Course;
import top.fjy8018.designpattern.pattern.behavior.observer.guava.GuavaEvent;

/**
 * @author F嘉阳
 * @date 2020/3/5 15:58
 */
@Slf4j
class GuavaEventTest {

    @Test
    void subscribe() {
        EventBus eventBus = new EventBus();
        GuavaEvent event = new GuavaEvent();
        // 注册
        eventBus.register(event);
        eventBus.post("提交事件的内容");
    }
}
```



输出

```
16:24:27.716 [main] INFO top.fjy8018.designpattern.pattern.behavior.observer.GuavaEvent - 执行订阅方法，传入参数是：提交事件的内容
```



## 备忘录模式

### 介绍

定义：保存一个对象的某个状态，以便在适当的时候恢复对象。（类似历史记录存储）

“后悔药”

类型：行为型



适用场景

- 保存及恢复数据相关业务场景
- 后悔的时候，即想恢复到之前的状态



优点

- 为用户提供一种可恢复机制
- 存档信息的封装



缺点

- 资源占用



相关设计模式

- 备忘录模式和状态模式



### 代码样例

类图

![Article](/images/recovered/09d9e7677ac38f766936.png)

文章

```java
package top.fjy8018.designpattern.pattern.behavior.memento;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * 文章，字段不宜过多，否则导致过大内存占用
 *
 * @author F嘉阳
 * @date 2020/3/6 17:00
 */
@Data
@AllArgsConstructor
public class Article {

    private String title;

    private String content;

    private String imgs;

    /**
     * 保存
     * @return
     */
    public ArticleMemento saveToMemento() {
        ArticleMemento articleMemento = new ArticleMemento(this.title,this.content,this.imgs);
        return articleMemento;
    }

    /**
     * 撤销
     * @param articleMemento
     */
    public void undoFromMemento(ArticleMemento articleMemento) {
        this.title = articleMemento.getTitle();
        this.content = articleMemento.getContent();
        this.imgs = articleMemento.getImgs();
    }
}
```

文章备忘录（快照）

```java
package top.fjy8018.designpattern.pattern.behavior.memento;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.ToString;
import org.springframework.binding.message.StateManageableMessageContext;

/**
 * 文章备忘录（快照）
 * 快照不需要set方法，只能通过构造器注入
 *
 * Spring工作流中源码 {@link StateManageableMessageContext#createMessagesMemento()}
 *
 * @author F嘉阳
 * @date 2020/3/6 17:03
 */
@Getter
@ToString
@AllArgsConstructor
public class ArticleMemento {

    private String title;

    private String content;

    private String imgs;
}
```

备忘录核心，栈实现管理者

```java
package top.fjy8018.designpattern.pattern.behavior.memento;

import java.util.Stack;

/**
 * 保存一个对象的某个状态，以便在适当的时候恢复对象
 *
 * @author F嘉阳
 * @date 2020/3/6 17:04
 */
public class ArticleMementoManager {

    /**
     * 使用栈特性实现动作撤销
     */
    private final Stack<ArticleMemento> ARTICLE_MEMENTO_STACK = new Stack<ArticleMemento>();

    public ArticleMemento getMemento() {
        ArticleMemento articleMemento= ARTICLE_MEMENTO_STACK.pop();
        return articleMemento;
    }

    public void addMemento(ArticleMemento articleMemento)
    {
        ARTICLE_MEMENTO_STACK.push(articleMemento);
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.memento;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

/**
 * @author F嘉阳
 * @date 2020/3/6 17:07
 */
@Slf4j
class ArticleMementoTest {

    @Test
    void getTitle() {
        ArticleMementoManager articleMementoManager = new ArticleMementoManager();

        Article article= new Article("如影随行的设计模式A","手记内容A","手记图片A");
        // 存档
        ArticleMemento articleMemento = article.saveToMemento();

        articleMementoManager.addMemento(articleMemento);
        log.info("标题:"+article.getTitle()+" 内容:"+article.getContent()+" 图片:"+article.getImgs()+" 暂存成功");

        log.info("手记完整信息:"+article);
        
        log.info("修改手记start");

        article.setTitle("如影随行的设计模式B");
        article.setContent("手记内容B");
        article.setImgs("手记图片B");

        log.info("修改手记end");

        log.info("手记完整信息:"+article);

        articleMemento = article.saveToMemento();
        articleMementoManager.addMemento(articleMemento);
        
        article.setTitle("如影随行的设计模式C");
        article.setContent("手记内容C");
        article.setImgs("手记图片C");

        log.info("暂存回退start");
        // 取档
        log.info("回退出栈1次");
        articleMemento = articleMementoManager.getMemento();
        article.undoFromMemento(articleMemento);

        log.info("回退出栈2次");
        articleMemento = articleMementoManager.getMemento();
        article.undoFromMemento(articleMemento);

        log.info("暂存回退end");
        log.info("手记完整信息:"+article);
    }
}
```

输出

```
17:33:51.154 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 标题:如影随行的设计模式A 内容:手记内容A 图片:手记图片A 暂存成功
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 手记完整信息:Article(title=如影随行的设计模式A, content=手记内容A, imgs=手记图片A)
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 修改手记start
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 修改手记end
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 手记完整信息:Article(title=如影随行的设计模式B, content=手记内容B, imgs=手记图片B)
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 暂存回退start
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 回退出栈1次
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 回退出栈2次
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 暂存回退end
17:33:51.169 [main] INFO top.fjy8018.designpattern.pattern.behavior.memento.ArticleMementoTest - 手记完整信息:Article(title=如影随行的设计模式A, content=手记内容A, imgs=手记图片A)
```





## 命令模式

### 介绍

定义：将请求封装成对象,以便使用不同的请求      

特点：命令模式解决了应用程序中对象的职责以及它们之间的通信方式

类型：行为型



适用场景

- 请求调用者和请求接收者需要解耦,使得调用者和接收者不直接交互
- 需要抽象出等待执行的行为



优点

- 降低耦合
- 容易扩展新命令或者一组命令



缺点

- 命令的无限扩展会增加类的数量，提高系统实现复杂度



相关设计模式

- 命令模式和备忘录模式



### 代码样例

类图

![Command](/images/recovered/4eb9685bcf9eb58ca58a.png)

命令抽象

```java
package top.fjy8018.designpattern.pattern.behavior.command;

/**
 * 命令抽象
 * <p>
 * Java相关源码 {@link Runnable} 可理解为命令抽象
 * 其实现类为具体的命令
 *
 * @author F嘉阳
 * @date 2020/7/21 15:58
 */
public interface Command {
    void execute();
}
```

操作视频

```java
package top.fjy8018.designpattern.pattern.behavior.command;

import lombok.AllArgsConstructor;

/**
 * 关闭视频命令
 *
 * @author F嘉阳
 * @date 2020/7/21 15:58
 */
@AllArgsConstructor
public class CloseCourseVideoCommand implements Command {
    private final CourseVideo courseVideo;

    @Override
    public void execute() {
        courseVideo.close();
    }
}
```

打开视频命令

```java
package top.fjy8018.designpattern.pattern.behavior.command;

import lombok.AllArgsConstructor;

/**
 * 打开视频命令
 *
 * @author F嘉阳
 * @date 2020/7/21 15:58
 */
@AllArgsConstructor
public class OpenCourseVideoCommand implements Command {
    private final CourseVideo courseVideo;

    @Override
    public void execute() {
        courseVideo.open();
    }
}
```

关闭视频命令

```java
package top.fjy8018.designpattern.pattern.behavior.command;

import lombok.AllArgsConstructor;

/**
 * 关闭视频命令
 *
 * @author F嘉阳
 * @date 2020/7/21 15:58
 */
@AllArgsConstructor
public class CloseCourseVideoCommand implements Command {
    private final CourseVideo courseVideo;

    @Override
    public void execute() {
        courseVideo.close();
    }
}
```

命令执行人

```java
package top.fjy8018.designpattern.pattern.behavior.command;

import java.util.ArrayList;
import java.util.List;

/**
 * 命令执行人
 *
 * @author F嘉阳
 * @date 2020/7/21 15:58
 */
public class Staff {
    /**
     * 保证执行顺序
     */
    private final List<Command> commandList = new ArrayList<Command>();

    public void addCommand(Command command) {
        commandList.add(command);
    }

    public void executeCommands() {
        for (Command command : commandList) {
            command.execute();
        }
        commandList.clear();
    }

}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.command;

import org.junit.jupiter.api.Test;

/**
 * @author F嘉阳
 * @date 2020/7/21 16:02
 */
class CommandTest {

    @Test
    void doTest() {
        CourseVideo courseVideo = new CourseVideo("Java设计模式精讲");
        OpenCourseVideoCommand openCourseVideoCommand = new OpenCourseVideoCommand(courseVideo);
        CloseCourseVideoCommand closeCourseVideoCommand = new CloseCourseVideoCommand(courseVideo);

        Staff staff = new Staff();

        staff.addCommand(openCourseVideoCommand);
        staff.addCommand(closeCourseVideoCommand);

        staff.executeCommands();
    }
}
```

输出

```
Java设计模式精讲课程视频开放
Java设计模式精讲课程视频关闭
```











## 中介者模式

### 介绍

定义：定义一个 封装一组对象如何交互的对象

特点：通过使对象明确地相互引用来促进松散耦合,并允许独立地改变它们的交互



适用场景

- 系统中对象之间存在复杂的引用关系，产生的相互依赖关系结构混乱且难以理解
- 交互的公共行为，如果需要改变行为则可以增加新的中介者类



优点

- 将一对多转化成了一对一、降低程序复杂度
- 类之间解耦



缺点

- 中介者过多,导致系统复杂



相关设计模式

- 中介者模式和观察者模式



### 代码样例

类图

![Mediator](/images/recovered/5324226703c2aabd423e.png)

学习群组（中介者）

```java
package top.fjy8018.designpattern.pattern.behavior.mediator;

import java.util.Date;
import java.util.Timer;

/**
 * 学习群组（中介者）
 * <p>
 * jdk源码 {@link Timer#schedule(java.util.TimerTask, Date)} 多个方法重载
 * 都是调用{@link Timer#sched(java.util.TimerTask, long, long)} 实现的，由底层方法进行整体协调
 *
 * @author F嘉阳
 * @date 2020/7/21 16:20
 */
public class StudyGroup {

    public static void showMessage(User user, String message) {
        System.out.println(new Date().toString() + " [" + user.getName() + "] : " + message);
    }
}
```

用户

```java
package top.fjy8018.designpattern.pattern.behavior.mediator;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * @author F嘉阳
 * @date 2020/7/21 16:20
 */
@Data
@AllArgsConstructor
public class User {
    private String name;

    public void sendMessage(String message) {
        // 只和中介者交互
        StudyGroup.showMessage(this, message);
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.mediator;

import org.junit.jupiter.api.Test;

/**
 * @author F嘉阳
 * @date 2020/7/21 16:25
 */
class MediatorTest {

    @Test
    void doTest() {
        User fjy = new User("F嘉阳");
        User tom = new User("Tom");

        fjy.sendMessage(" Hey! Tom! Let's learn Design Pattern");
        tom.sendMessage("OK! F嘉阳");
    }
}
```

输出

```
Tue Jul 21 16:47:03 CST 2020 [F嘉阳] :  Hey! Tom! Let's learn Design Pattern
Tue Jul 21 16:47:03 CST 2020 [Tom] : OK! F嘉阳
```

## 责任链模式

### 介绍

定义：为请求创建一个接收此次请求对象的链            

类型：行为型



适用场景

- 一个请求的处理需要多个对象当中的一个或几个协作处理



优点

- 请求的发送者和接收者(请求的处理)解耦
- 责任链可以动态组合



缺点

- 责任链太长或者处理时间过长,影响性能
- 责任链有可能过多



相关设计模式

- 责任链模式和状态模式



### 代码样例

类图

![chain](/images/recovered/ff831166499db5f45e8f.png)

模拟二级审批场景

```java
package top.fjy8018.designpattern.pattern.behavior.chainofresponsibility;

import javax.servlet.FilterChain;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

/**
 * 模拟二级审批场景
 * <p>
 * 审批抽象
 * <p>
 * java 过滤器实现 {@link javax.servlet.Filter#doFilter(ServletRequest, ServletResponse, FilterChain)}
 * 实现 {@link FilterChain#doFilter(ServletRequest, ServletResponse)} 接口的组成一条过滤器链
 * 所有子类通过调用 chain.doFilter(request, response) 实现链式传递
 * <p>
 * SpringSecurity过滤器链实现也类似
 *
 * @author F嘉阳
 * @date 2020/7/21 16:59
 */
public abstract class Approver {
    /**
     * 责任链核心：包含与自身相同的类型对象
     */
    protected Approver approver;

    /**
     * 设置下一个节点，组成链条
     *
     * @param approver
     */
    public void setNextApprover(Approver approver) {
        this.approver = approver;
    }

    /**
     * 交由子类实现
     *
     * @param course
     */
    public abstract void deploy(Course course);
}
```

手记审批

```java
package top.fjy8018.designpattern.pattern.behavior.chainofresponsibility;

import org.apache.commons.lang3.StringUtils;

/**
 * 手记审批
 *
 * @author F嘉阳
 * @date 2020/7/21 16:59
 */
public class ArticleApprover extends Approver {
    @Override
    public void deploy(Course course) {
        if (StringUtils.isNotEmpty(course.getArticle())) {
            System.out.println(course.getName() + "含有手记,批准");
            // 是否为末尾
            if (approver != null) {
                // 执行下一个处理链
                approver.deploy(course);
            }
        } else {
            System.out.println(course.getName() + "不含有手记,不批准,流程结束");
            return;
        }
    }
}
```

视频审批

```java
package top.fjy8018.designpattern.pattern.behavior.chainofresponsibility;

import org.apache.commons.lang3.StringUtils;

/**
 * 视频审批
 *
 * @author F嘉阳
 * @date 2020/7/21 16:59
 */
public class VideoApprover extends Approver {
    @Override
    public void deploy(Course course) {
        if (StringUtils.isNotEmpty(course.getVideo())) {
            System.out.println(course.getName() + "含有视频,批准");
            if (approver != null) {
                approver.deploy(course);
            }
        } else {
            System.out.println(course.getName() + "不含有视频,不批准,流程结束");
            return;
        }
    }
}
```

课程

```java
package top.fjy8018.designpattern.pattern.behavior.chainofresponsibility;

import lombok.Data;

/**
 * 课程
 *
 * @author F嘉阳
 * @date 2020/7/21 16:59
 */
@Data
public class Course {
    private String name;

    private String article;

    private String video;
}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.chainofresponsibility;

import org.junit.jupiter.api.Test;

/**
 * @author F嘉阳
 * @date 2020/7/21 15:06
 */
class ChainofResponsibilityTest {

    @Test
    void doTest() {
        Approver articleApprover = new ArticleApprover();
        Approver videoApprover = new VideoApprover();

        Course course = new Course();
        course.setName("Java设计模式");
        course.setArticle("Java设计模式的手记");
        course.setVideo("Java设计模式的视频");

        articleApprover.setNextApprover(videoApprover);

        articleApprover.deploy(course);
    }
}
```

输出

```
Java设计模式含有手记,批准
Java设计模式含有视频,批准
```



## 访问者模式

### 介绍

定义：封装作用于某数据结构(如List/set/Map等)中的各元素的操作

特性：可以在不改变各元素的类的前提下定义作用于这些元素的操作

类型：行为型



适用场景

- 一个数据结构如(List/set/Map等)包含很多类型对象        
- 数据结构与数据操作分离



优点

- 增加新的操作很容易即增加一个新的访问者



缺点

- 增加新的数据结构困难          
- 具体元素变更比较麻烦



相关设计模式

-  访问者模式和迭代器模式



### 代码样例

类图

![visitor](/images/recovered/993660a48c46217171b0.png)

课程抽象

```java
package top.fjy8018.designpattern.pattern.behavior.visitor;

import lombok.Data;

/**
 * @author F嘉阳
 * @date 2020/7/22 10:20
 */
@Data
public abstract class Course {
    private String name;

    public abstract void accept(IVisitor visitor);

}
```

实战课

```java
package top.fjy8018.designpattern.pattern.behavior.visitor;

import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 实战课，包含价格
 *
 * @author F嘉阳
 * @date 2020/7/22 10:20
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class CodingCourse extends Course {
    private int price;

    @Override
    public void accept(IVisitor visitor) {
        visitor.visit(this);
    }
}
```

免费课

```java
package top.fjy8018.designpattern.pattern.behavior.visitor;

/**
 * 免费课
 *
 * @author F嘉阳
 * @date 2020/7/22 10:20
 */
public class FreeCourse extends Course {

    /**
     * 接受策略
     *
     * @param visitor
     */
    @Override
    public void accept(IVisitor visitor) {
        visitor.visit(this);
    }
}
```

访问者

```java
package top.fjy8018.designpattern.pattern.behavior.visitor;

/**
 * 封装操作数据结构的方法
 *
 * @author F嘉阳
 * @date 2020/7/22 10:20
 */
public interface IVisitor {

    void visit(FreeCourse freeCourse);

    void visit(CodingCourse codingCourse);
}
```

访问者核心实现

```java
package top.fjy8018.designpattern.pattern.behavior.visitor;

/**
 * 访问者
 * 核心：对不同类型产生不同的操作行为
 * <p>
 * jdk源码 {@link java.nio.file.FileVisitor} 实现对文件的访问
 * spring源码 {@link org.springframework.beans.factory.config.BeanDefinitionVisitor} 遍历Bean具体属性并填充
 *
 * @author F嘉阳
 * @date 2020/7/22 10:20
 */
public class Visitor implements IVisitor {

    /**
     * 访问免费课程，打印所有免费课程名称
     *
     * @param freeCourse
     */
    @Override
    public void visit(FreeCourse freeCourse) {
        System.out.println("免费课程:" + freeCourse.getName());
    }

    /**
     * 访问实战课程，打印所有实战课程名称及价格
     *
     * @param codingCourse
     */
    @Override
    public void visit(CodingCourse codingCourse) {
        System.out.println("实战课程:" + codingCourse.getName() + " 价格:" + codingCourse.getPrice() + "元");
    }

}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.visitor;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

/**
 * @author F嘉阳
 * @date 2020/7/22 16:19
 */
class VisitorTest {

    @Test
    void visit() {
        List<Course> courseList = new ArrayList<>();

        FreeCourse freeCourse = new FreeCourse();
        freeCourse.setName("SpringMVC数据绑定");

        CodingCourse codingCourse = new CodingCourse();
        codingCourse.setName("Java设计模式精讲");
        codingCourse.setPrice(299);
        // 数组组装
        courseList.add(freeCourse);
        courseList.add(codingCourse);

        for (Course course : courseList) {
            course.accept(new Visitor());
        }
    }
}
```

输出

```
免费课程:SpringMVC数据绑定
实战课程:Java设计模式精讲 价格:299元
```









## 状态模式

### 介绍

定义：允许一个对象在其内部状态改变时改变它的行为           

类型：行为型



适用场景

- 一个对象存在多个状态(不同状态下行为不同),且状态可相互转换



优点

- 将不同的状态隔离 
- 把各种状态的转换逻辑,分布到 State的子类中,减少相互间依赖    
- 增加新的状态非常简单



缺点

- 状态多的业务场景导致类数目增加,系统变复杂



相关设计模式

- 状态模式和享元模式



### 代码样例

类图

![state](/images/recovered/e3f4141d49e9df4b7408.png)

视频播放状态转换场景

```java
package top.fjy8018.designpattern.pattern.behavior.state;

import javax.faces.lifecycle.Lifecycle;

/**
 * 视频播放状态转换场景
 * <p>
 * {@link Lifecycle#execute(javax.faces.context.FacesContext)} 该方法通过外部状态控制改变行为
 * {@link javax.faces.webapp.FacesServlet} 状态控制
 *
 * @author F嘉阳
 * @date 2020/7/22 15:20
 */
public abstract class CourseVideoState {
    /**
     * 视频上下文
     */
    protected CourseVideoContext courseVideoContext;

    public void setCourseVideoContext(CourseVideoContext courseVideoContext) {
        this.courseVideoContext = courseVideoContext;
    }

    public abstract void play();

    public abstract void speed();

    public abstract void pause();

    public abstract void stop();

}
```

视频上下文

```java
package top.fjy8018.designpattern.pattern.behavior.state;

/**
 * 视频上下文
 *
 * @author F嘉阳
 * @date 2020/7/22 15:20
 */
public class CourseVideoContext {

    /**
     * 存储当前状态
     */
    private CourseVideoState courseVideoState;

    /**
     * 结合享元模式设置为内存共享
     */
    public final static PlayState PLAY_STATE = new PlayState();
    public final static StopState STOP_STATE = new StopState();
    public final static PauseState PAUSE_STATE = new PauseState();
    public final static SpeedState SPEED_STATE = new SpeedState();

    public CourseVideoState getCourseVideoState() {
        return courseVideoState;
    }

    public void setCourseVideoState(CourseVideoState courseVideoState) {
        this.courseVideoState = courseVideoState;
        // 把自己本身设置到实例上下文中
        this.courseVideoState.setCourseVideoContext(this);
    }
    public void play(){
        this.courseVideoState.play();
    }

    public void speed(){
        this.courseVideoState.speed();
    }

    public void stop(){
        this.courseVideoState.stop();
    }

    public void pause(){
        this.courseVideoState.pause();
    }
}
```

各状态实现

```java
package top.fjy8018.designpattern.pattern.behavior.state;

/**
 * @author F嘉阳
 * @date 2020/7/22 15:20
 */
public class PlayState extends CourseVideoState {

    @Override
    public void play() {
        System.out.println("正常播放课程视频状态");
    }

    @Override
    public void speed() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.SPEED_STATE);
    }

    @Override
    public void pause() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.PAUSE_STATE);
    }

    @Override
    public void stop() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.STOP_STATE);
    }
}
```



```java
package top.fjy8018.designpattern.pattern.behavior.state;

/**
 * @author F嘉阳
 * @date 2020/7/22 15:20
 */
public class PauseState extends CourseVideoState {

    @Override
    public void play() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.PLAY_STATE);
    }

    @Override
    public void speed() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.SPEED_STATE);
    }

    @Override
    public void pause() {
        System.out.println("暂停播放课程视频状态");
    }

    @Override
    public void stop() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.STOP_STATE);
    }
}
```



```java
package top.fjy8018.designpattern.pattern.behavior.state;

/**
 * @author F嘉阳
 * @date 2020/7/22 15:20
 */
public class SpeedState extends CourseVideoState {
    @Override
    public void play() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.PLAY_STATE);
    }

    @Override
    public void speed() {
        System.out.println("快进播放课程视频状态");
    }

    @Override
    public void pause() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.PAUSE_STATE);
    }

    @Override
    public void stop() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.STOP_STATE);
    }
}
```



```java
package top.fjy8018.designpattern.pattern.behavior.state;

/**
 * @author F嘉阳
 * @date 2020/7/22 15:20
 */
public class StopState extends CourseVideoState {
    @Override
    public void play() {
        super.courseVideoContext.setCourseVideoState(CourseVideoContext.PLAY_STATE);
    }

    @Override
    public void speed() {
        System.out.println("ERROR 停止状态不能快进!!");
    }

    @Override
    public void pause() {
        System.out.println("ERROR 停止状态不能暂停!!");
    }

    @Override
    public void stop() {
        System.out.println("停止播放课程视频状态");
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.behavior.state;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/7/22 16:19
 */
class PlayStateTest {

    @Test
    void play() {
        CourseVideoContext courseVideoContext = new CourseVideoContext();
        courseVideoContext.setCourseVideoState(new PlayState());

        System.out.println("当前状态:"+courseVideoContext.getCourseVideoState().getClass().getSimpleName());
        courseVideoContext.pause();

        System.out.println("当前状态:"+courseVideoContext.getCourseVideoState().getClass().getSimpleName());

        courseVideoContext.speed();

        System.out.println("当前状态:"+courseVideoContext.getCourseVideoState().getClass().getSimpleName());

        courseVideoContext.stop();

        System.out.println("当前状态:"+courseVideoContext.getCourseVideoState().getClass().getSimpleName());

        courseVideoContext.speed();
    }
}
```

输出

```
当前状态:PlayState
当前状态:PauseState
当前状态:SpeedState
当前状态:StopState
ERROR 停止状态不能快进!!
```
