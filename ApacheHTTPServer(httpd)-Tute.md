## Apache HTTP Server (httpd) Tutorial
#### 1. How Apache Works  
 Unlike Nginx’s event-driven architecture, the traditional Apache HTTP Server uses a process-driven/thread-driven architecture. Depending on the Multi-Processing Module (MPM) configured, Apache handles requests differently:
 - `MPM Prefork:` Allocates a dedicated system process for every single incoming connection
 - `MPM Worker / Event:` Uses a hybrid approach, launching multiple processes that each manage a pool of threads to handle concurrent requests.

 *Note*:While it consumes more memory per connection than Nginx, it offers excellent isolation—if one request crashes, it won't affect the others.

#### 2. Installation & Service Management
* *Installation*: On Linux systems, Apache is packaged under different names
  - Ubuntu/Debian (Apache2): `sudo apt update && sudo apt install apache2`
  - CentOS/RHEL/Fedora (httpd): `sudo dnf install httpd`

* *Service Commands*
  Apache runs as a background service managed by `systemd`
  - *Start:* `
    ```
       # In Redhat
        sudo systemctl start httpd
       # In Ubuntu
         sudo systemctl start apache2
    ```
  - *Stop:* `sudo systemctl stop httpd `
  - *Reload* (Apply changes smoothly without dropping connections):
  -    `sudo systemctl reload httpd`
---
#### 3. Configuration Files & Request Call Flow
  The Main Configuration File:
  - CentOS/RHEL: `/etc/httpd/conf/httpd.conf`
  - Ubuntu/Debian: `/etc/apache2/apache2.conf`

Apache pulls in modular configuration files using Include or IncludeOptional directives, typically targeting directories like `/etc/httpd/conf.d/` or `/etc/apache2/sites-enabled/`.

---

####  ** The Call Flow (How a Request is Processed) **
```
 [ User Request ]
       │
       ▼
 1. Main Context (httpd.conf) ──► Global settings (ServerRoot, Timeout, MPM settings)
       │
       ▼
 2. VirtualHost Block (<VirtualHost *:80>) ──► Matches domain (ServerName) and port
       │
       ▼
 3. Directory / Location Blocks (<Directory> / <Location>) ──► Sets filesystem permissions or URL rules
```

#### 4. How to Analyze Logs
Apache keeps track of everything inside its log directory
- `/var/log/httpd/` on RHEL
- `/var/log/apache2/` on ubuntu

**Access Log (access_log or access.log)**
- Tracks every request made to the server.
Example entry:
```
192.168.1.5 - - [23/Jun/2026:11:20:00 +0000] "GET /index.html HTTP/1.1" 200 3426
```
Monitoring : : Monitor HTTP status codes for trends. Use 
 `tail -f /var/log/httpd/access_log` to stream incoming traffic in real-time.
**Error Log (error_log or error.log)**
`tail -n 50 /var/log/httpd/error_log`

#### 5. Troubleshooting Day-to-Day Problems

**Step 0** : Test the Syntax First
Before restarting or reloading Apache after modifying config files, always run:
`sudo apachectl configtest`  (or `sudo apache2ctl configtest` on Ubuntu)  
This checks your configuration syntax and reports exact lines containing errors or typos.

---

#### APACHE AS A LOAD BALANCER  
Apache can act both as a standalone Web Server (serving flat HTML/assets out of a directory) or as a dedicated Load Balancer sitting in front of application pools  
To achieve load balancing, Apache utilizes its` mod_proxy` and `mod_proxy_balancer` modules.

The Load Balancer Configuration :  
 you define a proxy balancing cluster` (balancer://)` and direct traffic to it via `ProxyPass`:

 ```
# Ensure mod_proxy modules are enabled
<Proxy balancer://my_backend_servers>
    # Define backend cluster members
    BalancerMember http://serv11:8089
    BalancerMember http://serv2:8089
    BalancerMember http://serv3:8089

    # Use round-robin scheduling method
    ProxySet lbmethod=byrequests
</Proxy>

<VirtualHost *:80>
    ServerName _
    
    # Route all traffic to the balancer cluster
    ProxyPass / balancer://my_backend_servers/
    ProxyPassReverse / balancer://my_backend_servers/

    # Recommended headers for passing client data safely downstream
    ProxyPreserveHost On
    RequestHeader set X-Real-IP "%{REMOTE_ADDR}s"
</VirtualHost>
```
##### 2. Standard Web Server Configuration (For comparison)
For a standard web server hosting a static site, you don't declare any proxy clusters. Instead, you map a network domain directly onto a local storage folder:

```
<VirtualHost *:80>
    ServerName example.com
    
    # Points directly to the local folder holding index.html
    DocumentRoot /var/www/html

    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```


---

### 3. Path Mapping Configuration (Routing Sub-directories)
If you want to route specific URL paths to completely separate local folders on your server, use the `Alias` directive. This keeps configurations modular without needing multiple domains.
file : `sudo vi /etc/httpd/conf.d/welcome.conf` since this welcome.conf is default , if you have other web site then other name
- eg example.com file : `sudo vi /etc/httpd/conf.d/example.com.conf`

```apache
<VirtualHost *:80>
    ServerName example.com
    
    # Default root folder for [example.com/](https://example.com/)
    DocumentRoot /var/www/html

    # Map [example.com/news](https://example.com/news) to the /new folder
    Alias /news /var/www/new
    <Directory /var/www/new>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # Map [example.com/sports](https://example.com/sports) to the sports/ folder
    Alias /sports /var/www/sports
    <Directory /var/www/sports>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

---

#### Hosting a web site
If you are hosting a full, standalone website for example.com, you will isolate it completely into its own virtual host file rather than leaving it in a generic default file.
example.com
##### 1. Create the Configuration File
`sudo vi /etc/httpd/conf.d/example.com.conf`

##### 2. Paste the Full Configuration
his maps the main domain to its own directory and cleanly attaches your /news and /sports sub-directories:
```
<VirtualHost *:80>
    # 1. Server Identity
    ServerName example.com
    ServerAlias www.example.com

    # 2. Main Site Document Root
    DocumentRoot /var/www/html

    # 3. Main Site Directory Permissions
    <Directory /var/www/html>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # 4. Path Mappings (Routing Sub-directories)
    # Maps example.com/news to /var/www/new
    Alias /news /var/www/new
    <Directory /var/www/new>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # Maps example.com/sports to /var/www/sports
    Alias /sports /var/www/sports
    <Directory /var/www/sports>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    # 5. Dedicated Logs for example.com
    ErrorLog /var/log/httpd/example_error.log
    CustomLog /var/log/httpd/example_access.log combined
</VirtualHost>
```
##### 3. Apply the Changes Safely
a) Fix File Permissions: Make sure Apache owns and can read all three directories:
```
 sudo chown -R apache:apache /var/www/html /var/www/new /var/www/sports
 sudo chmod -R 755 /var/www/html /var/www/new /var/www/sports
```
b) Test your syntax:
```
 sudo apachectl configtest
```
c) Reload the Service: If the test returns Syntax OK, activate the configuration:
```
sudo systemctl reload httpd
```
