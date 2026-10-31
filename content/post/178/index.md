{
  "title": "Jenkins job编写测试",
  "date": "2018-08-26T12:00:00+08:00",
  "lastmod": "2018-08-26T19:20:03+08:00",
  "typecho_cid": 178,
  "url": "/archives/178/",
  "comments": false,
  "draft": false,
  "slug": "178",
  "categories": [
    "开发"
  ],
  "tags": [
    "Jenkins"
  ],
  "math": false
}

## 系统预配置
### 关闭防止跨站请求伪造
测试期间系统设置中临时关闭防止跨站请求伪造，否则容易出现登录超时无法新建任务
[![Jenkins10.png](https://i.loli.net/2018/08/26/5b821f7039ead.png)](https://i.loli.net/2018/08/26/5b821f7039ead.png)

[![Jenkins22.png](https://i.loli.net/2018/08/26/5b821f77db05d.png)](https://i.loli.net/2018/08/26/5b821f77db05d.png)
### 添加远程仓库配置
GitLab的用户邮箱、用户名、密码，用于拉取远程仓库代码
[![Jenkins11.png](https://i.loli.net/2018/08/26/5b821f702fa6f.png)](https://i.loli.net/2018/08/26/5b821f702fa6f.png)

### 凭据
添加凭据，凭据为用户的标识
[![Jenkins12.png](https://i.loli.net/2018/08/26/5b821f70357fd.png)](https://i.loli.net/2018/08/26/5b821f70357fd.png)

选择全局凭据
[![Jenkins13.png](https://i.loli.net/2018/08/26/5b821f7033e32.png)](https://i.loli.net/2018/08/26/5b821f7033e32.png)

添加凭据
[![Jenkins14.png](https://i.loli.net/2018/08/26/5b821f703124d.png)](https://i.loli.net/2018/08/26/5b821f703124d.png)

添加为Git用户
[![Jenkins15.png](https://i.loli.net/2018/08/26/5b821f7038826.png)](https://i.loli.net/2018/08/26/5b821f7038826.png)

## Jenkins job
### freestyle Job
#### freestyle Job简介
1. 需要在页面添加模块配置项与参数完成配置
2. 每个Job仅能实现一个开发功能
3. 无法将配置代码化，不利于Job配置迁移与版本控制
4. 没有版本日志记录
5. 逻辑简单

#### 新建freestyle Job
新建任务
[![Jenkins16.png](https://i.loli.net/2018/08/26/5b821f7036e38.png)](https://i.loli.net/2018/08/26/5b821f7036e38.png)

添加选项参数
[![Jenkins17.png](https://i.loli.net/2018/08/26/5b821f70329b8.png)](https://i.loli.net/2018/08/26/5b821f70329b8.png)

添加文本参数
[![Jenkins18.png](https://i.loli.net/2018/08/26/5b821f702e141.png)](https://i.loli.net/2018/08/26/5b821f702e141.png)

指定远程仓库地址
[![Jenkins19.png](https://i.loli.net/2018/08/26/5b821f702a326.png)](https://i.loli.net/2018/08/26/5b821f702a326.png)

添加Shell脚本
[![Jenkins20.png](https://i.loli.net/2018/08/26/5b821f77dc787.png)](https://i.loli.net/2018/08/26/5b821f77dc787.png)

[![Jenkins21.png](https://i.loli.net/2018/08/26/5b821f77e46e7.png)](https://i.loli.net/2018/08/26/5b821f77e46e7.png)

保存后选择通过参数构建
[![Jenkins23.png](https://i.loli.net/2018/08/26/5b821f77dde13.png)](https://i.loli.net/2018/08/26/5b821f77dde13.png)

构建报错
[![Jenkins28.png](https://i.loli.net/2018/08/26/5b821f77e2de2.png)](https://i.loli.net/2018/08/26/5b821f77e2de2.png)

检查后发现Shell脚本开头的`#!/bin/bash`写成了`#! /bin/bash`，中间包含空格后系统无法识别

修正错误后重新构建
[![Jenkins24.png](https://i.loli.net/2018/08/26/5b821f77e5ba4.png)](https://i.loli.net/2018/08/26/5b821f77e5ba4.png)

报语法错误，12行缺少空格
[![Jenkins30.png](https://i.loli.net/2018/08/26/5b821f7d24a0b.png)](https://i.loli.net/2018/08/26/5b821f7d24a0b.png)

检查发现`if [ -s test.properties ]`写成了`if [ -s test.properties]`，修正错误后再次构建
修正后的Shell脚本为
```
#!/bin/bash
# export PATH="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin"

# 打印环境变量
echo "[INFO] 打印环境变量"
echo "[INFO] 当前发布环境为 $deploy_env" >> test.properties
echo "[INFO] 构建版本为 $version " >> test.properties
echo "[INFO] 打印环境变量完成..."

# 检查test.properties
echo "[INFO] 检查test.properties"
if [ -s test.properties ]
then
  cat test.properties
  echo "[INFO] 检查完成..."
else
  echo "[WARN] test.properties为空"
fi

echo "[INFO] 构建完成..."
```
构建成功，输出正常
[![Jenkins29.png](https://i.loli.net/2018/08/26/5b821f77df647.png)](https://i.loli.net/2018/08/26/5b821f77df647.png)


查看构建历史
[![Jenkins25.png](https://i.loli.net/2018/08/26/5b821f77d9a0b.png)](https://i.loli.net/2018/08/26/5b821f77d9a0b.png)

[![Jenkins27.png](https://i.loli.net/2018/08/26/5b821f77e1271.png)](https://i.loli.net/2018/08/26/5b821f77e1271.png)

同时显示构建稳定性
[![Jenkins26.png](https://i.loli.net/2018/08/26/5b821f77d85c4.png)](https://i.loli.net/2018/08/26/5b821f77d85c4.png)

### pipeline job
#### pipeline job简介
1. 所有代码包裹在pipeline{}内
2. stages{}用来包含pipeline所有子层
3. stage(管道名称){}每个子层可以执行一个任务，并不互相影响
4. steps{}用来添加具体需要调用的模块语句

#### 新建pipeline任务
[![Jenkins31.png](https://i.loli.net/2018/08/26/5b821f7d279f0.png)](https://i.loli.net/2018/08/26/5b821f7d279f0.png)

#### 编写pipeline 脚本
```
#!groovy

pipeline {
    // agent 定义pipeline在何处运行，使用any、none或者Jenkins node主机名
	agent {node {label 'master'}}
	// 声明环境变量，environment 定义系统环境变量，可以应用于所有stages
	// 定义局部环境变量则于steps平级即可
	environment {
		PATH="/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin"
	}

	parameters {
		// 声明可选参数
		choice(
				// 可选参数为两个，以空行分隔
				choices: 'dev\nprod',
				// 设置参数描述
				description: '选择发布环境',
				// 声明参数变量名
				name: 'deploy_env'
			)
		// 声明文本参数，和默认值
		string (name: 'version', defaultValue: '0.0.1',description: '构建版本号')
	}

	stages {
		// 执行一个任务
		stage("切换到测试版本仓库") {
			// 添加具体需要调用的模块语句
			steps {
				// 关闭Git ssl安全认证
				sh 'git config --system http.sslVerify false'
				// 指定工作空间
				dir ("${env.WORKSPACE}") {
					// 指定分支和Jenkins凭据ID
					git branch: 'master',
						credentialsId: '52f4c34f-544c-4830-828d-6691d603b8e4',
						url: 'http://home.fjy8018.top:8099/jenkins/test-repo.git'
				}
			}
		}
		stage("打印环境变量") {
			steps {
				dir ("${env.WORKSPACE}") {
					sh """
						echo "[INFO] 打印环境变量"
						echo "[INFO] 当前发布环境为 $deploy_env" >> test.properties
						echo "[INFO] 构建版本为 $version " >> test.properties
						echo "[INFO] 打印环境变量完成..."
					"""
				}
			}
		}
		stage("检查test.properties") {
			steps {
				dir ("${env.WORKSPACE}") {
					sh """
						echo "[INFO] 检查test.properties"
						if [ -s test.properties ]
						then
						  cat test.properties
						  echo "[INFO] 检查完成..."
						else
						  echo "[WARN] test.properties为空"
						fi
					"""
					echo "[INFO] 构建完成..."
				}
			}
		}
	}
}
```
其中`credentialsId`来自用户的凭据唯一标识，可在凭据页面查看
[![Jenkins32.png](https://i.loli.net/2018/08/26/5b821f7d23347.png)](https://i.loli.net/2018/08/26/5b821f7d23347.png)

#### 写入Shell脚本
[![Jenkins33.png](https://i.loli.net/2018/08/26/5b821f7d204fe.png)](https://i.loli.net/2018/08/26/5b821f7d204fe.png)

执行报错，`error: could not lock config file /etc/gitconfig: ????`
[![Jenkins34.png](https://i.loli.net/2018/08/26/5b821f7d21c71.png)](https://i.loli.net/2018/08/26/5b821f7d21c71.png)



由于使用root用户执行同样命令不会报错，故猜测没有权限，修改语法为`git config --global http.sslVerify false`即可
重新构建
[![Jenkins35.png](https://i.loli.net/2018/08/26/5b821f7d294a2.png)](https://i.loli.net/2018/08/26/5b821f7d294a2.png)

日志符合预期
[![Jenkins36.png](https://i.loli.net/2018/08/26/5b821f7d1bde0.png)](https://i.loli.net/2018/08/26/5b821f7d1bde0.png)

### freestyle shell Job
新建任务
[![Jenkins37.png](https://i.loli.net/2018/08/26/5b821f7d1ec30.png)](https://i.loli.net/2018/08/26/5b821f7d1ec30.png)

写入shell脚本如下
```
#!/bin/bash

user=`whoami`

if [ $user == 'deploy' ]; then
	echo "成功，当前用户为 $user"
else
	echo "失败，当前用户不是 $user"
fi
# 查看主机ip
ip addr
# 查看系统版本
cat /etc/system-release
# 查看内存状态
free -m
# 查看磁盘状态
df -h
# 将python安装位置赋值给变量
py_cmd=`which python`
# 查看python版本号
$py_cmd --version
```
[![Jenkins38.png](https://i.loli.net/2018/08/26/5b821f7d1d3a0.png)](https://i.loli.net/2018/08/26/5b821f7d1d3a0.png)

运行并查看日志，符合预期
[![Jenkins39.png](https://i.loli.net/2018/08/26/5b821f7d26264.png)](https://i.loli.net/2018/08/26/5b821f7d26264.png)

### 参数任务
新建参数化构建任务
[![Jenkins44.png](https://i.loli.net/2018/08/26/5b82700347046.png)](https://i.loli.net/2018/08/26/5b82700347046.png)

添加选项参数等
[![Jenkins45.png](https://i.loli.net/2018/08/26/5b8270034698e.png)](https://i.loli.net/2018/08/26/5b8270034698e.png)

添加shell构建参数
[![Jenkins46.png](https://i.loli.net/2018/08/26/5b8270034511c.png)](https://i.loli.net/2018/08/26/5b8270034511c.png)

构建
[![Jenkins47.png](https://i.loli.net/2018/08/26/5b82700345d4a.png)](https://i.loli.net/2018/08/26/5b82700345d4a.png)

输出符合预期
[![Jenkins48.png](https://i.loli.net/2018/08/26/5b82700341009.png)](https://i.loli.net/2018/08/26/5b82700341009.png)
