{
  "title": "RocketMQ学习笔记4——消费者核心",
  "date": "2020-12-23T19:11:00+08:00",
  "lastmod": "2023-09-07T15:06:18+08:00",
  "typecho_cid": 254,
  "url": "/archives/254/",
  "comments": false,
  "draft": false,
  "slug": "254",
  "categories": [
    "学习"
  ],
  "tags": [
    "Java",
    "源码学习",
    "RocketMQ"
  ],
  "math": true
}

## 配置参数详解

### PushConsumer核心参数

`ConsumeFromWhere`源码，支持三种参数配置，默认是`CONSUME_FROM_LAST_OFFSET`

```java
package org.apache.rocketmq.common.consumer;

public enum ConsumeFromWhere {
    /**
     * 第一次启动时从队列最后开始消费
     * 下次启动从上次读取的位置开始消费
     */
    CONSUME_FROM_LAST_OFFSET,

    @Deprecated
    CONSUME_FROM_LAST_OFFSET_AND_FROM_MIN_WHEN_BOOT_FIRST,
    @Deprecated
    CONSUME_FROM_MIN_OFFSET,
    @Deprecated
    CONSUME_FROM_MAX_OFFSET,
    /**
     * 从队列最开始消费
     * 下次启动从上次读取的位置开始消费
     */
    CONSUME_FROM_FIRST_OFFSET,
    /**
     * 指定具体时间点开始消费
     * 下次启动从上次读取的位置开始消费
     */
    CONSUME_FROM_TIMESTAMP,
}
```



`AllocateMessageQueueStrategy`接口用于集群模式下消息策略，默认配置为平均消息分配器`AllocateMessageQueueAveragely`

![image-20201212110317224](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212110317224.png)

默认配置源码

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Constructor specifying consumer group and enabled msg trace flag.
     *
     * @param consumerGroup Consumer group.
     * @param enableMsgTrace Switch flag instance for message trace.
     */
    public DefaultMQPushConsumer(final String consumerGroup, boolean enableMsgTrace) {
        this(null, consumerGroup, null, new AllocateMessageQueueAveragely(), enableMsgTrace, null);
    }
}
```



`subscription`订阅参数，传递两个值，一个是主题，一个是表达式tag过滤

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Subscription relationship
     */
    private Map<String /* topic */, String /* sub expression */> subscription = new HashMap<String, String>();
}
```

样例：

```java
consumer.subscribe("test_model_topic2", "TagA||TagB");
```

```java
consumer.subscribe("test_model_topic2", "TagA");
```

```java
consumer.subscribe("test_model_topic2", "*");
```



`offsetStore`配置核心偏移量，有两个实现，用于支持远程存储和本地存储，即支持集群和单机模式

![image-20201212110754861](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212110754861.png)



`consumeThreadMin`与`consumeThreadMax`线程池自动调整参数，默认为20

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Minimum consumer thread number
     */
    private int consumeThreadMin = 20;

    /**
     * Max consumer thread number
     */
    private int consumeThreadMax = 20;
}
```



流控参数`consumeConcurrentlyMaxSpan`与`pullThresholdForQueue`

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Concurrently max span offset.it has no effect on sequential consumption
     * 单个队列并行消费的最大跨度
     */
    private int consumeConcurrentlyMaxSpan = 2000;

    /**
     * Flow control threshold on queue level, each message queue will cache at most 1000 messages by default,
     * Consider the {@code pullBatchSize}, the instantaneous value may exceed the limit
     * 一个队列最大的消息消费个数
     */
    private int pullThresholdForQueue = 1000;
}
```



消息拉取参数`pullInterval`与`pullBatchSize`

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Message pull Interval
     * 消息拉取的时间间隔
     */
    private long pullInterval = 0;

    /**
     * Batch pull size
     * 一次拉取的数据量
     */
    private int pullBatchSize = 32;
}
```



`consumeMessageBatchMaxSize`一次消息最大拉取的数据数量配置

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Batch consumption size
     * 一次消息最大拉取的数据数量
     */
    private int consumeMessageBatchMaxSize = 1;
}
```



`MessageListener`用于消息监听配置，包括并发、顺序读取等

![image-20201212111901572](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212111901572.png)

`MessageModel`配置消息模式，广播或者集群，默认为集群模式

