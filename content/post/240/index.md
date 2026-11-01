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

![image-20200313100955490](/images/recovered/a26798cb0ed774fffac5.png)

切换到之前的某一次提交

![image-20200313101041682](/images/recovered/9abb1b7430c191ef6975.png)



执行命令

```bash
$ git checkout de11fa87ea
```



提示，当前位于“分离头指针”状态

![image-20200313101137934](/images/recovered/29d1219a9af97a5fe11b.png)



分支图

![image-20200313101230748](/images/recovered/9e298532f8fcc1d19671.png)

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

![image-20200313101811004](/images/recovered/a597b0f2217d379fa9a8.png)

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

![image-20200313101817932](/images/recovered/e9d74ce5429966c18b6e.png)



此时查看分支图，刚才的commit已经不可见

![image-20200313102044269](/images/recovered/21d8a1891cb0cd67407e.png)

### 补救

此时发现刚才的commit十分重要，可根据git的提示进行补救

执行命令

```bash
$ git branch hot-fix 199ac20
```



再次查看分支图，可见commit已经恢复

![image-20200313102203644](/images/recovered/7428707566513d9c8d7a.png)

## 本地分支操作

以下操作仅适用于本地分支，无远程分支协同工作的情况



### 修改当前commit的message——`amend`

当前分支图

![image-20200313102633268](/images/recovered/ff80443253acbe9947c1.png)

执行命令

```bash
$ git commit --amend
```

自动弹出编辑器

![image-20200313102714191](/images/recovered/7fcc7f2c8940cec8ec45.png)



修改后保存并关闭编辑器即可，输出如下

![image-20200313102735178](/images/recovered/bd43c06de33fd08811c6.png)



再次查看分支图

![image-20200313102751917](/images/recovered/748127f9f87e90136846.png)



### 修改前面某次commit的message——`rebase`

现计划修改如下message

![image-20200313102837128](/images/recovered/06d6dd6713f563e1d4d4.png)



使用IDE拷贝其父提交的SHA值

![image-20200313102938536](/images/recovered/5a8427a07cccebe1b92d.png)



执行命令，`-i`表示交互式执行

```bash
$ git rebase -i 199ac203c90f881024c6870d56517df9e2080841
```



自动弹出编辑器

![image-20200313103103273](/images/recovered/185df5200e2044406c3c.png)



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

![image-20200313103140977](/images/recovered/f90604b16dfc111d4048.png)



保存并关闭编辑器，会自动弹出新编辑器界面

![image-20200313103156452](/images/recovered/df7930ace19ab5ea4a80.png)



修改后保存并关闭即可，输出如下

![image-20200313103234131](/images/recovered/c400899a77249ca7e9a9.png)



查看分支图

![image-20200313103250780](/images/recovered/d1f061dba32bcbddca36.png)



### 整理连续多个commit——`rebase`

现计划合并3个commit

![image-20200313104229297](/images/recovered/257e6f48889bff583eb5.png)

使用IDE拷贝其父SHA值

![image-20200313104256202](/images/recovered/5d837f75a15e7e3634c9.png)

执行命令

```bash
$ git rebase -i 199ac203c90f881024c6870d56517df9e2080841
```



此处使用`squash`，官方介绍如下

> s, squash <commit> = use commit, but meld into previous commit



修改内容如下，说明将中间两个合并进第一个commit中

![image-20200313104553536](/images/recovered/db34920acbc8eabae138.png)



保存后关闭，会弹出新的编辑器界面，提示可以输出合并commit的message

![image-20200313104708882](/images/recovered/75247d2104920354c3cc.png)



编写message

![image-20200313104849690](/images/recovered/31cec4549fb6b5cbc064.png)



保存后关闭，提示修改成功

![image-20200313105805083](/images/recovered/1203e6ea7c56718ea498.png)



查看分支图

![image-20200313105829642](/images/recovered/7c2bc24abe83aaee5406.png)

## 分支合并策略

演示不同分支合并策略效果，当前的分支图如下

![1584157562406](/images/recovered/da620d3033bac6aab107.png)

现在将hot-fix合并进master

### GitLab默认合并策略——`merge commit`

gitlab默认合并请求使用的策略

![1584157617890](/images/recovered/ab0e0971671617cd8cb0.png)

![1584157635041](/images/recovered/d4ef0dd203b1136bf328.png)

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

![1584157751505](/images/recovered/e36b50a8c3176cd77aab.png)

查看分支图，故当前分支会影响特性分支并产生新的提交

![1584157894622](/images/recovered/2f06aa50c27961298b7d.png)



### GitLab合并提交策略

提交合并请求的时候勾选策略`Squash commits when merge request is accepted`

![1584158031481](/images/recovered/35ae39a87d87ad1a8ec7.png)

![1584158086855](/images/recovered/c14a6258a5b69f29585a.png)

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

![1584158157862](/images/recovered/13000af93bdca68c1a49.png)

查看分支图，可见其影响特性分支，会产生新的提交，同时覆盖特性分支最后一次提交

![1584158250648](/images/recovered/0367e5d65c02f40fd6d0.png)



### 分支合并策略——`squash merge`

GitHub支持`squash merge`合并策略，此处通过命令行执行测试

