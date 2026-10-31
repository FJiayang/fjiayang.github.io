{
  "title": "Ansible安装配置",
  "date": "2018-08-19T16:38:00+08:00",
  "lastmod": "2018-08-26T19:35:22+08:00",
  "typecho_cid": 175,
  "url": "/archives/175/",
  "comments": false,
  "draft": false,
  "slug": "175",
  "categories": [
    "服务器",
    "开发"
  ],
  "tags": [
    "Ansible"
  ],
  "math": false
}

[ansible官方文档指南](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

## 系统预配置 ## 
关闭防火墙

    [root@localhost ~]# systemctl stop firewalld

关闭防火墙开机启动

    [root@localhost ~]# systemctl disable firewalld
    Removed symlink /etc/systemd/system/multi-user.target.wants/firewalld.service.
    Removed symlink /etc/systemd/system/dbus-org.fedoraproject.FirewallD1.service.

关闭强制访问控制安全策略

    vi /etc/sysconfig/selinux

    # This file controls the state of SELinux on the system.
    # SELINUX= can take one of these three values:
    #     enforcing - SELinux security policy is enforced.
    #     permissive - SELinux prints warnings instead of enforcing.
    #     disabled - No SELinux policy is loaded.
    SELINUX=enforcing
    # SELINUXTYPE= can take one of three two values:
    #     targeted - Targeted processes are protected,
    #     minimum - Modification of targeted policy. Only selected processes are protected.
    #     mls - Multi Level Security protection.
    SELINUXTYPE=targeted

`SELINUX=enforcing`改成`SELINUX=disabled`

reboot使禁用操作生效

查看操作是否生效

    [root@localhost ~]# getenforce
    Disabled

## 安装Python3 ## 

    wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz

[![ansible1.png](https://i.loli.net/2018/08/19/5b792c501dafe.png)](https://i.loli.net/2018/08/19/5b792c501dafe.png)
解压编译包

    tar xf Python-3.7.0.tar.xz

查看文件

    [root@localhost ~]# ls
    anaconda-ks.cfg  Python-3.7.0  Python-3.7.0.tar.xz
    [root@localhost ~]# cd Python-3.7.0

安装OpenSSL依赖，否则使用pip3.7会报找不到SSL模块错误

    yum install openssl-devel

设定编译参数，/usr/local为安装位置，--with-ensurepip=install指定安装包管理工具，--enable-shared配置Python匹配系统参数

    [root@localhost Python-3.7.0]# ./configure --prefix=/usr/local --with-ensurepip=install --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib" --with-ssl
    checking build system type... x86_64-pc-linux-gnu
    checking host system type... x86_64-pc-linux-gnu
    checking for python3.7... no
    checking for python3... no
    checking for python... python
    checking for --enable-universalsdk... no
    checking for --with-universal-archs... no
    checking MACHDEP... checking for --without-gcc... no
    checking for --with-icc... no
    checking for gcc... no
    checking for cc... no
    checking for cl.exe... no
    configure: error: in `/root/Python-3.7.0':
    configure: error: no acceptable C compiler found in $PATH
    See `config.log' for more details

报错为找不到C编译器，由于系统为最小化安装，没有自带gcc编译器
安装gcc

    yum install gcc

[![ansible2.png](https://i.loli.net/2018/08/19/5b792c501d7ef.png)](https://i.loli.net/2018/08/19/5b792c501d7ef.png)
再次编译，编译通过
安装编译文件

     make && make altinstall

[![ansible3.png](https://i.loli.net/2018/08/19/5b792c501ced6.png)](https://i.loli.net/2018/08/19/5b792c501ced6.png)
日志如下

    Traceback (most recent call last):
      File "/root/Python-3.7.0/Lib/runpy.py", line 193, in _run_module_as_main
        "__main__", mod_spec)
      File "/root/Python-3.7.0/Lib/runpy.py", line 85, in _run_code
        exec(code, run_globals)
      File "/root/Python-3.7.0/Lib/ensurepip/__main__.py", line 5, in <module>
        sys.exit(ensurepip._main())
      File "/root/Python-3.7.0/Lib/ensurepip/__init__.py", line 204, in _main
        default_pip=args.default_pip,
      File "/root/Python-3.7.0/Lib/ensurepip/__init__.py", line 117, in _bootstrap
        return _run_pip(args + [p[0] for p in _PROJECTS], additional_paths)
      File "/root/Python-3.7.0/Lib/ensurepip/__init__.py", line 27, in _run_pip
        import pip._internal
    zipimport.ZipImportError: can't decompress data; zlib not available

    make: *** [altinstall] 错误 1

编译报错，找不到zlib，同理，安装zlib

    yum -y install zlib*

另外，此时安装的是3.7版本，3.7版本需要一个新的包libffi-devel否则也会编译报错

    yum install libffi-devel -y

安装成功

[![ansible4.png](https://i.loli.net/2018/08/19/5b792c501d0bd.png)](https://i.loli.net/2018/08/19/5b792c501d0bd.png)

Python3.7对应的包管理工具pip版本也为3.7，查看其路径

    [root@localhost Python-3.7.0]# which pip3.7
    /usr/local/bin/pip3.7

设置软链接

    ln -s /usr/local/bin/pip3.7 /usr/local/bin/pip

## 安装virtualenv ## 
安装virtualenv，用于隔离Python环境

    pip install virtualenv

[![ansible5.png](https://i.loli.net/2018/08/19/5b792c5019c9d.png)](https://i.loli.net/2018/08/19/5b792c5019c9d.png)

安装git工具及其依赖

    yum -y install git nss curl

创建ansible账户

    useradd ansible

切换用户

    [root@localhost Python-3.7.0]# su - ansible
    [ansible@localhost ~]$

在ansible用户下创建virtualenv实例，用于集成ansible2.5

    virtualenv -p /usr/local/bin/python3.7 .py3-a2.5-env

[![ansible6.png](https://i.loli.net/2018/08/19/5b792c5018bf5.png)](https://i.loli.net/2018/08/19/5b792c5018bf5.png)
源码安装git-ansible2.5

    cd /home/ansible/.py3-a2.5-env

下载源码

    git clone https://github.com/ansible/ansible.git

[![ansible7.png](https://i.loli.net/2018/08/19/5b792c5018b6c.png)](https://i.loli.net/2018/08/19/5b792c5018b6c.png)
加载virtualenv环境

    [ansible@localhost .py3-a2.5-env]$ source /home/ansible/.py3-a2.5-env/bin/activate
    (.py3-a2.5-env) [ansible@localhost .py3-a2.5-env]$

安装ansible依赖

    pip install paramiko PyYAML jinja2

[![ansible8.png](https://i.loli.net/2018/08/19/5b792c5018808.png)](https://i.loli.net/2018/08/19/5b792c5018808.png)

查看文件

    (.py3-a2.5-env) [ansible@localhost .py3-a2.5-env]$ ll
    总用量 8
    drwxrwxr-x 14 ansible ansible 4096 8月  18 20:24 ansible
    drwxrwxr-x  2 ansible ansible  248 8月  18 20:16 bin
    drwxrwxr-x  2 ansible ansible   24 8月  18 20:13 include
    drwxrwxr-x  3 ansible ansible   23 8月  18 20:13 lib
    -rw-rw-r--  1 ansible ansible   59 8月  18 20:16 pip-selfcheck.json

移动源码至虚拟环境

    mv ansible/ .py3-a2.5-env/

进入虚拟环境源码目录

    (.py3-a2.5-env) [ansible@localhost .py3-a2.5-env]$ cd .py3-a2.5-env/
    (.py3-a2.5-env) [ansible@localhost .py3-a2.5-env]$ ll
    总用量 108
    drwxrwxr-x  2 ansible ansible   223 8月  18 20:24 bin
    drwxrwxr-x  3 ansible ansible    63 8月  18 20:24 changelogs
    -rw-rw-r--  1 ansible ansible 10591 8月  18 20:24 CODING_GUIDELINES.md
    drwxrwxr-x  4 ansible ansible    53 8月  18 20:24 contrib
    -rw-rw-r--  1 ansible ansible 35148 8月  18 20:24 COPYING
    drwxrwxr-x  7 ansible ansible    71 8月  18 20:24 docs
    -rw-rw-r--  1 ansible ansible    48 8月  18 20:24 docsite_requirements.txt
    drwxrwxr-x  4 ansible ansible   192 8月  18 20:24 examples
    drwxrwxr-x  5 ansible ansible   305 8月  18 20:24 hacking
    drwxrwxr-x  3 ansible ansible    21 8月  18 20:24 lib
    drwxrwxr-x  2 ansible ansible    78 8月  18 20:24 licenses
    -rw-rw-r--  1 ansible ansible 13452 8月  18 20:24 Makefile
    -rw-rw-r--  1 ansible ansible   557 8月  18 20:24 MANIFEST.in
    -rw-rw-r--  1 ansible ansible   201 8月  18 20:24 MODULE_GUIDELINES.md
    drwxrwxr-x 10 ansible ansible   120 8月  18 20:24 packaging
    -rw-rw-r--  1 ansible ansible  5265 8月  18 20:24 README.rst
    -rw-rw-r--  1 ansible ansible   371 8月  18 20:24 requirements.txt
    -rw-rw-r--  1 ansible ansible 10586 8月  18 20:24 setup.py
    -rw-rw-r--  1 ansible ansible  3287 8月  18 20:24 shippable.yml
    drwxrwxr-x 10 ansible ansible   121 8月  18 20:24 test
    -rw-rw-r--  1 ansible ansible  1103 8月  18 20:24 tox.ini

切换版本

    (.py3-a2.5-env) [ansible@localhost .py3-a2.5-env]$ git checkout stable-2.5

分支 stable-2.5 设置为跟踪来自 origin 的远程分支 stable-2.5。
切换到一个新分支 'stable-2.5'

    (.py3-a2.5-env) [ansible@localhost ansible]$ git branch
      devel
    * stable-2.5
    
    (.py3-a2.5-env) [ansible@localhost ansible]$ pwd
    /home/ansible/.py3-a2.5-env/ansible

## 加载ansible2.5版本 ## 

    source /home/ansible/.py3-a2.5-env/ansible/hacking/env-setup -q

验证版本

    (.py3-a2.5-env) [ansible@localhost ansible]$ ansible --version
    ansible 2.5.8 (stable-2.5 b23b1c2ee0) last updated 2018/08/18 20:35:45 (GMT +800)
      config file = None
      configured module search path = ['/home/ansible/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
      ansible python module location = /home/ansible/.py3-a2.5-env/ansible/lib/ansible
      executable location = /home/ansible/.py3-a2.5-env/ansible/bin/ansible
      python version = 3.7.0 (default, Aug 18 2018, 20:09:08) [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
