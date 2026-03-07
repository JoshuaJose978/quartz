---
title: Using Kubernetes with Tanzu, GCP, AWS, Azure
---

## **1. Overview**

Each cloud provider has its own Kubernetes management platform:
- **VMware Tanzu** (on-prem or in vSphere)
- **Google Kubernetes Engine (GKE)**
- **AWS Elastic Kubernetes Service (EKS)**
- **Azure Kubernetes Service (AKS)**

All four ultimately converge on using `kubectl` for cluster management—authentication and kubeconfig handling differ.

---

## **2. Common Concepts & Tools**

| Concept         | Use/Command                                |
|-----------------|--------------------------------------------|
| `kubectl`       | Standard K8s CLI tool, works on all clouds |
| Kubeconfig      | Stores cluster access details, contexts     |
| Context         | Named set of access info for a cluster      |
| Namespace       | Logical K8s resource grouping              |
| `k9s`           | Terminal-based K8s dashboard/browser       |

---

## **3. Cloud Provider-Specific CLI Tools**

| Platform/Cloud | CLI Tool          | Purpose                                              |
| -------------- | ----------------- | ---------------------------------------------------- |
| Tanzu/vSphere  | `kubectl vsphere` | Login, get kubeconfig for Tanzu/VCF managed clusters |
| GCP/GKE        | `gcloud`          | Auth, cluster credentials, manage cloud resources    |
| AWS/EKS        | `aws` & `eksctl`  | Auth, get cluster details, manage clusters           |
| Azure/AKS      | `az`              | Auth, get cluster creds, manage clusters             |

---

## **4. Step-by-Step Guide for Each Platform**

---

### **A. VMware Tanzu Kubernetes (vSphere / TKGS)**

#### **a. Authentication & Kubeconfig**

- Login and populate kubeconfig with cluster contexts:
  ```bash
  kubectl vsphere login \
    --server=https://<vcenter-or-supervisor-ip> \
    --insecure-skip-tls-verify \
    --vsphere-username <user@domain> \
    --tanzu-kubernetes-cluster-namespace <namespace> \
    --tanzu-kubernetes-cluster-name <workload-cluster>
  ```
- This uses SSO/vCenter credentials and populates kubeconfig with both Supervisor and Workload cluster contexts.

#### **b. Switch Context & Use Cluster**
```bash
kubectl config get-contexts
kubectl config use-context <workload-cluster-context>
```

#### **c. List Namespaces**
```bash
kubectl get namespaces
```

#### **d. Use a Namespace (kubectl/k9s)**
- For kubectl:
  ```bash
  kubectl -n <namespace> get pods
  ```
- For k9s:
  ```bash
  k9s -n <namespace>
  ```

---

### **B. Google Kubernetes Engine (GKE)**

#### **a. Authenticate to GCP (need IAM permissions)**
```bash
# If using personal identity (via browser)
gcloud auth login

# Or, use a service account key:
gcloud auth activate-service-account --key-file <service-account.json>
```

#### **b. Add GKE Cluster Kubeconfig**
```bash
gcloud container clusters get-credentials <gke-cluster-name> \
  --region <region> \
  --project <project-id>
```
- Automatically updates kubeconfig with a new context for the cluster.

#### **c. List & Use Context, Namespaces**
```bash
kubectl config get-contexts
kubectl config use-context <gke-context>
kubectl get namespaces
```

#### **d. Set Default Namespace for Context**
```bash
kubectl config set-context --current --namespace=<namespace>
```

#### **e. Use k9s**
```bash
k9s -n <namespace>
```

---

### **C. AWS Elastic Kubernetes Service (EKS)**

#### **a. Authenticate with AWS CLI**
```bash
aws configure  # Set AWS access keys/etc
# Or, if MFA, use an assumed role, etc
```

#### **b. Populate kubeconfig for EKS Cluster**
```bash
aws eks update-kubeconfig --region <region> --name <cluster-name>
```
- Adds/updates context in kubeconfig for your EKS cluster.

