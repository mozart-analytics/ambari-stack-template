from resource_management import *
import sys

class DummyMaster(Script):
    def install(self, env):
        print 'Install the Dummy Master.'

        # Load the all configuration files
        config = Script.get_config()
        # Bind to a local variable
        dummy_user = config['configurations']['my-config-env']['dummy_user']

        # Install packages
        self.install_packages(env)

        # Create a new user and group
        Execute( format("groupadd -f {dummy_user}") )
        Execute( format("id -u {dummy_user} &>/dev/null || useradd -s /bin/bash {dummy_user} -g {dummy_user}") )

        ### Continue installing and configuring your service

        print 'Installation complete.'

    def stop(self, env):
        print 'Stop the Dummy Master'
        # Stop your service

        #Since we have not installed a real service, there is no PID file created by it.
        #Therefore we are going to artificially remove the PID.
        Execute( "rm -f /tmp/dummy_master.pid" )

    def start(self, env):
        print 'Start the Dummy Master'
        # Reconfigure all files
        # Start your service

        #Since we have not installed a real service, there is no PID file created by it.
        #Therefore we are going to artificially create the PID.
        Execute( "touch /tmp/dummy_master.pid" )

    def status(self, env):
        print 'Status of the Dummy Master'
        dummy_master_pid_file = "/tmp/dummy_master.pid"
        #check_process_status(dummy_master_pid_file)
        Execute( format("cat {dummy_master_pid_file}") )
        pass

if __name__ == "__main__":
    DummyMaster().execute()
