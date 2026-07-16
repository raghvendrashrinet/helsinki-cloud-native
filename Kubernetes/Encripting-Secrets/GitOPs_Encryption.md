## GitOps secret Implementation
### 1. Argo CD Implementation (Using Argo CD Vault Plugin)
Unlike Flux, Argo CD requires a plugin (such as the argocd-vault-plugin) to manage SOPS decryption, as it doesn't support it natively out of the box.

##### Step 1: Define the Age Key inside the Cluster
Create a secret containing your private key in the namespace where Argo CD is running:
```
kubectl create secret generic argocd-sops-age \
  --namespace=argocd \
  --from-file=key.txt=./key.txt
```
##### Step 2: Configure the Argo CD Repo Server
You need to customize the Argo CD argocd-repo-server pod so it installs the plugin and passes the environment variables. If you use the Argo CD Operator or standard manifests, you inject the secret as an environment variable into the repo-server container:
```yaml
# Inside the argocd-repo-server deployment patch
env:
  - name: SOPS_AGE_KEY_FILE
    value: /home/argocd/sops/key.txt
volumeMounts:
  - name: sops-age-volume
    mountPath: /home/argocd/sops
volumes:
  - name: sops-age-volume
    secret:
      secretName: argocd-sops-age
```
##### Step 3: Configure the Argo CD Application
When declaring your application manifest, tell Argo CD to process the manifests using the plugin:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-gitops-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/your-repo/kubernetes-manifests.git'
    targetRevision: HEAD
    path: 'apps'
    # Define the plugin usage
    plugin:
      name: argocd-vault-plugin-helm-html # Or standard avp plugin config
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: default
```
---

### 1. Flux CD Implementation (Native Support)
Flux CD has native, built-in support for SOPS. It reads the encrypted files directly from Git and decrypts them in-cluster using a private key stored in a standard Kubernetes Secret.
##### Step 1: Create the Age Secret in the Cluster
You must feed your private age key into the cluster so the Flux controller can access it. Run this command manually once:
```yaml
kubectl create secret generic sops-age \
  --namespace=flux-system \
  --from-file=age.agekey=./key.txt
```
##### Step 2: Configure the Flux Kustomization
In your Git repository where you define your Flux synchronization resources, configure your Kustomization manifest to enable decryption and point to the secret created above:
```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: secrets-deploy
  namespace: flux-system
spec:
  interval: 10m
  path: "./deployments" # Path to your manifests containing secret.enc.yaml
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  # Enable SOPS decryption
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```
Flux will automatically detect secret.enc.yaml, decrypt it using the sops-age secret, and apply the plaintext secret into the cluster without ever writing it back to Git.