```java
package org.apache.rocketmq.client.consumer;

public class DefaultMQPushConsumer extends ClientConfig implements MQPushConsumer {
    /**
     * Message model defines the way how messages are delivered to each consumer clients.
     * </p>
     *
     * RocketMQ supports two message models: clustering and broadcasting. If clustering is set, consumer clients with
     * the same {@link #consumerGroup} would only consume shards of the messages subscribed, which achieves load
     * balances; Conversely, if the broadcasting is set, each consumer client will consume all subscribed messages
     * separately.
     * </p>
     *
     * This field defaults to clustering.
     */
    private MessageModel messageModel = MessageModel.CLUSTERING;
}
```



## 集群与广播模式

### 集群模式

`MessageModel`源码支持两种模式，集群和广播

```java
package org.apache.rocketmq.common.protocol.heartbeat;

/**
 * Message model
 */
public enum MessageModel {
    /**
     * broadcast
     */
    BROADCASTING("BROADCASTING"),
    /**
     * clustering（默认）
     */
    CLUSTERING("CLUSTERING");

    private String modeCN;

    MessageModel(String modeCN) {
        this.modeCN = modeCN;
    }

    public String getModeCN() {
        return modeCN;
    }
}
```

- 集群模式下GroupName用于把多个Consumer组织到一起，所以同一个集群，GroupName必须相同

- 相同的GroupName的Consumer只消费所订阅消息的一部分，即支持负载均衡

- 优势：集群模式下增加节点能动态增加负载均衡
- 一条消息只会被一个Consumer消费



#### 样例

- 消息消费与奇偶性无关，随机负载均衡，并且负载均衡存在一定的差值，并非100%平分
- 为提高附在均衡度，可以用2个consume监听4个队列，或者3个consume监听6个队列
- Producer只能保证平均分配到各个队列，不能保证被平均的消费

生产者

```java
public class Producer {
	
    public static void main(String[] args) throws MQClientException, InterruptedException {
    	String group_name = "test_model_producer_name";
        DefaultMQProducer producer = new DefaultMQProducer(group_name);
        producer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
        producer.start();
      
        for (int i = 0; i < 10; i++) {
            try {
            	String tag = (i % 2 ==0) ? "TagA":"TagB";
                Message msg = new Message("test_model_topic2",// topic
                		tag,// tag
                    ("信息内容" + i).getBytes()// body
                );
                SendResult sendResult = producer.send(msg);
                System.out.println(sendResult);
            }
            catch (Exception e) {
                e.printStackTrace();
                Thread.sleep(1000);
            }
        }
        
        producer.shutdown();
    }
}
```

消费者1

```java
public class Consumer1 {

	public Consumer1() {
		try {
			String group_name = "test_model_consumer_name";
			DefaultMQPushConsumer consumer = new DefaultMQPushConsumer(group_name);
			consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
			consumer.subscribe("test_model_topic2", "*");
			consumer.setMessageModel(MessageModel.CLUSTERING);
//			consumer.setMessageModel(MessageModel.BROADCASTING);
			consumer.registerMessageListener(new Listener());
			consumer.start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	
	class Listener implements MessageListenerConcurrently {
		public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
			try {
				for(MessageExt msg : msgs){
					String topic = msg.getTopic();
					String msgBody = new String(msg.getBody(),"utf-8");
					String tags = msg.getTags();
					//if(tags.equals("TagA")) {
						System.out.println("收到消息：" + "  topic :" + topic + "  ,tags : " + tags + " ,msg : " + msgBody);
					//}
				}
			} catch (Exception e) {	
				e.printStackTrace();
				return ConsumeConcurrentlyStatus.RECONSUME_LATER;
			}			
			return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
		}
		
	}
	
	public static void main(String[] args) {
		Consumer1 c1 = new Consumer1();
		System.out.println("c1 start..");
		
	}
}
```

消费者2

```java
public class Consumer2 {

	public Consumer2() {
		try {
			String group_name = "test_model_consumer_name";
			DefaultMQPushConsumer consumer = new DefaultMQPushConsumer(group_name);
			consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
			consumer.subscribe("test_model_topic2", "*");
			consumer.setMessageModel(MessageModel.CLUSTERING);
//			consumer.setMessageModel(MessageModel.BROADCASTING);
			consumer.registerMessageListener(new Listener());
			consumer.start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	
	class Listener implements MessageListenerConcurrently {
		public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
			try {
				for(MessageExt msg : msgs){
					String topic = msg.getTopic();
					String msgBody = new String(msg.getBody(),"utf-8");
					String tags = msg.getTags();
					//if(tags.equals("TagB")) {
						System.out.println("收到消息：" + "  topic :" + topic + "  ,tags : " + tags + " ,msg : " + msgBody);
					//}
				}
			} catch (Exception e) {	
				e.printStackTrace();
				return ConsumeConcurrentlyStatus.RECONSUME_LATER;
			}			
			return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
		}
		
	}
	
	public static void main(String[] args) {
		Consumer2 c2 = new Consumer2();
		System.out.println("c2 start..");
		
	}
}
```

