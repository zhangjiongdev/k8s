## Centos7 安装 docker

#### 1. 移除旧的版本
```
sudo yum remove docker \
docker-client \
docker-client-latest \
docker-common \
docker-latest \
docker-latest-logrotate \
docker-logrotate \
docker-selinux \
docker-engine-selinux \
docker-engine
```

#### 2. 安装一些必要的系统工具
```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
```

#### 3. 添加软件源信息
```
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

```


#### 4. 更新 yum 缓存
```
yum makecache fast
```

#### 5. 安装 Docker-ce
```
yum -y install docker-ce

```

#### 6. 启动 Docker 后台服务
```
systemctl start docker && systemctl enable docker
```

#### 7. 查看 Docker版本
```
docker --version
```
