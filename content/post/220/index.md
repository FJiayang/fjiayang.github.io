{
  "title": "k8s监控平台搭建",
  "date": "2019-11-12T21:33:00+08:00",
  "lastmod": "2019-11-12T22:19:49+08:00",
  "typecho_cid": 220,
  "url": "/archives/220/",
  "comments": false,
  "draft": false,
  "slug": "220",
  "categories": [
    "服务器",
    "学习"
  ],
  "tags": [
    "docker",
    "Kubernetes",
    "Prometheus",
    "Grafana"
  ],
  "math": false
}

## 架构

目前主流容器化监控平台采用`Prometheus`+`Grafana`架构，下图为`Prometheus`架构图，可以主动发现各种指标和采集数据，实现

- 监控每个节点基础指标
- 监控每个容器基础指标
- 监控k8s集群组件基础指标

![Prometheus architecture](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/architecture.png)

## 基础环境

Kubernetes：v1.14.0

Docker：17.03.1-ce

机器数：$3 \times master + 2 \times worker$



## 部署

### Helm

Helm作为k8s平台软件包管理工具，结合prometheus-operator可以类似插件的方式快速搭建监控体系，Helm旗下包含charts项目，为软件包仓库

Helm官方仓库：<https://github.com/helm/helm>

charts官方仓库：<https://github.com/helm/charts>



#### 安装Helm

通过官方仓库查看目前最新版为v2.16.0，但由于仍有不稳定的情况，故不推荐该版本，原因可通过其issue查看

