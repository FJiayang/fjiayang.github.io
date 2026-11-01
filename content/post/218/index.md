{
  "title": "Kubernetes基础命令学习",
  "date": "2019-10-20T13:00:00+08:00",
  "lastmod": "2019-11-27T22:03:29+08:00",
  "typecho_cid": 218,
  "url": "/archives/218/",
  "comments": false,
  "draft": false,
  "slug": "218",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "Kubernetes"
  ],
  "image": "/images/recovered/5d56b001c55d28ddb0c2.png",
  "math": false
}

## 配置命令语法提示

执行命令查看指南

```bash
$ kubectl completion -h
Output shell completion code for the specified shell (bash or zsh). The shell code must be evaluated to provide
interactive completion of kubectl commands.  This can be done by sourcing it from the .bash_profile.

 Detailed instructions on how to do this are available here:
https://kubernetes.io/docs/tasks/tools/install-kubectl/#enabling-shell-autocompletion

 Note for zsh users: [1] zsh completions are only supported in versions of zsh >= 5.2

Examples:
  # Installing bash completion on macOS using homebrew
  ## If running Bash 3.2 included with macOS
  brew install bash-completion
  ## or, if running Bash 4.1+
  brew install bash-completion@2
  ## If kubectl is installed via homebrew, this should start working immediately.
  ## If you've installed via other means, you may need add the completion to your completion directory
  kubectl completion bash > $(brew --prefix)/etc/bash_completion.d/kubectl


  # Installing bash completion on Linux
  ## If bash-completion is not installed on Linux, please install the 'bash-completion' package
  ## via your distribution's package manager.
  ## Load the kubectl completion code for bash into the current shell
  source <(kubectl completion bash)
  ## Write bash completion code to a file and source if from .bash_profile
  kubectl completion bash > ~/.kube/completion.bash.inc
  printf "
  # Kubectl shell completion
  source '$HOME/.kube/completion.bash.inc'
  " >> $HOME/.bash_profile
  source $HOME/.bash_profile

  # Load the kubectl completion code for zsh[1] into the current shell
  source <(kubectl completion zsh)
  # Set the kubectl completion code for zsh[1] to autoload on startup
  kubectl completion zsh > "${fpath[1]}/_kubectl"

Usage:
  kubectl completion SHELL [options]

Use "kubectl options" for a list of global command-line options (applies to all commands).
```



按照指南操作即可



## 配置多个上下文环境

查看当前上下文配置

```bash
$ kubectl config get-contexts
CURRENT   NAME       CLUSTER    AUTHINFO           NAMESPACE
*         minikube   minikube   minikube
```



编辑`~/.kube/config`文件新增需要的上下文配置即可，配置完成后查看上下文信息

```bash
$ kubectl config get-contexts
CURRENT   NAME       CLUSTER    AUTHINFO           NAMESPACE
          kubeadm    kubeadm    kubernetes-admin
*         minikube   minikube   minikube
```



切换上下文

```bash
$ kubectl config use-context kubeadm
Switched to context "kubeadm".
```



再次查看，可见切换成功

```bash
$ kubectl config get-contexts
CURRENT   NAME       CLUSTER    AUTHINFO           NAMESPACE
*         kubeadm    kubeadm    kubernetes-admin
          minikube   minikube   minikube
```



## Pod相关操作

### 默认查看`default`命名空间的Pod

```bash
$ kubectl get pod
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-54f57cf6bf-pznmh   1/1     Running   0          52s
nginx-deployment-54f57cf6bf-r9q89   1/1     Running   0          52s
```



### 查看所有命名空间的Pod

```bash
$ kubectl get pod --all-namespaces
NAMESPACE     NAME                                 READY   STATUS    RESTARTS   AGE
kube-system   coredns-58cc8c89f4-c297b             1/1     Running   0          10m
kube-system   coredns-58cc8c89f4-spzhj             1/1     Running   0          10m
kube-system   etcd-k8s-master                      1/1     Running   0          9m57s
kube-system   kube-apiserver-k8s-master            1/1     Running   0          10m
kube-system   kube-controller-manager-k8s-master   1/1     Running   0          9m58s
kube-system   kube-flannel-ds-amd64-6fwg5          1/1     Running   0          5m
kube-system   kube-flannel-ds-amd64-6rchg          1/1     Running   0          9m12s
kube-system   kube-flannel-ds-amd64-z4plh          1/1     Running   0          4m54s
kube-system   kube-proxy-cdcs4                     1/1     Running   0          5m
kube-system   kube-proxy-nlmbb                     1/1     Running   0          4m54s
kube-system   kube-proxy-xlb62                     1/1     Running   0          10m
kube-system   kube-scheduler-k8s-master            1/1     Running   0          10m
```



