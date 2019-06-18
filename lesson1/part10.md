创建nginx无状态容器(2个副本集)
```
cat << EOF > nginxdeployment.yaml
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2 # tells deployment to run 2 pods matching the template
  template: # create pods using pod definition in this template
    metadata:
      # unlike pod-nginx.yaml, the name is not included in the meta data as a unique name is
      # generated from the deployment name
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
        ports:
        - containerPort: 80
EOF

kubectl create -f nginxdeployment.yaml


kubectl get pods

```


创建nginx无状态容器的服务，并测试cluster-ip
```
cat << EOF > nginxsvc.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    run: nginx
spec:
  ports:
  - port: 80
    name: http
    protocol: TCP
    targetPort: 80
  selector:
    app: nginx
EOF


kubectl create -f nginxsvc.yaml


kubectl get svc
```