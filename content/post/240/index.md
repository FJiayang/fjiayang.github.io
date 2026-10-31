{
  "title": "Git工作使用笔记",
  "date": "2020-03-13T14:08:00+08:00",
  "lastmod": "2020-03-17T15:11:29+08:00",
  "typecho_cid": 240,
  "url": "/archives/240/",
  "comments": false,
  "draft": false,
  "slug": "240",
  "categories": [
    "学习"
  ],
  "tags": [
    "git"
  ],
  "image": "/images/recovered/7029ed877105a9b0efec.png",
  "math": false
}

## 分离头指针

当前分支图

![image-20200313100955490](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313100955490.png)

切换到之前的某一次提交

![image-20200313101041682](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313101041682.png)



执行命令

```bash
$ git checkout de11fa87ea
```



提示，当前位于“分离头指针”状态

![image-20200313101137934](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313101137934.png)



分支图

![image-20200313101230748](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313101230748.png)

注意

- 在分离头指针状态下没有绑定分支
- 产生的commit不会被保存
- 分支切换后在分支图中看不到该commit
- **一段时间**后会被git自动清除



使用场景

- 尝试性做一些变更，可以随时丢弃



此处演示分离头指针丢失commit的情况和补救措施

### 丢失commit

使用IDE修改文件并提交，忽略所有警告，修改后分支图如下

![image-20200313101811004](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313101811004.png)

此时接到其他需求，需要切换分支进行紧急修复

执行命令

```bash
$ git checkout master
```



分支切换成功，并弹出提示和告警

> Warning: you are leaving 1 commit behind, not connected to
> any of your branches:
>
>   199ac20 游离状态修改文件
>
> If you want to keep it by creating a new branch, this may be a good time
> to do so with:
>
>  git branch <new-branch-name> 199ac20
>
> Switched to branch 'master'
> Your branch is up to date with 'origin/master'.

![image-20200313101817932](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313101817932.png)



此时查看分支图，刚才的commit已经不可见

![image-20200313102044269](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102044269.png)

### 补救

此时发现刚才的commit十分重要，可根据git的提示进行补救

执行命令

```bash
$ git branch hot-fix 199ac20
```



再次查看分支图，可见commit已经恢复

![image-20200313102203644](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102203644.png)

## 本地分支操作

以下操作仅适用于本地分支，无远程分支协同工作的情况



### 修改当前commit的message——`amend`

当前分支图

![image-20200313102633268](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102633268.png)

执行命令

```bash
$ git commit --amend
```

自动弹出编辑器

![image-20200313102714191](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102714191.png)



修改后保存并关闭编辑器即可，输出如下

![image-20200313102735178](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102735178.png)



再次查看分支图

![image-20200313102751917](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102751917.png)



### 修改前面某次commit的message——`rebase`

现计划修改如下message

![image-20200313102837128](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102837128.png)



使用IDE拷贝其父提交的SHA值

![image-20200313102938536](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313102938536.png)



执行命令，`-i`表示交互式执行

```bash
$ git rebase -i 199ac203c90f881024c6870d56517df9e2080841
```



自动弹出编辑器

![image-20200313103103273](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313103103273.png)



同时包含提示操作

> Rebase 199ac20..bfe2b7f onto 199ac20 (3 commands)
>
> Commands:
> p, pick <commit> = use commit
> r, reword <commit> = use commit, but edit the commit message
> e, edit <commit> = use commit, but stop for amending
> s, squash <commit> = use commit, but meld into previous commit
> f, fixup <commit> = like "squash", but discard this commit's log message
> x, exec <command> = run command (the rest of the line) using shell
> b, break = stop here (continue rebase later with 'git rebase --continue')
> d, drop <commit> = remove commit
> l, label <label> = label current HEAD with a name
> t, reset <label> = reset HEAD to a label
> m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
> .       create a merge commit using the original merge commit's
> .       message (or the oneline, if no original merge commit was
> .       specified). Use -c <commit> to reword the commit message.
>
> These lines can be re-ordered; they are executed from top to bottom.
>
> If you remove a line here THAT COMMIT WILL BE LOST.
>
> However, if you remove everything, the rebase will be aborted.
>
> Note that empty commits are commented out



由此可见“变基”支持很多操作，此处需要使用的是`reword`，修改目标提交的命令为`r`

![image-20200313103140977](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313103140977.png)



保存并关闭编辑器，会自动弹出新编辑器界面

![image-20200313103156452](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313103156452.png)



修改后保存并关闭即可，输出如下

![image-20200313103234131](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313103234131.png)



查看分支图

