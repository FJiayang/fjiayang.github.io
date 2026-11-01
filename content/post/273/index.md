{
  "title": "Kubesphere落地DevOps",
  "date": "2021-06-19T22:16:00+08:00",
  "lastmod": "2024-08-04T19:34:53+08:00",
  "typecho_cid": 273,
  "url": "/archives/273/",
  "comments": false,
  "draft": false,
  "slug": "273",
  "categories": [
    "服务器",
    "学习"
  ],
  "tags": [
    "docker",
    "CICD",
    "DevOps",
    "Kubernetes",
    "kubesphere"
  ],
  "math": true
}

## 创建企业空间

创建一个企业空间和一个帐户 (`project-admin`)，必须邀请该帐户至该企业空间并赋予 `workspace-self-provisioner` 角色。

![1623583200028](/images/recovered/ea9bbb7e31d4a35158a8.png)



进入企业空间，切换到DevOps工程，点击创建

![1623583256804](/images/recovered/dced84112780ed526272.png)



创建工程

![1623583296345](/images/recovered/2eefdee1b3fbb4fb8e72.png)



## 安装helm

```shell
$ curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```



### 找不到环境变量报错

安装helm遇到报错

```shell
$ curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
unset -f pathmunge
                                 Dload  Upload   Total   Spent    Left  Speed
100 11248  100 11248    0     0  61543      0 --:--:-- --:--:-- --:--:-- 61802
Helm v3.6.0 is available. Changing from version v3.2.1.
Downloading https://get.helm.sh/helm-v3.6.0-linux-amd64.tar.gz
Verifying checksum... Done.
Preparing to install helm into /usr/local/bin
helm installed into /usr/local/bin/helm
helm not found. Is /usr/local/bin on your $PATH?
Failed to install helm
        For support, go to https://github.com/helm/helm.
```



则需要配置环境变量

```shell
$ vi /etc/profile
# 添加配置
export PATH=/usr/local/bin:$PATH

$ source /etc/profile
```



验证

```shell
$ helm version
version.BuildInfo{Version:"v3.6.0", GitCommit:"7f2df6467771a75f5646b7f12afb408590ed1755", GitTreeState:"clean", GoVersion:"go1.16.3"}
```



## 安装SonarQube

执行以下命令安装 SonarQube 服务器

```shell
$ helm upgrade --install sonarqube sonarqube --repo https://charts.kubesphere.io/main -n kubesphere-devops-system  --create-namespace --set service.type=NodePort
```

输出

![1623589400716](/images/recovered/746cefabe4b1d8f534e7.png)



执行以下命令以获取 SonarQube NodePort

```shell
$ export NODE_PORT=$(kubectl get --namespace kubesphere-devops-system -o jsonpath="{.spec.ports[0].nodePort}" services sonarqube-sonarqube)
$ export NODE_IP=$(kubectl get nodes --namespace kubesphere-devops-system -o jsonpath="{.items[0].status.addresses[0].address}")
$ echo http://$NODE_IP:$NODE_PORT
```

输出

![1623589466239](/images/recovered/930b4d1c1f4fbad23a38.png)



此时可在kubesphere控制台中看到sonar服务

![1623589521856](/images/recovered/e160945c268d616ce126.png)



## 配置 SonarQube 服务器

访问地址，点击右上角的 **Log in**，然后使用默认帐户 `admin/admin` 登录。

![1623589484956](/images/recovered/318f45c8e4470dac1fb4.png)



### 创建 SonarQube 管理员令牌 (Token)

点击右上角字母 **A**，然后从菜单中选择 **My Account** 以转到 **Profile** 页面。

![1623589658291](/images/recovered/1057ab3b055d13c8ccf7.png)



生成token

![1623589677983](/images/recovered/15351033dbc2e519bce5.png)



### 创建 Webhook 服务器

执行以下命令获取 SonarQube Webhook 的地址。

