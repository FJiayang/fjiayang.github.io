{
  "title": "k8s证书失效问题排查",
  "date": "2020-12-27T12:00:58+08:00",
  "lastmod": "2020-12-27T12:00:58+08:00",
  "typecho_cid": 262,
  "url": "/archives/262/",
  "comments": false,
  "draft": false,
  "slug": "262",
  "categories": [
    "开发"
  ],
  "tags": [
    "Linux",
    "Kubernetes"
  ],
  "math": false
}

## 问题背景

生产环境`kuberneties`集群搭建于2019年11月7日，使用`kubeadm`结合国内镜像搭建，参考文章

[相关文章](/archives/217/)



2020年11月8日突然发现生产环境集群服务全都失效并且不可用，进行紧急排查处理



## 处理过程

### 1. 排查服务是否启动

```bash
[root@k8smaster1 ~]$ docker ps
CONTAINER ID        IMAGE                                               COMMAND                  CREATED             STATUS              PORTS               NAMES
65dff767f422        b95b1efa0436                                        "kube-controller-m..."   20 hours ago        Up 20 hours                             k8s_kube-controller-manager_kube-controller-manager-k8smaster1_kube-system_7a524400c16990c1a69c237c9da4c7f2_11
1b26acecbcea        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_kube-controller-manager-k8smaster1_kube-system_7a524400c16990c1a69c237c9da4c7f2_1
9c6449df0a18        00638a24688b                                        "kube-scheduler --..."   20 hours ago        Up 20 hours                             k8s_kube-scheduler_kube-scheduler-k8smaster1_kube-system_baebad22afce708e52c6d3f886ff9424_10
028a1177cc9b        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_kube-scheduler-k8smaster1_kube-system_baebad22afce708e52c6d3f886ff9424_1
6c6bdc2c2644        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_kube-apiserver-k8smaster1_kube-system_0e954d211e160f48f5ca9fd42d295c10_1
fe4a12daa7d7        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_etcd-k8smaster1_kube-system_6119961323d801d05a7dd23e429cda3f_1
```

容器服务正常，但`kubelet`服务有报错信息，报连接不上`apiserver`

```bash
[root@k8smaster1 ~]$ systemctl status kubelet -l
● kubelet.service - kubelet: The Kubernetes Node Agent
   Loaded: loaded (/usr/lib/systemd/system/kubelet.service; enabled; vendor preset: disabled)
  Drop-In: /usr/lib/systemd/system/kubelet.service.d
           └─10-kubeadm.conf
   Active: active (running) since 日 2020-11-08 22:16:07 CST; 20h ago
     Docs: https://kubernetes.io/docs/
 Main PID: 15313 (kubelet)
    Tasks: 16
   Memory: 68.4M
   CGroup: /system.slice/kubelet.service
           └─15313 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf --config=/var/lib/kubelet/config.yaml --cgroup-driver=systemd --network-plugin=cni --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1

11月 09 18:43:06 k8smaster1 kubelet[15313]: E1109 18:43:06.967416   15313 reflector.go:126] k8s.io/kubernetes/pkg/kubelet/kubelet.go:442: Failed to list *v1.Service: Get https://192.168.1.14:6443/api/v1/services?limit=500&resourceVersion=0: dial tcp 192.168.1.14:6443: connect: connection refused
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.009411   15313 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.109665   15313 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:43:07 k8smaster1 kubelet[15313]: I1109 18:43:07.165755   15313 kubelet_node_status.go:283] Setting node annotation to enable volume controller attach/detach
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.167106   15313 reflector.go:126] k8s.io/client-go/informers/factory.go:133: Failed to list *v1beta1.CSIDriver: Get https://192.168.1.14:6443/apis/storage.k8s.io/v1beta1/csidrivers?limit=500&resourceVersion=0: dial tcp 192.168.1.14:6443: connect: connection refused
11月 09 18:43:07 k8smaster1 kubelet[15313]: I1109 18:43:07.169000   15313 kubelet_node_status.go:72] Attempting to register node k8smaster1
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.209831   15313 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.310013   15313 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.362049   15313 kubelet_node_status.go:94] Unable to register node "k8smaster1" with API server: Post https://192.168.1.14:6443/api/v1/nodes: dial tcp 192.168.1.14:6443: connect: connection refused
11月 09 18:43:07 k8smaster1 kubelet[15313]: E1109 18:43:07.410174   15313 kubelet.go:2244] node "k8smaster1" not found
```





