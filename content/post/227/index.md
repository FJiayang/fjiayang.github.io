{
  "title": "k8s环境下GitLab+Helm+GitLab Runner Java项目CICD落地实践",
  "date": "2019-11-27T10:24:00+08:00",
  "lastmod": "2020-05-11T09:10:45+08:00",
  "typecho_cid": 227,
  "url": "/archives/227/",
  "comments": false,
  "draft": false,
  "slug": "227",
  "categories": [
    "开发",
    "学习"
  ],
  "tags": [
    "GitLab",
    "docker",
    "CICD",
    "Kubernetes"
  ],
  "image": "/images/recovered/f5cace70efb61011b9df.png",
  "math": false
}

## 背景

目前使用5台服务器搭建了`Kubernetes`集群环境，监控、日志采集均已落地，业务也手工迁移到集群中顺利运行，故需要将原本基于原生`docker`环境的CICD流程迁移到`Kubernetes`集群中



## 优势

`Kubernetes`集群实现CICD有几个显著优势

1. `Deployment` 天然支持滚动部署、结合其他`Kubernetes`特性还能实现蓝绿部署、金丝雀部署等
2. 新版本的`GitLab`与`GitLab Runner`天然支持`Kubernetes`集群，支持`runner`自动伸缩，减小资源占用



## 环境

`Kubernetes`版本：1.14

`GitLab`版本：12.2.5

`GitLab-Runner`版本：12.1.0

`Docker`环境版本：17.03.1



## GitLab-Runner部署

### 配置介绍

原始环境的`gitlab runner`通过手动执行官网提供的注册命令和启动命令，分成两部部署，需要较多的手工操作，而在`Kubernetes`中，其支持使用`Helm`一键部署，官方文档如下

