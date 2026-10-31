{
  "title": "YARN单节点伪分布式搭建",
  "date": "2018-04-09T20:14:00+08:00",
  "lastmod": "2023-09-07T14:48:40+08:00",
  "typecho_cid": 144,
  "url": "/archives/144/",
  "comments": false,
  "draft": false,
  "slug": "144",
  "categories": [
    "默认分类"
  ],
  "tags": [
    "hadoop",
    "YARN"
  ],
  "math": true
}

## 配置YARN ##
首先启动之前配置好的HDFS服务，然后进入`/www/hadoop/hadoop-2.6.0-cdh5.7.0/etc/hadoop`目录，按照官方指导配置YARN单节点环境
![请输入图片描述][1]

使用`cp mapred-site.xml.template mapred-site.xml`命令把`mapred-site.xml.template`复制一份，加入官方的配置
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
![请输入图片描述][2]

同时对`yarn-site.xml`也进行配置
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
![请输入图片描述][3]

## 启动YARN ##
进入`/www/hadoop/hadoop-2.6.0-cdh5.7.0/sbin`目录，使用`./start-yarn.sh`命令启动YARN服务

    [hadoop@localhost sbin]$ ./start-yarn.sh
    starting yarn daemons
    starting resourcemanager, logging to /www/hadoop/hadoop-2.6.0-cdh5.7.0/logs/yarn-hadoop-resourcemanager-localhost.localdomain.out
    localhost: starting nodemanager, logging to /www/hadoop/hadoop-2.6.0-cdh5.7.0/logs/yarn-hadoop-nodemanager-localhost.localdomain.out
用`jps`命令查看是否启动成功，看到如下显示即为启动成功，主要是**NodeManager**和**ResourceManager**两个服务

    [hadoop@localhost sbin]$ jps
    7056 SecondaryNameNode
    7475 NodeManager
    6775 NameNode
    6872 DataNode
    7374 ResourceManager
    7679 Jps
## 开放端口 ##
YARN的浏览器客户端占用8088端口，故使用宝塔面板开放8088端口
![请输入图片描述][4]

## 访问YARN图形化界面 ##
使用浏览器打开`http://ip:8088/`可见如下界面，则YARN启动成功
![请输入图片描述][5]

## 测试 ##
YARN官方提供了示例java程序来测试资源调度，进入`/www/hadoop/hadoop-2.6.0-cdh5.7.0/share/hadoop/mapreduce`目录，可见

    [hadoop@localhost mapreduce]$ ls
    hadoop-mapreduce-client-app-2.6.0-cdh5.7.0.jar              hadoop-mapreduce-client-nativetask-2.6.0-cdh5.7.0.jar
    hadoop-mapreduce-client-common-2.6.0-cdh5.7.0.jar           hadoop-mapreduce-client-shuffle-2.6.0-cdh5.7.0.jar
    hadoop-mapreduce-client-core-2.6.0-cdh5.7.0.jar             hadoop-mapreduce-examples-2.6.0-cdh5.7.0.jar
    hadoop-mapreduce-client-hs-2.6.0-cdh5.7.0.jar               lib
    hadoop-mapreduce-client-hs-plugins-2.6.0-cdh5.7.0.jar       lib-examples
    hadoop-mapreduce-client-jobclient-2.6.0-cdh5.7.0.jar        sources
    hadoop-mapreduce-client-jobclient-2.6.0-cdh5.7.0-tests.jar
其中`hadoop-mapreduce-examples-2.6.0-cdh5.7.0.jar`就是MapReduce的测试程序，通过`hadoop jar`的方式来运行
用命令查看可配置的参数`hadoop jar hadoop-mapreduce-examples-2.6.0-cdh5.7.0.jar`

    [hadoop@localhost mapreduce]$ hadoop jar hadoop-mapreduce-examples-2.6.0-cdh5.7.0.jar
    An example program must be given as the first argument.
    Valid program names are:
      aggregatewordcount: An Aggregate based map/reduce program that counts the words in the input files.
      aggregatewordhist: An Aggregate based map/reduce program that computes the histogram of the words in the input files.
      bbp: A map/reduce program that uses Bailey-Borwein-Plouffe to compute exact digits of Pi.
      dbcount: An example job that count the pageview counts from a database.
      distbbp: A map/reduce program that uses a BBP-type formula to compute exact bits of Pi.
      grep: A map/reduce program that counts the matches of a regex in the input.
      join: A job that effects a join over sorted, equally partitioned datasets
      multifilewc: A job that counts words from several files.
      pentomino: A map/reduce tile laying program to find solutions to pentomino problems.
      pi: A map/reduce program that estimates Pi using a quasi-Monte Carlo method.
      randomtextwriter: A map/reduce program that writes 10GB of random textual data per node.
      randomwriter: A map/reduce program that writes 10GB of random data per node.
      secondarysort: An example defining a secondary sort to the reduce.
      sort: A map/reduce program that sorts the data written by the random writer.
      sudoku: A sudoku solver.
      teragen: Generate data for the terasort
      terasort: Run the terasort
      teravalidate: Checking results of terasort
      wordcount: A map/reduce program that counts the words in the input files.
      wordmean: A map/reduce program that counts the average length of the words in the input files.
      wordmedian: A map/reduce program that counts the median length of the words in the input files.
      wordstandarddeviation: A map/reduce program that counts the standard deviation of the length of the words in the input files.
    [hadoop@localhost mapreduce]$ hadoop jar hadoop-mapreduce-examples-2.6.0-cdh5.7.0.jar pi
    Usage: org.apache.hadoop.examples.QuasiMonteCarlo <nMaps> <nSamples>
    Generic options supported are
    -conf <configuration file>     specify an application configuration file
    -D <property=value>            use value for given property
    -fs <local|namenode:port>      specify a namenode
    -jt <local|resourcemanager:port>    specify a ResourceManager
    -files <comma separated list of files>    specify comma separated files to be copied to the map reduce cluster
    -libjars <comma separated list of jars>    specify comma separated jar files to include in the classpath.
    -archives <comma separated list of archives>    specify comma separated archives to be unarchived on the compute machines.
    
    The general command line syntax is
    bin/hadoop command [genericOptions] [commandOptions]
从上可知测试程序可以做诸如数学π、随机文件写入等操作，这里做数学π的运算
使用命令`hadoop jar hadoop-mapreduce-examples-2.6.0-cdh5.7.0.jar pi 2 3`做两个map计算精度为3的数学π运算,运算结束后会显示结果如下

    Job Finished in 26.996 seconds
    Estimated value of Pi is 4.00000000000000000000
同时浏览器也可看到作业情况
![请输入图片描述][6]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mE8vN.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mEHYc.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mE5lK.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mEqP6.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mEhVT.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2mE3pt.png
