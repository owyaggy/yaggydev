# Serving Flask Using Docker, uWSGI and Nginx on Ubuntu

### Installing Docker

* Update the package list

```commandline
sudo apt update
```

* Install prerequisite packages which let `apt` use packages over HTTPS:

```commandline
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

* Then add GPG key for the official Docker repository to the system:

```commandline
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

* Add the Docker repository to APT sources:

```commandline
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

* Update the existing package list again to recognize the addition:

```commandline
sudo apt update
```

* Ensure installation will be from Docker repo rather than default Ubuntu repo:

```commandline
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

```commandline
sudo apt install docker-ce
```

* Check that it's running:

```commandline
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

```commandline
sudo usermod -aG docker ${USER}
```

* To apply new group membership, log out of the server and then back in, or type the following:

```commandline
su - ${USER}
```

* The user password will be required
* Confirm that the user has been added to the `docker` group:

```commandline
groups
```

* The output should show `owen sudo users docker`
* If it is necessary to add a user to the `docker` group that isn't currently logged in, that username can be declared
explicitly:

```commandline
sudo usermod -aG docker owen
```

* The rest of this guide assumes that the user has been added to the `docker` group

### Using the Docker Command

* Using `docker` consists of passing it a chain of options and commands followed by arguments
* THe syntax takes this form:

```commandline
docker [option] [command] [arguments]
```

* To view all available subcommands, type:

```commandline
docker
```

* To view the options available to a specific command, type:

```commandline
docker docker-subcommand --help
```

* To view system-wide information about Docker, use:

```commandline
docker info
```

### Working With Docker Images

* Docker containers are built from Docker images
* By default, these images are pulled from [Docker Hub](https://hub.docker.com/)
  * A Docker registry managed by Docker
* Anyone can host their Docker images on Docker hub, so most necessary applications and Linux distributions will have
images hosted there
* To check if it is possible to access and download images from Docker Hub, type:

```commandline
docker run hello-world
```

* The output will indicate that Docker is working correctly
* To search for images available on the Docker Hub, use the `docker` command with the `search` subcommand
* For example, to search for the Ubuntu image:

```commandline
docker search ubuntu
```

* The script will crawl the Docker Hub and return a listing of all images whose name matches the search string
* In the **OFFICIAL** column of the output, **OK** indicates an image built and supported by the company behind the
project
* After identifying the image to use, to download it, use the `pull` subcommand
* Execute the following command to download the official `ubuntu` image:

```commandline
docker pull ubuntu
```

* After an image has been downloaded, it's possible to run a container using the downloaded image with the `run`
subcommand
* If an image has not been downloaded when `docker` is executed with the `run` subcommand, Docker will first download
the image, then run a container using it
* To see downloaded images, type:

```commandline
docker images
```

* Images that are used to run containers can be modified and used to generate new images, which may then be uploaded
  (*pushed* is the technical term) to Docker Hub or other Docker registries

### Running A Docker Container

* The `hello-world` container is an example of a container that runs and exits after emitting a test message
* Containers can be much more useful: they're similar to virtual machines, only more resource-friendly
* As an example, run a container using the latest image of Ubuntu
* The combination of the **-i** and **-t** switches gives interactive shell access into the container

```commandline
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

```commandline
root@3e5d18b36062:/# apt update
```

* Then install any application in it, for example, Node.js:

```commandline
root@3e5d18b36062:/# apt install nodejs
```

* This installs Node.js in the container from the official Ubuntu repository
* When the installation finishes, verify that Node.js is installed:

```commandline
root@3e5d18b36062:/# node -v
```

* The version number will be displayed in the terminal
* Any changes made inside a container only apply to that container
* To exit the container, type `exit` at the prompt

### Managing Docker Containers

* After using Docker for a while, there will be many active (running) and inactive containers on the system
* To view the **active** ones, use:

```commandline
docker ps
```

* The output should show the headers of a table, but not list any containers right now:

```
CONTAINER ID        IMAGE               COMMAND             CREATED
```

* In this guide, two containers were started: one from the `hello-world` image and another from the `ubuntu` image
  * Both are no longer running, but still exist on the system
* To view all containers, active and inactive, run `docker ps` with the `-a` switch:

```commandline
docker ps -a
```

* The output should show both the `ubuntu` and `hello-world` containers
* To view the most recently created container, pass it the `-l` switch:

```commandline
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

```commandline
docker start 3e5d18b36062
```

* The container will start
* To see its status:

```commandline
docker ps
```

`Output`:

```
CONTAINER ID   IMAGE     COMMAND       CREATED          STATUS          PORTS     NAMES
3e5d18b36062   ubuntu    "/bin/bash"   17 minutes ago   Up 51 seconds             ecstatic_napier
```

* To stop a running container, use `docker stop` followed by the container ID or name
* For example, to use the assigned name, which in this case is `ecstatic_napier`:

```commandline
docker stop ecstatic_napier
```

* Once a container is no longer needed, remove it with the `docker rm` command
  * Again, use either the container ID or the name
* Use the `docker ps -a` command to find the container ID or name for the container associated with the `hello-world`
image and remove it:

```commandline
docker ps -a
```

`Output`:

```
CONTAINER ID   IMAGE         COMMAND       CREATED          STATUS                            PORTS     NAMES
3e5d18b36062   ubuntu        "/bin/bash"   19 minutes ago   Exited (137) About a minute ago             ecstatic_napier
90cb7494cd79   hello-world   "/hello"      34 minutes ago   Exited (0) 34 minutes ago                   practical_gates
```

* Remove the container using its name `practical_gates`:

```commandline
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

```commandline
docker commit -m "What you did to the image" -a "Author Name" container_id repository/new_image_name
```

* The **-m** switch is for the commit message that describes the changes made
* The **-a** switch is to specify the author
* The `repository` is usually the user's username on Docker Hub
* For example, for the user **owyaggy**, with the container ID of `3e5d18b36062`, the command would be:

```commandline
docker commit -m "added Node.js" -a "owen" 3e5d18b36062 owyaggy/ubuntu-nodejs
```

* When a user *commits* an image, the new image is saved locally on the user's computer
* Listing the Docker images again will show the new image, as well as the old one it was derived from:

```commandline
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

```commandline
docker login -u docker-registry-username
```

* This should be followed by a prompt to authenticate via password
  * Note: if the Docker registry username differs from the local username used to create the image, the image needs to be
  tagged with the registry username
    * For the example previously given, type:
    * ```commandline
      docker tag owyaggy/ubuntu-nodejs docker-registry-username/ubuntu-nodejs
      ```
      
* An image can now be pushed using:

```commandline
docker push docker-registry-username/docker-image-name
```

* To push the `ubuntu-nodejs` image to the `owyaggy` repository, the command would be:

```commandline
docker push owyaggy/ubuntu-nodejs
```

* After pushing an image to a registry, it should be listed in the user's account dashboard, under `Images` > `Hub`
* Now, `docker pull owyaggy/ubuntu-nodejs` can be used to pull the image to a new machine adn use it to run a new
container