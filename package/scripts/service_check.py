import sys
from resource_management import *

class DummyServiceCheck(Script):

    def service_check(self, env):
        print 'Service Check'
        Execute( "ls -la",
            tries     = 3,
            try_sleep = 5,
            user = params.smoke_test_user,
            logoutput = True
        )

if __name__ == "__main__":
  DummyServiceCheck().execute()