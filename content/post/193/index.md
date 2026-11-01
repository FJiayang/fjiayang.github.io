{
  "title": "Java8生产环境下性能监控与调优详解笔记",
  "date": "2018-12-09T17:05:00+08:00",
  "lastmod": "2019-12-05T15:34:27+08:00",
  "typecho_cid": 193,
  "url": "/archives/193/",
  "comments": false,
  "draft": false,
  "slug": "193",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java"
  ],
  "math": false
}

[toc]


[官方文档](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/index.html)
## JDK命令行参数 
### 标准化参数，各个jvm版本中不变
#### -参数
-help
-version 
-server
-client

### 非标准化参数，不同jvm版本可能会变化
#### -X参数
-Xint:解释执行
-Xcomp:第一次全部编译成本地代码（首次运行速度慢）
-Xmixed:混合模式（默认），JVM自己决定是否编译成本地代码

```
PS C:\Users\11860> java -version
java version "1.8.0_151"
Java(TM) SE Runtime Environment (build 1.8.0_151-b12)
Java HotSpot(TM) 64-Bit Server VM (build 25.151-b12, mixed mode)
```

#### -XX参数
##### 布尔类型
格式：-XX:[+-]<name>表示启用或禁用
-XX:+UseConcMarkSweepGC 表示启用CMS垃圾回收器
-XX:+UseG1GC 表示启用G1垃圾回收器

##### 值类型
格式：-XX:<name>=<value>表示name属性的值是value
-XX:MaxGCPauseMillis=500 表示GC最大停顿时间为500
-XX:GCTimeRatio=19

##### -Xms -Xmx
-Xms等价于-XX:InitialHeapSize 即初始化堆大小
-Xmx等价于-XX:MaxHeapSize 最大堆大小

## JVM运行时参数
-XX:+PrintFlagsInitial 查看初始值
-XX:+PrintFlagsFinal 查看最终值
-XX:+UnlockDiagnosticVMOptions 解锁诊断参数
-XX:+PrintCommandLineFlags 打印命令行参数

+PrintFlagsFinal
= 即默认值
:= 即用户或JVM修改后的值


```
PS C:\Users\11860> java -XX:+PrintFlagsFinal -version
[Global flags]
    uintx AdaptiveSizeDecrementScaleFactor          = 4                                   {product}
    uintx AdaptiveSizeMajorGCDecayTimeScale         = 10                                  {product}
    uintx AdaptiveSizePausePolicy                   = 0                                   {product}
    uintx AdaptiveSizePolicyCollectionCostMargin    = 50                                  {product}
    uintx InitialCodeCacheSize                      = 2555904                             {pd product}
    uintx InitialHeapSize                          := 268435456                           {product}
    bool UseG1GC                                    = false                                {product}
```

### jps 
专用于查看java进程

```
PS C:\Users\11860> jps
14624 Jps
10248
14168 proxyee-down.exe
2120 RemoteMavenServer
5192 main\proxyee-down-core.jar
```
> jps -l显示全称

