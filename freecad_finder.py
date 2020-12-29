#!/usr/bin/env python3
"""
Finds FreeCAD lib directories and adds them to `sys.path`, so that FreeCAD
modules can be imported and used outside of FreeCAD.
"""

import os
from subprocess import check_output, CalledProcessError
from tempfile import NamedTemporaryFile
import sys
import warnings
import glob

# FreeCAD python script will print this as first line, since exit code seems to
# generally be 1, and I can't seem to change that. So we need to distinguish
# real errors, which we will do by checking this first line.
_magic_first_line = 'Freecad python working!'
_line_before_sys_version = 'sys.version:'

_freecad_diag_script = '''
import sys
print('{}')
for x in sys.path:
    print(x)
print('{}')
print(sys.version)
# Otherwise the console mode seems to stay open, waiting for EOF.
sys.exit()
'''.format(_magic_first_line, _line_before_sys_version)

# These are in order they appear in `sys.path`. All subdirectories of the 'Mod'
# directory precede these directories in `sys.path`.
required_subdirs = [
    # There will also be a bunch of lines in `sys.path` for subdirectories of
    # this, but we will only consider this one required, as you may not want to
    # use modules / the modules available may be more likely to change.
    'Mod',
    'lib',
    'Ext',
    # Not including 'bin' here, though at least one way of calling FreeCAD on my
    # machine does add it. Likewise not including macro directories though
    # FreeCAD does always seem to add those (though at the bottom, not the top,
    # of `sys.path`).
]

# TODO add function get_freecad_executable so people can call that to inspect
# the executable that would be used (and maybe fullpath the one on PATH first,
# if that's the one selected?)

def get_freecad_lib_root(freecad_executable=None):
    """Returns path to root containing FreeCAD libraries.

    If the environment variable FREECAD_LIB_ROOT is defined, it will be
    returned.

    Otherwise, the `FreeCAD` executable will be invoked (in the headless
    "console" mode) with a Python script that will print out the contents of 
    `sys.path` (in the Python integrated with FreeCAD). The output of this will
    be used to determine this path.
    
    By default, this will not work if `FreeCAD` executable is not
    found in your terminal (i.e. not on $PATH). However, you can specify the
    path to the FreeCAD executable with the environment variable
    FREECAD_EXECUTABLE or the `freecad_executable` keyword argument. The keyword
    argument takes precedence.
    """
    freecad_lib_root_envvar = 'FREECAD_LIB_ROOT'
    if freecad_lib_root_envvar in os.environ:
        freecad_lib_root = os.environ[freecad_lib_root_envvar]
        if not os.path.isdir(freecad_lib_root):
            raise IOError(f'FREECAD_LIB_ROOT={freecad_lib_root} does not exist'
                'as a directory'
            )
        return freecad_lib_root

    expand = True
    if freecad_executable is None:
        # By default, assume FreeCAD is on $PATH, and try to invoke without
        # specifying full path.
        freecad_executable = 'FreeCAD'
        expand = False

        freecad_exe_envvar = 'FREECAD_EXECUTABLE'
        if freecad_exe_envvar in os.environ:
            # Just assuming this exists. Will let subsequent calls fail if not.
            freecad_executable = os.environ[freecad_exe_envvar]
            expand = True

    if expand:
        freecad_executable = os.path.expanduser(freecad_executable)

    # Note that it seems this approach might not work in Windows, because we may
    # not be able to open this temporary file in another process...
    # https://stackoverflow.com/questions/3924117
    with NamedTemporaryFile(mode='w+t', suffix='.py') as temp:
        temp.write(_freecad_diag_script)
        temp.flush()

        # TODO should i support lowercase 'freecad' too?
        # (if so, also check bin directory in case insensitive way, if i'm still
        # doing that)
        freecad_cmd = f'{freecad_executable} -c {temp.name}'
        try:
            # The parts of `check_output` input besides `freecad_cmd`
            # are to make it seem to FreeCAD like the output is a tty.
            # Otherwise, FreeCAD seems to decide not to produce output.
            # You can verify this behavior by running:
            # `FreeCAD -c test.py > test.out` (where `test.py` should print
            # something) `test.out` will not contain what `test.py` was supposed
            # to print (it will instead by empty).
            # https://stackoverflow.com/questions/32910661
            # https://stackoverflow.com/questions/41542960 had a similar way of
            # faking a tty output that was more in python than shell, but the
            # shell way seemed simpler.
            check_output(['script', '-qefc', freecad_cmd, '/dev/null'])

            assert False, 'did not expect 0 exit code'

        # Expecting this to always happen (hence the assert above)
        except CalledProcessError as e:
            lines = e.output.decode('utf-8').splitlines()

            # In case FreeCAD doesn't always have this retcode, across versions
            # and deployments, I'll just check the first line instead of also
            # checking the return code is 1.
            #if e.returncode != 1:

            # TODO check empty output doesn't cause indexerror here
            if lines[0] != _magic_first_line:
                # TODO maybe print some other data from `e`?
                raise
        '''
        print('freecad_cmd:')
        print(freecad_cmd)
        import ipdb; ipdb.set_trace()
        '''

    # Getting rid of `_magic_first_line`, which we no longer need.
    lines = lines[1:]

    # Index of `_line_before_sys_version` in output. Preceding lines should
    # each contain one element of `sys.path` and following data should be
    # the `sys.version` string.
    vidx = None
    for i, line in enumerate(lines):
        if line == _line_before_sys_version:
            assert vidx is None, \
                '_line_before_sys_version encountered >1 times'
            vidx = i
    assert vidx is not None, '_line_before_sys_version not found'

    # "Caveats" section of https://wiki.freecadweb.org/Embedding%20FreeCAD
    # seems to say that `sys.version` should be similar in any external python
    # you wish you use w/ FreeCAD and this info from within the integrated
    # FreeCAD python.
    freecad_sys_path = lines[:vidx]
    freecad_sys_version = '\n'.join(lines[(vidx + 1):])
    if sys.version != freecad_sys_version:
        warnings.warn('sys.version of this python != sys.version of the FreeCAD'
            ' python. Using FreeCAD Python libraries outside of FreeCAD may not'
            ' work.'
        )

    # Could refactor to use (some of) these FreeCAD sys.path lines directly
    # in our sys.path, in case the stuff that needs to be on sys.path isn't
    # always in the same structure under one particular root directory.
    # Perhaps when not installed from source (or not exactly as I have it),
    # this is possible.
    '''
    print('freecad sys.path:')
    from pprint import pprint
    pprint(freecad_sys_path)
    '''

    main_freecad_lib = 'FreeCAD.so'
    freecad_lib_subdirs = []
    for d in freecad_sys_path:
        if os.path.exists(os.path.join(d, main_freecad_lib)):
            freecad_lib_subdirs.append(d)

    if len(freecad_lib_subdirs) == 0:
        raise IOError(f'{main_freecad_lib} not found in any sys.path '
            'directories whose paths ended with "/lib"'
        )
    elif len(freecad_lib_subdirs) > 1:
        raise RuntimeError(f'{main_freecad_lib} found in multiple .../lib '
            f'directories: {freecad_lib_subdirs}. ambiguous!'
        )

    freecad_lib_root = os.path.split(freecad_lib_subdirs[0])[0]

    for d in required_subdirs:
        assert os.path.isdir(os.path.join(freecad_lib_root, d))

    # TODO why is there is a '' entry (just before '/usr/lib/python36.zip') when
    # running some ways but (seemingly?) not when printing `sys.path` from the
    # python console in a running GUI freecad?
    # also there when calling `Freecad -c <diag-script-path>` from terminal
    # manually. probably doesn't matter much though...
    # (actually there might be more differences... 'About' of FreeCAD invoked
    # from terminal or .desktop launcher had same version, but not sure they are
    # 100% the same. at least it seems they might be copies, not symlinks.)

    return freecad_lib_root


