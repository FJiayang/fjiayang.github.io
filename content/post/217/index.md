{
  "title": "Kubernetes 集群搭建",
  "date": "2019-10-20T12:31:00+08:00",
  "lastmod": "2019-11-27T22:11:04+08:00",
  "typecho_cid": 217,
  "url": "/archives/217/",
  "comments": false,
  "draft": false,
  "slug": "217",
  "categories": [
    "服务器",
    "学习"
  ],
  "tags": [
    "集群",
    "Kubernetes",
    "Vagrant"
  ],
  "image": "https://s2.ax1x.com/2019/11/27/QCRTo9.jpg",
  "math": false
}

## 搭建方法分类

如果是搭建`Kubernetes`的学习环境，则可以直接使用`minikube`快速搭建单节点的`Kubernetes`环境，官方推荐使用kubeadm搭建`Kubernetes`集群生产环境

但kubeadm需要连接谷歌容器仓库获取镜像，在网络受限的情况下无法搭建成功，故有两种搭建方法：

- 服务器使用代理，代理所有的`http`和`https`连接，可以自由访问任意地址
- 使用阿里云镜像地址

本次采用第二种方式进行搭建

## 环境准备

本次宿主机为`CentOS 7`，结合3台`virtual box`虚拟机模拟集群环境，虚拟机使用`Vagrant`进行管理，`vagrant`安装比较简单，此处不再赘述

宿主机配置：

- CPU：4C
- RAM：8G



## 虚拟机配置

由于网络受限，`vagrant`默认拉取的操作系统文件地址不可访问，需要自行从官方下载镜像或者使用代理下载镜像，此处对此操作也不再赘述

三台虚拟机配置文件

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.6.0"

boxes = [
    {
        :name => "k8s-master",
        :eth1 => "192.168.205.120",
        :mem => "2048",
        :cpu => "2"
    },
    {
        :name => "k8s-node1",
        :eth1 => "192.168.205.121",
        :mem => "2048",
        :cpu => "1"
    },
    {
        :name => "k8s-node2",
        :eth1 => "192.168.205.122",
        :mem => "2048",
        :cpu => "1"
    }

]

Vagrant.configure(2) do |config|

  config.vm.box = "centos/7"
  boxes.each do |opts|
    config.vm.define opts[:name] do |config|
      config.vm.hostname = opts[:name]
      config.vm.provider "vmware_fusion" do |v|
        v.vmx["memsize"] = opts[:mem]
        v.vmx["numvcpus"] = opts[:cpu]
      end
      config.vm.provider "virtualbox" do |v|
        v.customize ["modifyvm", :id, "--memory", opts[:mem]]
        v.customize ["modifyvm", :id, "--cpus", opts[:cpu]]
      end
      config.vm.network :private_network, ip: opts[:eth1]
    end
  end
  config.vm.provision "shell", privileged: true, path: "./setup.sh"
end
```



所有虚拟机启动后都会执行`./setup.sh`脚本配置基础环境，脚本内容如下

```bash
#/bin/sh

sudo yum install -y vim telnet bind-utils wget yum-utils

sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
sudo yum -y install docker-ce-18.09.8 docker-ce-cli-18.09.8 containerd.io

if [ ! $(getent group docker) ];
then 
    sudo groupadd docker;
else
    echo "docker user group already exists"
fi

sudo gpasswd -a $USER docker
sudo systemctl restart docker

# open password auth for backup if ssh key doesn't work, bydefault, username=vagrant password=vagrant
sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sudo systemctl restart sshd

sudomkdir /etc/yum.repos.d/bak && mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/bak
sudowget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.cloud.tencent.com/repo/centos7_base.repo
sudowget -O /etc/yum.repos.d/epel.repo http://mirrors.cloud.tencent.com/repo/epel-7.repo

yum clean all && yum makecache

sudo bash -c 'cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF'

sudo wget https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo -O /etc/yum.repos.d/docker-ce.repo
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://clayphwh.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

sudo setenforce 0

sudo yum install -y kubelet kubeadm kubectl

sudo bash -c 'cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward=1
EOF'
sudo sysctl --system

