{
  "title": "设计模式学习——原则",
  "date": "2020-01-22T09:25:00+08:00",
  "lastmod": "2020-02-28T15:30:56+08:00",
  "typecho_cid": 237,
  "url": "/archives/237/",
  "comments": false,
  "draft": false,
  "slug": "237",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "设计模式"
  ],
  "math": false
}

## 开闭原则

### 介绍

定义：一个软件实体如类、模块和函数应该对扩展开放,对修改关闭      

用抽象构建框架,用实现扩展细节

优点：提高软件系统的可复用性及可维护性

### 代码样例

类图

![image-20200120112838846](/images/recovered/0f2a8de41008e343907c.png)

课程接口

```java
package top.fjy8018.designpattern.principle.openclose;

import java.math.BigDecimal;

/**
 * 课程接口
 * 对于面向接口编程，接口应当是稳定的
 * 根据开闭原则，在此体现为对接口的增加和修改时关闭的，因为会导致所有实现类的变化
 * 而对课程类的扩展（extend）是开放的
 *
 * @author F嘉阳
 * @date 2018-09-18 16:28
 */
public interface Course {
    /**
     * 获取课程ID
     *
     * @return
     */
    Integer getId();

    /**
     * 获取课程名称
     *
     * @return
     */
    String getName();

    /**
     * 获取课程价格
     *
     * @return
     */
    BigDecimal getPrice();
}
```

课程实现类

```java
package top.fjy8018.designpattern.principle.openclose;

import java.math.BigDecimal;

/**
 * 课程实现类
 *
 * @author F嘉阳
 * @date 2018-09-18 16:30
 */
public class JavaCourse implements Course {
    private Integer id;

    private String name;

    private BigDecimal price;

    public JavaCourse(Integer id, String name, BigDecimal price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }

    @Override
    public Integer getId() {
        return this.id;
    }

    @Override
    public String getName() {
        return this.name;
    }

    @Override
    public BigDecimal getPrice() {
        return this.price;
    }

    @Override
    public String toString() {
        return "JavaCourse{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", price=" + price.setScale(2, BigDecimal.ROUND_HALF_UP) +
                '}';
    }
}
```

Java课程促销类

```java
package top.fjy8018.designpattern.principle.openclose;

import java.math.BigDecimal;

/**
 * Java课程促销
 * 根据开闭原则：对于扩展是开放的，对于修改是关闭的
 * 故通过继承方式实现
 *
 * @author F嘉阳
 * @date 2018-09-18 16:43
 */
public class JavaDiscountCourse extends JavaCourse {

    public JavaDiscountCourse(Integer id, String name, BigDecimal price) {
        super(id, name, price);
    }

    @Override
    public Integer getId() {
        return super.getId();
    }

    @Override
    public String getName() {
        return super.getName();
    }

    /**
     * 实现打折价格逻辑
     *
     * @return
     */
    public BigDecimal getDistcountPrice() {
        // BigDecimal推荐使用String构造器，防止精度转换问题
        return super.getPrice().multiply(new BigDecimal("0.8"));
    }

    /**
     * 根据里氏替换原则：父类实现的方法不应该覆盖
     * 获取原价
     *
     * @return
     */
    @Override
    public BigDecimal getPrice() {

        return super.getPrice();
    }

    @Override
    public String toString() {
        return super.toString();
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.openclose;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import java.io.PrintStream;
import java.math.BigDecimal;


/**
 * 开闭原则单元测试
 *
 * 由于底层通过加锁实现，故生产环境严禁使用{@link PrintStream#println(String)}
 */
@Slf4j
class JavaCourseTest {

    /**
     * 普通情况
     */
    @Test
    public void normal() {
        Course javaCourse = new JavaCourse(1, "Java课程", new BigDecimal("99"));
        log.info("课程Id：{},课程名称：{},价格：{}", javaCourse.getId(), javaCourse.getName(), javaCourse.getPrice());
    }

    /**
     * 促销打折情况
     */
    @Test
    public void discount() {
        Course course = new JavaDiscountCourse(1, "Java课程", new BigDecimal("99"));
        JavaDiscountCourse javaCourse = (JavaDiscountCourse) course;
        log.info("课程Id：{},课程名称：{},原价：{},折后价格：{}",
                javaCourse.getId(), javaCourse.getName(), javaCourse.getPrice(),
                javaCourse.getDistcountPrice().setScale(2, BigDecimal.ROUND_HALF_UP));
    }

}
```



