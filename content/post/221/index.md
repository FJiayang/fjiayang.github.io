{
  "title": "k8s共享存储以及Redis高可用集群快速搭建",
  "date": "2019-11-20T15:55:00+08:00",
  "lastmod": "2019-11-27T22:02:33+08:00",
  "typecho_cid": 221,
  "url": "/archives/221/",
  "comments": false,
  "draft": false,
  "slug": "221",
  "categories": [
    "学习"
  ],
  "tags": [
    "Redis",
    "docker",
    "Kubernetes"
  ],
  "image": "/images/recovered/96bce7011ae633f4c9aa.png",
  "math": false
}

## 介绍

 `StorageClass` 为管理员提供了描述存储 `"类"` 的方法。 不同的`类型`可能会映射到不同的服务质量等级或备份策略，通常由运维制定的任意策略 

 用户通过在 `PersistentVolumeClaim` 中包含存储类来请求动态供应的存储 ，动态卷供应的实现基于 `storage.k8s.io` API 组中的 `StorageClass` API 对象。 集群管理员可以根据需要定义多个 `StorageClass` 对象，每个对象指定一个*卷插件*（又名 *provisioner*）， 卷插件向卷供应商提供在创建卷时需要的数据卷信息及相关参数。

## 环境

Kubernetes：v1.14.0

Docker：17.03.1-ce

机器数：$3 \times master + 2 \times worker$

其中，master3、worker1、worker2都挂载了2块磁盘，非系统盘为纯净未分区磁盘，用于提供给GlusterFs管理

## 安装GlusterFs

在所有可能被调度到`pod`的节点安装`glusterfs`

```bash
$ yum install -y glusterfs glusterfs-fuse net-tools
```



## 启动GlusterFs与heketi

使用`yaml`文件启动`glusterfs`及其操作工具`heketi`

`glusterfs-daemonset.yaml`

```yaml
---
kind: DaemonSet
apiVersion: extensions/v1beta1
metadata:
  name: glusterfs
  labels:
    glusterfs: daemonset
  annotations:
    description: GlusterFS DaemonSet
    tags: glusterfs
spec:
  template:
    metadata:
      name: glusterfs
      labels:
        glusterfs: pod
        glusterfs-node: pod
    spec:
      nodeSelector:
        storagenode: glusterfs
      hostNetwork: true
      containers:
      - image: gluster/gluster-centos:latest
        imagePullPolicy: IfNotPresent
        name: glusterfs
        env:
        # alternative for /dev volumeMount to enable access to *all* devices
        - name: HOST_DEV_DIR
          value: "/mnt/host-dev"
        # set GLUSTER_BLOCKD_STATUS_PROBE_ENABLE to "1" so the
        # readiness/liveness probe validate gluster-blockd as well
        - name: GLUSTER_BLOCKD_STATUS_PROBE_ENABLE
          value: "1"
        - name: GB_GLFS_LRU_COUNT
          value: "15"
        - name: TCMU_LOGDIR
          value: "/var/log/glusterfs/gluster-block"
        resources:
          requests:
            memory: 100Mi
            cpu: 100m
        volumeMounts:
        - name: glusterfs-heketi
          mountPath: "/var/lib/heketi"
        - name: glusterfs-run
          mountPath: "/run"
        - name: glusterfs-lvm
          mountPath: "/run/lvm"
        - name: glusterfs-etc
          mountPath: "/etc/glusterfs"
        - name: glusterfs-logs
          mountPath: "/var/log/glusterfs"
        - name: glusterfs-config
          mountPath: "/var/lib/glusterd"
        - name: glusterfs-host-dev
          mountPath: "/mnt/host-dev"
        - name: glusterfs-misc
          mountPath: "/var/lib/misc/glusterfsd"
        - name: glusterfs-block-sys-class
          mountPath: "/sys/class"
        - name: glusterfs-block-sys-module
          mountPath: "/sys/module"
        - name: glusterfs-cgroup
          mountPath: "/sys/fs/cgroup"
          readOnly: true
        - name: glusterfs-ssl
          mountPath: "/etc/ssl"
          readOnly: true
        - name: kernel-modules
          mountPath: "/usr/lib/modules"
          readOnly: true
        securityContext:
          capabilities: {}
          privileged: true
        readinessProbe:
          timeoutSeconds: 3
          initialDelaySeconds: 40
          exec:
            command:
            - "/bin/bash"
            - "-c"
            - "if command -v /usr/local/bin/status-probe.sh; then /usr/local/bin/status-probe.sh readiness; else systemctl status glusterd.service; fi"
          periodSeconds: 25
          successThreshold: 1
          failureThreshold: 50
        livenessProbe:
          timeoutSeconds: 3
          initialDelaySeconds: 40
          exec:
            command:
            - "/bin/bash"
            - "-c"
            - "if command -v /usr/local/bin/status-probe.sh; then /usr/local/bin/status-probe.sh liveness; else systemctl status glusterd.service; fi"
          periodSeconds: 25
          successThreshold: 1
          failureThreshold: 50
      volumes:
      - name: glusterfs-heketi
        hostPath:
          path: "/var/lib/heketi"
      - name: glusterfs-run
      - name: glusterfs-lvm
        hostPath:
          path: "/run/lvm"
      - name: glusterfs-etc
        hostPath:
          path: "/etc/glusterfs"
      - name: glusterfs-logs
        hostPath:
          path: "/var/log/glusterfs"
      - name: glusterfs-config
        hostPath:
          path: "/var/lib/glusterd"
      - name: glusterfs-host-dev
        hostPath:
          path: "/dev"
      - name: glusterfs-misc
        hostPath:
          path: "/var/lib/misc/glusterfsd"
      - name: glusterfs-block-sys-class
        hostPath:
          path: "/sys/class"
      - name: glusterfs-block-sys-module
        hostPath:
          path: "/sys/module"
      - name: glusterfs-cgroup
        hostPath:
          path: "/sys/fs/cgroup"
      - name: glusterfs-ssl
        hostPath:
          path: "/etc/ssl"
      - name: kernel-modules
        hostPath:
          path: "/usr/lib/modules"
```



