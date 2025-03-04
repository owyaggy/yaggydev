# Serving Flask Using Docker, uWSGI and Nginx on Ubuntu

## Introduction To Docker

### Installing Docker

* Update the package list

```shell
sudo apt update
```

* Install prerequisite packages which let `apt` use packages over HTTPS:

```shell
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

* Then add GPG key for the official Docker repository to the system:

```shell
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

* Add the Docker repository to APT sources:

```shell
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

* Update the existing package list again to recognize the addition:

```shell
sudo apt update
```

* Ensure installation will be from Docker repo rather than default Ubuntu repo:

```shell
apt-cache policy docker-ce
```

* Output should resemble the following:

```
docker-ce:
  Installed: (none)
  Candidate: 5:20.10.14~3-0~ubuntu-jammy
  Version table:
     5:20.10.14~3-0~ubuntu-jammy 500
        500 https://download.docker.com/linux/ubuntu jammy/stable amd64 Packages
     5:20.10.13~3-0~ubuntu-jammy 500
        500 https://download.docker.com/linux/ubuntu jammy/stable amd64 Packages
```

* Install Docker:

```shell
sudo apt install docker-ce
```

* Check that it's running:

```shell
sudo systemctl status docker
```

* The output should indicate that the service is active and running
* Now you have not just the Docker service (daemon), but also the `docker` command line utility, or the Docker client

### Executing the Docker Command Without Sudo (Optional)

* By default, the `docker` command can only be run by the **root** user or a user in the **docker** group (created
automatically during Docker installation)
* Attempting to run `docker` command without `sudo` prefix results in an output like this:

```
docker: Cannot connect to the Docker daemon. Is the docker daemon running on this host?.
See 'docker run --help'.
```

or,

```
Server:
ERROR: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/info": dial unix /var/run/docker.sock: connect: permission denied
```

* To avoid needing to type `sudo` whenever running `docker` command, add username to the `docker` group:

```shell
sudo usermod -aG docker ${USER}
```

* To apply new group membership, log out of the server and then back in, or type the following:

```shell
su - ${USER}
```

* The user password will be required
* Confirm that the user has been added to the `docker` group:

```shell
groups
```

* The output should show `owen sudo users docker`
* If it is necessary to add a user to the `docker` group that isn't currently logged in, that username can be declared
explicitly:

```shell
sudo usermod -aG docker owen
```

* The rest of this guide assumes that the user has been added to the `docker` group

### Using the Docker Command

* Using `docker` consists of passing it a chain of options and commands followed by arguments
* THe syntax takes this form:

```shell
docker [option] [command] [arguments]
```

* To view all available subcommands, type:

```shell
docker
```

* To view the options available to a specific command, type:

```shell
docker docker-subcommand --help
```

* To view system-wide information about Docker, use:

```shell
docker info
```

### Working With Docker Images

* Docker containers are built from Docker images
* By default, these images are pulled from [Docker Hub](https://hub.docker.com/)
  * A Docker registry managed by Docker
* Anyone can host their Docker images on Docker hub, so most necessary applications and Linux distributions will have
images hosted there
* To check if it is possible to access and download images from Docker Hub, type:

```shell
docker run hello-world
```

* The output will indicate that Docker is working correctly
* To search for images available on the Docker Hub, use the `docker` command with the `search` subcommand
* For example, to search for the Ubuntu image:

```shell
docker search ubuntu
```

* The script will crawl the Docker Hub and return a listing of all images whose name matches the search string
* In the **OFFICIAL** column of the output, **OK** indicates an image built and supported by the company behind the
project
* After identifying the image to use, to download it, use the `pull` subcommand
* Execute the following command to download the official `ubuntu` image:

```shell
docker pull ubuntu
```

* After an image has been downloaded, it's possible to run a container using the downloaded image with the `run`
subcommand
* If an image has not been downloaded when `docker` is executed with the `run` subcommand, Docker will first download
the image, then run a container using it
* To see downloaded images, type:

```shell
docker images
```

* Images that are used to run containers can be modified and used to generate new images, which may then be uploaded
  (*pushed* is the technical term) to Docker Hub or other Docker registries

### Running A Docker Container

* The `hello-world` container is an example of a container that runs and exits after emitting a test message
* Containers can be much more useful: they're similar to virtual machines, only more resource-friendly
* As an example, run a container using the latest image of Ubuntu
* The combination of the **-i** and **-t** switches gives interactive shell access into the container

```shell
docker run -it ubuntu
```

* The command prompt should change to reflect the container being worked inside:

```
root@3e5d18b36062:/#
```

* Note the container ID, in this example `3e5d18b36062`
* The container ID is needed to identify the container to remove it
* It's now possible to run any command inside the container
* For example, update the package database inside the container:
  * It's not necessary to prefix commands with `sudo` because the root user is being used

```shell
root@3e5d18b36062:/# apt update
```

* Then install any application in it, for example, Node.js:

```shell
root@3e5d18b36062:/# apt install nodejs
```

* This installs Node.js in the container from the official Ubuntu repository
* When the installation finishes, verify that Node.js is installed:

```shell
root@3e5d18b36062:/# node -v
```

* The version number will be displayed in the terminal
* Any changes made inside a container only apply to that container
* To exit the container, type `exit` at the prompt

### Managing Docker Containers

* After using Docker for a while, there will be many active (running) and inactive containers on the system
* To view the **active** ones, use:

```shell
docker ps
```

* The output should show the headers of a table, but not list any containers right now:

```
CONTAINER ID        IMAGE               COMMAND             CREATED
```

* In this guide, two containers were started: one from the `hello-world` image and another from the `ubuntu` image
  * Both are no longer running, but still exist on the system
* To view all containers, active and inactive, run `docker ps` with the `-a` switch:

```shell
docker ps -a
```

* The output should show both the `ubuntu` and `hello-world` containers
* To view the most recently created container, pass it the `-l` switch:

```shell
docker ps -l
```

`Output`:

```
CONTAINER ID   IMAGE     COMMAND       CREATED          STATUS                     PORTS     NAMES
3e5d18b36062   ubuntu    "/bin/bash"   13 minutes ago   Exited (0) 7 minutes ago             ecstatic_napier
```

* Only `ubuntu` will be shown
* Note the Container ID of `3e5d18b36062`
* To start a stopped container, use `docker start` followed by the container ID or the container's name
* To start the Ubuntu-based container with the ID of `3e5d18b36062`:

```shell
docker start 3e5d18b36062
```

* The container will start
* To see its status:

```shell
docker ps
```

`Output`:

```
CONTAINER ID   IMAGE     COMMAND       CREATED          STATUS          PORTS     NAMES
3e5d18b36062   ubuntu    "/bin/bash"   17 minutes ago   Up 51 seconds             ecstatic_napier
```

* To stop a running container, use `docker stop` followed by the container ID or name
* For example, to use the assigned name, which in this case is `ecstatic_napier`:

```shell
docker stop ecstatic_napier
```

* Once a container is no longer needed, remove it with the `docker rm` command
  * Again, use either the container ID or the name
* Use the `docker ps -a` command to find the container ID or name for the container associated with the `hello-world`
image and remove it:

```shell
docker ps -a
```

`Output`:

```
CONTAINER ID   IMAGE         COMMAND       CREATED          STATUS                            PORTS     NAMES
3e5d18b36062   ubuntu        "/bin/bash"   19 minutes ago   Exited (137) About a minute ago             ecstatic_napier
90cb7494cd79   hello-world   "/hello"      34 minutes ago   Exited (0) 34 minutes ago                   practical_gates
```

* Remove the container using its name `practical_gates`:

```shell
docker rm practical_gates
```

* A new container can be started and given a name using the `--name` switch
* The `--rm` switch can be used to create a container that removes itself when its stopped
* See the `docker run help` command for more information on these options and others

### Committing Changes In A Container To A Docker Image

* In a Docker image, files can be crated, modified, and deleted just like in a virtual machine
* The changes will only apply to that container
* It can be started and stopped
* Once it's destroyed with the `docker rm` command, the changes are permanently lost
* The state of a container can be saved as a new Docker image
* For example, after installing Node.js inside the Ubuntu container, there is a container running off an image
* However, the container is different from the image used to create it
* To reuse this Node.js container as the basis for new images later, commit the changes to a new Docker image
* Use the following command:

```shell
docker commit -m "What you did to the image" -a "Author Name" container_id repository/new_image_name
```

* The **-m** switch is for the commit message that describes the changes made
* The **-a** switch is to specify the author
* The `repository` is usually the user's username on Docker Hub
* For example, for the user **owyaggy**, with the container ID of `3e5d18b36062`, the command would be:

```shell
docker commit -m "added Node.js" -a "owen" 3e5d18b36062 owyaggy/ubuntu-nodejs
```

* When a user *commits* an image, the new image is saved locally on the user's computer
* Listing the Docker images again will show the new image, as well as the old one it was derived from:

```shell
docker images
```

`Output`:

```
REPOSITORY              TAG       IMAGE ID       CREATED              SIZE
owyaggy/ubuntu-nodejs   latest    b1acbebf9703   About a minute ago   210MB
...
```

* In this example, `ubuntu-nodejs` is the new image, which was derived from the existing `ubuntu` image from Docker Hub
* The size difference reflects the changes that were made
* Images can also be built from a `Dockerfile`, which can automate the installation of software in a new image

### Pushing Docker Images To A Docker Repository

* If a new image is created from an existing image, it can be shared with a select few, on Docker Hub, or another Docker
registry
* An account is needed to push an image to Docker Hub or any other Docker registry
* To push an image, first log into Docker Hub

```shell
docker login -u docker-registry-username
```

* This should be followed by a prompt to authenticate via password
  * Note: if the Docker registry username differs from the local username used to create the image, the image needs to be
  tagged with the registry username
    * For the example previously given, type:
    * ```shell
      docker tag owyaggy/ubuntu-nodejs docker-registry-username/ubuntu-nodejs
      ```
      
* An image can now be pushed using:

```shell
docker push docker-registry-username/docker-image-name
```

* To push the `ubuntu-nodejs` image to the `owyaggy` repository, the command would be:

```shell
docker push owyaggy/ubuntu-nodejs
```

* After pushing an image to a registry, it should be listed in the user's account dashboard, under `Images` > `Hub`
* Now, `docker pull owyaggy/ubuntu-nodejs` can be used to pull the image to a new machine adn use it to run a new
container

## Building And Deploying Flask With Docker

### Setting Up Flask Application

* First create a directory structure to hold the Flask application

```shell
sudo mkdir /var/www/yaggydev
```

* Move in to the newly created `yaggydev` directory:

```shell
cd /var/www/yaggydev
```

* Next, create the base folder structure for the Flask application:

```shell
sudo mkdir -p app/static app/templates
```

* The `-p` flag indicates that `mkdir` will create a directory and all parent directories that don't exist
  * In this case, the `app` parent directory will be created in the process of making the `static` and `templates`
  directories
* The `app` directory will contain all files related to the Flask application such as its *views* and *blueprints*
* [Views](https://flask.palletsprojects.com/en/2.0.x/tutorial/views/) are the code that responds to requests to the
application
* *Blueprints* create application components and support common patterns within an application or across multiple
applications
* The `static` directory is where assets such as images, CSS, and JavaScript files live
* The `templates` directory is where HTML templates for the project are located
* Now, given the base folder structure, create the files needed to run the Flask application
* First create an `__init__.py` file inside the `app` directory
  * This file tells the Python interpreter that the `app` directory is a package and should be treated as such
* Run the following command to create the file:

```shell
sudo nano app/__init__.py
```

* Next, add code to the `__init__.py` that will create a Flask instance and import the logic from the `views.py` file
* Add the following code to the new file:

`/var/www/yaggydev/app/__init__.py`:

```python
from flask import Flask
app = Flask(__name__)
from app import views
```

* Now, create the `views.py` file in the `app` directory
  * This file will contain most of the application logic

```shell
sudo nano app/views.py
```

* Add the code to the `views.py` file
* This code will return the `hello world!` string to users who visit the web page:

`/var/www/yaggydev/app/views.py`:

```python
from app import app

