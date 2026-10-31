{
  "title": "设计模式学习——结构型",
  "date": "2020-03-04T10:44:04+08:00",
  "lastmod": "2020-03-04T10:44:04+08:00",
  "typecho_cid": 239,
  "url": "/archives/239/",
  "comments": false,
  "draft": false,
  "slug": "239",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "设计模式"
  ],
  "math": false
}

## 外观模式

### 介绍

又叫门面模式,提供了一个统一的接口,用来访问**子系统**中的一群接口

外观模式定义了一个高层接口,让子系统更容易使用

类型：结构型



适用场景：

- 子系统越来越复杂,增加外观模式提供简单调用接口            
- 构建多层系统结构,利用外观对象作为每层的入口,简化层间调用



优点：

- 简化了调用过程，无需了解深入子系统，防止带来风险。
- 减少系统依赖、松散耦合
- 更好的划分访问层次
- 符合迪米特法则，即最少知道原则



缺点：

- 增加子系统、扩展子系统行为容易引入风险
- 不符合开闭原则



相关的设计模式

- 外观模式和中介者模式
- 外观模式和单例模式
- 外观模式和抽象工厂模式



### 代码样例

#### 改造前

类图

![image-20200228111432933](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228111432933.png)



```java
package top.fjy8018.designpattern.pattern.structural.facade.before;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 外观模式又叫门面模式,提供了一个统一的接口,用来访问子系统中的一群接口
 * 积分礼物
 *
 * @author F嘉阳
 * @date 2020/2/28 10:33
 */
@Getter
@AllArgsConstructor
public class PointGift {
    private String name;
}
```



子系统一：积分校验子系统

```java
package top.fjy8018.designpattern.pattern.structural.facade.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 积分校验子系统
 *
 * @author F嘉阳
 * @date 2020/2/28 10:34
 */
@Slf4j
public class QualifyService {

    /**
     * 模拟积分校验逻辑
     * @param pointGift
     * @return
     */
    public boolean isAvalible(PointGift pointGift){
        log.info("校验礼物 {} 通过，积分校验通过，库存通过",pointGift.getName());
        return true;
    }
}
```



子系统二：积分支付校验子系统

```java
package top.fjy8018.designpattern.pattern.structural.facade.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 积分支付校验子系统
 *
 * @author F嘉阳
 * @date 2020/2/28 10:37
 */
@Slf4j
public class PointPaymentService {

    public boolean pay(PointGift pointGift){
        // 扣减积分逻辑
        log.info("支付礼物 {} 积分成功",pointGift.getName());
        return true;
    }
}
```



子系统三：物流子系统

```java
package top.fjy8018.designpattern.pattern.structural.facade.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 物流子系统
 *
 * @author F嘉阳
 * @date 2020/2/28 10:39
 */
@Slf4j
public class ShippingService {

    /**
     * 返回物流运单号
     *
     * @param pointGift
     * @return
     */
    public String shipGift(PointGift pointGift){
        // 物流系统对接逻辑
        log.info("礼物 {} 进入物流系统",pointGift.getName());
        return "123456";
    }
}
```



外观类——礼物兑换逻辑

```java
package top.fjy8018.designpattern.pattern.structural.facade.before;

import lombok.extern.slf4j.Slf4j;

/**
 * 外观类——礼物兑换逻辑
 *
 * 该服务定义了与各个子系统交互的逻辑，业务系统无需知道与内部子系统的交互逻辑，符合迪米特法则
 * @author F嘉阳
 * @date 2020/2/28 10:44
 */
@Slf4j
public class GiftExchangeService {

    private PointPaymentService pointPaymentService;

    private QualifyService qualifyService;

    private ShippingService shippingService;

    public void setPointPaymentService(PointPaymentService pointPaymentService) {
        this.pointPaymentService = pointPaymentService;
    }

    public void setQualifyService(QualifyService qualifyService) {
        this.qualifyService = qualifyService;
    }

    public void setShippingService(ShippingService shippingService) {
        this.shippingService = shippingService;
    }

    /**
     * 系统交互逻辑
     *
     * @param pointGift
     */
    public void giftExchange(PointGift pointGift){
        if (qualifyService.isAvalible(pointGift)){
            // 资格校验通过
            if (pointPaymentService.pay(pointGift)){
                // 如果积分支付成功
                String shippingOrderNo = shippingService.shipGift(pointGift);
                log.info("物流系统下单成功，订单号为{}",shippingOrderNo);
            }
        }
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.structural.facade.before;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

/**
 * @author F嘉阳
 * @date 2020/2/28 10:53
 */
@Slf4j
class GiftExchangeServiceTest {

    @Test
    void giftExchange() {
        PointGift pointGift = new PointGift("手环");
        // 注入服务
        GiftExchangeService exchangeService = new GiftExchangeService();
        exchangeService.setPointPaymentService(new PointPaymentService());
        exchangeService.setQualifyService(new QualifyService());
        exchangeService.setShippingService(new ShippingService());
        // 兑换
        exchangeService.giftExchange(pointGift);
    }
}
```

执行结果

```
10:56:55.639 [main] INFO top.fjy8018.designpattern.pattern.structural.facade.before.QualifyService - 校验礼物 手环 通过，积分校验通过，库存通过
10:56:55.652 [main] INFO top.fjy8018.designpattern.pattern.structural.facade.before.PointPaymentService - 支付礼物 手环 积分成功
10:56:55.652 [main] INFO top.fjy8018.designpattern.pattern.structural.facade.before.ShippingService - 礼物 手环 进入物流系统
10:56:55.652 [main] INFO top.fjy8018.designpattern.pattern.structural.facade.before.GiftExchangeService - 物流系统下单成功，订单号为123456
```



#### 改造后

改造点很简单，只要将应用层注入的类在逻辑层注入即可

```java
package top.fjy8018.designpattern.pattern.structural.facade;

import lombok.extern.slf4j.Slf4j;

/**
 * 外观类——礼物兑换逻辑
 * <p>
 * 该服务定义了与各个子系统交互的逻辑，业务系统无需知道与内部子系统的交互逻辑，符合迪米特法则
 *
 * @author F嘉阳
 * @date 2020/2/28 10:44
 */
@Slf4j
public class GiftExchangeService {

    private PointPaymentService pointPaymentService = new PointPaymentService();

    private QualifyService qualifyService = new QualifyService();

    private ShippingService shippingService = new ShippingService();

    /**
     * 系统交互逻辑
     *
     * @param pointGift
     */
    public void giftExchange(PointGift pointGift) {
        if (qualifyService.isAvalible(pointGift)) {
            // 资格校验通过
            if (pointPaymentService.pay(pointGift)) {
                // 如果积分支付成功
                String shippingOrderNo = shippingService.shipGift(pointGift);
                log.info("物流系统下单成功，订单号为{}", shippingOrderNo);
            }
        }
    }
}
```



业务层