`heketi-security.yaml` 用户与权限相关

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: heketi-clusterrolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: heketi-clusterrole
subjects:
- kind: ServiceAccount
  name: heketi-service-account
  namespace: default

---

apiVersion: v1
kind: ServiceAccount
metadata:
  name: heketi-service-account
  namespace: default

---

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: heketi-clusterrole
rules:
- apiGroups:
  - ""
  resources:
  - pods
  - pods/status
  - pods/exec
  verbs:
  - get
  - list
  - watch
  - create
```



`heketi-deployment.yaml `启动服务并使用ingress四层反向代理

```yaml
kind: Service
apiVersion: v1
metadata:
  name: heketi
  labels: 
    glusterfs: heketi-service
    deploy-heketi: support
  annotations: 
    description: Exposes Heketi Service
spec:
  selector: 
    name: heketi
  ports:
  - name: heketi
    port: 80
    targetPort: 8080

---

apiVersion: v1
kind: ConfigMap
metadata:
  name: tcp-services
  namespace: ingress-nginx
data:
  "30001": default/heketi:80

---

kind: Deployment
apiVersion: extensions/v1beta1
metadata:
  name: heketi
  labels: 
    glusterfs: heketi-deployment
  annotations: 
    description: Defines how to deploy Heketi
spec:
  replicas: 1
  template:
    metadata:
      name: heketi
      labels: 
        name: heketi
        glusterfs: heketi-pod
    spec:
      serviceAccountName: heketi-service-account
      containers:
      - image: heketi/heketi:6
        imagePullPolicy: Always
        name: heketi
        env:
        - name: HEKETI_EXECUTOR
          value: "kubernetes"
        - name: HEKETI_DB_PATH
          value: "/var/lib/heketi/heketi.db"
        - name: HEKETI_FSTAB
          value: "/var/lib/heketi/fstab"
        - name: HEKETI_SNAPSHOT_LIMIT
          value: "14"
        - name: HEKETI_KUBE_GLUSTER_DAEMONSET
          value: "y"
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: db
          mountPath: /var/lib/heketi
        readinessProbe:
          timeoutSeconds: 3
          initialDelaySeconds: 3
          httpGet: 
            path: /hello
            port: 8080
        livenessProbe:
          timeoutSeconds: 3
          initialDelaySeconds: 30
          httpGet: 
            path: /hello
            port: 8080
      volumes:
      - name: db
        hostPath:
          path: "/heketi-data"
