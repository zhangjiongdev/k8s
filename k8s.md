

- 用virtual box 创建2台虚机
30.0.2.11
30.0.2.12
- 把虚机的 CPU 调整到2 core
- 禁用selinux(30.0.2.11 30.0.2.12)
- 安装docker(30.0.2.11 30.0.2.12)
- 修改机器名
    - 30.0.2.11
    ```
    hostnamectl set-hostname master1
    ```
    - 30.0.2.12
    ```
    hostnamectl set-hostname master2
    ```
- 检查docker安装
    - 30.0.2.11 30.0.2.12
    ```
    systemctl status docker
    ```
- 关闭swap
    - 30.0.2.11 30.0.2.12
    ```
    sudo swapoff -a
    
    sudo sed -i "s/\/dev\/mapper\/centos-swap/# \/dev\/mapper\/centos-swap/g" /etc/fstab
    ```
- 修改sysctl内核参数
    - 30.0.2.11 30.0.2.12
    ```
    cat << EOF > /etc/sysctl.d/k8s.conf
    net.bridge.bridge-nf-call-ip6tables = 1
    net.bridge.bridge-nf-call-iptables = 1
    vm.swappiness=0
    net.ipv4.ip_forward = 1
    EOF
    
    modprobe br_netfilter
    sysctl -p /etc/sysctl.d/k8s.conf
    sysctl --system
    
    ```
- kube-proxy开启ipvs的前置条件
    - 30.0.2.11 30.0.2.12
    ```
    cat << EOF > /etc/sysconfig/modules/ipvs.modules
    #!/bin/bash
    modprobe -- ip_vs
    modprobe -- ip_vs_rr
    modprobe -- ip_vs_wrr
    modprobe -- ip_vs_sh
    modprobe -- nf_conntrack_ipv4
    EOF
    
    chmod 755 /etc/sysconfig/modules/ipvs.modules && bash /etc/sysconfig/modules/ipvs.modules && lsmod | grep -e ip_vs -e nf_conntrack_ipv4
    ```
- 配置kubernetes yum源
    - 30.0.2.11 30.0.2.12
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
- 安装 kubelet kubeadm kubectl
    - 30.0.2.11 30.0.2.12
    ```
    yum makecache fast
    yum install -y kubelet kubeadm kubectl
    ```
- 运行 kubelet
    - 30.0.2.11 30.0.2.12
    ```
    systemctl enable kubelet
    systemctl start kubelet
    ```
- 下载镜像
    - 30.0.2.11 30.0.2.12
    ```
    MY_REGISTRY=registry.cn-hangzhou.aliyuncs.com/openthings

    docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.1
    docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.1
    docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.1
    docker pull ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.1
    docker pull ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10
    docker pull ${MY_REGISTRY}/k8s-gcr-io-pause:3.1
    docker pull ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1
    
    docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-apiserver:v1.14.1 k8s.gcr.io/kube-apiserver:v1.14.1
    docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-scheduler:v1.14.1 k8s.gcr.io/kube-scheduler:v1.14.1
    docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-controller-manager:v1.14.1 k8s.gcr.io/kube-controller-manager:v1.14.1
    docker tag ${MY_REGISTRY}/k8s-gcr-io-kube-proxy:v1.14.1 k8s.gcr.io/kube-proxy:v1.14.1
    docker tag ${MY_REGISTRY}/k8s-gcr-io-etcd:3.3.10 k8s.gcr.io/etcd:3.3.10
    docker tag ${MY_REGISTRY}/k8s-gcr-io-pause:3.1 k8s.gcr.io/pause:3.1
    docker tag ${MY_REGISTRY}/k8s-gcr-io-coredns:1.3.1 k8s.gcr.io/coredns:1.3.1
    
    ```
- 修改配置信息
    - 30.0.2.11 30.0.2.12
    ```
    cat << EOF >> /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
    Environment="KUBELET_CGROUP_ARGS=--cgroup-driver=cgroupfs"
    Environment="KUBELET_EXTRA_ARGS=--fail-swap-on=false"
    EOF
    
    systemctl daemon-reload
    ```
- 修改hosts
    - 30.0.2.11 30.0.2.12
    ```
    cat << EOF >> /etc/hosts
    30.0.2.11 master1
    30.0.2.12 master2
    EOF
    
    ```

- 初始化
    - 30.0.2.11
    ```
    kubeadm init --kubernetes-version=v1.14.1 --apiserver-advertise-address=30.0.2.11 --pod-network-cidr=10.244.0.0/16
    
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config


    kubectl get cs
    ```
- 下载 kube-flannel.yml
    - 30.0.2.11
    ```
    yum install -y wget
    wget https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
    ```
- flannel
    - 30.0.2.11
    ```
    kubectl apply -f kube-flannel.yml
    
    
    kubectl get pod --all-namespaces -o wide
    ```
    
- 复制ca证书
    - 30.0.2.11
    ```
    ssh root@MASTER2 "mkdir -p /etc/kubernetes/pki/etcd"
    scp /etc/kubernetes/pki/ca.* root@MASTER2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/sa.* root@MASTER2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/front-proxy-ca.* root@MASTER2:/etc/kubernetes/pki/
    scp /etc/kubernetes/pki/etcd/ca.* root@MASTER2:/etc/kubernetes/pki/etcd/
    scp /etc/kubernetes/admin.conf root@MASTER2:/etc/kubernetes/
    ```
- 重启kubelet
    - 30.0.2.12
    ```
    systemctl restart kubelet
    ```

- 加入集群
    - 30.0.2.12
    ```
    kubeadm join 30.0.2.11:6443 --token 6wgxjf.8l7xdbbupwnbnf7z --discovery-token-ca-cert-hash sha256:b34e72280355492d4ff59b741c260838939d880d694e58853a97a95091b06f98 --experimental-control-plane
    ```

- 返回信息
```
[preflight] Running pre-flight checks
	[WARNING IsDockerSystemdCheck]: detected "cgroupfs" as the Docker cgroup driver. The recommended driver is "systemd". Please follow the guide at https://kubernetes.io/docs/setup/cri/
[preflight] Reading configuration from the cluster...
[preflight] FYI: You can look at this config file with 'kubectl -n kube-system get cm kubeadm-config -oyaml'
error execution phase preflight: 
One or more conditions for hosting a new control plane instance is not satisfied.

unable to add a new control plane instance a cluster that doesn't have a stable controlPlaneEndpoint address

Please ensure that:
* The cluster has a stable controlPlaneEndpoint address.
* The certificates that must be shared among control plane instances are provided.
```