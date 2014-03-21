import os
import re
import fnmatch
import sublime

#
# General helper functions
#


def get_settings(key, default=None, view=None):
    """ Lazy sublime settings loader for pyunit
    """
    try:
        if view is None:
            view = sublime.active_window().active_view()
        s = view.settings()
        if s.has(key):
            return s.get(key)
    except:
        pass
    return sublime.load_settings(
        'SublimePyunit.sublime-settings').get(key, default)


def strip_prefix(s, prefix):
    if prefix != "" and s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s


def is_home_dir(path):
    return os.path.realpath(path) == os.path.expandvars("$HOME")


def is_fs_root(path):
    return os.path.realpath(path) == "/" or \
        (get_settings("ProjRootStopAtHomeDir") and is_home_dir(path))


def find_project_root(path='.'):
    if not os.path.isdir(path):
        return find_project_root(os.path.dirname(os.path.realpath(path)))

    indicators = get_settings("ProjRootIndicators", ['setup.py', '.git'])
    markers = r'|'.join([fnmatch.translate(x) for x in indicators])
    if not is_fs_root(path):
        names = os.listdir(path)
        if any([re.search(markers, name) for name in names]):
            return os.path.realpath(path)
        return find_project_root(os.path.dirname(os.path.realpath(path)))
    raise IOError("Could not find project root")


def create_new_file(filename):
    base, filename = os.path.split(filename)
    create_folder(base)
    if filename != "":
        creation_path = os.path.join(base, filename)
        create_file(creation_path)


def create_file(name):
    open(name, "a").close()
    if get_settings("file_permissions", "") != "":
        file_permissions = get_settings("file_permissions", "")
        os.chmod(name, int(file_permissions, 8))


def create_folder(path):
    init_list = []
    temp_path = path
    while not os.path.exists(temp_path):
        init_list.append(temp_path)
        temp_path = os.path.dirname(temp_path)

    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise

    file_permissions = get_settings("file_permissions", "")
    folder_permissions = get_settings("folder_permissions", "")
    for entry in init_list:
        creation_path = os.path.join(entry, '__init__.py')
        open(creation_path, 'a').close()
        if file_permissions != "":
            os.chmod(creation_path, int(file_permissions, 8))
        if folder_permissions != "":
            os.chmod(entry, int(folder_permissions, 8))
