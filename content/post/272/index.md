{
  "title": "Kubesphere安装——以GCP为例",
  "date": "2021-06-19T22:15:00+08:00",
  "lastmod": "2024-08-04T19:35:38+08:00",
  "typecho_cid": 272,
  "url": "/archives/272/",
  "comments": false,
  "draft": false,
  "slug": "272",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "Linux",
    "kubesphere"
  ],
  "math": true
}

## 平台准备

创建工作空间

![1623574207829](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574207829.png)

启用计算引擎API

![1623574277108](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574277108.png)



## 准备虚拟机

作为演示环境，此处使用Google Cloud Platform创建3台虚拟机，配置如下

| CPU  | 内存 | 磁盘 |
| ---- | ---- | ---- |
| 4    | 16G  | 40G  |
| 4    | 16G  | 40G  |
| 4    | 16G  | 40G  |

### 创建实例模板

创建需要的实例模板

![1623574362360](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574362360.png)

配置操作系统、资源等，注意放行防火墙

![1623574465544](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574465544.png)



### 创建实例

基于实例模板创建3台虚拟机，选择地区为香港

![1623574509743](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574509743.png)

此处用于演示用途，可选择无状态机器，机器删除后不会保留磁盘内容

注意关闭自动扩缩容

![1623574573744](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574573744.png)

![1623575054375](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623575054375.png)

等待实例创建

![1623575697993](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623575697993.png)

由于资源调度问题，最终只成功分配两台虚拟机，不过对于演示环境安装过程一样。

### 配置连接秘钥

![1623574639897](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574639897.png)



添加本地生成好的rsa秘钥即可

![1623574692495](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623574692495.png)

本地SSH工具配置私钥即可连接

![1623575916094](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623575916094.png)

![1623575936073](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623575936073.png)



## 前置环境准备

### kubesphere建议前置项

> ### 节点要求
>
> - 所有节点必须都能通过 `SSH` 访问。
> - 所有节点时间同步。
> - 所有节点都应使用 `sudo`/`curl`/`openssl`。
>
> ### 依赖项要求
>
> KubeKey 可以一同安装 Kubernetes 和 KubeSphere。根据要安装的 Kubernetes 版本，需要安装的依赖项可能会不同。您可以参考下表，查看是否需要提前在节点上安装相关依赖项。
>
> | 依赖项      | Kubernetes 版本 ≥ 1.18 | Kubernetes 版本 < 1.18 |
> | :---------- | :--------------------- | :--------------------- |
> | `socat`     | 必须                   | 可选，但建议安装       |
> | `conntrack` | 必须                   | 可选，但建议安装       |
> | `ebtables`  | 可选，但建议安装       | 可选，但建议安装       |
> | `ipset`     | 可选，但建议安装       | 可选，但建议安装       |

以下内容所有节点都需要执行

```shell
$ yum install -y socat curl openssl conntrack ebtables ipset
```



主节点下载kubekey，由于使用google虚拟机，能正常访问google和github，故直接下载即可

```shell
$ curl -sfL https://get-kk.kubesphere.io | VERSION=v1.1.0 sh -
$ chmod +x kk
```



放行VPC防火墙

![1623579543782](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623579543782.png)

## 创建集群

### 服务器免密登陆

主节点生成免密登陆配置

```shell
$ ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa):
Created directory '/root/.ssh'.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:yxln4RFEXhsvIMcL0/EzF8CLUpo/hMlkM8KBDcNEjbU root@kubesphere-instance-group-1-bx5d
The key's randomart image is:
+---[RSA 2048]----+
|   +=Oo..=Bo+..  |
|    +.=.B++=.+ . |
|      E= @+o*.o  |
|        B.+o.=   |
|        S++      |
|       . *o      |
|        +  .     |
|                 |
|                 |
+----[SHA256]-----+
```

所有主机允许公钥免密登陆

```shell
$ vi /etc/ssh/sshd_config
# 将下面配置改为yes并去掉注释
PubkeyAuthentication yes
PermitRootLogin yes

$ service sshd restart
```



控制台添加主节点公钥，则所有新建主机都能被主节点访问

![1623576902639](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623576902639.png)



### 创建示例配置文件

```shell
$./kk create config --with-kubernetes v1.20.4 --with-kubesphere v3.1.0 -f gcp-config
```



