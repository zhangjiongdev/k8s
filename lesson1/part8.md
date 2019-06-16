下载需要的k8s docker images
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

关闭swap
```
echo 'swapoff -a' >> /etc/profile
source /etc/profile
```


复制公钥
```
mkdir /root/.ssh
chmod 700 /root/.ssh
scp root@master1:/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
```

复制 ca
```
mkdir -p /etc/kubernetes/pki/etcd
scp root@master1:/etc/kubernetes/pki/\{ca.*,sa.*,front-proxy-ca.*\} /etc/kubernetes/pki/
scp root@master1:/etc/kubernetes/pki/etcd/ca.* /etc/kubernetes/pki/etcd/
scp root@master1:/etc/kubernetes/admin.conf /etc/kubernetes/

mkdir -p $HOME/.kube
scp root@master1:$HOME/.kube/config $HOME/.kube/config

```

配置/etc/sysctl.d/k8s.conf
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


设置k8s 安装源信息
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

```


安装 kube 组件
```
yum install -y kubelet kubeadm kubectl

```

配置cgroups
```
echo  'Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"' >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
```
启动kubelet
```
systemctl enable kubelet && systemctl start kubelet && systemctl status kubelet
```

加入集群
```
kubeadm join 30.0.2.10:6443 --token abcdef.0123456789abcdef \
    --discovery-token-ca-cert-hash sha256:ff15d25af6327e348312bf3fddbba2e1f8b20f0ba26ca5cafdb9e3e5789aead0 \
    --experimental-control-plane
```

查看容器
```
kubectl -n kube-system get pod -o wide

```