```java
package top.fjy8018.designpattern.pattern.structural.facade;

import lombok.extern.slf4j.Slf4j;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.RequestFacade;

/**
 * 外观类——礼物兑换逻辑
 * <p>
 * 该服务定义了与各个子系统交互的逻辑，业务系统无需知道与内部子系统的交互逻辑，符合迪米特法则
 *
 * 源码：
 * {@link org.springframework.jdbc.support.JdbcUtils} 对数据库相关的操作进行封装
 * {@link org.apache.ibatis.session.Configuration#newMetaObject(Object)} 对创建对象的方法进行封装
 * {@link RequestFacade} 其定义了操作HTTPRequest的公用方法 {@link Request} 在Request中都用该外观类操作
 * 其他类似逻辑：
 * {@link org.apache.catalina.connector.ResponseFacade}
 * {@link org.apache.catalina.session.StandardSessionFacade}
 *
 *
 * @author F嘉阳
 * @date 2020/2/28 10:44
 */
@Slf4j
public class GiftExchangeService {

    private PointPaymentService pointPaymentService = new PointPaymentService();

    private QualifyService qualifyService = new QualifyService();

    private ShippingService shippingService = new ShippingService();

    /**
     * 系统交互逻辑
     *
     * @param pointGift
     */
    public void giftExchange(PointGift pointGift) {
        if (qualifyService.isAvalible(pointGift)) {
            // 资格校验通过
            if (pointPaymentService.pay(pointGift)) {
                // 如果积分支付成功
                String shippingOrderNo = shippingService.shipGift(pointGift);
                log.info("物流系统下单成功，订单号为{}", shippingOrderNo);
            }
        }
    }
}
```



类图

![image-20200228112525024](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228112525024.png)

此时业务层无需关心子系统，只和外观类通信



## 装饰器模式

### 介绍

定义：在不改变原有对象的基础之上，将功能附加到对象上

提供了比继承更有弹性的替代方案（扩展原有对象功能）

类型：结构型



适用场景

- 扩展一个类的功能或给一个类添加附加职责
- 动态的给一个对象添加功能，这些功能可以再动态的撤销



优点

- 继承的有力补充,比继承灵活,不改变原有对象的情况下给一个对象  扩展功能
- 通过使用不同装饰类以及这些装饰类的排列组合,可以实现不同效果
- 符合开闭原则



缺点

- 会出现更多的代码,更多的类,增加程序复杂性
- 动态装饰时,多层装饰时会更复杂



相关设计模式

- 装饰者模式和代理模式
- 装饰者模式和适配器模式

### 代码样例

#### 改造前

类图

![image-20200228143741677](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228143741677.png)

`Battercake`

```java
package top.fjy8018.designpattern.pattern.structural.decorator.before;

/**
 * @author F嘉阳
 * @date 2018-09-27 16:56
 */
public class Battercake {
    protected String getDesc() {
        return "煎饼";
    }

    protected int cost() {
        return 8;
    }
}
```



`BattercakeWithEgg`

```java
package top.fjy8018.designpattern.pattern.structural.decorator.before;

/**
 * 不使用装饰器则只能通过类继承扩展功能，可能引起类爆炸
 *
 * @author F嘉阳
 * @date 2018-09-27 16:59
 */
public class BattercakeWithEgg extends Battercake {
    @Override
    protected String getDesc() {
        return super.getDesc() + " 加一个鸡蛋";
    }

    @Override
    protected int cost() {
        return super.cost() + 1;
    }
}
```



`BattercakeWithEggSausage`

```java
package top.fjy8018.designpattern.pattern.structural.decorator.before;

/**
 * @author F嘉阳
 * @date 2018-09-27 17:00
 */
public class BattercakeWithEggSausage extends BattercakeWithEgg {
    @Override
    protected String getDesc() {
        return super.getDesc() + " 加一根香肠";
    }

    @Override
    protected int cost() {
        return super.cost() + 2;
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.structural.decorator;

@Slf4j
class BattercakeTest {

    /**
     * 通过继承扩展灵活度低，无法自由组合
     */
    @Test
    void before() {
        Battercake battercake = new Battercake();
        log.info(battercake.getDesc() + " 销售价格:" + battercake.cost());

        Battercake battercakeWithEgg = new BattercakeWithEgg();
        log.info(battercakeWithEgg.getDesc() + " 销售价格:" + battercakeWithEgg.cost());


        Battercake battercakeWithEggSausage = new BattercakeWithEggSausage();
        log.info(battercakeWithEggSausage.getDesc() + " 销售价格:" + battercakeWithEggSausage.cost());
    }
}
```

输出

```
14:42:18.640 [main] INFO top.fjy8018.designpattern.pattern.structural.decorator.BattercakeTest - 煎饼 销售价格:8
14:42:18.652 [main] INFO top.fjy8018.designpattern.pattern.structural.decorator.BattercakeTest - 煎饼 加一个鸡蛋 销售价格:9
14:42:18.652 [main] INFO top.fjy8018.designpattern.pattern.structural.decorator.BattercakeTest - 煎饼 加一个鸡蛋 加一根香肠 销售价格:11
```



#### 改造后

类图

![image-20200228143941570](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228143941570.png)

所有类的抽象

```java
package top.fjy8018.designpattern.pattern.structural.decorator.after;

/**
 * 装饰器模式按照业务场景一般有两层抽象，
 * 一层是所有类的抽象，一层是所有装饰器的抽象，
 * 所有装饰器的抽象可以为实现类提供实现额外功能的能力
 *
 * @author F嘉阳
 * @date 2018-09-27 17:02
 */
public abstract class AbstractBattercake {
    public abstract String getDesc();

    public abstract int cost();
}
```



所有装饰器的抽象

```java
package top.fjy8018.designpattern.pattern.structural.decorator.after;

/**
 * @author F嘉阳
 * @date 2018-09-27 17:05
 */
public abstract class AbstractBattercakeDecorator extends AbstractBattercake {

    private AbstractBattercake abstractBattercake;

    /**
     * 通过构造器注入待装饰对象
     *
     * @param abstractBattercake
     */
    public AbstractBattercakeDecorator(AbstractBattercake abstractBattercake) {
        this.abstractBattercake = abstractBattercake;
    }

    /**
     * 实现类可以提供额外能力
     */
    protected abstract void doSomething();

    @Override
    public String getDesc() {
        return this.abstractBattercake.getDesc();
    }

    @Override
    public int cost() {
        return this.abstractBattercake.cost();
    }
}
```



```java
package top.fjy8018.designpattern.pattern.structural.decorator.after;

/**
 * Servlet源码：{@link javax.servlet.http.HttpServletRequestWrapper}
 * JDK源码：IO类：{@link java.io.BufferedReader} {@link java.io.BufferedInputStream}
 * Spring源码:{@link org.springframework.cache.transaction.TransactionAwareCacheDecorator}
 * mybatis源码：{@link org.apache.ibatis.cache.decorators.LruCache}
 *
 * @author F嘉阳
 * @date 2018-09-27 17:04
 */
public class ABattercake extends AbstractBattercake {
    @Override
    public String getDesc() {
        return "煎饼";
    }

    @Override
    public int cost() {
        return 8;
    }
}
```



