{
  "title": "RocketMQ学习笔记2——入门",
  "date": "2020-12-23T19:06:00+08:00",
  "lastmod": "2023-09-07T15:06:28+08:00",
  "typecho_cid": 252,
  "url": "/archives/252/",
  "comments": false,
  "draft": false,
  "slug": "252",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "Linux",
    "源码学习",
    "RocketMQ"
  ],
  "math": true
}

## 生产者模型使用

步骤

1. 创建生产者对象DefaultMQProducer
2. 设置NamesrvAddr
3. 启动生产者服务
4. 创建消息并发送



简单消息发送

创建测试主题

![image-20200710104500348](/images/recovered/de256f2e06fc571aaebd.png)



常量定义

```java
public class Const {

	public static final String NAMESRV_ADDR_SINGLE = "10.139.12.52:9876";
}
```



```java
public class Producer {

	public static void main(String[] args) throws MQClientException, RemotingException, MQBrokerException, InterruptedException {
		
		DefaultMQProducer producer = new DefaultMQProducer("test_quick_producer_name");
		
		producer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
		
		producer.start();
		
		for(int i = 0 ; i <5; i ++) {
			//	1.	创建消息
			Message message = new Message("test_quick_topic",	//	主题
					"TagA", //	标签
					"key" + i,	// 	用户自定义的key ,唯一的标识
					("Hello RocketMQ" + i).getBytes());	//	消息内容实体（byte[]）
			SendResult sr = producer.send(message, new MessageQueueSelector() {
				@Override
				public MessageQueue select(List<MessageQueue> mqs, Message msg, Object arg) {
					Integer queueNumber = (Integer)arg;
					return mqs.get(queueNumber);
				}
			}, 2);
			System.err.println(sr);
			System.err.println("消息发出: " + sr);
		}
		producer.shutdown();
	}
}
```



运行结果

```java
SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FA830000, offsetMsgId=0A8B0C3400002A9F0000000000000B5E, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=0]
消息发出: SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FA830000, offsetMsgId=0A8B0C3400002A9F0000000000000B5E, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=0]
SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FA990001, offsetMsgId=0A8B0C3400002A9F0000000000000C20, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=1]
消息发出: SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FA990001, offsetMsgId=0A8B0C3400002A9F0000000000000C20, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=1]
SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FAA10002, offsetMsgId=0A8B0C3400002A9F0000000000000CE2, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=2]
消息发出: SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FAA10002, offsetMsgId=0A8B0C3400002A9F0000000000000CE2, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=2]
SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FAAE0003, offsetMsgId=0A8B0C3400002A9F0000000000000DA4, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=3]
消息发出: SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FAAE0003, offsetMsgId=0A8B0C3400002A9F0000000000000DA4, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=3]
SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FABA0004, offsetMsgId=0A8B0C3400002A9F0000000000000E66, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=4]
消息发出: SendResult [sendStatus=SEND_OK, msgId=BA01D58B19CC18B4AAC230A7FABA0004, offsetMsgId=0A8B0C3400002A9F0000000000000E66, messageQueue=MessageQueue [topic=test_quick_topic, brokerName=broker-a, queueId=2], queueOffset=4]
10:45:15.129 [NettyClientSelector_1] INFO RocketmqRemoting - closeChannel: close the connection to remote address[10.139.12.52:10911] result: true
10:45:15.132 [NettyClientSelector_1] INFO RocketmqRemoting - closeChannel: close the connection to remote address[10.139.12.52:10909] result: true
10:45:15.132 [NettyClientSelector_1] INFO RocketmqRemoting - closeChannel: close the connection to remote address[10.139.12.52:9876] result: true
```



## 消费者模型使用

步骤

1. 创建消费者对象DefaultMQPushConsumer
2. 设置NamesrvAddr及消费位置ConsumeFromWhere
3. 进行主题订阅Subscribe
4. 注册监听并消费registerMessageListener



简单消息消费