@app.route('/')
def home():
   return "hello world!"
```

* Now create the `uwsgi.ini` file
* uWSGI is a deployment option for Nginx that is both a protocol and an application server
  * The application server can serve uWSGI, FastCGI, and HTTP protocols
* To create this file, run:

```shell
sudo nano uwsgi.ini
```

* Next, add the following content to the file to configure the uWSGI server:

`/var/www/yaggydev/uwsgi.ini`:

```ini
[uwsgi]
module = main
callable = app
master = true
```

* This code defines the module that the Flask application will be served from
* In this case, this is the `main.py` file, referenced here as `main`
* The `callable` option instructs uWSGI to use the `app` instance exported by the main application
* The `master` option allows the application to keep running, so there is little downtime even when reloading the entire
application
* Next, create the `main.py` file, which is the entry point to the application
* The entry point instructs uWSGI on how to interact with the application

```shell
sudo nano main.py
```

* In the file, import the Flask instance named `app` from the application package that was previously created

`/var/www/yaggydev/main.py`:

```shell
from app import app
```

* Finally, create a `requirements.txt` file to specify the dependencies that the `pip` package manager will install to
the Docker deployment

```shell
sudo nano requirements.txt
```

* Add the following line to add Flask as a dependency:

`/var/www/yaggydev/requirements.txt`:

```text
Flask>=3.0.2
```

* This specifies the version of Flask to be installed

### Setting Up Docker

* To create the Docker deployment, two files will be created:
  * `Dockerfile`, a text document that contains the commands used to assemble the image
  * `start.sh`, a shell script that will build an image and create a container from the `Dockerfile`
* First create the `Dockerfile`:

```shell
sudo nano Dockerfile
```

`/var/www/yaggydev/Dockerfile`:

```dockerfile
# Python version changed to more modern, *non-alpine* version
FROM tiangolo/uwsgi-nginx-flask:python3.11
# RUN apk --update add bash nano # This line commented out because it threw an error...
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt
```

* This Docker image will be built off an existing image, `tiangolo/uwsgi-nginx-flask` (found on
[DockerHub](https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask))
* The first two lines specify the parent image used to run the application and install the bash command processor and
the `nano` text editor
* It also installs the `git` client for pulling and pushing to version control hosting services (GitHub, GitLab,
BitBucket, etc.)
* `ENV STATIC_URL /static` is an environment variable specific to this Docker image
  * It defines the static folder where all assets such as images, CSS files, and JavaScript files are served from
* The last two lines will copy the `requirements.txt` file into the container so that it can be executed, and then
parses the `requirements.txt` file to install the specified dependencies
* Now ensure there is an open port to use in the configuration
* To check if a port is free, run:

```shell
sudo nc localhost 56733 < /dev/null; echo $?
```

* If the output of the command above is `1`, then the port is free and usable
* Otherwise, a different port should be used in the `start.sh` configuration file
* Once an open port has been found, create the `start.sh` script:

```shell
sudo nano start.sh
```

* `start.sh` is a shell script that will build an image from the `Dockerfile` and create a container from the resulting
Docker image
* Add the configuration to the new file:

```shell
#!/bin/bash
app="docker.test"
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD:/app ${app}
```

* The first line is the *shebang*, which specifies that this is a bash file and will be executed as commands
* The next line specifies the name to give the image and container and saves as a variable named `app`
* The next line instructs Docker to build an image from the `Dockerfile` located in the current directory
  * This will create an image called `docker.test` in this example
* The last three lines create a new container named `docker.test` that is exposed at port `56733`
* Finally, it links the present directory to the `/var/www` directory of the container
* The `-d` flag is used to start a container in daemon mode, or as a background process
* The `-p` flag binds a port on the server to a particular port on the Docker container
  * In this case, binding port `56733` to port `80` on the Docker container
* The `-v` flag specifies a Docker volume to mount on the container
  * In this case, mounting the entire project directory to the `/var/www` folder on the Docker container
* Execute the `start.sh` script to create the Docker image and build a container from the resulting image:

```shell
sudo bash start.sh
```

* After the script runs, list all running containers:

```shell
sudo docker ps
```

* The output should show the containers:

`Output`:

```text
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                                              NAMES
e5d1ddd826d1   docker.test   "/entrypoint.sh /sta…"   7 seconds ago   Up 4 seconds   443/tcp, 0.0.0.0:56733->80/tcp, :::56733->80/tcp   docker.test
```

* The `docker.test` container should be running
* Now visit the IP address at the specified port in the browser: `http://ip-address:56733`
* A simple "hello world" page should be displayed