#### **c. List/Use Context and Namespace**
```bash
kubectl config get-contexts
kubectl config use-context <eks-context>
kubectl get namespaces
kubectl config set-context --current --namespace=<namespace>
```

#### **d. k9s**
```bash
k9s -n <namespace>
```

---

### **D. Azure Kubernetes Service (AKS)**

#### **a. Login to Azure**
```bash
az login  # device code or browser login
az account set --subscription "<Subscription Name or ID>"
```

#### **b. Get Cluster Credentials (Set Kubeconfig)**
```bash
az aks get-credentials --resource-group <rg-name> --name <aks-cluster-name>
```

#### **c. Use Context, Namespace, k9s**
```bash
kubectl config get-contexts
kubectl config use-context <aks-context>
kubectl get namespaces
kubectl config set-context --current --namespace=<namespace>
k9s -n <namespace>
```

---

## **5. Generic Kubernetes Workflow (Every Cloud)**

1. **Authenticate:**  
   - Login with cloud CLI as shown above.

2. **Get kubeconfig:**  
   - Use cloud-specific CLI to fetch and add/update cluster credentials to `~/.kube/config`.

3. **List and Change Contexts:**  
   ```bash
   kubectl config get-contexts
   kubectl config use-context <context-name>
   ```

4. **Work with Namespaces:**  
   - List:
     ```bash
     kubectl get namespaces
     ```
   - Set default for context:
     ```bash
     kubectl config set-context --current --namespace=<namespace>
     ```
   - Or use `-n` flag with kubectl and k9s:
     ```bash
     kubectl -n <namespace> get pods
     k9s -n <namespace>
     ```

---

## **6. Important Best Practices & Notes**

- **Never share your kubeconfig openly**; it contains access tokens and sensitive cluster info.
- **Always set your working namespace** in context or at command-line to minimize accidents (like applying resources to the wrong namespace).
- **Check your current context often:**
  ```bash
  kubectl config current-context
  ```
- **Use RBAC properly** (grant least-privilege per user/service-account).
- Consider using tools like [kubectx](https://github.com/ahmetb/kubectx) for quick context switching.
- **k9s** is a powerful TUI, but all namespace and context logic mirrors kubectl.

---

## **7. Troubleshooting Tips**

- If you get `You must be logged in...` or `forbidden`, check:
  - Your cloud CLI authentication/session.
  - kubeconfig context and role.
  - Namespace and resource RBAC.
- For GKE/EKS/AKS, ensure you have the correct roles/permissions in cloud IAM.
- For Tanzu/VMware, check cluster/namespace access in vSphere/vCenter.

---

### **Reference Table: Quick Commands**

| Task                      | Tanzu            | GKE                      | EKS                       | AKS                        |
|---------------------------|------------------|--------------------------|---------------------------|----------------------------|
| Login/auth                | `kubectl vsphere login` | `gcloud auth login`          | `aws configure`           | `az login`                 |
| Get kubeconfig            | (same as login)  | `gcloud container clusters get-credentials` | `aws eks update-kubeconfig` | `az aks get-credentials`   |
| List kube contexts        | `kubectl config get-contexts` | same                 | same                      | same                       |
| Switch context            | `kubectl config use-context` | same                 | same                      | same                       |
| List namespaces           | `kubectl get namespaces` | same                 | same                      | same                       |
| Set default namespace     | `kubectl config set-context --current --namespace=<ns>` | same | same              | same                       |
| Use k9s                   | `k9s -n <namespace>` | same                 | same                      | same                       |

---

# **Summary**

No matter the cloud, these steps are:
**Authenticate → Get kubeconfig → List/Choose context → Work in a namespace → Use kubectl or k9s.**

Learn the cloud’s login and kubeconfig-fetch commands; nearly everything else (contexts, namespaces, `kubectl`, `k9s`) is **portably identical across all clouds**!