```java
public class Consumer {

	public static void main(String[] args) throws MQClientException {
		// 采用Push方式
		DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("test_quick_consumer_name");
		
		consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
		
consumer.setConsumeFromWhere(ConsumeFromWhere.CONSUME_FROM_LAST_OFFSET);
		// 匹配所有Tag
		consumer.subscribe("test_quick_topic", "*");
		
		consumer.registerMessageListener(new MessageListenerConcurrently() {
			
			@Override
			public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
				MessageExt me = msgs.get(0);
				try {
					String topic = me.getTopic();
					String tags = me.getTags();
					String keys = me.getKeys();
					
					String msgBody = new String(me.getBody(), RemotingHelper.DEFAULT_CHARSET);
					System.err.println("topic: " + topic + ",tags: " + tags + ", keys: " + keys + ",body: " + msgBody);
				} catch (Exception e) {
					e.printStackTrace();
                    // 重发时间：messageDelayLevel=1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
					return ConsumeConcurrentlyStatus.RECONSUME_LATER;
				}
				return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
			}
		});
		consumer.start();
		System.err.println("consumer start...");
	}
}
```



模拟异常重试

```java
public class Consumer {

	public static void main(String[] args) throws MQClientException {
		// 采用Push方式
		DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("test_quick_consumer_name");
		
		consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
		
		consumer.setConsumeFromWhere(ConsumeFromWhere.CONSUME_FROM_LAST_OFFSET);
		// 匹配所有Tag
		consumer.subscribe("test_quick_topic", "*");
		
		consumer.registerMessageListener(new MessageListenerConcurrently() {
			
			@Override
			public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
				MessageExt me = msgs.get(0);
				try {
					String topic = me.getTopic();
					String tags = me.getTags();
					String keys = me.getKeys();
					// 模拟异常
					if(keys.equals("key1")) {
						System.err.println("消息消费失败..");
						int a = 1/0;
					}
					
					String msgBody = new String(me.getBody(), RemotingHelper.DEFAULT_CHARSET);
					System.err.println("topic: " + topic + ",tags: " + tags + ", keys: " + keys + ",body: " + msgBody);
				} catch (Exception e) {
					e.printStackTrace();
					// 重发次数
					int recousumeTimes = me.getReconsumeTimes();
					System.err.println("recousumeTimes: " + recousumeTimes);
					// 超过3次不再重发
					if(recousumeTimes == 3) {
						//		记录日志....
						//  	做补偿处理
						return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
					}
					// 重发时间：messageDelayLevel=1s 5s 10s 30s 1m 2m 3m 4m 5m 6m 7m 8m 9m 10m 20m 30m 1h 2h
					return ConsumeConcurrentlyStatus.RECONSUME_LATER;
				}
				return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
			}
		});
		consumer.start();
		System.err.println("consumer start...");
	}
}
```

日志输出

```java
consumer start...
topic: test_quick_topic,tags: TagA, keys: key0,body: Hello RocketMQ0
消息消费失败..
java.lang.ArithmeticException: / by zero
	at com.bfxy.rocketmq.quickstart.Consumer$1.consumeMessage(Consumer.java:40)
	at org.apache.rocketmq.client.impl.consumer.ConsumeMessageConcurrentlyService$ConsumeRequest.run(ConsumeMessageConcurrentlyService.java:417)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:748)
recousumeTimes: 0
topic: test_quick_topic,tags: TagA, keys: key2,body: Hello RocketMQ2
topic: test_quick_topic,tags: TagA, keys: key3,body: Hello RocketMQ3
topic: test_quick_topic,tags: TagA, keys: key4,body: Hello RocketMQ4
消息消费失败..
java.lang.ArithmeticException: / by zero
	at com.bfxy.rocketmq.quickstart.Consumer$1.consumeMessage(Consumer.java:40)
	at org.apache.rocketmq.client.impl.consumer.ConsumeMessageConcurrentlyService$ConsumeRequest.run(ConsumeMessageConcurrentlyService.java:417)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:748)
recousumeTimes: 1
消息消费失败..
java.lang.ArithmeticException: / by zero
	at com.bfxy.rocketmq.quickstart.Consumer$1.consumeMessage(Consumer.java:40)
	at org.apache.rocketmq.client.impl.consumer.ConsumeMessageConcurrentlyService$ConsumeRequest.run(ConsumeMessageConcurrentlyService.java:417)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:748)
recousumeTimes: 2
消息消费失败..
java.lang.ArithmeticException: / by zero
	at com.bfxy.rocketmq.quickstart.Consumer$1.consumeMessage(Consumer.java:40)
	at org.apache.rocketmq.client.impl.consumer.ConsumeMessageConcurrentlyService$ConsumeRequest.run(ConsumeMessageConcurrentlyService.java:417)
	at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
	at java.util.concurrent.FutureTask.run(FutureTask.java:266)
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
	at java.lang.Thread.run(Thread.java:748)
recousumeTimes: 3
```