```bash
$ git merge --squash origin/hot-fix
$ git commit -m "squash commit"
```



查看分支图，特性分支不变，目标分支合并提交后产生一条提交，效果与GitLab合并提交类似，但命令使用方式不同

![1584158902921](/images/recovered/5bf70aa11224b190e474.png)



**注意：`squash merge`会变更提交者作者信息，这是一个很大的问题，后期问题追溯不好处理**

### 变基合并策略——`rebase merge`

该策略也是GitHub支持的合并策略，可能会产生较多冲突

![1584159613476](/images/recovered/b0af8ccba7c6a9bcf7e9.png)

选择合并策略，最后一种即变基合并策略

![1584159638818](/images/recovered/0bd8f8b320dd1555e358.png)

![1584159659905](/images/recovered/e91caf832a49688da317.png)

合并成功

![1584159671515](/images/recovered/c278c1bb7e2aeb39ca1a.png)

查看分支图，其产生的三次提交即变基合并的结果，不会影响特性分支，也不会变更提交人，类似`cherry pick`

![1584159735805](/images/recovered/3812f388a8ac34af0c94.png)



## 分支回滚策略

回滚策略分为两种，一种是合并后回滚，一种是普通提交回滚，不同回滚策略操作方法不同



### 普通提交回滚

当前分支图，计划回滚最新提交

![image-20200317114811482](/images/recovered/d94205b738f53a628162.png)

直接在IDE中执行`revert`操作即可

![image-20200317114905943](/images/recovered/25b2cf6f6d5d3327c5aa.png)

![image-20200317114935874](/images/recovered/2f28213b5368ac94fb7a.png)



回滚会产生新的提交，回滚结束

![image-20200317114957310](/images/recovered/baaf7347aecfdf748dbf.png)



### 合并后回滚

此时分支图，使用`merge commit`方式进行过一次合并，此时不想要合并的结果，想恢复到未合并状态

![image-20200317115211900](/images/recovered/5531fb105edd5e69f39c.png)

#### 错误操作——直接执行`revert`

此时IDE已经不支持通过revert进行回滚合并操作，通过命令行强行执行

查找SHA值

![image-20200317115622215](/images/recovered/4b4a34f43f35806fa12f.png)

回滚`merge`需要加上`-m`参数git就知道到底要revert哪一个merge 

```bash
$ git revert -n 25d7b405a4d50fe1b36019d90276973a8ed9160d -m 1
```



回滚后做一次commit即可，使用默认的message后如下

![image-20200317120022233](/images/recovered/25ebf008ddeb5ba476e1.png)

验证回滚结果，使用两个提交进行差异比对

![image-20200317122223636](/images/recovered/3f2b5b13db8d8f5fd570.png)

无差异，回滚看似成功了

<img src="/images/recovered/c5eace1246597ae11eac.png" alt="image-20200317122240317" style="zoom:50%;" />

此时在原分支做了修复后再进行合并

![image-20200317141053618](/images/recovered/0a615c6bd9402f5c92b3.png)

报无法合并，因为分支已经进行过合并

![image-20200317141147054](/images/recovered/5508ca5239d6df2eef27.png)



#### 正确操作——`reset`

使用reset操作到上一次提交

![image-20200317141254057](/images/recovered/c247395776583daa2e5e.png)

使用`--hard`参数，丢弃后续的commit

![image-20200317141341299](/images/recovered/bd4dcf5cdf5074b1c6e2.png)

![image-20200317141418080](/images/recovered/60bb59610737ddba639e.png)

此时继续进行操作，并支持重新合并

![image-20200317141504021](/images/recovered/ee6756766f095385a68b.png)



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

![image-20200313144526583](/images/recovered/f9559f682c92e859166e.png)

另一开发者在本地修改后执行变基操作，此处以修改历史提交message为例

![image-20200313150137509](/images/recovered/bcfd2275129a9a8ef603.png)



变基

![image-20200313150232682](/images/recovered/a93661207f078348ffff.png)

录入变基信息

![image-20200313150328135](/images/recovered/75fb9f14dce4dfef94bd.png)

变基成功

![image-20200313150426190](/images/recovered/ee8c394d6c3c6d4c5ff8.png)

此时查看本地分支图，可见产生了新的分支路径，同时远程message并没有变化，故rebase对存在远程分支的情况无效

![image-20200313150514493](/images/recovered/f09e2b04e9c3b9478c64.png)



变基后推送到远端分支，提示需要合并，选择“合并”

![image-20200313150709744](/images/recovered/bfe7335765348f758f86.png)

合并后分支图如下

![image-20200313151107792](/images/recovered/94522cd8a19ba5a84b96.png)



此时其他开发者修改文件后并`fetch`远程分支查看变更情况如下

![image-20200313151245155](/images/recovered/a10b931096c9d9c27eb3.png)



此时**无法**对远程分支进行`push`操作

![image-20200313151349842](/images/recovered/2fa0025e9eaa193651a0.png)



#### 处理方法

pull远程分支在本地合并后重新推送，此时在本地再产生一次合并

![image-20200313151452121](/images/recovered/b73ddf118ee1c1f5a647.png)



此时可以成功推送

![image-20200313151550190](/images/recovered/1f583cbb1ab795c8ddf0.png)



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