def add_freecad_dirs_to_syspath(freecad_executable=None, append_all=False
    ) -> None:
    """Adds directories to `sys.path` so FreeCAD modules can be imported.

    Args:
    freecad_executable (str): path to FreeCAD executable. With default of `None`
        will first use the value in FREECAD_EXECUTABLE, if that environment
        variable is set, but will otherwise try `FreeCAD` as if it were on the
        PATH.

    append_all (bool): whether to put all FreeCAD paths at the end of
        `sys.path`, rather than inserting some at the beginning as FreeCAD does.
        Defaults to `False`.

    Not currently adding the:
    <$HOME>/.FreeCAD/Macro/
    <$HOME>/src/FreeCAD/build/Macro
    directories that FreeCAD inserts at the end of `sys.path`.
    """
    freecad_lib_root = get_freecad_lib_root(
        freecad_executable=freecad_executable
    )
    '''
    from pprint import pprint
    print('sys.path BEFORE:')
    pprint(sys.path)
    '''

    # From some manual testing I did, it seems every subdirectory of
    # <freecad_lib_root>/Mod is added to `sys.path`
    for d in required_subdirs[::-1]:
        abs_d = os.path.join(freecad_lib_root, d)
        # See Ulf Rompe's answer https://stackoverflow.com/questions/10095037
        # for one reason to not insert at 0, though I think FreeCAD already
        # screws this up so it shouldn't matter.
        sys.path.insert(0, abs_d)

    mod_subdirs = glob.glob(os.path.join(freecad_lib_root, 'Mod', '*/'))
    for d in mod_subdirs:
        # Checking `isdir` in case a file gets added to this directory at some
        # point (accidentally or intentionally via the FreeCAD project).
        if os.path.isdir(d):
            sys.path.insert(0, d)

    '''
    print('sys.path AFTER:')
    pprint(sys.path)
    '''

    # TODO do FreeCAD [+ maybe FreeCADCmd] need to be on PYTHONPATH?
    # when freecad_executable=/home/tom/src/FreeCAD/build/bin/FreeCAD,
    # /home/tom/src/FreeCAD/build/bin is one of the sys.path entries, but when
    # freecad_executable=FreeCAD (-> /usr/local/bin/FreeCAD), there is no such
    # line. but maybe the binary is just in one of the other folders in
    # PYTHONPATH in that case?

    # TODO test that in non-source installations, all the directories we want to
    # add to sys.path still share the same prefix, and have the same kind of
    # structure as those under my build directory


def main():
    add_freecad_dirs_to_syspath()


if __name__ == '__main__':
    main()

