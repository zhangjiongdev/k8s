*搭建ETCD所需要的私有的自动发现服务

>由于服务本身也依赖ETCD，所以可以先搭建一个静态发现的ETCD，或者使用公共的自动发现地址


**下载镜像**
```
docker pull quay.io/coreos/discovery.etcd.io

docker images

```

**启动容器**
```

docker run -d -p 80:8087 -e DISC_ETCD=http://30.0.2.11:2379 -e DISC_HOST=http://localhost quay.io/coreos/discovery.etcd.io

docker ps
netstat -tnlp

```

**获取自动发现服务地址**
```

curl http://localhost/new?size=3

# or
curl http://30.0.2.4/new?size=4

# or

curl --verbose -X PUT localhost:80/new
```