- [No kind Job is registered for version batch/v1 #6894](https://github.com/helm/helm/issues/6894)

- [Unable to Deploy on Polyaxon with helm v2.16.0 (No kind Job is registered for version batch/v1) #601](https://github.com/polyaxon/polyaxon/issues/601)

![1573557182761](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573557182761.png)



此处选择安装v2.15.2的版本，[下载页面](https://github.com/helm/helm/releases/tag/v2.15.2)

解压并放到可执行目录下

```bash
$ tar -zxvf helm-v2.15.2-linux-amd64.tar.gz
$ mv linux-amd64/helm /usr/local/bin/
```



#### Tiller安装

Tiller 是以 Deployment 方式部署在 Kubernetes 集群中的，由于国内网络原因，需要配置为阿里云镜像

```bash
$ helm init --client-only --stable-repo-url https://aliacs-app-catalog.oss-cn-hangzhou.aliyuncs.com/charts/
$ helm repo add incubator https://aliacs-app-catalog.oss-cn-hangzhou.aliyuncs.com/charts-incubator/
$ helm repo update
```

因为官方的镜像无法拉取，使用-i指定自己的镜像

```bash
$ helm init --service-account tiller --upgrade -i registry.cn-hangzhou.aliyuncs.com/google_containers/tiller:v2.15.2  --stable-repo-url https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
```

创建TLS认证服务端

```bash
$ helm init --service-account tiller --upgrade -i registry.cn-hangzhou.aliyuncs.com/google_containers/tiller:v2.15.2 --tiller-tls-cert /etc/kubernetes/ssl/tiller001.pem --tiller-tls-key /etc/kubernetes/ssl/tiller001-key.pem --tls-ca-cert /etc/kubernetes/ssl/ca.pem --tiller-namespace kube-system --stable-repo-url https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
```

#### Tiller授权

 Tiller 需要访问ApiServer去对集群进行操作。目前的 Tiller 部署时默认没有定义授权的 ServiceAccount，这会导致访问 API Server 时被拒绝。所以我们需要明确为 Tiller 部署添加授权

创建ServiceAccount和创建角色绑定

```bash
$ kubectl create serviceaccount --namespace kube-system tiller
$ kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
```



#### 验证

查看Tiller的ServiceAccount，需要跟创建的名字一致：tiller

```bash
$ kubectl get deploy --namespace kube-system tiller-deploy -o yaml|grep serviceAccount
      serviceAccount: tiller
      serviceAccountName: tiller
```

验证pods

```bash
$  kubectl -n kube-system get pods|grep tiller
tiller-deploy-b6c45d5bc-jhntj          1/1     Running   0          2d8h
```

验证版本

```bash
$ helm version
Client: &version.Version{SemVer:"v2.15.2", GitCommit:"8dce272473e5f2a7bf58ce79bb5c3691db54c96b", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.15.2", GitCommit:"8dce272473e5f2a7bf58ce79bb5c3691db54c96b", GitTreeState:"clean"}
```



### Operator

可以自定义资源类型(CDR)结合自定义控制器实现

样例

```yaml
apiVersion: app.example.com/v1
kind: AppService
metadata:
  name: nginx-app
spec:
  size: 2
  image: nginx:1.7.9
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30002
```

### Charts

charts项目下stable目录里存放所有软件包内容，由于其默认从多处镜像仓库中拉取镜像，可能存在网络问题，需结合实际情况修改镜像配置，手动安装软件包

推荐配置地址：

- `quay.io` 替换为 `quay.azk8s.cn`
- `gcr.io/google-containers` 替换为 `registry.cn-hangzhou.aliyuncs.com/google-containers`

本次需要安装的软件包为`prometheus-operator`，但其还包含多个依赖软件如下

- `grafana`
- `kube-state-metrics`
- `prometheus-node-exporter`

若需要手动安装则需要按照整理目录如下

```bash
prometheus-operator/
├── charts
│   ├── grafana
│   ├── kube-state-metrics
│   └── prometheus-node-exporter
...
```

### 手动安装

#### Etcd监控配置

监控etcd需要额外配置，而且较为复杂，具体步骤如下

1. 查看etcd在集群中的配置，由于本k8s集群基于kubeadm搭建，故etcd通过容器方式运行，查看方法

   ```bash
   # 查看etcd所在pod名称
   $ kubectl get pod --all-namespaces | grep etcd
   kube-system     etcd-k8smaster1                                         1/1     Running   0          7d1h
   # 展开etcd详细配置
   $ kubectl get pod -n kube-system etcd-k8smaster1 -o yaml
   ```

   配置内容查看其健康检查端点，`--listen-client-urls`指明其监听在https端点，故需要配置安全证书才能访问

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     annotations:
       kubernetes.io/config.hash: 6119961323d801d05a7dd23e429cda3f
       kubernetes.io/config.mirror: 6119961323d801d05a7dd23e429cda3f
       kubernetes.io/config.seen: "2019-11-05T19:17:28.480984831+08:00"
       kubernetes.io/config.source: file
     creationTimestamp: "2019-11-05T11:18:53Z"
     labels:
       component: etcd
       tier: control-plane
     name: etcd-k8smaster1
     namespace: kube-system
     resourceVersion: "876368"
     selfLink: /api/v1/namespaces/kube-system/pods/etcd-k8smaster1
     uid: 0ccf5e91-ffbe-11e9-a5d2-000c298872e2
   spec:
     containers:
     - command:
       - etcd
       - --advertise-client-urls=https://192.168.1.15:2379
       - --cert-file=/etc/kubernetes/pki/etcd/server.crt
       - --client-cert-auth=true
       - --data-dir=/var/lib/etcd
       - --initial-advertise-peer-urls=https://192.168.1.15:2380
       - --initial-cluster=k8smaster1=https://192.168.1.15:2380
       - --key-file=/etc/kubernetes/pki/etcd/server.key
       - --listen-client-urls=https://127.0.0.1:2379,https://192.168.1.15:2379
       - --listen-peer-urls=https://192.168.1.15:2380
       - --name=k8smaster1
       - --peer-cert-file=/etc/kubernetes/pki/etcd/peer.crt
       - --peer-client-cert-auth=true
       - --peer-key-file=/etc/kubernetes/pki/etcd/peer.key
       - --peer-trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
       - --snapshot-count=10000
       - --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
       image: registry.cn-hangzhou.aliyuncs.com/imooc/etcd:3.3.10
       imagePullPolicy: IfNotPresent
       livenessProbe:
   ...
   hostIP: 192.168.1.15
   ...
   ```

2. 配置安全证书

   k8s创建etcd时会自动创建相关证书，当前集群版本为1.14，证书位于`/etc/kubernetes/pki/etcd/`中

   ```bash
   $ ls /etc/kubernetes/pki/etcd/
   ca.crt  ca.key  healthcheck-client.crt  healthcheck-client.key  peer.crt  peer.key  server.crt  server.key
   ```

   可以通过`curl`命令加载证书测试能否访问健康检查端点

   ```bash
   $ curl -k --cert /etc/kubernetes/pki/etcd/healthcheck-client.crt --key /etc/kubernetes/pki/etcd/healthcheck-client.key https://192.168.1.15:2379/metrics
   ```

   若有如下输出则正常

   ```bash
   # HELP etcd_debugging_mvcc_db_compaction_keys_total Total number of db keys compacted.
   # TYPE etcd_debugging_mvcc_db_compaction_keys_total counter
   etcd_debugging_mvcc_db_compaction_keys_total 1.030132e+06
   # HELP etcd_debugging_mvcc_db_compaction_pause_duration_milliseconds Bucketed histogram of db compaction pause duration.
   # TYPE etcd_debugging_mvcc_db_compaction_pause_duration_milliseconds histogram
   etcd_debugging_mvcc_db_compaction_pause_duration_milliseconds_bucket{le="1"} 0
   etcd_debugging_mvcc_db_compaction_pause_duration_milliseconds_bucket{le="2"} 0
   etcd_debugging_mvcc_db_compaction_pause_duration_milliseconds_bucket{le="4"} 0
   etcd_debugging_mvcc_db_compaction_pause_duration_milliseconds_bucket{le="8"} 0
   ...
   ```

3. 创建证书秘钥

   关联三个证书文件，创建k8s访问秘钥，秘钥名称为`etcd-certs`

   ```bash
   $ kubectl create secret generic etcd-certs -n monitoring --from-file=/etc/kubernetes/pki/etcd/ca.crt --from-file=/etc/kubernetes/pki/etcd/healthcheck-client.crt --from-file=/etc/kubernetes/pki/etcd/healthcheck-client.key
   ```

4. 写入prometheus配置文件`values.yaml`

   注意，此处路径前缀固定写法为`/etc/prometheus/secrets/`+秘钥名称+文件名称，若写错证书路径则无法在指标中查看到对应的`target`

   ```yaml
   ... 
     serviceMonitor:
       ## Scrape interval. If not set, the Prometheus default scrape interval is used.
       ##
       interval: ""
       scheme: https
       insecureSkipVerify: true
       serverName: ""
       caFile: /etc/prometheus/secrets/etcd-certs/ca.crt
       certFile: /etc/prometheus/secrets/etcd-certs/healthcheck-client.crt
       keyFile: /etc/prometheus/secrets/etcd-certs/healthcheck-client.key
   ...
   ```



#### 创建

指定命名空间和文件目录，若命名空间不存在会自动创建

```bash
$ helm install /root/prometheus-operator/ --name k8s-prometheus --namespace monitoring
```

等待一段时间，输出如下则创建成功

```bash
NAME:   k8s-prometheus
LAST DEPLOYED: Tue Nov 12 20:27:18 2019
NAMESPACE: monitoring
STATUS: DEPLOYED

RESOURCES:
==> v1/Alertmanager
NAME                                    AGE
k8s-prometheus-prometheus-alertmanager  33s

==> v1/ClusterRole
NAME                                         AGE
k8s-prometheus-grafana-clusterrole           34s
k8s-prometheus-prometheus-alertmanager       34s
k8s-prometheus-prometheus-operator           34s
k8s-prometheus-prometheus-operator-psp       34s
k8s-prometheus-prometheus-prometheus         34s
k8s-prometheus-prometheus-prometheus-psp     34s
psp-k8s-prometheus-kube-state-metrics        34s
psp-k8s-prometheus-prometheus-node-exporter  34s

==> v1/ClusterRoleBinding
NAME                                         AGE
k8s-prometheus-grafana-clusterrolebinding    34s
k8s-prometheus-prometheus-alertmanager       34s
k8s-prometheus-prometheus-operator           34s
k8s-prometheus-prometheus-operator-psp       34s
k8s-prometheus-prometheus-prometheus         34s
k8s-prometheus-prometheus-prometheus-psp     34s
psp-k8s-prometheus-kube-state-metrics        34s
psp-k8s-prometheus-prometheus-node-exporter  34s

==> v1/ConfigMap
NAME                                                         DATA  AGE
k8s-prometheus-grafana                                       1     34s
k8s-prometheus-grafana-config-dashboards                     1     34s
k8s-prometheus-grafana-test                                  1     34s
k8s-prometheus-prometheus-apiserver                          1     34s
k8s-prometheus-prometheus-cluster-total                      1     34s
k8s-prometheus-prometheus-controller-manager                 1     34s
k8s-prometheus-prometheus-etcd                               1     34s
k8s-prometheus-prometheus-grafana-datasource                 1     34s
k8s-prometheus-prometheus-k8s-coredns                        1     34s
k8s-prometheus-prometheus-k8s-resources-cluster              1     34s
k8s-prometheus-prometheus-k8s-resources-namespace            1     34s
k8s-prometheus-prometheus-k8s-resources-node                 1     34s
k8s-prometheus-prometheus-k8s-resources-pod                  1     34s
k8s-prometheus-prometheus-k8s-resources-workload             1     34s
k8s-prometheus-prometheus-k8s-resources-workloads-namespace  1     34s
k8s-prometheus-prometheus-kubelet                            1     34s
k8s-prometheus-prometheus-namespace-by-pod                   1     34s
k8s-prometheus-prometheus-namespace-by-workload              1     34s
k8s-prometheus-prometheus-node-cluster-rsrc-use              1     34s
k8s-prometheus-prometheus-node-rsrc-use                      1     34s
k8s-prometheus-prometheus-nodes                              1     34s
k8s-prometheus-prometheus-persistentvolumesusage             1     34s
k8s-prometheus-prometheus-pod-total                          1     34s
k8s-prometheus-prometheus-pods                               1     34s
k8s-prometheus-prometheus-prometheus                         1     34s
k8s-prometheus-prometheus-proxy                              1     34s
k8s-prometheus-prometheus-scheduler                          1     34s
k8s-prometheus-prometheus-statefulset                        1     34s
k8s-prometheus-prometheus-workload-total                     1     34s

==> v1/DaemonSet
NAME                                     DESIRED  CURRENT  READY  UP-TO-DATE  AVAILABLE  NODE SELECTOR  AGE
k8s-prometheus-prometheus-node-exporter  5        5        5      5           5          <none>         33s

==> v1/Deployment
NAME                                READY  UP-TO-DATE  AVAILABLE  AGE
k8s-prometheus-grafana              1/1    1           1          33s
k8s-prometheus-kube-state-metrics   1/1    1           1          33s
k8s-prometheus-prometheus-operator  1/1    1           1          33s

==> v1/Pod(related)
NAME                                                 READY  STATUS   RESTARTS  AGE
k8s-prometheus-grafana-769d6dfb69-mtbdg              2/2    Running  0         33s
k8s-prometheus-kube-state-metrics-76b8ff78cd-kjxvl   1/1    Running  0         33s
k8s-prometheus-prometheus-node-exporter-jqkvf        1/1    Running  0         33s
k8s-prometheus-prometheus-node-exporter-jxpzm        1/1    Running  0         33s
k8s-prometheus-prometheus-node-exporter-k8n6x        1/1    Running  0         33s
k8s-prometheus-prometheus-node-exporter-kpjzk        1/1    Running  0         33s
k8s-prometheus-prometheus-node-exporter-qc6kv        1/1    Running  0         33s
k8s-prometheus-prometheus-operator-5f894bc75d-kvkvs  2/2    Running  0         33s

==> v1/Prometheus
NAME                                  AGE
k8s-prometheus-prometheus-prometheus  33s

==> v1/PrometheusRule
NAME                                                            AGE
k8s-prometheus-prometheus-alertmanager.rules                    32s
k8s-prometheus-prometheus-etcd                                  32s
k8s-prometheus-prometheus-general.rules                         32s
k8s-prometheus-prometheus-k8s.rules                             32s
k8s-prometheus-prometheus-kube-apiserver.rules                  32s
k8s-prometheus-prometheus-kube-prometheus-node-recording.rules  32s
k8s-prometheus-prometheus-kube-scheduler.rules                  32s
k8s-prometheus-prometheus-kubernetes-absent                     32s
k8s-prometheus-prometheus-kubernetes-apps                       32s
k8s-prometheus-prometheus-kubernetes-resources                  32s
k8s-prometheus-prometheus-kubernetes-storage                    32s
k8s-prometheus-prometheus-kubernetes-system                     32s
k8s-prometheus-prometheus-kubernetes-system-apiserver           32s
k8s-prometheus-prometheus-kubernetes-system-controller-manager  32s
k8s-prometheus-prometheus-kubernetes-system-kubelet             32s
k8s-prometheus-prometheus-kubernetes-system-scheduler           32s
k8s-prometheus-prometheus-node-exporter                         32s
k8s-prometheus-prometheus-node-exporter.rules                   32s
k8s-prometheus-prometheus-node-network                          32s
k8s-prometheus-prometheus-node-time                             32s
k8s-prometheus-prometheus-node.rules                            32s
k8s-prometheus-prometheus-prometheus                            32s
k8s-prometheus-prometheus-prometheus-operator                   32s

==> v1/Role
NAME                         AGE
k8s-prometheus-grafana-test  34s

==> v1/RoleBinding
NAME                         AGE
k8s-prometheus-grafana-test  34s

==> v1/Secret
NAME                                                 TYPE    DATA  AGE
alertmanager-k8s-prometheus-prometheus-alertmanager  Opaque  1     34s
k8s-prometheus-grafana                               Opaque  3     34s

==> v1/Service
NAME                                               TYPE       CLUSTER-IP     EXTERNAL-IP  PORT(S)           AGE
k8s-prometheus-grafana                             ClusterIP  10.100.203.67  <none>       80/TCP            33s
k8s-prometheus-kube-state-metrics                  ClusterIP  10.98.35.173   <none>       8080/TCP          33s
k8s-prometheus-prometheus-alertmanager             ClusterIP  10.97.189.252  <none>       9093/TCP          33s
k8s-prometheus-prometheus-coredns                  ClusterIP  None           <none>       9153/TCP          34s
k8s-prometheus-prometheus-kube-controller-manager  ClusterIP  None           <none>       10252/TCP         34s
k8s-prometheus-prometheus-kube-etcd                ClusterIP  None           <none>       2379/TCP          34s
k8s-prometheus-prometheus-kube-proxy               ClusterIP  None           <none>       10249/TCP         34s
k8s-prometheus-prometheus-kube-scheduler           ClusterIP  None           <none>       10251/TCP         34s
k8s-prometheus-prometheus-node-exporter            ClusterIP  10.100.146.95  <none>       9100/TCP          33s
k8s-prometheus-prometheus-operator                 ClusterIP  10.105.23.58   <none>       8080/TCP,443/TCP  33s
k8s-prometheus-prometheus-prometheus               ClusterIP  10.99.7.136    <none>       9090/TCP          34s

==> v1/ServiceAccount
NAME                                     SECRETS  AGE
k8s-prometheus-grafana                   1        34s
k8s-prometheus-grafana-test              1        34s
k8s-prometheus-kube-state-metrics        1        34s
k8s-prometheus-prometheus-alertmanager   1        34s
k8s-prometheus-prometheus-node-exporter  1        34s
k8s-prometheus-prometheus-operator       1        34s
k8s-prometheus-prometheus-prometheus     1        34s

==> v1/ServiceMonitor
NAME                                               AGE
k8s-prometheus-prometheus-alertmanager             32s
k8s-prometheus-prometheus-apiserver                32s
k8s-prometheus-prometheus-coredns                  32s
k8s-prometheus-prometheus-grafana                  32s
k8s-prometheus-prometheus-kube-controller-manager  32s
k8s-prometheus-prometheus-kube-etcd                32s
k8s-prometheus-prometheus-kube-proxy               32s
k8s-prometheus-prometheus-kube-scheduler           32s
k8s-prometheus-prometheus-kube-state-metrics       32s
k8s-prometheus-prometheus-kubelet                  32s
k8s-prometheus-prometheus-node-exporter            32s
k8s-prometheus-prometheus-operator                 32s
k8s-prometheus-prometheus-prometheus               32s

==> v1beta1/ClusterRole
NAME                               AGE
k8s-prometheus-kube-state-metrics  34s

==> v1beta1/ClusterRoleBinding
NAME                               AGE
k8s-prometheus-kube-state-metrics  34s

==> v1beta1/MutatingWebhookConfiguration
NAME                                 AGE
k8s-prometheus-prometheus-admission  33s

==> v1beta1/PodSecurityPolicy
NAME                                     PRIV   CAPS      SELINUX           RUNASUSER  FSGROUP    SUPGROUP  READONLYROOTFS  VOLUMES
k8s-prometheus-grafana                   false  RunAsAny  RunAsAny          RunAsAny   RunAsAny   false     configMap,emptyDir,projected,secret,downwardAPI,persistentVolumeClaim
k8s-prometheus-grafana-test              false  RunAsAny  RunAsAny          RunAsAny   RunAsAny   false     configMap,downwardAPI,emptyDir,projected,secret
k8s-prometheus-kube-state-metrics        false  RunAsAny  MustRunAsNonRoot  MustRunAs  MustRunAs  false     secret
k8s-prometheus-prometheus-alertmanager   false  RunAsAny  RunAsAny          MustRunAs  MustRunAs  false     configMap,emptyDir,projected,secret,downwardAPI,persistentVolumeClaim
k8s-prometheus-prometheus-node-exporter  false  RunAsAny  RunAsAny          MustRunAs  MustRunAs  false     configMap,emptyDir,projected,secret,downwardAPI,persistentVolumeClaim,hostPath
k8s-prometheus-prometheus-operator       false  RunAsAny  RunAsAny          MustRunAs  MustRunAs  false     configMap,emptyDir,projected,secret,downwardAPI,persistentVolumeClaim
k8s-prometheus-prometheus-prometheus     false  RunAsAny  RunAsAny          MustRunAs  MustRunAs  false     configMap,emptyDir,projected,secret,downwardAPI,persistentVolumeClaim

==> v1beta1/Role
NAME                    AGE
k8s-prometheus-grafana  34s

==> v1beta1/RoleBinding
NAME                    AGE
k8s-prometheus-grafana  34s

==> v1beta1/ValidatingWebhookConfiguration
NAME                                 AGE
k8s-prometheus-prometheus-admission  32s


NOTES:
The Prometheus Operator has been installed. Check its status by running:
  kubectl --namespace monitoring get pods -l "release=k8s-prometheus"

Visit https://github.com/coreos/prometheus-operator for instructions on how
to create & configure Alertmanager and Prometheus instances using the Operator.
```



#### 升级软件包

一般用于修改`yaml`配置文件重载应用

```bash
$ helm upgrade k8s-prometheus /root/prometheus-operator/ -f /root/prometheus-operator/charts/grafana/values.yaml
```



#### 删除

使用Helm的优势在于安装软件包和删除都非常方便，通过命令即可快速删除

普通删除，会放入回收站

```bash
$ helm delete k8s-prometheus
```

强制删除，不会放入回收站

```bash
$ helm delete k8s-prometheus --purge
```

对于当前监控组件来说，删除后同时要删除`CRD`

```bash
$ kubectl get crd | grep coreos
```

删除所有的`CRD`

```bash
$ kubectl delete crd $(kubectl get crd | grep coreos | awk '{print $1}')
```





## 访问指标面板

由于当前集群配置了`ingress-nginx`负载均衡，故新增两个配置文件即可访问Prometheus和Grafana

访问Grafana

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: prom-grafana
  namespace: monitoring
spec:
  rules:
  - host: your.domain
    http:
      paths:
      - backend:
          serviceName: k8s-prometheus-grafana
          servicePort: 80
        path: /
```

访问Prometheus

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: prometheus
  namespace: monitoring
spec:
  rules:
  - host: your.domain
    http:
      paths:
      - backend:
          serviceName: k8s-prometheus-prometheus-prometheus
          servicePort: web
        path: /
```



### Prometheus 

访问Prometheus web站点，首页支持执行`PromeQL`查询采集指标信息

![1573563429972](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573563429972.png)



访问target可见所有指标采集器都处于正常状态

![1573562831317](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573562831317.png)



访问监控与告警可查看所有告警规则

![1573563374318](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573563374318.png)



### Grafana

首次访问会要求登陆

![1573563646221](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573563646221.png)

#### 查看用户名和密码

在`grafana`软件包的`values.yaml`配置中有如下描述，声明密码被存储在`k8s`的secret中

```yaml
# Administrator credentials when not using an existing secret (see below)
adminUser: admin
# adminPassword: strongpassword

# Use an existing secret for the admin user.
admin:
  existingSecret: ""
  userKey: admin-user
  passwordKey: admin-password
```

查看监控命名空间的秘钥

```bash
$ kubectl get secrets -n monitoring
NAME                                                         TYPE                                  DATA   AGE
alertmanager-k8s-prometheus-prometheus-alertmanager          Opaque                                1      34m
default-token-hrhgk                                          kubernetes.io/service-account-token   3      2d10h
etcd-certs                                                   Opaque                                3      2d8h
k8s-prometheus-grafana                                       Opaque                                3      34m
k8s-prometheus-grafana-test-token-nnnvk                      kubernetes.io/service-account-token   3      34m
k8s-prometheus-grafana-token-cdw2n                           kubernetes.io/service-account-token   3      34m
k8s-prometheus-kube-state-metrics-token-6rxp4                kubernetes.io/service-account-token   3      34m
k8s-prometheus-prometheus-admission                          Opaque                                3      2d10h
k8s-prometheus-prometheus-alertmanager-token-hxqm9           kubernetes.io/service-account-token   3      34m
k8s-prometheus-prometheus-node-exporter-token-vjrcs          kubernetes.io/service-account-token   3      34m
k8s-prometheus-prometheus-operator-token-bkhrb               kubernetes.io/service-account-token   3      34m
k8s-prometheus-prometheus-prometheus-token-wf2v6             kubernetes.io/service-account-token   3      34m
prometheus-k8s-prometheus-prometheus-prometheus              Opaque                                1      37m
prometheus-k8s-prometheus-prometheus-prometheus-tls-assets   Opaque                                0      34m
```



`k8s-prometheus-grafana `即目标秘钥，展示其详情

```bash
$ kubectl get secrets -n monitoring k8s-prometheus-grafana -o yaml
apiVersion: v1
data:
  admin-password: b3BlcmF0b3ItYWRtaW4=
  admin-user: cm9vdA==
  ldap-toml: ""
kind: Secret
metadata:
  creationTimestamp: "2019-11-12T12:27:55Z"
  labels:
    app: grafana
    chart: grafana-4.0.2
    heritage: Tiller
    release: k8s-prometheus
  name: k8s-prometheus-grafana
  namespace: monitoring
  resourceVersion: "1033230"
  selfLink: /api/v1/namespaces/monitoring/secrets/k8s-prometheus-grafana
  uid: da7e86d0-0547-11ea-a5d2-000c298872e2
type: Opaque
```

秘钥默认通过`Base64` 加密，通过在线网站对该`Base64`解密即可得到用户名和密码



登录后可查看`Grafana`已经被配置好的多种可视化面板提供指标展示

![1573563198155](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573563198155.png)

点击左上角即可查看已经配置好的指标展示面板

![1573563283684](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573563283684.png)

Etcd监控面板

![1573563299117](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573563299117.png)

节点监控

![1573564479823](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573564479823.png)

计算资源监控

![1573564530686](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1573564530686.png)