```java
package top.fjy8018.designpattern.pattern.structural.decorator.after;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-09-27 17:08
 */
@Slf4j
public class EggBattercake extends AbstractBattercakeDecorator {

    public EggBattercake(AbstractBattercake abstractBattercake) {
        super(abstractBattercake);
    }

    @Override
    protected void doSomething() {
        log.info("EggBattercake doSomething...");
    }

    @Override
    public String getDesc() {
        return super.getDesc() + " 加一个鸡蛋";
    }

    @Override
    public int cost() {
        return super.cost() + 1;
    }
}
```



```java
package top.fjy8018.designpattern.pattern.structural.decorator.after;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-09-27 17:10
 */
@Slf4j
public class SausageBattercake extends AbstractBattercakeDecorator {
    public SausageBattercake(AbstractBattercake abstractBattercake) {
        super(abstractBattercake);
    }

    @Override
    protected void doSomething() {
        log.info("SausageBattercake doSomething...");
    }

    @Override
    public String getDesc() {
        return super.getDesc() + " 加一根香肠";
    }

    @Override
    public int cost() {
        return super.cost() + 2;
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.structural.decorator;

@Slf4j
class BattercakeTest {

    @Test
    void after() {
        // 自由组合装饰
        AbstractBattercake battercake = new EggBattercake(new SausageBattercake(new ABattercake()));
        log.info(battercake.getDesc() + " 销售价格:" + battercake.cost());

        AbstractBattercake battercake2 = new EggBattercake((new ABattercake()));
        log.info(battercake2.getDesc() + " 销售价格:" + battercake2.cost());
    }
}
```

输出

```
14:42:18.660 [main] INFO top.fjy8018.designpattern.pattern.structural.decorator.BattercakeTest - 煎饼 加一根香肠 加一个鸡蛋 销售价格:11
14:42:18.660 [main] INFO top.fjy8018.designpattern.pattern.structural.decorator.BattercakeTest - 煎饼 加一个鸡蛋 销售价格:9
```



## 适配器模式

### 介绍

定义将一个类的接口转换成客户期望的另一个接口

使原本接口不兼容的类可以一起工作

 类型：结构型



适用场景

- 不是软件设计阶段考虑的设计模式,是随着软件维护,由于  不同产品、不同厂家造成功能类似而接口不相同情况下的解决方案
- 已经存在的类,它的方法和需求不匹配时(方法结果相同或相似)



优点

- 能提高类的透明性和复用,现有的类复用但不需要改变          
- 目标类和适配器类解耦,提高程序扩展性
- 符合开闭原则



缺点

- 适配器编写过程需要全面考虑,可能会增加系统的复杂性              
- 增加系统代码可读的难度



分类与扩展

- 对象适配器
- 类适配器



相关设计模式

- 适配器模式和外观模式

### 代码样例——电源适配器

类图

![image-20200228145631132](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228145631132.png)

220V

```java
package top.fjy8018.designpattern.pattern.structural.adapter.poweradapter;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-10-09 16:24
 */
@Slf4j
public class AC220 {
    public int output() {
        int output = 220;
        log.info(this.getClass().getSimpleName() + "output:" + output + "V");
        return output;
    }
}
```



5V

```java
package top.fjy8018.designpattern.pattern.structural.adapter.poweradapter;

/**
 * @author F嘉阳
 * @date 2018-10-09 16:25
 */
public interface DC5 {
    int output();
}
```



适配器

```java
package top.fjy8018.designpattern.pattern.structural.adapter.poweradapter;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-10-09 16:25
 */
@Slf4j
public class Adapter implements DC5 {

    private AC220 ac220 = new AC220();

    @Override
    public int output() {
        int output220 = ac220.output();
        // 变压器模拟
        int output5 = output220 / 44;
        log.info("{} 输入{}V,输出{}V", this.getClass().getSimpleName(), output220, output5);
        return output5;
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.structural.adapter.poweradapter;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class AdapterTest {

    @Test
    void output() {
        AC220 ac220 = new AC220();
        ac220.output();

        DC5 dc5 = new Adapter();
        dc5.output();
    }
}
```

输出

```
14:58:14.719 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.poweradapter.AC220 - AC220output:220V
14:58:14.729 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.poweradapter.AC220 - AC220output:220V
14:58:14.729 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.poweradapter.Adapter - Adapter 输入220V,输出5V
```



### 代码样例——类适配器

类图

![image-20200228145904885](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228145904885.png)

目标类实现接口

```java
package top.fjy8018.designpattern.pattern.structural.adapter.classadapter;

/**
 * 目标类实现接口
 *
 * @author F嘉阳
 * @date 2018-10-09 16:05
 */
public interface Target {
    void request();
}
```



被适配对象

```java
package top.fjy8018.designpattern.pattern.structural.adapter.classadapter;

import lombok.extern.slf4j.Slf4j;

/**
 * 适配器模式：
 * 类适配器模式
 * 被适配对象
 *
 * @author F嘉阳
 * @date 2018-10-09 16:04
 */
@Slf4j
public class Adaptee {

    public void adapteeRequest() {
        log.info("adapteeRequest...");
    }
}
```



```java
package top.fjy8018.designpattern.pattern.structural.adapter.classadapter;

/**
 * 适配器模式：将一个类的接口转换成客户希望的另一个接口。适配器模式让那些接口不兼容的类可以一起工作
 *
 * JDK源码：{@link javax.xml.bind.annotation.adapters.XMLAdapter}
 * spring源码：{@link jdk.internal.org.objectweb.asm.commons.AdviceAdapter}
 *  {@link org.springframework.web.servlet.HandlerAdapter}
 * JPA源码：{@link org.springframework.orm.jpa.JpaVendorAdapter}
 *
 * @author F嘉阳
 * @date 2018-10-09 16:07
 */
public class Adapter extends Adaptee implements Target {
    @Override
    public void request() {
        // ... 新增业务逻辑
        super.adapteeRequest();
    }
}
```



目标类具体实现

```java
package top.fjy8018.designpattern.pattern.structural.adapter.classadapter;

import lombok.extern.slf4j.Slf4j;

/**
 * 目标类具体实现
 *
 * @author F嘉阳
 * @date 2018-10-09 16:06
 */
@Slf4j
public class ConcreteTarget implements Target {

    @Override
    public void request() {
        log.info("ConcreteTarget...");
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.structural.adapter.classadapter;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@Slf4j
class AdapterTest {

    /**
     * 通过适配器实现调用新接口将具体实现转发到旧类中实现
     */
    @Test
    void request() {
        Target newTarget = new ConcreteTarget();
        newTarget.request();

        Target adapter = new Adapter();
        adapter.request();
    }
}
```

输出

