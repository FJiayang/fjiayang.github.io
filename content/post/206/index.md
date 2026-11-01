{
  "title": "DevOps GitLab CICD 实践2——Runner 部署",
  "date": "2019-04-03T16:31:00+08:00",
  "lastmod": "2019-04-07T10:54:36+08:00",
  "typecho_cid": 206,
  "url": "/archives/206/",
  "comments": false,
  "draft": false,
  "slug": "206",
  "categories": [
    "服务器",
    "总结"
  ],
  "tags": [
    "GitLab",
    "docker",
    "CICD",
    "DevOps"
  ],
  "math": false
}

前置步骤：[DevOps GitLab CICD 实践1——GitLab 部署](/archives/205/)


## 官方文档

[文档地址](https://docs.gitlab.com/runner/install/docker.html)

虽然有官方指引，但个人感觉指引的不够清晰，导致初次配置可能频繁失败

> # Run GitLab Runner in a container
>
> This is how you can run GitLab Runner inside a Docker container.
>
> ## General GitLab Runner Docker image usage
>
> GitLab Runner Docker images (based on [Ubuntu or Alpine Linux](https://docs.gitlab.com/runner/install/docker.html#docker-images)) are designed as wrappers around the standard `gitlab-runner` command, like if GitLab Runner was installed directly on the host.
>
> The general rule is that every GitLab Runner command that normally would be executed as:
>
> ```bash
> gitlab-runner [Runner command and options...]
> ```
>
> can be executed with:
>
> ```bash
> docker run [chosen docker options...] gitlab/gitlab-runner [Runner command and options...]
> ```
>
> For example, getting the top-level help information for GitLab Runner command could be executed as:
>
> ```bash
> docker run --rm -t -i gitlab/gitlab-runner --help
> 
> NAME:
>    gitlab-runner - a GitLab Runner
> 
> USAGE:
>    gitlab-runner [global options] command [command options] [arguments...]
> 
> VERSION:
>    10.7.0 (7c273476)
> 
> (...)
> ```
>
> In short, the `gitlab-runner` part of the command is replaced with `docker run [docker options] gitlab/gitlab-runner`, while the rest of Runner’s command stays as it is described in the [register documentation](https://docs.gitlab.com/runner/register/index.html). The only difference is that the `gitlab-runner` command is executed inside of a Docker container.
>
> ## Docker image installation and configuration
>
> 1. Install Docker first:
>
>    ```bash
>     curl -sSL https://get.docker.com/ | sh
>    ```
>
> 2. You need to mount a config volume into the `gitlab-runner` container to be used for configs and other resources:
>
>    ```bash
>     docker run -d --name gitlab-runner --restart always \
>       -v /srv/gitlab-runner/config:/etc/gitlab-runner \
>       -v /var/run/docker.sock:/var/run/docker.sock \
>       gitlab/gitlab-runner:latest
>    ```
>
>    **Tip:** On macOS, use `/Users/Shared` instead of `/srv`.
>
>    Or, you can use a config container to mount your custom data volume:
>
>    ```bash
>     docker run -d --name gitlab-runner-config \
>         -v /etc/gitlab-runner \
>         busybox:latest \
>         /bin/true
>    ```
>
>    And then, run the Runner:
>
>    ```bash
>     docker run -d --name gitlab-runner --restart always \
>         -v /var/run/docker.sock:/var/run/docker.sock \
>         --volumes-from gitlab-runner-config \
>         gitlab/gitlab-runner:latest
>    ```
>
> 3. Register the runner you just launched by following the instructions in the [Docker section of Registering Runners](https://docs.gitlab.com/runner/register/index.html#docker). The runner won’t pick up any jobs until it’s registered.



## 安装步骤

### 获取Gitlab Runner秘钥

可以通过Gitlab管理员账号获取，也可以让每一个用户自行配置

- 普通用户查看秘钥

进入任意一个仓库的设置中，查看CICD配置

[![1554266163188.png](/images/recovered/3081bff4a37d74a8a1ea.png)](/images/recovered/3081bff4a37d74a8a1ea.png)

准备注册专用Runner令牌

[![1554266217632.png](/images/recovered/524156a5210b2633cf8b.png)](/images/recovered/524156a5210b2633cf8b.png)



- 管理员查看令牌

进入总设置页面，配置全局Runner令牌

[![1554266287842.png](/images/recovered/7febd5e20f496fcd92ee.png)](/images/recovered/7febd5e20f496fcd92ee.png)



### Runner注册

由于Runner一般运行复杂构建、打包任务，推荐配置在性能、带宽更大的机房

####  准备Docker环境

```bash
$ curl -sSL https://get.docker.com/ | sh
$ systemctl start docker
```



#### 注册

可以根据需要选择注册Runner类型

同时，为了方便配置，使用单行注册并且关闭交互

[单行注册官方文档](https://docs.gitlab.com/runner/register/index.html#one-line-registration-command)

命令说明：

- `-v`挂载的目的是为了将注册后的配置文件持久化，用于运行容器
- `--rm`指定容器运行结束后自动删除停止的容器
- `-it`指定使用命令行交互方式运行，便于查看注册结果



```bash
$ docker run --rm -it \
  -v /www/wwwroot/gitlab/srv/gitlab-runner/config:/etc/gitlab-runner \
  gitlab/gitlab-runner:alpine-v11.8.0 register \
  --non-interactive \
  --executor "docker" \
  --docker-image docker:stable \
  --url "Gitlab URL" \
  --registration-token "令牌" \
  --description "描述" \
  --tag-list "标签1,标签2" \
  --run-untagged \
  --docker-privileged \
  --locked="false"
```



注册成功提示

[![1554277014308.png](/images/recovered/8c2fd4c5485abe7dafc3.png)](/images/recovered/8c2fd4c5485abe7dafc3.png)



此时管理面板显示新的Runner已经注册

[![1554277086811.png](/images/recovered/16885f67d7b841618125.png)](/images/recovered/16885f67d7b841618125.png)



### Runner 启动

挂载本地配置信息并启动Runner

```bash
$ docker run -d --name gitlab-runner --restart always \
 	-v /www/wwwroot/gitlab/srv/gitlab-runner/config:/etc/gitlab-runner \
    -v /var/run/docker.sock:/var/run/docker.sock \
    gitlab/gitlab-runner:alpine-v11.8.0
```



此时可见Runner已经保持和Gitlab的联系

[![1554277457677.png](/images/recovered/1e4651221bc4d7449ea5.png)](/images/recovered/1e4651221bc4d7449ea5.png)
