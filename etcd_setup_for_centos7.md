> 只是文档，不是一键安装






> *server1:30.0.2.11<br>server2:30.0.2.12 <br>server3:30.0.2.13*


server 1~3
```
ETCD_VER=v3.3.13

GITHUB_URL=https://github.com/etcd-io/etcd/releases/download

DOWNLOAD_URL=${GITHUB_URL}

curl -L ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz -o /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz

mkdir -p /tmp/etcd-download-test

tar xzvf /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz -C /tmp/etcd-download-test --strip-components=1

rm -f /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz

cp /tmp/etcd-download-test/etcd /usr/local/bin/
cp /tmp/etcd-download-test/etcdctl /usr/local/bin/

rm -rf /tmp/etcd-download-test/

/usr/local/bin/etcd --version
/usr/local/bin/etcdctl --version
```

```
#ETCDCTL_API=3
curl https://discovery.etcd.io/new?size=3
#https://discovery.etcd.io/43410f7029583f9d3f9e5bc1d64511e5
```


**server1**
```
mkdir -p /var/log/etcd/
mkdir -p /data/etcd/

/usr/local/bin/etcd --name etcd1 --data-dir /data/etcd \
--initial-advertise-peer-urls http://30.0.2.11:2380 \
--listen-peer-urls http://30.0.2.11:2380 \
--listen-client-urls http://30.0.2.11:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://30.0.2.11:2379 \
--discovery https://discovery.etcd.io/43410f7029583f9d3f9e5bc1d64511e5
```

**server2**
```
mkdir -p /var/log/etcd/
mkdir -p /data/etcd/

/usr/local/bin/etcd --name etcd2 --data-dir /data/etcd \
--initial-advertise-peer-urls http://30.0.2.12:2380 \
--listen-peer-urls http://30.0.2.12:2380 \
--listen-client-urls http://30.0.2.12:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://30.0.2.12:2379 \
--discovery https://discovery.etcd.io/43410f7029583f9d3f9e5bc1d64511e5
```

**server3**
```
mkdir -p /var/log/etcd/
mkdir -p /data/etcd/

/usr/local/bin/etcd --name etcd3 --data-dir /data/etcd \
--initial-advertise-peer-urls http://30.0.2.13:2380 \
--listen-peer-urls http://30.0.2.13:2380 \
--listen-client-urls http://30.0.2.13:2379,http://127.0.0.1:2379 \
--advertise-client-urls http://30.0.2.13:2379 \
--discovery https://discovery.etcd.io/43410f7029583f9d3f9e5bc1d64511e5
```

**check server1**
```
/usr/local/bin/etcdctl member list
/usr/local/bin/etcdctl cluster-health
```