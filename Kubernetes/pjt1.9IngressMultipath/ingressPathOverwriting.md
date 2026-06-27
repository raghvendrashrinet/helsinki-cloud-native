
### Target path overrighting 
##### This strips "/logout" or "/pingpong" before sending it to the app
    nginx.ingress.kubernetes.io/rewrite-target: /
```
kubectl create ingress ingress1 --rule="/pingpong=pong-app:8000" --rule="/=dep-node-port:2345"
```

---
## Target Path Overwriting (Ingress Layer vs. App Layer)
When routing traffic via sub-directories (like /news or /sports), you have two choices for handling how the backend application receives the path context.

- **Approach A**: Overwriting at the Ingress Layer (Recommended)
This method strips the path context at the cluster edge. The backend application pod doesn't need any special routing rules; it simply receives the request as if it were hitting the root (/) directory.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multipath-ingress
  annotations:
    # Captures the text after the prefix and rewrites the target path to just that text
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /news(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: news-service
            port:
              number: 80
```
Imperative CLI Command Shortcut:
```
kubectl create ingress ingress1 --rule="/pingpong=pong-app:8000" --rule="/=dep-node-port:2345"
```

#### RegEx match
##### Step 1: Ingress Matches the Regex Path
The Ingress controller looks at its rules and matches the request to your path pattern:
```yaml
path: /news(/|$)(.*)
```
- The Regex engine splits the incoming path /news/details.html into hidden variables (capture groups) based on the parentheses:
- The Prefix: /news (This is matched outside the groups)
- Group 1 (/|$): Matches the slash right after news.  
  Variable $1 = /
- Group 2 (.*): Matches everything else left over at the end of the URL.  
 Variable $2 = details.html

##### Step 2: The Rewrite Target Swaps the Value
Next, the Ingress looks at your rewrite instruction:
```
nginx.ingress.kubernetes.io/rewrite-target: /$2
```
It dynamically builds a brand-new path by substituting $2 with its captured value (details.html):
`Target path = / + $2 => /+default.html => /default.html`

**Approach B** : Overwriting at the App Layer (If Ingress Passes the Path)
If your Ingress configuration simply passes the raw path downstream without an annotation, the request will hit your application still carrying the `/news` or `/sports` prefix.

If your backend is running Apache (httpd), you must explicitly configure your app architecture to handle or strip this path internally using mod_rewrite so it doesn't return a 404 Not Found.

If your backend is running Apache (httpd), you must explicitly configure your app architecture to handle or strip this path internally using mod_rewrite so it doesn't return a 404 Not Found.

```httpd
<VirtualHost *:80>
    ServerName example.com
    DocumentRoot /var/www/html

    # Enable the rewriting engine inside Apache
    RewriteEngine On

    # Strips "/news" from the front of the incoming URL internally
    RewriteRule ^/news/(.*)$ /var/www/new/$1 [L]
    
    <Directory /var/www/new>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```