发送10条消息结果

![image-20201212153332162](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212153332162.png)

消费者1结果

![image-20201212153337722](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212153337722.png)

消费者2结果

![image-20201212153342986](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212153342986.png)

**注意，若使用集群模式，则tag表达式应该为*号，才能支持多consumer消费，若集群模式下指定tag表达式，则会导致消费结果不确定**，原因如下

1. consumerA监听4条队列中的2条，consumerB监听4条队列中的另外2条。
2. Producer将包含TagA和TagB的消息均分到4条队列中。
3. consumerA消费TagA的消息，那么此时consumerA监听的2条队列中的TagB消息则永远不会被消费

样例

consumer1改成监听`TagA`，其他内容不变

```java
consumer.subscribe("test_model_topic2", "TagA");
```

此时发送10条消息，consumer1监听的结果

![image-20201212160206853](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212160206853.png)

此时将consumer2改成监听`TagB`并启动

```java
consumer.subscribe("test_model_topic2", "TagB");
```

此时发送10条消息，consumer1监听的结果

![image-20201212160312513](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212160312513.png)

consumer2监听结果为空，大量消息丢失

![image-20201212160329310](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212160329310.png)

经过实测发现，只要集群模式下指定了tag，那么只有一个consumer能正常进行消费，其他consumer都为空



### 广播模式

- 同一个ConsumeGroup里的Consumer都消费订阅Topic全部信息
- 也就是一条消息会被每个Consume消费

样例

将consumer1和2改成广播模式，并监听所有tag

```java
consumer.setMessageModel(MessageModel.BROADCASTING);
consumer.subscribe("test_model_topic2", "*");
```

发送10条消息consumer1消费结果

![image-20201212161104586](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212161104586.png)

consumer2消费结果

![image-20201212161110693](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212161110693.png)



**注意广播模式下使用服务端tag过滤仍然有bug**

将consumer1设置为只监听tagA消息

```java
consumer.subscribe("test_model_topic2", "TagA");
```



consumer2设置为只监听tag2消息

```java
consumer.subscribe("test_model_topic2", "TagB");
```

发送10条消息consumer1消费结果

![image-20201212162320622](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212162320622.png)

consumer2消费结果

![image-20201212162328860](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212162328860.png)

结果只有其中一个consumer能正常消费，与集群模式一样的问题

目前（4.4.0）若想要实现同一个topic的tag过滤，则只能让consumer监听所有消息并主动判断

样例：

```java
public class Consumer1 {

	public Consumer1() {
		try {
			String group_name = "test_model_consumer_name";
			DefaultMQPushConsumer consumer = new DefaultMQPushConsumer(group_name);
			consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
			consumer.subscribe("test_model_topic2", "*");
			consumer.setMessageModel(MessageModel.BROADCASTING);
			consumer.registerMessageListener(new Listener());
			consumer.start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	
	class Listener implements MessageListenerConcurrently {
		public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
			try {
				for(MessageExt msg : msgs){
					String topic = msg.getTopic();
					String msgBody = new String(msg.getBody(),"utf-8");
					String tags = msg.getTags();
					if(tags.equals("TagA")) {
						System.out.println("收到消息：" + "  topic :" + topic + "  ,tags : " + tags + " ,msg : " + msgBody);
					}
				}
			} catch (Exception e) {	
				e.printStackTrace();
				return ConsumeConcurrentlyStatus.RECONSUME_LATER;
			}			
			return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
		}
		
	}
	
	public static void main(String[] args) {
		Consumer1 c1 = new Consumer1();
		System.out.println("c1 start..");
	}
}
```



发送10条消息结果

![image-20201212114407769](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212114407769.png)

消费者1结果

![image-20201212114422118](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212114422118.png)

消费者2结果

![image-20201212114435569](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212114435569.png)



对于consumer消费指定队列消息，推荐做法是将消息投递到专属的队列中，由同一个consumer监听，即相当于用groupname+topic唯一定位一个consumer，该方法集群与广播模式均适用