## 四种集群环境

集群环境拓扑图

![image-20200710111127488](/images/recovered/6b691a8ced02a19be58b.png)

分类

1. 单点模式（不推荐）
2. 主从模式
3. 双主模式（不推荐）
4. 双主双从、多主多从模式



## 主从集群环境构建

优势：

- 主从模式可以保障消息的即时性与可靠性
- 当投递一条消息后关闭主节点，从节点可以继续提供消费者进行消费，但不能接受消息
- 主节点上线后会进行消费进度offset同步



### 基础环境

选择2台服务器进行部署验证

| IP               | IP           |      |
| ---------------- | ------------ | ---- |
| GY11-SyOCM33-101 | 10.139.12.52 | 主   |
| GY11-SyOCM33-201 | 10.139.12.53 | 从   |



53节点按照单点部署时操作好对应目录和日志配置

### 修改主节点配置

52节点修改主节点配置文件`broker-a.properties`如下

修改了`namesrvAddr`

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样
brokerName=broker-a
#0 表示 Master，>0 表示 Slave
brokerId=0
#nameServer 地址，分号分割
namesrvAddr=10.139.12.52:9876;10.139.12.53:9876
#在发送消息时，自动创建服务器不存在的 topic，默认创建的队列数
defaultTopicQueueNums=4
#是否允许 Broker 自动创建 Topic，建议线下开启，线上关闭
autoCreateTopicEnable=true
#是否允许 Broker 自动创建订阅组，建议线下开启，线上关闭
autoCreateSubscriptionGroup=true
#Broker 对外服务的监听端口
listenPort=10911
#删除文件时间点，默认凌晨 4 点
deleteWhen=04
#文件保留时间，默认 48 小时
fileReservedTime=120
#commitLog 每个文件的大小默认 1G
mapedFileSizeCommitLog=1073741824
#ConsumeQueue 每个文件默认存 30W 条，根据业务情况调整
mapedFileSizeConsumeQueue=300000
#destroyMapedFileIntervalForcibly=120000
#redeleteHangedFileInterval=120000
#检测物理文件磁盘空间
diskMaxUsedSpaceRatio=88
#存储路径
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/abort
#限制的消息大小
maxMessageSize=65536

#flushCommitLogLeastPages=4
#flushConsumeQueueLeastPages=2
#flushCommitLogThoroughInterval=10000
#flushConsumeQueueThoroughInterval=60000

#Broker 的角色
#- ASYNC_MASTER 异步复制 Master
#- SYNC_MASTER 同步双写 Master
#- SLAVE
brokerRole=ASYNC_MASTER

#刷盘方式
#- ASYNC_FLUSH 异步刷盘
#- SYNC_FLUSH 同步刷盘
flushDiskType=ASYNC_FLUSH

