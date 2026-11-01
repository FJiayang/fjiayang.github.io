{
  "title": "DevOps GitLab CICD 实践1——GitLab 部署",
  "date": "2019-04-03T16:30:00+08:00",
  "lastmod": "2019-04-07T09:36:24+08:00",
  "typecho_cid": 205,
  "url": "/archives/205/",
  "comments": false,
  "draft": false,
  "slug": "205",
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

## 配置目标

- 邮件提示
- GitHub第三方授权登陆
- GitLab Runner
- Docker私服注册

## 官方介绍

目前微服务盛行环境下，服务部署优先考虑Docker方式，便于迁移和弹性伸缩

官方镜像介绍 [GitLab Docker images](https://docs.gitlab.com/omnibus/docker/)

> # GitLab Docker images
>
> Both GitLab CE and EE are in Docker Hub:
>
> - [GitLab CE Docker image](https://registry.hub.docker.com/u/gitlab/gitlab-ce/)
> - [GitLab EE Docker image](https://registry.hub.docker.com/u/gitlab/gitlab-ee/)
>
> The GitLab Docker images are monolithic images of GitLab running all the necessary services on a single container.
>
> In the following examples we are using the image of GitLab CE. To use GitLab EE instead of GitLab CE, replace the image name to `gitlab/gitlab-ee:latest`.
>
> If you want to use the latest RC image, use `gitlab/gitlab-ce:rc` or `gitlab/gitlab-ee:rc` for GitLab CE and GitLab EE respectively.
>
> The GitLab Docker images can be run in multiple ways:
>
> - [Run the image in Docker Engine](https://docs.gitlab.com/omnibus/docker/#run-the-image)
> - [Install GitLab into a cluster](https://docs.gitlab.com/omnibus/docker/#install-gitlab-into-a-cluster)
> - [Install GitLab using docker-compose](https://docs.gitlab.com/omnibus/docker/#install-gitlab-using-docker-compose)



## docker-compose 脚本

此处选择社区版(CE)安装，同时为了便于参数配置，使用`docker-compose`方式编写脚本文件

> ## Install GitLab using docker-compose
>
> With [Docker compose](https://docs.docker.com/compose/) you can easily configure, install, and upgrade your Docker-based GitLab installation.
>
> 1. [Install](https://docs.docker.com/compose/install/) Docker Compose
>
> 2. Create a `docker-compose.yml` file (or [download an example](https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/docker/docker-compose.yml)):
>
>    ```yaml
>     web:
>       image: 'gitlab/gitlab-ce:latest'
>       restart: always
>       hostname: 'gitlab.example.com'
>       environment:
>         GITLAB_OMNIBUS_CONFIG: |
>           external_url 'https://gitlab.example.com'
>           # Add any other gitlab.rb configuration here, each on its own line
>       ports:
>         - '80:80'
>         - '443:443'
>         - '22:22'
>       volumes:
>         - '/srv/gitlab/config:/etc/gitlab'
>         - '/srv/gitlab/logs:/var/log/gitlab'
>         - '/srv/gitlab/data:/var/opt/gitlab'
>    ```
>
> 3. Make sure you are in the same directory as `docker-compose.yml` and run `docker-compose up -d` to start GitLab
>
> Read [“Pre-configure Docker container”](https://docs.gitlab.com/omnibus/docker/#pre-configure-docker-container) to see how the `GITLAB_OMNIBUS_CONFIG` variable works.
>
> Below is another `docker-compose.yml` example with GitLab running on a custom HTTP and SSH port. Notice how the `GITLAB_OMNIBUS_CONFIG` variables match the `ports` section:
>
> ```yaml
> web:
>   image: 'gitlab/gitlab-ce:latest'
>   restart: always
>   hostname: 'gitlab.example.com'
>   environment:
>     GITLAB_OMNIBUS_CONFIG: |
>       external_url 'http://gitlab.example.com:9090'
>       gitlab_rails['gitlab_shell_ssh_port'] = 2224
>   ports:
>     - '9090:9090'
>     - '2224:22'
>   volumes:
>     - '/srv/gitlab/config:/etc/gitlab'
>     - '/srv/gitlab/logs:/var/log/gitlab'
>     - '/srv/gitlab/data:/var/opt/gitlab'
> ```
>
> This is the same as using `--publish 9090:9090 --publish 2224:22`.



官方提示说明Docker CE版基于`Omnibus`版本，故环境配置也可参考相关文档

### Omnibus文档目录

> #### Installation and Configuration using omnibus package
>
> **Note:** This section describes the commonly used configuration settings. Check [configuration](https://docs.gitlab.com/omnibus/README.html#configuring) section of the documentation for complete configuration settings.
>
> - Installing GitLab
>   - [Manually downloading and installing a GitLab package](https://docs.gitlab.com/omnibus/manual_install.html)
> - [Setting up a domain name/URL](https://docs.gitlab.com/omnibus/settings/configuration.html#configuring-the-external-url-for-gitlab) for the GitLab Instance so that it can be accessed easily
> - [Enabling HTTPS](https://docs.gitlab.com/omnibus/settings/nginx.html#enable-https)
> - [Enabling notification EMails](https://docs.gitlab.com/omnibus/settings/smtp.html#smtp-settings)
> - Enabling replying via email
>   - [Installing and configuring postfix](https://docs.gitlab.com/ce/administration/reply_by_email_postfix_setup.html)
> - Enabling container registry on GitLab
>   - You will require SSL certificates for the domain used for container registry
> - Enabling GitLab Pages
>   - If you want HTTPS enabled, you will have to get wildcard certificates
> - [Enabling Elasticsearch](https://docs.gitlab.com/ee/integration/elasticsearch.html)
> - [GitLab Mattermost](https://docs.gitlab.com/omnibus/gitlab-mattermost/README.html) Set up the Mattermost messaging app that ships with Omnibus GitLab package.
> - [GitLab Prometheus](https://docs.gitlab.com/ce/administration/monitoring/performance/prometheus.html) Set up the Prometheus monitoring included in the Omnibus GitLab package.
> - [GitLab High Availability Roles](https://docs.gitlab.com/omnibus/roles/README.html)







结合配置目标编写yaml文件

注意：

- 此处邮件使用163邮箱（官方没有提供163邮箱支持案例）
- Docker私服公钥执行从私服上获取
- 由于特殊原因，目标配置未启动SSL安全连接，但GitLab可以通过简单配置支持SSL并**自动更新证书**

[配置文档](https://docs.gitlab.com/omnibus/settings/ssl.html#lets-encrypthttpsletsencryptorg-integration)

> ### [Let’s Encrypt](https://letsencrypt.org/) Integration
>
> #### Primary GitLab Instance
>
> > **Note**: Introduced in GitLab version **10.5** and disabled by default. Enabled by default in GitLab version **10.7** and later if `external_url` is set with the *https*protocol and no certificates are configured.
>
> > **Note**: In order for Let’s Encrypt verification to work correctly, ports 80 and 443 will need to be accessible to the Let’s Encrypt servers that run the validation. Also note that the validation currently [does not work with non-standard ports](https://gitlab.com/gitlab-org/omnibus-gitlab/issues/3580).
>
> > **Caution** Administrators installing or upgrading to GitLab version **10.7** or later and do not plan on using **Let’s Encrypt** should set the following in `/etc/gitlab/gitlab.rb` to disable:
> >
> > ```properties
> > letsencrypt['enable'] = false
> > ```
>
> Add the following entries to `/etc/gitlab/gitlab.rb` to enable **Let’s Encrypt** support for the primary domain:
>
> ```properties
> letsencrypt['enable'] = true                      # GitLab 10.5 and 10.6 require this option
> external_url "https://gitlab.example.com"	  # Must use https protocol
> letsencrypt['contact_emails'] = ['foo@email.com'] # Optional
> ```



生成163邮箱授权密码

[![1554263126117.png](/images/recovered/e2c94689f680c2f60dcb.png)](/images/recovered/e2c94689f680c2f60dcb.png)



生成GitHub授权秘钥

[![1554262788318.png](/images/recovered/12d0e2dacab60ceaa061.png)](/images/recovered/12d0e2dacab60ceaa061.png)

[![1554262821319.png](/images/recovered/c3fdca4f2f7cf67ff04f.png)](/images/recovered/c3fdca4f2f7cf67ff04f.png)



最终配置

```yaml
version: '3.1'

services:

  gitlab:
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url '外部访问地址'
        gitlab_rails['gitlab_shell_ssh_port'] = 外部SSH端口
        registry_external_url 'Docker私服地址'
        registry_nginx['ssl_certificate'] = "Docker 私服CA证书 crt文件"
        registry_nginx['ssl_certificate_key'] = "Docker 私服公钥 pem文件"
        gitlab_rails['smtp_enable'] = true
        gitlab_rails['smtp_address'] = "smtp.163.com"
        gitlab_rails['smtp_port'] = 465
        gitlab_rails['smtp_user_name'] = "邮件发送者名称"
        gitlab_rails['gitlab_email_from'] = '邮件发送地址'
        gitlab_rails['smtp_password'] = "授权密码"
        gitlab_rails['smtp_domain'] = "163.com"
        gitlab_rails['smtp_authentication'] = "login"
        gitlab_rails['smtp_enable_starttls_auto'] = true
        gitlab_rails['smtp_tls'] = true
        gitlab_rails['omniauth_enabled'] = true
        gitlab_rails['omniauth_allow_single_sign_on'] = true
        gitlab_rails['omniauth_block_auto_created_users'] = true
        gitlab_rails['omniauth_providers'] = [
          {
            "name" => "github",
            "app_id" => "Client ID",
            "app_secret" => "Client Secret",
            "url" => "https://github.com/",
            "args" => { "scope" => "user:email" }
          }
        ]
    image: gitlab/gitlab-ce:latest
    hostname: gitlab.fjy8018.top
    restart: always
    networks:
    - devops-service-bridge
    ports:
    - '8443:443'
    - '8099:8099'
    - '8022:22'
    volumes:
    - ./srv/gitlab/config:/etc/gitlab
    - ./srv/gitlab/logs:/var/log/gitlab
    - ./srv/gitlab/data:/var/opt/gitlab
    - /etc/docker/certs.d:/etc/docker/certs.d


networks:
  devops-service-bridge:
    driver: bridge
```
