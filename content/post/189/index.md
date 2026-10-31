{
  "title": "Scala 学习笔记",
  "date": "2018-12-09T16:59:00+08:00",
  "lastmod": "2019-12-05T15:40:16+08:00",
  "typecho_cid": 189,
  "url": "/archives/189/",
  "comments": false,
  "draft": false,
  "slug": "189",
  "categories": [
    "学习"
  ],
  "tags": [
    "Scala"
  ],
  "math": false
}

## 伴生类与伴生对象
特点
1. 同名的class与同名的object互为伴生类和伴生对象
2. 若object中有名为apply的方法，则通过`类名()`会在类初始化完成后调用object的apply方法
3. 若class有名为apply的方法，则通过`对象()`默认调用class的apply方法

```scala
object A{
    def apply(){
        ...
    }
}
class A{
    def apply(){
        ...
    }
}

val b = A() //此处默认调用object 的apply方法

val c = new A()
c() // 此处调用class 的apply方法

```
**最佳实践：在object的apply方法中new class**

## trait
类似java的接口
用法
```scala
class A extends B with C with D ...
```

## 集合
### List
特点
1. Nil 为不可变的空List
2. List由head和tail组成，head为第一个元素，剩余元素为tail
3. List组装通过`::`实现
```scala
val l1 = 1 :: Nil // 返回包含一个元素的集合List(1)，即把1作为head，Nil作为tail
```
4. List可通过`:_*`转成可变参数
```scala
l1.tail:_*
```

## 模式匹配
特点
1. 类似java中的switch
2. 支持多重过滤
3. 支持内容、类型匹配

## 函数高级操作

### 字符串高级操作

#### 插值

字符串前通过字母s声明，内容通过$接变量名即可

```scala
  val h = "hello"
  val name = "FJY"
  println(h +" "+ name) // hello FJY

  println(s"hello $name") // hello FJY
```

输出结果相同



#### 多行字符串

IDEA创建多行字符串：Shift+’ 按3次即可，创建结果为

```scala
  val b =
    """
      |
    """.stripMargin
```

- 样例

```scala
  val b =
    """
      |多行字符串样例
      |Hello Scala
    """.stripMargin

  println(b)
```

最终结果为原样输出

### 匿名函数

函数可以命名，也可以不命名

定义方式：（参数名：参数类型...）=> 函数体

- 样例1

```scala
    val m = (x:Int) => x+1
    println(m(10)) // 11
```

`(x:Int) => x+1`为匿名函数，等价于`{(x:Int) => x+1}`

匿名函数可传给变量，也可传给函数

- 样例2

```scala
    def plus = (x:Int,y:Int)=> x+y
    println(plus(2,3)) // 5
```



### 柯里化函数

- 样例

```scala
    // 原函数
    def plus1(x:Int,y:Int)= x+y
    println(plus1(2,3))
    
    // 柯里化后
    def plus2(x:Int)(y:Int)= x+y
    println(plus2(2)(3))
```

即将多参数分拆



## 高阶函数

### map
作用：逐个操作集合中的元素
```scala
list.map((x)=>x+1) // 对集合中的每个元素执行+1操作
list.map(_ * 2) // 集合中每个元素*2，_ 为占位符
```
其中`x=>x+1`为匿名函数，只有一个元素参数的函数括号可以省略
### filter
作用：过滤
```scala
list.filter(_ > 2) // 只拿出大于2的元素
```
### reduce
作用：操作两个元素
```scala
list.reduce(_ + _) // 集合中相邻的元素两两相加，即求和
```
#### reduceXX方法
reduceLeft,reduceRight,foldLeft,foldRight方法
```scala
val a = List(1,7,2,9)
val a1 = a.reduceLeft(_ - _)//      ((1-7) - 2) - 9 = -17
val a2 = a.foldLeft(0)(_ - _) //    0-1-7-2-9 = -19
```
对于foldLeft方法还有一种简写，这种写法的本意是让你通过/:来联想一棵树的样子 
对/:操作符来说，初始值是第一个操作元本题中是0，：后是第二个操作元a
```scala
val a3 = (0 /: a)(_ - _) //      等价于a.foldLeft(0)(_ - _
```
- foldRight或:\的变体
```scala
val a4 = a.foldRight(0)(_ - _)//    1-(7-(2-(9-0))) = -13
val a5 = (a :\ 0)(_ - _)   //    等价于a.foldRight(0)(_ - _)
```
### flatten
作用：将多个集合元素转成一个集合元素

