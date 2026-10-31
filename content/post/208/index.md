{
  "title": "Docker 19.03 版本对原Gitlab-Runner的影响",
  "date": "2019-07-28T13:09:00+08:00",
  "lastmod": "2019-07-28T14:12:32+08:00",
  "typecho_cid": 208,
  "url": "/archives/208/",
  "comments": false,
  "draft": false,
  "slug": "208",
  "categories": [
    "开发"
  ],
  "tags": [
    "GitLab",
    "docker",
    "CICD"
  ],
  "math": false
}

## 版本变化始末

- 在 2019.07.24 Docker社区发布了`19.03`的新版本，在此前版本号为`18.0x`



## 新版本带来的坑

原本没太在意`docker`版本的变化，因为多数情况都是兼容旧版的所有特性和功能的

结果在近期的CICD构建中，在ci脚本没有变化的情况下突然所有`runner`的构建都失败了

随后立即采取以下措施尝试修复

1. 工程版本回退到上一次可用状态
2. 更换`runner`服务器和容器
3. 更改`ci`脚本
4. 重启`docker`服务

均无效

![1564288081390.png](https://i.loli.net/2019/07/28/5d3d2d216a5f496230.png)



执行构建步骤出现了以往没有出现过的警告信息

```bash
Running with gitlab-runner 11.8.0 (4745a6f3)
  on docker-in-docker-runner 4iAG2sYM
Using Docker executor with image docker:stable ...
Starting service docker:dind ...
Pulling docker image docker:dind ...
Using docker image sha256:fd0c64832f7e46b63a180e6000dbba7ad7a63542c5764841cba73429ba74a39e for docker:dind ...
Waiting for services to be up and running...

*** WARNING: Service runner-4iAG2sYM-project-89-concurrent-0-docker-0 probably didn't start properly.

Health check error:
service "runner-4iAG2sYM-project-89-concurrent-0-docker-0-wait-for-service" timeout

Health check container logs:

...

2019-07-24T03:11:35.365911823Z time="2019-07-24T03:11:35.365537741Z" level=info msg="API listen on [::]:2376"
2019-07-24T03:11:35.366107674Z time="2019-07-24T03:11:35.365626706Z" level=info msg="API listen on /var/run/docker.sock"

*********

Pulling docker image docker:stable ...
Using docker image sha256:c4154a2b47a18fe9437956ab981bd5924b19e7ae3eb3ed60c42cf8dfa394d550 for docker:stable ...
```

最终报错信息

```bash
Downloading artifacts for maven-build (280)...
Downloading artifacts from coordinator... ok        id=280 responseStatus=200 OK token=L9iuC5Ss
$ docker build -t $CONTAINER_IMAGE:$IMAGE_VERSION .
Cannot connect to the Docker daemon at tcp://docker:2375. Is the docker daemon running?
ERROR: Job failed: exit code 1
```



## 寻找解决方法

该错误在早期版本就出现过，但与本次情况均不符合，以往通过挂载容器路径即可，而本次情况是`runner`服务和构建脚本均不变的情况下突然出现构建失败的情况

![1564288454164.png](https://i.loli.net/2019/07/28/5d3d2d21691a426024.png)



最终在社区ISSUS讨论中发现了相关讨论，并且问题发生时间相近

[Jobs failing with "Cannot connect to the Docker daemon"](https://gitlab.com/gitlab-org/gitlab-ce/issues/64959)

![1564288560626.png](https://i.loli.net/2019/07/28/5d3d2d212457666352.png)

官方开发者解释 当天几个小时前发布的新版本 `19.03`默认开启了`TLS`确实会影响已有的`Docker in Docker `模式的构建环境

![1564288621569.png](https://i.loli.net/2019/07/28/5d3d2d2147bd260875.png)



同时官方开发人员建议自行部署的`runner`建议开启`TLS`功能

![1564288718662.png](https://i.loli.net/2019/07/28/5d3d2d214685a34515.png)



该开发者在另一个讨论中提供了19.03环境下的runner启动和配置样板，同时还有样例ci脚本

[Update DinD example for 19.03](https://gitlab.com/gitlab-org/gitlab-ce/merge_requests/31051#note_194866340)

![1564288829375.png](https://i.loli.net/2019/07/28/5d3d2d21539a832091.png)



## 解决方法

1. 最好可以卸载旧版本的Docker，尽管运行runner和dind环境都基于docker容器中
2. 加入TLS相关runner注册配置



此处采用更新Docker版本并使用最新版的runner镜像进行注册

### 更新docker版本

[官方文档](https://docs.docker.com/install/linux/docker-ce/centos/)

卸载旧docker

```bash
$ sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
```



配置生产环境的依赖仓库

```bash
$ sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
```



**官方建议**的安装新版Docker命令

```bash
$ sudo yum install docker-ce docker-ce-cli containerd.io
```



但经过这次事件后个人不建议使用该命令，而是应该手动指定所有Docker环境版本号，防止以后版本更新导致不兼容问题

查看当前可以安装的所有版本

```bash
$ sudo yum list docker-ce --showduplicates | sort -r
 * updates: repos.lax.quadranet.com
Loaded plugins: fastestmirror
 * extras: mirror.hostduplex.com
 * epel: d2lzkl7pfhq30w.cloudfront.net
 * elrepo-kernel: repos.lax-noc.com
docker-ce.x86_64            3:19.03.1-3.el7                     docker-ce-stable
docker-ce.x86_64            3:19.03.0-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.8-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.7-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.6-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.5-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.4-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.3-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.2-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.1-3.el7                     docker-ce-stable
docker-ce.x86_64            3:18.09.0-3.el7                     docker-ce-stable
docker-ce.x86_64            18.06.3.ce-3.el7                    docker-ce-stable
docker-ce.x86_64            18.06.2.ce-3.el7                    docker-ce-stable
docker-ce.x86_64            18.06.1.ce-3.el7                    docker-ce-stable
docker-ce.x86_64            18.06.0.ce-3.el7                    docker-ce-stable
docker-ce.x86_64            18.03.1.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            18.03.0.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.12.1.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.12.0.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.09.1.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.09.0.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.06.2.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.06.1.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.06.0.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.03.3.ce-1.el7                    docker-ce-stable
docker-ce.x86_64            17.03.2.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.03.1.ce-1.el7.centos             docker-ce-stable
docker-ce.x86_64            17.03.0.ce-1.el7.centos             docker-ce-stable
Determining fastest mirrors
 * base: mirror.hostduplex.com
Available Packages
```



指定最新版本

```bash
$ sudo yum install docker-ce-19.03.1 docker-ce-cli-19.03.1 containerd.io
```



启动docker

```bash
$ sudo systemctl start docker
```



设置开机自启

```bash
$ sudo systemctl enable docker
```



### 安装Gitlab Runner

官方对新版启用TLS的注册样例

> 1. Register GitLab Runner from the command line to use `docker` and `privileged`
> mode:
>
   >  ```bash
   >  sudo gitlab-runner register -n \
   >    --url https://gitlab.com/ \
   >    --registration-token REGISTRATION_TOKEN \
   >    --executor docker \
   >    --description "My Docker Runner" \
   >    --docker-image "docker:stable" \
   >    --docker-privileged \
   >    --docker-volumes "/certs/client"
   >  ```



此处采用容器化注册runner命令为

```bash
$ docker run --rm -t -i \
-v /etc/gitlab-runner/config:/etc/gitlab-runner \
gitlab/gitlab-runner:alpine-v12.1.0 register \
--url "https://gitlab.com/" \
--registration-token REGISTRATION_TOKEN \
--executor docker \
--non-interactive \
--run-untagged \
--tag-list "Runner,Docker" \
--run-untagged="true" \
--locked="false" \
--description "My Docker Runner" \
--docker-image "docker:stable" \
--docker-privileged \
--docker-volumes "/certs/client"
```

主要的变化至于增加了证书挂载`--docker-volumes "/certs/client"`配置，同时指定了`runner`的版本号



启动`runner`

```bash
$ docker run --name gitlab-runner --restart always -d \
-v /etc/gitlab-runner/config:/etc/gitlab-runner \
-v /var/run/docker.sock:/var/run/docker.sock \
gitlab/gitlab-runner:alpine-v12.1.0
```



### 修改构建脚本

官方对新版启用`TLS`的构建脚本样例，指定了构建时使用的`docker`版本与外部一直，防止不兼容的问题

同时加入了`TLS`环境变量配置

```yaml
 image: docker:19.03

 variables:
   # When using dind service we need to instruct docker, to talk with
   # the daemon started inside of the service. The daemon is
   # available with a network connection instead of the default
   # /var/run/docker.sock socket. docker:19.03-dind does this
   # automatically by setting the DOCKER_HOST in
   # https://github.com/docker-library/docker/blob/d45051476babc297257df490d22cbd806f1b11e4/19.03/docker-entrypoint.sh#L23-L29
   #
   # The 'docker' hostname is the alias of the service container as described at
   # https://docs.gitlab.com/ee/ci/docker/using_docker_images.html#accessing-the-services.
   #
   # Note that if you're using the Kubernetes executor, the variable should be set to
   # tcp://localhost:2376/ because of how the Kubernetes executor connects services
   # to the job container
   # DOCKER_HOST: tcp://localhost:2376/
   #
   # When using dind, it's wise to use the overlayfs driver for
   # improved performance.
   DOCKER_DRIVER: overlay2
   # Specify to Docker where to create the certificates, Docker will
   # create them automatically on boot, and will create
   # `/certs/client` that will be shared between the service and
   # build container.
   DOCKER_TLS_CERTDIR: "/certs"

 services:
   - docker:19.03-dind

 before_script:
   - echo $DOCKER_HOST
   - docker info

 build:
   stage: build
   script:
     - docker build -t my-docker-image .
```



在此前自己的构建脚本是按照官网提供的样板，没有指定版本，因此会导致每次构建都会使用当前最新的版本作为基础，最终导致外部Docker和内部Docker容器版本不一致

官网示例DinD构建脚本

```yaml
image: docker:stable
services:
  - docker:dind
...
```



按照社区配置修改后重新构建则成功

![1564290149104.png](https://i.loli.net/2019/07/28/5d3d2d213b81385192.png)



## 总结

对于Docker等云服务平台仍然需要特别注意版本变化，为了防止不兼容的情况，在生产环境尽量不要使用`latest`版本标签，而是应该手动指定所有参与构建的版本环境