样例

此时consumer1变为`test_model_consumer_name1`

```java
public class Consumer1 {

	public Consumer1() {
		try {
			String group_name = "test_model_consumer_name1";
			DefaultMQPushConsumer consumer = new DefaultMQPushConsumer(group_name);
			consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
			consumer.subscribe("test_model_topic2", "TagA");
//			consumer.setMessageModel(MessageModel.CLUSTERING);
			consumer.setMessageModel(MessageModel.BROADCASTING);
			consumer.registerMessageListener(new Listener());
			consumer.start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	class Listener implements MessageListenerConcurrently {
		public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
			try {
				for(MessageExt msg : msgs){
					String topic = msg.getTopic();
					String msgBody = new String(msg.getBody(),"utf-8");
					String tags = msg.getTags();
					if(tags.equals("TagA")) {
						System.out.println("收到消息：" + "  topic :" + topic + "  ,tags : " + tags + " ,msg : " + msgBody);
					}
				}
			} catch (Exception e) {	
				e.printStackTrace();
				return ConsumeConcurrentlyStatus.RECONSUME_LATER;
			}			
			return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
		}
		
	}
	
	public static void main(String[] args) {
		Consumer1 c1 = new Consumer1();
		System.out.println("c1 start..");
	}
}
```



consumer2变为`test_model_consumer_name2`

```java
public class Consumer2 {

	public Consumer2() {
		try {
			String group_name = "test_model_consumer_name2";
			DefaultMQPushConsumer consumer = new DefaultMQPushConsumer(group_name);
			consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
			consumer.subscribe("test_model_topic2", "TagB");
//			consumer.setMessageModel(MessageModel.CLUSTERING);
			consumer.setMessageModel(MessageModel.BROADCASTING);
			consumer.registerMessageListener(new Listener());
			consumer.start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	class Listener implements MessageListenerConcurrently {
		public ConsumeConcurrentlyStatus consumeMessage(List<MessageExt> msgs, ConsumeConcurrentlyContext context) {
			try {
				for(MessageExt msg : msgs){
					String topic = msg.getTopic();
					String msgBody = new String(msg.getBody(),"utf-8");
					String tags = msg.getTags();
					if(tags.equals("TagB")) {
						System.out.println("收到消息：" + "  topic :" + topic + "  ,tags : " + tags + " ,msg : " + msgBody);
					}
				}
			} catch (Exception e) {	
				e.printStackTrace();
				return ConsumeConcurrentlyStatus.RECONSUME_LATER;
			}			
			return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
		}
		
	}
	
	public static void main(String[] args) {
		Consumer2 c2 = new Consumer2();
		System.out.println("c2 start..");
	}
}
```



发送10条消息结果

![image-20201212163558602](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212163558602.png)

消费者1结果

![image-20201212114422118](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212114422118.png)

消费者2结果

![image-20201212114435569](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20201212114435569.png)



## 消费存储核心-OffSet

- Offset是消费者消费进度的核心
- Offset指某个topic下的一条消息在某个MessageQueue里的位置
- 通过Offset可以进行定位到这条消息
- Offset的存储实现分为远程文件类型和本地文件类型两种



### 集群模式-`RemoteBrokerOffsetStore`

- 默认集群模式clustering，采用远程文件存储Offset
- 本质上因为多消费模式，每个Consumer消费所订阅主题的一部分



### 广播模式-`LocalFileOffsetStore`

- 广播模式下，由于每个Consumer都会收到消息且消费
- 各个Consumer之间没有任何干扰，独立线程消费
- 所以使用LocalFileOffsetStore，也就是把Offset存储到本地



## PushConsumer长轮询模式分析

- `DefaultMQPushConsumer`是使用长轮询模式进行实现的
- 通常主流的消息获取模式：Push消息推送模式与Pull消息拉取模式
- Push模式消耗broker端性能，若消费端消费速度不一致，可能导致消息堆积
- pull模式消耗消费端性能，消费端不知道消息达到时间
- RocketMQ采用长轮询机制（消费端主动获取）



### 长轮询过程

![img](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/9919411-b8b4cfdba4c58e12.png)

1. 客户端发起获取消息请求，假设一次请求超时时间为15s
2. 服务端判断是否有消息，有则直接返回
3. 服务端无消息，则等待5s（阈值），5s后再次检查是否有消息，有则返回，无则继续等待
4. 15s后循环检查结束，若仍然无消息，则返回给客户端



