Process properties:
  docs: process-properties
  based on: icommandlib
  about: |
    Process properties can be queried at any time
    and should reflect the current status of the process.
  given:
    files:
      waiting.py: |
        import time
        
        time.sleep(0.1)
        print("DONE!")
    setup: |
      from icommandlib import ICommand, UnexpectedExit
      from commandlib import python
      import time

      process = ICommand(python("waiting.py")).run()
  variations:
    Running:
      about: |
        The 'running' property will report whether the
        status is currently running or not.
      given:
        code: |
          assert process.running == True
          time.sleep(0.2)
          assert process.running == False
      steps:
        - Run code
        
    Exit code:
      about: |
        exit_code property will be None while the process
        is running, and contain the exit code once finished.
      given:
        code: |
          assert process.exit_code is None
          time.sleep(0.2)
          assert process.exit_code == 0, process.exit_code
      steps:
        - Run code
        
        
    Process ID:
      about: |
        pid property contains the pid of the process while
        the process is running, and None once it is finished.
        
        If you try and get .pid after the process has finished
        of its own accord, without having explicitly waited
        for it, it will raise an UnexpectedExit exception.
      given:
        code: |
          assert process.pid is not None
          time.sleep(0.2)
          
          try:
              now_finished = process.pid
          except UnexpectedExit:
              pass

          assert process.pid is None, process.pid
      steps:
        - Run code
