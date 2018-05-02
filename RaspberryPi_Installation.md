
## Install Raspbian
Install Raspbian using 2018-03-13-raspbian-stretch.img
with instructions from https://www.raspberrypi.org/downloads/raspbian/

## Updata Java
The default version of java is not enough to build imagej-server using maven, so you need to upgrade first.

* From Oracle website, download latest JDK
http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html

In my case it was: jdk-8u172-linux-arm32-vfp-hflt.tar.gz

```
sudo tar zxvf jdk-8u172-linux-arm32-vfp-hflt.tar.gz -C /opt
sudo update-alternatives --install "/usr/bin/java" "java" "/opt/jdk1.8.0_172/bin/java" 1 
sudo update-alternatives --install "/usr/bin/javac" "javac" "/opt/jdk1.8.0_172/bin/javac" 1 
java -version
sudo update-alternatives --config java
```

and choose the version you just installed.

* Update JAVA_HOME path as well

````
nano ~/.bashrc
````
add those lines 
````
export JAVA_HOME="/opt/jdk1.8.0_172"
export PATH=$PATH:$JAVA_HOME/bin
````
Save file and re-login.

## Install maven
(full instructions at https://xianic.net/2015/02/21/installing-maven-on-the-raspberry-pi/)
````
cd ~
wget http://www.mirrorservice.org/sites/ftp.apache.org/maven/maven-3/3.2.5/binaries/apache-maven-3.2.5-bin.tar.gz
cd /opt
sudo tar -xzvf /home/pi/apache-maven-3.2.5-bin.tar.gz
sudoedit /etc/profile.d/maven.sh
````
add those lines 
````
export M2_HOME=/opt/apache-maven-3.2.5
export PATH=$PATH:$M2_HOME/bin
````
Save file and re-login.
````
mvn -version
````
## Get imagej-server
Clone the imagej-server repo
````
git clone https://github.com/imagej/imagej-server.git
cd imagej-server
mvn -Pexec
````
It takes a while to build, when it's done, open clients/web/index.html in your web browser.

Some tests are failing but the server starts and seems to works.

## Trying the Python wrapper.

* Install from Pypi (https://pypi.python.org/pypi/imagej) using:
```
pip install imagej
```
This, however does not come with the example program "usage.py". 

* Get it by cloning repo from github:
```
git clone https://github.com/imagej/imagej.py.git
cd imagej.py/
````
I had to adjust a path to match a test image on my Pi.
````
nano usage.py
````
Look for the following line 
````
#load an image.
img_in = ij.upload('../../src/test/resources/imgs/about4.tif')
````
And update absolute path to match a test image on your system.

Save and exit nano

````
python usage.py
````

## Note
The following line 
```
ij.retrieve(img_out, format='png', dest='/tmp')
```
retrieves the result image and saves it in the temp folder with a unique name, so when testing repeatedely, it will slowly fill your temp folder.
I added these lines to usage.py that renames and moves the output image to a given location on my Desktop, overwriting the last result.

````
import os
...
ij.retrieve(img_out, format='png', dest='/tmp')
name = img_out.split(':')[1]
os.rename('/tmp/'+name+'.png','/home/pi/Desktop/images/result.png')
````







