# How to create a software Stack for Ambari 1.7.0

**[Hadoop, Ambari, Ambari Stack]**

By: **Abdiel Aviles**

*In this post I will try to give a more detailed explanation on how to build a customized Ambari Stack. I've decided to share all that I've learned through reading Ambari Server's source code. This is my way of giving back to the community.*

# What is Ambari? and What is an Ambari Stack?
If you are reading this it is because you already know what Ambari is and what Ambari Stacks are. But still let's refresh our memories.

What is Ambari, from the Ambari website:

>"The Apache Ambari project is aimed at making Hadoop management simpler by developing software for provisioning, managing, and monitoring Apache Hadoop clusters. Ambari provides an intuitive, easy-to-use Hadoop management web UI backed by its RESTful APIs."

In simpler words, Ambari is a Resource Management Platform. That is, you have your cluster and it lets you install and monitor distributed apps (for Hadoop), easily.

As of this writing, Ambari provides an explanation to what and [how to build custom Ambari Stacks](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=38571133). If that link was good enough for you, great! you are done. But it was not as clear for me and that's why I took the time to go through their code and existing stacks. After many many hours I ended up developing an Ambari Stack for Spark 1.2. Preparing a stack for Spark is not as straightforward as it is the case for other services, mostly because of it's topology (if you have specific questions regarding a Spark Stack shoot me an email). But that is not what I'm going to show you here, instead I'm going to give you a template source code that you can use with your apps. That being said, keep in mind that this article is written from a "hacker" perspective.

Oh yes, what is a Stack? What I understand is that an Ambari Stack is akin to an RPM or a DEB. It is simply a service installation package for distributed clusters managed by Ambari. I chosed the word "service" since that is how Ambari refers to the apps it manages. HDFS is installed from a stack, HBASE is installed from a stack, Zookeeper is installed from a stack, Storm is .... well you get the idea.

Since version 1.7.0 they allow you to install custom Stacks or services from the Ambari Web UI. This is not the same as Ambari Views and I might spare a blog later for this.

> NOTE: Download the source code from the link found at the end of this post. OPEN all files and refer to them as we go through the sections.

# <a name="structure"></a>Folder and File Structure
This is how the (simplified) folder structure, of an Ambari Stack definition, looks like.

```
   metainfo.xml
   metrics.json
   |_ configuration
      my-config-env.xml
   |_ package
      |_scripts
        master.py
        slave.py
        client.py
        service_check.py
        params.py
```

The most important file here is `metainfo.xml` and it defines what the stack is, how to install it, what commands are available, and what are the handles (the scripts that do the work). Let's wee what's inside it.

```xml
<?xml version="1.0"?>
<metainfo>
    <schemaVersion>2.0</schemaVersion>
    <services>
        <service>
            <name>DUMMY_APP</name>
            <displayName>My Dummy APP</displayName>
            <comment>This is a distributed app.</comment>
            <version>0.1</version>
            <components>
                <component>
                    <name>DUMMY_MASTER</name>
                    <displayName>Dummy Master Component</displayName>
                    <category>MASTER</category>
                    <cardinality>1</cardinality>
                    <commandScript>
                        <script>scripts/master.py</script>
                        <scriptType>PYTHON</scriptType>
                        <timeout>600</timeout>
                    </commandScript>
                    <customCommands>
                        <customCommand>
                            <name>MYCOMMAND</name>
                            <commandScript>
                                <script>scripts/mycustomcommand.py</script>
                                <scriptType>PYTHON</scriptType>
                                <timeout>600</timeout>
                            </commandScript>
                        </customCommand>
                    </customCommands>
                </component>
                <component>
                    <name>DUMMY_SLAVE</name>
                    <displayName>Dummy Slave Component</displayName>
                    <category>SLAVE</category>
                    <cardinality>1+</cardinality>
                    <commandScript>
                        <script>scripts/slave.py</script>
                        <scriptType>PYTHON</scriptType>
                        <timeout>600</timeout>
                    </commandScript>
                </component>
                <component>
                    <name>DUMMY_CLIENT</name>
                    <displayName>Dummy Client Component</displayName>
                    <category>CLIENT</category>
                    <cardinality>0+</cardinality>
                    <commandScript>
                        <script>scripts/client.py</script>
                        <scriptType>PYTHON</scriptType>
                        <timeout>600</timeout>
                    </commandScript>
                </component>
            </components>
            <osSpecifics>
                <osSpecific>
                    <osFamily>any</osFamily>
                    <packages>
                        <package>
                            <name>imagemagick</name>
                        </package>
                        <package>
                            <name>dummy-app</name>
                        </package>
                    </packages>
                </osSpecific>
            </osSpecifics>
            <commandScript>
                <script>scripts/service_check.py</script>
                <scriptType>PYTHON</scriptType>
                <timeout>300</timeout>
            </commandScript>
            <requiredServices>
                <service>HDFS</service>
                <service>YARN</service>
            </requiredServices>
            <configuration-dependencies>
                <config-type>my-config-env</config-type>
            </configuration-dependencies>
        </service>
    </services>
</metainfo>
```