![image-20200313103250780](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313103250780.png)



### 整理连续多个commit——`rebase`

现计划合并3个commit

![image-20200313104229297](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313104229297.png)

使用IDE拷贝其父SHA值

![image-20200313104256202](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313104256202.png)

执行命令

```bash
$ git rebase -i 199ac203c90f881024c6870d56517df9e2080841
```



此处使用`squash`，官方介绍如下

> s, squash <commit> = use commit, but meld into previous commit



修改内容如下，说明将中间两个合并进第一个commit中

![image-20200313104553536](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313104553536.png)



保存后关闭，会弹出新的编辑器界面，提示可以输出合并commit的message

![image-20200313104708882](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313104708882.png)



编写message

![image-20200313104849690](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313104849690.png)



保存后关闭，提示修改成功

![image-20200313105805083](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313105805083.png)



查看分支图

![image-20200313105829642](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313105829642.png)

## 分支合并策略

演示不同分支合并策略效果，当前的分支图如下

![1584157562406](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584157562406.png)

现在将hot-fix合并进master

### GitLab默认合并策略——`merge commit`

gitlab默认合并请求使用的策略

![1584157617890](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584157617890.png)

![1584157635041](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584157635041.png)

由于没有冲突，可以线上直接合并

其对应执行的命令如下

> **Step 1.** Fetch and check out the branch for this merge request
>
> ```bash
> $ git fetch origin
> $ git checkout -b hot-fix origin/hot-fix
> ```
>
> **Step 2.** Review the changes locally
>
> **Step 3.** Merge the branch and fix any conflicts that come up
>
> ```bash
> $ git fetch origin
> $ git checkout origin/master
> $ git merge --no-ff hot-fix
> ```
>
> **Step 4.** Push the result of the merge to GitLab
>
> ```bash
> $ git push origin master
> ```

合并完成

![1584157751505](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584157751505.png)

查看分支图，故当前分支会影响特性分支并产生新的提交

![1584157894622](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584157894622.png)



### GitLab合并提交策略

提交合并请求的时候勾选策略`Squash commits when merge request is accepted`

![1584158031481](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584158031481.png)

![1584158086855](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584158086855.png)

其对应执行的命令如下（与默认策略一致）

> **Step 1.** Fetch and check out the branch for this merge request
>
> ```bash
> $ git fetch origin
> $ git checkout -b hot-fix origin/hot-fix
> ```
>
> **Step 2.** Review the changes locally
>
> **Step 3.** Merge the branch and fix any conflicts that come up
>
> ```bash
> $ git fetch origin
> $ git checkout origin/master
> $ git merge --no-ff hot-fix
> ```
>
> **Step 4.** Push the result of the merge to GitLab
>
> ```bash
> $ git push origin master
> ```

合并成功

![1584158157862](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584158157862.png)

查看分支图，可见其影响特性分支，会产生新的提交，同时覆盖特性分支最后一次提交

![1584158250648](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584158250648.png)



### 分支合并策略——`squash merge`

GitHub支持`squash merge`合并策略，此处通过命令行执行测试

```bash
$ git merge --squash origin/hot-fix
$ git commit -m "squash commit"
```



查看分支图，特性分支不变，目标分支合并提交后产生一条提交，效果与GitLab合并提交类似，但命令使用方式不同

![1584158902921](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584158902921.png)



**注意：`squash merge`会变更提交者作者信息，这是一个很大的问题，后期问题追溯不好处理**

### 变基合并策略——`rebase merge`

该策略也是GitHub支持的合并策略，可能会产生较多冲突

![1584159613476](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584159613476.png)

选择合并策略，最后一种即变基合并策略

![1584159638818](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584159638818.png)

![1584159659905](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584159659905.png)

合并成功

![1584159671515](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584159671515.png)

查看分支图，其产生的三次提交即变基合并的结果，不会影响特性分支，也不会变更提交人，类似`cherry pick`

![1584159735805](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/1584159735805.png)



## 分支回滚策略

回滚策略分为两种，一种是合并后回滚，一种是普通提交回滚，不同回滚策略操作方法不同



### 普通提交回滚

当前分支图，计划回滚最新提交

![image-20200317114811482](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317114811482.png)

直接在IDE中执行`revert`操作即可

![image-20200317114905943](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317114905943.png)

![image-20200317114935874](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317114935874.png)



回滚会产生新的提交，回滚结束

![image-20200317114957310](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317114957310.png)



### 合并后回滚

此时分支图，使用`merge commit`方式进行过一次合并，此时不想要合并的结果，想恢复到未合并状态