```shell
$ export NODE_PORT=$(kubectl get --namespace kubesphere-devops-system -o jsonpath="{.spec.ports[0].nodePort}" services ks-jenkins)
$ export NODE_IP=$(kubectl get nodes --namespace kubesphere-devops-system -o jsonpath="{.items[0].status.addresses[0].address}")
$ echo http://$NODE_IP:$NODE_PORT/sonarqube-webhook/
```

输出

![1623589732948](/images/recovered/6150dcefd7cc296e237b.png)



依次点击 **Administration**、**Configuration** 和 **Webhooks** 创建一个 Webhook。

![1623589828830](/images/recovered/5d85d8f656afd2acd16e.png)



点击 **Create**

由于webhook都通过内部网络调用，故可以使用内部网络地址

![1623589887169](/images/recovered/8d5a1ac24ac1f38e34a5.png)



### 将 SonarQube 配置添加到 ks-installer

执行以下命令编辑 `ks-installer`

```shell
$ kubectl edit cc -n kubesphere-system ks-installer
```



搜寻至 `devops`。添加字段 `sonarqube` 并在其下方指定 `externalSonarUrl` 和 `externalSonarToken`。

```yaml
  devops:
    enabled: true
    jenkinsJavaOpts_MaxRAM: 2g
    jenkinsJavaOpts_Xms: 512m
    jenkinsJavaOpts_Xmx: 512m
    jenkinsMemoryLim: 2Gi
    jenkinsMemoryReq: 1500Mi
    jenkinsVolumeSize: 8Gi
    sonarqube:
      externalSonarUrl: http://10.170.0.5:32108
      externalSonarToken: c6a6e2e15a9d52e30b744df0eef4c639bbea88a1
```

完成操作后保存此文件。



### 将 SonarQube 服务器添加至 Jenkins

执行以下命令获取 Jenkins 的地址。

```shell
$ export NODE_PORT=$(kubectl get --namespace kubesphere-devops-system -o jsonpath="{.spec.ports[0].nodePort}" services ks-jenkins)
$ export NODE_IP=$(kubectl get nodes --namespace kubesphere-devops-system -o jsonpath="{.items[0].status.addresses[0].address}")
$ echo http://$NODE_IP:$NODE_PORT
```

输出

![1623590243987](/images/recovered/577c6ee53476f48c2b4c.png)



使用地址 `http://{$Public IP}:30180` 访问 Jenkins。安装 KubeSphere 时，默认情况下也会安装 Jenkins 仪表板。此外，Jenkins 还配置有 KubeSphere LDAP，这意味着您可以直接使用 KubeSphere 帐户（例如 `admin/P@88w0rd`）登录 Jenkins。

![1623590218736](/images/recovered/47030135d3fd24f33d91.png)



使用kubesphere admin账户登录

![1623590300294](/images/recovered/0340063ee1866b31dd7c.png)



前往**系统管理**下的 **Manage Credentials** 并点击 **Stores scoped to Jenkins** 下的 **Jenkins**，再点击**全局凭据 (unrestricted)**

![1623590813853](/images/recovered/25a1a46e71332fe1397e.png)



点击左侧导航栏的**添加凭据**，用 SonarQube 管理员令牌添加凭证

![1623590901716](/images/recovered/cac331a35ea962c12d1e.png)





点击左侧的**系统管理**，向下翻页找到并点击**系统配置**。

![1623590362224](/images/recovered/6a59e0d9670e2038d606.png)



搜寻到 **SonarQube servers**，然后点击 **Add SonarQube**。

![1623590399204](/images/recovered/10a406b65ad693b16a05.png)



添加sonar服务器地址和名称，点击**应用**完成操作。

![1623590948756](/images/recovered/5d152bc8443988bb0d54.png)



### 将 sonarqubeURL 添加到 KubeSphere 控制台

指定 `sonarqubeURL`，以便可以直接从 KubeSphere 控制台访问 SonarQube。

执行以下命令：

```shell
$ kubectl edit  cm -n kubesphere-system  ks-console-config
```