sudo systemctl stop firewalld
sudo systemctl disable firewalld
sudo swapoff -a

sudo systemctl enable docker.service
sudo systemctl enable kubelet.service
```



脚本内已将K8S镜像均配置为阿里云镜像仓库，并配置了阿里云容器加速服务地址，更便于在国内拉取镜像



## 启动虚拟机

使用命令启动虚拟机

```bash
$ vagrant up
```



启动需要较长时间，若出现大量超时也请耐心等待

```bash
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
 * base: mirrors.aliyun.com
 * extras: mirrors.163.com
 * updates: mirrors.163.com
http://vault.centos.org/7.1.1503/os/x86_64/repodata/0e6e90965f55146ba5025ea450f822d1bb0267d0299ef64dd4365825e6bad995-c7-x86_64-comps.xml.gz: [Errno 12] Timeout on http://vault.centos.org/7.1.1503/os/x86_64/repodata/0e6e90965f55146ba5025ea450f822d1bb0267d0299ef64dd4365825e6bad995-c7-x86_64-comps.xml.gz: (28, 'Operation too slow. Less than 1000 bytes/sec transferred the last 30 seconds')
Trying other mirror.
http://vault.centos.org/7.1.1503/updates/x86_64/repodata/93b71f445d2ec2138d28152612f4fb29c8e76ee31f2666b964d88249b4e0a955-primary.sqlite.bz2: [Errno 12] Timeout on http://vault.centos.org/7.1.1503/updates/x86_64/repodata/93b71f445d2ec2138d28152612f4fb29c8e76ee31f2666b964d88249b4e0a955-primary.sqlite.bz2: (28, 'Operation too slow. Less than 1000 bytes/sec transferred the last 30 seconds')
Trying other mirror.
http://vault.centos.org/7.2.1511/os/x86_64/repodata/c6411f1cc8a000ed2b651b49134631d279abba1ec1f78e5dcca79a52d8c1eada-primary.sqlite.bz2: [Errno 12] Timeout on http://vault.centos.org/7.2.1511/os/x86_64/repodata/c6411f1cc8a000ed2b651b49134631d279abba1ec1f78e5dcca79a52d8c1eada-primary.sqlite.bz2: (28, 'Operation too slow. Less than 1000 bytes/sec transferred the last 30 seconds')
Trying other mirror.
...
```



启动完成后通过命令查看虚拟机状态

```bash
$ vagrant status
Current machine states:

k8s-master                running (virtualbox)
k8s-node1                 running (virtualbox)
k8s-node2                 running (virtualbox)

This environment represents multiple VMs. The VMs are all listed
above with their current state. For more information about a specific
VM, run `vagrant status NAME`.
```



## K8S master节点初始化

进入主节点，查看环境是否已经配置完成

```bash
$ vagrant ssh k8s-master
```



执行以下三条语句查看是否有预期输出

```bash
[vagrant@k8s-master ~]$ sudo which kubeadm
/bin/kubeadm
[vagrant@k8s-master ~]$ sudo which kubelet
/bin/kubelet
[vagrant@k8s-master ~]$ sudo which kubectl
/bin/kubectl
[vagrant@k8s-master ~]$ sudo docker version
Client:
 Version:           18.09.8
 API version:       1.39
 Go version:        go1.10.8
 Git commit:        0dd43dd87f
 Built:             Wed Jul 17 17:40:31 2019
 OS/Arch:           linux/amd64
 Experimental:      false

Server: Docker Engine - Community
 Engine:
  Version:          18.09.8
  API version:      1.39 (minimum version 1.12)
  Go version:       go1.10.8
  Git commit:       0dd43dd
  Built:            Wed Jul 17 17:10:42 2019
  OS/Arch:          linux/amd64
  Experimental:     false
