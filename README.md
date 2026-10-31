# F嘉阳的博客

使用 Hugo Extended **0.169.0** 和 Stack **v4.0.3** 构建，站点地址为 <https://blog.fjy8018.top/>。主题通过 Hugo Modules 锁定在 `go.mod` / `go.sum`，保留主题版权信息。

## 本地预览与验证

安装 Hugo Extended 0.169.0、Go 1.24.3 和 Python 3.11+；`hugo version` 应包含 `extended`。

```sh
hugo server --bind 127.0.0.1 --baseURL http://localhost:1313/
```

打开 <http://localhost:1313/>。完整构建与校验：

```sh
python3 -m unittest discover -s tests -v
mkdir -p .migration
hugo --gc --minify --cleanDestinationDir > .migration/hugo-build.log 2>&1
python3 scripts/verify_site.py
python3 scripts/report_resources.py .migration/hugo-build.log
```

站点图标和侧栏头像使用原仓库的 `/images/avatar.png`，原文件恢复到 `static/images/avatar.png`。

除下文已从本地恢复的 49 个图片地址外，其余文章图片、封面和附件保留原地址。**保留 Stack 默认图片模板**：Hugo 构建会下载远程图片以读取元数据；关闭生成缩略图及响应式派生图，页面继续使用原地址。不可达图片产生警告，不阻止发布。原站及图床需要继续提供资源。首次构建受图片网络速度影响，缓存可加快后续构建。

`reports/resources.json` 记录本次本地构建的图片请求警告；没有警告不代表链接永久可用，HTML 原生图片、附件和友情链接不会因 Hugo 构建而获得完整的可用性检查。

## 日常写作

新增 `content/post/<唯一标识>/index.md`，例如：

```yaml
---
title: 新文章
date: 2026-10-31T12:00:00+08:00
slug: new-post
url: /archives/new-post/
categories: [开发]
tags: [Hugo]
comments: false
---
正文。
```

新文章不需要 `typecho_cid`。不再维护 Typecho 或自动同步数据库；评论在全站禁用，无评论脚本和服务。

## 一次性迁移工具

迁移源为 `typecho_offical`。每次导出只建立一个 MySQL 连接，所有查询复用该连接，认证或查询失败时立即停止、不自动重试。数据库只读访问，密码仅从 `WARP_PASSWORD` 环境变量读取，传给 MySQL 子进程的 `MYSQL_PWD`，不写文件或输出。默认 MySQL 路径是 `/opt/homebrew/opt/mysql-client/bin/mysql`，可用 `MYSQL_BIN` 覆盖。

```sh
# 首次或最终增量核对：需要已设置 WARP_PASSWORD
python3 scripts/migrate_typecho.py --extract
# 使用本地已导出快照重新转换，不连接数据库
python3 scripts/migrate_typecho.py
```

仅查询公开、无密码文章，以及源码/友情链接页面及其关联元数据。不查询评论，不提取私密文章、密码文章、草稿和修订。迁移基线为 127 篇文章、2 个页面；另生成归档和搜索页。分类和标签按关联内容生成。友情链接从链接表生成。

原始公开内容快照保存在被忽略的 `.migration/public-content.json`。转换后的文章使用 JSON front matter（Hugo 原生支持），发布时间转换为东八区，文章永久地址保持 `/archives/<cid>/`。转换卡片、提示块和文章互链；图片绝对地址不变，相对地址补全为原 Typecho 域名。原始代码中的换行与字面量 `\n` 保留。

`reports/migration.json` 保存迁移清单、遗留语法、未解析文章引用及远程资源清单。重复执行会覆盖迁移文章并删除上次迁移清单内已不符合范围的文章，不删除手写文章。**迁移完成后不要继续运行此工具覆盖日常手工编辑**。

## GitHub Pages

`.github/workflows/hugo.yaml` 对 PR 运行转换测试、Hugo 构建及站点校验；向 `master` 推送或在 `master` 手动触发时部署。CI 只读取仓库文件，不连接 MySQL，也不需要数据库密码。`public/` 和缓存不提交。

首次上线：

1. 停止原 Typecho 的内容编辑，执行最终 `--extract`，检查迁移差异并重新构建校验。
2. 在仓库 Settings → Pages → Build and deployment 将 Source 设为 **GitHub Actions**，Custom domain 设为 `blog.fjy8018.top`，DNS 的 `blog` CNAME 指向 `fjiayang.github.io`，证书就绪后启用 Enforce HTTPS。
3. 合并迁移分支到 `master`，检查 Build and deploy Hugo 工作流完成。
4. 验证首页、`/archives/`、文章、分类、标签、搜索、`/project.html`、`/links.html`、`/index.xml`、`/sitemap.xml` 和 404 页面。

当前自定义域名为 `blog.fjy8018.top`，Hugo 的 `baseURL` 与 Pages 设置需保持一致。原 Typecho 数据库和服务不由本仓库修改，旧 Gridea 文章没有兼容跳转。

## 回滚

旧站基线提交：`0c4886639cccbee92d8e1727986c044a877e68d0`。回滚时用新提交恢复该提交的文件树（不要强推或删除历史），并把 Pages Source 恢复为 **Deploy from a branch → master / (root)**。若保留 GitHub Actions 发布模式，也可先重新部署最后成功的 Hugo 产物。原 Typecho 服务始终保持可用。

迁移期间的分支为 `codex/typecho-hugo-stack`；生成文件和原始导出不作为备份介质，旧站代码由 Git 历史保留。

## 头图与本地图片恢复

首页文章卡片和文章页顶部优先使用 front matter 的 `image`。未设置封面时，模板自动取正文第一张图片，支持 Markdown、引用式图片和 HTML 图片，代码示例不参与选取。没有图片的文章保留文字卡片。默认 Stack 图片下载模板保持不变。

已从本地草稿和图片仓库恢复 49 个失败图片地址，涉及 27 篇已发布文章，文件保存在 `static/images/recovered/`，使用 SHA-256 命名并去重。`reports/image-recovery.json` 记录原 URL、本地来源、校验值、关联文章和剩余 2 个未找到本地文件的地址；这些未确认图片继续保留原 URL。

需要复现修复时运行（只读取本地草稿，不访问网络和数据库）：

```sh
python3 scripts/recover_images.py '/Users/fjy/Documents/workspace/blog-note/01博客'
# 可继续从其他图片目录恢复未解决项；已有恢复文件及记录会保留
python3 scripts/recover_images.py '/Users/fjy/Documents/workspace/images/img'
```

若重新执行一次性 Typecho 导入，请在导入后运行恢复命令以重新应用本地图片引用。原草稿不修改，草稿正文不导入站点。
