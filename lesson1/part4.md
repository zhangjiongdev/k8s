设置环境IP
```
yum install -y net-tools

vip=30.0.2.10
master1=30.0.2.11
master2=30.0.2.12
master3=30.0.2.13
node1=30.0.2.14
netswitch=`ifconfig | grep 'UP,BROADCAST,RUNNING,MULTICAST' | awk -F: '{print $1}'`
```

设置hosts
```
cat >>/etc/hosts<<EOF
${master1} master1
${master2} master2
${master3} master3
${node1} node1
EOF
```

配置 /etc/sysconfig/modules/ipvs.modules
```
cat > /etc/sysconfig/modules/ipvs.modules <<EOF
modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack_ipv4
EOF

chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod | grep -e ip_vs -e nf_conntrack_ipv4
```

安装keepalived+haproxy
```
yum install -y keepalived haproxy ipvsadm ipset

```