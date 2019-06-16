```
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

生成公钥与私钥对
```
ssh-keygen -t rsa

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

设置初始化位置文件
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

```

初始化
```
kubeadm init --config kubeadm-init.yaml

```

设置kube config
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

查看容器
```
kubectl get cs
kubectl get pod --all-namespaces -o wide

```

下载flannel配置
```
yum install -y wget

wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

应用flannel
```
kubectl apply -f kube-flannel.yml
```


查看容器
```
kubectl -n kube-system get pod -o wide

```