This is a good enough definition for what I'm going to show you in this post. But keep in mind that there are other configurations. From experience, you are better off browsing the [repo](https://github.com/apache/ambari/tree/release-1.7.0/ambari-server/src/main/resources/stacks/HDP) and looking at the existing stacks.

Next, I'll describe the interesting parts and what they do, skipping the obvious tags like `name`, `description` and so on.

# Service

This is where you define what you are installing. As you can see we are able to define multiple services in a single definition. I have never defined more than a single service but it might be useful.

```xml
<service>
    <name>DUMMY_APP</name>
    <displayName>My Dummy APP</displayName>
    <comment>This is a distributed app.</comment>
    <version>0.1</version>
    <components>
    ...
    </components>
    <osSpecifics>
    ...
    </osSpecifics>
    <commandScript>
    ...
    </commandScript>
    <requiredServices>
    ...
    </requiredServices>
    <configuration-dependencies>
    ...
    </configuration-dependencies>
</service>
```

Skipping the obvious, we have `components`, `osSpecifics`, `commandScript`, `requiredServices` and `configuration-dependencies`.

### Components

The `components` block defines the topology of your distributed app. We can have `MASTER` nodes, `SLAVE` nodes and `CLIENT`'s. Ambari expects and knows how to manage this kind of distributed topology.

```xml
<component>
    <name>DUMMY_MASTER</name>
    <displayName>Dummy Master Component</displayName>
    <category>MASTER</category>
    <cardinality>1</cardinality>
    <commandScript>
        <script>scripts/master.py</script>
        <scriptType>PYTHON</scriptType>
        <timeout>600</timeout>
    </commandScript>
    <customCommands>
        <customCommand>
            <name>MYCOMMAND</name>
            <commandScript>
                <script>scripts/mycustomcommand.py</script>
                <scriptType>PYTHON</scriptType>
                <timeout>600</timeout>
            </commandScript>
        </customCommand>
    </customCommands>
</component>
```

