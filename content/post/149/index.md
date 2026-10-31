{
  "title": "MapReduce对网站日志进行分析",
  "date": "2018-04-20T22:58:00+08:00",
  "lastmod": "2023-09-07T14:44:47+08:00",
  "typecho_cid": 149,
  "url": "/archives/149/",
  "comments": false,
  "draft": false,
  "slug": "149",
  "categories": [
    "开发"
  ],
  "tags": [
    "Java",
    "hadoop",
    "MapReduce"
  ],
  "math": true
}

## 代码 ##
[GitHub链接][1]
[开源工具类UserAgentParser地址][2]
## 日志来源 ##
根据之前的作业提交系统项目的后台获取，为了本地测试，故先从数据库中备份下来并做了适当的处理，仅保留UserAgent的相关信息
![请输入图片描述][3]

## 本地文件测试 ##
使用开源工具类解析UserAgent中的信息

    @Test
        public void testReadFile() throws Exception {
            String path = "F:\\JAVA Workspace\\hadoopstudy\\access.log";
            BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(new File(path))));
    
            String line = "";
            int count = 0;
    
            //模拟MapReduce存储
            Map<String, Integer> browerMap = new HashMap<String, Integer>();
    
            UserAgentParser userAgentParser = new UserAgentParser();
    
            while (line != null) {
                line = reader.readLine();
                count++;
                if (StringUtils.isNotBlank(line)) {
                    String source = line;
                    UserAgent agent = userAgentParser.parse(source);
                    //测试
                    String browser = agent.getBrowser();
                    String engine = agent.getEngine();
                    String engineVersion = agent.getEngineVersion();
                    String os = agent.getOs();
                    String platform = agent.getPlatform();
                    boolean mobile = agent.isMobile();
                    Integer browserValue = browerMap.get(browser);
                    
                    if (browserValue != null) {
                        browerMap.put(browser, browerMap.get(browser) + 1);
                    } else {
                        browerMap.put(browser, 1);
                    }
    
                    //输出解析的信息
                    System.out.println(browser + "," + engine + "," + engineVersion + "," + os + "," + platform + "," + mobile);
                }
    
            }
            System.out.println("总记录数：" + count);
            System.out.println("====================================");
            for (Map.Entry<String,Integer>entry :browerMap.entrySet()){
                System.out.println(entry.getKey()+":"+entry.getValue());
            }
        }
执行单元测试
![请输入图片描述][4]

## 使用MapReduce统计 ##
代码以WordCount为原型，结合本地测试的代码编写
    ...
    boolean mobile = agent.isMobile();
    
                if (mobile){
                    mobileuser = "手机用户";
                }else {
                    mobileuser = "非手机用户";
                }
    
                //通过上下文把map的处理结果输出
                context.write(new Text(browser), one);
    ...
### 打包运行 ###
将工程用`mvn assembly:assembly`命令把插件一起打包，上传至虚拟机，同时将log上传至HDFS的根目录
    [hadoop@localhost testFile]$ hadoop fs -put access.log /
    18/04/11 06:12:14 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    [hadoop@localhost testFile]$ hadoop fs -ls /
    18/04/11 06:12:21 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Found 9 items
    -rw-r--r--   1 hadoop supergroup         73 2018-04-11 00:30 /PartitionerTest.txt
    -rw-r--r--   1 hadoop supergroup      26888 2018-04-11 06:12 /access.log
    drwxr-xr-x   - hadoop supergroup          0 2018-04-08 10:56 /hdfsapi
    -rw-r--r--   1 hadoop supergroup         60 2018-04-10 23:03 /hello.txt
    drwxrwx---   - hadoop supergroup          0 2018-04-11 01:28 /history
    drwxr-xr-x   - hadoop supergroup          0 2018-04-11 00:35 /output
    drwxr-xr-x   - hadoop supergroup          0 2018-04-08 10:35 /test
    drwx------   - hadoop supergroup          0 2018-04-11 01:36 /tmp
    drwxr-xr-x   - hadoop supergroup          0 2018-04-09 20:11 /user
运行
![请输入图片描述][5]

![请输入图片描述][6]

结果与本地测试一致
    [hadoop@localhost testFile]$ hadoop fs -ls /logaccess/browserout
    18/04/11 06:15:18 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Found 2 items
    -rw-r--r--   1 hadoop supergroup          0 2018-04-11 06:14 /logaccess/browserout/_SUCCESS
    -rw-r--r--   1 hadoop supergroup         32 2018-04-11 06:14 /logaccess/browserout/part-r-00000
    [hadoop@localhost testFile]$ hadoop fs -text /logaccess/browserout/part-r-00000
    18/04/11 06:15:32 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Chrome  191
    Firefox 10
    Unknown 1
增加其他属性重新运行MapReduce，结果如下
    [hadoop@localhost testFile]$ hadoop fs -ls /logaccess
    18/04/11 06:33:11 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    Found 2 items
    -rw-r--r--   1 hadoop supergroup          0 2018-04-11 06:32 /logaccess/_SUCCESS
    -rw-r--r--   1 hadoop supergroup        192 2018-04-11 06:32 /logaccess/part-r-00000
    [hadoop@localhost testFile]$ hadoop fs -text /logaccess/part-r-00000
    18/04/11 06:33:21 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
    20100101        10
    537.36  191
    604.3.5 1
    Android 48
    Chrome  191
    Firefox 10
    Gecko   10
    Linux   48
    Unknown 1
    Webkit  192
    Windows 296
    Windows 7       10
    iPhone  1
    iPhone OS 11.1  1
    手机用户        49
    非手机用户      153
日志离线统计完成！



  [1]: https://github.com/FJiayang/hadoopstudy
  [2]: https://github.com/LeeKemp/UserAgentParser
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/25OjDr.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/25ObQF.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/25OQyM.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/25Oamt.png
