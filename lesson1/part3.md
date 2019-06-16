安装一些docker必要的系统工具
```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

```

添加 docker yum 源信息：
```
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

更新 yum 缓存
```
yum makecache fast
```

安装 Docker-ce
```
yum -y install docker-ce
```

启动 Docker 后台服务
```
systemctl start docker && systemctl enable docker
```

测试Docker版本
```
docker --version

Docker version 18.09.6, build 481bc77156
```