### 2. 检查APIServer

apiserver 端口连接正常

```bash
[root@k8smaster1 ~]$ telnet 192.168.1.14 6443
Trying 192.168.1.14...
telnet: connect to address 192.168.1.14: Connection refused
```

重设防火墙，并重新检查，连接正常

```bash
[root@k8smaster1 ~]$ iptables -F && iptables -X && iptables -F -t nat && iptables -X -t nat && iptables -P FORWARD ACCEPT
[root@k8smaster1 ~]$ telnet 192.168.1.14 6443
Trying 192.168.1.14...
Connected to 192.168.1.14.
```

但服务仍然无法访问



### 3. 重启kubelet

```bash
[root@k8smaster1 ~]$ systemctl restart kubelet
[root@k8smaster1 ~]$ docker ps
CONTAINER ID        IMAGE                                               COMMAND                  CREATED             STATUS              PORTS               NAMES
4383926ef6c9        ecf910f40d6e                                        "kube-apiserver --..."   3 seconds ago       Up 2 seconds                            k8s_kube-apiserver_kube-apiserver-k8smaster1_kube-system_0e954d211e160f48f5ca9fd42d295c10_1362
88eb6134fe3c        2c4adeb21b4f                                        "etcd --advertise-..."   3 seconds ago       Up 2 seconds                            k8s_etcd_etcd-k8smaster1_kube-system_6119961323d801d05a7dd23e429cda3f_1768
65dff767f422        b95b1efa0436                                        "kube-controller-m..."   20 hours ago        Up 20 hours                             k8s_kube-controller-manager_kube-controller-manager-k8smaster1_kube-system_7a524400c16990c1a69c237c9da4c7f2_11
1b26acecbcea        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_kube-controller-manager-k8smaster1_kube-system_7a524400c16990c1a69c237c9da4c7f2_1
9c6449df0a18        00638a24688b                                        "kube-scheduler --..."   20 hours ago        Up 20 hours                             k8s_kube-scheduler_kube-scheduler-k8smaster1_kube-system_baebad22afce708e52c6d3f886ff9424_10
028a1177cc9b        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_kube-scheduler-k8smaster1_kube-system_baebad22afce708e52c6d3f886ff9424_1
6c6bdc2c2644        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_kube-apiserver-k8smaster1_kube-system_0e954d211e160f48f5ca9fd42d295c10_1
fe4a12daa7d7        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1   "/pause"                 20 hours ago        Up 20 hours                             k8s_POD_etcd-k8smaster1_kube-system_6119961323d801d05a7dd23e429cda3f_1
```

检查kubelet状态，仍然报错

```bash
[root@k8smaster1 ~]$ systemctl status kubelet -l
● kubelet.service - kubelet: The Kubernetes Node Agent
   Loaded: loaded (/usr/lib/systemd/system/kubelet.service; enabled; vendor preset: disabled)
  Drop-In: /usr/lib/systemd/system/kubelet.service.d
           └─10-kubeadm.conf
   Active: active (running) since 一 2020-11-09 18:52:24 CST; 24s ago
     Docs: https://kubernetes.io/docs/
 Main PID: 31759 (kubelet)
    Tasks: 15
   Memory: 30.1M
   CGroup: /system.slice/kubelet.service
           └─31759 /usr/bin/kubelet --bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf --config=/var/lib/kubelet/config.yaml --cgroup-driver=systemd --network-plugin=cni --pod-infra-container-image=registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1

11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.063832   31759 controller.go:115] failed to ensure node lease exists, will retry in 3.2s, error: Get https://192.168.1.14:6443/apis/coordination.k8s.io/v1beta1/namespaces/kube-node-lease/leases/k8smaster1?timeout=10s: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.152723   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.252964   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.353226   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.453452   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.553682   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.653965   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.754181   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.854401   31759 kubelet.go:2244] node "k8smaster1" not found
11月 09 18:52:48 k8smaster1 kubelet[31759]: E1109 18:52:48.954576   31759 kubelet.go:2244] node "k8smaster1" not found
```



