## Encrypting secrets
- Since anyone can reverse the base64 version, we can't save that to version control
- Since we want to store our configuration in long-term storage, we'll need to encrypt the value
- multiple solutions for secret management depending on the platform. Azure keyVauly,AWS Secret Manager.

####   The Solution: The Cast of Characters
To solve this, the chapter introduces two tools that work together:
1. **age (The Lock & Key Maker)**: This tool creates a unique, incredibly secure padlock (the Public Key) and a matching physical key (the Private/Secret Key).
 ```bash
   #Install in windows
    winget install --id FiloSottile.age     or choco install age.portable
  ```

2. **SOPS (The Smart Assistant)**: This tool takes your Kubernetes document, finds the sensitive parts, and uses your age padlock to lock them up.
```
# Install Scoop if you haven't already
iwr -useb get.scoop.sh | iex

# Install SOPS
scoop install sops
```
###### Step 1: You create your lock and key
First, you run a command to generate your keys.  
- You get a Public Key (which you can show to anyone). Think of this as an open padlock.
- You get a Secret Key (which you must hide). This is the physical key to open that padlock.

###### Step 2: You hand the padlock to SOPS to encrypt the file
- You tell SOPS: "Here is my public padlock. Please lock up the sensitive information in this configuration file."

- SOPS is smart. Instead of locking up the entire file, it only locks up the actual secret values (like your API keys), leaving the rest of the file structure (like the name of the file) visible.

###### Ex : The Scenario
Imagine you have a Kubernetes web application that needs a database password to run.  
The Secret Password: `super-secret-db-pass`

> The Goal: Store your Kubernetes configuration file on GitHub so your team can use it, but without exposing that database password to the public.

**Step 1:** Create your Lock and Key
First, you need to generate a key pair. We use a tool called age to do this.

🔑 Analogy: Think of this like buying a padlock and physical key set from a hardware store. The padlock (Public Key) can be handed to anyone, but you keep the physical key (Private Key) hidden safely in your pocket.

In your terminal, you run a command to generate these keys:

```Bash
age-keygen -o key.txt
# This creates a file called key.txt containing:
```
- Your Lock (Public Key): `age17mgq9ygh23q0cr00mjn0dfn8msak0apdy0ymjv5k50qzy75zmfkqzjdam4`
- Your Key (Private Key): Keep this secret!

**Step 2:** Write the "Before" File (Plaintext)
Next, you write your normal Kubernetes Secret file (secret.yaml). Kubernetes requires sensitive values to be encoded in Base64 (which, remember, is just a weak disguise, not real encryption).

super-secret-db-pass encoded in Base64 is` c3VwZXItc2VjcmV0LWRiLXBhc3M=.`

```YAML
# secret.yaml (UNSAFE FOR GITHUB)
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
data:
  DB_PASSWORD: c3VwZXItc2VjcmV0LWRiLXBhc3M=
```
**Step 3:** Lock the Secret (The "After" File)
Now, we use SOPS to encrypt only the sensitive data inside our file. We tell SOPS to use our age public padlock:

```Bash
sops --encrypt --age age17mgq9ygh23q0cr00mjn0dfn8msak0apdy0ymjv5k50qzy75zmfkqzjdam4 --encrypted-regex '^(data)$' secret.yaml > secret.enc.yaml
```
> 🧠 Why SOPS is smart: It reads the rules we gave it (--encrypted-regex '^(data)$') and realizes: "Ah, I only need to lock up the things inside the data section. I will leave the metadata alone."

Your new file, secret.enc.yaml, now looks like this:

```YAML
# secret.enc.yaml (SAFE FOR GITHUB)
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
data:
  DB_PASSWORD: ENC[AES256_GCM,data:gK3x8d...,iv:Lk29...] # <-- Jumbled Gibberish!
sops:
  age:
    - recipient: age17mgq9ygh23q0cr00mjn0dfn8msak0apdy0ymjv5k50qzy75zmfkqzjdam4
      enc: |
        -----BEGIN AGE ENCRYPTED FILE-----
        ...
        -----END AGE ENCRYPTED FILE-----
```
You can now safely upload secret.enc.yaml to GitHub! Anyone looking at your repository can see that a secret named db-credentials exists, but they have absolutely no way of knowing what the password is.