### 指定Pod对应的app名称

```bash
$ kubectl get pod -l app=nginx
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-54f57cf6bf-pznmh   1/1     Running   0          58s
nginx-deployment-54f57cf6bf-r9q89   1/1     Running   0          58s
```



### 查看更多信息

```bash
$ kubectl get deployment -o wide
NAME               READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES        SELECTOR
nginx-deployment   2/2     2            2           64s   nginx        nginx:1.7.9   app=nginx
```



### 查看Pod详细信息

```bash
$ kubectl describe pod
Name:         nginx-deployment-54f57cf6bf-67llv
Namespace:    default
Priority:     0
Node:         k8s-node1/10.0.2.15
Start Time:   Sun, 20 Oct 2019 10:19:42 +0800
Labels:       app=nginx
              pod-template-hash=54f57cf6bf
Annotations:  <none>
Status:       Running
IP:           172.100.1.3
IPs:
  IP:           172.100.1.3
Controlled By:  ReplicaSet/nginx-deployment-54f57cf6bf
Containers:
  nginx:
    Container ID:   docker://ffd4b4fa3fd4678a61797cfdcba31ea2b0b36459b65a95100484eda4be286b9f
    Image:          nginx:1.7.9
    Image ID:       docker-pullable://nginx@sha256:e3456c851a152494c3e4ff5fcc26f240206abac0c9d794affb40e0714846c451
    Port:           80/TCP
    Host Port:      0/TCP
    State:          Running
      Started:      Sun, 20 Oct 2019 10:19:45 +0800
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-zjpq9 (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  default-token-zjpq9:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-zjpq9
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type    Reason     Age        From                Message
  ----    ------     ----       ----                -------
  Normal  Scheduled  <unknown>  default-scheduler   Successfully assigned default/nginx-deployment-54f57cf6bf-67llv to k8s-node1
  Normal  Pulled     46s        kubelet, k8s-node1  Container image "nginx:1.7.9" already present on machine
  Normal  Created    46s        kubelet, k8s-node1  Created container nginx
  Normal  Started    45s        kubelet, k8s-node1  Started container nginx


Name:         nginx-deployment-54f57cf6bf-r9q89
Namespace:    default
Priority:     0
Node:         k8s-node2/10.0.2.15
Start Time:   Sun, 20 Oct 2019 10:17:24 +0800
Labels:       app=nginx
              pod-template-hash=54f57cf6bf
Annotations:  <none>
Status:       Running
IP:           172.100.2.3
IPs:
  IP:           172.100.2.3
Controlled By:  ReplicaSet/nginx-deployment-54f57cf6bf
Containers:
  nginx:
    Container ID:   docker://61894b3762d723eabe2510284bb107098bdbcb8da4f841eea863a9c7a59c5806
    Image:          nginx:1.7.9
    Image ID:       docker-pullable://nginx@sha256:e3456c851a152494c3e4ff5fcc26f240206abac0c9d794affb40e0714846c451
    Port:           80/TCP
    Host Port:      0/TCP
    State:          Running
      Started:      Sun, 20 Oct 2019 10:18:08 +0800
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-zjpq9 (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  default-token-zjpq9:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-zjpq9
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type    Reason     Age        From                Message
  ----    ------     ----       ----                -------
  Normal  Scheduled  <unknown>  default-scheduler   Successfully assigned default/nginx-deployment-54f57cf6bf-r9q89 to k8s-node2
  Normal  Pulling    3m4s       kubelet, k8s-node2  Pulling image "nginx:1.7.9"
  Normal  Pulled     2m24s      kubelet, k8s-node2  Successfully pulled image "nginx:1.7.9"
  Normal  Created    2m22s      kubelet, k8s-node2  Created container nginx
  Normal  Started    2m22s      kubelet, k8s-node2  Started container nginx
```



## Deployment相关操作

### 部署Deployment

```bash
$ kubectl create -f nginx_deployment.yml
deployment.apps/nginx-deployment created
```



### 升级Deployment

`apply`兼有`create`的语义，故也可直接使用`apply`创建\部署`deployment`

