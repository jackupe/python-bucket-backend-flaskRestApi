"""


"""

from werkzeug.utils import secure_filename
from aws import AwsHandler

import datetime
import logging
import os
import pathlib



class FileHandler(object):
    #ALLOWED_EXTENSIONS = set(['xml', 'csv', 'json'])
    uploads = 'uploads'
    archives = 'archives'

    def __init__(self):
        basedir = pathlib.Path(__file__).parent.resolve()
        self.BASE_UPLOAD_FOLDER = os.path.join(basedir, FileHandler.uploads)
        self.BASE_ARCHIVE_FOLDER = os.path.join(basedir, FileHandler.archives)

        if not os.path.exists(self.BASE_UPLOAD_FOLDER):
            os.makedirs(self.BASE_UPLOAD_FOLDER)

        if not os.path.exists(self.BASE_ARCHIVE_FOLDER):
            os.makedirs(self.BASE_ARCHIVE_FOLDER)

        self.create_subdir()
        self.aws = AwsHandler()

    def create_subdir(self):
        subdir = "{date:%Y%m%d}".format(date=datetime.datetime.now())
        logging.info(subdir)
        if not os.path.exists(os.path.join(self.BASE_UPLOAD_FOLDER, subdir)):
            os.makedirs(os.path.join(self.BASE_UPLOAD_FOLDER, subdir))

        return str(subdir)

    def save_file(self, file=None):
        if file is not None:
            subdir = self.create_subdir()
            filename = "_".join((subdir, secure_filename(file.filename)))
            logging.info("Saving as %s" % filename)

            file.save(os.path.join(self.BASE_UPLOAD_FOLDER, subdir, filename))

            self.aws.upload_file(os.path.join(self.BASE_UPLOAD_FOLDER, subdir, filename), "%s/%s/%s" % (FileHandler.uploads, subdir, filename))

            return os.path.join(subdir, filename)

        return None

    def list_files(self):
        """Endpoint to list files on the server."""
        files = []
        for filename in os.listdir(self.BASE_UPLOAD_FOLDER):
            path = os.path.join(self.BASE_UPLOAD_FOLDER, filename)
            if os.path.isfile(path):
                files.append(filename)

        for subdir in self.fast_scandir(self.BASE_UPLOAD_FOLDER):
            for sub_dir in os.listdir(subdir):
                path = os.path.join(subdir, sub_dir)
                if os.path.isfile(path):
                    files.append(path.removeprefix(self.BASE_UPLOAD_FOLDER + os.sep))

        return files

    def delete_file(self, filename):
        if filename is not None:
            logging.info("Removing as %s" % filename)
            #os.remove(os.path.join(self.BASE_UPLOAD_FOLDER,  filename))


    def fast_scandir(self, dirname):
        subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
        for subdirname in list(subfolders):
            subfolders.extend(self.fast_scandir(subdirname))
        return subfolders


class FileDto(dict):

    def __init__(self, dictionary):
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

    print (os.sep)