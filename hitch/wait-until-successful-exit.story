Wait until successful exit:
  based on: icommandlib
  about: |
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
          process = ICommand(python("successful_exit.py")).run()
          process.wait_for_successful_exit()

          with open("finalscreenshot.txt", "w") as handle:
              handle.write(process.screenshot())

          assert process.exit_code == 0, process.exit_code
      steps:
      - Run code
      - File contents should be:
          filename: finalscreenshot.txt
          stripped: hello
          height: 24
          width: 80

    Unsuccessful exit:
      given:
        code: |
          ICommand(python("unsuccessful_exit.py")).run().wait_for_successful_exit()
      steps:
      - Raises exception:
          exception type: icommandlib.exceptions.ExitWithError
          message: |-
            Process exited with non-zero exit code 255. Output:
            something went wrong!