### 4.检查API Server日志

查容器ID

```bash
[root@k8smaster1 ~]$ docker ps -l
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
27a3b7787748        ecf910f40d6e        "kube-apiserver --..."   18 seconds ago      Up 18 seconds                           
```

查看日志

```bash
[root@k8smaster1 ~]$ docker logs 27a
Flag --insecure-port has been deprecated, This flag will be removed in a future version.
I1109 10:55:42.281078       1 server.go:559] external host was not specified, using 192.168.1.15
I1109 10:55:42.281264       1 server.go:146] Version: v1.14.0
I1109 10:55:42.759000       1 plugins.go:158] Loaded 9 mutating admission controller(s) successfully in the following order: NamespaceLifecycle,LimitRanger,ServiceAccount,NodeRestriction,TaintNodesByCondition,Priority,DefaultTolerationSeconds,DefaultStorageClass,MutatingAdmissionWebhook.
I1109 10:55:42.759031       1 plugins.go:161] Loaded 6 validating admission controller(s) successfully in the following order: LimitRanger,ServiceAccount,Priority,PersistentVolumeClaimResize,ValidatingAdmissionWebhook,ResourceQuota.
E1109 10:55:42.759943       1 prometheus.go:138] failed to register depth metric admission_quota_controller: duplicate metrics collector registration attempted
E1109 10:55:42.759976       1 prometheus.go:150] failed to register adds metric admission_quota_controller: duplicate metrics collector registration attempted
E1109 10:55:42.760007       1 prometheus.go:162] failed to register latency metric admission_quota_controller: duplicate metrics collector registration attempted
E1109 10:55:42.760038       1 prometheus.go:174] failed to register work_duration metric admission_quota_controller: duplicate metrics collector registration attempted
E1109 10:55:42.760065       1 prometheus.go:189] failed to register unfinished_work_seconds metric admission_quota_controller: duplicate metrics collector registration attempted
E1109 10:55:42.760086       1 prometheus.go:202] failed to register longest_running_processor_microseconds metric admission_quota_controller: duplicate metrics collector registration attempted
I1109 10:55:42.760102       1 plugins.go:158] Loaded 9 mutating admission controller(s) successfully in the following order: NamespaceLifecycle,LimitRanger,ServiceAccount,NodeRestriction,TaintNodesByCondition,Priority,DefaultTolerationSeconds,DefaultStorageClass,MutatingAdmissionWebhook.
I1109 10:55:42.760110       1 plugins.go:161] Loaded 6 validating admission controller(s) successfully in the following order: LimitRanger,ServiceAccount,Priority,PersistentVolumeClaimResize,ValidatingAdmissionWebhook,ResourceQuota.
I1109 10:55:42.763844       1 client.go:352] parsed scheme: ""
I1109 10:55:42.763866       1 client.go:352] scheme "" not registered, fallback to default scheme
I1109 10:55:42.764295       1 asm_amd64.s:1337] ccResolverWrapper: sending new addresses to cc: [{127.0.0.1:2379 0  <nil>}]
I1109 10:55:42.764449       1 asm_amd64.s:1337] balancerWrapper: got update addr from Notify: [{127.0.0.1:2379 <nil>}]
W1109 10:55:42.771517       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
I1109 10:55:43.756910       1 client.go:352] parsed scheme: ""
I1109 10:55:43.756939       1 client.go:352] scheme "" not registered, fallback to default scheme
I1109 10:55:43.756999       1 asm_amd64.s:1337] ccResolverWrapper: sending new addresses to cc: [{127.0.0.1:2379 0  <nil>}]
I1109 10:55:43.757077       1 asm_amd64.s:1337] balancerWrapper: got update addr from Notify: [{127.0.0.1:2379 <nil>}]
W1109 10:55:43.763355       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:43.770837       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:44.764994       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:45.541971       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:46.657328       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:47.938720       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:48.730961       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:51.899665       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:52.961615       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:55:59.193916       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
W1109 10:56:00.025333       1 clientconn.go:1251] grpc: addrConn.createTransport failed to connect to {127.0.0.1:2379 0  <nil>}. Err :connection error: desc = "transport: authentication handshake failed: x509: certificate has expired or is not yet valid". Reconnecting...
F1109 10:56:02.764150       1 storage_decorator.go:57] Unable to create storage backend: config (&{ /registry {[https://127.0.0.1:2379] /etc/kubernetes/pki/apiserver-etcd-client.key /etc/kubernetes/pki/apiserver-etcd-client.crt /etc/kubernetes/pki/etcd/ca.crt} false true 0xc0007a94d0 apiextensions.k8s.io/v1beta1 <nil> 5m0s 1m0s}), err (context deadline exceeded)
```

