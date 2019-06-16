VirtualBox 新建虚机
```
名称：（自定义）
类型：Linux
版本：Red Hat（64-bit）

内存大小：1024 MB
虚拟磁盘：现在创建虚拟硬盘（默认）
虚拟硬盘文件类型：VDI（VirtualBox 磁盘映像）
存储在物理硬盘上：动态分配
```

调整CPU设置
```
选中虚拟机（新创建的）>> 控制 >> 设置 >> 系统 >> 处理器 
处理器数量：2
```

调整网络设置
```
选中虚拟机（新创建的）>> 控制 >> 设置 >> 网络 >> 网卡 1 >>
启用网络连接：勾选
连接方式：NAT 网络
界面名称：nat30

```

设置安装光盘
```
选中虚拟机（新创建的）>> 控制 >> 设置 >> 存储 >> 控制器: IDE >> 没有盘片
分配光驱: 第二IDE控制器主通道 >> 圆形图标 >> 选择一个虚拟光盘文件 >> 找到 CentOS-7-x86_64-DVD-1810.iso 文件

```

安装CentOS-7-x86_64 （跳过部分安装步骤明细）
```
选中虚拟机（新创建的）>> 启动

选择：中文、简体中文（中国）
软件选择：最小安装

# 没有说明的选项均为默认值
```

用root账号登录CentOS

启用网卡
```
sed -i "s/ONBOOT=no/ONBOOT=yes/g" /etc/sysconfig/network-scripts/ifcfg-enp0s3
service network restart
```

停止、禁用CentOS防火墙
```
systemctl stop firewalld
systemctl disable firewalld
```

禁用selinux
```
sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/sysconfig/selinux
```

设置静态IP地址
```
hip=30.0.2.11
sed -i "s/BOOTPROTO=dhcp/BOOTPROTO=static/g" /etc/sysconfig/network-scripts/ifcfg-enp0s3
cat >>/etc/sysconfig/network-scripts/ifcfg-enp0s3<<EOF
IPADDR=${hip}
NETMASK=255.255.255.0
GATEWAY=30.0.2.1
DNS1=30.0.2.1
EOF

```
修改主机名
```
hostnamectl set-hostname master1
```

重启服务器
```
reboot
```