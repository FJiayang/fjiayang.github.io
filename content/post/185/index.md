{
  "title": "Mesos集群安装",
  "date": "2018-10-03T22:10:00+08:00",
  "lastmod": "2018-10-03T22:10:46+08:00",
  "typecho_cid": 185,
  "url": "/archives/185/",
  "comments": false,
  "draft": false,
  "slug": "185",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "docker",
    "mesos",
    "集群"
  ],
  "math": false
}

## 基础环境

4台服务器，一台外部客户机

[![mesos.png](/images/recovered/5298b9d43479be9ff137.png)](/images/recovered/5298b9d43479be9ff137.png)

## 安装指南

官方支持C++源码编译安装和Docker安装

[C++源码编译安装地址](http://mesos.apache.org/downloads/)

[Docker镜像仓库](https://hub.docker.com/u/mesosphere/)

## 停止所有容器命令

```bash
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
```



## 安装

### mesos主节点

- node1

  ```bash
  docker pull mesosphere/mesos-master:1.7.0
  ```


- node2(host)

  ```bash
  docker run --name mesos-zookeeper -p 2181:2181 --restart always -d zookeeper:3.5
  ```


node1执行脚本(需替换zk IP地址)

`MESOS_QUORUM=1`即1为单机运行，3个节点为2，计算方式为 `n÷2+1 \`

若不手动指定`hostname`映射的IP，则所有节点默认通过主机名进行通信

- 使用host通信脚本

  ```bash
  docker run -d --net=host \
    -e MESOS_PORT=5050 \
    -e MESOS_ZK=zk://192.168.0.32:2181/mesos \
    -e MESOS_QUORUM=1 \
    -e MESOS_REGISTRY=in_memory \
    -e MESOS_LOG_DIR=/var/log/mesos \
    -e MESOS_WORK_DIR=/var/tmp/mesos \
    -v "$(pwd)/log/mesos:/var/log/mesos" \
    -v "$(pwd)/work/mesos:/var/tmp/mesos" \
    -p 5050:5050 \
    --name=mesos-master \
    mesosphere/mesos-master:1.7.0 \
  ```


- 使用IP通信脚本

  ```bash
  docker run -d --net=host \
    --hostname=192.168.0.32 \
    -e MESOS_PORT=5050 \
    -e MESOS_ZK=zk://192.168.0.32:2181/mesos \
    -e MESOS_QUORUM=1 \
    -e MESOS_REGISTRY=in_memory \
    -e MESOS_LOG_DIR=/var/log/mesos \
    -e MESOS_WORK_DIR=/var/tmp/mesos \
    -v "$(pwd)/log/mesos:/var/log/mesos" \
    -v "$(pwd)/work/mesos:/var/tmp/mesos" \
    -p 5050:5050 \
    --name=mesos-master \
    mesosphere/mesos-master:1.7.0 \
    --no-hostname_lookup \
    --ip=192.168.0.33
  ```


查看日志

```bash
docker logs mesos-master
```



成功输出日志

```bash
I1003 08:41:29.868827    14 group.cpp:341] Group process (zookeeper-group(2)@192.168.0.33:5050) connected to ZooKeeper
I1003 08:41:29.868902    14 group.cpp:831] Syncing group operations: queue size (joins, cancels, datas) = (0, 0, 0)
I1003 08:41:29.868921    14 group.cpp:419] Trying to create path '/mesos' in ZooKeeper
I1003 08:41:29.902194    14 contender.cpp:268] New candidate (id='1') has entered the contest for leadership
I1003 08:41:29.904409     8 detector.cpp:152] Detected a new leader: (id='1')
I1003 08:41:29.904513     8 group.cpp:700] Trying to get '/mesos/json.info_0000000001' in ZooKeeper
I1003 08:41:29.912968     8 zookeeper.cpp:262] A new leading master (UPID=master@192.168.0.33:5050) is detected
I1003 08:41:29.913091     8 master.cpp:2113] Elected as the leading master!
I1003 08:41:29.913115     8 master.cpp:1668] Recovering from registrar
I1003 08:41:29.916913    11 registrar.cpp:383] Successfully fetched the registry (0B) in 3.734016ms
I1003 08:41:29.917054    11 registrar.cpp:487] Applied 1 operations in 26us; attempting to update the registry
I1003 08:41:29.918582    11 registrar.cpp:544] Successfully updated the registry in 1.449984ms
I1003 08:41:29.918630    11 registrar.cpp:416] Successfully recovered registrar
I1003 08:41:29.918772     8 master.cpp:1782] Recovered 0 agents from the registry (121B); allowing 10mins for agents to reregister
```



访问IP:5050，对于PWD，可以访问`http://SSHIP-5050.direct.labs.play-with-docker.com/#/`，将SSH ip替换成实际提供的IP即可

[![mesos-master1.png](/images/recovered/4382c1e966af6ddb4ea6.png)](/images/recovered/4382c1e966af6ddb4ea6.png)

### mesos从节点

