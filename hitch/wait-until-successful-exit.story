Wait until successful exit:
  based on: icommandlib
  description: |
    Wait until exit with status code 0.
  given:
    files:
      successful_exit.py: |
        import sys
        sys.stdout.write("hello")
        sys.stdout.flush()
      unsuccessful_exit.py: |
        import sys
        sys.stderr.write("something went wrong!")
        sys.stderr.flush()
        sys.exit(255)
    setup: |
      from icommandlib import ICommand
      from commandlib import python
  variations:
    Without errors:
      given:
        code: |
          finished_process = ICommand(python("successful_exit.py")).run().wait_for_successful_exit()

          with open("finalscreenshot.txt", "w") as handle:
              handle.write(finished_process.screenshot)
          
          assert finished_process.exit_code == 0
      steps:
        - Run code
        - File contents will be:
            filename: finalscreenshot.txt
            reference: finalscreenshot

    Unsuccessful exit:
      given:
        code: |
          finished_process = ICommand(python("unsuccessful_exit.py")).run().wait_for_successful_exit()
      steps:
        - Raises exception:
            exception type: icommandlib.exceptions.ExitWithError
            message: |-
              Process had non-zero exit code '255'. Output:
              something went wrong!