优势：

- 主动权在客户端，当服务端消息堆积，不会全推送到客户端



缺点：

- 连接返回时间较长，占用客户端资源（请求阻塞，等待服务端返回）



### 源码分析

源码实现位置

![1608375938631](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1608375938631.png)



`PullRequestHoldService`继承自`Runnable`接口

![1608376015873](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1608376015873.png)

核心类`PullRequestHoldService`源码全貌

```java
package org.apache.rocketmq.broker.longpolling;

public class PullRequestHoldService extends ServiceThread {
    private static final InternalLogger log = InternalLoggerFactory.getLogger(LoggerName.BROKER_LOGGER_NAME);
    private static final String TOPIC_QUEUEID_SEPARATOR = "@";
    private final BrokerController brokerController;
    private final SystemClock systemClock = new SystemClock();
    private ConcurrentMap<String/* topic@queueId */, ManyPullRequest> pullRequestTable =
        new ConcurrentHashMap<String, ManyPullRequest>(1024);

    public PullRequestHoldService(final BrokerController brokerController) {
        this.brokerController = brokerController;
    }

    public void suspendPullRequest(final String topic, final int queueId, final PullRequest pullRequest) {
        String key = this.buildKey(topic, queueId);
        ManyPullRequest mpr = this.pullRequestTable.get(key);
        if (null == mpr) {
            mpr = new ManyPullRequest();
            ManyPullRequest prev = this.pullRequestTable.putIfAbsent(key, mpr);
            if (prev != null) {
                mpr = prev;
            }
        }

        mpr.addPullRequest(pullRequest);
    }

    private String buildKey(final String topic, final int queueId) {
        StringBuilder sb = new StringBuilder();
        sb.append(topic);
        sb.append(TOPIC_QUEUEID_SEPARATOR);
        sb.append(queueId);
        return sb.toString();
    }

    @Override
    public void run() {
        log.info("{} service started", this.getServiceName());
        while (!this.isStopped()) {
            try {
                // 判断是否启用长轮询
                if (this.brokerController.getBrokerConfig().isLongPollingEnable()) {
                    // 等待5s
                    this.waitForRunning(5 * 1000);
                } else {
                    this.waitForRunning(this.brokerController.getBrokerConfig().getShortPollingTimeMills());
                }

                long beginLockTimestamp = this.systemClock.now();
                // 检查请求
                this.checkHoldRequest();
                long costTime = this.systemClock.now() - beginLockTimestamp;
                if (costTime > 5 * 1000) {
                    log.info("[NOTIFYME] check hold request cost {} ms.", costTime);
                }
            } catch (Throwable e) {
                log.warn(this.getServiceName() + " service has exception. ", e);
            }
        }

        log.info("{} service end", this.getServiceName());
    }

    @Override
    public String getServiceName() {
        return PullRequestHoldService.class.getSimpleName();
    }

    private void checkHoldRequest() {
        // 遍历所有请求的channel
        for (String key : this.pullRequestTable.keySet()) {
            String[] kArray = key.split(TOPIC_QUEUEID_SEPARATOR);
            if (2 == kArray.length) {
                String topic = kArray[0];
                int queueId = Integer.parseInt(kArray[1]);
                final long offset = this.brokerController.getMessageStore().getMaxOffsetInQueue(topic, queueId);
                try {
                    // 唤醒
                    this.notifyMessageArriving(topic, queueId, offset);
                } catch (Throwable e) {
                    log.error("check hold request failed. topic={}, queueId={}", topic, queueId, e);
                }
            }
        }
    }

    public void notifyMessageArriving(final String topic, final int queueId, final long maxOffset) {
        notifyMessageArriving(topic, queueId, maxOffset, null, 0, null, null);
    }

    public void notifyMessageArriving(final String topic, final int queueId, final long maxOffset, final Long tagsCode,
        long msgStoreTime, byte[] filterBitMap, Map<String, String> properties) {
        String key = this.buildKey(topic, queueId);
        // 取出等待的channel（请求）
        ManyPullRequest mpr = this.pullRequestTable.get(key);
        if (mpr != null) {
            List<PullRequest> requestList = mpr.cloneListAndClear();
            if (requestList != null) {
                List<PullRequest> replayList = new ArrayList<PullRequest>();
                // 循环所有的请求
                for (PullRequest request : requestList) {
                    long newestOffset = maxOffset;
                    if (newestOffset <= request.getPullFromThisOffset()) {
                        newestOffset = this.brokerController.getMessageStore().getMaxOffsetInQueue(topic, queueId);
                    }

                    if (newestOffset > request.getPullFromThisOffset()) {
                        boolean match = request.getMessageFilter().isMatchedByConsumeQueue(tagsCode,
                            new ConsumeQueueExt.CqExtUnit(tagsCode, msgStoreTime, filterBitMap));
                        // match by bit map, need eval again when properties is not null.
                        if (match && properties != null) {
                            match = request.getMessageFilter().isMatchedByCommitLog(null, properties);
                        }
                        // 如果匹配上
                        if (match) {
                            try {
                                // 唤醒request
                                this.brokerController.getPullMessageProcessor().executeRequestWhenWakeup(request.getClientChannel(),
                                    request.getRequestCommand());
                            } catch (Throwable e) {
                                log.error("execute request when wakeup failed.", e);
                            }
                            continue;
                        }
                    }

                    if (System.currentTimeMillis() >= (request.getSuspendTimestamp() + request.getTimeoutMillis())) {
                        try {
                            this.brokerController.getPullMessageProcessor().executeRequestWhenWakeup(request.getClientChannel(),
                                request.getRequestCommand());
                        } catch (Throwable e) {
                            log.error("execute request when wakeup failed.", e);
                        }
                        continue;
                    }

                    replayList.add(request);
                }

                if (!replayList.isEmpty()) {
                    mpr.addPullRequest(replayList);
                }
            }
        }
    }
}
```

