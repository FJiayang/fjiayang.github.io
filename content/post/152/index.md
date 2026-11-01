{
  "title": "Excel使用宏将复杂操作自动化",
  "date": "2018-05-12T12:42:00+08:00",
  "lastmod": "2023-09-07T15:04:03+08:00",
  "typecho_cid": 152,
  "url": "/archives/152/",
  "comments": false,
  "draft": false,
  "slug": "152",
  "categories": [
    "默认分类"
  ],
  "tags": [
    "Excel"
  ],
  "math": true
}

## 简单宏操作 ##
Excel的宏实质是VB语句，现考虑制作一个宏用于将当前表中的数据复制成4个工作簿
### 录制 ###
打开目标工作簿，当前只有`Sheet1`中有数据，预期结果是将当期数据复制到`Sheet2`、`Sheet3`、`Sheet4`中
![请输入图片描述][1]

点击视图->录制宏
![请输入图片描述][2]

指定名称和快捷键即可开始录制操作
![请输入图片描述][3]

### 查看代码 ###
录制完成后店家查看宏，选择编辑即可查看VB代码
![请输入图片描述][4]

![请输入图片描述][5]

在此提供代码，注意，该代码起点是`Sheet2`,即切换到`Sheet2`中才能开始执行，否则会报错
    Sub 复制()
    '
    ' 复制 宏
    '
    ' 快捷键: Ctrl+o
    '
        Cells.Select
        Selection.Copy
        Sheets("Sheet2").Select
        ActiveSheet.Paste
        Sheets("Sheet3").Select
        ActiveSheet.Paste
        Sheets.Add After:=ActiveSheet
        ActiveSheet.Paste
        Range("E29").Select
        Application.CutCopyMode = False
        ActiveWorkbook.Save
    End Sub

## 复杂宏 ##
VB自然支持函数（宏）调用，例如以下代码，先录制了三个预测函数操作，通过一个`预测()`宏对三个函数操作进行调用

    Sub 预测线性()
    '
    ' 预测线性 宏
    '
    ' 快捷键: Ctrl+a
    '
        Range("A31").Select
        ActiveCell.FormulaR1C1 = "=R[-26]C+1"
        Range("A32").Select
        ActiveWorkbook.Save
        Range("B31").Select
        Application.CutCopyMode = False
        ActiveCell.FormulaR1C1 = _
            "=FORECAST(RC[-1],R[-26]C:R[-1]C,R[-26]C[-1]:R[-1]C[-1])"
        Range("A31:B31").Select
        Selection.Font.Bold = True
        ActiveWorkbook.Save
    End Sub
    Sub 指数预测()
    '
    ' 指数预测 宏
    '
    ' 快捷键: Ctrl+e
    '
        Range("A31").Select
        ActiveCell.FormulaR1C1 = "=R[-26]C+1"
        Range("B31").Select
        Application.CutCopyMode = False
        Application.CutCopyMode = False
        Application.CutCopyMode = False
        ActiveCell.FormulaR1C1 = _
            "=GROWTH(R[-26]C:R[-8]C,R[-26]C[-1]:R[-8]C[-1],RC[-1])"
        Range("A31:B31").Select
        Selection.Font.Bold = True
        ActiveWorkbook.Save
    End Sub
    Sub 对数预测()
    '
    ' 对数预测 宏
    '
    ' 快捷键: Ctrl+w
    '
        Application.Run "PERSONAL.XLSB!预测线性"
        Range("B31").Select
        Selection.ClearContents
        Range("B31").Select
        ActiveCell.FormulaR1C1 = "=(Sheet1!RC+Sheet3!RC)/2"
        Range("B31").Select
        ActiveWorkbook.Save
    End Sub
    Sub 预测()
    '
    ' 预测 宏
    '
    ' 快捷键: Ctrl+q
    '
        Application.Run "PERSONAL.XLSB!预测线性"
        Sheets("Sheet3").Select
        Application.Run "PERSONAL.XLSB!指数预测"
        Sheets("Sheet2").Select
        Application.Run "PERSONAL.XLSB!对数预测"
        ActiveWorkbook.Save
    End Sub

  [1]: /images/recovered/b90a35598b3beafd2f71.png
  [2]: /images/recovered/cebc286c81d30505d355.png
  [3]: /images/recovered/c0e02c622414378f54fd.png
  [4]: /images/recovered/3ab6e91527863eb6eeea.png
  [5]: /images/recovered/d6c4c1fbe18a725b254c.png