```



## GlusterFS初始化

### 创建

使用`heketi-cli`初始化`GlusterFS`节点，找到`heketi`容器并进入

```bash
$ docker ps | grep hek
9c92cf25e4bb        heketi/heketi@sha256:44058f20a91211234abc533c9b4b5c42764b8cd740e21d03377bee14ebca4497   "/usr/bin/heketi-s..."   About a minute ago   Up 58 seconds                           k8s_he eti_heketi-68f9dfdfbf-w4qrd_default_c0566bf2-09ff-11ea-b6ce-000c298872e2_0
ebafb92c4dc1        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1                                       "/pause"                 About a minute ago   Up About a minute                       k8s_POD_heketi-68f9dfdfbf-w4qrd_default_c0566bf2-09ff-11ea-b6ce-000c298872e2_0
$ docker exec -it 9c92 /bin/bash
```

配置容器本地环境变量，并配置节点`json`文件

```bash
$ export HEKETI_CLI_SERVER=http://localhost:8080
$ vi topology.json
```



主机名需要唯一并可以访问

```json
{
  "clusters": [
    {
      "nodes": [
        {
          "node": {
            "hostnames": {
              "manage": [
                "k8smaster3"
              ],
              "storage": [
                "192.168.1.17"
              ]
            },
            "zone": 1
          },
          "devices": ["/dev/sdb"]
        },
        {
          "node": {
            "hostnames": {
              "manage": [
                "k8sworker1"
              ],
              "storage": [
                "192.168.1.18"
              ]
            },
            "zone": 1
          },
          "devices": ["/dev/sdb"]
        },
        {
          "node": {
            "hostnames": {
              "manage": [
                "k8sworker2"
              ],
              "storage": [
                "192.168.1.19"
              ]
            },
            "zone": 1
          },
          "devices": ["/dev/sdb"]
        }
      ]
    }
  ]
}
```



装载`json`文件

```bash
$ heketi-cli topology load --json topology.json
        Found node k8smaster3 on cluster 84d8a3a128c43a2a7d6c36aa6833823f
                Adding device /dev/sdb ... OK
        Found node k8sworker1 on cluster 84d8a3a128c43a2a7d6c36aa6833823f
                Adding device /dev/sdb ... OK
        Found node k8sworker2 on cluster 84d8a3a128c43a2a7d6c36aa6833823f
                Adding device /dev/sdb ... OK
```



#### 可能出现的问题

##### 1. 无法初始化

报错信息为

```bash
Creating cluster ... ID: 84d8a3a128c43a2a7d6c36aa6833823f
        Allowing file volumes on cluster.
        Allowing block volumes on cluster.
        Creating node k8smaster3 ... ID: b97a53e296850d59bbdd4043b13ebf78
                Adding device /dev/sdb ... Unable to add device: Unable to execute command on glusterfs-4vgh8:   WARNING: Device /dev/sdb not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/centos/root not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/sda1 not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/centos/swap not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/sda2 not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/sdb not initialized in udev database even after waiting 10000000 microseconds.
  Can't initialize physical volume "/dev/sdb" of volume group "vg_9bc3bdaff53104647cd24abe9ca60745" without -ff
  /dev/sdb: physical volume not initialized.
        Creating node k8sworker1 ... ID: 3a57327dbd24d9aedcae01f72857ef5e
                Adding device /dev/sdb ... Unable to add device: Unable to execute command on glusterfs-wzcf8:   WARNING: Device /dev/sdb not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/centos/root not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/sda1 not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/centos/swap not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/sda2 not initialized in udev database even after waiting 10000000 microseconds.
  WARNING: Device /dev/sdb not initialized in udev database even after waiting 10000000 microseconds.
  Can't initialize physical volume "/dev/sdb" of volume group "vg_c6a688843cd06e333c83e56814c95c55" without -ff
  /dev/sdb: physical volume not initialized.
        Creating node k8sworker2 ... ID: 141f497c0797b26a22a31288ca97acf1
