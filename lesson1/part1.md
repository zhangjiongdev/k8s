部署环境
```
台式电脑：
CPU：Intel i7
内存：16GB
操作系统：64位 Windows 10 专业版

虚机软件：VirtualBox 6.0.8
虚机操作系统镜像：CentOS-7-x86_64-DVD-1810.iso
```


VirtualBox and CentOS
```
VirtualBox 主页
www.virtualbox.org

VirtualBox-6.0.8-130520-Win.exe
https://download.virtualbox.org/virtualbox/6.0.8/VirtualBox-6.0.8-130520-Win.exe

Oracle_VM_VirtualBox_Extension_Pack-6.0.8.vbox-extpack
https://download.virtualbox.org/virtualbox/6.0.8/Oracle_VM_VirtualBox_Extension_Pack-6.0.8.vbox-extpack

CentOS 主页
https://www.centos.org

CentOS-7-x86_64-DVD-1810.iso
http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-1810.iso
```

安装VirtualBox-6.0.8-130520-Win.exe


VirtualBox 导入 Extension_Pack
```
菜单：
管理 >> 全局设定 >> 扩展 >> 添加新包 >> 选择Oracle_VM_VirtualBox_Extension_Pack-6.0.8.vbox-extpack
```

创建NAT网络
```
管理 >> 全局设定 >> 网络 >> 添加新NAT网络 >> 编辑NAT网络（新添加的）

修改：
网络名称：nat30
网络CIDR：30.0.2.0/24
支持 DHCP：勾选
支持 IPv6：勾选

端口转发 >> IPv4
名称 | 协议 | 主机IP | 主机端口 | 
master1 | TCP | 0.0.0.0 | 2122 | 30.0.2.11 | 22
master2 | TCP | 0.0.0.0 | 2222 | 30.0.2.12 | 22
master3 | TCP | 0.0.0.0 | 2322 | 30.0.2.13 | 22
node1 | TCP | 0.0.0.0 | 2422 | 30.0.2.14 | 22
```
