
# Builds Wistar from git based on an Ubuntu image
# docker run -d --privileged -p 80:80 -v /opt/wistar/user_images:/opt/wistar/user_images -v /var/run/libvirt:/var/run/libvirt --name wistar01 juniper/wistar

# Steps before creating the docker image:
# Create the /opt/wistar/user_images/instances directory structure with www-data:www-data user permissions on the host machine
# Change user permissions on /var/run/libvirt to www-data:www-data
# Install docker-ce
# Follow the instructions on wistar README page to setup bridging and networking

#To run the docker container from the image created from the Dockerfile 
# docker run -d -it --privileged -p <host port: port on docker> -v /opt/wistar/user_images:/opt/wistar/user_images -v /var/run/libvirt:/var/run/libvirt --name wistar01 <Image-Id>


FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

# Optional if you have apt cache in your lab
# RUN echo 'Acquire::HTTP::Proxy "http://10.86.9.12:3142";' >> /etc/apt/apt.conf.d/01proxy \
# && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy

# Update all packages to the latest version
RUN apt-get update

# Install Junos eznc dependencies
RUN apt-get install -y build-essential libxml2-dev libxslt1-dev libz-dev libffi-dev \
    libssl-dev python-dev git python-pip

# Install python-cryptography and Junos eznc
RUN pip install cryptography junos-eznc jxmlease pyvbox

# Install Wistar dependencies
RUN apt-get install -y qemu-kvm libvirt-bin socat python-pexpect python-libvirt \
    python-yaml unzip bridge-utils python-numpy genisoimage python-netaddr \
    python-markupsafe python-setuptools mtools dosfstools openvswitch-switch apache2\
    libapache2-mod-wsgi sudo

# Install Django
RUN pip install django==1.9.9

#  Create the required directory structures
RUN mkdir -p /opt/wistar/user_images/instances
RUN mkdir -p /opt/wistar/media
RUN mkdir -p /opt/wistar/seeds
WORKDIR /opt/wistar

# Pull latest wistar from Git
RUN git clone -b nembery050218 https://github.com/Juniper/wistar.git --depth=1 wistar-master

# Create Wistar tables
RUN /opt/wistar/wistar-master/manage.py migrate

# Enable the Apache2 module “wsgi”
RUN a2enmod wsgi;service apache2 restart

# Create log files
RUN touch /var/log/apache2/wistar.log /var/log/apache2/wistar_access.log /var/log/wistar.log

# Copy wistar config file to apache
COPY 999-wistar.conf /etc/apache2/sites-available/999-wistar.conf

# Set appropriate permissions
RUN chown -R www-data:www-data /opt/wistar /var/log/wistar.log /var/log/apache2/wistar.log /var/log/apache2/wistar_access.log

# Enable wistar site in apache
RUN ln -sf /etc/apache2/sites-available/999-wistar.conf /etc/apache2/sites-enabled/999-wistar.conf

# Add www-data to libvirt users
RUN usermod -a -G libvirtd www-data

# Allow libvirtd user to create and modify ovs bridges
RUN echo '%libvirtd ALL=NOPASSWD: /usr/bin/ovs-vsctl' >> /etc/sudoers

# Bind the port mentioned in 999-wistar.conf file 
EXPOSE 8080


ENTRYPOINT service apache2 restart && service openvswitch-switch start