```
15:05:50.583 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.classadapter.ConcreteTarget - ConcreteTarget...
15:05:50.601 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.classadapter.Adaptee - adapteeRequest...
```



### 代码样例——对象适配器

类图

![image-20200228150732030](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228150732030.png)

`Target`、`Adaptee`、`ConcreteTarget`都与类适配器一致、`Adapter`修改如下

```java
package top.fjy8018.designpattern.pattern.structural.adapter.objectadapter;

/**
 * 适配器模式：将一个类的接口转换成客户希望的另一个接口。适配器模式让那些接口不兼容的类可以一起工作
 *
 * @author F嘉阳
 * @date 2018-10-09 16:07
 */
public class Adapter implements Target {

    /**
     * 将继承改成组合方式，降低耦合度
     */
    private Adaptee adaptee = new Adaptee();

    @Override
    public void request() {
        // ... 新增业务逻辑
        adaptee.adapteeRequest();
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.structural.adapter.objectadapter;

import org.junit.jupiter.api.Test;

class AdapterTest {

    @Test
    void request() {
        Target newTarget = new ConcreteTarget();
        newTarget.request();

        Target adapter = new Adapter();
        adapter.request();
    }
}
```

输出

```
15:10:00.866 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.objectadapter.ConcreteTarget - ConcreteTarget...
15:10:00.876 [main] INFO top.fjy8018.designpattern.pattern.structural.adapter.objectadapter.Adaptee - adapteeRequest...
```



## 享元模式

### 介绍

定义：提供了减少对象数量从而改善应用所需的对象结构的方式

运用共享技术有效地支持大量细粒度的对象

类型：结构型



适用场景

- 常常应用于系统底层的开发,以便解决系统的性能问题              
- 系统有大量相似对象、需要缓冲池的场景。



优点

- 减少对象的创建，降低内存中对象的数量，降低系统的内存，提高效率
- 减少内存之外的其他资源占用



缺点

- 关注内/外部状态、关注线程安全问题
- 使系统、程序的逻辑复杂化



分类与扩展

- 内部状态
- 外部状态



相关设计模式

- 享元模式和代理模式
- 享元模式和单例模式



### 代码样例

类图

![image-20200228154426599](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200228154426599.png)



```java
package top.fjy8018.designpattern.pattern.structural.flyweight;

/**
 * 享元模式：利用共享的方式来支持大量细粒度的对象，这些对象一部分内部状态是相同的。
 * JDK源码：{@link Integer#valueOf(int)} {@link Integer.IntegerCache}
 *  其他类型同理 {@link Long#valueOf(long)} {@link Boolean#valueOf(boolean)} {@link Byte#valueOf(byte)} {@link Character#valueOf(char)}
 * Apache源码：连接池{@link org.apache.commons.pool2.impl.GenericObjectPool#returnObject(Object)},连接池配置 {@link org.apache.commons.pool2.impl.GenericObjectPoolConfig}
 *
 * @author F嘉阳
 * @date 2018-10-14 16:13
 */
public interface Employee {
    void report();
}
```



员工工厂类

```java
package top.fjy8018.designpattern.pattern.structural.flyweight;

import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 员工工厂类
 *
 * @author F嘉阳
 * @date 2018-10-14 16:15
 */
@Slf4j
public class EmployeeFactory {
    private static final Map<String, Employee> EMPLOYEE_MAP = new ConcurrentHashMap<>();

    public static Employee getEmployee(String department) {
        Manager manager = (Manager) EMPLOYEE_MAP.get(department);
        // 如果在对象池中不存在，则新建对象
        if (manager == null) {
            manager = new Manager(department);
            log.warn("创建{}部门经理", department);
            String content = "报告内容……";
            log.warn("创建报告，内容为:{}", content);
            manager.setContent(content);
            EMPLOYEE_MAP.put(department, manager);
        }
        return manager;
    }
}
```



```java
package top.fjy8018.designpattern.pattern.structural.flyweight;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2018-10-14 16:16
 */
@Slf4j
public class Manager implements Employee {

    private String content;

    private String department;

    /**
     * 内部状态
     */
    private String title = "部门经理";

    public Manager(String department) {
        this.department = department;
    }

    public void setContent(String content) {
        this.content = content;
    }

    @Override
    public void report() {
        log.info("{}{}，汇报内容：{}", department, title, content);
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.structural.flyweight;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

@Slf4j
class EmployeeTest {

    private static final String departments[] = {"RD", "QA", "PM", "BD"};

    @Test
    void report() {
        for (int i = 0; i < 10; i++) {
            String department = departments[(int) (Math.random() * departments.length)];
            Employee employee = EmployeeFactory.getEmployee(department);
            employee.report();
        }
    }
}
```

输出

```
15:47:51.177 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建PM部门经理
15:47:51.187 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建报告，内容为:报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - PM部门经理，汇报内容：报告内容……
15:47:51.188 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建BD部门经理
15:47:51.188 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建报告，内容为:报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - BD部门经理，汇报内容：报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - BD部门经理，汇报内容：报告内容……
15:47:51.188 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建RD部门经理
15:47:51.188 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建报告，内容为:报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - RD部门经理，汇报内容：报告内容……
15:47:51.188 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建QA部门经理
15:47:51.188 [main] WARN top.fjy8018.designpattern.pattern.structural.flyweight.EmployeeFactory - 创建报告，内容为:报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - QA部门经理，汇报内容：报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - RD部门经理，汇报内容：报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - QA部门经理，汇报内容：报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - BD部门经理，汇报内容：报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - RD部门经理，汇报内容：报告内容……
15:47:51.188 [main] INFO top.fjy8018.designpattern.pattern.structural.flyweight.Manager - BD部门经理，汇报内容：报告内容……
```

由此可见，在初次创建部门经理后都无需重新创建，后续的汇报可以直接从对象池里直接获取s



## 组合模式

### 介绍

定义：将对象组合成树形结构以表示“部分-整体”的层次结构        

组合模式使客户端对单个对象和组合对象保持一致的方式处理

类型：结构型



适用场景

- 希望客户端可以忽略组合对象与单个对象的差异时        
- 处理一个树形结构时



优点

- 清楚地定义分层次的复杂对象,表示对象的全部或部分层次
- 让客户端忽略了层次的差异,方便对整个层次结构进行控制
- 简化客户端代码
- 



缺点

- 使设计变得更加抽象
- 限制类型时会较为复杂



相关设计模式

- 组合模式和访问者模式

### 代码样例

类图

![image-20200229092541389](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200229092541389.png)

课程抽象类

