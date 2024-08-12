#!/usr/bin/env python
# import subprocess
# import os
from cdk8s import App, Chart
from constructs import Construct
from imports import k8s

class MyChart(Chart):
   def __init__(self, scope: Construct, id: str, *, ns: str, app_label: str):
       super().__init__(scope, id)

       # Define a Kubernetes Namespace
       k8s.KubeNamespace(self, "my-namespace",
                         metadata=k8s.ObjectMeta(name=ns))

       # Define a Kubernetes Deployment
       k8s.KubeDeployment(self, "my-deployment",
                       metadata=k8s.ObjectMeta(namespace=ns),
                       spec=k8s.DeploymentSpec(
                           replicas=3,
                           selector=k8s.LabelSelector(match_labels={"app": app_label}),
                           template=k8s.PodTemplateSpec(
                               metadata=k8s.ObjectMeta(labels={"app": app_label}),
                               spec=k8s.PodSpec(containers=[
                                   k8s.Container(
                                       name="app-container",
                                       image="nginx:latest",
                                       ports=[k8s.ContainerPort(container_port=80)],
                                       resources=k8s.ResourceRequirements(
                                           requests={
                                               "cpu": k8s.Quantity.from_string("100m"),
                                               "memory": k8s.Quantity.from_string("500Mi")
                                           },
                                           limits={
                                               "cpu": k8s.Quantity.from_string("100m"),
                                               "memory": k8s.Quantity.from_string("500Mi")
                                           }
                                       )
                                   )
                               ])
                           )
                       )
                   )

       # Define a Kubernetes Service
       k8s.KubeService(self, "my-service",
                       metadata=k8s.ObjectMeta(namespace=ns, name="my-service", labels={"app": app_label}),
                       spec=k8s.ServiceSpec(
                           selector={"app": app_label},
                           ports=[k8s.ServicePort(port=80, target_port=k8s.IntOrString.from_number(80))]
                       ))

       # Define a Kubernetes Ingress
       k8s.KubeIngress(self, "my-ingress",
                       metadata=k8s.ObjectMeta(namespace=ns),
                       spec=k8s.IngressSpec(
                           ingress_class_name="nginx",
                           rules=[
                               k8s.IngressRule(
                                   host="myapp.danslinky",
                                   http=k8s.HttpIngressRuleValue(
                                       paths=[
                                           k8s.HttpIngressPath(
                                               path="/",
                                               path_type="Prefix",
                                               backend=k8s.IngressBackend(
                                                   service=k8s.IngressServiceBackend(
                                                       name="my-service",
                                                       port=k8s.ServiceBackendPort(number=80)
                                                   )
                                               )
                                           )
                                       ]
                                   )
                               )
                           ]
                       ))

app = App()
MyChart(app, "my-website", ns="my-namespace", app_label="my-app")
app.synth()