Kill:
  based on: icommandlib
  description: |
    When an icommand is run, it is run in a separate process group. When it is killed,
    the entire process group is killed.
    
    For ordinary processes this changes nothing.
    
    For processes that start child processes this means that their child processes
    and their child processes are killed.
  preconditions:
    files:
      child.py: |
        # Write out pid of this process so we can check if it is still alive
        import os
        
        with open("child.pid", "w") as handle:
            handle.write(str(os.getpid()))

        # Infinite loop. This misbehaving processs needs a kill -9 to die!
        while True:
            pass
      parent.py: |
        import os
        import sys
        import subprocess
        
        # Write out pid of this process so we can check if it is still alive
        with open("parent.pid", "w") as handle:
            handle.write(str(os.getpid()))
        
        # Run child.py with the same python used to run parent.py
        subprocess.call([sys.executable, "child.py"])
        
        # Infinite loop. This misbehaving processs needs a kill -9 to die!
        while True:
            pass
    setup: |
      from icommandlib import ICommand
      from commandlib import python
      import time
    code: |
      process = ICommand(python("parent.py")).run()
      time.sleep(0.5)
      process.kill()
  scenario:
    - Run code
    - Processes not alive:
        from filenames:
        - parent.pid
        - child.pid