`ManyPullRequest`里存储的实际为`PullRequest`数组

```java
public class ManyPullRequest {
    private final ArrayList<PullRequest> pullRequestList = new ArrayList<>();
	...
}
```

`PullRequest`实际存储NIO请求

```java
public class PullRequest {
    private final RemotingCommand requestCommand;
    /** NIO channel */
    private final Channel clientChannel;
    private final long timeoutMillis;
    private final long suspendTimestamp;
    private final long pullFromThisOffset;
    private final SubscriptionData subscriptionData;
    private final MessageFilter messageFilter;
	...
}
```



## `DefaultMQPullConsumer`消息拉取模式

- 实现类`DefaultMQPullConsumer`
- 主要逻辑
  - 获取Message Queue并遍历
  - 维护OffsetStore
  - 根据不同消息状态做不同处理

### 生产者样例

```java
public class Producer {
    public static void main(String[] args) throws MQClientException, InterruptedException {
    	
    	String group_name = "test_pull_producer_name";
        DefaultMQProducer producer = new DefaultMQProducer(group_name);
        producer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
        producer.start();
 
        for (int i = 0; i < 10; i++) {
            try {
                Message msg = new Message("test_pull_topic",// topic
                		"TagA",// tag
                		("Hello RocketMQ " + i).getBytes()// body
                );
                // 配置延迟
                msg.setDelayTimeLevel(2);
                
                SendResult sendResult = producer.send(msg, new MessageQueueSelector() {
                    // 外部方法的arg会传递到Object中
                    @Override
                    public MessageQueue select(List<MessageQueue> list, Message message, Object o) {
                        Integer queueNumber = (Integer) o;
                        return list.get(queueNumber);
                    }
                },1);

                SendStatus status = sendResult.getSendStatus();
                System.out.println(status);

                Thread.sleep(1000);
            }
            catch (Exception e) {
                e.printStackTrace();
                Thread.sleep(3000);
            }
        }
        producer.shutdown();
    }
}
```

发送消息后的结果，在队列1有45条消息

![1608436249690](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1608436249690.png)

### 使用普通Pull轮询模式