按默认配置只安装控制台和基础服务

```yaml
apiVersion: kubekey.kubesphere.io/v1alpha1
kind: Cluster
metadata:
  name: sample
spec:
  hosts:
  - {name: node1, address: 34.92.90.181, internalAddress: 10.170.0.5, privateKeyPath: "/root/.ssh/id_rsa"}
  - {name: node2, address: 35.220.138.230, internalAddress: 10.170.0.6, privateKeyPath: "/root/.ssh/id_rsa"}
  roleGroups:
    etcd:
    - node1
    master: 
    - node1
    worker:
    - node1
    - node2
  controlPlaneEndpoint:
    domain: lb.kubesphere.local
    address: ""
    port: 6443
  kubernetes:
    version: v1.20.4
    imageRepo: kubesphere
    clusterName: cluster.local
  network:
    plugin: calico
    kubePodsCIDR: 10.233.64.0/18
    kubeServiceCIDR: 10.233.0.0/18
  registry:
    registryMirrors: []
    insecureRegistries: []
  addons: []


---
apiVersion: installer.kubesphere.io/v1alpha1
kind: ClusterConfiguration
metadata:
  name: ks-installer
  namespace: kubesphere-system
  labels:
    version: v3.1.0
spec:
  persistence:
    storageClass: ""       
  authentication:
    jwtSecret: ""
  zone: ""
  local_registry: ""        
  etcd:
    monitoring: false      
    endpointIps: localhost  
    port: 2379             
    tlsEnable: true
  common:
    redis:
      enabled: false
    redisVolumSize: 2Gi 
    openldap:
      enabled: false
    openldapVolumeSize: 2Gi  
    minioVolumeSize: 20Gi
    monitoring:
      endpoint: http://prometheus-operated.kubesphere-monitoring-system.svc:9090
    es:  
      elasticsearchMasterVolumeSize: 4Gi   
      elasticsearchDataVolumeSize: 20Gi   
      logMaxAge: 7          
      elkPrefix: logstash
      basicAuth:
        enabled: false
        username: ""
        password: ""
      externalElasticsearchUrl: ""
      externalElasticsearchPort: ""  
  console:
    enableMultiLogin: true 
    port: 30880
  alerting:       
    enabled: false
    # thanosruler:
    #   replicas: 1
    #   resources: {}
  auditing:    
    enabled: false
  devops:           
    enabled: false
    jenkinsMemoryLim: 2Gi     
    jenkinsMemoryReq: 1500Mi 
    jenkinsVolumeSize: 8Gi   
    jenkinsJavaOpts_Xms: 512m  
    jenkinsJavaOpts_Xmx: 512m
    jenkinsJavaOpts_MaxRAM: 2g
  events:          
    enabled: false
    ruler:
      enabled: true
      replicas: 2
  logging:         
    enabled: false
    logsidecar:
      enabled: true
      replicas: 2
  metrics_server:             
    enabled: false
  monitoring:
    storageClass: ""
    prometheusMemoryRequest: 400Mi  
    prometheusVolumeSize: 20Gi  
  multicluster:
    clusterRole: none 
  network:
    networkpolicy:
      enabled: false
    ippool:
      type: none
    topology:
      type: none
  notification:   
    enabled: false
  openpitrix:
    store:
      enabled: false
  servicemesh:    
    enabled: false  
  kubeedge:
    enabled: false
    cloudCore:
      nodeSelector: {"node-role.kubernetes.io/worker": ""}
      tolerations: []
      cloudhubPort: "10000"
      cloudhubQuicPort: "10001"
      cloudhubHttpsPort: "10002"
      cloudstreamPort: "10003"
      tunnelPort: "10004"
      cloudHub:
        advertiseAddress: 
          - ""           
        nodeLimit: "100"
      service:
        cloudhubNodePort: "30000"
        cloudhubQuicNodePort: "30001"
        cloudhubHttpsNodePort: "30002"
        cloudstreamNodePort: "30003"
        tunnelNodePort: "30004"
    edgeWatcher:
      nodeSelector: {"node-role.kubernetes.io/worker": ""}
      tolerations: []
      edgeWatcherAgent:
        nodeSelector: {"node-role.kubernetes.io/worker": ""}
        tolerations: []
```