**Step 4**: Unlock "On the Fly"
When your automated deployment server (like GitHub Actions) or your terminal wants to send this secret to Kubernetes, you use your private key to unlock it and feed it directly to the cluster.

First, point SOPS to your private key file:

```ash
export SOPS_AGE_KEY_FILE=$(pwd)/key.txt
```
Then, run the unlock-and-apply command:

```Bash
sops --decrypt secret.enc.yaml | kubectl apply -f -
```
> 🔄 How the "Pipe" (|) Works:

sops --decrypt reads the locked file, grabs your private key, decrypts the password back into plain text, and spits it out.

The pipe | catches that decrypted text in mid-air and hands it straight to kubectl apply (the Kubernetes brain).

Crucial Safety: The unencrypted password never gets saved onto your hard drive. It only exists in your computer's temporary memory for a fraction of a second while passing to Kubernetes.


---
# Secret Management in Real-World Production Systems

In a production environment, hardcoding passwords or storing plain Base64-encoded Kubernetes Secret files in Git is a major security violation. Instead, enterprise systems manage secrets using one of two primary architectural philosophies.

---

## Philosophy 1: GitOps-Driven (The SOPS / SealedSecrets Way)

This matches the GitOps methodology where the Git repository acts as the single source of truth for the entire cluster's state. Tools like ArgoCD or Flux are used to continuously deploy everything automatically from GitHub.

