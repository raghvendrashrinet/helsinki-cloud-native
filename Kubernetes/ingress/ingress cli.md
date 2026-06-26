##1. Host-Based Routing
Command:
```
kubectl.exe create ingress ing1 --rule=example.com/=svc1:80 --dry-run=client -o yaml
```
Verdict: Correct.

Logic: The syntax is host/path=service:port. 
By specifying example.com/, you define the host as example.com and the path as / (root).
Since a host is explicitly defined, this creates a Host-Based rule (traffic is routed based on the Host header matching example.com). 
2. Path-Based Routing
Command:
```
kubectl.exe create ingress ing1 --rule=example.com/app=svc1:80 --dry-run=client -o yaml
```
Verdict: Technically Path-Based, but includes a Host.

Logic: This defines host example.com and path /app. 
Nuance: This is not a "pure" path-based rule (which usually implies catching any host).  It is a Host-and-Path rule.  It will only work if the request header is Host: example.com AND the URL is /app. 
Pure Path-Based (No Host): If you want to route based only on the path (ignoring the domain), you must omit the host part entirely:
# Correct for pure path-based (catch-all host)
```
kubectl.exe create ingress ing1 --rule=/app=svc1:80 --dry-run=client -o yaml
```
Summary of Differences
Command	Host Rule	Path Rule	Type
example.com/	example.com	/	Host-Based (matches any path on this domain)
example.com/app	example.com	/app	Host + Path (matches specific path on specific domain)
/app	(none)	/app	Pure Path-Based (matches any domain with this path)


