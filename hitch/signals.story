Stop on signals:
  based on: icommandlib
  description: |
    When a SIGTERM is received, icommandlib should SIGKILL its
    process and subprocesses.
  given:
    files:
      child.py: |
        import os
        import time
        
        # Write out pid of this process so we can check if it is still alive
        with open("child.pid", "w") as handle:
            handle.write(str(os.getpid()))

        # Infinite loop. This misbehaving processs needs a kill -9 to die!
        while True:
            time.sleep(1)
      parent.py: |
        import os
        import sys
        import time
        import signal
        import subprocess
        
        # Write out pid of this process so we can check if it is still alive
        with open("parent.pid", "w") as handle:
            handle.write(str(os.getpid()))
        
        # Run child.py with the same python used to run parent.py
        subprocess.call([sys.executable, "child.py"])
        
        # Infinite loop. This misbehaving processs needs a kill -9 to die!
        while True:
            time.sleep(1)
            
    setup: |
      from icommandlib import ICommand
      from commandlib import python
      import os
      
    code: |
      ICommand(python("parent.py")).run().wait_for_successful_exit()
  with:
    signal: SIGTERM
  steps:
  - Start code
  - Pause for half a second
  - Send signal and wait for finish: (( signal ))
  - Processes not alive:
      from_filenames:
      - parent.pid
      - child.pid
  
  variations:
    sigint:
      with:
        signal: SIGINT
    sigterm:
      with:
        signal: SIGTERM
