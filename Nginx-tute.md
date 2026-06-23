## 1. How Nginx Works
Unlike traditional web servers (like Apache) that create a new process or thread for every single user request, Nginx uses an asynchronous, event-driven, non-blocking architecture.

The Analogy: Think of a fast-food restaurant. Instead of one waiter sitting at a table with a customer until they finish eating (thread-per-request), Nginx has a single cashier taking orders rapidly, sending them to the kitchen, and moving immediately to the next customer (event-driven).

This allows Nginx to handle tens of thousands of concurrent connections using very little memory.

### 2. Installation & Service Management
* **Installation**  
On Linux systems, use the built-in package manager:
 > Ubuntu/Debian: sudo apt update && sudo apt install nginx

 > CentOS/RHEL: sudo dnf install nginx

* **Service Commands**  
  Nginx runs as a background service managed by systemd. Use these commands to control it:  
 * Start: `sudo systemctl start nginx`
 * Stop: `sudo systemctl stop nginx`
 * Restart (Hard stop & start): `sudo systemctl restart nginx`
 * Reload (Apply changes without dropping connections): `sudo systemctl reload nginx`
 * Check Status: `sudo systemctl status nginx`

### 3. Configuration Files & Request Call Flow
The Main Configuration File , The main entry point for Nginx is located at:  
   
    ` /etc/nginx/nginx.conf `  

  Inside this file, Nginx uses include directives to pull in modular configuration files, typically located in  
    ` /etc/nginx/conf.d/ ` or  `/etc/nginx/sites-enabled/.`  

**The Call Flow (How a Request is Processed)**  
When a user types a URL (e.g., http://example.com/images/logo.png), Nginx processes the request sequentially through a top-down hierarchy:  
```
   [ User Request ]
       │
       ▼
 1. Main Context (nginx.conf) ──► Global settings (worker processes, logging paths)
       │
       ▼
 2. HTTP Context (http { ... }) ──► Defines general web behavior (Gzip, SSL settings)
       │
       ▼
 3. Server Block (server { ... }) ──► Matches the domain name (server_name) and port (listen)
       │
       ▼
 4. Location Block (location { ... }) ──► Matches the specific URI path (/images/) to find the file

```

### 4. How to Analyze Logs  
Nginx keeps track of everything in two default files located in   
 `/var/log/nginx/:  `

**Access Log (access.log)**  
- Tracks every request made to the server.
- What it looks like:
   `192.168.1.5 - - [23/Jun/2026:11:20:00] "GET /index.html HTTP/1.1" 200 3426`  

How to analyze it:   
- Look at the HTTP Status Code (e.g., 200 means success, 404 means not found).  
- Use `tail -f /var/log/nginx/access.log` to watch incoming traffic in real-time.

**Error Log (error.log)**  
Tracks server glitches, configuration mistakes, or application connection crashes.  

How to analyze it: 
If something isn't loading, check this file first.
- Use `tail -n 50 /var/log/nginx/error.log` to see the last 50 errors.


### 5. Troubleshooting Day-to-Day Problems  
When Nginx isn't behaving, use this checklist to diagnose and fix the issue quickly:  
- Step 0: Test the Syntax First   
   Before restarting Nginx after editing a config file, always run:  

  ` sudo nginx -t `
  This tells you exactly which line has a typo or a missing semicolon.

### Common Error Codes & Fixes  

| Error Code | Meaning | Common Cause & Fix |
| :--- | :--- | :--- |
| **502 Bad Gateway** | Nginx is working, but the backend app behind it is down. | **Fix:** Check if your backend app service (Node, PHP-FPM, Python) is running: `sudo systemctl status <service>` |
| **504 Gateway Timeout** | The backend application took too long to respond. | **Fix:** Increase timeout limits (`proxy_read_timeout`) in your Nginx server block. |
| **403 Forbidden** | Nginx does not have permission to access the requested files. | **Fix:** Fix file permissions: `sudo chmod -R 755 /var/www/html` and ensure the `nginx` user owns them. |
| **404 Not Found** | The file or path requested does not exist where Nginx is looking. | **Fix:** Double-check your `root` or `alias` directive paths inside the location block. |
| **Configuration Error** | Nginx fails to start or reload. | **Fix:** Run `sudo nginx -t` to find the exact line with the syntax error or missing semicolon. |

### Nginx Service Control Cheat Sheet 

| Command | Action | When to Use |
| :--- | :--- | :--- |
| `sudo nginx -t` | **Test Configuration** | Run this **every time** before reloading or restarting to catch syntax errors. |
| `sudo systemctl reload nginx` | **Graceful Reload** | Applies configuration changes safely *without* dropping active user connections. |
| `sudo systemctl restart nginx` | **Hard Restart** | Fully stops and starts the service. Use this if a reload doesn't apply your changes. |
| `sudo systemctl status nginx` | **Check Status** | Tells you if Nginx is active (running) or failed, and shows recent error lines. |
| `tail -f /var/log/nginx/error.log` | **Live Error Stream** | Keeps the terminal open to watch errors happen in real-time while you debug. |

---
## NGINX LOAD BALANCER  
Nginx Server and Nginx LB (Load Balancer) are not two different pieces of software. They are the exact same program, but they are configured to do two entirely different jobs.  
1. Nginx as a Web Server  
When used as a standard web server, Nginx is responsible for hosting and delivering a website's files directly to the user.

2. Nginx as a Load Balancer (LB)  
When used as a Load Balancer, Nginx acts as a traffic cop sitting in front of multiple backend application servers. It does not host the website files itself.

**What it does:**  
When a user request comes in, Nginx evaluates which backend server (App Server 1, App Server 2, etc.) is the least busy and forwards the request to it. It then takes the response from that backend server and passes it back to the user.

#### configuration-wise, they both are completely different.  
When you configure Nginx as a Web Server, you tell it where to find files on the disk. When you configure it as a Load Balancer (LBR), you tell it the IP addresses of your backend App Servers.  

1. **The Load Balancer Configuration**  
To configure Nginx as a Load Balancer, you must define an upstream block (a group of backend servers) and use proxy_pass inside the `location block` to route the traffic to that group.  

According to your task instructions, you need to update the main configuration file` (/etc/nginx/nginx.conf) inside the http { ... } context`:

```
http {
    upstream my_backend_servers {
        server serv11:8089; # Replace with actual App Server 1 details
        server serv2:8089; # Replace with actual App Server 2 details
        server serv3:8089; # Replace with actual App Server 3 details
    }

    server {
    listen       80;
    listen       [::]:80;
    server_name  _;

 
    location / {
        proxy_pass http://my_backend_servers;

        # Recommended headers for proper load balancing
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Load configuration files for the default server block.
    include /etc/nginx/default.d/*.conf;

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html; # Moved root here so errors can still find files
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html; # Moved root here so errors can still find files
    }
}
}
```

2. **Standard Web Server Configuration (For comparison)** 
For a standard web server hosting a static site, you don't use upstream or proxy_pass. Instead, you point Nginx directly to a folder path using root:
```
http {
    server {
        listen 80;
        server_name example.com;

        # Points directly to the local folder holding index.html
        root /var/www/html; 

        location / {
            try_files $uri $uri/ =404;
        }
    }
}
```
