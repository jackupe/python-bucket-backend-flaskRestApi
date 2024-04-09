"""


"""

from werkzeug.utils import secure_filename
from aws import AwsHandler
from process_error import ProcessError

import datetime
import logging
import os
import pathlib


class FileHandler(object):
    # ALLOWED_EXTENSIONS = set(['xml', 'csv', 'json'])
    uploads = 'uploads'
    archives = 'archives'

    def __init__(self):
        """
        Initialize base directories and class instances
        Class is using to store uploaded files in subdirectories with current date as name in `upload directory`
        each file has added date as a prefix.
        """
        basedir = pathlib.Path(__file__).parent.resolve()
        self.BASE_UPLOAD_FOLDER = os.path.join(basedir, FileHandler.uploads)
        self.BASE_ARCHIVE_FOLDER = os.path.join(basedir, FileHandler.archives)

        try:
            if not os.path.exists(self.BASE_UPLOAD_FOLDER):
                os.makedirs(self.BASE_UPLOAD_FOLDER)

            if not os.path.exists(self.BASE_ARCHIVE_FOLDER):
                os.makedirs(self.BASE_ARCHIVE_FOLDER)
        except OSError as e:
            logging.error(e)
            raise ProcessError(e)
        else:
            self.aws = AwsHandler()
            self.create_subdir()

    def create_subdir(self):
        """
        Create subdirectory with year month and day in name

        Returns: string representation of sub_dir

        """
        subdir = "{date:%Y%m%d}".format(date=datetime.datetime.now())
        logging.info(subdir)
        try:
            if not os.path.exists(os.path.join(self.BASE_UPLOAD_FOLDER, subdir)):
                os.makedirs(os.path.join(self.BASE_UPLOAD_FOLDER, subdir))
        except OSError as e:
            logging.error(e)
            raise ProcessError(e)

        return str(subdir)

    def save_file(self, file=None):
        """
        Save file in subdirectory with current date.
        Saved filename are prefixed with date

        Make backup of file to AWS bucket.

        Args:
            file: original filename to save

        Returns: saved file name

        """
        if file is not None:
            try:
                subdir = self.create_subdir()
                filename = "_".join((subdir, secure_filename(file.filename)))
                logging.info("Saving as %s" % filename)

                file.save(os.path.join(self.BASE_UPLOAD_FOLDER, subdir, filename))

                self.aws.upload_file(os.path.join(self.BASE_UPLOAD_FOLDER, subdir, filename),
                                     "%s/%s/%s" % (FileHandler.uploads, subdir, filename))

                return os.path.join(subdir, filename)
            except OSError as e:
                logging.error(e)
                raise ProcessError(e)

        return None

    def list_files(self):
        """
        List files on the server.

        Returns: List of uploaded files to server

        """
        files = []
        try:
            for filename in os.listdir(self.BASE_UPLOAD_FOLDER):
                path = os.path.join(self.BASE_UPLOAD_FOLDER, filename)
                if os.path.isfile(path):
                    files.append(filename)

            for subdir in self.fast_scandir(self.BASE_UPLOAD_FOLDER):
                for sub_dir in os.listdir(subdir):
                    path = os.path.join(subdir, sub_dir)
                    if os.path.isfile(path):
                        files.append(path.removeprefix(self.BASE_UPLOAD_FOLDER + os.sep))
        except OSError as e:
            logging.error(e)

        return files

    def delete_file(self, filename):
        """
        Remove file from disk

        Args:
            filename: file to remove

        Returns: True if file removed, else False

        """
        if filename is not None:
            logging.info("Removing as %s" % filename)
            # os.remove(os.path.join(self.BASE_UPLOAD_FOLDER,  filename))
            return True

        return False

    def fast_scandir(self, dirname):
        """

        Recursively list files in directory and subdirectories

        Args:
            dirname: dirname to list

        Returns: List of files in directory

        """
        try:
            subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
            for subdirname in list(subfolders):
                subfolders.extend(self.fast_scandir(subdirname))
            return subfolders
        except OSError as e:
            logging.error(e)
            return []


class FileDto(dict):
    """
    Simple class do store some information about file
    """

    def __init__(self, dictionary):
        dict.__init__(self)
        for k, v in dictionary.items():
            dict.__setitem__(self, k, v)


if __name__ == '__main__':
    print("{date:%Y%m%d}".format(date=datetime.datetime.now()))

    fh = FileHandler()

    # print(fh.fast_scandir(fh.BASE_UPLOAD_FOLDER))
    print(fh.list_files())
    files = fh.list_files()
    files = ["/".join(file.split(os.sep)) for file in files]

    print(files)

    print(os.sep)