### How it Works:
1. **Cloud KMS as the Master Lock:** Instead of using local age keys, teams use a managed Cloud Key Management Service (KMS)—such as **[Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-portal)**, AWS KMS, or Google Cloud Secret Manager—to act as the master key.
2. **Local Encryption:** Developers write standard Kubernetes manifests but encrypt them locally with **[SOPS](https://github.com/getsops/sops)** using the Cloud KMS key. The encrypted file (`secret.enc.yaml`) is completely safe to commit to Git.
3. **Just-in-Time Decryption:** A GitOps controller running inside the Kubernetes cluster is granted IAM permissions to access the Cloud KMS. It decrypts the file on the fly and applies it directly to the cluster's memory as a native Kubernetes Secret.

---

## Philosophy 2: Zero-K8s-Secret Storage (The CSI Driver / Operator Way)

Highly regulated environments (such as banking, healthcare, and fintech) prefer this approach because they **do not want actual secrets stored inside the Kubernetes database (`etcd`) at all**. 

Instead of storing encrypted secrets in Git, they store the raw secrets directly in an external managed vault and pull them dynamically.

Two major tools dominate this space:

### A. Secrets Store CSI Driver (Mounting as Volumes)
* **How it works:** When a Pod starts, the **[Secrets Store CSI Driver](https://kubernetes-sigs.github.io/secrets-store-csi-driver/)** logs into your managed vault (like Azure Key Vault), grabs the secret, and mounts it directly as an in-memory file inside the running container.
* **Production Advantage:** The secret only exists in temporary memory while the container is active. It never gets written to the server's hard drive or saved in the cluster's database.

### B. External Secrets Operator (ESO)
* **How it works:** A background controller running in Kubernetes continuously watches your managed vault. If you update a password in Azure Key Vault, the operator automatically detects the change, pulls the new value, and updates the native Kubernetes Secret in your cluster.
* **Production Advantage:** This decouples your application configuration from the cloud provider. If the external vault experiences temporary downtime, your application doesn't crash because the last synced secret is still cached safely in the cluster.

---

## Summary Comparison

| Feature | GitOps / SOPS | CSI Driver / External Secrets |
| :--- | :--- | :--- |
| **Where Secret is Stored** | Encrypted in Git | Inside a Managed Vault (Azure/AWS/HashiCorp) |
| **Setup Complexity** | **Low** (Simple CLI tools) | **Medium** (Requires cluster operators & cloud permissions) |
| **Best Suited For** | Startups, independent projects, and developer-centric workflows | Highly secure, regulated enterprise systems and large-scale cloud applications |


---
#### In Azure :  Azure Key Vault is very straightforward. You can do this either through the Azure Portal (Web UI) or via the Azure CLI (Command Line). 



Storing Secrets in Azure Key Vault
Azure Key Vault allows you to securely store and control access to tokens, passwords, certificates, and API keys.

**Method 1:** Using the Azure Portal (Web Interface)
- Navigate to your Key Vault:

- Sign in to the Azure Portal.

- Search for Key Vaults in the top search bar and select your Key Vault resource.

- Open the Secrets Menu:

- In the left-hand sidebar under the Objects section, click on Secrets.

- Generate/Import the Secret:

- Click the + Generate/Import button in the top menu.

- Upload options: Set this to Manual.

- Name: Enter a unique identifier for your secret (e.g., pixabay-apikey).

- Secret value: Paste your sensitive API key or password.

- Optional: Define activation or expiration dates if needed.

- Save:

- Click Create at the bottom of the form.

**Method 2:** Using the Azure CLI (Command Line)
If you prefer automating your infrastructure or working in a terminal, you can set secrets directly using the command line.

Log in to Azure:

```Bash
az login
```
Save the Secret:
Use the az keyvault secret set command to upload your secret value:

```Bash
az keyvault secret set \
  --vault-name "<your-keyvault-name>" \
  --name "pixabay-apikey" \
  --value "your-actual-api-key-here"
```
Connecting Azure Key Vault with SOPS
If you want to use Azure as the secure backend for your SOPS configuration files instead of using local age keys, you can encrypt your local YAML files directly using an asymmetric key stored in Azure Key Vault:

```Bash
sops --encrypt \
  --azure-kv https://<your-vault-name>.vault.azure.net/keys/<your-key-name>/<key-version> \
  --encrypted-regex '^(data)$' \
  secret.yaml > secret.enc.yaml
```

---
###### To reference a secret stored in Azure Key Vault inside your Kubernetes manifest files, the standard and most secure way is to use the Secrets Store CSI Driver along with the Azure Key Vault Provider.

The Workflow Overview
```
 [ Azure Key Vault ]  ---(Pulls Secret)---> [ SecretProviderClass ] 
                                                    │
                                             (Syncs/Mounts)
                                                    ▼
                                            [ Your Pod Manifest ]
```

**Step 1:** Define the Bridge (SecretProviderClass)
First, you create a special Kubernetes configuration file that tells the CSI Driver exactly which Key Vault to look at and which secret to pull.
```Yaml
# secret-provider.yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-kv-provider
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"         # Or "true" depending on how your cluster authenticates to Azure
    keyvaultName: "your-keyvault-name" # The name of your Azure Key Vault
    objects:  |
      array:
        - |
          objectName: pixabay-apikey # The name of the secret inside Azure Key Vault
          objectType: secret        # It's stored as a secret
          objectVersion: ""         # Leave blank to pull the latest version
    tenantId: "your-azure-tenant-id"
```

**Step 2:** Reference it in your Pod / Deployment Manifest
Now, in your deployment.yaml manifest, you mount this secret-provider just like a USB flash drive (a volume) and tell your container to read from it.
```Yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: imageapi-deployment
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: imageapi
    spec:
      containers:
        - name: imageagain
          image: jakousa/dwk-app4:b7fc18de2376da80ff0cfc72cf581a9f94d10e64
          # 2. Inside the container, look for the API key in this directory
          volumeMounts:
            - name: secrets-store-inline
              mountPath: "/mnt/secrets-store"
              readOnly: true
      # 1. Mount the SecretProviderClass we created in Step 1 as a volume
      volumes:
        - name: secrets-store-inline
          csi:
            driver: secrets-store.csi.k8s.io
            readOnly: true
            volumeAttributes:
              secretProviderClass: "azure-kv-provider"
```
How this works in practice:
When Kubernetes starts your container, the CSI driver logs into your Azure Key Vault, grabs the pixabay-apikey, and writes it to a temporary file located at /mnt/secrets-store/pixabay-apikey.

Your application code simply reads the contents of that file to get the password.

Security Bonus: The actual secret is never saved to your Git repository, and it never gets written to your node's disk in plaintext.
