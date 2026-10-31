{
  "title": "Excel字符串根据指定内容进行变化的嵌套函数",
  "date": "2018-05-12T13:10:00+08:00",
  "lastmod": "2023-09-07T15:03:31+08:00",
  "typecho_cid": 153,
  "url": "/archives/153/",
  "comments": false,
  "draft": false,
  "slug": "153",
  "categories": [
    "默认分类"
  ],
  "tags": [],
  "math": true
}

## 目标 ##
当前工作簿内容，其标题为`万科A(000002)近一个月历史交易(1525501238 符嘉阳)`
现希望其根据当前证券名称结合下方的日期自动变更标题为`万科A(000002)从20180309至20180410近一个月历史交易(15251101238 符嘉阳)`
![请输入图片描述][1]

## 分析 ##
其中应该涉及一下几点

 1. 保留当前的标题，并对证券名称和证券代码进行截取
 2. 将开始日期和结束日期获取并转为目标格式的字符串
 3. 字符串拼接

## 所用函数 ##
函数名称：MID
主要功能：从一个文本字符串的指定位置开始，截取指定数目的字符。
使用格式：MID(text,start_num,num_chars)
参数说明：text代表一个文本字符串；start_num表示指定的起始位置；num_chars表示要截取的数目。

函数名称：TEXT
主要功能：将数值转换为按指定数字格式表示的文本。
使用格式：TEXT(value,format_text)
参数说明：Value为数值、计算结果为数字值的公式，或对包含数字值的单元格的引用。

函数名称：CONCATENATE
主要功能：将两个或多个文本字符串联接为一个字符串。
使用格式：CONCATENATE(text1, [text2], ...)
参数说明：text1   （必需）要联接的第一个项目。项目可以是文本值、数字或单元格引用。Text2, ...   （可选）要联接的其他文本项目。最多可以有 255 个项目，总共最多支持 8,192 个字符。

## 设计结果 ##

    =CONCATENATE(MID(A89,1,FIND(")",A89)),"从",TEXT(A25,"yyyymmdd"),"至",TEXT(A5,"yyyymmdd"),"近一个月历史交易(15251101238 符嘉阳)")

效果如图
![请输入图片描述][2]

![请输入图片描述][3]

通用性测试成功
![请输入图片描述][4]

时间也会自动随内容变化
![请输入图片描述][5]


  [1]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2vOyVF.png
  [2]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2vOku1.png
  [3]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2vOZUa.png
  [4]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2vOtvd.png
  [5]: https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/2vOf6u.png