[GitLab Runner Helm Chart](https://docs.gitlab.com/runner/install/`Kubernetes`.html)

其实官方文档的指引并不清晰，许多配置在文档中没有介绍用法，推荐去其源码仓库查看详细的参数使用文档

[The Kubernetes executor](https://gitlab.com/gitlab-org/gitlab-ci-multi-runner/blob/master/docs/executors/`Kubernetes`.md#the-keywords)

其中介绍了几个关键配置，在后面修改工程的`ci`配置文件时会用到

#### 使用DinD方式构建已经不再推荐

[官方文档](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#use-docker-in-docker-workflow-with-docker-executor)介绍

> ### Use docker-in-docker workflow with Docker executor
>
> The second approach is to use the special docker-in-docker (dind) [Docker image](https://hub.docker.com/_/docker/) with all tools installed (`docker`) and run the job script in context of that image in privileged mode.
>
> **Note:** `docker-compose` is not part of docker-in-docker (dind). To use `docker-compose` in your CI builds, follow the `docker-compose` [installation instructions](https://docs.docker.com/compose/install/).
>
> **Danger:** By enabling `--docker-privileged`, you are effectively disabling all of the security mechanisms of containers and exposing your host to privilege escalation which can lead to container breakout. For more information, check out the official Docker documentation on [Runtime privilege and Linux capabilities](https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities).
>
> Docker-in-Docker works well, and is the recommended configuration, but it is not without its own challenges:
>
> - When using docker-in-docker, each job is in a clean environment without the past history. Concurrent jobs work fine because every build gets it’s own instance of Docker engine so they won’t conflict with each other. But this also means jobs can be slower because there’s no caching of layers.
> - By default, Docker 17.09 and higher uses `--storage-driver overlay2` which is the recommended storage driver. See [Using the overlayfs driver](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#using-the-overlayfs-driver) for details.
> - Since the `docker:19.03.1-dind` container and the Runner container don’t share their root filesystem, the job’s working directory can be used as a mount point for child containers. For example, if you have files you want to share with a child container, you may create a subdirectory under `/builds/$CI_PROJECT_PATH` and use it as your mount point (for a more thorough explanation, check [issue #41227](https://gitlab.com/gitlab-org/gitlab-foss/issues/41227)):

总之使用`DinD`进行容器构建并非不可行，但面临许多问题，例如使用`overlay2`网络需要Docker版本高于 17.09



> ### Using `docker:dind` 
>
> Running the `docker:dind` also known as the `docker-in-docker` image is also possible but sadly needs the containers to be run in privileged mode. If you're willing to take that risk other problems will arise that might not seem as straight forward at first glance. Because the docker daemon is started as a `service` usually in your `.gitlab-ci.yaml` it will be run as a separate container in your Pod. Basically containers in Pods only share volumes assigned to them and an IP address by which they can reach each other using `localhost`. `/var/run/docker.sock` is not shared by the `docker:dind` container and the `docker` binary tries to use it by default.
>
> To overwrite this and make the client use TCP to contact the Docker daemon, in the other container, be sure to include the environment variables of the build container:
>
> -  `DOCKER_HOST=tcp://localhost:2375` for no TLS connection.
> -  `DOCKER_HOST=tcp://localhost:2376` for TLS connection.
>
> Make sure to configure those properly. As of Docker 19.03, TLS is enabled by default but it requires mapping certificates to your client. You can enable non-TLS connection for DIND or mount certificates as described in [**Use Docker In Docker Workflow wiht Docker executor**](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html#use-docker-in-docker-workflow-with-docker-executor)

在Docker 19.03.1版本之后默认开启了`TLS`配置，在构建的环境变量中需要声明，否则报连接不上`docker`的错误，并且使用`DinD`构建需要`runner`开启特权模式，以访问主机的资源，并且由于使用了特权模式，在`Pod`中对`runner`需要使用的资源限制将失效

![1574777453616](/images/recovered/a582dfca06d2650a98e5.png)



#### 使用Kaniko构建Docker镜像

目前官方提供另一种方式在`docker`容器中构建并推送镜像，实现更加优雅，可以实现无缝迁移，那就是`kaniko`

[Building a Docker image with kaniko](https://docs.gitlab.com/ee/ci/docker/using_kaniko.html)

其优势官网描述如下

> 在Kubernetes集群中构建Docker映像的另一种方法是使用[kaniko](https://github.com/GoogleContainerTools/kaniko)。iko子
>
> - 允许您构建没有特权访问权限的映像。
> - 无需Docker守护程序即可工作。



在后面的实践中会使用两种方式构建Docker镜像，可根据实际情况选择

### 使用Helm部署

拉取`Helm` `Gitlab-Runner`仓库到本地，修改配置

[GitLab Runner](https://gitlab.com/gitlab-org/charts/gitlab-runner)

将原有的`gitlab-runner`配置迁移到`Helm`中，迁移后如下

```yaml
image: alpine-v12.1.0
imagePullPolicy: IfNotPresent
gitlabUrl: https://gitlab.fjy8018.top/
runnerRegistrationToken: "***"
unregisterRunners: true
terminationGracePeriodSeconds: 3600
concurrent: 10
checkInterval: 30
rbac:
  create: true
  clusterWideAccess: false
metrics:
  enabled: true
  listenPort: 9090
runners:
  image: ubuntu:16.04
  imagePullSecrets:
    - name: registry-secret
  locked: false
  tags: "k8s"
  runUntagged: true
  privileged: true
  pollTimeout: 180
  outputLimit: 4096
  cache: {}
  builds: {}
  services: {}
  helpers: {}
resources:
   limits:
     memory: 2048Mi
     cpu: 1500m
   requests:
     memory: 128Mi
     cpu: 200m
affinity: {}
nodeSelector: {}
tolerations: []
hostAliases:
   - ip: "192.168.1.13"
     hostnames:
     - "gitlab.fjy8018.top"
   - ip: "192.168.1.30"
     hostnames:
     - "harbor.fjy8018.top"
podAnnotations: {}
```

其中配置了私钥、内网`harbor`地址、`harbor`拉取资源私钥，资源限制策略



#### GitLab-Runner选择可能导致的坑

选择`runner`镜像为`alpine-v12.1.0`，这一点单独说一下，目前最新的runner版本为12.5.0，但其有许多问题，`alpine`新版镜像在`Kubernetes`中间断发生无法解析`DNS`的问题，反映到`GitLab-Runner`中就是`Could not resolve host`和`server misbehaving`

![1574778107416](/images/recovered/4f62d2a71d572b8c5a3e.png)

![1574778146693](/images/recovered/5ef3418a63807e9d2f99.png)



查阅解决方法

![1574777890021](/images/recovered/64134951d07447515eb3.png)

通过查询发现，其官方仓库还有多个相关issue没有关闭

官方gitlab：[Kubernetes runner: Could not resolve host](https://gitlab.com/gitlab-org/charts/gitlab-runner/issues/96)

stackoverflow：[Gitlab Runner is not able to resolve DNS of Gitlab Server](https://stackoverflow.com/questions/57049548/gitlab-runner-is-not-able-to-resolve-dns-of-gitlab-server)



给出的解决方案无一例外都是降级到alpine-v12.1.0

> We had same issue for couple of days. We tried change CoreDNS config, move runners to different k8s cluster and so on. Finally today i checked my personal runner and found that i'm using different version. Runners in cluster had `gitlab/gitlab-runner:alpine-v12.3.0`, when mine had `gitlab/gitlab-runner:alpine-v12.0.1`. We added line
>
> ```yaml
> image: gitlab/gitlab-runner:alpine-v12.1.0
> ```
>
> in `values.yaml` and this solved problem for us



其问题的根源应该在于alpine基础镜像对Kubernetes 集群支持有问题，

[ndots breaks DNS resolving #64924](https://github.com/`Kubernetes`/`Kubernetes`/issues/64924)

![1574778408166](/images/recovered/77a31a4d5b4eed770682.png)



![1574778416868](/images/recovered/a94cb221a51ffb83822b.png)



`docker-alpine`仓库对应也有未关闭的`issue`，其中就提到了关于`DNS`解析超时和异常的问题

[DNS Issue #255](https://github.com/gliderlabs/docker-alpine/issues/255)

![1574778470283](/images/recovered/26b612781eb91e309dcd.png)

#### 安装

一行命令安装即可

```bash
$ helm install /root/gitlab-runner/ --name k8s-gitlab-runner --namespace gitlab-runner
```

输出如下

```bash
NAME:   k8s-gitlab-runner
LAST DEPLOYED: Tue Nov 26 21:51:57 2019
NAMESPACE: gitlab-runner
STATUS: DEPLOYED

RESOURCES:
==> v1/ConfigMap
NAME                             DATA  AGE
k8s-gitlab-runner-gitlab-runner  5     0s

==> v1/Deployment
NAME                             READY  UP-TO-DATE  AVAILABLE  AGE
k8s-gitlab-runner-gitlab-runner  0/1    1           0          0s

==> v1/Pod(related)
NAME                                              READY  STATUS   RESTARTS  AGE
k8s-gitlab-runner-gitlab-runner-744d598997-xwh92  0/1    Pending  0         0s

==> v1/Role
NAME                             AGE
k8s-gitlab-runner-gitlab-runner  0s

==> v1/RoleBinding
NAME                             AGE
k8s-gitlab-runner-gitlab-runner  0s

==> v1/Secret
NAME                             TYPE    DATA  AGE
k8s-gitlab-runner-gitlab-runner  Opaque  2     0s

==> v1/ServiceAccount
NAME                             SECRETS  AGE
k8s-gitlab-runner-gitlab-runner  1        0s


NOTES:

Your GitLab Runner should now be registered against the GitLab instance reachable at: "https://gitlab.fjy8018.top/"
```

查看gitlab admin页面，发现已经有一个runner成功注册

![1574778634857](/images/recovered/d10b19e854073addd985.png)



## 工程配置

### DinD方式构建所需配置

如果原本的`ci`文件是基于`19.03 DinD`镜像构建的则需要加上`TLS`相关配置

```yaml
image: docker:19.03

variables:
  DOCKER_DRIVER: overlay
  DOCKER_HOST: tcp://localhost:2375
  DOCKER_TLS_CERTDIR: ""
...
```

其余配置保持不变，使用DinD构建



### Kubectl和Kubernetes权限配置

由于使用`k8s`集群，而通过集群部署需要使用`kubectl`客户端，故手动创建了一个`kubectl` `docker`镜像，使用`gitlab`触发`dockerhub`构建，构建内容公开透明，可放心使用，如有其它版本的构建需求也可提pull request，会在后面补充，目前用到的只有1.14.0

[fjy8018/kubectl](https://hub.docker.com/r/fjy8018/kubectl)

![1574778835433](/images/recovered/a201ffc6c21b0774726a.png)



有`kubectl`客户端，还需要配置连接`TLS`和连接账户

为了保障安全，新建一个专门访问该工程命名空间的`ServiceAccount`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hmdt-gitlab-ci
  namespace: hmdt
```

利用集群提供的RBAC机制，为该账户授予该命名空间的admin权限

```yaml
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: RoleBinding
metadata:
  name: hmdt-gitlab-role
  namespace: hmdt
subjects:
  - kind: ServiceAccount
    name: hmdt-gitlab-ci
    namespace: hmdt
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: admin
```

创建后在查询其在k8s集群中生成的唯一名称，此处为`hmdt-gitlab-ci-token-86n89`

```bash
$ kubectl describe sa hmdt-gitlab-ci -n hmdt
Name:                hmdt-gitlab-ci
Namespace:           hmdt
Labels:              <none>
Annotations:         kubectl.`Kubernetes`.io/last-applied-configuration:
                       {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"name":"hmdt-gitlab-ci","namespace":"hmdt"}}
Image pull secrets:  <none>
Mountable secrets:   hmdt-gitlab-ci-token-86n89
Tokens:              hmdt-gitlab-ci-token-86n89
Events:              <none>
```


然后根据上面的Secret找到CA证书

```bash
$ kubectl get secret hmdt-gitlab-ci-token-86n89 -n hmdt -o json | jq -r '.data["ca.crt"]' | base64 -d
```

再找到对应的 Token 

```bash
$ kubectl get secret hmdt-gitlab-ci-token-86n89  -n hmdt -o json | jq -r '.data.token' | base64 -d
```



### Kubernetes关联GitLab配置

进入gitlab Kubernetes集群配置页面，填写相关信息，让gitlab自动连接上集群环境

![1574779375430](/images/recovered/1e7a628a0b17a63beebd.png)

![1574779403873](/images/recovered/077f2302c8f248b212a1.png)

注意，需要将此处取消勾选，否则gitlab会自动创建新的用户账户，而不使用已经创建好的用户账户，在运行过程中会报无权限错误

![1574779467185](/images/recovered/2676ec20b4fd0cf870d5.png)

不取消导致的报错如下，gitlab创建了新的用户账户`hmdt-prod-service-account`，但没有操作指定命名空间的权限

![1574779599949](/images/recovered/eaefe7781ff71d9bf4f8.png)



### GitLab环境配置

创建环境

![image-20191127095307604](/images/recovered/b401fca8b9d48e6ffe48.png)

名称和url可以按需自定义

![image-20191127095330949](/images/recovered/3b954ff180a10d352428.png)



### CI脚本配置

最终配置CI文件如下，该文件使用`DinD`方式构建`Dockerfile`

```yaml
image: docker:19.03

variables:
  MAVEN_CLI_OPTS: "-s .m2/settings.xml --batch-mode -Dmaven.test.skip=true"
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  DOCKER_DRIVER: overlay
  DOCKER_HOST: tcp://localhost:2375
  DOCKER_TLS_CERTDIR: ""
  SPRING_PROFILES_ACTIVE: docker
  IMAGE_VERSION: "1.8.6"
  DOCKER_REGISTRY_MIRROR: "https://XXX.mirror.aliyuncs.com"

stages:
  - test
  - package
  - review
  - deploy

maven-build:
  image: maven:3-jdk-8
  stage: test
  retry: 2
  script:
    - mvn $MAVEN_CLI_OPTS clean package -U -B -T 2C
  artifacts:
    expire_in: 1 week
    paths:
      - target/*.jar

maven-scan:
  stage: test
  retry: 2
  image: maven:3-jdk-8
  script:
    - mvn $MAVEN_CLI_OPTS verify sonar:sonar

maven-deploy:
  stage: deploy
  retry: 2
  image: maven:3-jdk-8
  script:
    - mvn $MAVEN_CLI_OPTS deploy

docker-harbor-build:
  image: docker:19.03
  stage: package
  retry: 2
  services:
    - name: docker:19.03-dind
      alias: docker
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
  script:
    - docker build --pull -t "$CI_REGISTRY_IMAGE:$IMAGE_VERSION" .
    - docker push "$CI_REGISTRY_IMAGE:$IMAGE_VERSION"
    - docker logout $CI_REGISTRY

deploy_live:
  image: fjy8018/kubectl:v1.14.0
  stage: deploy
  retry: 2
  environment:
    name: prod
    url: https://XXXX
  script:
    - kubectl version
    - kubectl get pods -n hmdt
    - cd manifests/
    - sed -i "s/__IMAGE_VERSION_SLUG__/${IMAGE_VERSION}/" deployment.yaml
    - kubectl apply -f deployment.yaml
    - kubectl rollout status -f deployment.yaml
    - kubectl get pods -n hmdt
```



若需要使用`Kaniko`构建`Dockerfile`，则配置如下

注意，其中依赖的镜像` gcr.io/kaniko-project/executor:debug `属于谷歌镜像仓库，可能存在无法拉取的情况

```yaml
image: docker:19.03

variables:
  MAVEN_CLI_OPTS: "-s .m2/settings.xml --batch-mode -Dmaven.test.skip=true"
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  DOCKER_DRIVER: overlay
  DOCKER_HOST: tcp://localhost:2375
  DOCKER_TLS_CERTDIR: ""
  SPRING_PROFILES_ACTIVE: docker
  IMAGE_VERSION: "1.8.6"
  DOCKER_REGISTRY_MIRROR: "https://XXX.mirror.aliyuncs.com"

cache:
  paths:
    - target/

stages:
  - test
  - package
  - review
  - deploy

maven-build:
  image: maven:3-jdk-8
  stage: test
  retry: 2
  script:
    - mvn $MAVEN_CLI_OPTS clean package -U -B -T 2C
  artifacts:
    expire_in: 1 week
    paths:
      - target/*.jar

maven-scan:
  stage: test
  retry: 2
  image: maven:3-jdk-8
  script:
    - mvn $MAVEN_CLI_OPTS verify sonar:sonar

maven-deploy:
  stage: deploy
  retry: 2
  image: maven:3-jdk-8
  script:
    - mvn $MAVEN_CLI_OPTS deploy


docker-harbor-build:
  stage: package
  retry: 2
  image:
    name: gcr.io/kaniko-project/executor:debug
    entrypoint: [""]
  script:
    - echo "{\"auths\":{\"$CI_REGISTRY\":{\"username\":\"$CI_REGISTRY_USER\",\"password\":\"$CI_REGISTRY_PASSWORD\"}}}" > /kaniko/.docker/config.json
    - /kaniko/executor --context $CI_PROJECT_DIR --dockerfile $CI_PROJECT_DIR/Dockerfile --destination $CI_REGISTRY_IMAGE:$IMAGE_VERSION

deploy_live:
  image: fjy8018/kubectl:v1.14.0
  stage: deploy
  retry: 2
  environment:
    name: prod
    url: https://XXXX
  script:
    - kubectl version
    - kubectl get pods -n hmdt
    - cd manifests/
    - sed -i "s/__IMAGE_VERSION_SLUG__/${IMAGE_VERSION}/" deployment.yaml
    - kubectl apply -f deployment.yaml
    - kubectl rollout status -f deployment.yaml
    - kubectl get pods -n hmdt
```





## 执行流水线

### runner自动扩缩容

`Kubernetes`中的runner会根据任务多少自动扩缩容，目前配置的上限为10个


![1574776369212](/images/recovered/f133f2b163c321857b7d.png)



Grafana也能监控到集群在构建过程中的资源使用情况

![1574776599795](/images/recovered/fc84ee8606979d63f789.png)

### 使用`DinD`构建`Dockerfile`结果

![image-20191127100525518](/images/recovered/e02aa3fbd03eb1439886.png)



### 使用`Kaniko`构建`Dockerfile`的结果

![image-20191127100458620](/images/recovered/4f6b513823e8e91ea79c.png)



### 部署结果

执行部署时gitlab会自动注入配置好的`kubectl` config

![image-20191127095832650](/images/recovered/4e517f5b0185c4d5feb1.png)



### 构建结果

![image-20191127095739561](/images/recovered/69370e29a5e76a27e1a9.png)

部署完成后可在环境配置页中查看部署结果，只有成功的部署才会被记录

![image-20191127095923676](/images/recovered/2d3fb9fb02c9cce4f051.png)