```java
package top.fjy8018.designpattern.pattern.structural.composite;

import java.awt.*;
import java.util.Collection;
import java.util.Map;

/**
 * 课程抽象类
 * 抽象组件应当多加考虑，哪些参数需要，哪些不需要
 *
 * JDK组合模式源码
 * {@link java.awt.Container#add(Component)} 增加一个父类操作
 * {@link java.util.HashMap#putAll(Map)}
 * {@link java.util.ArrayList#addAll(Collection)}
 *
 * Mybatis源码
 * {@link org.apache.ibatis.scripting.xmltags.SqlNode} 公共接口
 * 实现：{@link org.apache.ibatis.scripting.xmltags.MixedSqlNode}
 *
 * @author F嘉阳
 * @date 2020/2/28 16:19
 */
public abstract class CatalogComponent {

    public void add(CatalogComponent catalogComponent) {
        throw new UnsupportedOperationException("不支持添加操作");
    }

    public void remove(CatalogComponent catalogComponent) {
        throw new UnsupportedOperationException("不支持删除操作");
    }

    public String getName(CatalogComponent catalogComponent) {
        throw new UnsupportedOperationException("不支持获取名称操作");
    }

    public Double getPrice(CatalogComponent catalogComponent) {
        throw new UnsupportedOperationException("不支持获取价格操作");
    }

    public void print() {
        throw new UnsupportedOperationException("不支持获取打印操作");
    }
}
```



课程

```java
package top.fjy8018.designpattern.pattern.structural.composite;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * 课程
 * 重写抽象类需要充分考虑业务逻辑
 *
 * @author F嘉阳
 * @date 2020/2/28 16:24
 */
@Slf4j
@AllArgsConstructor
public class Course extends CatalogComponent {

    private String name;

    private Double price;

    @Override
    public String getName(CatalogComponent catalogComponent) {
        return this.name;
    }

    @Override
    public Double getPrice(CatalogComponent catalogComponent) {
        return this.price;
    }

    @Override
    public void print() {
        log.info("课程名称：{}，价格：{}",name,price);
    }
}
```



课程目录

```java
package top.fjy8018.designpattern.pattern.structural.composite;

import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.List;

/**
 * 课程目录
 * 可以添加目录节点
 *
 * @author F嘉阳
 * @date 2020/2/28 16:34
 */
@Slf4j
public class CourseCatalog extends CatalogComponent{

    private List<CatalogComponent> items = new ArrayList<>();

    private String name;

    public CourseCatalog(String name) {
        this.name = name;
    }

    @Override
    public void add(CatalogComponent catalogComponent) {
        items.add(catalogComponent);
    }

    @Override
    public void remove(CatalogComponent catalogComponent) {
        items.remove(catalogComponent);
    }

    @Override
    public void print() {
        log.info("课程目录名称：{}",name);
        items.forEach(CatalogComponent::print);
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.structural.composite;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/2/28 16:37
 */
@Slf4j
class CatalogComponentTest {

    @Test
    void add() {
        // 将课程与课程目录都认为是同一个类型，进行统一处理
        CatalogComponent linuxCourse = new Course("Linux课程",35.0);
        CatalogComponent windowsCourse = new Course("windows课程",61.0);
        CatalogComponent macOsCourse = new Course("macOs课程",20.0);

        CatalogComponent springCourse = new Course("spring课程",55.0);
        CatalogComponent servletCourse = new Course("servlet课程",11.0);

        // 课程目录
        CatalogComponent javaCourseCatalog = new CourseCatalog("java课程目录");
        CatalogComponent schoolCourseCatalog = new CourseCatalog("学校课程主目录");

        javaCourseCatalog.add(springCourse);
        javaCourseCatalog.add(servletCourse);

        // 既可以添加课程，也可以添加目录
        schoolCourseCatalog.add(linuxCourse);
        schoolCourseCatalog.add(windowsCourse);
        schoolCourseCatalog.add(macOsCourse);
        schoolCourseCatalog.add(javaCourseCatalog);

        schoolCourseCatalog.print();
    }
}
```

输出

```
09:24:29.687 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.CourseCatalog - 课程目录名称：学校课程主目录
09:24:29.691 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.Course - 课程名称：Linux课程，价格：35.0
09:24:29.693 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.Course - 课程名称：windows课程，价格：61.0
09:24:29.694 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.Course - 课程名称：macOs课程，价格：20.0
09:24:29.694 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.CourseCatalog - 课程目录名称：java课程目录
09:24:29.694 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.Course - 课程名称：spring课程，价格：55.0
09:24:29.694 [main] INFO top.fjy8018.designpattern.pattern.structural.composite.Course - 课程名称：servlet课程，价格：11.0
```



## 桥接模式

### 介绍

定义：将抽象部分与它的具体实现部分分离,使它们都可以独立地变化

通过组合的方式建立两个类之间联系,而不是继承

类型：结构型



适用场景

- 抽象和具体实现之间增加更多的灵活性        
- 一个类存在两个(或多个)独立变化的维度,且这两个(或多个)  维度都需要独立进行扩展      
- 不希望使用继承,或因为多层继承导致系统类的个数剧增



优点

- 分离抽象部分及其具体实现部分
- 提高了系统的可扩展性
- 符合开闭原则
- 符合合成复用原则



缺点

- 增加了系统的理解与设计难度
- 需要正确地识别出系统中两个独立变化的维度



相关设计模式

- 桥接模式和组合模式
- 桥接模式和适配器模式









### 代码样例

类图

![image-20200229143734541](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200229143734541.png)

桥接模式核心在于将抽象与实现通过组合模式连接，使抽象和实现都可以自由扩展



银行账号——行为接口

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import java.sql.Driver;
import java.sql.DriverManager;

/**
 * 银行账号——行为接口
 *
 * JDBC 为操作不同的数据库提供了同一个{@link java.sql.Connection} 连接
 * 由MySQL或Oracle连接驱动实现相关接口操作数据库
 *
 * {@link java.sql.Driver}
 * {@link DriverManager} 中的 {@link java.sql.DriverInfo}
 * 实现对 {@link java.sql.Driver} 的具体封装
 *
 * JDBC 实现的 {@link com.mysql.cj.jdbc.Driver} 初始化时调 {@link DriverManager#registerDriver(Driver)}
 *
 * @author F嘉阳
 * @date 2020/2/29 9:55
 */
public interface Account {

    /**
     * 打开一个账号
     *
     * @return
     */
    Account openAccount();

    /**
     * 查看账号类型
     */
    void showAccountType();
}
```



抽象银行

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import lombok.AllArgsConstructor;

/**
 * 抽象银行
 * 组合账户接口，交由子类实现具体的行为
 *
 * @author F嘉阳
 * @date 2020/2/29 10:05
 */
@AllArgsConstructor
public abstract class Bank {

    protected Account account;

    /**
     * 打开一个账户
     * 该方法定义与接口相同，方法名称可以不同
     * 当前抽象类的openAccount方法需要委托给Account接口openAccount方法实现
     * 当前类为抽象类，委托给接口的实现类执行，体现抽象与实现分离
     * @return
     */
    abstract Account openAccount();
}
```



活期账户

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import lombok.extern.slf4j.Slf4j;

/**
 * 活期账户
 *
 * @author F嘉阳
 * @date 2020/2/29 9:58
 */