```

通过查阅资料，发现如下issue，官方提供磁盘擦除命令，执行后重新初始化节点

[deploy fails using k8s 1.7.1 when heketi tries to add devices to cluster #2 #279](https://github.com/gluster/gluster-kubernetes/issues/279)

> Destroy the heketi and GlusterFS pods, then try the following on each of the nodes:
>
> ```bash
> pvdisplay -C -o pv_name,vg_name # look for VGs on PVs on your target devices
> lvremove -ff <any VGs found above>
> vgremove -f <any VGs found above>
> pvremove -f <any PVs found above>
> wipefs -a <target device>
> ```
>
> Then try gk-deploy from the beginning again. Naturally, double-check that you're definitely removing something only on the target devices. :)



进入挂载磁盘节点，查看当前磁盘信息

```bash
$ lsblk
NAME            MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda               8:0    0   40G  0 disk
├─sda1            8:1    0    1G  0 part /boot
└─sda2            8:2    0   39G  0 part
  ├─centos-root 253:0    0   35G  0 lvm  /
  └─centos-swap 253:1    0    4G  0 lvm
sdb               8:16   0   40G  0 disk
sr0              11:0    1 1024M  0 rom
```

查看`pvs`名称

```bash
$ pvs
  PV         VG                                  Fmt  Attr PSize   PFree
  /dev/sda2  centos                              lvm2 a--  <39.00g     0
  /dev/sdb   vg_c6a688843cd06e333c83e56814c95c55 lvm2 a--   39.87g 39.87g
```



抹除磁盘

```bash
$ pvdisplay -C -o /dev/sdb,vg_c6a688843cd06e333c83e56814c95c55
$ lvremove -ff vg_c6a688843cd06e333c83e56814c95c55
$ vgremove -f vg_c6a688843cd06e333c83e56814c95c55
$ pvremove -f /dev/sdb
$ wipefs -a /dev/sdb
```

抹除后重新进入容器创建即可

### 验证

进入3个存储节点，检查创建情况，此处以`worker1`为例

```bash
$ netstat -ntlp | grep glusterd
tcp        0      0 0.0.0.0:24007           0.0.0.0:*               LISTEN      25997/glusterd
$ docker ps | grep glus
eae6ef1d4a37        22a008905c35                                                                                                                         "/usr/local/bin/up..."   31 minutes ago      Up 31 minutes                           k8s_glusterfs_glusterfs-wzcf8_default_940d0f57-09ff-11ea-b6ce-000c298872e2_0
858fd84edbc2        registry.cn-hangzhou.aliyuncs.com/imooc/pause:3.1                                                                                    "/pause"                 31 minutes ago      Up 31 minutes                           k8s_POD_glusterfs-wzcf8_default_940d0f57-09ff-11ea-b6ce-000c298872e2_0
$ docker exec -it eae6 /bin/bash
$ gluster pool list
UUID                                    Hostname        State
6d4eda3d-a7c2-4e27-999c-972106c54c3d    k8smaster3      Connected
56a6e1d4-46db-4ff2-83eb-39c313bc9197    192.168.1.19    Connected
a8ac96bd-b596-433c-8e2a-e3a97873886b    localhost       Connected
```



## 创建storage-class

定义`StorageClass`，通过访问`ingress-nginx`四层代理暴露的端口管理`glusterfs`

`glusterfs-storage-class.yaml`

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: glusterfs-storage-class
provisioner: kubernetes.io/glusterfs
parameters:
  resturl: "http://192.168.1.16:30001"
  restauthenabled: "false"
```



## 创建PVC