## 依赖倒置原则

### 介绍

定义：高层模块不应该依赖低层模块，二者都应该依赖其抽象

抽象不应该依赖细节；细节应该依赖抽象

针对接口编程，不要针对实现编程

优点：可以减少类间的耦合性、提高系统稳定性，提高代码可读性和可维护性，可降低修改程序所造成的风险

### 代码样例

#### 改造前

```java
package top.fjy8018.designpattern.principle.dependenceinversion.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 低层模块（模块被调用方）
 * <p>
 * 此时如果要加一个课程，必须修改该类
 * 而对低层模块的修改应该尽量避免
 *
 * @author F嘉阳
 * @date 2018-09-18 17:14
 */
@Slf4j
public class Student {

    public void studyJavaCourse() {
        log.info("学习Java课程");
    }

    public void studyPythonCourse() {
        log.info("学习Python课程");
    }

    public void studyVueCourse() {
        log.info("学习Vue课程");
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.dependenceinversion.before;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 依赖倒置实现前单元测试
 * 高层模块（模块调用方）
 */
class StudentTest {

    /**
     * 此时存在的问题：
     * 如果高层模块要学多一门课程
     * 则低层模块{@link Student} 也要对应修改，即存在高层模块依赖低层模块，面向具体实现类编程
     */
    @Test
    public void study() {
        Student student = new Student();
        student.studyJavaCourse();
        student.studyPythonCourse();
        student.studyVueCourse();
    }
}
```



#### 改造后

类图

![image-20200120113206348](/images/recovered/18f906e224e85bc15400.png)

抽象学习课程接口

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

/**
 * 学习课程接口
 * 接口作为抽象存在，成为一个契约
 * 面向抽象编程比面向具体实现细节编程实现简单，灵活度高
 *
 * @author F嘉阳
 * @date 2018-09-18 17:19
 */
public interface DCourse {
    void study();
}
```

具体学习过程接口，java课程

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

import lombok.extern.slf4j.Slf4j;

/**
 * 课程都面向接口，满足依赖倒置原则：高层次的模块不应该依赖于低层次的模块，他们都应该依赖于抽象
 *
 * @author F嘉阳
 * @date 2018-09-18 17:19
 */
@Slf4j
public class JavaDCourse implements DCourse {
    @Override
    public void study() {
        log.info("学习Java课程");
    }
}
```

Python课程

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

import lombok.extern.slf4j.Slf4j;

/**
 * 所有课程实现类后面都不应该修改，添加新课程则增加新实现类，满足开闭原则
 *
 * @author F嘉阳
 * @date 2018-09-18 17:19
 */
@Slf4j
public class PythonDCourse implements DCourse {
    @Override
    public void study() {
        log.info("学习Python课程");
    }
}
```

Vue课程

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-09-18 17:19
 */
@Slf4j
public class VueDCourse implements DCourse {
    @Override
    public void study() {
        log.info("学习Vue课程");
    }
}
```

##### 三种注入方式——参数注入

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

/**
 * @author F嘉阳
 * @date 2018-09-18 17:20
 */
public class Student {

