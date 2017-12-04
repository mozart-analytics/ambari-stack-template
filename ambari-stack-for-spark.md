# Installing Spark with Ambari

**[Spark, Hadoop, Ambari, Ambari Stack]**

By: **Abdiel Aviles**

*A while ago I wrote about how to build an Ambari Stack for your custom apps. In that article I mentioned I had implemented a stack for Spark. So, as expected, some people showed interest on me sharing that code. Unfortunately I cannot do that, but I might re-implement that solution in the near future. What I can do in the mean time is share some notes on how to do it.*

Before going any further, please read my previous blog on [how to implement custom Ambari Stacks](http://mozartanalytics.com/how-to-create-a-software-stack-for-ambari/). Once you feel you get it, come back.

Since the last time I looked, there were 3 ways of running Spark: standalone, YARN, and Hadoop. There is no point in focusing on the standalone if you are doing this through Ambari, so I will focus on Hadoop. To run using Yarn on your Ambari cluster there's a little change to be made but I'll talk about it if anyone asks for it.

If you recall my blog, an Ambari Stack consists of various python scripts that perform various tasks. One of them is to install your app. There will be a specific script that installs your app in the slave nodes and another specific script that installs your app in the master node. The most important of those 2 scripts is the installation in the master node. The installation in the slave nodes is exactly the same but it skips some commands done with HDFS.

Another thing that will make it easier to install Spark is to provide a package for Spark. That is either an RPM or a DEB, depending on your platform. When I created the Spark Stack there was no Spark RPM nor DEB package, so I had to create the RPM myself and publish it locally.

### Pre-Work:

1. Create an RPM or DEB package (unless there is a publicly available RPM/DEB for Spark)
2. Publish locally
3. Install your local repo in your master and slaves

### Installation (this is what goes inside the python installation script):

1. Install Spark package (this is done through a simple method provided by Ambari that will itself call `yum` or `apt-get`)
2. Create spark user and group
3. Create the `spark_env.sh` file
4. Create the `slaves` file
5. Create the `metric.properties` file (optional: this is to publish metrics to ganglia)
6. Create the `spark-defaults.conf` file
7. Create the `HDFS:/user/spark/share/lib` directory (only @ master)
8. Give ownership of the previous HDFS dir to the Spark user (only @ master)
9. Copy Spark assembly libraries from local installation dir to the previous HDFS dir (only @ master; only for YARN)
10. Publish Master's public key to all slaves... this is hard :) but critical. Spark's Master will execute commands in the slave through SSH.

And that is how you install Spark with Ambari. The Ambari/Hortonworks people have been promising Spark for a long time but I suspect they are holding off due to step #10. Publishing the keys is not as easy as it sounds. It would be way easier if one of 2 things happen. 1- Ambari implements a safe mechanism to create users and register keys, or 2- Spark changes its topology to allow the execution of commands from Ambari Server instead of Spark's Master node. But then again, that's my guess.

Please feel free to comment if you think I got something wrong. As soon as I implement this again, I'll post it. Stay tuned.