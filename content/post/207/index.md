{
  "title": "DevOps GitLab CICD 实践3——CI文件编写",
  "date": "2019-04-03T16:32:00+08:00",
  "lastmod": "2023-09-07T17:15:33+08:00",
  "typecho_cid": 207,
  "url": "/archives/207/",
  "comments": false,
  "draft": false,
  "slug": "207",
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
  "math": true
}

前置步骤：

- Docker 版 GitLab CICD 实践1——GitLab 部署 [[Docker 版 GitLab CICD 实践]]
- Docker 版 GitLab CICD 实践2——Runner 部署 [[Docker 版 GitLab CICD 实践——Runner 部署]]


## 官方文档

编写结构类似Jenkins pineline流水线

[GitLab CI/CD Pipeline Configuration Reference](https://docs.gitlab.com/ee/ci/yaml/README.html)

> # GitLab CI/CD Pipeline Configuration Reference
>
> GitLab CI/CD [pipelines](https://docs.gitlab.com/ee/ci/pipelines.html) are configured using a YAML file called `.gitlab-ci.yml` within each project.
>
> The `.gitlab-ci.yml` file defines the structure and order of the pipelines and determines:
>
> - What to execute using [GitLab Runner](https://docs.gitlab.com/runner/).
> - What decisions to make when specific conditions are encountered. For example, when a process succeeds or fails.
>
> This topic covers CI/CD pipeline configuration. For other CI/CD configuration information, see:
>
> - [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/README.html), for configuring the environment the pipelines run in.
> - [GitLab Runner advanced configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration.html), for configuring GitLab Runner.
>
> We have complete examples of configuring pipelines:
>
> - For a quick introduction to GitLab CI, follow our [quick start guide](https://docs.gitlab.com/ee/ci/quick_start/README.html).
> - For a collection of examples, see [GitLab CI/CD Examples](https://docs.gitlab.com/ee/ci/examples/README.html).
> - To see a large `.gitlab-ci.yml` file used in an enterprise, see the [`.gitlab-ci.yml` file for `gitlab-ce`](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/.gitlab-ci.yml).

## 目标

- maven项目自动打包
- ~~自动测试~~
- 自动镜像构建并上传



官方参数表列出了作业的可用参数：

| 关键词                                                       | 描述                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`script`](https://docs.gitlab.com/ee/ci/yaml/README.html#script) | 由Runner执行的Shell脚本。                                    |
| [`image`](https://docs.gitlab.com/ee/ci/yaml/README.html#image) | 使用泊坞窗图像。也可用：`image:name`和`image:entrypoint`。   |
| [`services`](https://docs.gitlab.com/ee/ci/yaml/README.html#services) | 使用docker services图像。也可用：`services:name`，`services:alias`，`services:entrypoint`，和`services:command`。 |
| [`before_script`](https://docs.gitlab.com/ee/ci/yaml/README.html#before_script-and-after_script) | 覆盖在作业之前执行的一组命令。                               |
| [`after_script`](https://docs.gitlab.com/ee/ci/yaml/README.html#before_script-and-after_script) | 覆盖作业后执行的一组命令。                                   |
| [`stages`](https://docs.gitlab.com/ee/ci/yaml/README.html#stages) | 定义管道中的阶段。                                           |
| [`stage`](https://docs.gitlab.com/ee/ci/yaml/README.html#stage) | 定义作业阶段（默认值:) `test`。                              |
| [`only`](https://docs.gitlab.com/ee/ci/yaml/README.html#onlyexcept-basic) | 创建作业时限制。也可用：[`only:refs`，`only:kubernetes`，`only:variables`，和`only:changes`](https://docs.gitlab.com/ee/ci/yaml/README.html#onlyexcept-advanced)。 |
| [`except`](https://docs.gitlab.com/ee/ci/yaml/README.html#onlyexcept-basic) | 在未创建作业时限制。也可用：[`except:refs`，`except:kubernetes`，`except:variables`，和`except:changes`](https://docs.gitlab.com/ee/ci/yaml/README.html#onlyexcept-advanced)。 |
| [`tags`](https://docs.gitlab.com/ee/ci/yaml/README.html#tags) | 用于选择Runner的标签列表。                                   |
| [`allow_failure`](https://docs.gitlab.com/ee/ci/yaml/README.html#allow_failure) | 让工作失败。失败的作业无助于提交状态。                       |
| [`when`](https://docs.gitlab.com/ee/ci/yaml/README.html#when) | 什么时候开始工作。也可用：`when:manual`和`when:delayed`。    |
| [`environment`](https://docs.gitlab.com/ee/ci/yaml/README.html#environment) | 作业部署到的环境的名称。也可用：`environment:name`，`environment:url`，`environment:on_stop`，和`environment:action`。 |
| [`cache`](https://docs.gitlab.com/ee/ci/yaml/README.html#cache) | 后续运行之间应缓存的文件列表。也可用：`cache:paths`，`cache:key`，`cache:untracked`，和`cache:policy`。 |
| [`artifacts`](https://docs.gitlab.com/ee/ci/yaml/README.html#artifacts) | 成功附加到作业的文件和目录列表。也可用：`artifacts:paths`，`artifacts:name`，`artifacts:untracked`，`artifacts:when`，`artifacts:expire_in`，`artifacts:reports`，和`artifacts:reports:junit`。  在GitLab [企业版](https://about.gitlab.com/pricing/)，这些都是可供选择：`artifacts:reports:codequality`，`artifacts:reports:sast`，`artifacts:reports:dependency_scanning`，`artifacts:reports:container_scanning`，`artifacts:reports:dast`，`artifacts:reports:license_management`，和`artifacts:reports:performance`。 |
| [`dependencies`](https://docs.gitlab.com/ee/ci/yaml/README.html#dependencies) | 作业所依赖的其他作业，以便您可以在它们之间传递工件。         |
| [`coverage`](https://docs.gitlab.com/ee/ci/yaml/README.html#coverage) | 给定作业的代码覆盖率设置。                                   |
| [`retry`](https://docs.gitlab.com/ee/ci/yaml/README.html#retry) | 在发生故障的情况下，可以自动重试作业的次数和次数。           |
| [`parallel`](https://docs.gitlab.com/ee/ci/yaml/README.html#parallel) | 应该并行运行多少个作业实例。                                 |
| [`trigger`](https://docs.gitlab.com/ee/ci/yaml/README.html#trigger-premium) | 定义下游管道触发器。                                         |
| [`include`](https://docs.gitlab.com/ee/ci/yaml/README.html#include) | 允许此作业包含外部YAML文件。也可用：`include:local`，`include:file`，`include:template`，和`include:remote`。 |
| [`extends`](https://docs.gitlab.com/ee/ci/yaml/README.html#extends) | 此作业将继承的配置条目。                                     |
| [`pages`](https://docs.gitlab.com/ee/ci/yaml/README.html#pages) | 上传作业结果以用于GitLab Pages。                             |
| [`variables`](https://docs.gitlab.com/ee/ci/yaml/README.html#variables) | 在作业级别定义作业变量。                                     |

**注：** 参数`types`和`type`被[弃用](https://docs.gitlab.com/ee/ci/yaml/README.html#deprecated-parameters)。



## 参考

官方构建案例

[Deploy a Spring Boot application to Cloud Foundry with GitLab CI/CD](https://docs.gitlab.com/ee/ci/examples/deploy_spring_boot_to_cloud_foundry/index.html)



参考其脚本

> ## Configure GitLab CI/CD to deploy your application
>
> Now we need to add the GitLab CI/CD configuration file ([`.gitlab-ci.yml`](https://docs.gitlab.com/ee/ci/yaml/README.html)) to our project’s root. This is how GitLab figures out what commands need to be run whenever code is pushed to our repository. We will add the following `.gitlab-ci.yml` file to the root directory of the repository, GitLab will detect it automatically and run the steps defined once we push our code:
>
> ```yaml
> image: java:8
> 
> stages:
>   - build
>   - deploy
> 
> build:
>   stage: build
>   script: ./mvnw package
>   artifacts:
>     paths:
>       - target/demo-0.0.1-SNAPSHOT.jar
> 
> production:
>   stage: deploy
>   script:
>   - curl --location "https://cli.run.pivotal.io/stable?release=linux64-binary&source=github" | tar zx
>   - ./cf login -u $CF_USERNAME -p $CF_PASSWORD -a api.run.pivotal.io
>   - ./cf push
>   only:
>   - master
> ```



## 配置

### 全局变量

进入工程CI设置配置全局变量脚本，包含镜像仓库登陆名称、密码、打包名称等

配置全局变量目的在于配置脚本中**不应该**包含密码等敏感信息

[![1554278638713.png](/images/recovered/af7cce73632b17e25367.png)](/images/recovered/af7cce73632b17e25367.png)



若希望使用GitLab内置环境变量，可参考官方表格

[GitLab CI/CD environment variables](https://docs.gitlab.com/ee/ci/variables/README.html)





### CI脚本

结合可用参数和样例配置，根据已经存在的SpringBoot项目编写响应的CI脚本`.gitlab-ci.yml`

```yaml
image: docker:stable
services:
  - docker:dind

variables:
  DOCKER_DRIVER: overlay
  SPRING_PROFILES_ACTIVE: gitlab-ci

stages:
  - build
  - package

maven-build:
  image: maven:3-jdk-8
  stage: build
  script: "mvn package -B"
  artifacts:
    paths:
      - target/*.jar

docker-build:
  stage: package
  script:
    - docker build -t $CONTAINER_IMAGE:latest .
    - docker login -u $DOCKER_HUB_USER -p $DOCKER_HUB_PASS
    - docker push $CONTAINER_IMAGE:latest
```



该脚本对于满足脚本目标的工程都可复用，若需要测试，则增加相关的测试步骤即可

此处由于工程包含外部依赖关系，不在构建时测试



### 自动构建

默认的触发构建事件为`commit`等

触发后会自动执行任务

[![1554278973797.png](/images/recovered/6962e7bec46dd02dd6fc.png)](/images/recovered/6962e7bec46dd02dd6fc.png)



[![1554279027476.png](/images/recovered/767eee344cf27e970b30.png)](/images/recovered/767eee344cf27e970b30.png)



Maven自动触发构建，自动镜像打包

[![1554279219445.png](/images/recovered/6a886ba9fd995a06044b.png)](/images/recovered/6a886ba9fd995a06044b.png)

[![1554279272711.png](/images/recovered/af376e5618731af03d84.png)](/images/recovered/af376e5618731af03d84.png)

自动上传（推送）镜像

[![1554279311054.png](/images/recovered/203756983dc32c4ee639.png)](/images/recovered/203756983dc32c4ee639.png)

### 执行结果

[![1554279508887.png](/images/recovered/8251f1ff39f3475408c3.png)](/images/recovered/8251f1ff39f3475408c3.png)

若执行失败则会发送邮件给开发人员

[![1554279616575.png](/images/recovered/88d0e56ab64d8fd3b57e.png)](/images/recovered/88d0e56ab64d8fd3b57e.png)



CICD全套流程目标实现！



## 总结

不管使用GitLab CICD或者是使用Jenkins+Ansible的方式，目标都在于践行DevOps，打通开发与运维流程，一旦配置好CICD流程，往后开发人员便不再操心打包、构建等操作，可以专注开发