    /**
     * 具体学习哪个课程，交给高层模块通过参数注入
     *
     * @param course 课程
     */
    public void studyCourse(DCourse course) {
        course.study();
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 依赖倒置接口方法实现后单元测试
 * 高层模块
 */
class StudentTest {

    /**
     * 修改后高层不依赖低层模块{@link Student}的实现
     * 此时如果高层模块要学多一门课程
     * 则不需要修改Student，直接增加一个实现{@link DCourse} 的接口课程即可
     * 实现了高层模块与低层模块的解耦
     */
    @Test
    void study() {
        Student student = new Student();
        student.studyCourse(new JavaDCourse());
        student.studyCourse(new PythonDCourse());
        student.studyCourse(new VueDCourse());
    }
}
```



##### 三种注入方式——参数注入

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

/**
 * 构造器注入课程
 *
 * @author F嘉阳
 * @date 2018-09-18 17:40
 */
public class Student2 {

    private DCourse dCourse;

    public Student2(DCourse dCourse) {
        this.dCourse = dCourse;
    }

    /**
     * 具体学习哪个课程，交给高层模块通过构造器注入
     */
    public void studyCourse() {
        dCourse.study();
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 依赖倒置构造器实现实现后单元测试
 * 高层模块
 */
class Student2Test {

    @Test
    void study() {
        Student2 student = new Student2(new JavaDCourse());
        student.studyCourse();
    }
}
```



##### 三种注入方式——setter注入

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

/**
 * Setter注入课程
 *
 * @author F嘉阳
 * @date 2018-09-18 17:40
 */
public class Student3 {

    private DCourse dCourse;

    public Student3() {
    }

    /**
     * 具体学习哪个课程，交给高层模块通过构造器注入
     */
    public void studyCourse() {
        dCourse.study();
    }

    public void setdCourse(DCourse dCourse) {
        this.dCourse = dCourse;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.dependenceinversion.after;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 依赖倒置Setter实现实现后单元测试
 * 高层模块
 */
class Student3Test {

    @Test
    void study() {
        Student3 student = new Student3();
        student.setdCourse(new JavaDCourse());
        student.studyCourse();

        student.setdCourse(new PythonDCourse());
        student.studyCourse();

        student.setdCourse(new VueDCourse());
        student.studyCourse();
    }
}
```



## 单一职责原则

### 介绍

定义:不要存在多于一个导致类变更的原因

一个类/接口/方法只负责一项职责

优点:降低类的复杂度、提高类的可读性提高系统的可维护性、降低变更引起的风险



### 代码样例

#### 改造前

类单一职责

```java
package top.fjy8018.designpattern.principle.singleresponsibility.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 单一职责：一个类应该只有一个发生变化的原因
 *
 * @author F嘉阳
 * @date 2018-09-22 10:35
 */
@Slf4j
public class Bird {
    /**
     * 当前类有两个职责：走和飞
     * 没有使用单一职责当业务变更必须修改代码，带来风险
     *
     * @param name
     */
    public void mainMoveMode(String name) {
        if ("鸵鸟".equals(name)) {
            log.info("{}用脚走", name);
        } else {
            log.info("{}用翅膀飞", name);
        }
        // 当边界值越来越多（承担更多职责）的时候变更变得更加困难
    }
}
```

方法单一职责

```java
package top.fjy8018.designpattern.principle.singleresponsibility.before;

/**
 * 方法单一职责
 *
 * @author F嘉阳
 * @date 2018-09-22 10:57
 */
public class Method {
    private String name;
    private Integer age;

    /**
     * 此时该方法承担两个职责：更新名字和年龄
     *
     * @param name
     * @param age
     */
    public void updateUserInfo(String name, Integer age) {
        this.name = name;
        this.age = age;
    }

    /**
     * 承担多个职责，同时包含可变参数，即不一定更新哪些属性
     *
     * @param name
     * @param properties
     */
    public void updateProperties(String name, String... properties) {
        // TODO 更新用户名和属性
    }
}
```

接口单一职责

```java
package top.fjy8018.designpattern.principle.singleresponsibility.before;

/**
 * 接口单一职责
 * 当前接口承担多个职责
 *
 * @author F嘉阳
 * @date 2018-09-22 10:43
 */
public interface SCourse {
    /**
     * 课程信息相关职责
     */
    String getCourseName();

    byte[] getCourseVideo();

    /**
     * 课程管理相关职责
     */
    void paid();

    void studyCourse();
}
```



#### 改造后

类单一职责

```java
package top.fjy8018.designpattern.principle.singleresponsibility.after;

import lombok.extern.slf4j.Slf4j;

/**
 * 当前类只承担一个职责：飞
 *
 * @author F嘉阳
 * @date 2018-09-22 10:40
 */
@Slf4j
public class FlyBird {
    public void mainMoveMode(String name) {
        log.info("{}用翅膀飞", name);
    }
}
```



```java
package top.fjy8018.designpattern.principle.singleresponsibility.after;

import lombok.extern.slf4j.Slf4j;

/**
 * 当前类只承担一个职责：走
 *
 * @author F嘉阳
 * @date 2018-09-22 10:40
 */
@Slf4j
public class WalkBird {
    public void mainMoveMode(String name) {
        log.info("{}用脚走", name);
    }
}
```

方法单一职责

```java
package top.fjy8018.designpattern.principle.singleresponsibility.after;

/**
 * 方法单一职责
 *
 * @author F嘉阳
 * @date 2018-09-22 10:57
 */
public class Method {
    private String name;
    private Integer age;

    /**
     * 此时该方法承担一个职责：更新名字
     *
     * @param name
     */
    public void updateUserName(String name) {
        this.name = name;
    }

    /**
     * 只更新年龄
     *
     * @param age
     */
    public void updateUserAge(Integer age) {
        this.age = age;
    }

    /**
     * 对于有布尔值的方法也建议拆分
     *
     * @param name
     * @param bool
     */
    public void updateProperties(String name, boolean bool) {
        if (bool) {
            // TODO
        } else {
            // TODO
        }
        this.name = name;
    }
}
```

接口单一职责

类图

![image-20200120141648612](/images/recovered/c76476e410f66921d804.png)

课程管理相关

```java
package top.fjy8018.designpattern.principle.singleresponsibility.after;

/**
 * 只承担课程管理相关职责
 *
 * @author F嘉阳
 * @date 2018-09-22 10:46
 */
public interface CourseManagement {
    void paid();

    void studyCourse();
}
```

课程信息相关

```java
package top.fjy8018.designpattern.principle.singleresponsibility.after;

/**
 * 一个接口变更，只对一个实现类有影响，对其他接口无关
 * 只承担课程信息相关职责
 *
 * @author F嘉阳
 * @date 2018-09-22 10:45
 */
public interface CourseInfo {
    String getCourseName();

    byte[] getCourseVideo();
}
```

课程实现类

```java
package top.fjy8018.designpattern.principle.singleresponsibility.after;

import lombok.extern.slf4j.Slf4j;

/**
 * 课程实现类
 * 接口实现单一职责后可以通过实现类多重实现的方式组合
 *
 * @author F嘉阳
 * @date 2018-09-22 10:46
 */
@Slf4j
public class CourseImpl implements CourseInfo, CourseManagement {
    @Override
    public String getCourseName() {
        return "设计模式课程";
    }

    @Override
    public byte[] getCourseVideo() {
        return new byte[0];
    }

    @Override
    public void paid() {
        log.info("支付成功");
    }

    @Override
    public void studyCourse() {
        log.info("学习课程");
    }
}
```

​        

测试类

```java
package top.fjy8018.designpattern.principle.singleresponsibility.before;

import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.principle.singleresponsibility.after.FlyBird;
import top.fjy8018.designpattern.principle.singleresponsibility.after.WalkBird;

import static org.junit.jupiter.api.Assertions.*;

class BirdTest {

    /**
     * 没有使用单一职责情况
     */
    @Test
    void mainMoveModeBefore() {
        Bird bird = new Bird();
        bird.mainMoveMode("大雁");
        // 业务变更
        bird.mainMoveMode("鸵鸟");
    }

    /**
     * 使用单一职责后
     * 不同职责调用交由应用层负责
     */
    @Test
    void mainMoveModeAfter() {
        FlyBird flyBird = new FlyBird();
        flyBird.mainMoveMode("大雁");
        WalkBird walkBird = new WalkBird();
        walkBird.mainMoveMode("鸵鸟");
    }
}
```



### 介绍

定义:用多个专门的接口,而不使用单一的总接口, 客户端不应该依赖它不需要的接口

一个类对一个类的依赖应该建立在最小的接口上    建立单一接口,不要建立庞大臃肿的接口

尽量细化接口,接口中的方法尽量少

注意适度原则,一定要适度

优点:符合我们常说的高内聚低耦合的设计思想，从而使得类具有很好的可读性、可扩展性和可维护性。

### 代码样例

#### 改造前

类图

![image-20200120142833920](/images/recovered/a0d495bed12d966adbca.png)

接口

```java
package top.fjy8018.designpattern.principle.interfacesegregation.before;

/**
 * 接口隔离原则：客户端不应该依赖它不需要的接口；一个类对另一个类的依赖应该建立在最小的接口上
 * 旧版：一个接口承担过多功能，使得实现类对有些不需要的方法也必须实现
 *
 * @author F嘉阳
 * @date 2018-09-22 11:40
 */
public interface IAnimalAction {
    void eat();

    void fly();

    void swim();
}
```

实现类

```java
package top.fjy8018.designpattern.principle.interfacesegregation.before;

/**
 * @author F嘉阳
 * @date 2018-09-22 11:41
 */
public class Bird implements IAnimalAction {
    @Override
    public void eat() {

    }

    @Override
    public void fly() {

    }

    @Override
    public void swim() {
        // 不需要的接口，但被迫实现
    }
}
```



```java
package top.fjy8018.designpattern.principle.interfacesegregation.before;

/**
 * @author F嘉阳
 * @date 2018-09-22 11:44
 */
public class Dog implements IAnimalAction {
    @Override
    public void eat() {

    }

    @Override
    public void fly() {
        // 不需要的接口，但被迫实现
    }

    @Override
    public void swim() {

    }
}
```



#### 改造后

类图

![image-20200120142946445](/images/recovered/4a88eefd7237878b5437.png)

接口

```java
package top.fjy8018.designpattern.principle.interfacesegregation.after;

/**
 * 隔离接口方法，但注意适度，不是越少越好
 *
 * @author F嘉阳
 * @date 2018-09-22 11:42
 */
public interface IEatAction {
    void eat();
}
```



```java
package top.fjy8018.designpattern.principle.interfacesegregation.after;

/**
 * @author F嘉阳
 * @date 2018-09-22 11:43
 */
public interface IFlyAction {
    void fly();
}
```



```java
package top.fjy8018.designpattern.principle.interfacesegregation.after;

/**
 * @author F嘉阳
 * @date 2018-09-22 11:43
 */
public interface ISwimAction {
    void swim();
}
```

实现类

```java
package top.fjy8018.designpattern.principle.interfacesegregation.after;

/**
 * 实现类可以实现需要的接口
 *
 * @author F嘉阳
 * @date 2018-09-22 11:43
 */
public class Bird implements IFlyAction, IEatAction {
    @Override
    public void eat() {

    }

    @Override
    public void fly() {

    }
}
```



```java
package top.fjy8018.designpattern.principle.interfacesegregation.after;

/**
 * 接口隔离注重接口方法之间的关系
 * 单一职责关心类、方法、接口承担的职责，即一个接口只要职责单一就不关系方法之间的关系
 *
 * @author F嘉阳
 * @date 2018-09-22 11:44
 */
public class Dog implements IEatAction, ISwimAction {
    @Override
    public void eat() {

    }

    @Override
    public void swim() {

    }
}
```

## 迪米特原则

### 介绍      

定义:一个对象应该对其他对象保持最少的了解。又叫最少知道原则

尽量降低类与类之间的耦合

优点:降低类之间的耦合

特点：

- 强调只和朋友交流,不和陌生人说话

- 朋友:  
  - 出现在成员变量、方法的输入、输出参数中的类称为成员朋友类，而出现在方法体内部的类不属于朋友类。

### 代码样例

类图

![image-20200120143636461](/images/recovered/56913a2ffc011a5d3b43.png)

```java
package top.fjy8018.designpattern.principle.demeter;

import lombok.extern.slf4j.Slf4j;

import java.util.List;

/**
 * 迪米特法则（Law of Demeter）又叫作最少知识原则（Least Knowledge Principle 简写LKP），
 * 就是说一个对象应当对其他对象有尽可能少的了解
 * 和朋友交流，不和陌生人说话
 * 朋友指的是出现在类成员变量、方法参数、返回值的对象
 *
 * @author F嘉阳
 * @date 2018-09-22 17:02
 */
@Slf4j
public class Boss {

    /**
     * 此处朋友为{@link TeamLeader},{@link DCourse}不是类成员变量、方法参数、返回值的对象，所以不应该在类内引用
     * 即当前类知道的应该尽可能少
     *
     * @param teamLeader
     */
    public void commandCheckNumber(TeamLeader teamLeader) {
        List courses = teamLeader.checkNumberOfCourses();
        log.info("课程的数量是：{}", courses.size());
    }
}
```



```java
package top.fjy8018.designpattern.principle.demeter;

/**
 * @author F嘉阳
 * @date 2018-09-22 17:04
 */
public class DCourse {
}
```



```java
package top.fjy8018.designpattern.principle.demeter;

import java.util.ArrayList;
import java.util.List;

/**
 * @author F嘉阳
 * @date 2018-09-22 17:04
 */
public class TeamLeader {

    /**
     * {@link DCourse}作为方法返回值，属于“朋友”
     *
     * @return
     */
    public List<DCourse> checkNumberOfCourses() {
        List<DCourse> courseList = new ArrayList<DCourse>();
        for (int i = 0; i < 20; i++) {
            courseList.add(new DCourse());
        }
        return courseList;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.demeter;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class BossTest {

    @Test
    void commandCheckNumber() {
        Boss boss = new Boss();
        boss.commandCheckNumber(new TeamLeader());
    }
}
```



## 里氏替换原则

### 介绍

定义:    如果对每一个类型为T1的对象o1,都有类型为T2的对象o2,使得以T1定义的所有程序P在所有的对象o1都替换成2时,  程序P的行为没有发生变化,那么类型T2是类型T1的子类型。

定义扩展:    一个软件实体如果适用一个父类的话那一定适用于其子类,所有引用父类的地方必须能透明地使用其子类的对象,子类对象能够  替换父类对象,而程序逻辑不变。



引申意义:子类可以扩展父类的功能,但不能改变父类原有的功能。

- 含义1:子类可以实现父类的抽象方法但不能覆盖父类的非抽象方法。

- 含义2:子类中可以增加自己特有的方法。

### 代码样例——类级别

改造前

类图

![image-20200120144312693](/images/recovered/a231f4b97f7c510ebe4e.png)

```java
package top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.before;

/**
 * 里氏替换原则：如果对每一个类型为S的对象o1，都有类型为T的对象o2，使得以T定义的所有程序P在所有的对象o1都代换为o2，程序P的行为没有发生变化，那么类型S是类型T的子类型
 * 即：所有使用父类对象的地方替换成子类对象依然正常运行
 *
 * @author F嘉阳
 * @date 2018-09-22 20:01
 */
public class Rectangle {
    private long length;
    private long width;

    public long getLength() {
        return length;
    }

    public void setLength(long length) {
        this.length = length;
    }

    public long getWidth() {
        return width;
    }

    public void setWidth(long width) {
        this.width = width;
    }
}
```



```java
package top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.before;

/**
 * @author F嘉阳
 * @date 2018-09-22 20:03
 */
public class Square extends Rectangle {
    private long sideLength;

    @Override
    public long getLength() {
        return sideLength;
    }

    /**
     * 覆盖了父类的实现，不满足里氏替换原则
     *
     * @param length
     */
    @Override
    public void setLength(long length) {
        this.sideLength = length;
    }

    @Override
    public long getWidth() {
        return sideLength;
    }

    @Override
    public void setWidth(long width) {
        this.sideLength = width;
    }
}
```



改造后

类图

![image-20200120144357908](/images/recovered/1a4eeedd93237c405b66.png)

```java
package top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.after;

/**
 * 通过四边形接口连接，防止继承泛滥
 *
 * @author F嘉阳
 * @date 2018-09-22 20:11
 */
public interface Quadrangle {
    long getWidth();

    long getLength();
}
```



```java
package top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.after;

/**
 * @author F嘉阳
 * @date 2018-09-22 20:03
 */
public class ASquare implements Quadrangle {
    private long sideLength;

    @Override
    public long getWidth() {
        return sideLength;
    }

    @Override
    public long getLength() {
        return sideLength;
    }

    public void setLength(long sideLength) {
        this.sideLength = sideLength;
    }
}
```



```java
package top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.after;

/**
 * 里氏替换原则：如果对每一个类型为S的对象o1，都有类型为T的对象o2，使得以T定义的所有程序P在所有的对象o1都代换为o2，程序P的行为没有发生变化，那么类型S是类型T的子类型
 * 即：所有使用父类对象的地方替换成子类对象依然正常运行
 *
 * @author F嘉阳
 * @date 2018-09-22 20:01
 */
public class ARectangle implements Quadrangle {
    private long length;

    private long width;

    @Override
    public long getWidth() {
        return width;
    }

    public void setWidth(long width) {
        this.width = width;
    }

    @Override
    public long getLength() {
        return length;
    }

    public void setLength(long length) {
        this.length = length;
    }
}
```

测试类

```java
package top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.before;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.after.ARectangle;
import top.fjy8018.designpattern.principle.liskovsubstitution.classdemo.after.Quadrangle;

@Slf4j
class SquareTest {

    /**
     * resize要求传入父类对象，对长宽进行设置
     *
     * @param rectangle
     */
    public static void resize(Rectangle rectangle) {
        while (rectangle.getWidth() <= rectangle.getLength()) {
            rectangle.setWidth(rectangle.getWidth() + 1);
            log.info("width:{} length:{}", rectangle.getWidth(), rectangle.getLength());
            if (rectangle.getWidth() > 50 || rectangle.getLength() > 50) {
                log.error("方法溢出");
                break;
            }
        }
        log.info("resize方法结束 width:{} length:{}", rectangle.getWidth(), rectangle.getLength());
    }

    public static void resize(Quadrangle quadrangle) {
        while (quadrangle.getWidth() <= quadrangle.getLength()) {
//            quadrangle.setWidth(quadrangle.getWidth()+1);报错，原有方法已经不能正确运行，说明原有方法设计存在问题
            log.info("width:{} length:{}", quadrangle.getWidth(), quadrangle.getLength());
            if (quadrangle.getWidth() > 50 || quadrangle.getLength() > 50) {
                log.error("方法溢出");
                break;
            }
        }
        log.info("resize方法结束 width:{} length:{}", quadrangle.getWidth(), quadrangle.getLength());
    }

    @Test
    void before() {
        // 是长方形时业务正常运行
        Rectangle rectangle = new Rectangle();
        rectangle.setWidth(10);
        rectangle.setLength(20);
        resize(rectangle);
        // 使用之类替换父类对象，业务无法运行，方法溢出
        Square square = new Square();
        square.setLength(40);
        resize(square);
    }

    @Test
    void after() {
        // 通过里氏替换原则改造后
        ARectangle aRectangle = new ARectangle();
        aRectangle.setLength(20);
        aRectangle.setWidth(10);

    }
}
```



### 代码样例——方法级别

改造前

```java
package top.fjy8018.designpattern.principle.liskovsubstitution.method.input.before;

import lombok.extern.slf4j.Slf4j;

import java.util.Map;


/**
 * @author F嘉阳
 * @date 2018-09-23 11:29
 */
@Slf4j
class Base {

    public void method(Map map) {
        log.info("父类被执行");
    }
}
```



```java
package top.fjy8018.designpattern.principle.liskovsubstitution.method.input.before;

import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;

/**
 * @author F嘉阳
 * @date 2018-09-23 11:30
 */
@Slf4j
class Child extends Base {

    public void method(HashMap map) {
        log.info("子类HashMap入参方法被执行");
    }

}
```



改造后

```java
package top.fjy8018.designpattern.principle.liskovsubstitution.method.input.after;

import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;

/**
 * @author F嘉阳
 * @date 2018-09-23 11:29
 */
@Slf4j
class Base {

    public void method(HashMap map) {
        log.info("父类被执行");
    }
}
```



```java
package top.fjy8018.designpattern.principle.liskovsubstitution.method.input.after;

import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;
import java.util.Map;

/**
 * 里氏替换原则要求方法入参必须比父类范围更宽，返回值必须比父类更窄
 *
 * @author F嘉阳
 * @date 2018-09-23 11:30
 */
@Slf4j
class Child extends Base {

    /**
     * 方法重写，入参必须等于父类或者比父类范围更宽
     * 而返回值比父类更窄已经交由IDE判断，若不符合，则编译不通过
     *
     * @param map
     */
    @Override
    public void method(HashMap map) {
        log.info("子类HashMap入参方法被执行");
    }

    /**
     * 方法重写，是子类额外的方法
     *
     * @param map
     */
    public void method(Map map) {
        log.info("子类Map入参方法被执行");
    }


}
```

测试类

```java
package top.fjy8018.designpattern.principle.liskovsubstitution.method.input.after;

import org.junit.jupiter.api.Test;

import java.util.HashMap;

class ChildTest {

    @Test
    void before() {

    }

    @Test
    void after() {
        Child child = new Child();
        // 此时希望调用子类重写的方法，若子类没重写，则应执行父类的方法
        child.method(new HashMap());
    }
}
```



## 合成(组合)聚合复用原则

### 介绍

定义:尽量使用对象组合/聚合,而不是继承关系达到软件复用的目的

聚合hasA和组合 contains-A

优点:可以使系统更加灵活,降低类与类之间的耦合度,一个类的变化对其他类造成的影响相对较少



何时使用合成/聚合、继承

聚合has-A、组合 contains-A继承is-A

### 代码样例

改造前

类图

![image-20200120150405004](/images/recovered/4bf3c4160b17699ac6f0.png)

```java
package top.fjy8018.designpattern.principle.compositionaggregation.before;

/**
 * 合成复用原则：要尽量使用组合，尽量不要使用继承
 *
 * @author F嘉阳
 * @date 2018-09-23 15:50
 */
public class DBConnection {
    public String getConnection() {
        return "MySQL数据库连接";
    }
}
```



```java
package top.fjy8018.designpattern.principle.compositionaggregation.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 直接使用继承，属于聚合关系，业务变更困难
 *
 * @author F嘉阳
 * @date 2018-09-23 15:51
 */
@Slf4j
public class ProductDao extends DBConnection {

    public void addProduct() {
        log.info("使用{}", super.getConnection());
    }
}
```



改造后

类图

![image-20200120150804432](/images/recovered/6fd022c6d0e22fda3460.png)

```java
package top.fjy8018.designpattern.principle.compositionaggregation.after;

/**
 * 合成复用原则：要尽量使用组合，尽量不要使用继承
 *
 * @author F嘉阳
 * @date 2018-09-23 15:50
 */
public abstract class ADBConnection {
    public abstract String getConnection();
}
```



```java
package top.fjy8018.designpattern.principle.compositionaggregation.after;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-09-23 15:51
 */
@Slf4j
public class AProductDao {

    private final ADBConnection connection;

    /**
     * 通过构造器注入，解除继承关系，同时符合里氏替换原则和开闭原则
     *
     * @param connection
     */
    public AProductDao(ADBConnection connection) {
        this.connection = connection;
    }

    public void addProduct() {
        log.info("使用{}", connection.getConnection());
    }
}
```



```java
package top.fjy8018.designpattern.principle.compositionaggregation.after;

/**
 * @author F嘉阳
 * @date 2018-09-23 15:56
 */
public class MysqlConnection extends ADBConnection {
    @Override
    public String getConnection() {
        return "MySQL数据库连接";
    }
}
```



```java
package top.fjy8018.designpattern.principle.compositionaggregation.after;

/**
 * @author F嘉阳
 * @date 2018-09-23 15:57
 */
public class OracleConnection extends ADBConnection {
    @Override
    public String getConnection() {
        return "Oracle数据库连接";
    }
}
```



测试类

```java
package top.fjy8018.designpattern.principle.compositionaggregation.before;

import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.principle.compositionaggregation.after.AProductDao;
import top.fjy8018.designpattern.principle.compositionaggregation.after.MysqlConnection;
import top.fjy8018.designpattern.principle.compositionaggregation.after.OracleConnection;

import static org.junit.jupiter.api.Assertions.*;

class ProductDaoTest {

    @Test
    void before() {
        ProductDao productDao = new ProductDao();
        productDao.addProduct();
    }

    @Test
    void after() {
        // 变更交由业务层决定
        AProductDao productDao1 = new AProductDao(new MysqlConnection());
        productDao1.addProduct();
        AProductDao productDao2 = new AProductDao(new OracleConnection());
        productDao2.addProduct();
    }
}
```