@Slf4j
public class SavingAccount implements Account {
    /**
     * 打开一个账号
     *
     * @return
     */
    @Override
    public Account openAccount() {
        log.info("打开活期账户");
        return new SavingAccount();
    }

    /**
     * 查看账号类型
     */
    @Override
    public void showAccountType() {
        log.info("这是一个活期账户");
    }
}
```



定期账户

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import lombok.extern.slf4j.Slf4j;

/**
 * 定期账户
 *
 * @author F嘉阳
 * @date 2020/2/29 9:57
 */
@Slf4j
public class DepositAccount implements Account{
    /**
     * 打开一个账号
     *
     * @return
     */
    @Override
    public Account openAccount() {
        log.info("打开定期账户");
        return new DepositAccount();
    }

    /**
     * 查看账号类型
     */
    @Override
    public void showAccountType() {
        log.info("这是一个定期账户");
    }
}
```





广州银行实现

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2020/2/29 10:09
 */
@Slf4j
public class GCBBank extends Bank {

    public GCBBank(Account account) {
        super(account);
    }

    /**
     * 打开一个账户
     * 该方法定义与接口相同，方法名称可以不同
     * 当前抽象类的openAccount方法需要委托给Account接口openAccount方法实现
     * 当前类为抽象类，委托给接口的实现类执行，体现抽象与实现分离
     *
     * @return
     */
    @Override
    Account openAccount() {
        log.info("打开广州银行账户");
        // 委托
        account.openAccount();
        return account;
    }
}
```



工商银行实现

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2020/2/29 10:11
 */
@Slf4j
public class ICBCBank extends Bank {

    public ICBCBank(Account account) {
        super(account);
    }

    /**
     * 打开一个账户
     * 该方法定义与接口相同，方法名称可以不同
     * 当前抽象类的openAccount方法需要委托给Account接口openAccount方法实现
     * 当前类为抽象类，委托给接口的实现类执行，体现抽象与实现分离
     *
     * @return
     */
    @Override
    Account openAccount() {
        log.info("打开工商银行账户");
        // 委托
        account.openAccount();
        return account;
    }
}
```



测试

```java
package top.fjy8018.designpattern.pattern.structural.bridge;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/2/29 14:30
 */
@Slf4j
class AccountTest {

    @Test
    void openAccount() {
        Bank gcbBank = new GCBBank(new DepositAccount());
        Account gcbAccount = gcbBank.openAccount();
        gcbAccount.showAccountType();

        Bank icbcBank = new ICBCBank(new SavingAccount());
        Account icbcAccount = icbcBank.openAccount();
        icbcAccount.showAccountType();
    }
}
```



输出

```
14:36:13.478 [main] INFO top.fjy8018.designpattern.pattern.structural.bridge.GCBBank - 打开广州银行账户
14:36:13.488 [main] INFO top.fjy8018.designpattern.pattern.structural.bridge.DepositAccount - 打开定期账户
14:36:13.489 [main] INFO top.fjy8018.designpattern.pattern.structural.bridge.DepositAccount - 这是一个定期账户
14:36:13.489 [main] INFO top.fjy8018.designpattern.pattern.structural.bridge.ICBCBank - 打开工商银行账户
14:36:13.489 [main] INFO top.fjy8018.designpattern.pattern.structural.bridge.SavingAccount - 打开活期账户
14:36:13.489 [main] INFO top.fjy8018.designpattern.pattern.structural.bridge.SavingAccount - 这是一个活期账户
```



## 代理模式

### 介绍

定义：为其他对象提供一种代理,以控制对这个对象的访问        

代理对象在客户端和目标对象之间起到中介的作用        

类型：结构型



适用场景

- 保护目标对象            
- 增强目标对象



优点

- 代理模式能将代理对象与真实被调用的目标对象分离
- 一定程度上降低了系统的耦合度，扩展性好
- 保护目标对象
- 增强目标对象



缺点

- 代理模式会造成系统设计中类的数目增加
- 在客户端和目标对象增加一个代理对象，会造成请求处理速度变慢
- 增加系统的复杂度



分类与扩展

- 静态代理
  - 显式在业务实现类新增代理类实现代理功能，在代理类中对同名的业务方法进行增强和包装
- CGLib代理
  - 可以代理类
  - 代理类对象时，CGLib会生成代理类的**子类**，覆盖对应的方法
  - 由于利用了继承和重写的特性，若类或者方法被标识为`final`，则无法进行代理
- 动态代理
  - 无法代理类，可以代理**接口**
  - 若增强的对象新增了一个方法，而接口中不包含该新增方法，则无法进行增强
  - 对类的代理是在使用时动态创建了一个代理类的`class`文件，该`class`文件被字节码引擎执行，被代理类进行方法调用



#### Spring代理选择

- 当`Bean`有实现接口时, Spring就会用JDK的动态代理
- 当`Bean`没有实现接口时, Spring使用CGLib
- 可以强制使用 Cglib
  - 在Spring配置中加入`<aop: aspectj- autoproxy proxy-target-dass="true"/>`
- 参考资料： https://docs.spring.io/spring-framework/docs/current/spring-framework-reference/core.html 



#### 代理速度对比

- CGLib：基于ASM字节码生成，比反射效率高
- JDK动态代理
- 速度对比：万次执行的情况下，JDK7与JDK8的动态代理性能比CGLib速度快20%左右



相关设计模式

- 代理模式和装饰者模式
- 代理模式和适配器模式



### 代码样例——Spring 分库代理实现

自定义数据源上下文

```java
package top.fjy8018.designpattern.pattern.structural.proxy.db;

/**
 * 数据源上下文
 *
 * @author F嘉阳
 * @date 2020/2/29 16:27
 */
public class DataSourceContextHolder {
    /**
     * 存放数据源Bean Name
     */
    private static final ThreadLocal<String> CONTEXT_HOLDER = new ThreadLocal<>();

    /**
     * 配置哪个数据库，则动态数据源线程就会获取到哪个数据库
     * @param dbType
     */
    public static void setDBType(String dbType){
        CONTEXT_HOLDER.set(dbType);
    }

    public static String getDBType(){
        return CONTEXT_HOLDER.get();
    }

    /**
     * 清除，防止内存泄漏
     */
    public static void clear(){
        CONTEXT_HOLDER.remove();
    }
}
```



定义动态数据源

```java
package top.fjy8018.designpattern.pattern.structural.proxy.db;

import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;

/**
 * Spring分库实现
 *
 * @author F嘉阳
 * @date 2020/2/29 16:26
 */
public class DynamicDataSource extends AbstractRoutingDataSource {

    /**
     * 动态获取数据库
     * @return 当前线程所属数据源
     */
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.getDBType();
    }
}
```



多数据源配置

```xml
<bean id="dataSource" class="top.fjy8018.designpattern.pattern.structural.proxy.db.DynamicDataSource">
	<property name="targetDataSources">
		<map key-type="java.lang.String">
			<entry value-ref="db0" key="db0"></entry>
			<entry value-ref="db1" key="db1"></entry>
		</map>
	</property>
	<property name="defaultTargetDataSource" ref="db0"></property>
</bean>


<bean id="sqlSessionFactory" class="org.mybatis.spring.SqlSessionFactoryBean">
	<property name="dataSource" ref="dataSource" />
</bean>
```



