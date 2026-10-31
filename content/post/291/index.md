{
  "title": "本地LLM训练",
  "date": "2025-03-30T11:44:00+08:00",
  "lastmod": "2025-03-30T16:19:25+08:00",
  "typecho_cid": 291,
  "url": "/archives/291/",
  "comments": false,
  "draft": false,
  "slug": "291",
  "categories": [
    "学习"
  ],
  "tags": [
    "AI",
    "LLM"
  ],
  "math": true
}

## 参考资料

[jingyaogong/minimind](https://github.com/jingyaogong/minimind)

## 环境准备

本地环境配置
- CPU 12700
- 内存 32G DDR4 3200
- GPU RTX 2060Super
- 系统 Win11
- CUDA 12.6
- Python 3.12

由于需要本地编译，windows环境需要安装**Microsoft Visual C++ 编译器**，tiktoken编译需要rust环境，安装地址：
- [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- [rustup.rs - The Rust toolchain installer](https://rustup.rs/)

克隆并安装环境

```bash
git clone https://github.com/jingyaogong/minimind.git
cd minimind
pip install -r requirements.txt
```

注意：此处不建议使用清华源、也不建议使用conda虚拟环境，会导致pytorch包版本匹配失败

依赖安装检查，执行以下代码
```python
import torch  
print(torch.__version__)  
print(torch.version.cuda)  
print(torch.cuda.is_available())
```

输入如下即成功
```bash
(base) PS F:\java_workspace\minimind> python .\test_env.py
2.6.0+cu126
12.6
True
```


按照文档指引下载默认的预训练集和监督训练集
- [minimind_dataset · 数据集](https://www.modelscope.cn/datasets/gongjy/minimind_dataset/files)

## 训练过程
### 预训练
执行预训练
```bash
python train_pretrain.py
```
![file-20250329180305778](/images/recovered/ed35f099beb68ef9c0d6.png)
在我的环境下需要3小时才能完成预训练


执行预训练，得到`pretrain_*.pth`作为预训练的输出权重（其中为模型的dimension，默认为512）
![file-20250329205630234](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/本地LLM训练/file-20250329205630234.png)
### 监督微调
```bash
python train_full_sft.py
```
执行监督全参数微调，在我的环境下需要2.5小时
![file-20250329210505564](/images/recovered/27840e78e795fa10d888.png)

![file-20250329233223537](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/本地LLM训练/file-20250329233223537.png)
## 效果测试

测试全参微调
```bash
python eval_model.py --model_mode 1
```
![file-20250330084041529](https://gitea.fjy8018.top/fjy8018/images/raw/branch/blog/img/本地LLM训练/file-20250330084041529.png)

从结果来看，能进行对话，但受限于参数量，很多知识不完整，对话回答质量比较一般。

## 模型优化
受本地环境限制，只能完成监督微调步骤，后续步骤执行会爆显存，耗时显著增加。
后续学习改为使用阿里云PAI-DSW环境
