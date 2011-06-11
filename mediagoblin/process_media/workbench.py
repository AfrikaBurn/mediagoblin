# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 Free Software Foundation, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import tempfile


DEFAULT_WORKBENCH_DIR = os.path.join(
    tempfile.gettempdir(), u'mgoblin_workbench')


# Exception(s)
# ------------

class WorkbenchOutsideScope(Exception):
    """
    Raised when a workbench is outside a WorkbenchManager scope.
    """
    pass


# Actual workbench stuff
# ----------------------

class WorkbenchManager(object):
    """
    A system for generating and destroying workbenches.

    Workbenches are actually just subdirectories of a temporary storage space
    for during the processing stage.
    """

    def __init__(self, base_workbench_dir):
        self.base_workbench_dir = os.path.abspath(base_workbench_dir)
        if not os.path.exists(self.base_workbench_dir):
            os.makedirs(self.base_workbench_dir)
        
    def create_workbench(self):
        """
        Create and return the path to a new workbench (directory).
        """
        return tempfile.mkdtemp(dir=self.base_workbench_dir)

    def destroy_workbench(self, workbench):
        """
        Destroy this workbench!  Deletes the directory and all its contents!

        Makes sure the workbench actually belongs to this manager though.
        """
        # just in case
        workbench = os.path.abspath(workbench)

        if not workbench.startswith(self.base_workbench_dir):
            raise WorkbenchOutsideScope(
                "Can't destroy workbench outside the base workbench dir")

        shutil.rmtree(workbench)

    def possibly_localize_file(self, workbench, storage, filepath,
                               filename_if_copying=None,
                               keep_extension_if_copying=True):
        """
        Possibly localize the file from this storage system (for read-only
        purposes, modifications should be written to a new file.).

        If the file is already local, just return the absolute filename of that
        local file.  Otherwise, copy the file locally to the workbench, and
        return the absolute path of the new file.

        If it is copying locally, we might want to require a filename like
        "source.jpg" to ensure that we won't conflict with other filenames in
        our workbench... if that's the case, make sure filename_if_copying is
        set to something like 'source.jpg'.  Relatedly, if you set
        keep_extension_if_copying, you don't have to set an extension on
        filename_if_copying yourself, it'll be set for you (assuming such an
        extension can be extacted from the filename in the filepath).

        Also returns whether or not it copied the file locally.

        Returns:
          (localized_filename, copied_locally)
          The first of these bieng the absolute filename as described above as a
          unicode string, the second being a boolean stating whether or not we
          had to copy the file locally.

        Examples:
          >>> wb_manager.possibly_localize_file(
          ...     '/our/workbench/subdir', local_storage,
          ...     ['path', 'to', 'foobar.jpg'])
          (u'/local/storage/path/to/foobar.jpg', False)

          >>> wb_manager.possibly_localize_file(
          ...     '/our/workbench/subdir', remote_storage,
          ...     ['path', 'to', 'foobar.jpg'])
          (u'/our/workbench/subdir/foobar.jpg', True)

          >>> wb_manager.possibly_localize_file(
          ...     '/our/workbench/subdir', remote_storage,
          ...     ['path', 'to', 'foobar.jpg'], 'source.jpeg', False)
          (u'/our/workbench/subdir/foobar.jpeg', True)

          >>> wb_manager.possibly_localize_file(
          ...     '/our/workbench/subdir', remote_storage,
          ...     ['path', 'to', 'foobar.jpg'], 'source', True)
          (u'/our/workbench/subdir/foobar.jpg', True)
        """
        if storage.local_storage:
            return (storage.get_local_path(filepath), False)
        else:
            if filename_if_copying is None:
                dest_filename = filepath[-1]
            else:
                orig_filename, orig_ext = os.path.splitext(filepath[-1])
                if keep_extension_if_copying and orig_ext:
                    dest_filename = filename_if_copying + '.' + orig_ext
                else:
                    dest_filename = filename_if_copying

            full_dest_filename = os.path.join(
                workbench, dest_filename)

            # copy it over
            storage.copy_locally(
                filepath, full_dest_filename)

            return (full_dest_filename, True)