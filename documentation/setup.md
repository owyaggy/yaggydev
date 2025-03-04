# Setting Up

### Need 3 pieces of information:

* Droplet's IP address
* Default username on server
* Default password for that username, if not using SSH keys

#### Get Droplet's IP address

* Visit [DigitalOcean Control Panel](https://cloud.digitalocean.com/)
* Copy the IP address listed for the droplet
* Default username should be `root` on Ubuntu

(Assuming already uploaded SSH keys to account and added to droplet upon creation)

### Connect

* SSH into root

```commandline
ssh root@203.0.113
```
* Respond yes when asked if you want to continue connecting
* You'll receive confirmation that the IP address has been added to the list of known hosts
* Might receive a remote host identification warning, particularly if just having destroyed a Droplet

### Create New User

```commandline
adduser owen
```
* Enter a strong password
* Fill in information as prompted (not required)

### Grant Admin Privileges

```commandline
usermod -aG sudo owen
```
* Can now type `sudo` before commands to run with superuser privileges when logged in as regular user

### Setting Up Firewall

* Check for installed UFW profiles

```commandline
ufw app list
```

* Should show OpenSSH available
* Need to allow SSH connections to make sure server can be logged into

```commandline
ufw allow OpenSSH
ufw enable
```

* Type `y` and press `ENTER` to proceed
* Check that SSH connections are allowed:

```commandline
ufw status
```

* Should show OpenSSH

### Enable External Access for Regular User

* To log into regular user with SSH key, must add copy of local public key to new user's `~/.ssh/authorized_keys` file
* Since public key is already in **root** account's `~/.ssh/authorized_keys` file on server, can copy that file and
directory structure to new user account using current session
* Copy files with correct ownership and permissions using `rsync` command
  * Will copy **root** user's `.ssh` directory, preserve permissions, modify file owners
  * Be sure to **not** include trailing slash after `.ssh`

```commandline
rsync --archive --chown=owen:owen ~/.ssh /home/owen
```

* Now open **new** terminal session (don't close original), use SSH with new username

```commandline
ssh owen@your_server_ip
```

* Should connect to server with new user account without password
* Use `sudo` when running commands that need admin privileges
* Will need regular user's password when using `sudo` for first time each session (periodically afterward)

### Disabling Password Authentication

* Once SSH keys have been configured and tested, it's a good idea to disable password authentication
* This prevents any user from signing with SSH using a password
* Connect to remote server and open `/etc/ssh/sshd_config` file with sudo privileges:

```commandline
sudo nano /etc/ssh/sshd_config
```

* Inside of file, search for `PasswordAuthentication` directive
* If it is commented out, uncomment it
* Set it to no to disable password logins:

```
PasswordAuthentication no
```

* Save and close file
* Restart SSH service to implement changes

```commandline
sudo service ssh restart
```

### Installing Nginx

* Nginx is available in Ubuntu's default repositories, so it is possible to install using `apt` packaging system
* Since this is the first interaction with `apt`, update local package index to have access to most recent package
listings
* Then install nginx:

```commandline
sudo apt udpdate
sudo apt install nginx
```

* Pres `Y` when prompted to confirm
* If prompted to restart any services, press `ENTER` to accept defaults and continue
* `apt` will install Nginx and any required dependencies to the server

### Adjusting Firewall

* The firewall needs to be configured to allow access to the service
* Nginx registers itself as a service with `ufw` upon installation, so it is straightforward to allow Nginx access

```commandline
sudo ufw app list
```

There are three profiles available for Nginx:

* **Nginx Full**: This profile open both port 80 (normal, unencrypted web traffic) and port 443 (TLS/SSL encrypted
traffic)
* **Nginx HTTP**: This profile opens only port 80
* **Nginx HTTPS**: This profile opens only port 443

It is recommended to enable the most restrictive profile that will still allow the traffic you've configured.

* Enable this by typing:

```commandline
sudo ufw allow 'Nginx HTTP'
```

* You can verify the change by typing:

```commandline
sudo ufw status
```

### Checking Web Server

* Ubuntu starts Nginx at the end of the installation process
* We can check with systemd init system to make sure service is running

```commandline
systemctl status nginx
```

* The output should show that the service has started
* The best way to verify Nginx is working is actually requesting a page
* Access default Nginx landing page by navigating to server's IP address
  * If you don't know it:

```commandline
curl -4 icanhazip.com
```

* Then enter server IP address into browser address bar
* You should receive the default Nginx landing page

### Managing the Nginx Process

* To stop web server:

```commandline
sudo systemctl stop nginx
```

* To start web server when it is stopped:

```commandline
sudo systemctl start nginx
```

* To stop and then start the service again:

```commandline
sudo systemctl restart nginx
```

* If only making configuration changes, Nginx can often reload without dropping connections
* To do this:

```commandline
sudo systemctl reload nginx
```

* To re-enable the service to start up at boot:

```commandline
sudo systemctl enable nginx
```

### Setting Up Server Blocks

*Using yaggy.dev as the example domain*

* *Server blocks* can be used to encapsulate configuration details and host more than one domain from a single server
* Nginx on Ubuntu 22.04 has one server block enabled by default that is configured to serve documents out of a directory
at `/var/www/html`
  * This is unwieldy if hosting multiple sites
* Instead of modifying `/var/www/html`, create directory structure within `/var/www` for your domain, leaving
`/var/www/html` as default directory to be served if a client request doesn't match any other sites
* Create directory for yaggy.dev as follows, using `-p` flag to create any necessary parent directories

```commandline
sudo mkdir -p /var/www/yaggy.dev/html
```

* Next assign ownership of directory with `$USER` environment variable

```commandline
sudo chown -R $USER:$USER /var/www/yaggy.dev/html
```

* Permissions of web roots should be correct if `unmask` value is unmodified
  * Which sets default file permissions
* To ensure permissions are correct and allow owner to read, write and execute files, while granting only read and
execute permissions to groups and others, input following command:

```commandline
sudo chmod -R 755 /var/www/yaggy.dev
```

* Next, create sample `index.html` page using `nano` or your favorite editor

```commandline
nano /var/www/yaggy.dev/html/index.html
```

* Add some boilerplate HTML, for example:

```html
<html>
    <head>
        <title>Welcome to yaggy.dev!</title>
    </head>
    <body>
        <h1>Success! The yaggy.dev server block is working!</h1>
    </body>
</html>
```

* In order for Nginx to serve this content, it's necessary to create a server block with the correct directives
* Instead of modifying default configuration file directly, make a new one at `/etc/nginx/sites-available/yaggy.dev`

```commandline
sudo nano /etc/nginx/sites-available/yaggy.dev
```

* Paste in the following configuration block, which is similar to the default, but updated for our new directory and
domain name:

```
server {
        listen 80;
        listen [::]:80;

        root /var/www/yaggy.dev/html;
        index index.html index.htm index.nginx-debian.html;

        server_name yaggy.dev www.yaggy.dev;

        location / {
                try_files $uri $uri/ =404;
        }
}
```

* Now `root` configuration has been updated to our new directory, and `server_name` to our domain name
* Next enable the file by creating a link to it from the `sites-enabled` directory, which Nginx reads from during
startup:

```commandline
sudo ln -s /etc/nginx/sites-available/yaggy.dev /etc/nginx/sites-enabled/
```

**Note:** Nginx uses a common practice called symbolic links, or symlinks, to track which of your server blocks are
enabled. Creating a symlink is like creating a shortcut on disk, so that you could later delete the shortcut from the
`sites-enabled` directory while keeping the server block in `sites-available` if you wanted to enable it.


* Two server blocks are now enabled and configured to respond to requests based on their `listen` and `server_name`
directives:
  * `yaggy.dev`: Will respond to requests for `yaggy.dev` and `www.yaggy.dev`
  * `default`: Will respond to any requests on port 80 that do not match the other two blocks
* To avoid possible hash bucket memory problem that can arise from adding additional server names, it is necessary to
adjust a single value in the `/etc/nginx/nginx.conf` file
* Open the file:

```commandline
sudo nano /etc/nginx/nginx.conf
```

* Find the `server_names_hash_bucket_size` directive and remove the `#` symbol to uncomment the line
* If using nano, search for words by pressing `CTRL` and `w`
  * **Note:** Commenting out lines is a way of disabling them without deleting them. Many configuration files ship with
multiple options commented out, so they can be enabled or disabled
* The file should look like this:

```
...
http {
    ...
    server_names_hash_bucket_size 64;
    ...
}
...
```

* Save and close file
* Next test to ensure there are no syntax files in any Nginx files

```commandline
sudo nginx -t
```

* If there aren't any problems, restart Nginx to enable changes

```commandline
sudo systemctl restart nginx
```

* Nginx should now be serving the domain name
* Test by navigating to `http://yaggy.dev`, where the previously created HTML file should be shown

### Important Nginx Files and Directories

#### Content

* `/var/www/html`
  * The actual web content, which by default consists only of the default Nginx page
  * Served out of the `/var/www/html` directory
  * Changed by altering Nginx configuration files

#### Server Configuration

* `/etc/nginx`
  * The Nginx configuration directory
  * All the Nginx configuration files reside here
* `/etc/nginx/nginx.conf`
  * The main Nginx configuration file
  * This can be modified to make changes to the Nginx global configuration
* `/etc/nginx/sites-available/`
  * The directory where per-site server blocks can be stored
  * Nginx will not use the configuration files found in this directory unless they are linked to the `sites-enabled`
directory
  * Typically, all server block configuration is done in this directory, and then enabled by linking to the other
directory
* `/etc/nginx/sites-enabled/`
  * The directory where enabled per-site server blocks are stored
  * Typically, these are created by linking to configuration files found in the `sites-available` directory
* `/etc/nginx/snippets`
  * This directory contains configuration fragments that can be included elsewhere in the Nginx configuration
  * Potentially repeatable configuration segments are good candidates for refactoring into snippets

#### Server Logs

* `/var/log/nginx/access.log`
  * Every request to the web server is recorded in this log file unless Nginx is configured to do otherwise
* `/var/log/nginx/error.log`
  * Any Nginx errors will be recorded in this log

### Securing Nginx with Let's Encrypt

#### Prerequisites

* Ubuntu 22.04 server set up by following the above documentation
* Registered domain name
* The following DNS records set up for the server:
  * An A record with `yaggy.dev` pointing to the server's public IP address
  * An A record with `www.yaggy.dev` pointing to the server's public IP address
* Nginx installed by following the above documentation
  * Including a server block for the domain
    * `/etc/nginx/sites-available/yaggy.dev`

#### Installing Certbot

* Install snap

```commandline
sudo snap install core; sudo snap refresh core
```

* Remove any older versions of certbot, if they exist

```commandline
sudo apt remove certbot
```

* **Note:** Have found that the following command seems to work better:
  * ```commandline
    sudo snap remove certbot
    ```

* Install `certbot` package

```commandline
sudo snap install --classic certbot
```

* Link `certbot` command from snap install directory to the path
  * Allows running by just typing `certbot`

```commandline
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

#### Confirming Nginx's Configuration

* Certbot needs to be able to find correct `server` block in the Nginx configuration to automatically configure SSL
* Check for a server block at `/etc/nginx/sites-available/yaggy.dev` with `server_name` set up appropriately
* Open the configuration file using `nano`:

```commandline
sudo nano /etc/nginx/sites-available/yaggy.dev
```

* Find the existing `server_name` line
* It should look like this:

```
...
server_name example.com www.example.com;
...
```

* If it does, exit the editor and move to the next step
* If not, update it to match, then check for errors using `sudo nginx -t`
* Once set up correctly, load the new configuration:

```commandline
sudo systemctl reload nginx
```

#### Allowing HTTPS Through the Firewall

* See current setting of `ufw` firewall:

```commandline
sudo ufw status
```

* Should see that only HTTP traffic is currently allowed
* Allow the Nginx Full profile and delete the redundant Nginx HTTP profile

```commandline
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 'Nginx HTTP'
```

* Check status again

```commandline
sudo ufw status
```

#### Obtaining SSL Certificate

* The Nginx plugin will take care of reconfiguring Nginx and reloading the config whenever necessary
* To use this plugin:

```commandline
sudo certbot --nginx -d yaggy.dev -d www.yaggy.dev
```

* This runs `certbot` with the `--nginx` plugin, using `-d` to specify the domain names the certificate should be valid
for
* Running the command will bring up a prompt to enter an email address and agree to the terms of service
* After doing so, a message will say the process was successful and give the location of the certificates
* This means the certificates are downloaded, installed, and loaded, and the Nginx configuration will now automatically
redirect all web requests to `https://`
* The browser security indicator should now indicate the site is secured
* Testing the server using the [SSL Labs Server Test](https://www.ssllabs.com/ssltest/) should result in an **A** grade

#### Verifying Certbot Auto-Renewal

* Let's Encrypt certificates are only valid for 90 days
* `certbot` adds a systemd timer that will run twice a day and automatically renew any certificate within thirty days
of expiration
* Query status of timer using `systemctl`:

```commandline
sudo systemctl status snap.certbot.renew.service
```

* Test renewal process using a dry run with `certbot`:

```commandline
sudo certbot renew --dry-run
```

* If no errors, then all set!
* If the automated renewal process ever fails, Let's Encrypt will send a message to the email specified, warning when
the certificate is about to expire

### Serving Flask Applications with Gunicorn and Nginx on Ubuntu 22.04

#### Prerequisites

* Above steps followed

#### Install Components from Ubuntu Repositories

* First update local package index and install packages necessary to build Python environment

```commandline
sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
```

#### Create Python Virtual Environment

* Set up a virtual environment to isolate Flask application from other Python files on the system
* Start by installing `python3-venv` package, which installs the `venv` module

```commandline
sudo apt install python3-venv
```

* Make a parent directory for your Flask project
* Move into the directory after it's created

```commandline
mkdir ~/yaggydev
cd ~/yaggydev
```

* Create a virtual environment to store Flask project's Python requirements:

```commandline
python3 -m venv venv
```

* Activate the virtual environment

```commandline
source venv/bin/activate
```

#### Setting Up A Flask Application

* Now it's time to install Flask and Gunicorn
* First install `wheel` to ensure packages will install even if missing wheel archives

```commandline
pip install wheel
```

  * **Note:** Make sure to use the `pip` command (not `pip3`)

* Next install Flask and Gunicorn

```commandline
pip install gunicorn flask
```

##### Creating a Sample App

* Create a demo Flask app in a single file, `yaggydev.py`

```commandline
nano ~/yaggydev/yaggydev.py
```

* This is where the application code goes
* It will import Flask and instantiate a Flask object
* Use this to define the functions that should be run when a specific route is requested

`~/yaggydev/yaggydev.py`:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```

* To test the application, need to allow access to port `5000`:

```commandline
sudo ufw allow 5000
```

* Now test the Flask app

```commandline
python yaggydev.py
```

* This should show a warning that this server setup should not be used in production
* Visit the server's IP address followed by `:5000` in the browser
* The result should be similar to the following:

<h1 style='color:blue'>Hello There!</h1>

* Hit `CTRL-C` in the terminal window to stop the Flask development server

##### Creating the WSGI Entry Point

* Next, create a file that will serve as the entry point for the application
* This will tell the Gunicorn server how to interact with the application
* Call the file `wsgi.py`:

```commandline
nano ~/yaggydev/wsgi.py
```

* In this file, import the Flask instance from the application and then run it:

`~/yaggydev/wsgi.py`:

```python
from yaggydev import app
if __name__ == "__main__":
    app.run()
```

* Save and close the file when finished

#### Configuring Gunicorn

* The entry point for the application is now established
* Now it's time to configure Gunicorn
* First check that Gunicorn can serve the application correctly
  * Try passing Gunicorn the name of the application's entry point
    * Constructed as the name of the module (minus the `.py` extension), plus the name of the callable within the
application (in this case, `wsgi:app`)
  * Also specify the interface and port to bind to using the `0.0.0.0:5000` argument to the application will be started
on a publicly available interface:

```commandline
cd ~/yaggydev
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

* The output should resemble the following:

```commandline
Output
[2020-05-20 14:13:00 +0000] [46419] [INFO] Starting gunicorn 20.0.4
[2020-05-20 14:13:00 +0000] [46419] [INFO] Listening at: http://0.0.0.0:5000 (46419)
[2020-05-20 14:13:00 +0000] [46419] [INFO] Using worker: sync
[2020-05-20 14:13:00 +0000] [46421] [INFO] Booting worker with pid: 46421
```

* Visit the server's IP address with `:5000` appended at the end in the web browser again
* This should display the same output as before:

<h1 style='color:blue'>Hello There!</h1>

* After confirming that it's working, press `CTRL-C` in the terminal window
* The virtual environment can now be deactivated

```commandline
deactivate
```

* Now any Python commands will use the system's Python environment
* Next, create the systemd service unit file
* This will allow Ubuntu's init system to automatically start Gunicorn and serve the Flask application whenever the
server boots
* Create a unit file ended in `.service` within the `/etc/systemd/system` directory to begin

```commandline
sudo nano /etc/systemd/system/yaggydev.service
```

* Inside, start with the `[Unit]` section, used to specify metadata and dependencies
  * Add a description of the service here and tell the init system to only start this after the networking target has been
  reached
* Next, add a `[Service]` section
  * This will specify the user and group the process should run under
  * Give the regular user account ownership of the process since it owns all the relevant files
  * Also give group ownership to the `www-data` group so Nginx can easily communicate with the Gunicorn processes
  * Remember to use the correct username
* Next, map out the working directory and set the `PATH` environmental variable
  * Tells the init system that the executables for the process are located within the virtual environment
* Also specify the command to start the service, which does the following:
  * Starts 3 worker processes (should be adjusted as necessary)
  * Creates and binds to a Unix socket file, `yaggydev.sock`, within the project directory
    * The unmask value will be set to `007` so the socket file is created giving access to owner and group, but
restricting other access
  * Specifies the WSGI entry point file name, along with the Python callable within that file (`wsgi:app`)
* Systemd requires a full path to the Gunicorn executable, which is installed within the virtual environment
* Remember to use the correct username and project paths
* Finally, add an `[Install]` section
  * Tells systemd what to link this service to if it's enabled to start at boot
  * This service should start when the regular multi-user system is up and running

`/etc/systemd/system/yaggydev.service`:

```
[Unit]
Description=Gunicorn instance to serve yaggydev
After=network.target

[Service]
User=owen
Group=www-data
WorkingDirectory=/home/owen/yaggydev
Environment="PATH=/home/owen/yaggydev/venv/bin"
ExecStart=/home/owen/yaggydev/venv/bin/gunicorn --workers 3 --bind unix:yaggydev.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

* Now the systemd service file is complete
* Save and close it
* Start the previously-created Gunicorn service and enable it so it starts at boot

```commandline
sudo systemctl start yaggydev
sudo systemctl enable yaggydev
```

* Check the status

```commandline
sudo systemctl status yaggydev
```

* Resolve any errors before continuing

#### Configuring Nginx to Proxy Requests

* Now configure Nginx to pass web requests to the socket by making small additions to its configuration file
* Begin by creating a new server block configuration file in Nginx's `sites-available` directory
  * Here, calling it `yaggydev`

```commandline
sudo nano /etc/nginx/sites-available/yaggydev
```

* Open up a server block and tell Nginx to listen on the default port `80`
* Also tell it to use this block for requests to the server's domain name 
* Next, add a location block that matches every request
* Within this block, include `proxy_params` file that specifies some general proxying parameters that need to be set
* Then pass the requests to the socket defined using the `proxy_pass` directive

```/etc/nginx/sites-available/yaggydev```:

```
server {
    listen 80;
    server_name yaggy.dev www.yaggy.dev;
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/owen/yaggydev/yaggydev.sock;
    }
}
```

* Save and close the file when finished
* To enable the Nginx server block configuration file that was just created, link the file to the `sites-enabled`
directory:

```commandline
sudo ln -s /etc/nginx/sites-available/yaggydev /etc/nginx/sites-enabled
```

* Now test for syntax errors

```commandline
sudo nginx -t
```

* If there are no issues, restart the Nginx process to read the new configuration

```commandline
sudo systemctl restart nginx
```

* Finally, adjust the firewall again to restrict access through port `5000`
* Also make sure access is allowed to the Nginx server (should already be allowed)

```commandline
sudo ufw delete allow 5000
sudo ufw allow 'Nginx Full'
```

* Now, navigating to the server's domain name in the web browser should result in the application's output from before:

<h1 style='color:blue'>Hello There!</h1>

##### Potential Problems

* If Nginx cannot access gunicorn's socket file, there will be an HTTP 502 gateway error
  * Usually because user's home directory does not allow other users to access files inside it
  * If socket file is called `/home/owen/yaggydev/yaggydev.sock`, ensure `/home/owen` has a minimum of `0755`
permissions
  * Use a tool like `chmod` to change these permissions:
  ```commandline
  sudo chmod 755 /home/owen
  ```
* If any errors are encountered, try checking the following:
* `sudo less /var/log/nginx/error.log`: Check the Nginx error logs
* `sudo less /var/log/nginx/access.log`: Check the Nginx access logs
* `sudo journalctl -u nginx`: Check the Nginx process logs
* `sudo journalctl -u yaggydev`: Check the Flask app's Gunicorn logs
