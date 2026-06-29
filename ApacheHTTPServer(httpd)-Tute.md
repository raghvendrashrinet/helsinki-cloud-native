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
  - Ubuntu/Debian: `/etc/apache2/apache2.conf`  and ports.conf has the Listen port and host ip
```
 Listen 80
  # It binds to all network interfaces,Instead of only listening to requests coming from your local machine (127.0.0.1), Apache will now bind to 0.0.0.0 (for IPv4) and ::

 Listen 127.0.0.1:8080
  # if cohosted with Reverse proxy,ha proxy on same server ,Nginx acts as the strict "front gate."

```
#### How Apache2 Boots Up (Execution Order

---

####  ** The Call Flow (How a Request is Processed) **
```text
[ Start Apache ]
       │
       ▼
┌──────────────────────────────┐
│  /etc/apache2/apache2.conf   │  <-- (1. Master rules loaded first)
│  (Global Settings)           │
│                              │
│  IncludeOptional... ─────────┼──┐
└──────────────────────────────┘  │
                                  ▼  (2. Jumps to the folder)
                     ┌──────────────────────────────┐
                     │ /etc/apache2/sites-enabled/  │
                     │                              │
                     │  ├── 000-default.conf        │ <-- (3. Read 1st: Fallback)
                     │  └── your-website.conf       │ <-- (4. Read 2nd: Custom site)
                     └──────────────────────────────┘

```
##### Sequence of events
Step 1. The Master Blueprint `/etc/apache2/apache2.conf or httpd.conf`
- When you turn on Apache, first. It reads only one file: /etc/apache2/apache2.conf.
- This master file contains global server settings, such as
    * Security settings: Who is allowed to look at your server folders?
      ```
      <Directory /var/www/>
      Options Indexes FollowSymLinks
      AllowOverride None
      Require all granted #Require all granted line allows public users to look at files inside /var/www/. If it says         Require all denied
     </Directory>
     ```
     

    * Performance settings: How much memory can Apache use?  
        Performance and memory limits are handled by a system called Multi-Processing Modules (MPM)
    * Log settings: Where should Apache save error reports?
      ```
       ErrorLog ${APACHE_LOG_DIR}/error.log
       LogLevel warn
      ```
  Step 2. How it Connects to the Website Files?
   how does it ever see our website files in sites-enabled?
   ```
    # Near the bottom of /etc/apache2/apache2.conf
    IncludeOptional sites-enabled/*.conf
   ```
   Step 3. Apache reaches the bottom of apache2.conf and sees the IncludeOptional `sites-enabled/*.conf `instruction.
   Step 4.  Apache jumps into the sites-enabled folder.
    It sorts the files alphabetically and reads them:
     1. Reads 000-default.conf first (becomes the fallback).
     2. Reads your-website.conf next
    
    Step 5: When Web Traffic Arrives (The Decision)
     Once the server is running, the choice of which file to use depends entirely on what the user types into their    browser:  
  * **Scenario A: The user types example.com**  
        1. The request hits Apache.Apache checks its memory list for an exact match for example.com.It finds the exact match inside `your-website.conf`.  
        2. Apache completely ignores 000-default.conf and serves the files from your custom project folder. 
      
  * **Scenario B: The user types your server's raw IP address (e.g., 192.168.1.50)**
        1. The request hits apache,It finds no exact match.
        2. Apache serves the default placeholder page from 000-default.conf
       
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