```bash
$ kubectl apply -f nginx_deployment_scale.yml
deployment.apps/nginx-deployment configured
```



### 查看Deployment更多信息

```bash
$ kubectl get deployment -o wide
NAME               READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS   IMAGES      SELECTOR
nginx-deployment   2/2     2            2           5m28s   nginx        nginx:1.8   app=nginx
```



### 查看详细信息

```bash
$ kubectl describe deployments.apps
Name:                   nginx-deployment
Namespace:              default
CreationTimestamp:      Sun, 20 Oct 2019 10:17:24 +0800
Labels:                 <none>
Annotations:            deployment.kubernetes.io/revision: 3
                        kubectl.kubernetes.io/last-applied-configuration:
                          {"apiVersion":"apps/v1","kind":"Deployment","metadata":{"annotations":{},"name":"nginx-deployment","namespace":"default"},"spec":{"replica...
Selector:               app=nginx
Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=nginx
  Containers:
   nginx:
    Image:        nginx:1.9.1
    Port:         80/TCP
    Host Port:    0/TCP
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Progressing    True    NewReplicaSetAvailable
  Available      True    MinimumReplicasAvailable
OldReplicaSets:  <none>
NewReplicaSet:   nginx-deployment-56f8998dbc (2/2 replicas created)
Events:
  Type    Reason             Age                  From                   Message
  ----    ------             ----                 ----                   -------
  Normal  ScalingReplicaSet  22m                  deployment-controller  Scaled up replica set nginx-deployment-54f57cf6bf to 2
  Normal  ScalingReplicaSet  18m                  deployment-controller  Scaled up replica set nginx-deployment-9f46bb5 to 1
  Normal  ScalingReplicaSet  17m                  deployment-controller  Scaled down replica set nginx-deployment-54f57cf6bf to 1
  Normal  ScalingReplicaSet  17m                  deployment-controller  Scaled up replica set nginx-deployment-9f46bb5 to 2
  Normal  ScalingReplicaSet  16m                  deployment-controller  Scaled down replica set nginx-deployment-54f57cf6bf to 0
  Normal  ScalingReplicaSet  15m                  deployment-controller  Scaled up replica set nginx-deployment-9f46bb5 to 4
  Normal  ScalingReplicaSet  12m                  deployment-controller  Scaled down replica set nginx-deployment-9f46bb5 to 3
  Normal  ScalingReplicaSet  6m25s                deployment-controller  Scaled up replica set nginx-deployment-56f8998dbc to 1
  Normal  ScalingReplicaSet  5m43s                deployment-controller  Scaled down replica set nginx-deployment-9f46bb5 to 2
  Normal  ScalingReplicaSet  63s (x6 over 5m43s)  deployment-controller  (combined from similar events): Scaled down replica set nginx-deployment-56f8998dbc to 2
```





## Node相关

### 查看Node

```bash
$ kubectl get nodes
NAME         STATUS   ROLES    AGE   VERSION
k8s-master   Ready    master   24m   v1.16.2
k8s-node1    Ready    <none>   18m   v1.16.2
k8s-node2    Ready    <none>   18m   v1.16.2
```



### 查看更多信息

```bash
$ kubectl get nodes -o wide
NAME         STATUS   ROLES    AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                KERNEL-VERSION               CONTAINER-RUNTIME
k8s-master   Ready    master   24m   v1.16.2   10.0.2.15     <none>        CentOS Linux 7 (Core)   3.10.0-957.12.2.el7.x86_64   docker://18.9.8
k8s-node1    Ready    <none>   18m   v1.16.2   10.0.2.15     <none>        CentOS Linux 7 (Core)   3.10.0-957.12.2.el7.x86_64   docker://18.9.8
k8s-node2    Ready    <none>   18m   v1.16.2   10.0.2.15     <none>        CentOS Linux 7 (Core)   3.10.0-957.12.2.el7.x86_64   docker://18.9.8
```



### 查看标签

```bash
$ kubectl get nodes --show-labels
NAME         STATUS   ROLES    AGE   VERSION   LABELS
k8s-master   Ready    master   24m   v1.16.2   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=k8s-master,kubernetes.io/os=linux,node-role.kubernetes.io/master=
k8s-node1    Ready    <none>   18m   v1.16.2   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=k8s-node1,kubernetes.io/os=linux
k8s-node2    Ready    <none>   18m   v1.16.2   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=k8s-node2,kubernetes.io/os=linux
```



### 设置角色标签