创建PVC， 可以被单个节点映射为`ReadWriteOnce`,或者多个节点映射为`ReadOnlyMany`,但不能同时使用这两种方式来映射。 

`glusterfs-pvc.yaml`

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: glusterfs-pvc
spec:
  storageClassName: glusterfs-storage-class
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

检查`pvc`，可见已经是已绑定(`Bound`)状态

```bash
$ kubectl get pvc
NAME            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS              AGE
glusterfs-pvc   Bound    pvc-7c4f94cd-0a04-11ea-b6ce-000c298872e2   1Gi        RWO            glusterfs-storage-class   128m
```



## 基于Helm安装Redis-HA

访问`charts`官方仓库：<https://github.com/helm/charts>

在stable目录下找到`redis-ha`目录，修改`values.yaml`文件如下，主要配置存储类为`storageClass: glusterfs-storage-class`，然后修改用户名和密码等相关信息即可



```yaml
image:
  repository: redis
  tag: 5.0.5-alpine
  pullPolicy: IfNotPresent
replicas: 3
labels: {}
configure-service-account/
serviceAccount:
  create: truetemplate
Automatically proxies to Redis master.
haproxy:
  enabled: false
  readOnly:
    enabled: false
    port: 6380
  replicas: 1
  image:
    repository: haproxy
    tag: 2.0.4
    pullPolicy: IfNotPresent
  annotations: {}
  resources: {}
  service:
    type: ClusterIP
    loadBalancerIP:
    annotations: {}
  serviceAccount:
    create: true
  exporter:
    image:
      repository: quay.azk8s.cn/prometheus/haproxy-exporter
      tag: v0.9.0
    enabled: false
    port: 9101
  init:
    resources: {}
  timeout:
    connect: 4s
    server: 30s
    client: 30s
  securityContext:
    runAsUser: 1000
    fsGroup: 1000
    runAsNonRoot: true
rbac:
  create: true
sysctlImage:
  enabled: false
  command: []
  registry: docker.io
  repository: busybox
  tag: 1.31.1
  pullPolicy: Always
  mountHostSys: false
configure-multiple-schedulers/
redis:
  port: 6379
  masterGroupName: mymaster
  config:
    min-replicas-to-write: 1unlimited.instance. Default is volatile-lru.with a new slave. The only way to prevent this is to enable diskless replication.
    save: "900 1"the disk as intermediate storage. Default is false.
    repl-diskless-sync: "yes"
    rdbcompression: "yes"
    rdbchecksum: "yes"
  resources: {}

sentinel:
  port: 26379
  quorum: 2
  config:
    down-after-milliseconds: 10000
    failover-timeout: 180000
    parallel-syncs: 5
  resources: {}

securityContext:
  runAsUser: 1000
  fsGroup: 1000
  runAsNonRoot: true
assign-pod-node/#nodeselectorassign-pod-node/#taints-and-tolerations-beta-featureassign-pod-node/#affinity-and-anti-affinity
nodeSelector: {}
requiredDuringSchedulingIgnoredDuringExecution as opposed to preferred.assign-pod-node/#inter-pod-affinity-and-anti-affinity-beta-feature
hardAntiAffinity: true
additionalAffinities: {}
affinity: |
exporter:
  enabled: true
  image: oliver006/redis_exporter
  tag: v0.31.0
  pullPolicy: IfNotPresent
  port: 9121
  scrapePath: /metrics
  resources: {}
  extraArgs: {}
  serviceMonitor:
    enabled: falsePrometheus Operator
podDisruptionBudget: {}
auth: true
redisPassword: password
authKey: auth
persistentVolume:
  enabled: true
  storageClass: glusterfs-storage-class
  accessModes:
    - ReadWriteOnce
  size: 100Mi
  annotations: {}
init:
  resources: {}

hostPath:
  chown: true
```

从修改后的本地文件安装`redis-ha`

