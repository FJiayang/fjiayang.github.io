{
  "title": "redis多种启动配置方式",
  "date": "2018-12-09T11:19:49+08:00",
  "lastmod": "2018-12-09T11:19:49+08:00",
  "typecho_cid": 187,
  "url": "/archives/187/",
  "comments": false,
  "draft": false,
  "slug": "187",
  "categories": [
    "开发"
  ],
  "tags": [
    "Redis"
  ],
  "math": false
}

## 总览

三种启动方式：

1. 动态参数启动（指定端口号）
2. 配置文件启动（生产环境推荐）
3. 最简单启动

## 官方安装指南

安装前置环境`gcc-c++`

```bash
$ yum install -y gcc-c++
```

[官方下载安装文档](https://redis.io/download)

```bash
$ wget http://download.redis.io/releases/redis-5.0.0.tar.gz
$ tar xzf redis-5.0.0.tar.gz
$ cd redis-5.0.0
$ make MALLOC=libc
$ make install
```

编译后在`src`目录下生成可执行文件

```bash
$ ls | grep redis-
```
```
redis-benchmark ——性能测试
redis-benchmark.c
redis-benchmark.o
redis-check-aof ——aof修复
redis-check-aof.c
redis-check-aof.o
redis-check-rdb ——rdb修复
redis-check-rdb.c
redis-check-rdb.o
redis-cli ——客户端
redis-cli.c
redis-cli.o
redis-sentinel ——集群
redis-server ——服务器
redis-trib.rb
```

## 启动

### 简单启动

```bash
$ redis-server 
2660:C 21 Nov 2018 20:01:10.958 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
2660:C 21 Nov 2018 20:01:10.958 # Redis version=5.0.0, bits=64, commit=00000000, modified=0, pid=2660, just started
2660:C 21 Nov 2018 20:01:10.958 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
2660:M 21 Nov 2018 20:01:10.959 * Increased maximum number of open files to 10032 (it was originally set to 1024).
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis 5.0.0 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                   
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 2660
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |           http://redis.io        
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

2660:M 21 Nov 2018 20:01:10.961 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
2660:M 21 Nov 2018 20:01:10.961 # Server initialized
2660:M 21 Nov 2018 20:01:10.961 # WARNING overcommit_memory is set to 0! Background save may fail under low memory condition. To fix this issue add 'vm.overcommit_memory = 1' to /etc/sysctl.conf and then reboot or run the command 'sysctl vm.overcommit_memory=1' for this to take effect.
2660:M 21 Nov 2018 20:01:10.961 # WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo never > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
2660:M 21 Nov 2018 20:01:10.961 * Ready to accept connections
```

客户端连接测试

```bash
$ redis-cli -h 127.0.0.1 -p 6379
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> set hello world
OK
127.0.0.1:6379> get hello
"world"
```

### 动态参数启动

```bash
$ redis-server --port 6380
```

连接默认端口测试

```bash
$ redis-cli -h 127.0.0.1 -p 6379
Could not connect to Redis at 127.0.0.1:6379: Connection refused
not connected> exit
```
连接新端口测试
```bash
$ redis-cli -h 127.0.0.1 -p 6380
127.0.0.1:6380> ping
PONG
127.0.0.1:6380> exit
```

通过进程查看

```bash
$ ps -ef | grep redis-server |grep -v grep
root       2666   1469  0 20:04 pts/0    00:00:00 redis-server *:6380
```

### 配置文件启动

拷贝默认配置

```bash
$ pwd
/root/redis-5.0.0
$ mkdir config
$ cp redis.conf config/
$ cd config/
$ ls
redis.conf
```
查看默认配置，以下命令用于去除注释和空格
```bash
$ cat redis.conf | grep -v "#" | grep -v "^$" > redis-default.conf
$ cat redis-default.conf 
bind 127.0.0.1
protected-mode yes
port 6379 #端口号
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize no #默认非守护进程启动
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile "" #日志文件名称
databases 16
always-show-logo yes
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./ #工作目录
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
replica-priority 100
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
```
由于默认配置redis为单线程，故一台服务器一般起多个redis实例，配置文件以端口号区分
```bash
$ cp redis-default.conf redis-6379.conf
$ ll
总用量 72
-rw-r--r--. 1 root root    65 11月 21 20:46 redis-6379.conf
-rw-r--r--. 1 root root 62155 11月 21 20:36 redis.conf
-rw-r--r--. 1 root root  1425 11月 21 20:41 redis-default.conf
```
简化配置如下：

```
port 6380
daemonize yes
logfile "6380.log"
dir "/root/tmp/redis"
```

配置文件启动

```bash
 $ redis-server config/redis-6380.conf
```
