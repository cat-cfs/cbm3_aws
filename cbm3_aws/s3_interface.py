import os
import shutil
import zipfile
from tempfile import TemporaryDirectory
from cbm3_aws import log_helper
from mypy_boto3_s3.service_resource import S3ServiceResource
from boto3.s3.transfer import TransferConfig

logger = log_helper.get_logger(__name__)


class S3Interface(object):
    def __init__(
        self,
        s3_resource: S3ServiceResource,
        bucket_name: str,
    ):
        self.bucket_name = bucket_name
        self.bucket = s3_resource.Bucket(bucket_name)
        self._format = "zip"
        self._singleFileFlag = "__is__single__file_archive__"

    def download_file(self, keyName, localPath) -> None:
        logger.info(
            "downloading file from S3 '{0}' to '{1}'".format(
                keyName, localPath
            )
        )
        self.bucket.download_file(
            keyName, localPath, Config=TransferConfig(num_download_attempts=10)
        )

    def upload_file(self, localPath: str, keyName: str) -> None:
        logger.info(
            "uploading file '{0}' to S3 '{1}'".format(localPath, keyName)
        )
        self.bucket.upload_file(
            localPath, keyName, Config=TransferConfig(num_download_attempts=10)
        )

    def make_zipfile(self, output_filename, source_dir) -> None:
        """
        mostly borrowed from an answer on Stack overflow
        https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
        """
        relroot = os.path.abspath(source_dir)
        with zipfile.ZipFile(
            output_filename, "w", zipfile.ZIP_DEFLATED, allowZip64=True
        ) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for _file in files:
                    filename = os.path.join(root, _file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(
                            os.path.relpath(root, relroot), _file
                        )
                        zip.write(filename, arcname)

    def archive_file_or_directory(
        self, pathToArchive: str, archiveName: str, temp_dir: str
    ) -> str:
        if os.path.isdir(pathToArchive):
            archivePath = os.path.join(temp_dir, archiveName)
            logger.debug(
                "archiving documents at '{0}' to '{1}'".format(
                    pathToArchive, archivePath
                )
            )
            outputPath = archivePath + ".zip"
            self.make_zipfile(outputPath, pathToArchive)
            return outputPath
        elif os.path.isfile(pathToArchive):
            outputPath = (
                os.path.join(temp_dir, archiveName) + "." + self._format
            )
            logger.debug(
                "archiving file '{0}' to '{1}'".format(
                    pathToArchive, outputPath
                )
            )
            with zipfile.ZipFile(
                outputPath, "w", zipfile.ZIP_DEFLATED, True
            ) as z:
                z.write(pathToArchive, os.path.basename(pathToArchive))
                singleFilePath = os.path.join(temp_dir, self._singleFileFlag)
                with open(singleFilePath, mode="w"):
                    z.write(singleFilePath, self._singleFileFlag)
                os.remove(singleFilePath)
            return outputPath
        else:
            raise ValueError(
                f"specified pathToArchive '{pathToArchive}' "
                "is neither a dir or a file path"
            )

    def unpack_file_or_directory(
        self, archive_name: str, destination_path: str
    ) -> None:
        logger.debug(
            "upacking files in '{0}' to '{1}'".format(
                archive_name, destination_path
            )
        )
        with zipfile.ZipFile(archive_name, "r", allowZip64=True) as z:
            files = z.namelist()
            if self._singleFileFlag in files:
                if len(files) != 2:
                    raise ValueError(
                        "single file archive expected to have a single file"
                    )
                # it's a single file archive, so the destination path is
                # assumed to be the full path to the filename
                destinationDir = os.path.dirname(destination_path)
                if not os.path.exists(destinationDir):
                    os.makedirs(destinationDir)
                destinationFileName = os.path.basename(destination_path)
                compressedFileName = [
                    x for x in files if x != self._singleFileFlag
                ][0]
                with TemporaryDirectory() as extraction_dir:
                    z.extractall(extraction_dir)
                    shutil.copyfile(
                        src=os.path.join(extraction_dir, compressedFileName),
                        dst=os.path.join(destinationDir, destinationFileName),
                    )

            else:
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)
                z.extractall(destination_path)

    def upload_compressed(
        self, key_name_prefix: str, document_name: str, local_path: str
    ) -> None:
        with TemporaryDirectory() as tempdir:
            fn = self.archive_file_or_directory(
                local_path, document_name, tempdir
            )
            # archive directory may add a file extension
            ext = os.path.splitext(fn)[1]
            document_name = document_name + ext
            s3_key = "/".join([key_name_prefix, document_name])
            self.upload_file(fn, s3_key)
            os.remove(fn)

    def download_compressed(
        self, key_name_prefix: str, document_name: str, local_path: str
    ) -> None:
        with TemporaryDirectory() as tempdir:
            document_name = "{0}.{1}".format(document_name, self._format)
            archiveName = os.path.join(
                tempdir, document_name.replace("/", "_")
            )
            # for the above replace: if the documentname itself represents a
            # nested S3 key, convert it to something that can be written to
            # file systems for the local temp file
            s3_key = "/".join([key_name_prefix, document_name])
            self.download_file(s3_key, archiveName)
            self.unpack_file_or_directory(archiveName, local_path)
            os.remove(archiveName)