```



使用初始化命令，并指定拉取镜像地址为阿里云地址，同时指定容器网络地址和注册中心广播地址

```bash
$ sudo kubeadm init --pod-network-cidr 172.100.0.0/16 --image-repository registry.aliyuncs.com/google_containers --apiserver-advertise-address 192.168.205.120
```



输出如下即初始化完成

```bash
$ sudo kubeadm init --pod-network-cidr 172.100.0.0/16 --image-repository registry.aliyuncs.com/google_containers --apiserver-advertise-address 192.168.205.120
W1020 01:31:27.560129   20473 version.go:101] could not fetch a `Kubernetes`version from the internet: unable to get URL "https://dl.k8s.io/release/stable-1.txt": Get https://dl.k8s.io/release/stable-1.txt: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
W1020 01:31:27.560713   20473 version.go:102] falling back to the local client version: v1.16.2
[init] Using `Kubernetes`version: v1.16.2
[preflight] Running pre-flight checks
        [WARNING IsDockerSystemdCheck]: detected "cgroupfs" as the Docker cgroup driver. The recommended driver is "systemd". Please follow the guide at https://kubernetes.io/docs/setup/cri/
[preflight] Pulling images required for setting up a `Kubernetes`cluster
[preflight] This might take a minute or two, depending on the speed of your internet connection
[preflight] You can also perform this action in beforehand using 'kubeadm config images pull'
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Activating the kubelet service
[certs] Using certificateDir folder "/etc/kubernetes/pki"
[certs] Generating "ca" certificate and key
[certs] Generating "apiserver" certificate and key
[certs] apiserver serving cert is signed for DNS names [k8s-master `kubernetes`kubernetes.default kubernetes.default.svc kubernetes.default.svc.cluster.local] and IPs [10.96.0.1 192.168.205.120]
[certs] Generating "apiserver-kubelet-client" certificate and key
[certs] Generating "front-proxy-ca" certificate and key
[certs] Generating "front-proxy-client" certificate and key
[certs] Generating "etcd/ca" certificate and key
[certs] Generating "etcd/server" certificate and key
[certs] etcd/server serving cert is signed for DNS names [k8s-master localhost] and IPs [192.168.205.120 127.0.0.1 ::1]
[certs] Generating "etcd/peer" certificate and key
[certs] etcd/peer serving cert is signed for DNS names [k8s-master localhost] and IPs [192.168.205.120 127.0.0.1 ::1]
[certs] Generating "etcd/healthcheck-client" certificate and key
[certs] Generating "apiserver-etcd-client" certificate and key
[certs] Generating "sa" key and public key
[kubeconfig] Using kubeconfig folder "/etc/kubernetes"
[kubeconfig] Writing "admin.conf" kubeconfig file
[kubeconfig] Writing "kubelet.conf" kubeconfig file
[kubeconfig] Writing "controller-manager.conf" kubeconfig file
[kubeconfig] Writing "scheduler.conf" kubeconfig file
[control-plane] Using manifest folder "/etc/kubernetes/manifests"
[control-plane] Creating static Pod manifest for "kube-apiserver"
[control-plane] Creating static Pod manifest for "kube-controller-manager"
[control-plane] Creating static Pod manifest for "kube-scheduler"
[etcd] Creating static Pod manifest for local etcd in "/etc/kubernetes/manifests"
[wait-control-plane] Waiting for the kubelet to boot up the control plane as static Pods from directory "/etc/kubernetes/manifests". This can take up to 4m0s
[kubelet-check] Initial timeout of 40s passed.
[apiclient] All control plane components are healthy after 59.511578 seconds
[upload-config] Storing the configuration used in ConfigMap "kubeadm-config" in the "kube-system" Namespace
[kubelet] Creating a ConfigMap "kubelet-config-1.16" in namespace kube-system with the configuration for the kubelets in the cluster
[upload-certs] Skipping phase. Please see --upload-certs
[mark-control-plane] Marking the node k8s-master as control-plane by adding the label "node-role.kubernetes.io/master=''"
[mark-control-plane] Marking the node k8s-master as control-plane by adding the taints [node-role.kubernetes.io/master:NoSchedule]
[bootstrap-token] Using token: rod570.p67pymzbil4m6u8d
[bootstrap-token] Configuring bootstrap tokens, cluster-info ConfigMap, RBAC Roles
[bootstrap-token] configured RBAC rules to allow Node Bootstrap tokens to post CSRs in order for nodes to get long term certificate credentials
[bootstrap-token] configured RBAC rules to allow the csrapprover controller automatically approve CSRs from a Node Bootstrap Token
[bootstrap-token] configured RBAC rules to allow certificate rotation for all node client certificates in the cluster
[bootstrap-token] Creating the "cluster-info" ConfigMap in the "kube-public" namespace
[addons] Applied essential addon: CoreDNS
[addons] Applied essential addon: kube-proxy

