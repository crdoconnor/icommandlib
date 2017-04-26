from hitchstory import StoryCollection, StorySchema, BaseEngine, exceptions, validate
from hitchrun import Path, hitch_maintenance, expected
from commandlib import Command
from pathquery import pathq
from strictyaml import MapPattern, Str, Int
from commandlib import python
import hitchpython
import hitchserve
import strictyaml
import hitchtest


KEYPATH = Path(__file__).abspath().dirname()
git = Command("git").in_dir(KEYPATH.parent)


class Paths(object):
    def __init__(self, keypath):
        self.keypath = keypath
        self.project = keypath.parent
        self.state = keypath.parent.joinpath("state")
        self.engine = keypath


class Engine(BaseEngine):
    schema = StorySchema(
        preconditions={
            "files": MapPattern(Str(), Str()),
            "variables": MapPattern(Str(), Str()),
            "python version": Str(),
        },
        params={
            "python version": Str(),
        },
    )

    def __init__(self, keypath, settings):
        self.path = Paths(keypath)
        self.settings = settings

    def set_up(self):
        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        for filename, text in self.preconditions.get("files", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().mkdir()
            filepath.write_text(str(text))

        for filename, text in self.preconditions.get("variables", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().mkdir()
            filepath.write_text(str(text))

        self.path.engine.joinpath("code_that_does_things.py").copy(self.path.state)

        self.python_package = hitchpython.PythonPackage(
            self.preconditions.get('python_version', self.preconditions['python version'])
        )
        self.python_package.build()

        self.pip = self.python_package.cmd.pip
        self.python = self.python_package.cmd.python

        with hitchtest.monitor([self.path.keypath.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.keypath).run()

        self.pip("uninstall", "icommandlib", "-y").ignore_errors().run()
        self.pip("install", ".").in_dir(self.path.project).run()

        self.services = hitchserve.ServiceBundle(
            str(self.path.project),
            startup_timeout=8.0,
            shutdown_timeout=1.0
        )

        self.services['IPython'] = hitchpython.IPythonKernelService(self.python_package)

        self.services.startup(interactive=False)
        self.ipython_kernel_filename = self.services['IPython'].wait_and_get_ipykernel_filename()
        self.ipython_step_library = hitchpython.IPythonStepLibrary()
        self.ipython_step_library.startup_connection(self.ipython_kernel_filename)

        self.run("import os")
        self.run("from path import Path")
        self.run("os.chdir('{}')".format(self.path.state))
        self.run("from code_that_does_things import *")

        for var, value in self.preconditions.get("variables", {}).items():
            self.run("{0} = Path('{0}').bytes().decode('utf8')".format(var))

    def run(self, command):
        self.ipython_step_library.run(command)

    def assert_true(self, command):
        self.ipython_step_library.assert_true(command)

    def exception_is_raised(self, command, exception):
        self.ipython_step_library.assert_exception(command, exception)

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

        artefact = self.path.engine.joinpath(
            "artefacts", "{0}.txt".format(reference.replace(" ", "-").lower())
        )

        from simex import DefaultSimex
        simex = DefaultSimex(
            open_delimeter="(((",
            close_delimeter=")))",
        )

        simex_contents = content

        if changeable is not None:
            for replacement in changeable:
                simex_contents = simex.compile(replacement).sub(replacement, simex_contents)

        if not artefact.exists():
            artefact.write_text(simex_contents)
        else:
            if self.settings.get('overwrite artefacts'):
                artefact.write_text(simex_contents)
                self.services.log(content)
            else:
                if simex.compile(artefact.bytes().decode('utf8')).match(content) is None:
                    raise RuntimeError("Expected to find:\n{0}\n\nActual output:\n{1}".format(
                        artefact.bytes().decode('utf8'),
                        content,
                    ))
                else:
                    self.services.log(content)

    def file_contents_will_be(self, filename, text=None, reference=None, changeable=None):
        output_contents = self.path.state.joinpath(filename).bytes().decode('utf8')
        self._will_be(output_contents, text, reference, changeable)

    def output_will_be(self, text=None, reference=None, changeable=None):
        output_contents = self.path.state.joinpath("output.txt").bytes().decode('utf8')
        self._will_be(output_contents, text, reference, changeable)

    @validate(seconds=Int())
    def sleep(self, seconds):
        import time
        time.sleep(int(seconds))

    def shell(self):
        if hasattr(self, 'services'):
            self.services.start_interactive_mode()
            import sys
            import time
            from os import path
            from subprocess import call
            time.sleep(0.5)
            if path.exists(path.join(
                path.expanduser("~"), ".ipython/profile_default/security/",
                self.ipython_kernel_filename)
            ):
                call([
                        sys.executable, "-m", "IPython", "console",
                        "--existing",
                        path.join(
                            path.expanduser("~"),
                            ".ipython/profile_default/security/",
                            self.ipython_kernel_filename
                        )
                    ])
            else:
                call([
                    sys.executable, "-m", "IPython", "console",
                    "--existing", self.ipython_kernel_filename
                ])
            self.services.stop_interactive_mode()

    def on_failure(self):
        self.shell()

    def tear_down(self):
        """Clean out the state directory."""
        try:
            self.shutdown_connection()
        except:
            pass
        if hasattr(self, 'services'):
            self.services.shutdown()


@expected(strictyaml.exceptions.YAMLValidationError)
@expected(exceptions.HitchStoryException)
def test(*words):
    """
    Run test with words.
    """
    print(
        StoryCollection(
            pathq(KEYPATH).ext("story"), Engine(KEYPATH, {"overwrite artefacts": True})
        ).shortcut(*words).play().report()
    )


def ci():
    """
    Run all stories.
    """
    lint()
    print(
        StoryCollection(
            pathq(KEYPATH).ext("story"), Engine(KEYPATH, {})
        ).ordered_by_name().play().report()
    )


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        KEYPATH.parent.joinpath("icommandlib"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        KEYPATH.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")
