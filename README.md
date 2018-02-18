# Set Up Apache Airflow on Kubernetes
This Airflow setup has been implemented on IBM Cloud but you can run the code on any other cloud or even on-premisses or on Minikube. I'll let you know when you need to change code if you are on a different cloud.

#### Database
I'm using Postgres to store all the Airflow metadata. In case you don't have your own postgres or mysql database, all the required files to setup a postgres database on Kubernetes are in the 'postgres' directory.

#### Persistent Volume Claims
First you need to create persistent volumes to make them available for the deployments which will be created in the following steps. Make sure you are in the same directory as all the yml files provided in this repo.
1. To create the persistent volume run `kubectl apply -f airflow-pvc.yml`
>This is the step you may need to make some changes in case you are running on a different cloud provider. You need to check the storage classes they provide and use them instead.
2. To check your new persistent volume run claim `kubectl get pvc`

#### Creating the Docker image
For the following steps you need to have Docker instlled on your local machine to be able to build the Airflow image.
1. Create the Airflow image on your local machine running the following command:
```
docker build -t registry.ng.bluemix.net/<your namespace>/apache-airflow:1.9
```
>The image tag here follows the IBM cloud registry directives. Use the correct registry for your environment / cloud.
2. Make sure your image has been created successfully running `docker images` to list all the local images.
3. Push the image to your cloud provider (in this case IBM Cloud):
```
docker push registry.ng.bluemix.net/proxxi_cts/apache-airflow:1.9
```

#### Creating the Airflow Deployments
Now it's time to create the Airflow deployments, web and scheduler. At this time your must have your postgres or mysql database up and running.
1. Create the Airflow web running the following command:
```
kubectl create -f dep-airflow-web.yml
```
>Airflow web is responsible for all the web interface with some GUI controls as well as graphics and dashboards.
2. Ensure your deployment is running using the `kubectl get deployments` command. To view more details run `kubectl get pods` to view all the pods, copy your dep-airflow-web pod and run the command `kubectl describe pod dep-airflow-web-<some code>`.
3. Create the Airflow scheduler running the following:
```
kubectl create -f dep-airflow-scheduler.yml
```
>Airflow scheduler is responsible for runnning a deamon to trigger any scheduled DAG.
2. Follow the steps in Airflow web to check the deployment is running.

#### Exposing the Web interface
There are two ways to access the Airflow interface.
1. A more secure way is port-forwarding the pod port to your local machine. To do so, get the pod name from your deployment running `kubectl get pods` and then using the pod name run:
```
kubectl port-forward <your pod name> <local port>:<pod port>
```
>This way you restrict your access to your local host increasing the setup security.
2. Exposing the port so it can be accessed using the Kubernetes cluster IP.<BR>
  To do so create the Airflow service running `kubectl create -f service-airflow.yml`<BR>
  Check your service has been created running `kubectl get services`.

>To access the Airflow interface you need to get the Kubernetes cluster IP and the way to get that depends on your cloud provider. To do so on IBM Cloud run `bx cs clusters` to get your cluster name and then `bx cs workers <your cluster name>`. The command outputs some info about the cluster including the cluster worker public IP. With that simple open the address (<worker public IP>:30002) on your browser.<BR>
  You may need a more robust setup using Ingress to redirect the access to the correct worker within the cluster.

#### A word on volume permissions
On IBM Cloud, all the PVCs are owned by the "nobody" user and other normal user does not have permission to write on them. The second link in the references session below describe some workarounds for that but I'd like to share an easier way.<BR><BR>
Create the PVC and then mount it in a simple pod so you can access it (you can find really simple pods on the internet). Access the container in the pod runnin `kubectl exec -it <pod name> /bin/bash`.<BR><BR>
In the container as root, go to the mounted volume and create two folders, 'dags' and 'logs', grant them read, write and execute permission for others.<BR><BR>
If you go to your airflow deployment now and access it, you'll be able to access those folders and write on them being the airflow user.

#### References
Some links on how to manage volumes on Kubernetes with IBM Cloud
* [Creating Persistent Volumes on IBM Cloud](https://console.bluemix.net/docs/containers/cs_storage.html#storage)
* [Handling volumes permissions on IBM Cloud](https://console.bluemix.net/docs/containers/cs_storage.html#nonroot)