```
PS C:\Users\11860> jps -l
10248
14168 proxyee-down-2.54\proxyee-down.exe
1800 sun.tools.jps.Jps
2120 org.jetbrains.idea.maven.server.RemoteMavenServer
5192 /proxyee-down-2.54/main\proxyee-down-core.jar
```
[命令参考地址](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/jps.html#CHDCGECD)

### jinfo
查看正在运行的java程序参数

```
PS C:\Users\11860> jinfo
Usage:
    jinfo [option] <pid>
        (to connect to running process)
    jinfo [option] <executable <core>
        (to connect to a core file)
    jinfo [option] [server_id@]<remote server IP or hostname>
        (to connect to remote debug server)

where <option> is one of:
    -flag <name>         to print the value of the named VM flag
    -flag [+|-]<name>    to enable or disable the named VM flag
    -flag <name>=<value> to set the named VM flag to the given value
    -flags               to print VM flags
    -sysprops            to print Java system properties
    <no option>          to print both of the above
    -h | -help           to print this help message
```
查看最大内存
> jinfo -flag MaxHeapSize 

```
PS C:\Users\11860> jinfo -flag MaxHeapSize 2120
-XX:MaxHeapSize=805306368
```

查看垃圾回收器
> jinfo -flag  UseG1GC

### jstat 
查看jvm统计信息

```
PS C:\Users\11860> jstat -help
Usage: jstat -help|-options
       jstat -<option> [-t] [-h<lines>] <vmid> [<interval> [<count>]]

Definitions:
  <option>      An option reported by the -options option
  <vmid>        Virtual Machine Identifier. A vmid takes the following form:
                     <lvmid>[@<hostname>[:<port>]]
                Where <lvmid> is the local vm identifier for the target
                Java virtual machine, typically a process id; <hostname> is
                the name of the host running the target Java virtual machine;
                and <port> is the port number for the rmiregistry on the
                target host. See the jvmstat documentation for a more complete
                description of the Virtual Machine Identifier.
  <lines>       Number of samples between header lines.
  <interval>    Sampling interval. The following forms are allowed:
                    <n>["ms"|"s"]
                Where <n> is an integer and the suffix specifies the units as
                milliseconds("ms") or seconds("s"). The default units are "ms".
  <count>       Number of samples to take before terminating.
  -J<flag>      Pass <flag> directly to the runtime system.
```
[官方文档](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/jstat.html#BEHHGFAE)

可选参数
> -statOption
> Determines the statistics information the jstat command displays. The following lists the available options. Use the -options general option to display the list of options for a particular platform installation. See Stat Options and Output.
> 
>     class: Displays statistics about the behavior of the class loader.
>     
>     compiler: Displays statistics about the behavior of the Java HotSpot VM Just-in-Time compiler.
>     
>     gc: Displays statistics about the behavior of the garbage collected heap.
>     
>     gccapacity: Displays statistics about the capacities of the generations and their corresponding spaces.
>     
>     gccause: Displays a summary about garbage collection statistics (same as -gcutil), with the cause of the last and current (when applicable) garbage collection events.
>     
>     gcnew: Displays statistics of the behavior of the new generation.
>     
>     gcnewcapacity: Displays statistics about the sizes of the new generations and its corresponding spaces.
>     
>     gcold: Displays statistics about the behavior of the old generation and metaspace statistics.
>     
>     gcoldcapacity: Displays statistics about the sizes of the old generation.
>     
>     gcmetacapacity: Displays statistics about the sizes of the metaspace.
>     
>     gcutil: Displays a summary about garbage collection statistics.
>     
>     printcompilation: Displays Java HotSpot VM compilation method statistics.

#### 类加载 
> -class
> Stat Options and Output
> The following information summarizes the columns that the jstat command outputs for each statOption.
> 
> -class option
>     Class loader statistics.
>     
>     Loaded: Number of classes loaded.
>     
>     Bytes: Number of kBs loaded.
>     
>     Unloaded: Number of classes unloaded.
>     
>     Bytes: Number of Kbytes unloaded.
>     
>     Time: Time spent performing class loading and unloading operations.


```
PS C:\Users\11860> jstat -class 2120
Loaded  Bytes  Unloaded  Bytes     Time
  4271  7387.1       98   137.6       3.28
```


#### 垃圾收集 
-gc 
输出含义
S0C、S1C、S0U、S1U：S0和S1的总用量与使用量
EC、EU：Eden区总量与使用量
OC、OU：Old区总量与使用量
MC、MU：Metaspace区总量与使用量
CCSC、CCSU：压缩类空间总量与使用量
YGC、YGCT：YoungGC的次数与时间
FGC、FGCT：FullGC的次数与时间
GCT：总的GC时间

解释：S0=S1，同一时间只启用s1或s0，S0+S1+Eden=Young，内存堆=Young+Old
默认命令只输出一次
```
PS C:\Users\11860> jstat -gc 2120
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT
35840.0 51712.0  0.0    0.0   158720.0 11900.5   102400.0    9199.6   24192.0 22964.4 2944.0 2550.2      8    0.314   2      0.154    0.468
```
指定输出参数为每隔一秒输出一次，共输出10次

```
PS C:\Users\11860> jstat -gc 5192 1000 10
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT
4352.0 4352.0 2228.1  0.0   34944.0  19156.1   87424.0    75913.1   36864.0 35975.9  0.0    0.0     2338    7.004   8      0.459    7.463
4352.0 4352.0  0.0   2131.3 34944.0   7184.2   87424.0    76050.5   36864.0 35975.9  0.0    0.0     2339    7.006   8      0.459    7.466
4352.0 4352.0  0.0   2131.3 34944.0  31117.2   87424.0    76050.5   36864.0 35975.9  0.0    0.0     2339    7.006   8      0.459    7.466
4352.0 4352.0 2320.3  0.0   34944.0   8482.5   87424.0    76050.5   36864.0 35975.9  0.0    0.0     2340    7.009   8      0.459    7.468
4352.0 4352.0 2320.3  0.0   34944.0  29236.0   87424.0    76050.5   36864.0 35975.9  0.0    0.0     2340    7.009   8      0.459    7.468
4352.0 4352.0  0.0   2058.5 34944.0  11809.7   87424.0    76348.8   36864.0 35975.9  0.0    0.0     2341    7.012   8      0.459    7.471
4352.0 4352.0 2339.3  0.0   34944.0    0.0     87424.0    76348.8   36864.0 35975.9  0.0    0.0     2342    7.015   8      0.459    7.474
4352.0 4352.0 2339.3  0.0   34944.0  11533.3   87424.0    76348.8   36864.0 35975.9  0.0    0.0     2342    7.015   8      0.459    7.474
4352.0 4352.0  0.0   2076.1 34944.0   3826.1   87424.0    76520.6   36864.0 35975.9  0.0    0.0     2343    7.017   8      0.459    7.476
4352.0 4352.0  0.0   2076.1 34944.0  11102.7   87424.0    76520.6   36864.0 35975.9  0.0    0.0     2343    7.017   8      0.459    7.476
```


#### JIT编译
-complier

```
PS C:\Users\11860> jstat -compiler 2120
Compiled Failed Invalid   Time   FailedType FailedMethod
    5234      0       0    16.70          0
```

JVM内存结构
![image](/images/recovered/cb905cf3e364f273d93e.jpg)

## 内存溢出
### 堆区内存溢出

### 非堆区内存溢出

### 导出内存映像文件
当内存溢出时自动导出
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=./

jmap命令手动导出

```
PS C:\Users\11860> jmap -help
Usage:
    jmap [option] <pid>
        (to connect to running process)
    jmap [option] <executable <core>
        (to connect to a core file)
    jmap [option] [server_id@]<remote server IP or hostname>
        (to connect to remote debug server)

where <option> is one of:
    <none>               to print same info as Solaris pmap
    -heap                to print java heap summary
    -histo[:live]        to print histogram of java object heap; if the "live"
                         suboption is specified, only count live objects
    -clstats             to print class loader statistics
    -finalizerinfo       to print information on objects awaiting finalization
    -dump:<dump-options> to dump java heap in hprof binary format
                         dump-options:
                           live         dump only live objects; if not specified,
                                        all objects in the heap are dumped.
                           format=b     binary format
                           file=<file>  dump heap to <file>
                         Example: jmap -dump:live,format=b,file=heap.bin <pid>
    -F                   force. Use with -dump:<dump-options> <pid> or -histo
                         to force a heap dump or histogram when <pid> does not
                         respond. The "live" suboption is not supported
                         in this mode.
    -h | -help           to print this help message
    -J<flag>             to pass <flag> directly to the runtime system
```

手动导出映像文件

```
PS C:\Users\11860> jmap -dump:format=b,file=heap.hprof 11720
Dumping heap to L:\heap.hprof ...
Heap dump file created
```
jmap相关命令

```
PS C:\Users\11860> jmap -heap 11720
Attaching to process ID 11720, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.151-b12

using thread-local object allocation.
Parallel GC with 8 thread(s)

Heap Configuration:
   MinHeapFreeRatio         = 0
   MaxHeapFreeRatio         = 100
   MaxHeapSize              = 33554432 (32.0MB)
   NewSize                  = 11010048 (10.5MB)
   MaxNewSize               = 11010048 (10.5MB)
   OldSize                  = 22544384 (21.5MB)
   NewRatio                 = 2
   SurvivorRatio            = 8
   MetaspaceSize            = 21807104 (20.796875MB)
   CompressedClassSpaceSize = 1073741824 (1024.0MB)
   MaxMetaspaceSize         = 17592186044415 MB
   G1HeapRegionSize         = 0 (0.0MB)

Heap Usage:
PS Young Generation
Eden Space:
   capacity = 7864320 (7.5MB)
   used     = 6748264 (6.435646057128906MB)
   free     = 1116056 (1.0643539428710938MB)
   85.80861409505208% used
From Space:
   capacity = 1572864 (1.5MB)
   used     = 950272 (0.90625MB)
   free     = 622592 (0.59375MB)
   60.416666666666664% used
To Space:
   capacity = 1572864 (1.5MB)
   used     = 0 (0.0MB)
   free     = 1572864 (1.5MB)
   0.0% used
PS Old Generation
   capacity = 22544384 (21.5MB)
   used     = 21187512 (20.20598602294922MB)
   free     = 1356872 (1.2940139770507812MB)
   93.9813303392987% used

16212 interned Strings occupying 2160560 bytes.
```

### MAT分析内存溢出
[工具下载](https://www.eclipse.org/mat/downloads.php)
导入文件显示怀疑内存溢出（Leak suspects）

![image](/images/recovered/b337be0079864cbba13e.png)
选择直方图

![image](/images/recovered/11841225b22bb3e9b544.png)
找到影响最大的项目，右键查看强引用以判断这些占用内存大的对象由谁引用，由此定位内存溢出问题

![image](/images/recovered/d1852dfe000e1830b957.png)

![image](/images/recovered/ed2937ccab73ec722619.png)
选择实体树

![image](/images/recovered/d98dffa6b227ba227d6f.png)
也可看出存在大量对象加载

![image](/images/recovered/8276bf2237796379f644.png)

### jstack
分析线程状态

```
PS C:\Users\11860> jstack
Usage:
    jstack [-l] <pid>
        (to connect to running process)
    jstack -F [-m] [-l] <pid>
        (to connect to a hung process)
    jstack [-m] [-l] <executable> <core>
        (to connect to a core file)
    jstack [-m] [-l] [server_id@]<remote server IP or hostname>
        (to connect to a remote debug server)

Options:
    -F  to force a thread dump. Use when jstack <pid> does not respond (process is hung)
    -m  to print both java and native frames (mixed mode)
    -l  long listing. Prints additional information about locks
    -h or -help to print this help message
```
手动导出

```
jstack 23276 > RemoteMavenServerJstack
```

[线程状态官方文档](https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/tooldescr034.html#sthref31)

[线程状态互相转化]https://mp.weixin.qq.com/s/GsxeFM7QWuR--Kbpb7At2w)

#### jstack定位CPU飙高问题



## tomcat 远程监控
### 开启tomcat远程监控
startup.sh 在最后一行的'start "$@"'前加上'jpda'

catalina.sh 搜索jpda,可看到jpda使用说明
