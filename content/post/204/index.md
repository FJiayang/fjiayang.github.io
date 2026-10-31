{
  "title": "阿里云CDN + nginx多级代理获取客户端IP",
  "date": "2019-04-03T10:01:44+08:00",
  "lastmod": "2019-04-03T10:01:44+08:00",
  "typecho_cid": 204,
  "url": "/archives/204/",
  "comments": false,
  "draft": false,
  "slug": "204",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "Java",
    "CDN",
    "nginx"
  ],
  "math": false
}

## 无Nginx代理场景

业务层通过获取请求头参数即可拿到客户端IP

```java
request.getRemoteAddr();
```



## 一级Nginx代理

使用代理后直接读取请求头参数会读取到代理服务器的IP地址，而非真实客户端IP

解决方法是添加Nginx请求头参数提前保存客户端IP



`nginx.conf`配置加入内容

```
location / {
    ...
    # IP地址转发
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Real-Port $remote_port;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
```



业务层读取nginx配置的请求头参数即可

```java
public static String getIpAddr(HttpServletRequest request) {
        String ip = request.getHeader("X-Real-IP");
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
            log.info("【Proxy-Client-IP】 {}", ip);
        }
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
            log.info("【WL-Proxy-Client-IP】{}", ip);
        }
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Forwarded-For");
            log.info("【X-Forwarded-For】{}", ip);
        }
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
            log.info("【unknown】{}", ip);
        }
        return ip;
    }
```



## 多级Nginx代理

若存在多级Nginx代理，则需要在第一级代理时获取客户端IP，在后续代理逐层传递

第一级代理配置同上，第N级代理配置`nginx.conf`如下

```
location /{
   # IP地址转发
   proxy_set_header X-Real-IP $X-Real-IP;
   proxy_set_header X-Real-Port $X-Real-Port;
   proxy_set_header X-Forwarded-For $X-Forwarded-For;
}
```



业务层保持不变即可读取到传递的IP地址



## 阿里云CDN转发

在已经存在nginx代理的场景下，加入CDN后源客户端IP在CDN处被转发，故第一级nginx代理使用`$remote_addr`参数读取到的是CDN服务的地址，而根据一般约定，CDN转发会将IP地址存放在`X-Forwarded-For`参数下

修改顶级Nginx配置以支持优先获取CDN代理地址，也可以通过修改业务层读取优先级实现

```
location / {
    ...
    # IP地址转发
    # proxy_set_header X-Real-IP $remote_addr;
    # proxy_set_header X-Real-Port $remote_port;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
```



但经过对阿里云CDN测试，发现`X-Forwarded-For`下不仅包含真实客户端IP也包含CDN服务IP，故业务层需要做一定的处理进行区分

如图，第一个为真实客户端IP，第二个为CDN代理IP

[![1554256476626.png](https://i.loli.net/2019/04/03/5ca413f53a191.png)](https://i.loli.net/2019/04/03/5ca413f53a191.png)



```java
public static String getIpAddr(HttpServletRequest request) {
        String ip = request.getHeader("X-Real-IP");
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
            log.info("【Proxy-Client-IP】 {}", ip);
        }
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
            log.info("【WL-Proxy-Client-IP】{}", ip);
        }
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Forwarded-For");
            if (ip.contains(",")) {
                // 通过阿里云CDN转发后可能读取到2个IP地址
                String[] cdnMutilIp = ip.split(",");
                ip = cdnMutilIp[0];
            }
            log.info("【X-Forwarded-For】{}", ip);
        }
        if (ip == null || ip.length() == 0 || " unknown ".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
            log.info("【unknown】{}", ip);
        }
        return ip;
    }
}
```
