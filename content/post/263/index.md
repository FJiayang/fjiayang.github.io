{
  "title": "DevOps实践心得二",
  "date": "2020-12-27T12:25:47+08:00",
  "lastmod": "2020-12-27T12:25:47+08:00",
  "typecho_cid": 263,
  "url": "/archives/263/",
  "comments": false,
  "draft": false,
  "slug": "263",
  "categories": [
    "开发"
  ],
  "tags": [
    "mesos",
    "DevOps",
    "marathon",
    "Kubernetes"
  ],
  "math": false
}

## 背景

上一篇DevOps实践心得编写于2019年08月16日

[相关文章](/archives/213/)



文章最后提到未来探索方向是

> - 全面容器化服务治理方向
>   - 国内对容器化有非常多的实践
>   - `kubernetes`作为容器调度成为大多数服务治理的选择
>   - 容器隔离、迁移和伸缩带来的巨大优势
> - 容器与传统应用部署结合方式
>   - 以半全自动方式落地`DevOps`，采用`Mesos`+`marathon`方式同时兼容传统服务部署和容器化部署
>   - 兼容分布式服务治理
>   - 国外有大量的实践案例
>   - 日志收集体系完备

经过一年半的时间，完成对完整DevOps的探索



## Mesos+Marathon的DevOps分布式环境探索

参考文章

[相关文章](/archives/215/)



该架构更加适合还未进行容器化改造的项目，其支持较为通用，但各组件都是由开源组件协调而成，故搭建较为繁琐，而且后续版本升级并不方便



## 全面容器化服务探索

探索历程

[相关文章](/archives/217/)



[相关文章](/archives/218/)



[相关文章](/archives/220/)



[相关文章](/archives/221/)



最终完成了DevOps容器化自动部署实践

[相关文章](/archives/227/)



采用kuberneties方案，其统一性更加一致，依赖的基础设施也多支持容器化部署，机器利用率较高，版本升级、维护较为方便，适用于云原生项目部署





## 遇到的坑

最终生产环境采用kuberneties集群方案，5个节点，但由于实施经验不足，依然遇到不少坑

[相关文章](/archives/262/)





## 后续发展展望

云原生技术还在不断发展中，不少公司也研发并开源关于kuberneties集群管理方案，例如`kubesphere`

[kubesphere](https://kubesphere.io/) — The Kubernetes platform tailored for hybrid multicloud

![kubesphere](/images/recovered/10394e73acf79a23f18c.svg)



经过测试，其2.x版本资源占用较高，还处于刚起步阶段，暂时不适用于小规模集群
