from hitchstory import StoryCollection, GivenDefinition, GivenProperty, validate
from hitchstory import InfoDefinition, InfoProperty
from hitchstory import BaseEngine, no_stacktrace_for, HitchStoryException
from hitchrun import expected, DIR
from commandlib import Command, CommandError
from pathquery import pathquery
from strictyaml import MapPattern, Map, Str, Float, Seq, Bool
from hitchrunpy import HitchRunPyException, ExamplePythonCode, ExpectedExceptionMessageWasDifferent
from commandlib import python
import hitchpylibrarytoolkit
from templex import Templex
import signal


class Engine(BaseEngine):
    given_definition = GivenDefinition(
        files=GivenProperty(MapPattern(Str(), Str())),
        variables=GivenProperty(MapPattern(Str(), Str())),
        python_version=GivenProperty(Str()),
        setup=GivenProperty(Str()),
        code=GivenProperty(Str()),
    )

    info_definition = InfoDefinition(
        known_failure=InfoProperty(Bool()),
    )

    def __init__(self, pathgroup, settings):
        self.path = pathgroup
        self.settings = settings

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

        self.path.key.joinpath("code_that_does_things.py").copy(self.path.state)

        self.python = hitchpylibrarytoolkit.project_build(
            "icommandlib",
            self.path,
            self.given["python version"],
        ).bin.python

        self.example_py_code = ExamplePythonCode(
            self.python, self.path.state,
        ).with_setup_code(
            self.given.get('setup', '')
        ).with_code(
            self.given.get('code', '')
        ).with_timeout(4.0)

    @no_stacktrace_for(HitchRunPyException)
    def run_code(self):
        self.result = self.example_py_code.run()

    @no_stacktrace_for(HitchRunPyException)
    def start_code(self):
        self.running_python = self.example_py_code.running_code()

    def pause_for_half_a_second(self):
        import time
        time.sleep(0.5)

    def send_signal_and_wait_for_finish(self, signal_name):
        SIGNAL_NAMES_TO_NUMBERS = {
            name: getattr(signal, name) for name in dir(signal)
            if name.startswith('SIG') and '_' not in name
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
                exception_type = exception_type['in python 2']\
                    if self.given['python version'].startswith("2")\
                    else exception_type['in python 3']

        if message is not None:
            if not isinstance(message, str):
                differential = True
                message = message['in python 2']\
                    if self.given['python version'].startswith("2")\
                    else message['in python 3']

        try:
            result = self.example_py_code.expect_exceptions().run()
            result.exception_was_raised(exception_type, message)
        except ExpectedExceptionMessageWasDifferent as error:
            if self.settings.get("overwrite artefacts") and not differential:
                self.current_step.update(message=error.actual_message)
            else:
                raise

    @validate(from_filenames=Seq(Str()))
    def processes_not_alive(self, from_filenames=None):
        still_alive = []
        for from_filename in from_filenames:
            import psutil
            pid = int(self.path.state.joinpath(from_filename).bytes().decode('utf8').strip())
            try:
                proc = psutil.Process(pid)
                proc.kill()
                still_alive.append(from_filename)
            except psutil.NoSuchProcess:
                pass
        if len(still_alive) > 0:
            raise Exception("Processes from {0} still alive.".format(', '.join(still_alive)))

    def touch_file(self, filename):
        self.path.state.joinpath(filename).write_text("\nfile touched!", append=True)

    def _will_be(self, content, text, reference, changeable=None):
        if text is not None:
            if content.strip() == text.strip():
                return
            else:
                raise RuntimeError("Expected to find:\n{0}\n\nActual output:\n{1}".format(
                    text,
                    content,
                ))

        artefact = self.path.key.joinpath(
            "artefacts", "{0}.txt".format(reference.replace(" ", "-").lower())
        )
        text = artefact.text()

        if not artefact.exists():
            artefact.write_text(content)
        else:
            if self.settings.get('overwrite artefacts'):
                if artefact.bytes().decode('utf8') != content:
                    artefact.write_text(content)
            else:
                Templex(text).assert_match(content)

    def file_contents_will_be(self, filename, text=None, reference=None, changeable=None):
        output_contents = self.path.state.joinpath(filename).bytes().decode('utf8')
        self._will_be(output_contents, text, reference, changeable)

    def output_will_be(self, text=None, reference=None, changeable=None):
        output_contents = self.path.state.joinpath("output.txt").bytes().decode('utf8')
        self._will_be(output_contents, text, reference, changeable)

    @validate(seconds=Float())
    def sleep(self, seconds):
        import time
        time.sleep(float(seconds))

    def on_success(self):
        if self.settings.get("overwrite artefacts"):
            self.new_story.save()


@expected(HitchStoryException)
def bdd(*words):
    """
    Run story in BDD mode that matches keywords (e.g. tdd wait finished)
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {"overwrite artefacts": True})
    ).shortcut(*words).play()


def regression():
    """
    Run all stories.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {})
    ).only_uninherited().filter(
        lambda story: not story.info.get('known_failure')
    ).ordered_by_name().play()


def rewrite():
    """
    Run all stories and rewrite any with different output.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {"overwrite artefacts": True})
    ).only_uninherited().ordered_by_name().play()


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "icommandlib"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()


@expected(CommandError)
def doctest(version="3.5.0"):
    Command(DIR.gen.joinpath("py{0}".format(version), "bin", "python"))(
        "-m", "doctest", "-v", DIR.project.joinpath("icommandlib", "utils.py")
    ).in_dir(DIR.project.joinpath("icommandlib")).run()


def rerun(version="3.5.0"):
    """
    Rerun last example code block with specified version of python.
    """
    Command(DIR.gen.joinpath("py{0}".format(version), "bin", "python"))(
        DIR.gen.joinpath("state", "examplepythoncode.py")
    ).in_dir(DIR.gen.joinpath("state")).run()


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("icommandlib"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")