### 安装集群

![1623578613894](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623578613894.png)



此时，在虚拟机安装代理即可查看虚拟机监控

![1623579284817](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623579284817.png)



创建完成

![1623579607890](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623579607890.png)



访问成功

![1623579584535](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623579584535.png)



集群正常，不安装组件时内存占用率并不高

![1623579689768](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623579689768.png)

安装`kubectl`

```shell
$ yum install -y kubectl
```



## 安装可插拔组件

点击**自定义资源 CRD**，然后在搜索栏中输入 `clusterconfiguration`，点击搜索结果进入其详情页面。

![1623579764558](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623579764558.png)



按照自身需要启用可插拔组件，此处打开所有组件，即修改为如下配置

```yaml
apiVersion: installer.kubesphere.io/v1alpha1
kind: ClusterConfiguration
metadata:
  labels:
    version: v3.1.0
  name: ks-installer
  namespace: kubesphere-system
spec:
  alerting:
    enabled: true
  auditing:
    enabled: true
  authentication:
    jwtSecret: ''
  common:
    es:
      basicAuth:
        enabled: false
        password: ''
        username: ''
      elasticsearchDataVolumeSize: 20Gi
      elasticsearchMasterVolumeSize: 4Gi
      elkPrefix: logstash
      externalElasticsearchPort: ''
      externalElasticsearchUrl: ''
      logMaxAge: 7
    minioVolumeSize: 2Gi
    monitoring:
      endpoint: 'http://prometheus-operated.kubesphere-monitoring-system.svc:9090'
    openldap:
      enabled: true
    openldapVolumeSize: 2Gi
    redis:
      enabled: true
    redisVolumSize: 2Gi
  console:
    enableMultiLogin: true
    port: 30880
  devops:
    enabled: true
    jenkinsJavaOpts_MaxRAM: 2g
    jenkinsJavaOpts_Xms: 512m
    jenkinsJavaOpts_Xmx: 512m
    jenkinsMemoryLim: 2Gi
    jenkinsMemoryReq: 1500Mi
    jenkinsVolumeSize: 8Gi
  etcd:
    endpointIps: 10.170.0.5
    monitoring: true
    port: 2379
    tlsEnable: true
  events:
    enabled: true
    ruler:
      enabled: true
      replicas: 2
  kubeedge:
    cloudCore:
      cloudHub:
        advertiseAddress:
          - ''
        nodeLimit: '100'
      cloudhubHttpsPort: '10002'
      cloudhubPort: '10000'
      cloudhubQuicPort: '10001'
      cloudstreamPort: '10003'
      nodeSelector:
        node-role.kubernetes.io/worker: ''
      service:
        cloudhubHttpsNodePort: '30002'
        cloudhubNodePort: '30000'
        cloudhubQuicNodePort: '30001'
        cloudstreamNodePort: '30003'
        tunnelNodePort: '30004'
      tolerations: []
      tunnelPort: '10004'
    edgeWatcher:
      edgeWatcherAgent:
        nodeSelector:
          node-role.kubernetes.io/worker: ''
        tolerations: []
      nodeSelector:
        node-role.kubernetes.io/worker: ''
      tolerations: []
    enabled: true
  logging:
    enabled: true
    logsidecar:
      enabled: true
      replicas: 2
  metrics_server:
    enabled: true
  monitoring:
    prometheusMemoryRequest: 400Mi
    prometheusVolumeSize: 5Gi
    storageClass: ''
  multicluster:
    clusterRole: none
  network:
    ippool:
      type: calico
    networkpolicy:
      enabled: true
    topology:
      type: weave-scope
  openpitrix:
    store:
      enabled: true
  persistence:
    storageClass: ''
  servicemesh:
    enabled: true
```



通过在线控制台，查看安装进度

![1623580120458](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623580120458.png)



执行以下命令

```shell
$ kubectl logs -n kubesphere-system $(kubectl get pod -n kubesphere-system -l app=ks-install -o jsonpath='{.items[0].metadata.name}') -f
```

![1623580089627](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623580089627.png)



安装组件过程中，对CPU负载较大

![1623580387124](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623580387124.png)



所有组件安装完成

![1623580751492](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623580751492.png)



资源占用情况

![1623580770352](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1623580770352.png)