### Serving Template Files

* [Templates](https://flask.palletsprojects.com/en/2.0.x/tutorial/templates/) display static and dynamic content to
users who visit the application
* Start by creating a `home.html` file in the `app/templates` directory:

```shell
sudo nano app/templates/home.html
```

* Add some template code:

`/var/www/yaggydev/app/templates/home.html`:

```html
<!doctype html>

<html lang="en-us">   
  <head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <title>Welcome home</title>
  </head>
  
  <body>
    <h1>Home Page</h1>
    <p>This is the home page of our application.</p>
  </body> 
</html>
```

* Next, modify `app/views.py` file to serve the newly created file:

```shell
sudo nano app/views.py
```

* Add a line at the beginning of the file to import the `render_template` method from Flask
  * This method parses an HTML file to render a web page to the user

```python
from flask import render_template
...
```

* At the end of the file, add a new route to render the template file
* This code specifies that users are served the contents of the `home.html` file whenever they visit the `/template`
route on the application

```python
...
@app.route('/template')
def template():
    return render_template('home.html')
```

* The updated `app/views.py` file will look like this:

`/var/www/yaggydev/app/views.py`:

```python
from flask import render_template
from app import app 

@app.route('/')
def home():
    return "hello world!"

@app.route('/template')
def template():
    return render_template('home.html')
```

* In order for the changes to take effect, the Docker container will need to be stopped and restarted
* Run the following command to rebuild the container:

```shell
sudo docker stop docker.test && sudo docker start docker.test
```

* Visit the application at `http://ip-address:56733/template` to see the new template being served