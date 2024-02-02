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
* You'll receive confirmation that the IP address has been added to the lis tof known hosts
* Might receive a remote host identification warning, particularly if just having destryoyed a Droplet

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

* **Nginx Full**: This profile open both port 80 (normal, unecrypted web traffic) and port 443 (TLS/SSL encrypted
traffic)
* **Nginx HTTP**: This profile opens only port 80
* **Nginx HTTPS**: This profile opens only port 443

It is recommended to enable the most restrictive profile that will still allow the traffic you've configured.

* Enable this by typing:

```sudo ufw allow 'Nginx HTTP'```

* You can verify the change by typing:

```sudo ufw status```

### Checking Web Server

* Ubuntu starts Nginx at the end of the installation process
* We can check with `systemd` init system to make sure service is running

```systemctl status nginx```

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