Your `Kubernetes`control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.205.120:6443 --token rod570.p67pymzbil4m6u8d \
    --discovery-token-ca-cert-hash sha256:8f4cb9d555c78d58befeb3cfa3f7537989aa599e53e4f1bae929d8cc7afd1476
```



## kubectl 配置

拷贝kubectl配置

```bash
$ rm -rf ~/.kube
$ mkdir -p $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```



若不配置直接使用则报无法连接错误

```bash
[vagrant@k8s-master ~]$ kubectl get pod --all-namespaces
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```



此时使用`kubectl`可查看k8s容器运行情况，输出如下则为初始化成功，启动由于未配置网络插件，故`coredns`一直处于`Pending`状态

```bash
[vagrant@k8s-master ~]$ kubectl get pod --all-namespaces
NAMESPACE     NAME                                 READY   STATUS    RESTARTS   AGE
kube-system   coredns-58cc8c89f4-c297b             0/1     Pending   0          81s
kube-system   coredns-58cc8c89f4-spzhj             0/1     Pending   0          81s
kube-system   etcd-k8s-master                      1/1     Running   0          39s
kube-system   kube-apiserver-k8s-master            1/1     Running   0          49s
kube-system   kube-controller-manager-k8s-master   1/1     Running   0          40s
kube-system   kube-proxy-xlb62                     1/1     Running   0          81s
kube-system   kube-scheduler-k8s-master            1/1     Running   0          51s
```



## 安装网络插件

网络插件有多个可选，可通过[官网](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/#pod-network)查看，此处选择安装`flannel` CNI网络插件

> For `flannel` to work correctly, you must pass `--pod-network-cidr=10.244.0.0/16` to `kubeadm init`.
>
> Set `/proc/sys/net/bridge/bridge-nf-call-iptables` to `1` by running `sysctl net.bridge.bridge-nf-call-iptables=1` to pass bridged IPv4 traffic to iptables’ chains. This is a requirement for some CNI plugins to work, for more information please see [here](https://kubernetes.io/docs/concepts/cluster-administration/network-plugins/#network-plugin-requirements).
>
> Make sure that your firewall rules allow UDP ports 8285 and 8472 traffic for all hosts participating in the overlay network. see [here ](https://coreos.com/flannel/docs/latest/troubleshooting.html#firewalls).
>
> Note that `flannel` works on `amd64`, `arm`, `arm64`, `ppc64le` and `s390x` under Linux. Windows (`amd64`) is claimed as supported in v0.11.0 but the usage is undocumented.
>
> ```shell
> kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml
> ```
>
> For more information about `flannel`, see [the CoreOS flannel repository on GitHub ](https://github.com/coreos/flannel).



相关的网络配置已在脚本中写入，此时直接执行yml脚本即可

```bash
$ kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml
```



再次查看容器运行情况，所有容器均已运行，则master节点配置完成

```bash
[vagrant@k8s-master ~]$ kubectl get pod --all-namespaces
NAMESPACE     NAME                                 READY   STATUS    RESTARTS   AGE
kube-system   coredns-58cc8c89f4-c297b             1/1     Running   0          5m17s
kube-system   coredns-58cc8c89f4-spzhj             1/1     Running   0          5m17s
kube-system   etcd-k8s-master                      1/1     Running   0          4m35s
kube-system   kube-apiserver-k8s-master            1/1     Running   0          4m45s
kube-system   kube-controller-manager-k8s-master   1/1     Running   0          4m36s
kube-system   kube-flannel-ds-amd64-6rchg          1/1     Running   0          3m50s
kube-system   kube-proxy-xlb62                     1/1     Running   0          5m17s
kube-system   kube-scheduler-k8s-master            1/1     Running   0          4m47s
```



## 配置worker节点

以`k8s-node1`为例，执行`master`初始化时提供的脚本即可加入`k8s`集群，输出如下则加入成功

```bash
[vagrant@k8s-node1 ~]$ sudo kubeadm join 192.168.205.120:6443 --token 8ry5oo.y48ksgurn103zq4h \
>     --discovery-token-ca-cert-hash sha256:ead07352591500c2cfe3321bf87d2e068790e16f2a7e0cc23541c864d24006d4
[preflight] Running pre-flight checks
        [WARNING IsDockerSystemdCheck]: detected "cgroupfs" as the Docker cgroup driver. The recommended driver is "systemd". Please follow the guide at https://kubernetes.io/docs/setup/cri/
