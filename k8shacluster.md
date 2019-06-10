## 基于 kubeadm 搭建 Kubernetes HA 集群

供学习测试使用


# 前言
本文档以3台master节点+1台node节点为例，详细如下：
```
30.0.2.11 master1
30.0.2.12 master2
30.0.2.13 master3
30.0.2.14 node1
```

# master1

#### 每台机器都要装好docker并启动了服务

##### 1. 安装wget
```
yum install -y wget
```
##### 2. 提前下载需要的k8s docker images
```
MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10
docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
docker pull ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1
docker pull jmgao1983/flannel:v0.11.0-amd64

docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2 k8s.gcr.io/kube-apiserver:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2 k8s.gcr.io/kube-controller-manager:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2 k8s.gcr.io/kube-scheduler:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2 k8s.gcr.io/kube-proxy:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10 k8s.gcr.io/etcd:3.3.10
docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
docker tag ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1 k8s.gcr.io/coredns:1.3.1
docker tag jmgao1983/flannel:v0.11.0-amd64 quay.io/coreos/flannel:v0.11.0-amd64
```

#### 3. 关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```

##### 设置环境IP
```
vip=30.0.2.10
master1=30.0.2.11
master2=30.0.2.12
master3=30.0.2.13
node1=30.0.2.14
netswitch=`ifconfig | grep 'UP,BROADCAST,RUNNING,MULTICAST' | awk -F: '{print $1}'`
```
#### 4. 设置hosts
```
cat >>/etc/hosts<<EOF
${master1} master1
${master2} master2
${master3} master3
${node1} node1
EOF
```
#### 5. 生成公钥与私钥对
```
ssh-keygen -t rsa
```

#### 6. 
```
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
EOF

sysctl --system

```
#### 7. 
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
#### 8. 安装keepalived+haproxy
```
yum install -y keepalived haproxy ipvsadm ipset
```
#### 9. 
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

##### 10. 配置haproxy
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

##### 11. 启动 keepalived
```
systemctl enable keepalived && systemctl start keepalived && systemctl status keepalived

```
##### 12. 启动 haproxy
```
systemctl enable haproxy && systemctl start haproxy && systemctl status haproxy

```


##### 13. 设置k8s repo
```
cat << EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
```

##### 14. 安装 kube 组件
```
yum makecache fast
yum install -y kubelet kubeadm kubectl
```

##### 15.  这是cgroupfs
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf

systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet
```
##### 16. 设置初始化位置文件
```
cat >kubeadm-init.yaml<<END1
apiVersion: kubeadm.k8s.io/v1beta1
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: abcdef.0123456789abcdef
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: ${master1}
  bindPort: 6443
nodeRegistration:
  criSocket: /var/run/dockershim.sock
  name: master1
  taints:
  - effect: NoSchedule
    key: node-role.kubernetes.io/master
---
apiVersion: kubeadm.k8s.io/v1beta1
kind: ClusterConfiguration
apiServer:
  timeoutForControlPlane: 4m0s
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controlPlaneEndpoint: "${vip}:6443"
dns:
  type: CoreDNS
etcd:
  local:
    dataDir: /var/lib/etcd
kubernetesVersion: v1.14.2
networking:
  dnsDomain: cluster.local
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.245.0.0/16"
scheduler: {}
controllerManager: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: "ipvs"
END1


kubeadm init --config kubeadm-init.yaml

```
##### 17. 设置kube config
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

```
##### 18. 查看容器
```
  kubectl get cs
kubectl get pod --all-namespaces -o wide
```
##### 19. 下载flannel配置
```
wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
##### 20. 应用flannel
```
kubectl apply -f kube-flannel.yml
```
##### 21. 查看容器
```
  kubectl get nodes
kubectl -n kube-system get pod -o wide
```







# master2/3(4....)

#### 每台机器都要装好docker并启动了服务

##### 1. 
```
MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10
docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
docker pull ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1
docker pull jmgao1983/flannel:v0.11.0-amd64

docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2 k8s.gcr.io/kube-apiserver:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2 k8s.gcr.io/kube-controller-manager:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2 k8s.gcr.io/kube-scheduler:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2 k8s.gcr.io/kube-proxy:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10 k8s.gcr.io/etcd:3.3.10
docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
docker tag ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1 k8s.gcr.io/coredns:1.3.1
docker tag jmgao1983/flannel:v0.11.0-amd64 quay.io/coreos/flannel:v0.11.0-amd64
```


##### 2. 关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```

##### 3. 设置环境IP
```
vip=30.0.2.10
master1=30.0.2.11
master2=30.0.2.12
master3=30.0.2.13
node1=30.0.2.14
netswitch=`ifconfig | grep 'UP,BROADCAST,RUNNING,MULTICAST' | awk -F: '{print $1}'`
```

##### 4. 设置hosts
```
cat >>/etc/hosts<<EOF
${master1} master1
${master2} master2
${master3} master3
${node1} node1
EOF
```
##### 5. 复制公钥
```
mkdir /root/.ssh
chmod 700 /root/.ssh
scp root@master1:/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
```

#### 6. 复制 ca 
```
mkdir -p /etc/kubernetes/pki/etcd
scp root@master1:/etc/kubernetes/pki/\{ca.*,sa.*,front-proxy-ca.*\} /etc/kubernetes/pki/
scp root@master1:/etc/kubernetes/pki/etcd/ca.* /etc/kubernetes/pki/etcd/
scp root@master1:/etc/kubernetes/admin.conf /etc/kubernetes/

mkdir -p $HOME/.kube
scp root@master1:$HOME/.kube/config $HOME/.kube/config

```


#### 7. 配置k8s.conf
```
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
EOF

sysctl --system

```
#### 8. 配置ipvs
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
#### 9. 安装keepalived haproxy
```
yum install -y keepalived haproxy ipvsadm ipset

```

#### 10. 配置keepalive
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
    priority 90
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

##### 11. 配置haproxy
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

##### 12. 启动keepalived
```
systemctl enable keepalived && systemctl start keepalived && systemctl status keepalived
```
##### 13. 启动haproxy
```
systemctl enable haproxy && systemctl start haproxy && systemctl status haproxy
```


##### 14. 设置k8s repo
```
cat << EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

yum makecache fast
yum install -y kubelet kubeadm kubectl

```

##### 15. 设置cgroupfs
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet

```
##### 16. 加入集群
```

(master)
kubeadm token create --print-join-command
kubeadm join ...  --experimental-control-plane

kubectl get cs
kubectl get nodes
kubectl -n kube-system get pod -o wide
kubectl get pod --all-namespaces -o wide
```








# node1(2,3,...)

#### 每台机器都要装好docker并启动了服务

#### 1. 关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```
#### 2. 设置环境IP
```
vip=30.0.2.10
master1=30.0.2.11
master2=30.0.2.12
master3=30.0.2.13
node1=30.0.2.14
```
#### 3. 设置hosts
```
cat >>/etc/hosts<<EOF
${master1} MASTER1
${master2} MASTER2
${master3} MASTER3
${node1} NODE1
EOF
```
#### 4. 复制公钥
```
mkdir /root/.ssh
chmod 700 /root/.ssh
scp root@master1:/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
```
#### 5. 设置k8s.conf
```
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
EOF

sysctl --system

```
#### 6. 配置ipvs
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

#### 7. 下载容器镜像
```
MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
docker pull jmgao1983/flannel:v0.11.0-amd64

docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2 k8s.gcr.io/kube-proxy:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
docker tag jmgao1983/flannel:v0.11.0-amd64 quay.io/coreos/flannel:v0.11.0-amd64

```

#### 8. 设置k8s repo
```
cat << EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

yum makecache fast
yum install -y kubelet kubeadm kubectl

```

#### 9. 设置cgroupfs
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf

systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet

```

##### 10. 设置kube config文件
```
mkdir -p $HOME/.kube
scp root@master1:$HOME/.kube/config $HOME/.kube/config

（master）
kubeadm token create --print-join-command
kubeadm join ...

kubectl get cs
kubectl get pod --all-namespaces -o wide
```