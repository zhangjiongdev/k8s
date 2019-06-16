设置环境IP
```
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

配置keepalived
```
mv /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.bak

nodename=`/bin/hostname`
cat >/etc/keepalived/keepalived.conf<<END4
! Configuration File for keepalived
global_defs {
   router_id ${nodename}
}
vrrp_instance VI_1 {
    state MASTER
    interface ${netswitch}
    virtual_router_id 88
    advert_int 1
    priority 100
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
      ${vip}/24
    }
}
END4

```

配置haproxy
```
cat >/etc/haproxy/haproxy.cfg<<END1
global
        chroot  /var/lib/haproxy
        daemon
        group haproxy
        user haproxy
        log 127.0.0.1:514 local0 warning
        pidfile /var/lib/haproxy.pid
        maxconn 20000
        spread-checks 3
        nbproc 8
 
defaults
        log     global
        mode    tcp
        retries 3
        option redispatch
 
listen https-apiserver
        bind ${vip}:8443
        mode tcp
        balance roundrobin
        timeout server 15s
        timeout connect 15s
 
        server apiserver01 ${master1}:6443 check port 6443 inter 5000 fall 5
        server apiserver02 ${master2}:6443 check port 6443 inter 5000 fall 5
        server apiserver03 ${master3}:6443 check port 6443 inter 5000 fall 5
END1
```

启动 keepalived 和 haproxy
```
systemctl enable keepalived && systemctl start keepalived && systemctl status keepalived

systemctl enable haproxy && systemctl start haproxy && systemctl status haproxy
```