```bash
$ kubectl label nodes k8s-node1 node-role.kubernetes.io/worker=
node/k8s-node1 labeled
```



### 查看详细信息

```bash
$ kubectl describe nodes
Name:               k8s-master
Roles:              master
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=k8s-master
                    kubernetes.io/os=linux
                    node-role.kubernetes.io/master=
Annotations:        flannel.alpha.coreos.com/backend-data: {"VtepMAC":"32:38:c5:18:f0:ed"}
                    flannel.alpha.coreos.com/backend-type: vxlan
                    flannel.alpha.coreos.com/kube-subnet-manager: true
                    flannel.alpha.coreos.com/public-ip: 10.0.2.15
                    kubeadm.alpha.kubernetes.io/cri-socket: /var/run/dockershim.sock
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Sun, 20 Oct 2019 10:05:02 +0800
Taints:             node-role.kubernetes.io/master:NoSchedule
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Sun, 20 Oct 2019 10:27:46 +0800   Sun, 20 Oct 2019 10:05:02 +0800   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Sun, 20 Oct 2019 10:27:46 +0800   Sun, 20 Oct 2019 10:05:02 +0800   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Sun, 20 Oct 2019 10:27:46 +0800   Sun, 20 Oct 2019 10:05:02 +0800   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Sun, 20 Oct 2019 10:27:46 +0800   Sun, 20 Oct 2019 10:07:42 +0800   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:  10.0.2.15
  Hostname:    k8s-master
Capacity:
 cpu:                2
 ephemeral-storage:  41921540Ki
 hugepages-2Mi:      0
 memory:             1882144Ki
 pods:               110
Allocatable:
 cpu:                2
 ephemeral-storage:  38634891201
 hugepages-2Mi:      0
 memory:             1779744Ki
 pods:               110
System Info:
 Machine ID:                 d74c50274729456aad2a6198de9863b3
 System UUID:                D74C5027-4729-456A-AD2A-6198DE9863B3
 Boot ID:                    fb2ea7bd-afb2-4051-afb7-78d9f59ec6f6
 Kernel Version:             3.10.0-957.12.2.el7.x86_64
 OS Image:                   CentOS Linux 7 (Core)
 Operating System:           linux
 Architecture:               amd64
 Container Runtime Version:  docker://18.9.8
 Kubelet Version:            v1.16.2
 Kube-Proxy Version:         v1.16.2
PodCIDR:                     172.100.0.0/24
PodCIDRs:                    172.100.0.0/24
Non-terminated Pods:         (8 in total)
  Namespace                  Name                                  CPU Requests  CPU Limits  Memory Requests  Memory Limits  AGE
  ---------                  ----                                  ------------  ----------  ---------------  -------------  ---
  kube-system                coredns-58cc8c89f4-c297b              100m (5%)     0 (0%)      70Mi (4%)        170Mi (9%)     23m
  kube-system                coredns-58cc8c89f4-spzhj              100m (5%)     0 (0%)      70Mi (4%)        170Mi (9%)     23m
  kube-system                etcd-k8s-master                       0 (0%)        0 (0%)      0 (0%)           0 (0%)         22m
  kube-system                kube-apiserver-k8s-master             250m (12%)    0 (0%)      0 (0%)           0 (0%)         22m
  kube-system                kube-controller-manager-k8s-master    200m (10%)    0 (0%)      0 (0%)           0 (0%)         22m
  kube-system                kube-flannel-ds-amd64-6rchg           100m (5%)     100m (5%)   50Mi (2%)        50Mi (2%)      21m
  kube-system                kube-proxy-xlb62                      0 (0%)        0 (0%)      0 (0%)           0 (0%)         23m
  kube-system                kube-scheduler-k8s-master             100m (5%)     0 (0%)      0 (0%)           0 (0%)         22m
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests     Limits
  --------           --------     ------
  cpu                850m (42%)   100m (5%)
  memory             190Mi (10%)  390Mi (22%)
  ephemeral-storage  0 (0%)       0 (0%)
Events:
  Type    Reason                   Age                From                    Message
  ----    ------                   ----               ----                    -------
  Normal  NodeHasSufficientMemory  23m (x8 over 23m)  kubelet, k8s-master     Node k8s-master status is now: NodeHasSufficientMemory
  Normal  NodeHasNoDiskPressure    23m (x8 over 23m)  kubelet, k8s-master     Node k8s-master status is now: NodeHasNoDiskPressure
  Normal  NodeHasSufficientPID     23m (x7 over 23m)  kubelet, k8s-master     Node k8s-master status is now: NodeHasSufficientPID
  Normal  Starting                 23m                kube-proxy, k8s-master  Starting kube-proxy.


Name:               k8s-node1
Roles:              <none>
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=k8s-node1
                    kubernetes.io/os=linux
Annotations:        flannel.alpha.coreos.com/backend-data: {"VtepMAC":"16:5c:40:b1:14:b6"}
                    flannel.alpha.coreos.com/backend-type: vxlan
                    flannel.alpha.coreos.com/kube-subnet-manager: true
                    flannel.alpha.coreos.com/public-ip: 10.0.2.15
                    kubeadm.alpha.kubernetes.io/cri-socket: /var/run/dockershim.sock
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Sun, 20 Oct 2019 10:11:03 +0800
Taints:             <none>
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Sun, 20 Oct 2019 10:28:08 +0800   Sun, 20 Oct 2019 10:11:03 +0800   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Sun, 20 Oct 2019 10:28:08 +0800   Sun, 20 Oct 2019 10:11:03 +0800   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Sun, 20 Oct 2019 10:28:08 +0800   Sun, 20 Oct 2019 10:11:03 +0800   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Sun, 20 Oct 2019 10:28:08 +0800   Sun, 20 Oct 2019 10:11:34 +0800   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:  10.0.2.15
  Hostname:    k8s-node1
Capacity:
 cpu:                1
 ephemeral-storage:  41921540Ki
 hugepages-2Mi:      0
 memory:             1882296Ki
 pods:               110
Allocatable:
 cpu:                1
 ephemeral-storage:  38634891201
 hugepages-2Mi:      0
 memory:             1779896Ki
 pods:               110
System Info:
 Machine ID:                 5d806dde9b0444bdb5c9800a228267d8
 System UUID:                5D806DDE-9B04-44BD-B5C9-800A228267D8
 Boot ID:                    e6b7222c-686c-49cb-8e56-9bb263852d36
 Kernel Version:             3.10.0-957.12.2.el7.x86_64
 OS Image:                   CentOS Linux 7 (Core)
 Operating System:           linux
 Architecture:               amd64
 Container Runtime Version:  docker://18.9.8
 Kubelet Version:            v1.16.2
 Kube-Proxy Version:         v1.16.2
PodCIDR:                     172.100.1.0/24
PodCIDRs:                    172.100.1.0/24
Non-terminated Pods:         (4 in total)
  Namespace                  Name                              CPU Requests  CPU Limits  Memory Requests  Memory Limits  AGE
  ---------                  ----                              ------------  ----------  ---------------  -------------  ---
  default                    nginx-deployment-9f46bb5-7vlb7    0 (0%)        0 (0%)      0 (0%)           0 (0%)         3m53s
  default                    nginx-deployment-9f46bb5-c7czx    0 (0%)        0 (0%)      0 (0%)           0 (0%)         6m35s
  kube-system                kube-flannel-ds-amd64-6fwg5       100m (10%)    100m (10%)  50Mi (2%)        50Mi (2%)      17m
  kube-system                kube-proxy-cdcs4                  0 (0%)        0 (0%)      0 (0%)           0 (0%)         17m
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                100m (10%)  100m (10%)
  memory             50Mi (2%)   50Mi (2%)
  ephemeral-storage  0 (0%)      0 (0%)
Events:
  Type    Reason                   Age   From                   Message
  ----    ------                   ----  ----                   -------
  Normal  Starting                 17m   kubelet, k8s-node1     Starting kubelet.
  Normal  NodeHasSufficientMemory  17m   kubelet, k8s-node1     Node k8s-node1 status is now: NodeHasSufficientMemory
  Normal  NodeHasNoDiskPressure    17m   kubelet, k8s-node1     Node k8s-node1 status is now: NodeHasNoDiskPressure
  Normal  NodeHasSufficientPID     17m   kubelet, k8s-node1     Node k8s-node1 status is now: NodeHasSufficientPID
  Normal  NodeAllocatableEnforced  17m   kubelet, k8s-node1     Updated Node Allocatable limit across pods
  Normal  Starting                 17m   kube-proxy, k8s-node1  Starting kube-proxy.
  Normal  NodeReady                16m   kubelet, k8s-node1     Node k8s-node1 status is now: NodeReady


Name:               k8s-node2
Roles:              <none>
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=k8s-node2
                    kubernetes.io/os=linux
Annotations:        flannel.alpha.coreos.com/backend-data: {"VtepMAC":"76:49:24:1f:e5:d6"}
                    flannel.alpha.coreos.com/backend-type: vxlan
                    flannel.alpha.coreos.com/kube-subnet-manager: true
                    flannel.alpha.coreos.com/public-ip: 10.0.2.15
                    kubeadm.alpha.kubernetes.io/cri-socket: /var/run/dockershim.sock
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Sun, 20 Oct 2019 10:11:09 +0800
Taints:             <none>
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Sun, 20 Oct 2019 10:27:42 +0800   Sun, 20 Oct 2019 10:11:09 +0800   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Sun, 20 Oct 2019 10:27:42 +0800   Sun, 20 Oct 2019 10:11:09 +0800   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Sun, 20 Oct 2019 10:27:42 +0800   Sun, 20 Oct 2019 10:11:09 +0800   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Sun, 20 Oct 2019 10:27:42 +0800   Sun, 20 Oct 2019 10:11:40 +0800   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:  10.0.2.15
  Hostname:    k8s-node2
Capacity:
 cpu:                1
 ephemeral-storage:  41921540Ki
 hugepages-2Mi:      0
 memory:             1882296Ki
 pods:               110
Allocatable:
 cpu:                1
 ephemeral-storage:  38634891201
 hugepages-2Mi:      0
 memory:             1779896Ki
 pods:               110
System Info:
 Machine ID:                 7c59ba12638e4fdfa20cfeda0aa2fda1
 System UUID:                7C59BA12-638E-4FDF-A20C-FEDA0AA2FDA1
 Boot ID:                    e402f75c-42e7-454d-aaca-f96853091c15
 Kernel Version:             3.10.0-957.12.2.el7.x86_64
 OS Image:                   CentOS Linux 7 (Core)
 Operating System:           linux
 Architecture:               amd64
 Container Runtime Version:  docker://18.9.8
 Kubelet Version:            v1.16.2
 Kube-Proxy Version:         v1.16.2
PodCIDR:                     172.100.2.0/24
PodCIDRs:                    172.100.2.0/24
Non-terminated Pods:         (3 in total)
  Namespace                  Name                              CPU Requests  CPU Limits  Memory Requests  Memory Limits  AGE
  ---------                  ----                              ------------  ----------  ---------------  -------------  ---
  default                    nginx-deployment-9f46bb5-mv4b7    0 (0%)        0 (0%)      0 (0%)           0 (0%)         5m52s
  kube-system                kube-flannel-ds-amd64-z4plh       100m (10%)    100m (10%)  50Mi (2%)        50Mi (2%)      17m
  kube-system                kube-proxy-nlmbb                  0 (0%)        0 (0%)      0 (0%)           0 (0%)         17m
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                100m (10%)  100m (10%)
  memory             50Mi (2%)   50Mi (2%)
  ephemeral-storage  0 (0%)      0 (0%)
Events:
  Type    Reason                   Age   From                   Message
  ----    ------                   ----  ----                   -------
  Normal  Starting                 17m   kubelet, k8s-node2     Starting kubelet.
  Normal  NodeHasSufficientMemory  17m   kubelet, k8s-node2     Node k8s-node2 status is now: NodeHasSufficientMemory
  Normal  NodeHasNoDiskPressure    17m   kubelet, k8s-node2     Node k8s-node2 status is now: NodeHasNoDiskPressure
  Normal  NodeHasSufficientPID     17m   kubelet, k8s-node2     Node k8s-node2 status is now: NodeHasSufficientPID
  Normal  NodeAllocatableEnforced  17m   kubelet, k8s-node2     Updated Node Allocatable limit across pods
  Normal  Starting                 17m   kube-proxy, k8s-node2  Starting kube-proxy.
  Normal  NodeReady                16m   kubelet, k8s-node2     Node k8s-node2 status is now: NodeReady
```



## 服务伸缩

### `scale`命令方式

```bash
$ kubectl scale --replicas=6 deployment/nginx-deployment
deployment.apps/nginx-deployment scaled
```



### 查看副本数

```bash
$ kubectl get replicaset
NAME                          DESIRED   CURRENT   READY   AGE
nginx-deployment-54f57cf6bf   0         0         0       21m
nginx-deployment-56f8998dbc   6         6         3       5m7s
nginx-deployment-9f46bb5      0         0         0       16m
```