### 代码样例——静态代理

类图

![image-20200302101343908](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200302101343908.png)

订单

```java
package top.fjy8018.designpattern.pattern.structural.proxy;

import lombok.Getter;
import lombok.Setter;

/**
 * 订单
 *
 * @author F嘉阳
 * @date 2020/2/29 16:12
 */
@Getter
@Setter
public class Order {

    private Object orderInfo;

    private Integer userId;
}
```

DAO层

```java
package top.fjy8018.designpattern.pattern.structural.proxy;

/**
 * DAO层——与业务无关
 * 仿mybatis
 *
 * @author F嘉阳
 * @date 2020/2/29 16:15
 */
public interface IOrderDao {

    int insert(Order order);
}
```



```java
package top.fjy8018.designpattern.pattern.structural.proxy;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2020/2/29 16:17
 */
@Slf4j
public class IOrderDaoImpl implements IOrderDao {
    @Override
    public int insert(Order order) {
        log.info("DAO层添加订单记录成功");
        return 1;
    }
}
```



订单服务层

```java
package top.fjy8018.designpattern.pattern.structural.proxy;

/**
 * 订单服务层
 *
 * @author F嘉阳
 * @date 2020/2/29 16:14
 */
public interface IOrderService {

    /**
     * 保存订单
     * @param order
     * @return 保存的行数
     */
    int save(Order order);
}
```



```java
package top.fjy8018.designpattern.pattern.structural.proxy;

import lombok.extern.slf4j.Slf4j;

/**
 * @author F嘉阳
 * @date 2020/2/29 16:16
 */
@Slf4j
public class IOrderServiceImpl implements IOrderService {

    /**
     * 模拟Spring注入
     */
    private IOrderDao orderDao = new IOrderDaoImpl();

    /**
     * 保存订单
     *
     * @param order
     * @return 保存的行数
     */
    @Override
    public int save(Order order) {
        log.info("Service层调用DAO层添加订单记录成功");
        return orderDao.insert(order);
    }
}
```



静态代理类

```java
package top.fjy8018.designpattern.pattern.structural.proxy.staticproxy;

import lombok.extern.slf4j.Slf4j;
import top.fjy8018.designpattern.pattern.structural.proxy.IOrderService;
import top.fjy8018.designpattern.pattern.structural.proxy.IOrderServiceImpl;
import top.fjy8018.designpattern.pattern.structural.proxy.Order;
import top.fjy8018.designpattern.pattern.structural.proxy.db.DataSourceContextHolder;

/**
 * 静态代理实现分库
 *
 * @author F嘉阳
 * @date 2020/2/29 16:20
 */
@Slf4j
public class OrderServiceStaticProxy {

    /**
     * 模拟Spring注入
     */
    private IOrderService orderService = new IOrderServiceImpl();

    private static final String DB = "db";

    /**
     * 对源方法增强
     *
     * @param order
     * @return
     */
    public int save(Order order) {
        beforeMethod();

        // 通过用户ID对2取模分库
        Integer userId = order.getUserId();
        int dbRouter = userId % 2;
        log.info("静态代理分配到【db{}】处理数据", dbRouter);

        // 设置DataSource
        DataSourceContextHolder.setDBType(DB +  String.valueOf(dbRouter));

        afterMethod();

        return orderService.save(order);
    }

    private void beforeMethod() {
        log.info("静态代理before code");
    }

    private void afterMethod() {
        log.info("静态代理after code");
    }
}
```

测试

```java
package top.fjy8018.designpattern.pattern.structural.proxy.staticproxy;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.pattern.structural.proxy.Order;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @author F嘉阳
 * @date 2020/2/29 17:17
 */
@Slf4j
class OrderServiceStaticProxyTest {

    @Test
    void save() {
        Order order1 = new Order();
        order1.setUserId(1);
        Order order2 = new Order();
        order2.setUserId(2);

        OrderServiceStaticProxy proxy = new OrderServiceStaticProxy();
        proxy.save(order1);
        proxy.save(order2);
    }
}
```

输出

```java

17:20:36.012 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.staticproxy.OrderServiceStaticProxy - 静态代理before code
17:20:36.022 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.staticproxy.OrderServiceStaticProxy - 静态代理分配到【db1】处理数据
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.staticproxy.OrderServiceStaticProxy - 静态代理after code
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderServiceImpl - Service层调用DAO层添加订单记录成功
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderDaoImpl - DAO层添加订单记录成功
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.staticproxy.OrderServiceStaticProxy - 静态代理before code
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.staticproxy.OrderServiceStaticProxy - 静态代理分配到【db0】处理数据
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.staticproxy.OrderServiceStaticProxy - 静态代理after code
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderServiceImpl - Service层调用DAO层添加订单记录成功
17:20:36.024 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderDaoImpl - DAO层添加订单记录成功
```



### 代码样例——动态代理

类图

![image-20200303161327080](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200303161327080.png)

动态代理类

```java
package top.fjy8018.designpattern.pattern.structural.proxy.dynamic;

import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.binding.MapperProxy;
import org.springframework.aop.framework.ProxyFactoryBean;
import top.fjy8018.designpattern.pattern.structural.proxy.Order;
import top.fjy8018.designpattern.pattern.structural.proxy.db.DataSourceContextHolder;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/**
 * 动态代理实现分库
 * 动态代理适用场景更加广泛，可以实现通用分库逻辑
 * <p>
 * {@link ProxyFactoryBean#getObject()} 代理工厂类
 * {@link org.springframework.aop.framework.JdkDynamicAopProxy} spring AOP实现，对动态代理封装
 * {@link org.springframework.aop.framework.CglibAopProxy} Cglib 对类进行代理增强
 * {@link org.apache.ibatis.binding.MapperProxyFactory#newInstance(MapperProxy)} 实现mapper代理
 * 实际封装在 {@link MapperProxy#invoke(Object, Method, Object[])}
 * 其获取的方法利用了享元模式 {@link MapperProxy#cachedMapperMethod(Method)}
 *
 * @author F嘉阳
 * @date 2020/3/3 11:00
 */
@Slf4j
public class OrderServiceDynamicProxy implements InvocationHandler {

    private Object target;

    private static final String DB = "db";

    public OrderServiceDynamicProxy(Object target) {
        this.target = target;
    }

    /**
     * 绑定目标对象
     *
     * @return
     */
    public Object bind() {
        Class clazz = target.getClass();
        return Proxy.newProxyInstance(clazz.getClassLoader(), clazz.getInterfaces(), this);
    }

    /**
     * 代理
     *
     * @param proxy  代理对象，一般不调用该参数
     * @param method 要被增强的方法对象
     * @param args   方法参数
     * @return
     * @throws Throwable
     */
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 参数传递
        Object argObject = args[0];
        beforeMethod(argObject);
        // object是要被增强的方法的返回值
        Object object = method.invoke(target, args);
        afterMethod();
        return object;
    }

    /**
     * 前置增强方法
     *
     * @param args 方法参数
     */
    private void beforeMethod(Object args) {
        int userId = 0;
        // 对参数取模
        log.info("动态代理，before code");
        if (args instanceof Order) {
            Order order = (Order) args;
            userId = order.getUserId();
        }
        int dbRouter = userId % 2;
        log.info("动态代理分配到【db{}】处理数据", dbRouter);

        // 设置DataSource
        DataSourceContextHolder.setDBType(DB + dbRouter);
    }

    private void afterMethod() {
        log.info("动态代理after code");
    }
}
```

