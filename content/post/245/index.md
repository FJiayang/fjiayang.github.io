{
  "title": "微服务平台开发总结（3）——第二代密码管理平台",
  "date": "2020-05-07T21:38:00+08:00",
  "lastmod": "2020-05-28T11:35:17+08:00",
  "typecho_cid": 245,
  "url": "/archives/245/",
  "comments": false,
  "draft": false,
  "slug": "245",
  "categories": [
    "开发",
    "学习",
    "总结"
  ],
  "tags": [
    "SpringCloud",
    "MyBatis",
    "Nacos",
    "Sentinel",
    "Turbine",
    "Vuex",
    "Avue",
    "Jwt"
  ],
  "math": false
}

### 背景

吸取前两代系统的失败经验，对第二代密码管理微服务进行重新规划，并且在探索过程中见识到了cloud-platform、SpringBlade、pigx等优秀的微服务项目，考虑基于开源项目二次开发

## 规划

为了尽快落地上线，第一期以实现最小功能为主，其他非必须功能尽可能往后放

### 第一期

- SpringCloud微服务集成
- Nacos、Sentinel、graylog、zipkin、 Turbine集成
- 前后端密码管理功能对接
- 操作日志记录
- 邮件通知
- Excel导入导出
- v1迁移到v2工具包

### 第二期

- dble读写分离
- 支持忘记密码、密码锁定等
- 集成微信推送、微信注册功能
- 支持上传前端日志
- 页面排序、检索优化

### 第三期

- 增加用户反馈功能
- 接入Seata分布式事务
- 支持配置导入导出权限
- 支持录入标签
- …

## 技术体系

### 前端

- 前后端分离-采用前后端分离模式，前端基于Vue
- 采用Vuex进行状态管理，采用ES6作为语法支持
- 前后端基于开源项目SpringBlade二次开发
- 前后端代码生成-定制针对两套前端与后端的代码生成模板，轻松生成整个模块的前后端代码，减少重复工作量
- 多租户顶部菜单配置-提供给每个租户独立的顶部菜单配置模块，可以自定义顶部菜单切换

### 后端

- 基于SpringCloud的分布式架构
- 采用Mybatis与MybatisPlus作为ORM持久层框架
- 多租户系统-完整的SaaS多租户架构
- 借鉴OAuth2，通过Jwt令牌实现了多终端认证系统，可控制子系统的token权限互相隔离
- 权限管理-精心设计的权限管理方案，角色权限精确到按钮
- 集成邮件服务，通过事件传播实现不依赖消息队列通知发送服务
- 集成微信推送服务，实现微信注册、敏感操作消息推送
- 动态聚合文档-实现基于Nacos的Swagger SpringCloud聚合文档
- 实现动态网关，不重启就能设置网关配置项
- 集成Turbine聚合熔断监控

### 数据架构

- 采用MySQL进行数据存储，底层配置为一主两从的高可用集群
- 采用ElasticSearch三节点集群进行日志数据存储

### 分布式支持

- Nacos-集成阿里巴巴的Nacos完成统一的服务注册与配置
- Sentinel-集成Sentinel从流量控制、熔断降级、系统负载等多个维度保护服务的稳定性
- 采用Docker打包，部署于Kubernetes集群上
- Seata分布式事务-定制集成Seata，支持分布式事务，无代码侵入，不失灵活与简洁
- 使用graylog进行分布式日志采集，集中监控
- 通过zipkin进行分布式链路追踪，耗时统计和服务调用情况

### DevOps

- 配置管理采用单仓库模式，集成docker打包插件，自动推送到harbor仓库
- 采用GitLab Runner CICD流水线自动部署到测试环境和生产环境
- 结合Maven私服和Harbor私服为内网自动化部署提供支持

## 官方架构图

 ![pw-cloud-v2架构图](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/pw-cloud-v2%E6%9E%B6%E6%9E%84%E5%9B%BE.jpg)

## 截图

### 管理员

操作日志记录

![1588579947777](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588579947777.png)

错误日志系统内采集

![1588581001650](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581001650.png)

Turbine集成熔断监控

![1588580468453](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580468453.png)

通知发布

![1588579968512](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588579968512.png)

### 普通用户

主题切换

![1588579979531](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588579979531.png)

微信扫码注册

![1588580114649](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580114649.png)

补全信息

![1588580190679](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580190679.png)

主页资源权限控制

![1588580246683](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580246683.png)



![1588584226440](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588584226440.png)

菜单资源权限控制

![1588580268145](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580268145.png)

Excel导入导出

![1588580286188](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580286188.png)

![1588580307993](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580307993.png)

![1588580302209](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580302209.png)

密码管理

![1588580328939](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580328939.png)

![1588580345585](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580345585.png)



![1588580360145](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580360145.png)



![1588580378111](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580378111.png)





![1588580423240](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580423240.png)

### 运维

Nacos注册中心

![1588581761146](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581761146.png)

Sentinel限流管控

![image-20200507154857570](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200507154857570.png)

SpringBoot Admin应用内指标监控

![image-20200521161617030](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200521161617030.png)

![image-20200521161630570](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200521161630570.png)

![image-20200521161745282](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200521161745282.png)

Harbor内网私服

![1588584874907](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588584874907.png)

Nexus内网私服，提供maven和npm包

![1588584922069](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588584922069.png)



graylog日志采集

![1588580515850](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580515850.png)

三节点ES集群支持日志存储

![1588581945300](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581945300.png)



![1588580536165](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580536165.png)

耗时统计

![1588580556444](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580556444.png)

新UI风格

![1588580850602](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580850602.png)

动态服务依赖关系图

![1588580591683](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580591683.png)

新UI依赖图

![1588580908961](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580908961.png)

Prometheus指标采集

![image-20200507154338613](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200507154338613.png)

Grafana资源指标监控

![1588580674840](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580674840.png)

![1588580713872](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580713872.png)

Kuberneties服务部署监控

![1588580784287](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580784287.png)

### 开发过程工具

Gitlab CICD流水线

![1588580803424](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580803424.png)

![1588580814213](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588580814213.png)

![1588581090189](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581090189.png)

看板

![1588581109459](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581109459.png)



![1588581124259](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581124259.png)

功能开发周期分析

![1588584966734](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588584966734.png)

gitlab集成k8s部署环境

![1588581135887](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588581135887.png)

Sonarqube代码质量检查

![1588584033088](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1588584033088.png)

分支图

![image-20200507155216967](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200507155216967.png)

工程模块图

![image-20200507155249468](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200507155249468.png)



## 结果——成功

经过两个月的开发和调试，第一期工程符合预定计划，按期投产上线运行，并经过2周试运行和测试后，进入生产环境，迁移老版本数据，正式替换了运行一年半的第一代密码管理系统

## 时间线

1. 2020年3月开始基于SpringBlade 2.6.2编码
2. 2020年4月20日第一个测试版本进入k8s测试环境
3. 2020年4月28日第一个稳定版进行试运行阶段
4. 2020年5月4日试运行阶段结束，第一个稳定版1.1.2发布，正式进行数据迁移并投入使用