[preflight] Reading configuration from the cluster...
[preflight] FYI: You can look at this config file with 'kubectl -n kube-system get cm kubeadm-config -oyaml'
[kubelet-start] Downloading configuration for the kubelet from the "kubelet-config-1.16" ConfigMap in the kube-system namespace
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[kubelet-start] Writing kubelet environment file with flags to file "/var/lib/kubelet/kubeadm-flags.env"
[kubelet-start] Activating the kubelet service
[kubelet-start] Waiting for the kubelet to perform the TLS Bootstrap...

This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.

Run 'kubectl get nodes' on the control-plane to see this node join the cluster.
```



稍等片刻进入`master`节点查看容器运行情况，会发现多了几个网络容器，属于预期情况

```bash
[vagrant@k8s-master ~]$ kubectl get pod --all-namespaces
NAMESPACE     NAME                                 READY   STATUS    RESTARTS   AGE
kube-system   coredns-58cc8c89f4-c297b             1/1     Running   0          6m28s
kube-system   coredns-58cc8c89f4-spzhj             1/1     Running   0          6m28s
kube-system   etcd-k8s-master                      1/1     Running   0          5m46s
kube-system   kube-apiserver-k8s-master            1/1     Running   0          5m56s
kube-system   kube-controller-manager-k8s-master   1/1     Running   0          5m47s
kube-system   kube-flannel-ds-amd64-6fwg5          1/1     Running   0          49s
kube-system   kube-flannel-ds-amd64-6rchg          1/1     Running   0          5m1s
kube-system   kube-flannel-ds-amd64-z4plh          1/1     Running   0          43s
kube-system   kube-proxy-cdcs4                     1/1     Running   0          49s
kube-system   kube-proxy-nlmbb                     1/1     Running   0          43s
kube-system   kube-proxy-xlb62                     1/1     Running   0          6m28s
kube-system   kube-scheduler-k8s-master            1/1     Running   0          5m58s
```



## 集群验证

在`master`节点中启动`nginx`容器测试集群情况

```bash
$ kubectl create deployment nginx --image=nginx
```



稍等片刻，输出如下则集群正常运行，`k8s`集群配置完成

```bash
[vagrant@k8s-master ~]$ kubectl get pod --all-namespaces
NAMESPACE     NAME                                 READY   STATUS    RESTARTS   AGE
default       nginx-86c57db685-2gkxm               1/1     Running   0          58s
kube-system   coredns-58cc8c89f4-c297b             1/1     Running   0          7m46s
kube-system   coredns-58cc8c89f4-spzhj             1/1     Running   0          7m46s
kube-system   etcd-k8s-master                      1/1     Running   0          7m4s
kube-system   kube-apiserver-k8s-master            1/1     Running   0          7m14s
kube-system   kube-controller-manager-k8s-master   1/1     Running   0          7m5s
kube-system   kube-flannel-ds-amd64-6fwg5          1/1     Running   0          2m7s
kube-system   kube-flannel-ds-amd64-6rchg          1/1     Running   0          6m19s
kube-system   kube-flannel-ds-amd64-z4plh          1/1     Running   0          2m1s
kube-system   kube-proxy-cdcs4                     1/1     Running   0          2m7s
kube-system   kube-proxy-nlmbb                     1/1     Running   0          2m1s
kube-system   kube-proxy-xlb62                     1/1     Running   0          7m46s
kube-system   kube-scheduler-k8s-master            1/1     Running   0          7m16s
```
