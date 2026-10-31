{
  "title": "Hadoop伪分布式的一些坑",
  "date": "2018-04-08T11:10:00+08:00",
  "lastmod": "2023-09-07T14:49:14+08:00",
  "typecho_cid": 143,
  "url": "/archives/143/",
  "comments": false,
  "draft": false,
  "slug": "143",
  "categories": [
    "默认分类"
  ],
  "tags": [],
  "math": true
}

## 无法创建、上传文件 ##
### 问题描述 ###
当前hdfs文件结构如下，现通过JavaAPI远程创建目录和文件
![请输入图片描述][1]

创建目录
![请输入图片描述][2]

执行单元测试成功
![请输入图片描述][3]

通过API写文件
![请输入图片描述][4]

发现迟迟没有完成（可能有问题了，因为是虚拟机，延迟不应这么大）
![请输入图片描述][5]

测试不通过
![请输入图片描述][6]

报错为
    org.apache.hadoop.ipc.RemoteException(java.io.IOException): File /hdfsapi/test/api.txt could only be replicated to 0 nodes instead of minReplication (=1).  There are 1 datanode(s) running and 1 node(s) are excluded in this operation.
    	at org.apache.hadoop.hdfs.server.blockmanagement.BlockManager.chooseTarget4NewBlock(BlockManager.java:1595)
    	at org.apache.hadoop.hdfs.server.namenode.FSNamesystem.getAdditionalBlock(FSNamesystem.java:3287)
    	at org.apache.hadoop.hdfs.server.namenode.NameNodeRpcServer.addBlock(NameNodeRpcServer.java:677)
    	at org.apache.hadoop.hdfs.server.namenode.AuthorizationProviderProxyClientProtocol.addBlock(AuthorizationProviderProxyClientProtocol.java:213)
    	at org.apache.hadoop.hdfs.protocolPB.ClientNamenodeProtocolServerSideTranslatorPB.addBlock(ClientNamenodeProtocolServerSideTranslatorPB.java:485)
    	at org.apache.hadoop.hdfs.protocol.proto.ClientNamenodeProtocolProtos$ClientNamenodeProtocol$2.callBlockingMethod(ClientNamenodeProtocolProtos.java)
    	at org.apache.hadoop.ipc.ProtobufRpcEngine$Server$ProtoBufRpcInvoker.call(ProtobufRpcEngine.java:617)
    	at org.apache.hadoop.ipc.RPC$Server.call(RPC.java:1073)
    	at org.apache.hadoop.ipc.Server$Handler$1.run(Server.java:2086)
    	at org.apache.hadoop.ipc.Server$Handler$1.run(Server.java:2082)
    	at java.security.AccessController.doPrivileged(Native Method)
    	at javax.security.auth.Subject.doAs(Subject.java:422)
    	at org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1693)
    	at org.apache.hadoop.ipc.Server$Handler.run(Server.java:2080)
    
    
    	at org.apache.hadoop.ipc.Client.call(Client.java:1471)
    	at org.apache.hadoop.ipc.Client.call(Client.java:1408)
    	at org.apache.hadoop.ipc.ProtobufRpcEngine$Invoker.invoke(ProtobufRpcEngine.java:230)
    	at com.sun.proxy.$Proxy12.addBlock(Unknown Source)
    	at org.apache.hadoop.hdfs.protocolPB.ClientNamenodeProtocolTranslatorPB.addBlock(ClientNamenodeProtocolTranslatorPB.java:404)
    	at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    	at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
    	at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
    	at java.lang.reflect.Method.invoke(Method.java:498)
    	at org.apache.hadoop.io.retry.RetryInvocationHandler.invokeMethod(RetryInvocationHandler.java:256)
    	at org.apache.hadoop.io.retry.RetryInvocationHandler.invoke(RetryInvocationHandler.java:104)
    	at com.sun.proxy.$Proxy13.addBlock(Unknown Source)
    	at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.locateFollowingBlock(DFSOutputStream.java:1704)
    	at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.nextBlockOutputStream(DFSOutputStream.java:1500)
    	at org.apache.hadoop.hdfs.DFSOutputStream$DataStreamer.run(DFSOutputStream.java:668)
    
    
    Process finished with exit code -1
查看文件目录，发现有该文件，但大小为0，显然是文件流无法写入
![请输入图片描述][7]


### 解决方法 ###
经过爬贴寻找，发现是因为没有开放端口导致文件流无法写入，经过查找，发现Hadoop相关的端口很多，为了便于学习，直接关闭虚拟机防火墙即可，CentOS7 的命令为`sudo systemctl stop firewalld.service`

关闭防火墙后重新测试，测试通过
![请输入图片描述][8]

再次查看文件系统，发现文件大小已经不为0，说明文件内容已写入，用`hadoop fs -cat /hdfsapi/test/api.txt`查看文件内容，发现内容一致，问题解决
![请输入图片描述][9]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSnyX.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSemG.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSIXg.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cS658.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSVDi.png
  [6]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSZTw.png
  [7]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSkiL.png
  [8]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cStqW.png
  [9]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2cSftR.png
