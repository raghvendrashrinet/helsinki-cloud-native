
#### The General Strategy
- Store the Private Key as a Secret Variable: You store the contents of your key.txt (the age private key) as a secured environment variable/secret in your CI/CD platform (e.g., GitHub Secrets).
- Inject the Key at Runtime: During the pipeline run, the runner writes this secret key to a temporary file.
- Decrypt and Apply on the Fly: You use sops to decrypt the file and pipe it directly to kubectl apply without writing the unencrypted secret to the disk.
- Implementation Example: GitHub Actions
- 
Here is a practical workflow showing how this is configured in GitHub Actions:

#### Implementation Example: GitHub Actions
1. Add your Age Key to GitHub Secrets
First, copy the content of your private key file (key.txt).
Go to your ` GitHub Repository -> Settings -> Secrets and variables -> Actions and create a new repository secret:`
```
Name: SOPS_AGE_KEY

Value: (Paste the entire contents of your key.txt file)
```
2. Configure the Workflow File (.github/workflows/deploy.yml)
You can use the following workflow step to safely decrypt and apply the secret:
```yaml
name: Deploy to Kubernetes

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # 1. Install SOPS (if not already cached or pre-installed)
      - name: Install SOPS
        run: |
          WRK_DIR=$(pwd)
          curl -LO https://github.com/getsops/sops/releases/download/v3.8.1/sops-v3.8.1.linux.amd64
          mv sops-v3.8.1.linux.amd64 /usr/local/bin/sops
          chmod +x /usr/local/bin/sops

      # 2. Configure Kubectl (Assumes you have a step setting up your kubeconfig)
      - name: Set up Kubeconfig
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBECONFIG }}

      # 3. Decrypt and Apply on the fly
      - name: Decrypt and Apply Secret
        env:
          # We write the GitHub secret containing the age key to a temporary file path
          SOPS_AGE_KEY: ${{ secrets.SOPS_AGE_KEY }}
        run: |
          # Write the environment variable to a temporary file
          echo "$SOPS_AGE_KEY" > ./key.txt
          
          # Set the SOPS environment variable pointing to our temp key file
          export SOPS_AGE_KEY_FILE=$(pwd)/key.txt
          
          # Decrypt and pipe directly into Kubernetes without saving to disk
          sops --decrypt secret.enc.yaml | kubectl apply -f -
          
          # Clean up the key file immediately
          rm ./key.txt
```
### Note : In GitOPS Implemetation is diffrent , Check GitOps file in this repo
