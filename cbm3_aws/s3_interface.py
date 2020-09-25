import os
import zipfile
from cbm3_aws import log_helper

logger = log_helper.get_logger()


class S3Interface(object):

    def __init__(self, s3_resource, bucket_name, local_temp_dir):
        self.bucket_name = bucket_name
        self.bucket = s3_resource.Bucket(bucket_name)
        self.local_temp_dir = local_temp_dir
        self.__format = "zip"
        self.__singleFileFlag = "__is__single__file_archive__"

    def download_file(self, keyName, localPath):
        logger.debug(
            "downloading file from S3 '{0}' to '{1}'".format(
                keyName, localPath))
        self.bucket.download_file(keyName, localPath)

    def upload_file(self, localPath, keyName):
        logger.debug(
            "uploading file '{0}' to S3 '{1}'".format(localPath, keyName))
        self.bucket.upload_file(localPath, keyName)

    def make_zipfile(self, output_filename, source_dir):
        """
        mostly borrowed from an answer on Stack overflow
        https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
        """
        relroot = os.path.abspath(source_dir)
        with zipfile.ZipFile(output_filename, "w",
                             zipfile.ZIP_DEFLATED, allowZip64=True) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for _file in files:
                    filename = os.path.join(root, _file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(
                            os.path.relpath(root, relroot), _file)
                        zip.write(filename, arcname)

    def archive_file_or_directory(self, pathToArchive, archiveName):
        if os.path.isdir(pathToArchive):
            archivePath = os.path.join(self.local_temp_dir, archiveName)
            logger.debug(
                "archiving documents at '{0}' to '{1}'".format(
                    pathToArchive, archivePath))
            outputPath = archivePath + '.zip'
            self.make_zipfile(outputPath, pathToArchive)
            return outputPath
        elif os.path.isfile(pathToArchive):
            outputPath = \
                os.path.join(self.local_temp_dir, archiveName) + \
                "." + self.__format
            logger.debug(
                "archiving file '{0}' to '{1}'".format(
                    pathToArchive, outputPath))
            with zipfile.ZipFile(outputPath, 'w',
                                 zipfile.ZIP_DEFLATED, True) as z:
                z.write(pathToArchive, os.path.basename(pathToArchive))
                singleFilePath = os.path.join(
                    self.local_temp_dir, self.__singleFileFlag)
                with open(singleFilePath, mode='w'):
                    z.write(singleFilePath, self.__singleFileFlag)
                os.remove(singleFilePath)
            return outputPath
        else:
            raise ValueError(
                "specified pathToArchive '{0}' is neither a dir or a file path"
                .format(pathToArchive))

    def unpack_file_or_directory(self, archive_name, destination_path):
        logger.debug(
            "upacking files in '{0}' to '{1}'".format(
                archive_name, destination_path))
        with zipfile.ZipFile(archive_name, 'r', allowZip64=True) as z:
            files = z.namelist()
            if self.__singleFileFlag in files:
                if len(files) != 2:
                    raise ValueError(
                        "single file archive expected to have a single file")
                # it's a single file archive, so the destination path is
                # assumed to be the full path to the filename
                destinationDir = os.path.dirname(destination_path)
                destinationFileName = os.path.basename(destination_path)
                compressedFileName = [
                    x for x in files if x != self.__singleFileFlag][0]
                z.extractall(destinationDir)
                os.rename(
                    os.path.join(destinationDir, compressedFileName),
                    os.path.join(destinationDir, destinationFileName))
                os.remove(os.path.join(destinationDir, self.__singleFileFlag))
            else:
                z.extractall(destination_path)

    def upload_compressed(self, key_name_prefix, document_name, local_path):

        fn = self.archive_file_or_directory(local_path, document_name)
        # archive directory may add a file extension
        ext = os.path.splitext(fn)[1]
        document_name = document_name + ext
        self.upload_file(fn, "/".join([key_name_prefix, document_name]))
        os.remove(fn)

    def download_compressed(self, key_name_prefix, document_name, local_path):
        document_name = "{0}.{1}".format(document_name, self.__format)
        archiveName = os.path.join(
            self.local_temp_dir, document_name.replace('/', '_'))
        # for the above replace: if the documentname itself represents a
        # nested S3 key, convert it to something that can be written to
        # file systems for the local temp file
        self.download_file(
            "/".join([key_name_prefix, document_name]), archiveName)
        self.unpack_file_or_directory(archiveName, local_path)
        os.remove(archiveName)
