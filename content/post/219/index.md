{
  "title": "GitLab Api使用",
  "date": "2019-11-06T15:01:04+08:00",
  "lastmod": "2019-11-06T15:01:04+08:00",
  "typecho_cid": 219,
  "url": "/archives/219/",
  "comments": false,
  "draft": false,
  "slug": "219",
  "categories": [
    "开发"
  ],
  "tags": [
    "GitLab",
    "bash"
  ],
  "math": false
}

## 使用场景

为了进行规范化配置管理工作，基于`gitlab`规范分支管理流程，经常需要新建分支、设置保护分支和操作分支封板等，若只有几个工程则直接在`gitlab` web界面上操作即可，一旦工程数量增多，则会消耗大量时间，故考虑可通过`gitlab `提供的web `api`编写脚本进行自动化操作

## Api指南

此处摘要部分[官网](https://docs.gitlab.com/ee/api/)`API`文档指南，所有`api`操作都需要在`gitlab`上申请访问令牌，该令牌应当至少包含api访问权限

![image-20191106101754287](/images/recovered/770f238044d33171139f.png)

### 获取工程列表

支持多种参数过滤，非必传

> Get a list of all visible projects across GitLab for the authenticated user. When accessed without authentication, only public projects with “simple” fields are returned.
>
> ```
> GET /projects
> ```
>
> | Attribute                     | Type    | Required | Description                                                  |
> | :---------------------------- | :------ | :------- | :----------------------------------------------------------- |
> | `archived`                    | boolean | no       | Limit by archived status                                     |
> | `visibility`                  | string  | no       | Limit by visibility `public`, `internal`, or `private`       |
> | `order_by`                    | string  | no       | Return projects ordered by `id`, `name`, `path`, `created_at`, `updated_at`, or `last_activity_at` fields. Default is `created_at` |
> | `sort`                        | string  | no       | Return projects sorted in `asc` or `desc` order. Default is `desc` |
> | `search`                      | string  | no       | Return list of projects matching the search criteria         |
> | `simple`                      | boolean | no       | Return only limited fields for each project. This is a no-op without authentication as then *only* simple fields are returned. |
> | `owned`                       | boolean | no       | Limit by projects explicitly owned by the current user       |
> | `membership`                  | boolean | no       | Limit by projects that the current user is a member of       |
> | `starred`                     | boolean | no       | Limit by projects starred by the current user                |
> | `statistics`                  | boolean | no       | Include project statistics                                   |
> | `with_custom_attributes`      | boolean | no       | Include [custom attributes](https://docs.gitlab.com/ee/api/custom_attributes.html) in response (admins only) |
> | `with_issues_enabled`         | boolean | no       | Limit by enabled issues feature                              |
> | `with_merge_requests_enabled` | boolean | no       | Limit by enabled merge requests feature                      |
> | `with_programming_language`   | string  | no       | Limit by projects which use the given programming language   |
> | `wiki_checksum_failed`        | boolean | no       | Limit projects where the wiki checksum calculation has failed ([Introduced](https://gitlab.com/gitlab-org/gitlab/merge_requests/6137) in [GitLab Premium](https://about.gitlab.com/pricing/) 11.2) |
> | `repository_checksum_failed`  | boolean | no       | Limit projects where the repository checksum calculation has failed ([Introduced](https://gitlab.com/gitlab-org/gitlab/merge_requests/6137) in [GitLab Premium](https://about.gitlab.com/pricing/) 11.2) |
> | `min_access_level`            | integer | no       | Limit by current user minimal [access level](https://docs.gitlab.com/ee/api/members.html) |



### 分支操作

[文档地址](https://docs.gitlab.com/ee/api/branches.html)

#### 创建分支

需要传递仓库ID、源分支名、新分支名称

> Create a new branch in the repository.
>
> ```
> POST /projects/:id/repository/branches
> ```
>
> Parameters:
>
> | Attribute | Type    | Required | Description                                                  |
> | :-------- | :------ | :------- | :----------------------------------------------------------- |
> | `id`      | integer | yes      | ID or [URL-encoded path of the project](https://docs.gitlab.com/ee/api/README.html#namespaced-path-encoding) owned by the authenticated user. |
> | `branch`  | string  | yes      | Name of the branch.                                          |
> | `ref`     | string  | yes      | Branch name or commit SHA to create branch from.             |
>
> Example request:
>
> ```bash
> curl --request POST --header "PRIVATE-TOKEN: <your_access_token>" https://gitlab.example.com/api/v4/projects/5/repository/branches?branch=newbranch&ref=master
> ```

#### 保护分支

分支保护等级说明

> **Valid access levels**
>
> The access levels are defined in the `ProtectedRefAccess.allowed_access_levels` method. Currently, these levels are recognized:
>
> ```bash
> 0  => No access
> 30 => Developer access
> 40 => Maintainer access
> 60 => Admin access
> ```



需要传递分支名称、访问级别等信息

> Protects a single repository branch or several project repository branches using a wildcard protected branch.
>
> ```bash
> POST /projects/:id/protected_branches
> curl --request POST --header "PRIVATE-TOKEN: <your_access_token>" 'https://gitlab.example.com/api/v4/projects/5/protected_branches?name=*-stable&push_access_level=30&merge_access_level=30&unprotect_access_level=40'
> ```
>
> | Attribute                      | Type           | Required | Description                                                  |
> | :----------------------------- | :------------- | :------- | :----------------------------------------------------------- |
> | `id`                           | integer/string | yes      | The ID or [URL-encoded path of the project](https://docs.gitlab.com/ee/api/README.html#namespaced-path-encoding) owned by the authenticated user |
> | `name`                         | string         | yes      | The name of the branch or wildcard                           |
> | `push_access_level`            | string         | no       | Access levels allowed to push (defaults: `40`, maintainer access level) |
> | `merge_access_level`           | string         | no       | Access levels allowed to merge (defaults: `40`, maintainer access level) |
> | `unprotect_access_level`       | string         | no       | Access levels allowed to unprotect (defaults: `40`, maintainer access level) |
> | `allowed_to_push`              | array          | no       | Array of access levels allowed to push, with each described by a hash |
> | `allowed_to_merge`             | array          | no       | Array of access levels allowed to merge, with each described by a hash |
> | `allowed_to_unprotect`         | array          | no       | Array of access levels allowed to unprotect, with each described by a hash |
> | `code_owner_approval_required` | boolean        | no       | Prevent pushes to this branch if it matches an item in the [`CODEOWNERS` file](https://docs.gitlab.com/ee/user/project/code_owners.html). (defaults: false) |



#### 取消保护分支

需要传递仓库ID、分支名称

> Unprotects the given protected branch or wildcard protected branch.
>
> ```
> DELETE /projects/:id/protected_branches/:name
> curl --request DELETE --header "PRIVATE-TOKEN: <your_access_token>" 'https://gitlab.example.com/api/v4/projects/5/protected_branches/*-stable'
> ```
>
> | Attribute | Type           | Required | Description                                                  |
> | :-------- | :------------- | :------- | :----------------------------------------------------------- |
> | `id`      | integer/string | yes      | The ID or [URL-encoded path of the project](https://docs.gitlab.com/ee/api/README.html#namespaced-path-encoding) owned by the authenticated user |
> | `name`    | string         | yes      | The name of the branch                                       |



#### 删除分支

需要传递仓库ID和分支名称

> Delete a branch from the repository.
>
> **Note:** In the case of an error, an explanation message is provided.
>
> ```
> DELETE /projects/:id/repository/branches/:branch
> ```
>
> Parameters:
>
> | Attribute | Type           | Required | Description                                                  |
> | :-------- | :------------- | :------- | :----------------------------------------------------------- |
> | `id`      | integer/string | yes      | ID or [URL-encoded path of the project](https://docs.gitlab.com/ee/api/README.html#namespaced-path-encoding) owned by the authenticated user. |
> | `branch`  | string         | yes      | Name of the branch.                                          |
>
> Example request:
>
> ```bash
> curl --request DELETE --header "PRIVATE-TOKEN: <your_access_token>" https://gitlab.example.com/api/v4/projects/5/repository/branches/newbranch
> ```



## 接口测试

使用postman对接口进行测试

### 获取工程列表

通过该接口可以查询所有工程的ID，注意，该接口默认使用了分页

![image-20191106102650310](/images/recovered/f14504786f7edd67c402.png)



## 脚本编写

### 批量创建分支

定义工程ID数组，对数组进行遍历，并设置基础分支变量，方便调整，此处默认写死基础分支，有需要也可以通过变量传递

```bash
#!/usr/bin/env bash

# 访问令牌
PRIVATE_TOKEN="XXXX"
# 分支名称
branch_name=$1

base_branch="BasicBranch"

# 项目ID
projectids=(47 48 50 51 52 54 55 56 58 59 60 62 63 64 65 67 68 69 70 71 74 75 89 90 91 92 93 95 103 104 113 114 115 143)

for id in "${projectids[@]}" ; do
	curl --request POST --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" "http://10.139.6.26:7077/api/v4/projects/$id/repository/branches?branch=$branch_name&ref=$base_branch"
done
```



### 批量保护分支

此处写死了分支访问级别，可参照上文的参数进行配置

```bash
#!/usr/bin/env bash

# 访问令牌
PRIVATE_TOKEN="XXXX"
# 分支名称
branch_name=$1

# 项目ID
projectids=(47 48 50 51 52 54 55 56 58 59 60 62 63 64 65 67 68 69 70 71 74 75 89 90 91 92 93 95 103 104 113 114 115 143)

for id in "${projectids[@]}" ; do
    # 访问权限均为 Maintainer access
    curl --request POST --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" "http://10.139.6.26:7077/api/v4/projects/$id/protected_branches?name=$branch_name&push_access_level=40&merge_access_level=40&unprotect_access_level=40"
done
```



### 批量取消保护分支

调用对应的删除接口即可

```bash
#!/usr/bin/env bash

# 访问令牌
PRIVATE_TOKEN="XXXX"
# 分支名称
branch_name=$1

# 项目ID
projectids=(47 48 50 51 52 54 55 56 58 59 60 62 63 64 65 67 68 69 70 71 74 75 89 90 91 92 93 95 103 104 113 114 115 143)

for id in "${projectids[@]}" ; do
    # 访问权限均为 Maintainer access
    curl --request DELETE --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" "http://10.139.6.26:7077/api/v4/projects/$id/protected_branches/$branch_name"
done
```



### 批量分支封板

分支封板即设置访问级别为`no one`

```bash
#!/usr/bin/env bash

# 访问令牌
PRIVATE_TOKEN="XXXX"
# 分支名称
branch_name=$1

# 项目ID
projectids=(47 48 50 51 52 54 55 56 58 59 60 62 63 64 65 67 68 69 70 71 74 75 89 90 91 92 93 95 103 104 113 114 115 143)

for id in "${projectids[@]}" ; do
    # 分支封板
    curl --request POST --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" "http://10.139.6.26:7077/api/v4/projects/$id/protected_branches?name=$branch_name&push_access_level=0&merge_access_level=0&unprotect_access_level=40"
done
```



### 批量删除分支

删除分支属于危险操作，操作需谨慎，因为不管是否为保护分支，都可以直接删除，而且通过api操作不会弹出确认操作

```bash
#!/usr/bin/env bash

# 访问令牌
PRIVATE_TOKEN="XXXX"
# 分支名称
branch_name=$1

# 项目ID
projectids=(47 48 50 51 52 54 55 56 58 59 60 62 63 64 65 67 68 69 70 71 74 75 89 90 91 92 93 95 103 104 113 114 115 143)

for id in "${projectids[@]}" ; do
    echo "删除项目ID：$id 的 $branch_name 分支"
    curl --request DELETE --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" "http://10.139.6.26:7077/api/v4/projects/$id/repository/branches/$branch_name"
done
```
