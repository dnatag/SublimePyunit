import os
import sys
import time

import sublime
import sublime_plugin
from Default.exec import ExecCommand

from .layouts import FlatLayout, \
    SideBySideLayout, FollowHierarchyLayout, NoseLayout
from .helpers import get_settings, find_project_root, create_new_file

if sys.version_info < (3, 3):
    raise RuntimeError('Sublime PyUnit works with Sublime Text 3 only')

# result_layout = {"cols": [0.0, 0.5, 1.0],
#                  "rows": [0.0, 0.5, 1.0],
#                  "cells": [[0, 0, 1, 2], [1, 0, 2, 1], [1, 1, 2, 2]]}


def plugin_loaded():
    get_settings("PyUnitCmd")


class PyUnitBaseCommand(sublime_plugin.WindowCommand):

    def get_implementing_class(self):
        """ Factory method for TestLayout object constructors
        Returns
        -------
        TestLayout constructor
        """
        implementations = {
            'flat': FlatLayout,
            'follow-hierarchy': FollowHierarchyLayout,
            'side-by-side': SideBySideLayout,
            'nose': NoseLayout,
        }
        test_layout = get_settings("PyUnitTestsStructure", "follow-hierarchy")
        try:
            return implementations[test_layout]
        except KeyError:
            raise RuntimeError('No such test layout: %s' % test_layout)

    #
    # The main functions
    #

    def find_source_file_for_test_file(self, path):
        impl = self.get_implementing_class()(path)
        for f in impl.get_source_candidates(path):
            f = os.path.join(impl.project_root, f)
            if os.path.exists(f):
                return f
        raise Exception("Source file not found.")

    def get_test_file_for_source_file(self, path):
        impl = self.get_implementing_class()(path)
        return impl.get_test_file(path)

    def is_test_file(self, path):
        impl = self.get_implementing_class()(path)
        return impl.is_test_file(path)


class PyUnitSrcTestSwitchCommand(PyUnitBaseCommand):

    def run(self):
        path = self.window.active_view().file_name()
        if self.is_test_file(path):
            self.switch_to_source_file_for_test_file(path)
        else:
            self.switch_to_test_file_for_source_file(path)

    def _open_buffer_cmd(self, path, load_src=False):
        cur_window = self.window
        cur_view = cur_window.active_view()
        switch_layout = {
            'cols': [0, 0.5, 1],
            'rows': [0, 1],
            'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]
        }
        cur_window.set_layout(switch_layout)

        file_view = cur_window.find_open_file(path)
        if load_src:
            group, index = cur_window.get_view_index(cur_view)
            if group == 1:
                cur_window.set_view_index(cur_view, 1, index)
            else:
                cur_window.set_view_index(cur_view, 1, 0)
            if file_view is not None:
                if file_view.window() != cur_window\
                        or file_view not in cur_window.views_in_group(0):
                    cur_window.set_view_index(file_view, 0, 0)
                cur_window.focus_view(file_view)
            else:
                cur_window.open_file(path, group=0)
        else:
            group, index = cur_window.get_view_index(cur_window.active_view())
            cur_window.set_view_index(cur_window.active_view(), 0, index)
            if file_view is not None:
                if file_view.window() != cur_window\
                        or file_view not in cur_window.views_in_group(1):
                    cur_window.set_view_index(file_view, 1, 0)
                cur_window.focus_view(file_view)
            else:
                cur_window.open_file(path, group=1)

    def lcd_to_project_root(self, path):
        os.chdir(find_project_root(path))

    def switch_to_test_file_for_source_file(self, path):
        testfile = os.path.join(find_project_root(path),
                                self.get_test_file_for_source_file(path))
        if not os.path.isfile(testfile):
            # Ask the user for confirmation
            msg = "Test file does not exist yet. Create %s now?" %\
                testfile
            if not sublime.ok_cancel_dialog(msg):
                return

            create_new_file(testfile)
            with open(testfile, "w+") as f:
                f.write("import unittest\n")
                f.write("from %s import *\n\n" %
                        os.path.splitext(os.path.basename(path))[0])
                f.write(
                    "\n\nif __name__ == '__main__':\n    unittest.main()\n")

        self._open_buffer_cmd(testfile)
        self.lcd_to_project_root(path)

    def switch_to_source_file_for_test_file(self, path):
        sourcefile = self.find_source_file_for_test_file(path)

        self._open_buffer_cmd(sourcefile, load_src=True)
        self.lcd_to_project_root(path)


class PyUnitRunTestCommand(PyUnitBaseCommand):

    def run(self):
        path = self.window.active_view().file_name()
        prj_root = find_project_root(path)
        if not self.is_test_file(path):
            path = self.get_test_file_for_source_file(path)
        else:
            path = os.path.relpath(path, prj_root)
        self.window.run_command('exec2', {
            'shell_cmd': ' '.join([get_settings('PyUnitCmd'), path]),
            'file_regex': get_settings('PyUnitResultRegex'),
            'working_dir': prj_root})


class PyUnitRunAllTestsCommand(PyUnitBaseCommand):

    def run(self):
        path = self.window.active_view().file_name()
        self.window.run_command('exec2', {
            'shell_cmd': ' '.join([get_settings('PyUnitCmd'),
                                   get_settings('PyUnitTestsRoot')]),
            'file_regex': get_settings('PyUnitResultRegex'),
            'working_dir': find_project_root(path)})


class Exec2Command(ExecCommand):

    def finish(self, proc):
        if not self.quiet:
            elapsed = time.time() - proc.start_time
            exit_code = proc.exit_code()
            if exit_code == 0 or exit_code is None:
                self.append_string(proc,
                                  ("[No failed tests. Finished in %.1fs]"
                                   % (elapsed)))
            else:
                self.append_string(proc,
                                  ("[Finished in %.1fs with exit code %d]\n"
                                   % (elapsed, exit_code)))
                self.append_string(proc, self.debug_text)

        if proc != self.proc:
            return

        errs = self.output_view.find_all_results()
        if len(errs) == 0:
            sublime.status_message("Build finished without errors")
        else:
            sublime.status_message(
                ("Build finished with %d errors") % len(errs))