```bash
$ helm install /root/redis-ha/ --name k8s-redis-ha --namespace env-prod
NAME:   k8s-redis-ha
LAST DEPLOYED: Mon Nov 18 22:13:20 2019
NAMESPACE: env-prod
STATUS: DEPLOYED

RESOURCES:
==> v1/ConfigMap
NAME                    DATA  AGE
k8s-redis-ha-configmap  4     1s

==> v1/Pod(related)
NAME                   READY  STATUS   RESTARTS  AGE
k8s-redis-ha-server-0  0/3    Pending  0         0s

==> v1/Role
NAME          AGE
k8s-redis-ha  1s

==> v1/RoleBinding
NAME          AGE
k8s-redis-ha  1s

==> v1/Secret
NAME          TYPE    DATA  AGE
k8s-redis-ha  Opaque  1     1s

==> v1/Service
NAME                     TYPE       CLUSTER-IP      EXTERNAL-IP  PORT(S)                      AGE
k8s-redis-ha             ClusterIP  None            <none>       6379/TCP,26379/TCP,9121/TCP  1s
k8s-redis-ha-announce-0  ClusterIP  10.101.55.132   <none>       6379/TCP,26379/TCP,9121/TCP  1s
k8s-redis-ha-announce-1  ClusterIP  10.98.159.185   <none>       6379/TCP,26379/TCP,9121/TCP  1s
k8s-redis-ha-announce-2  ClusterIP  10.102.215.171  <none>       6379/TCP,26379/TCP,9121/TCP  1s

==> v1/ServiceAccount
NAME          SECRETS  AGE
k8s-redis-ha  1        1s

==> v1/StatefulSet
NAME                 READY  AGE
k8s-redis-ha-server  0/3    1s


NOTES:
Redis can be accessed via port 6379 and Sentinel can be accessed via port 26379 on the following DNS name from within your cluster:
k8s-redis-ha.env-prod.svc.cluster.local

To connect to your Redis server:
1. To retrieve the redis password:
   echo $(kubectl get secret k8s-redis-ha -o "jsonpath={.data['auth']}" | base64 --decode)

2. Connect to the Redis master pod that you can use as a client. By default the k8s-redis-ha-server-0 pod is configured as the master:

   kubectl exec -it k8s-redis-ha-server-0 sh -n env-prod

3. Connect using the Redis CLI (inside container):

   redis-cli -a <REDIS-PASS-FROM-SECRET>

```



检查`pvc`创建情况

```bash
$ kubectl get pvc -n env-prod
NAME                         STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS              AGE
data-k8s-redis-ha-server-0   Bound    pvc-9348a01f-0a0d-11ea-b6ce-000c298872e2   1Gi        RWO            glusterfs-storage-class   62m
data-k8s-redis-ha-server-1   Bound    pvc-9a8defcf-0a0d-11ea-b6ce-000c298872e2   1Gi        RWO            glusterfs-storage-class   62m
data-k8s-redis-ha-server-2   Bound    pvc-a1975bf8-0a0d-11ea-b6ce-000c298872e2   1Gi        RWO            glusterfs-storage-class   62m
```

检查`pv`

```bash
$ kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                 STORAGECLASS              REASON   AGE
pvc-7c4f94cd-0a04-11ea-b6ce-000c298872e2   1Gi        RWO            Delete           Bound    default/glusterfs-pvc                 glusterfs-storage-class            128m
pvc-9348a01f-0a0d-11ea-b6ce-000c298872e2   1Gi        RWO            Delete           Bound    env-prod/data-k8s-redis-ha-server-0   glusterfs-storage-class            63m
pvc-9a8defcf-0a0d-11ea-b6ce-000c298872e2   1Gi        RWO            Delete           Bound    env-prod/data-k8s-redis-ha-server-1   glusterfs-storage-class            63m
pvc-a1975bf8-0a0d-11ea-b6ce-000c298872e2   1Gi        RWO            Delete           Bound    env-prod/data-k8s-redis-ha-server-2   glusterfs-storage-class            63m
```



配置`ingress-nginx`四层反向代理

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tcp-services
  namespace: ingress-nginx
data:
  "30001": default/heketi:80
  "30002": env-prod/k8s-redis-ha:6379
  "30003": env-prod/k8s-redis-ha:26379
```



使用`redis`客户端连接即可