- node3 (slave-1)、node4(slave-2)

  启动脚本

  - 使用host通信脚本

    ```bash
    mkdir /cgroup
    docker run -d --net=host --privileged \
      -e MESOS_PORT=5051 \
      -e MESOS_MASTER=zk://192.168.0.32:2181/mesos \
      -e MESOS_SWITCH_USER=0 \
      -e MESOS_CONTAINERIZERS=docker,mesos \
      -e MESOS_LOG_DIR=/var/log/mesos \
      -e MESOS_WORK_DIR=/var/tmp/mesos \
      -v "$(pwd)/log/mesos:/var/log/mesos" \
      -v "$(pwd)/tmp/mesos:/var/tmp/mesos" \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v /cgroup:/cgroup \
      -v /sys:/sys \
      -v "$(which docker):/usr/local/bin/docker" \
      --name=mesos-slave \
      -p 5051:5051 \
      mesosphere/mesos-slave:1.7.0 \
      --no-systemd_enable_support
    ```




  - 使用IP通信脚本，`--ip`需要改成实际IP

    ```bash
    mkdir /cgroup
    docker run -d --net=host --privileged \
      -e MESOS_PORT=5051 \
      -e MESOS_MASTER=zk://192.168.0.32:2181/mesos \
      -e MESOS_SWITCH_USER=0 \
      -e MESOS_CONTAINERIZERS=docker,mesos \
      -e MESOS_LOG_DIR=/var/log/mesos \
      -e MESOS_WORK_DIR=/var/tmp/mesos \
      -v "$(pwd)/log/mesos:/var/log/mesos" \
      -v "$(pwd)/tmp/mesos:/var/tmp/mesos" \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v /cgroup:/cgroup \
      -v /sys:/sys \
      -v "$(which docker):/usr/local/bin/docker" \
      --name=mesos-slave \
      -p 5051:5051 \
      mesosphere/mesos-slave:1.7.0 \
      --no-systemd_enable_support \
      --no-hostname_lookup \
      --ip=192.168.0.31
    ```


  查看日志

  ```bash
  docker logs mesos-slave
  ```



  启动成功日志

  ```bash
  I1003 09:05:08.615039    12 group.cpp:341] Group process (zookeeper-group(1)@192.168.0.31:5051) connected to ZooKeeper
  I1003 09:05:08.615104    12 group.cpp:831] Syncing group operations: queue size (joins, cancels, datas) = (0, 0, 0)
  I1003 09:05:08.615121    12 group.cpp:419] Trying to create path '/mesos' in ZooKeeper
  I1003 09:05:08.618291    13 state.cpp:66] Recovering state from '/var/tmp/mesos/meta'
  I1003 09:05:08.618405    15 slave.cpp:6930] Finished recovering checkpointed state from '/var/tmp/mesos/meta', beginning agent recovery
  I1003 09:05:08.618475     8 task_status_update_manager.cpp:207] Recovering task status update manager
  I1003 09:05:08.618628     8 docker.cpp:908] Recovering Docker containers
  I1003 09:05:08.626359    13 detector.cpp:152] Detected a new leader: (id='3')
  I1003 09:05:08.626487    15 group.cpp:700] Trying to get '/mesos/json.info_0000000003' in ZooKeeper
  I1003 09:05:08.628664    15 zookeeper.cpp:262] A new leading master (UPID=master@192.168.0.33:5050) is detected
  I1003 09:05:08.997036    15 docker.cpp:921] Got the list of Docker containers
  I1003 09:05:08.997324    15 docker.cpp:1157] Finished processing orphaned Docker containers
  I1003 09:05:08.997436     8 slave.cpp:7159] Recovering executors
  I1003 09:05:08.997553     8 slave.cpp:7312] Finished recovery
  I1003 09:05:08.998044    11 task_status_update_manager.cpp:181] Pausing sending task status updates
  I1003 09:05:08.998045     8 slave.cpp:1275] New master detected at master@192.168.0.33:5050
  I1003 09:05:08.998159     8 slave.cpp:1329] No credentials provided. Attempting to register without authentication
  I1003 09:05:08.998181     8 slave.cpp:1340] Detecting new master
  I1003 09:05:09.446756    11 slave.cpp:1500] Registered with master master@192.168.0.33:5050; given agent ID b597695d-6e37-418a-9879-4ffe46117e17-S0
  I1003 09:05:09.449091    10 task_status_update_manager.cpp:188] Resuming sending task status updates
  ```



  访问主节点web界面可看见资源邀约有效

[![mesos-master2.png](/images/recovered/faf68189c029cce1e2d0.png)](/images/recovered/faf68189c029cce1e2d0.png)



节点情况

[![mesos-master3.png](/images/recovered/71f6aded9492c4f330d9.png)](/images/recovered/71f6aded9492c4f330d9.png)



### marathon安装

- node5

启动脚本

```bash
docker run -d --net=host \
  -p 8080:8080 \
  mesosphere/marathon:latest \
  --master zk://192.168.0.32:2181/mesos \
  --zk zk://192.168.0.32:2181/marathon
```

通过IP:8080查看运行结果

[![marathon1.png](/images/recovered/128ce0fe619a71f0e065.png)](/images/recovered/128ce0fe619a71f0e065.png)



### marathon-lb安装

- node6

  启动脚本

  ```bash
  docker run -d -e PORTS=9090 --net=host \
    -p 9090:9090 \
    mesosphere/marathon-lb sse \
    --group external \
    --marathon http://192.168.0.29:8080
  ```

  访问`IP:9090/haproxy?stats`可查看启动状态

[![marathon-lb1.png](/images/recovered/8aa580752352d8e3d28d.png)](/images/recovered/8aa580752352d8e3d28d.png)
