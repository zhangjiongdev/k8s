# 前言
本文档以3台master节点+1台node节点为例

# MASTER1
#### 1. 关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```
#### 2. 设置hosts
```
cat >>/etc/hosts<<EOF
30.0.2.11 MASTER1
30.0.2.12 MASTER2
30.0.2.13 MASTER3
30.0.2.14 NODE1
EOF
```
#### 3. 生成公钥与私钥对
```
ssh-keygen -t rsa
```
      #### 4. 
      ```
      ssh-copy-id MASTER2
      ssh-copy-id MASTER3
      ssh-copy-id NODE1
      ```
#### 5. 
```
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
EOF
```
#### 6. 
```
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
```
#### 8. 
```
chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod \| grep -e ip_vs -e nf_conntrack_ipv4
```
#### 9. 
```
yum install -y keepalived haproxy ipvsadm ipset
```
#### 10. 
```
mv /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.bak
```
##### 11. 
```
nodename=`/bin/hostname`
cat >/etc/keepalived/keepalived.conf<<END4
! Configuration File for keepalived
global_defs {
   router_id ${nodename}
}
vrrp_instance VI_1 {
    state MASTER
    interface enp0s3
    virtual_router_id 88
    advert_int 1
    priority 100         
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
      30.0.2.10/24
    }
}
END4
```

##### 12. 
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
        bind 30.0.2.10:8443
        mode tcp
        balance roundrobin
        timeout server 15s
        timeout connect 15s
 
        server apiserver01 30.0.2.11:6443 check port 6443 inter 5000 fall 5
        server apiserver02 30.0.2.12:6443 check port 6443 inter 5000 fall 5
        server apiserver03 30.0.2.13:6443 check port 6443 inter 5000 fall 5
END1
```

##### 13. 
```
systemctl enable keepalived && systemctl start keepalived && systemctl status keepalived
```
##### 14. 
```
systemctl enable haproxy && systemctl start haproxy && systemctl status haproxy
```
##### 15. 
```
MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10
docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
docker pull ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1

docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2 k8s.gcr.io/kube-apiserver:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2 k8s.gcr.io/kube-controller-manager:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2 k8s.gcr.io/kube-scheduler:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2 k8s.gcr.io/kube-proxy:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10 k8s.gcr.io/etcd:3.3.10
docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
docker tag ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1 k8s.gcr.io/coredns:1.3.1
```

##### 16.
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

##### 17. 
```
yum makecache fast
yum install -y kubelet kubeadm kubectl
```

##### 18. 
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
```
##### 19. 
```
systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet
```
##### 20. 
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
  advertiseAddress: 30.0.2.11
  bindPort: 6443
nodeRegistration:
  criSocket: /var/run/dockershim.sock
  name: MASTER1
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
controlPlaneEndpoint: "30.0.2.10:6443"
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
```
##### 21. 
```
kubeadm init --config kubeadm-init.yaml
```
##### 22. 
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
##### 23. 
```
kubectl get cs
kubectl get pod --all-namespaces -o wide
```
##### 24. 
```
ssh root@MASTER2 "mkdir -p /etc/kubernetes/pki/etcd"
scp /etc/kubernetes/pki/ca.* root@MASTER2:/etc/kubernetes/pki/
scp /etc/kubernetes/pki/sa.* root@MASTER2:/etc/kubernetes/pki/
scp /etc/kubernetes/pki/front-proxy-ca.* root@MASTER2:/etc/kubernetes/pki/
scp /etc/kubernetes/pki/etcd/ca.* root@MASTER2:/etc/kubernetes/pki/etcd/
scp /etc/kubernetes/admin.conf root@MASTER2:/etc/kubernetes/

ssh root@MASTER3 "mkdir -p /etc/kubernetes/pki/etcd"
scp /etc/kubernetes/pki/ca.* root@MASTER3:/etc/kubernetes/pki/
scp /etc/kubernetes/pki/sa.* root@MASTER3:/etc/kubernetes/pki/
scp /etc/kubernetes/pki/front-proxy-ca.* root@MASTER3:/etc/kubernetes/pki/
scp /etc/kubernetes/pki/etcd/ca.* root@MASTER3:/etc/kubernetes/pki/etcd/
scp /etc/kubernetes/admin.conf root@MASTER3:/etc/kubernetes/

ssh root@MASTER2 "mkdir -p $HOME/.kube"
scp $HOME/.kube/config root@MASTER2:$HOME/.kube/config

