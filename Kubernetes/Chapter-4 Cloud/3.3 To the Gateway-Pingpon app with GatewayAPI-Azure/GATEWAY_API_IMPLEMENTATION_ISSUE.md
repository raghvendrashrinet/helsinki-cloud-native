# Gateway API Implementation Issue - Status Report

## Project Status: PARKED ⏸️
**Date**: 2026-08-08  
**Issue**: Azure ALB Gateway API Controller not wiring up backends to Kubernetes services

---

## What Works ✅

1. **Kubernetes Deployments**: Both `logout` and `pingpong` apps deployed successfully
2. **Services**: `logoutput-svc` and `pingpong-svc` created and endpoints healthy
3. **HTTPRoute**: Route resource created and marked as "Programmed: True" 
4. **Gateway**: Gateway resource created and connected to ALB (status: Programmed)
5. **LoadBalancer Service Workaround**: Apps accessible via LoadBalancer service
   - Public IP: `20.237.96.234`
   - Access: `curl http://20.237.96.234/`
   - Status: ✅ **WORKING**

---

## What Doesn't Work ❌

1. **Azure ALB Gateway API Integration**: Traffic not routing from ALB to Kubernetes services
2. **Backend Pool Creation**: No backends auto-created in ALB despite HTTPRoute being "Programmed"
3. **Gateway API Controller**: Controller not processing Gateway/HTTPRoute resources
   - Controller logs show only Helm release processing
   - Not watching Gateway API resources

---

## Root Cause Analysis

### Issue Summary
The **ALB controller** shows HTTPRoute as "Programmed" but is NOT actually configuring the Azure ALB with backend pools or routing rules.

### Evidence
1. HTTPRoute Status:
   ```
   Reason: Programmed
   Status: True
   Message: "Application Gateway for Containers resource has been successfully updated"
   ```

2. ALB Status Check:
   ```
   - No backends registered in ALB
   - No routing rules configured
   - Frontend exists but not wired to any backends
   ```

3. Controller Logs:
   - Only processing Helm releases
   - Not processing Gateway/HTTPRoute/GRPCRoute resources
   - No errors - simply ignoring Gateway API resources

### Probable Causes
1. **ALB Controller misconfiguration** - Not configured to watch Gateway API resources
2. **RBAC permissions missing** - Controller lacks permissions to manage Gateway resources
3. **Feature not fully enabled** - Gateway API for ALB might need additional AKS configuration
4. **Preview feature** - Azure ALB Gateway API might still be in limited preview for this region/AKS version

---

## Current Deployment Architecture

### Working Path (LoadBalancer)
```
Browser → Internet → AKS LoadBalancer Service (20.237.96.234:80)
                     ↓
                  Kubernetes Service (logoutput-svc)
                     ↓
                  Pod (logout app port 5000)
```

### Intended Path (Gateway API - Not Working)
```
Browser → Internet → Azure ALB (20.241.184.191 / dwekbqaxhggafkhf.fz10.alb.azure.com)
                     ↓
                  ALB Backend Pool (MISSING!)
                     ↓
                  Kubernetes Service (logoutput-svc)
                     ↓
                  Pod (logout app port 5000)
```

---

## Files Involved

| File | Purpose | Status |
|------|---------|--------|
| `Gateway.yaml` | ALB Gateway definition | ✅ Applied, Programmed |
| `GatewayClass.yaml` | ALB Gateway Class | ✅ Applied |
| `manifest/httproute.yaml` | HTTP routing rules | ✅ Applied, Programmed |
| `manifest/deployment_logout.yaml` | Logout app deployment | ✅ Running |
| `manifest/deployment_pong.yaml` | Pingpong app deployment | ✅ Running |
| `manifest/service_logout.yaml` | Logout service | ✅ Running, endpoints healthy |
| `manifest/service_pong.yaml` | Pingpong service | ✅ Running, endpoints healthy |

---

## Azure Resources

### Created Successfully
- **ALB**: `my-agc` in `rg1`
- **Frontend**: `my-frontend` with FQDN `dwekbqaxhggafkhf.fz10.alb.azure.com`
- **Public IP**: `20.241.184.191`
- **Association**: ALB connected to AKS subnet `alb-subnet` (10.225.0.0/24)

### Missing/Not Configured
- **Backend Pools**: Not auto-created by controller
- **Backend Addresses**: No Kubernetes service endpoints registered
- **Routing Rules**: No listener/routing configuration

---

## Troubleshooting Steps Attempted

### ✅ Completed
1. Verified deployments and services running
2. Verified endpoints healthy and discoverable
3. Confirmed HTTPRoute syntax correct and references valid services
4. Confirmed Gateway annotation correct with ALB resource ID
5. Tested apps internally with `kubectl port-forward` ✅ Working
6. Tested apps with LoadBalancer service ✅ Working
7. Checked network policies - none blocking traffic ✅ Clear
8. Verified NSG rules - added ALB subnet to AKS NSG rules ✅ Done

### Still Need to Debug
1. ALB Controller RBAC permissions
2. Controller configuration/flags - what resources it watches
3. AKS feature flag status for Gateway API
4. ALB Controller CRD permissions
5. Detailed controller logs during Gateway resource processing

---

## Next Steps to Fix (When Resuming)

### Step 1: Verify RBAC
```powershell
kubectl get clusterrole | findstr alb
kubectl describe clusterrole alb-controller
kubectl describe clusterrolebinding alb-controller
```

### Step 2: Check Controller Configuration
```powershell
kubectl get deployment -n kube-system alb-controller -o yaml
# Look for --watch, --namespace, or resource filters
```

### Step 3: Verify CRDs
```powershell
kubectl get crd | findstr gateway
kubectl describe crd gateways.gateway.networking.k8s.io
```

### Step 4: Check Azure Feature Flag
```powershell
az feature list --query "[?name=='Microsoft.ContainerService/EnableALBPreview']"
```

### Step 5: Restart Controller
```powershell
kubectl rollout restart deployment/alb-controller -n kube-system
kubectl rollout status deployment/alb-controller -n kube-system
```

### Step 6: Monitor Controller Logs
```powershell
kubectl logs -n kube-system deployment/alb-controller -f
# Watch for gateway/route/backend processing
```

### Step 7: If Still Failing
- Contact Azure support about Gateway API + ALB integration
- Check AKS version compatibility
- Verify region support for this feature

---

## Workaround (Current Solution)

### Use LoadBalancer Service Instead
```yaml
apiVersion: v1
kind: Service
metadata:
  name: logout-lb
spec:
  type: LoadBalancer
  selector:
    app: logout
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```

**Current Public IP**: `20.237.96.234`

This works perfectly for now while Gateway API integration is debugged.

---

## Resources for Reference

- [Azure ALB for Kubernetes Docs](https://learn.microsoft.com/en-us/azure/application-gateway/for-containers/overview)
- [Gateway API Spec](https://gateway-api.sigs.k8s.io/)
- [ALB Controller GitHub](https://github.com/Azure/alb-controller)
- AKS Cluster: `myAKSCluster` in `rg1`
- ALB: `my-agc` in `rg1`

---

## Key Findings Summary

✅ **Apps are healthy and working**  
✅ **Kubernetes networking is correct**  
✅ **Azure ALB infrastructure exists**  
❌ **ALB Controller not wiring Kubernetes → ALB**  
✅ **Workaround using LoadBalancer works**

The infrastructure is set up correctly, but the controller integration has a configuration or permission issue preventing automatic backend pool creation.

---

**Last Updated**: 2026-08-08 17:10 UTC
