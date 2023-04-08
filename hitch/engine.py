from hitchstory import StoryCollection, BaseEngine, validate
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from strictyaml import Str, Map, Optional, Enum, MapPattern, Int, Bool, Seq, Float
from hitchstory import no_stacktrace_for, Failure
from hitchrunpy import (
    ExamplePythonCode,
    HitchRunPyException,
    ExpectedExceptionMessageWasDifferent,
)
from commandlib import Command
from templex import Templex
from path import Path
import psutil
import signal
import time

class Engine(BaseEngine):
    given_definition = GivenDefinition(
        files=GivenProperty(
            MapPattern(Str(), Str()),
            inherit_via=GivenProperty.OVERRIDE,
        ),
        variables=GivenProperty(
            MapPattern(Str(), Str()),
            inherit_via=GivenProperty.OVERRIDE,
        ),
        python_version=GivenProperty(Str()),
        setup=GivenProperty(Str()),
        code=GivenProperty(Str()),
        signal=GivenProperty(Str()),
    )

    info_definition = InfoDefinition(
        known_failure=InfoProperty(Bool()),
    )

    def __init__(self, paths, python_path, rewrite=False):
        self.path = paths
        self._python_path = python_path
        self._rewrite = rewrite

    def set_up(self):
        self.path.state = self.path.gen.joinpath("state")
        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        for filename, text in self.given.get("files", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().mkdir()
            filepath.write_text(str(text))
            filepath.chmod("u+x")

        for filename, text in self.given.get("variables", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().mkdir()
            filepath.write_text(str(text))

        if "signal" in self.given:
            SIGNAL_NAMES_TO_NUMBERS = {
                name: getattr(signal, name).value
                for name in dir(signal)
                if name.startswith("SIG") and "_" not in name
            }
            self._signal = SIGNAL_NAMES_TO_NUMBERS[self.given["signal"]]
        else:
            self._signal = None

        self.python = Command(self._python_path)

        self.example_py_code = (
            ExamplePythonCode(
                self.python,
                self.path.state,
            )
            .with_setup_code(self.given.get("setup", ""))
            .with_code(self.given.get("code", ""))
            .with_timeout(4.0)
            .in_dir(self.path.state)
        )

    @no_stacktrace_for(HitchRunPyException)
    def run_code(self):
        self.result = self.example_py_code.with_env(HOW_TO_DIE=self._signal).run()

    @no_stacktrace_for(HitchRunPyException)
    def start_code(self):
        self.running_python = self.example_py_code.running_code()

    def pause_for_half_a_second(self):
        time.sleep(0.5)

    def send_signal_and_wait_for_finish(self, signal_name):
        SIGNAL_NAMES_TO_NUMBERS = {
            name: getattr(signal, name)
            for name in dir(signal)
            if name.startswith("SIG") and "_" not in name
        }
        self.running_python.iprocess.psutil._send_signal(
            int(SIGNAL_NAMES_TO_NUMBERS[signal_name])
        )
        self.running_python.iprocess.wait_for_finish()

    @no_stacktrace_for(HitchRunPyException)
    @validate(
        exception_type=Map({"in python 2": Str(), "in python 3": Str()}) | Str(),
        message=Map({"in python 2": Str(), "in python 3": Str()}) | Str(),
    )
    def raises_exception(self, exception_type=None, message=None):
        """
        Expect an exception.
        """
        differential = False

        if exception_type is not None:
            if not isinstance(exception_type, str):
                differential = True
                exception_type = (
                    exception_type["in python 2"]
                    if self.given["python version"].startswith("2")
                    else exception_type["in python 3"]
                )

        if message is not None:
            if not isinstance(message, str):
                differential = True
                message = (
                    message["in python 2"]
                    if self.given["python version"].startswith("2")
                    else message["in python 3"]
                )

        try:
            result = self.example_py_code.expect_exceptions().run()
            result.exception_was_raised(exception_type, message)
        except ExpectedExceptionMessageWasDifferent as error:
            if self._rewrite and not differential:
                self.current_step.update(message=error.actual_message)
            else:
                raise

    @validate(from_filenames=Seq(Str()))
    def processes_not_alive(self, from_filenames=None):
        still_alive = []
        for from_filename in from_filenames:
            pid = int(self.path.state.joinpath(from_filename).text().strip())

            try:
                status = psutil.Process(pid).status()
                if status == "zombie":
                    pass
                else:
                    still_alive.append(from_filename)
            except psutil.NoSuchProcess:
                pass
        if len(still_alive) > 0:
            raise Failure(
                "Processes from {0} still alive.".format(", ".join(still_alive))
            )

    def touch_file(self, filename):
        self.path.state.joinpath(filename).write_text("\nfile touched!", append=True)

    @validate(height=Int(), width=Int())
    def file_contents_should_be(self, filename, stripped, height, width):
        output_contents = self.path.state.joinpath(filename).text()

        output_stripped = "\n".join(
            line.rstrip() for line in output_contents.split("\n") if line != ""
        ).rstrip()

        output_height = len(output_contents.split("\n"))
        output_width = max(len(line) for line in output_contents.split("\n"))

        try:
            Templex(stripped).assert_match(output_stripped)
            assert output_height == height
            assert output_width == width
        except AssertionError:
            if self._rewrite:
                self.current_step.update(stripped=output_stripped)
                self.current_step.update(height=output_height)
                self.current_step.update(width=output_width)
            else:
                raise

    @validate(seconds=Float())
    def sleep(self, seconds):
        time.sleep(float(seconds))

    def tear_down(self):

        if Path("/tmp/q").exists():
            print(Path("/tmp/q").text())

    def on_success(self):
        if self._rewrite:
            self.new_story.save()