The most important tags are `category`, `cardinality` and `commandScript`. Category dictates if your component is a `MASTER`, `SLAVE` or `CLIENT` node. Hosts (servers) could have any combination of components installed to them. Cardinality dictates how many of each components can your cluster have. In our example we **must** have 1 master, 1 or more slaves and none or more clients. The command script tag tells ambari the handle (script) for that particular component. We will discuss [these scripts later](#command_scripts).

### <a name="os_specifics"></a>OS Specifics

The `osSpecifics` tag will tell Ambari which packages/dependencies to install for this component. Ambari uses `yum` for RPM based distros and `apt-get` for debian distros (since Ambari v1.7) to manage the installation of all packages defined here.

```xml
<osSpecific>
    <osFamily>any</osFamily>
    <packages>
        <package>
            <name>imagemagick</name>
        </package>
        <package>
            <name>dummy-app</name>
        </package>
    </packages>
</osSpecific>
```

The `osFamily` tag bundles the packages to be installed on the target Linux flavor of your choice. For example you can set `redhat6`, `suse11`, `ubuntu12`, etc. Which ones exactly? I have no idea, but for version Ambari 2.0 there is a test that lists supported versions found in `org.apache.ambari.server.state.stack.OSFamilyTest`. 

The `packages` tag lists the packages to be installed by `yum` (or `apt-get`). So in our example we have `imagemagick` as part of our dependencies and that will result in the ambari-agent running a command that looks like `yum install imagemagick`. If your service or app is already bundled as an `RPM` or `DEB`, all you need to do is to add your repository to the hosts and Ambari will fetch it from there. If you do not have a packaged app, you might still be able to do your own installation through the stack handle scripts.

### <a name="command_script"></a>Command Script

The `commandScript` tag tells Ambari where to find the scripts that would manage the service. This tag can be defined in other places like the `component` tag. The scripts are Python scripts (mostly) and executed by the `ambari-agent` module. Ambari expects these scripts to contain the definition of specific methods. Let's quickly take a look at one of our scripts.

```python
import sys
from resource_management import *
class DummyMaster(Script):
    def install(self, env):
        import params
        env.set_params(params)
        print 'Install the Master'
        self.install_packages(env)
    def stop(self, env):
        print 'Stop the Master'
    def start(self, env):
        import params
        env.set_params(params)
        print 'Start the Master'
    def status(self, env):
        print 'Status of the Master'
if __name__ == "__main__":
    DummyMaster().execute()
```

If you are a python guru (I'm an ignorant) you'll breeze through this. As you can see there are various methods that match the default Ambari commands for managing the services. (**IMPORTANT:** All these scripts are run as **root**!) The ones I've used are:

- `install` - Executed only once during the service installation. The first thing you need to do here is to call the Ambari installer through `self.install_packages(env)`. Also notice that we first imported a module called params. I'll talk in more detail about [the params module later](#params). When you call the installer it will go through the [list of dependencies](#os_specifics) and install them. After this you can go ahead and add your own configurations and perform any necessary steps or commands. For example you could modify a configuration file (eg: `/etc/sysconfig/network`) if necessary.
- `start` - This command can be executed through the Ambari Web UI and it is expected of you to execute any command that would start your service. For example you can issue a `service myservice start` or `/opt/myservice/bin/start-my-service.sh` depending on how your service works. It is your responsibility to correctly implement and raise exceptions for your service. During the start process it is also desirable to re-configure the service. We will see the [configuration in more detail later](#configuration).
- `stop` - Same thing as the `start` command but now to `stop` the service.
- `status` - This command is automatically run by Ambari to learn the status of the service. Ambari provides some very useful sub-routines in order to aid in this process. I'll explain this later.

There you have it, Ambari's service handles. At least these fours subroutines are expected by Ambari and you shall always implement them. Ambari also provides a few python helper methods to execute OS level commands. The core helper methods are defined in the [`resource_management`](https://github.com/apache/ambari/blob/release-1.7.0/ambari-common/src/main/python/resource_management) package. There are various python scripts defined this package that are very useful and I recommend you to check them out one by one, specially those inside the `../resource_management/core` sub folder. Let's look at a few:

First import the dependency.

```python
from resource_management import *
```

#### Execute()
This helper method allows you to execute any binary as any user. It also provides various arguments to do re-tries, timeout, run as user, conditional checks, among other useful options. To use it you can do something as simple as:

```python
Execute( 'mkdir -P /tmp/myservice',
        logoutput = True
    )
```

The above will create the directory /tmp/myservice in the localhost and log the output internally within Ambari as well as show it on the UI.

#### ExecuteHadoop()
This one is similar to `Execute`. It is a wrapper to run the `hadoop --config` command. You would use it as:

```python
import params
ExecuteHadoop('fs -mkdir -p /tmp/myservice',
    user=params.hdfs_user,
    logoutput=True,
    conf_dir=params.hadoop_conf_dir,
    try_sleep=3,
    tries=5,
    bin_dir=params.hadoop_bin_dir
)
```

The above will create the directory `HDFS://tmp/myservice` in the Hadoop cluster. Notice that we are specifying the hdfs user, the hadoop configuration directory as well as the hadoop binaries directory. Don't worry about these, if the HDFS stack is already installed you will have access to these variables. I will go in more detail in the [Configuration Dependencies](#configuration) section.

#### format()
This method is used for string templates. It will replace local variables inside a text string. For example, the following snippet:

```python
localVar = "bar"
print format("foo {localVar} baz")
```

will print the following text : `foo bar baz`.

#### Component Status
This is one of the most important handles that should be properly defined by you. Ambari internally uses this method to display the component status and to validate before continuing various operations. For example, if you are going to delete a component from a host, Ambari will wait until the component is stopped. If this handle is not properly implemented you might never be able to remove the component.

Luckily for us, Ambari provides a convenience method that receives a PID file as an input and checks if the process is alive. Our component status check could look like the following:

```python
1    def status(self, env):
2        print 'Status of the Dummy Master'
3        dummy_master_pid_file = "/tmp/dummy_master.pid"
4        check_process_status(dummy_master_pid_file)
```

The `check_process_status()` method will exit successfully if there is a process running with the PID found inside `dummy.pid` file. If this is the case, Ambari will mark this service as alive and display on the UI. Otherwise the method exist in error and Ambari will mark it as stopped.

#### Service Status
The service status handle is different to the component status since it's purpose is to do a global service check. This method is only run at the Master node and must be invoked by the user from the Ambari Web UI. Usually we would run some command that would functionally test the service.

The code for this handle is defined in the `<commandScript>` tag owned by the `<service>` tag in the `metainfo.xml` file. In our dummy service it is defined as follows:

```xml
<commandScript>
    <script>scripts/service_check.py</script>
    <scriptType>PYTHON</scriptType>
    <timeout>300</timeout>
</commandScript>
```

#### Custom Commands

The `customCommand` tag works the same as the `commandScript` tag but it differs in that it **must** contain a method definition with the same name as the custom command specified by the tag. Custom commands are then injected into the Ambari web interface and can be executed from there. Go back to the [Command Script](#command_script) section and read through. There should be another subroutine defined (along with `start`, `stop`, etc.) with the name of the custom command you are describing here.

### Required Services
The `requiredServices` block tells Ambari which services must be installed prior to this stack/service. So in simpler terms, this are stack dependencies of stacks. For example, if your service needs HDFS and YARN to be pre-installed, then you would have something like:

```xml
<requiredServices>
    <service>HDFS</service>
    <service>YARN</service>
</requiredServices>
```

In our stack we are requiring the presence of the HDFS stack and the YARN stack. already installed in the cluster.

### <a name="configuration"></a>Configuration Dependencies

Configuration dependencies is one of the most useful features of the Ambari Stack. It allows the user to modify the service/app configuration through the Ambari Web UI. These configurations could be used from any of the subroutines defined in the command scripts. These values are defined inside an xml file. Recall from the `metainfo.xml` file shown before, there is a configuration dependency called `my-config-env`. This is telling ambari to look for a file named `<STACK_ROOT>/config/my-config-env.xml`. Inside this file we can define as many variables as we need. All of them will be available for re-definition through the Ambari Web UI. Let's look at `my-config-env.xml`:

```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
 
<configuration>
  <property>
    <name>dummy_user</name>
    <value>dummy</value>
    <description>Dummy App User Name.</description>
  </property>
  <property>
    <name>dummy_var</name>
    <value>123</value>
    <description>Dummy Variable.</description>
  </property>
</configuration>
```

We have just defined a couple of variables: `dummy_user` with a value of `dummy`, and `dummy_var` with a value of `123`. We can now use these variables from inside our scripts, and also modify them from the Ambari Web UI. For example, let's take the `install` subroutine inside the command script defined before. We need to create a new user for our Dummy Service. We could do this as follows:

```python
...
 1    def install(self, env):
 2		# Import the Resource Management package
 3		from resource_management import *
 4		# Load the all configuration files
 5		config = Script.get_config()
 6		# Bind to a local variable
 7		dummy_user = config['configurations']['my-config-env']['dummy_user']
 8
 9		print 'Install the Master.'
10		# Install packages
11		self.install_packages(env)
12
13		# Create a new user and group
14		Execute( format("groupadd -f {dummy_user}"))
15		Execute( format("useradd -s /bin/bash {dummy_user} -g {dummy_user}"))
16
17		print 'Installation complete.'
...
```

In the script above we are loading configuration variables (line `5`), installing dependencies (line `11`), creating a new group (line `14`) and a new user (line `15`). Note that we are using a few convenience methods provided by the `resource_management` package: `Script.get_config()`, `Execute()` and `format()`. The command `Script.get_config()` will load all configuration the variables that have been defined inside configuration files, and from all services. This means that you can access variables defined in other services as well as your own variables as seen in line `7`, where we bind the `dummy_user` configuration with a local variable.

#### Important Global Variables
There are other very important global variables that are useful to us. For example, during installation we might need to know who are the master and slaves nodes. This is defined during the installation wizard in the Ambari Web UI and obviously cannot be known in advance. Thankfully we can grab these values with the following snippet:

```python
# Import the Resource Management package
from resource_management import *
config = Script.get_config()

# Find the master node and the slaves list for our DUMMY_APP service
masterNode = config['clusterHostInfo']['dummy_app_master_hosts'][0]
slaveList = config['clusterHostInfo']['dummy_app_slave_hosts']
```

The `masterNode` variable now contains the FQDN name of the master node configured during installation. Similarly the `slaveList` variable contains an array with the FQDN names of the slaves nodes. It is also important to note that these variables were found from these two variables: `dummy_app_master_hosts` and `dummy_app_slave_hosts`. As you can see these variables are named after the name you assigned your service in `metainfo.xml`: **DUMMY_APP**.

There are other interesting variables you can find inside the `config` object. For example you can find the Ganglia host through `config['clusterHostInfo']['ganglia_server_host'][0]`, and in the same manner every other configuration of all installed services.

#### The role of the `start()` handle in configuring your service
The `start()` handle, as defined in the [Command Scripts](#command_script) section, must always check if configurations new configurations are in place. As a rule of thumb, always re-configure your service files when starting the service. This will ensure that your service will be up-to date when a configuration change has been made from the Ambari Web UI.s

# Installing your brand new Stack

### Copy Files
In order to install your stack, simply copy all your files to the following path in the Ambari Server host:

`/var/lib/ambari-server/resources/stacks/HDP/2.2/services/DUMMY_SERVICE`

Afterwards you must restart your ambari server with the following command:

```bash
ambari-server restart
```

Your service structure must follow the one described in the "Folder and File Structure" [section](structure).

### Installation Wizard

1. Login to Ambari Web UI,
	![Ambari Login](https://www.dropbox.com/s/z1j92xsoii4a972/ambari-login.png?dl=1)

2. From the Ambari dashboard,
	![Ambari Dashboard](https://www.dropbox.com/s/u90jqk69cmtm3pt/ambari-dash.png?dl=1)

3. Select the `Actions>Add Service`.
	![Add Service](https://www.dropbox.com/s/fqgx8lwyko8223t/ambari-add-service.png?dl=1)

4. The Installation Wizard will be shown. Select the service to be installed,
	![Wizard Select Service](https://www.dropbox.com/s/njncdaewnh1jmvz/ambari-wizard-select-service.png?dl=1)

5. Select the master node,
	![Wizard Select Master](https://www.dropbox.com/s/58x65hnvio3vgro/ambari-wizard-select-master.png?dl=1)

6. Select the slave nodes,
	![Wizard Select Slaves](https://www.dropbox.com/s/dkkz3yjt6avn2c9/ambari-wizard-select-slaves.png?dl=1)

7. Configure the service,
	![Wizard Configure](https://www.dropbox.com/s/gkp14mck1re328b/ambari-wizard-configure.png?dl=1)

8. Review the installation settings,
	![Wizard Review](https://www.dropbox.com/s/h44anpl8k099znq/ambari-wizard-summary.png?dl=1)

9. Monitor the installation,
	![Wizard Installing](https://www.dropbox.com/s/mr1ngiczr64oqm5/ambari-wizard-installing.png?dl=1)

10. Once the installation is complete, click `Next` to exit the wizard.
	![Wizard Installation Complete](https://www.dropbox.com/s/tn9rq2sxry1qc7h/ambari-wizard-installing-complete.png?dl=1)

11. Now your dashboard shows the newly added service.
	![Ambari Dashboard with Service](https://www.dropbox.com/s/fn5xsxr16mno9zx/ambari-dash-w-service.png?dl=1)

### Service Actions
Each service has an administration panel where you can monitor and control the service. Click on the service name.
	![Dummy Service](https://www.dropbox.com/s/t6nk9s2y17osupi/ambari-dummy-service.png?dl=1)

If you need to change any configuration, go into the `Configs` panel. Here you can edit the current service configurations or roll back into previous versions. Every time you edit the configurations, the service must be restarted in order to apply the changes. Recall from the ["Configuration Dependencies"](#configuration) section, that the `start()` handle will be in charge of editing the actual configuration files with these new settings.

There are various service level actions you can take through the UI.
	![Dummy Service Actions](https://www.dropbox.com/s/a3m85fj6c1z39cu/ambari-dummy-service-actions.png?dl=1)

Also, if you go to directly into the host through the `Hosts` tab, you could perform component level actions. For example you could stop just the master component of your service.
	![Dummy Service Component Actions](https://www.dropbox.com/s/oha5qzzei4i1q75/ambari-dummy-service-stop.png?dl=1)

Once an action has been performed, Ambari will automatically adjust the UI to show the current status. For example if you do a service level Stop, the UI should look like this.
	![Dummy Service Stop](https://www.dropbox.com/s/lp1ckn5to9wz2gt/ambari-dummy-service-stopped.png?dl=1)

To restart the service simply select the service level Start command.

# Wrap Up
We have seen how to describe your new service in the `metainfo.xml`. We have also seen how to install and control your service through the handles inside the command scripts. We saw how to allow for further configuration through the configuration xml files. And finally we went through the installation and control of our Dummy Service.

As any good hacker you might already be building your own distributed app in your head. I hope this was helpful and feel free to drop a line if you can't figure out how to do something else. There were many many other details that were not covered in this blog. Our aim is to present a simple but yet useful example that would bootstrap your Ambari Stack development.



### About Us
_At Mozart Analytics LLC, we ask your data how to make you more money._ We specialize in collecting and analyzing huge amounts of data from many sources, to provide real-time insights to our customers as a tool for aiding them in making informed and accurate decisions.

### Source Code
Fork the code from [https://github.com/mozart-analytics/ambari-stack-template](https://github.com/mozart-analytics/ambari-stack-template)
