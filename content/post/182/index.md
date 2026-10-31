{
  "title": "VPS性能测试",
  "date": "2018-09-13T13:00:22+08:00",
  "lastmod": "2018-09-13T13:00:22+08:00",
  "typecho_cid": 182,
  "url": "/archives/182/",
  "comments": false,
  "draft": false,
  "slug": "182",
  "categories": [
    "服务器"
  ],
  "tags": [],
  "math": false
}

## 测试命令

采用superbench

```shell
wget -qO- --no-check-certificate https://raw.githubusercontent.com/oooldking/script/master/superbench.sh | bash
```

## OpenVZ

以手上的HiFormance VPS为例，superbench自动识别虚拟化平台和硬件信息，并对国内不同地点、不同运营商的上行、下行速度测试和延迟测试

HiFormance 亚洲优化线路，由于HiFormance 亚洲优化线路虚拟化平台是OpenVZ+lxc，故无法安装BBR加速

[![vps6.png](https://i.loli.net/2018/09/13/5b99ea259b4f6.png)](https://i.loli.net/2018/09/13/5b99ea259b4f6.png)

HiFormance 普通线路，启用了BBR加速

[![vps4.png](https://i.loli.net/2018/09/13/5b99ebdd050a0.png)](https://i.loli.net/2018/09/13/5b99ebdd050a0.png)

## KVM

以搬瓦工VPS为例，平台识别正常

搬瓦工VPS，亚洲优化，启用BBR

[![vps3.png](https://i.loli.net/2018/09/13/5b99eccc9c3e7.png)](https://i.loli.net/2018/09/13/5b99eccc9c3e7.png)

阿里云ECS 1Mbps带宽，识别正常

[![vps2.png](https://i.loli.net/2018/09/13/5b99eda58e8b5.png)](https://i.loli.net/2018/09/13/5b99eda58e8b5.png)

## 物理机

识别平台为独立主机

[![vps1.png](https://i.loli.net/2018/09/13/5b99dcd864753.png)](https://i.loli.net/2018/09/13/5b99dcd864753.png)