![image-20200317115211900](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317115211900.png)

#### 错误操作——直接执行`revert`

此时IDE已经不支持通过revert进行回滚合并操作，通过命令行强行执行

查找SHA值

![image-20200317115622215](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317115622215.png)

回滚`merge`需要加上`-m`参数git就知道到底要revert哪一个merge 

```bash
$ git revert -n 25d7b405a4d50fe1b36019d90276973a8ed9160d -m 1
```



回滚后做一次commit即可，使用默认的message后如下

![image-20200317120022233](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317120022233.png)

验证回滚结果，使用两个提交进行差异比对

![image-20200317122223636](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317122223636.png)

无差异，回滚看似成功了

<img src="https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317122240317.png" alt="image-20200317122240317" style="zoom:50%;" />

此时在原分支做了修复后再进行合并

![image-20200317141053618](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317141053618.png)

报无法合并，因为分支已经进行过合并

![image-20200317141147054](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317141147054.png)



#### 正确操作——`reset`

使用reset操作到上一次提交

![image-20200317141254057](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317141254057.png)

使用`--hard`参数，丢弃后续的commit

![image-20200317141341299](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317141341299.png)

![image-20200317141418080](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317141418080.png)

此时继续进行操作，并支持重新合并

![image-20200317141504021](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200317141504021.png)



## 禁止类操作

**说明：禁止类说明是对开发人员禁止，而该命令在必要时候依然需要由配置管理员使用**



### `push -f`

官方使用说明

> -f, --force           force updates



原因：

- 默认情况下远端分支若能顺利合并（fast forward），则会顺利合并
- 若远端分支产生冲突，则会停止push，同时提示错误，要pull到本地处理冲突后重新push
- 加`-f`之后，本地分支会强行推送到远端，若本地分支落后于远端分支也**不会弹出提示**，由此导致远程**commit丢失**



适用场景：

- 远程分支已经混乱，本地分支符合需要，需要强制整理远程分支





### 公共分支禁止`rebase`

此处对场景进行模拟，正常情况下，多位开发者对公共分支`common-branch`进行修改，分支图如下

![image-20200313144526583](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313144526583.png)

另一开发者在本地修改后执行变基操作，此处以修改历史提交message为例

![image-20200313150137509](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313150137509.png)



变基

![image-20200313150232682](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313150232682.png)

录入变基信息

![image-20200313150328135](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313150328135.png)

变基成功

![image-20200313150426190](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313150426190.png)

此时查看本地分支图，可见产生了新的分支路径，同时远程message并没有变化，故rebase对存在远程分支的情况无效

![image-20200313150514493](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313150514493.png)



变基后推送到远端分支，提示需要合并，选择“合并”

![image-20200313150709744](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313150709744.png)

合并后分支图如下

![image-20200313151107792](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313151107792.png)



此时其他开发者修改文件后并`fetch`远程分支查看变更情况如下

![image-20200313151245155](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313151245155.png)



此时**无法**对远程分支进行`push`操作

![image-20200313151349842](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313151349842.png)



#### 处理方法

pull远程分支在本地合并后重新推送，此时在本地再产生一次合并

![image-20200313151452121](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313151452121.png)



此时可以成功推送

![image-20200313151550190](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/image-20200313151550190.png)



由此一来一回操作导致大量不必要的合并操作，并可能导致大量冲突，并且**没有解决问题**



## 警告类操作

### `reset --hard`

官方对`reset`操作用法说明

> usage: git reset [--mixed | --soft | --hard | --merge | --keep] [-q] [<commit>]
>    or: git reset [-q] [<tree-ish>] [--] <paths>...
>    or: EXPERIMENTAL: git reset [-q] [--stdin [-z]] [<tree-ish>]
>    or: git reset --patch [<tree-ish>] [--] [<paths>...]
>
>     -q, --quiet           be quiet, only report errors
>     --mixed               reset HEAD and index
>     --soft                reset only HEAD
>     --hard                reset HEAD, index and working tree
>     --merge               reset HEAD, index and working tree
>     --keep                reset HEAD but keep local changes
>     --recurse-submodules[=<reset>]
>                           control recursive updating of submodules
>     -p, --patch           select hunks interactively
>     -N, --intent-to-add   record only the fact that removed paths will be added later
>     -z                    EXPERIMENTAL: paths are separated with NUL character
>     --stdin               EXPERIMENTAL: read paths from <stdin>
>



原因：

- 在分支上执行该操作会丢失目标commit以后的所有commit



适用场景

- 用于分支回滚且不打算保留其后的所有变更
