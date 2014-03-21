import os
import sublime

from .helpers import get_settings, find_project_root, strip_prefix

#
# Classes that implement TestLayouts
#


class BaseTestLayout(object):

    def __init__(self, current_filename):
        # TODO: implement equivalent sublime functions
        self.source_root = get_settings("PyUnitSourceRoot", "")
        self.test_root = get_settings("PyUnitTestsRoot", 'tests')
        self.prefix = get_settings("PyUnitTestPrefix", 'test_')

        try:
            self.project_root = find_project_root(current_filename)
        except IOError:
            sublime.error_message(
                "Could not find the project root for %s\n" % current_filename)

    # Helper methods, to be used in subclasses
    def break_down(self, path):
        parts = path.split(os.sep)
        if len(parts) > 0:
            if parts[-1] == '__init__.py':
                del parts[-1]
            elif parts[-1].endswith(".py"):
                parts[-1] = parts[-1][:-len(".py")]
        return parts

    def glue_parts(self, parts, use_under_under_init=False):
        if use_under_under_init:
            parts = parts + ['__init__.py']
        else:
            parts = parts[:-1] + [parts[-1] + '.py']
        return os.sep.join(parts)

    def relatize(self, path):
        return os.path.relpath(path, self.project_root)

    def absolutify(self, path):
        if os.path.isabs(path):
            return path
        return os.sep.join([self.project_root, path])

    # The actual BaseTestLayout methods that need implementation
    def is_test_file(self, some_file):
        raise NotImplemented("Implement this method in a subclass.")

    def get_test_file(self, source_file):
        raise NotImplemented("Implement this method in a subclass.")

    def get_source_candidates(self, test_file):
        raise NotImplemented("Implement this method in a subclass.")

    def get_source_file(self, test_file):
        for candidate in self.get_source_candidates(test_file):
            if os.path.exists(candidate):
                return candidate
        raise RuntimeError("Source file not found.")


class SideBySideLayout(BaseTestLayout):

    def is_test_file(self, some_file):
        some_file = self.relatize(some_file)
        parts = self.break_down(some_file)
        filepart = parts[-1]
        return filepart.startswith(self.prefix)

    def get_test_file(self, source_file):
        source_file = self.relatize(source_file)
        parts = self.break_down(source_file)
        parts[-1] = self.prefix + parts[-1]
        return self.glue_parts(parts)

    def get_source_candidates(self, test_file):
        test_file = self.relatize(test_file)
        parts = self.break_down(test_file)
        filepart = parts[-1]
        if not filepart.startswith(self.prefix):
            raise RuntimeError("Not a test file.")
        parts[-1] = filepart[len(self.prefix):]
        return [self.glue_parts(parts)]


class FlatLayout(BaseTestLayout):

    def is_test_file(self, some_file):
        some_file = self.relatize(some_file)
        if not some_file.startswith(self.test_root):
            return False

        some_file = os.path.relpath(some_file, self.test_root)

        parts = self.break_down(some_file)
        if len(parts) != 1:
            return False
        return parts[0].startswith(self.prefix)

    def get_test_file(self, source_file):
        source_file = self.relatize(source_file)
        if not source_file.startswith(self.source_root):
            raise RuntimeError(
                "File %s is not under the source root." % source_file)

        source_file = os.path.relpath(source_file, self.source_root)
        parts = self.break_down(source_file)
        flat_file_name = "_".join(parts)
        parts = [self.test_root] + [self.prefix + flat_file_name]
        return self.glue_parts(parts)

    def get_source_candidates(self, test_file):
        test_file = self.relatize(test_file)
        if not test_file.startswith(self.test_root):
            raise RuntimeError(
                "File %s is not under the test root." % test_file)

        test_file = os.path.relpath(test_file, self.test_root)
        parts = self.break_down(test_file)
        if len(parts) != 1:
            raise RuntimeError(
                "Flat tests layout does not allow tests to be more than one directory deep.")
        file_name = strip_prefix(parts[0], self.prefix)
        parts = file_name.split("_")
        if self.source_root:
            parts = [self.source_root] + parts
        return [self.glue_parts(parts, x) for x in (False, True)]


class FollowHierarchyLayout(BaseTestLayout):

    def is_test_file(self, some_file):
        some_file = self.relatize(some_file)
        if not some_file.startswith(self.test_root):
            return False

        some_file = os.path.relpath(some_file, self.test_root)

        parts = self.break_down(some_file)
        for p in parts:
            if not p.startswith(self.prefix):
                return False
        return True

    def get_test_file(self, source_file):
        source_file = self.relatize(source_file)
        if not source_file.startswith(self.source_root):
            raise RuntimeError(
                "File %s is not under the source root." % source_file)

        source_file = os.path.relpath(source_file, self.source_root)

        parts = self.break_down(source_file)
        parts = map(lambda p: self.prefix + p, parts)
        parts = [self.test_root] + list(parts)
        return self.glue_parts(parts)

    def get_source_candidates(self, test_file):
        test_file = self.relatize(test_file)
        if not test_file.startswith(self.test_root):
            raise RuntimeError(
                "File %s is not under the test root." % test_file)

        test_file = os.path.relpath(test_file, self.test_root)
        parts = self.break_down(test_file)
        parts = [strip_prefix(p, self.prefix) for p in parts]
        if self.source_root:
            parts = [self.source_root] + parts
        result = [self.glue_parts(parts, x) for x in (False, True)]
        return result


class NoseLayout(BaseTestLayout):

    def is_test_file(self, some_file):
        some_file = self.relatize(some_file)
        if not some_file.startswith(self.test_root):
            return False

        some_file = os.path.relpath(some_file, self.test_root)

        parts = self.break_down(some_file)
        return parts[-1].startswith(self.prefix)

    def get_test_file(self, source_file):
        source_file = self.relatize(source_file)
        if not source_file.startswith(self.source_root):
            raise RuntimeError(
                "File %s is not under the source root." % source_file)

        source_file = os.path.relpath(source_file, self.source_root)
        parts = self.break_down(source_file)
        parts[-1] = self.prefix + parts[-1]
        parts = [self.test_root] + parts
        return self.glue_parts(parts)

    def get_source_candidates(self, test_file):
        test_file = self.relatize(test_file)
        if not test_file.startswith(self.test_root):
            raise RuntimeError(
                "File %s is not under the test root." % test_file)

        test_file = os.path.relpath(test_file, self.test_root)
        parts = self.break_down(test_file)
        parts = [strip_prefix(p, self.prefix) for p in parts]
        if self.source_root:
            parts = [self.source_root] + parts
        result = [self.glue_parts(parts, x) for x in (False, True)]
        return result