#checkTransactionMessageEnable=false
#发消息线程池数量
#sendMessageThreadPoolNums=128
#拉消息线程池数量
#pullMessageThreadPoolNums=128
```



### 修改从节点配置

修改从节点配置文件`broker-a-s.properties`如下

拷贝主节点配置后修改`id`和`brokerRole`

```properties
#所属集群名字
brokerClusterName=rocketmq-cluster
#broker 名字，注意此处不同的配置文件填写的不一样
brokerName=broker-a
#0 表示 Master，>0 表示 Slave
brokerId=1
#nameServer 地址，分号分割
namesrvAddr=10.139.12.52:9876;10.139.12.53:9876
#在发送消息时，自动创建服务器不存在的 topic，默认创建的队列数
defaultTopicQueueNums=4
#是否允许 Broker 自动创建 Topic，建议线下开启，线上关闭
autoCreateTopicEnable=true
#是否允许 Broker 自动创建订阅组，建议线下开启，线上关闭
autoCreateSubscriptionGroup=true
#Broker 对外服务的监听端口
listenPort=10911
#删除文件时间点，默认凌晨 4 点
deleteWhen=04
#文件保留时间，默认 48 小时
fileReservedTime=120
#commitLog 每个文件的大小默认 1G
mapedFileSizeCommitLog=1073741824
#ConsumeQueue 每个文件默认存 30W 条，根据业务情况调整
mapedFileSizeConsumeQueue=300000
#destroyMapedFileIntervalForcibly=120000
#redeleteHangedFileInterval=120000
#检测物理文件磁盘空间
diskMaxUsedSpaceRatio=88
#存储路径
storePathRootDir=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store
#commitLog 存储路径
storePathCommitLog=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/commitlog
#消费队列存储路径存储路径
storePathConsumeQueue=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/consumequeue
#消息索引存储路径
storePathIndex=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/index
#checkpoint 文件存储路径
storeCheckpoint=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/checkpoint
#abort 文件存储路径
abortFile=/home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/store/abort
#限制的消息大小
maxMessageSize=65536

#flushCommitLogLeastPages=4
#flushConsumeQueueLeastPages=2
#flushCommitLogThoroughInterval=10000
#flushConsumeQueueThoroughInterval=60000

#Broker 的角色
#- ASYNC_MASTER 异步复制 Master
#- SYNC_MASTER 同步双写 Master
#- SLAVE
brokerRole=SLAVE

#刷盘方式
#- ASYNC_FLUSH 异步刷盘
#- SYNC_FLUSH 同步刷盘
flushDiskType=ASYNC_FLUSH

#checkTransactionMessageEnable=false
#发消息线程池数量
#sendMessageThreadPoolNums=128
#拉消息线程池数量
#pullMessageThreadPoolNums=128
```



主从配置同步到53节点即可

### 启动NameSrv

启动Namesrv（主从节点均执行）

```bash
$ cd /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/bin
$ nohup sh mqnamesrv & 
```



### 启动Broker

主节点启动

```bash
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/conf/2m-2s-async/broker-a.properties >/dev/null 2>&1 &
```



从节点启动

```bash
$ nohup sh mqbroker -c /home/ocmuser/rocketmq-test/rocketmq-all-4.4.0-bin-release/conf/2m-2s-async/broker-a-s.properties >/dev/null 2>&1 &
```



### 启动控制台

修改控制台配置地址参数为

```properties
rocketmq.config.namesrvAddr=10.139.12.52:9876;10.139.12.53:9876
```



![image-20200714110245415](/images/recovered/2805bca5ca13f927ceef.png)

## 数据高可用机制故障演练

投递一条消息

![image-20200714110939305](/images/recovered/8d80823e56420d1e0dc3.png)

关闭主节点，剩余一个slave

![image-20200714111107887](/images/recovered/b4185ba8ad779f81e365.png)

启动消费者，消费正常

![image-20200714111150207](/images/recovered/b1ff4d93bb9d65186b43.png)

![image-20200714111203755](/images/recovered/4ea79bfe56f9aedd03fb.png)

主节点上线，同步消息位点（offset）使消费端不会重复消费

![image-20200714111327726](/images/recovered/e32e700994f863b91d1a.png)
