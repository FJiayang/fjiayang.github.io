{
  "title": "SpringBoot的一些坑",
  "date": "2018-07-08T16:03:00+08:00",
  "lastmod": "2023-09-07T14:44:16+08:00",
  "typecho_cid": 170,
  "url": "/archives/170/",
  "comments": false,
  "draft": false,
  "slug": "170",
  "categories": [
    "开发"
  ],
  "tags": [
    "SpringBoot"
  ],
  "math": true
}

## bindingResult无法捕获校验错误 ##
### 错误复现 ###
原工程代码，`RegisterForm`对象设置了校验规则
![请输入图片描述][1]

预期的返回结果

    {
        "code": 4,
        "msg": "表单错误",
        "data": null
    }

实际执行结果
![请输入图片描述][2]

并且控制台打出了异常堆栈，而且记录的log4j日志也没有显示
![请输入图片描述][3]

### 原因 ###
经过查阅资料，得到原因
> @Valid 和 BindingResult
> 是一一对应的，如果有多个@Valid，那么每个@Valid后面跟着的BindingResult就是这个@Valid的验证结果，顺序不能乱

### 解决 ###
故将`BindingResult`跟在`RegisterForm`后面即可

    public ResultVO doRegister(@Valid RegisterForm registerForm, BindingResult bindingResult, HttpServletRequest request) throws Exception{

再次执行得到预期返回值
![请输入图片描述][4]

控制台也打出预期的日志，并没有显示异常
![请输入图片描述][5]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/JJqlnW.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/JJqCTR.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/JJq18g.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/JJqu7w.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/JJqmZ8.png