```java
public class PullConsumer {
	//Map<key, value>  key为指定的队列，value为这个队列拉取数据的最后位置
    private static final Map<MessageQueue, Long> offseTable = new HashMap<MessageQueue, Long>();
 
    public static void main(String[] args) throws MQClientException {
    	
    	String group_name = "test_pull_consumer_name";
        DefaultMQPullConsumer consumer = new DefaultMQPullConsumer(group_name);
        consumer.setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
        consumer.start();
        System.err.println("consumer start");
        //	从TopicTest这个主题去获取所有的队列（默认会有4个队列）
        Set<MessageQueue> mqs = consumer.fetchSubscribeMessageQueues("test_pull_topic");
        //	遍历每一个队列，进行拉取数据
        for (MessageQueue mq : mqs) {
            System.out.println("Consume from the queue: " + mq);
            
            SINGLE_MQ: while (true) {
                try {
                	//	从queue中获取数据，从什么位置开始拉取数据 单次对多拉取32条记录
                    PullResult pullResult = consumer.pullBlockIfNotFound(mq, null, getMessageQueueOffset(mq), 32);
                    System.out.println(pullResult);
                    System.out.println(pullResult.getPullStatus());
                    System.out.println();
                    // 客户端自行维护Offset
                    putMessageQueueOffset(mq, pullResult.getNextBeginOffset());
                    switch (pullResult.getPullStatus()) {
	                    case FOUND:
	                    	List<MessageExt> list = pullResult.getMsgFoundList();
	                    	for(MessageExt msg : list){
	                    		System.out.println(new String(msg.getBody()));
	                    	}
	                        break;
	                    case NO_MATCHED_MSG:
	                        break;
	                    case NO_NEW_MSG:
	                    	System.out.println("没有新的数据啦...");
	                        break SINGLE_MQ;
	                    case OFFSET_ILLEGAL:
	                        break;
	                    default:
	                        break;
                    }
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
        consumer.shutdown();
    }
 
 
    private static void putMessageQueueOffset(MessageQueue mq, long offset) {
        offseTable.put(mq, offset);
    }
 
 
    private static long getMessageQueueOffset(MessageQueue mq) {
        Long offset = offseTable.get(mq);
        if (offset != null)
            return offset;
        return 0;
    }
}
```

消费结果，其会随机选择队列读取，导致服务端积压的消息得不到有效的消费

而且该模式需要客户端编码实现Offset存储

![1608436289786](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1608436289786.png)

### Pull定时任务实现样例

```java
public class PullScheduleService {

    public static void main(String[] args) throws MQClientException {
    	
    	String group_name = "test_pull_consumer_name";
    	// 使用定时任务
        final MQPullConsumerScheduleService scheduleService = new MQPullConsumerScheduleService(group_name);
        
        scheduleService.getDefaultMQPullConsumer().setNamesrvAddr(Const.NAMESRV_ADDR_SINGLE);
        
        scheduleService.setMessageModel(MessageModel.CLUSTERING);
        
        scheduleService.registerPullTaskCallback("test_pull_topic", new PullTaskCallback() {
 
            @Override
            public void doPullTask(MessageQueue mq, PullTaskContext context) {
                MQPullConsumer consumer = context.getPullConsumer();
                System.err.println("-------------- queueId: " + mq.getQueueId()  + "-------------");
                try {
                    // 获取从哪里拉取
                    long offset = consumer.fetchConsumeOffset(mq, false);
                    if (offset < 0)
                        offset = 0;
 
                    PullResult pullResult = consumer.pull(mq, "*", offset, 32);
                    switch (pullResult.getPullStatus()) {
                    case FOUND:
                    	List<MessageExt> list = pullResult.getMsgFoundList();
                    	for(MessageExt msg : list){
                    		//消费数据...
                    		System.out.println(new String(msg.getBody()));
                    	}
                        break;
                    case NO_MATCHED_MSG:
                        break;
                    case NO_NEW_MSG:
                    case OFFSET_ILLEGAL:
                        break;
                    default:
                        break;
                    }
                    // 客户端自动更新Offset，无需本地持久化维护
                    consumer.updateConsumeOffset(mq, pullResult.getNextBeginOffset());
                    // 设置再过3000ms后重新拉取
                    context.setPullNextDelayTimeMillis(3000);
          
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
 
        scheduleService.start();
    }
}
```

运行结果，由于采用多线程读取所有队列，所以当服务端有消息时可以及时获取

![1608436456415](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1608436456415.png)

### 实现原理

- `MQPullConsumerScheduleService`中将`PullTaskCallback`方法作为Map存储
- 并使用`ScheduledThreadPoolExecutor`作为线程池，配置线程数为10
- 线程通过调度`taskTable`中的`PullTaskImpl`任务，实现方法回调