ssh root@MASTER3 "mkdir -p $HOME/.kube"
scp $HOME/.kube/config root@MASTER3:$HOME/.kube/config

ssh root@NODE1 "mkdir -p $HOME/.kube"
scp $HOME/.kube/config root@NODE1:$HOME/.kube/config
```
##### 25. 
```
wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```
##### 26. 
```
kubectl apply -f kube-flannel.yml
```
##### 27. 
```
kubectl get nodes
kubectl -n kube-system get pod -o wide
```







# master2/3(4....)



#### 1. 关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```
#### 2. 设置hosts
```
cat >>/etc/hosts<<EOF
30.0.2.11 MASTER1
30.0.2.12 MASTER2
30.0.2.13 MASTER3
30.0.2.14 NODE1
EOF
```
#### 4. 
```
mkdir /root/.ssh
chmod 700 /root/.ssh
scp root@master1:/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
```
#### 5. 
```
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
EOF
```
#### 6. 
```
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
```
#### 8. 
```
chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod \| grep -e ip_vs -e nf_conntrack_ipv4
```
#### 9. 
```
yum install -y keepalived haproxy ipvsadm ipset
```
#### 10. 
```
mv /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.bak
```
##### 11. 
```
cat >/etc/keepalived/keepalived.conf<<END4
! Configuration File for keepalived
global_defs {
   router_id MASTER2
}
vrrp_instance VI_1 {
    state MASTER
    interface enp0s3
    virtual_router_id 88
    advert_int 1
    priority 100         
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    virtual_ipaddress {
      30.0.2.10/24
    }
}
END4
```

##### 12. 
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
        bind 30.0.2.10:8443
        mode tcp
        balance roundrobin
        timeout server 15s
        timeout connect 15s
 
        server apiserver01 30.0.2.11:6443 check port 6443 inter 5000 fall 5
        server apiserver02 30.0.2.12:6443 check port 6443 inter 5000 fall 5
        server apiserver03 30.0.2.13:6443 check port 6443 inter 5000 fall 5
END1
```

##### 13. 
```
systemctl enable keepalived && systemctl start keepalived && systemctl status keepalived
```
##### 14. 
```
systemctl enable haproxy && systemctl start haproxy && systemctl status haproxy
```
##### 15. 
```
MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10
docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
docker pull ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1

docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2 k8s.gcr.io/kube-apiserver:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2 k8s.gcr.io/kube-controller-manager:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2 k8s.gcr.io/kube-scheduler:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2 k8s.gcr.io/kube-proxy:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10 k8s.gcr.io/etcd:3.3.10
docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
docker tag ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1 k8s.gcr.io/coredns:1.3.1
```

##### 16.
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

##### 17. 
```
yum makecache fast
yum install -y kubelet kubeadm kubectl
```

##### 18. 
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
```
##### 19. 
```
systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet
```

##### 23. 
```
kubectl get cs
kubectl get pod --all-namespaces -o wide
```
##### 27. 
```
kubectl get nodes
kubectl -n kube-system get pod -o wide
```








# node1(2,3,...)

#### 1. 关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```
#### 2. 设置hosts
```
cat >>/etc/hosts<<EOF
30.0.2.11 MASTER1
30.0.2.12 MASTER2
30.0.2.13 MASTER3
30.0.2.14 NODE1
EOF
```
#### 4. 
```
mkdir .ssh
chmod 700 .ssh
scp root@t1:/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
```
#### 5. 
```
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_nonlocal_bind = 1
net.ipv4.ip_forward = 1
vm.swappiness=0
EOF
```
#### 6. 
```
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
```
#### 8. 
```
chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod \| grep -e ip_vs -e nf_conntrack_ipv4
```

##### 15. 
```
MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2
docker pull ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10
docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
docker pull ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1

docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.2 k8s.gcr.io/kube-apiserver:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.2 k8s.gcr.io/kube-controller-manager:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.2 k8s.gcr.io/kube-scheduler:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.2 k8s.gcr.io/kube-proxy:v1.14.2
docker tag ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10 k8s.gcr.io/etcd:3.3.10
docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
docker tag ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1 k8s.gcr.io/coredns:1.3.1
```

##### 16.
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

##### 17. 
```
yum makecache fast
yum install -y kubelet kubeadm kubectl
```

##### 18. 
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
```
##### 19. 
```
systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet
```

##### 23. 
```
kubectl get cs
kubectl get pod --all-namespaces -o wide
```