搜寻到 `client`，添加 `devops` 字段并指定 `sonarqubeURL`。

```yaml
    client:
      version:
        kubesphere: v3.1.0
        kubernetes: v1.20.4
        openpitrix: v0.3.5
      enableKubeConfig: true
      devops:
        sonarqubeURL: http://34.92.90.181:32108
```

结果

![1623591094844](/images/recovered/8e65227a783bf3d66c3b.png)



### 重启服务

执行以下命令。

```shell
$ kubectl -n kubesphere-system rollout restart deploy ks-apiserver
$ kubectl -n kubesphere-system rollout restart deploy ks-console
```



## 为新工程创建 SonarQube Token

创建一个 SonarQube 令牌，以便您的流水线可以在运行时与 SonarQube 通信。

在 SonarQube 控制台上，点击 **Create new project**。

![1623591255909](/images/recovered/8bf090a32b9dd97d52bd.png)



设置工程名称

![1623591269495](/images/recovered/aa5f9a55e64069943df8.png)



生成token

![1623591326774](/images/recovered/5df7650587deb41e10af.png)



创建令牌后，点击 **Continue**。

![1623591357570](/images/recovered/c5861847548837fa2b87.png)



分别选择 **Java** 和 **Maven**。复制下图所示绿色框中的序列号，如果要在流水线中使用，则需要在[凭证](https://kubesphere.io/zh/docs/devops-user-guide/how-to-use/credential-management/#创建凭证)中添加此序列号。

![1623591381678](/images/recovered/9d23be1b7fa0cba0f97e.png)



## 创建流水线工程

### 创建凭证

登录 KubeSphere 控制台。转到 DevOps 工程，在**工程管理**下的**凭证**页面创建以下凭证。

| 凭证 ID         | 类型       | 用途       |
| :-------------- | :--------- | :--------- |
| dockerhub-id    | 帐户凭证   | Docker Hub |
| demo-kubeconfig | kubeconfig | Kubernetes |

demo-kubeconfig

![1623591543502](/images/recovered/9d589a710ea6a3c4949e.png)



dockerhub-id

![1623591726548](/images/recovered/a9e229f3e585cfe0567c.png)



创建一个凭证 ID (`sonar-token`)

![1623591882055](/images/recovered/eb8b6e0fed93a92cae44.png)



列表中看到已创建的三个凭证。

![1623591917707](/images/recovered/62c836a1edee168c5bc4.png)



### 创建流水线

在**流水线**页面点击**创建**，为了使用图形化流水线搭建，不在此处引用代码仓库，直接点击下一步

![1623592917931](/images/recovered/eefcd4734da6d82f034c.png)



保持默认配置，点击创建

![1623592981578](/images/recovered/6fefff47857c97224971.png)

创建成功

![1623592994758](/images/recovered/098e571387288539e753.png)



进入流水线，点击编辑

![1623593005853](/images/recovered/bbb5720367c9c14f7443.png)



此时选择CICD模板

![1623593042443](/images/recovered/3ffc52d9e25d72e8f851.png)



可视化编辑流水线

![1623593102065](/images/recovered/439b3f7c3a40f5368b3d.png)



编辑后运行

![1623593508711](/images/recovered/4304e8dee39c03644e84.png)



流水线支持交互式操作

![1623664726853](/images/recovered/865d8f3e3449d7bdbb4b.png)

## 在 KubeSphere 控制台查看结果

流水线执行成功后，即可查看到代码质量标签

![1623664520315](/images/recovered/a7044f82a5b93ad0bad3.png)



sonar控制台也可以查看对应结果

![1623664594650](/images/recovered/3d038320fa8c788d03f0.png)



jenkins视图

![1623664630635](/images/recovered/76996c18679d19edee6c.png)



blue ocean

![1623664649276](/images/recovered/8f36aaa2df0c8f11e727.png)

![1623664672153](/images/recovered/531571e2834cf4a93bba.png)