```java
package org.apache.rocketmq.client.consumer;

public class MQPullConsumerScheduleService {
    private final InternalLogger log = ClientLogger.getLog();
    private final MessageQueueListener messageQueueListener = new MessageQueueListenerImpl();
    private final ConcurrentMap<MessageQueue, PullTaskImpl> taskTable =
        new ConcurrentHashMap<MessageQueue, PullTaskImpl>();
    private DefaultMQPullConsumer defaultMQPullConsumer;
    private int pullThreadNums = 20;
    private ConcurrentMap<String /* topic */, PullTaskCallback> callbackTable =
        new ConcurrentHashMap<String, PullTaskCallback>();
    private ScheduledThreadPoolExecutor scheduledThreadPoolExecutor;

    public MQPullConsumerScheduleService(final String consumerGroup) {
        this.defaultMQPullConsumer = new DefaultMQPullConsumer(consumerGroup);
        this.defaultMQPullConsumer.setMessageModel(MessageModel.CLUSTERING);
    }

    public void putTask(String topic, Set<MessageQueue> mqNewSet) {
        Iterator<Entry<MessageQueue, PullTaskImpl>> it = this.taskTable.entrySet().iterator();
        while (it.hasNext()) {
            Entry<MessageQueue, PullTaskImpl> next = it.next();
            if (next.getKey().getTopic().equals(topic)) {
                if (!mqNewSet.contains(next.getKey())) {
                    next.getValue().setCancelled(true);
                    it.remove();
                }
            }
        }

        for (MessageQueue mq : mqNewSet) {
            if (!this.taskTable.containsKey(mq)) {
                // 需要调度的任务
                PullTaskImpl command = new PullTaskImpl(mq);
                this.taskTable.put(mq, command);
                // 使用多线程调度
                this.scheduledThreadPoolExecutor.schedule(command, 0, TimeUnit.MILLISECONDS);

            }
        }
    }

    public void start() throws MQClientException {
        final String group = this.defaultMQPullConsumer.getConsumerGroup();
        this.scheduledThreadPoolExecutor = new ScheduledThreadPoolExecutor(
            this.pullThreadNums,
            new ThreadFactoryImpl("PullMsgThread-" + group)
        );

        this.defaultMQPullConsumer.setMessageQueueListener(this.messageQueueListener);

        this.defaultMQPullConsumer.start();

        log.info("MQPullConsumerScheduleService start OK, {} {}",
            this.defaultMQPullConsumer.getConsumerGroup(), this.callbackTable);
    }

    public void registerPullTaskCallback(final String topic, final PullTaskCallback callback) {
        // 放入回调任务集合
        this.callbackTable.put(topic, callback);
        this.defaultMQPullConsumer.registerMessageQueueListener(topic, null);
    }

    class MessageQueueListenerImpl implements MessageQueueListener {
        @Override
        public void messageQueueChanged(String topic, Set<MessageQueue> mqAll, Set<MessageQueue> mqDivided) {
            MessageModel messageModel =
                MQPullConsumerScheduleService.this.defaultMQPullConsumer.getMessageModel();
            switch (messageModel) {
                case BROADCASTING:
                    MQPullConsumerScheduleService.this.putTask(topic, mqAll);
                    break;
                case CLUSTERING:
                    MQPullConsumerScheduleService.this.putTask(topic, mqDivided);
                    break;
                default:
                    break;
            }
        }
    }

    class PullTaskImpl implements Runnable {
        private final MessageQueue messageQueue;
        private volatile boolean cancelled = false;

        public PullTaskImpl(final MessageQueue messageQueue) {
            this.messageQueue = messageQueue;
        }

        @Override
        public void run() {
            String topic = this.messageQueue.getTopic();
            if (!this.isCancelled()) {
                // 获取回调任务
                PullTaskCallback pullTaskCallback =
                    MQPullConsumerScheduleService.this.callbackTable.get(topic);
                if (pullTaskCallback != null) {
                    final PullTaskContext context = new PullTaskContext();
                    context.setPullConsumer(MQPullConsumerScheduleService.this.defaultMQPullConsumer);
                    try {
                        // 执行客户端实现的回调任务
                        pullTaskCallback.doPullTask(this.messageQueue, context);
                    } catch (Throwable e) {
                        context.setPullNextDelayTimeMillis(1000);
                        log.error("doPullTask Exception", e);
                    }

                    if (!this.isCancelled()) {
                        MQPullConsumerScheduleService.this.scheduledThreadPoolExecutor.schedule(this,
                            context.getPullNextDelayTimeMillis(), TimeUnit.MILLISECONDS);
                    } else {
                        log.warn("The Pull Task is cancelled after doPullTask, {}", messageQueue);
                    }
                } else {
                    log.warn("Pull Task Callback not exist , {}", topic);
                }
            } else {
                log.warn("The Pull Task is cancelled, {}", messageQueue);
            }
        }
    }
}
```
