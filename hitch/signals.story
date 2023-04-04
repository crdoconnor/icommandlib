#Stop on signals:
  #based on: icommandlib
  #about: |
    #When a SIGTERM is received, icommandlib should SIGKILL its
    #process and subprocesses.
  #given:
    #files:
      #child.py: |
        #import os
        #import time
        
        ## Write out pid of this process so we can check if it is still alive
        #with open("child.pid", "w") as handle:
            #handle.write(str(os.getpid()))
        
        ## Infinite loop. This misbehaving processs needs a kill -9 to die!
        #while True:
            #time.sleep(1)
      #parent.py: |
        #import os
        #import sys
        #import time
        #import signal
        #import subprocess
        
        ## How should I die?
        #signal_code = int(os.getenv("HOW_TO_DIE"))

        ## Write out pid of this process so we can check if it is still alive
        #pid = os.getpid()
        #with open("parent.pid", "w") as handle:
            #handle.write(str(pid))
        
        ## Run child.py with the same python used to run parent.py
        #process = subprocess.Popen([sys.executable, "child.py"])
        
        #time.sleep(1)

        ## this can't work
        #os.kill(pid, int(signal_code))
        
        #while True:
            #time.sleep(1)
            
    #setup: |
      #from icommandlib import ICommand
      #from commandlib import python
      
    #code: |
      #command = ICommand(python("parent.py"))
      #proc = command.run()
      #proc.wait_for_successful_exit()
  
  #variations:
    #sigint:
      #given:
        #signal: SIGINT
    #sigterm:
      #given:
        #signal: SIGTERM
        
  #steps:
  #- Run code
  #- Processes not alive:
      #from_filenames:
      #- parent.pid
      #- child.pid