测试类

```java
package top.fjy8018.designpattern.pattern.structural.proxy.dynamic;

import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import top.fjy8018.designpattern.pattern.structural.proxy.IOrderService;
import top.fjy8018.designpattern.pattern.structural.proxy.IOrderServiceImpl;
import top.fjy8018.designpattern.pattern.structural.proxy.Order;

/**
 * @author F嘉阳
 * @date 2020/3/3 15:54
 */
@Slf4j
class OrderServiceDynamicProxyTest {

    @Test
    void invoke() {
        Order order1 = new Order();
        order1.setUserId(1);
        Order order2 = new Order();
        order2.setUserId(2);

        // 动态代理直接代理接口
        IOrderService proxy = (IOrderService) new OrderServiceDynamicProxy(new IOrderServiceImpl()).bind();
        proxy.save(order1);
        proxy.save(order2);
    }
}
```



输出

```
15:57:57.234 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.dynamic.OrderServiceDynamicProxy - 动态代理，before code
15:57:57.238 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.dynamic.OrderServiceDynamicProxy - 动态代理分配到【db1】处理数据
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderServiceImpl - Service层调用DAO层添加订单记录成功
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderDaoImpl - DAO层添加订单记录成功
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.dynamic.OrderServiceDynamicProxy - 动态代理after code
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.dynamic.OrderServiceDynamicProxy - 动态代理，before code
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.dynamic.OrderServiceDynamicProxy - 动态代理分配到【db0】处理数据
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderServiceImpl - Service层调用DAO层添加订单记录成功
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.IOrderDaoImpl - DAO层添加订单记录成功
15:57:57.248 [main] INFO top.fjy8018.designpattern.pattern.structural.proxy.dynamic.OrderServiceDynamicProxy - 动态代理after code
```



#### 动态代理源码分析

`Proxy`类

```java
package java.lang.reflect;

public class Proxy implements java.io.Serializable {
    // 反射调用开始
	@CallerSensitive
    public static Object newProxyInstance(ClassLoader loader,
                                          Class<?>[] interfaces,
                                          InvocationHandler h)
        throws IllegalArgumentException
    {
        Objects.requireNonNull(h);

        final Class<?>[] intfs = interfaces.clone();
        final SecurityManager sm = System.getSecurityManager();
        if (sm != null) {
            // 合法性检查
            checkProxyAccess(Reflection.getCallerClass(), loader, intfs);
        }

        /*
         * 动态生成代理类
         */
        Class<?> cl = getProxyClass0(loader, intfs);

        /*
         * 实例化并返回新创建的类实例对象
         */
        try {
            if (sm != null) {
                checkNewProxyPermission(Reflection.getCallerClass(), cl);
            }

            final Constructor<?> cons = cl.getConstructor(constructorParams);
            final InvocationHandler ih = h;
            if (!Modifier.isPublic(cl.getModifiers())) {
                AccessController.doPrivileged(new PrivilegedAction<Void>() {
                    public Void run() {
                        cons.setAccessible(true);
                        return null;
                    }
                });
            }
            return cons.newInstance(new Object[]{h});
        } catch (IllegalAccessException|InstantiationException e) {
            throw new InternalError(e.toString(), e);
        } catch (InvocationTargetException e) {
            Throwable t = e.getCause();
            if (t instanceof RuntimeException) {
                throw (RuntimeException) t;
            } else {
                throw new InternalError(t.toString(), t);
            }
        } catch (NoSuchMethodException e) {
            throw new InternalError(e.toString(), e);
        }
    }
    
    private static void checkProxyAccess(Class<?> caller,
                                         ClassLoader loader,
                                         Class<?>... interfaces)
    {
        // 安全校验
        SecurityManager sm = System.getSecurityManager();
        if (sm != null) {
            ClassLoader ccl = caller.getClassLoader();
            if (VM.isSystemDomainLoader(loader) && !VM.isSystemDomainLoader(ccl)) {
                sm.checkPermission(SecurityConstants.GET_CLASSLOADER_PERMISSION);
            }
            ReflectUtil.checkProxyPackageAccess(ccl, interfaces);
        }
    }
    
    // 生成代理类
    private static Class<?> getProxyClass0(ClassLoader loader,
                                           Class<?>... interfaces) {
        // 若一个类中的接口数量超过限制则报错
        if (interfaces.length > 65535) {
            throw new IllegalArgumentException("interface limit exceeded");
        }

        // 从代理类缓存中读取
        return proxyClassCache.get(loader, interfaces);
    }
}
```



从代理类缓存中读取实现

```java
package java.lang.reflect;

final class WeakCache<K, P, V> {
   	public V get(K key, P parameter) {
        Objects.requireNonNull(parameter);

        expungeStaleEntries();

        Object cacheKey = CacheKey.valueOf(key, refQueue);

        // 使用并发包
        ConcurrentMap<Object, Supplier<V>> valuesMap = map.get(cacheKey);
        if (valuesMap == null) {
            ConcurrentMap<Object, Supplier<V>> oldValuesMap
                = map.putIfAbsent(cacheKey,
                                  valuesMap = new ConcurrentHashMap<>());
            if (oldValuesMap != null) {
                valuesMap = oldValuesMap;
            }
        }

        Object subKey = Objects.requireNonNull(subKeyFactory.apply(key, parameter));
        Supplier<V> supplier = valuesMap.get(subKey);
        Factory factory = null;

        while (true) {
            if (supplier != null) {
                // 循环获取，直到获取成功才返回
                V value = supplier.get();
                if (value != null) {
                    return value;
                }
            }
            // 若首次创建则通过工厂类创建对应的类
            if (factory == null) {
                factory = new Factory(key, parameter, subKey, valuesMap);
            }

            if (supplier == null) {
                supplier = valuesMap.putIfAbsent(subKey, factory);
                if (supplier == null) {
                    supplier = factory;
                }
            } else {
                if (valuesMap.replace(subKey, supplier, factory)) {
                    supplier = factory;
                } else {
                    supplier = valuesMap.get(subKey);
                }
            }
        }
    }
}
```

断点查看执行情况

![image-20200303182412370](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200303182412370.png)