### flatMap
作用：将多个集合元素转成一个集合后对每个元素执行操作

- Spark word count

```scala
text_file.flatMap(lambda line : line.split()).map(lambda word:(word,1)).reduceByKey(lambda a, b:a+b)
```

即将文件中的元素拆分，再映射上一个初值，最后两两相加

- 原生scala实现wordcount

```scala
txts.flatMap(_.split(",")).map(x => (x,1)).groupBy(_._1).mapValues(_.size).foreach(println)
```

## 偏函数

含义：被包在花括号内没有match的一组case语句

一般通过match实现方式

```scala
  val names = Array("A","B","C")
  val name = names(Random.nextInt(names.length))
  name match {
    case "A" => "AAAAAAAA"
    case "B" => "BBBBBBBB"
    case _ => "CCCCCCCC"
  }
```

通过偏函数实现

```scala
  // -A 输入参数类型 -B 输出参数类型
  def say:PartialFunction[String,String]={
    case "A" => "AAAAAAAA"
    case "B" => "BBBBBBBB"
    case _ => "CCCCCCCC"
  }
```

能自动进行模式匹配



## 隐式转换

解决问题：为一个已经存在的类添加一个方法

Java实现方式：动态代理

Scala实现方式：隐式转换

注意：该特性为双刃剑，容易使代码难以理解

> Scala 2.10引入了一种叫做隐式类的新特性。隐式类指的是用implicit关键字修饰的类。在对应的作用域内，带有这个关键字的类的主构造函数可用于隐式转换。

- 样例

```scala
object ImplicitApp extends App {

  // 定义隐式转换函数，传入源对象，输出目标对象
  implicit def  man2superman(man: Man):Superman=new Superman(man.name)

  val man = new Man("FJY")
  man.fly()
}

class Man(val name:String){
  def eat(): Unit ={
    printf(s"man[ $name ] eat...")
  }
}

class Superman(val name:String){
  def fly(): Unit ={
    printf(s"superman[ $name ] fly...")
  }
}
```

- 样例2：为Java IO类增加读取文件内容方法

```scala
object RichFileApp extends App {

  // 目的在于为Java IO类增加读取文件内容方法
  implicit def file2RichFile(file: File):RichFile=new RichFile(file)

  val f = new File("tmp/hello.txt")
  println(f.readConent)
}

class RichFile(file:File){
  def readConent={
    Source.fromFile(file.getPath).mkString
  }
}
```

### 隐式参数

隐式参数会自动寻找方法、类内部、伴生类内类型匹配的唯一参数，不推荐使用

- 样例

```scala
object ImplicitParaApp {

  implicit val test = "test"
  def main(args: Array[String]): Unit = {

    // 隐式参数会自动寻找方法、类内部、伴生类内类型匹配的唯一参数
    // 若外部定义了多个隐式参数则报错
    def testPara(implicit name:String): Unit ={
      println(name + "...")
    }

    testPara
  }

}
```

### 隐式类

使用隐式类时，类名必须在当前作用域内可见且无歧义，这一要求与隐式值等其他隐式类型转换方式类似。

```scala
object ImplicitClassApp extends App {

  implicit class Calculator(x:Int){
    def add(a:Int) = a+x
  }
  // 原本整数1不具有add方法，使用隐式类后拥有该方法
  println(1.add(2))

}
```

## 操作外部数据

### scala.io.Source

该对象支持操作文件、网络流等，例如读取文件方法源码支持通过柯里化指定字符集

```scala
  def fromFile(name: String)(implicit codec: Codec): BufferedSource =
    fromFile(new JFile(name))(codec)
```

- 样例——读取文件

```scala
val file = Source.fromFile("tmp/file.txt")(Codec.UTF8)
```



- 样例——逐行读取

```scala
  def readLine(file: BufferedSource): Unit ={
    for (line <- file.getLines()){
      println(line)
    }
  }
```


- 样例——逐个字符读取

```scala
  def readChar(file: BufferedSource): Unit ={
    for (ele <- file){
      print(ele)
    }
  }
```


- 样例——网络读取

```scala
  def readNet(url:String): Unit ={
    val file = Source.fromURL(url)
    for (line <- file.getLines()){
      println(line)
    }
  }
```