日志最后提示：`authentication handshake failed: x509: certificate has expired or is not yet valid`

以此信息查询解决方案



## 解决方案

### 外部推荐方案

最终在该网站找到解决方案

[Kubeadm证书过期时间调整](https://www.cnblogs.com/skymyyang/p/11093686.html) — Devops、小铁匠

![Kubeadm证书过期时间调整](/images/recovered/dd97e00269586198aae2.jpg)



### 采用方案

由于生产环境集群版本为1.14，是支持自动轮换证书的，故首先解决生产环境问题，先手动重新签发证书，再开启证书自动续签

#### 重新签发证书

国内网络直接签发证书会因为无法连接Google而报错

```bash
[root@k8smaster1 ~]$ kubeadm alpha certs renew all
I1109 19:33:40.266778   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
I1109 19:33:40.266978   22487 version.go:97] falling back to the local client version: v1.14.0
I1109 19:33:51.139051   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
I1109 19:33:51.139111   22487 version.go:97] falling back to the local client version: v1.14.0
I1109 19:34:01.511909   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
I1109 19:34:01.511967   22487 version.go:97] falling back to the local client version: v1.14.0
I1109 19:34:11.945411   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
I1109 19:34:11.945504   22487 version.go:97] falling back to the local client version: v1.14.0
I1109 19:34:22.145905   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
I1109 19:34:22.145975   22487 version.go:97] falling back to the local client version: v1.14.0
I1109 19:34:32.532514   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled (Client.Timeout exceeded while awaiting headers)
I1109 19:34:32.532561   22487 version.go:97] falling back to the local client version: v1.14.0
I1109 19:34:43.335574   22487 version.go:96] could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://storage.googleapis.com/kubernetes-release/release/stable-1.txt: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
I1109 19:34:43.335628   22487 version.go:97] falling back to the local client version: v1.14.0
```



先准备一份连接国内镜像的`kubeadm.conf`文件

```yaml
apiVersion: kubeadm.k8s.io/v1beta1
kind: ClusterConfiguration
kubernetesVersion: v1.14.0 #-->这里改成你集群对应的版本
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers 
#这里使用国内的镜像仓库，否则在重新签发的时候会报错：could not fetch a Kubernetes version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt"
```



重新签发，即可，并重启`kubelet`

```bash
[root@k8smaster1 ~]$ kubeadm alpha certs renew all --config=/root/kubeadm.conf
[root@k8smaster1 ~]$ systemctl restart kubelet
```



重新签发后若要使用kubectl命令，要重新生成`~/.kube/config`配置文件

```bash
[root@k8smaster1 kubernetes]$ kubeadm init phase kubeconfig all --config=/root/kubeadm.conf
[kubeconfig] Using kubeconfig folder "/etc/kubernetes"
[kubeconfig] Writing "admin.conf" kubeconfig file
[kubeconfig] Writing "kubelet.conf" kubeconfig file
[kubeconfig] Writing "controller-manager.conf" kubeconfig file
[kubeconfig] Writing "scheduler.conf" kubeconfig file
[root@k8smaster1 kubernetes]$ cp -i /etc/kubernetes/admin.conf ~/.kube/config
cp：是否覆盖"/root/.kube/config"？ y
```

命令正常使用

```bash
[root@k8smaster1 kubernetes]$ kubectl get pods
NAME                           READY   STATUS    RESTARTS   AGE
glusterfs-hfdmh                1/1     Running   0          351d
glusterfs-k766z                1/1     Running   0          351d
glusterfs-rrc7x                1/1     Running   0          351d
heketi-68f9dfdfbf-2k58b        1/1     Running   0          351d
nginx                          1/1     Running   1          370d
nginx-ds-29dbc                 1/1     Running   5          366d
nginx-ds-4w6cn                 1/1     Running   1          370d
nginx-ds-6lhsk                 0/1     Evicted   0          216d
nginx-ds-xq4h7                 1/1     Running   3          366d
tomcat-demo-6bc7d5b6f4-75rgc   0/1     Evicted   0          351d
```



重新启动集群上的所有服务，可见服务正常

#### 证书自动续签

> kubelet证书分为server和client两种， `k8s 1.9`默认启用了client证书的自动轮换，但server证书自动轮换需要用户开启

查询`kubelet`配置文件位置

```bash
[root@k8smaster1 ~]$ find / -name 10-kubeadm.conf
/usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
[root@k8smaster1 ~]$ vi /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
```

添加配置如下

```properties
# 在/etc/systemd/system/kubelet.service.d/10-kubeadm.conf 增加如下参数
Environment="KUBELET_EXTRA_ARGS=--feature-gates=RotateKubeletServerCertificate=true"
```



添加`Controller-Manager`参数

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    component: kube-controller-manager
    tier: control-plane
  name: kube-controller-manager
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-controller-manager
    - --allocate-node-cidrs=true
    # 证书有效期
    - --experimental-cluster-signing-duration=87600h0m0s
    # 证书自动签发
    - --feature-gates=RotateKubeletServerCertificate=true
    - --authentication-kubeconfig=/etc/kubernetes/controller-manager.conf
    - --authorization-kubeconfig=/etc/kubernetes/controller-manager.conf
    - --bind-address=127.0.0.1
    - --client-ca-file=/etc/kubernetes/pki/ca.crt
    - --cluster-cidr=172.22.0.0/16
    - --cluster-signing-cert-file=/etc/kubernetes/pki/ca.crt
    - --cluster-signing-key-file=/etc/kubernetes/pki/ca.key
    - --controllers=*,bootstrapsigner,tokencleaner
    - --kubeconfig=/etc/kubernetes/controller-manager.conf
    - --leader-elect=true
    - --node-cidr-mask-size=24
    - --requestheader-client-ca-file=/etc/k
```



创建RBAC对象

```bash
cat > ca-update.yaml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  labels:
    kubernetes.io/bootstrapping: rbac-defaults
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeserver
rules:
- apiGroups:
  - certificates.k8s.io
  resources:
  - certificatesigningrequests/selfnodeserver
  verbs:
  - create
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kubeadm:node-autoapprove-certificate-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeserver
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: system:nodes
EOF
```

```bash
[root@k8smaster1 ~]$ kubectl create -f ca-update.yaml
clusterrole.rbac.authorization.k8s.io/system:certificates.k8s.io:certificatesigningrequests:selfnodeserver created
clusterrolebinding.rbac.authorization.k8s.io/kubeadm:node-autoapprove-certificate-server created
```
