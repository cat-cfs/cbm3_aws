import unittest
import os
import shutil
import glob
from cbm3_aws.s3_interface import S3Interface


class MockS3Resource(object):
    def bind_bucket_method(self, method):
        self.bucket_method = method

    def Bucket(self, name):
        return self.bucket_method(name)


class MockS3Bucket(object):
    def __init__(self, name):
        self.name = name

    def bind_download_file_method(self, method):
        self.download_file_method = method

    def bind_upload_file_method(self, method):
        self.upload_file_method = method

    def download_file(self, keyName, localPath):
        self.download_file_method(keyName, localPath)

    def upload_file(self, localPath, keyName):
        self.upload_file_method(localPath, keyName)


class S3Interface_Test(unittest.TestCase):
    def test_constructor_creates_bucket_and_assigns_tempdir(self):
        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))
        s = S3Interface(m, "b", os.path.join(os.getcwd(), "temp"))
        self.assertIsInstance(s.bucket, MockS3Bucket)
        self.assertEqual(s.bucket.name, "b")
        self.assertEqual(s.local_temp_dir, os.path.join(os.getcwd(), "temp"))

    def test_downloadFileCallsBucketMethod(self):
        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))
        s = S3Interface(m, "b", os.path.join(os.getcwd(), "temp"))

        def func(keyName, localPath):
            self.assertEqual(localPath, "path")
            self.assertEqual(keyName, "key")

        s.bucket.bind_download_file_method(func)
        s.download_file("key", "path")

    def test_uploadFileCallsBucketMethod(self):
        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))
        s = S3Interface(m, "b", os.path.join(os.getcwd(), "temp"))

        def func(localPath, keyName):
            self.assertEqual(localPath, "path")
            self.assertEqual(keyName, "key")

        s.bucket.bind_upload_file_method(func)
        s.upload_file("path", "key")

    def test_archive_and_extract_file(self):
        tempPath = os.path.join(os.getcwd(), "tests", "temp")
        compressPath = os.path.join(tempPath, "compress")
        extractPath = os.path.join(tempPath, "extract")

        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))
        s = S3Interface(m, "b", tempPath)

        os.makedirs(compressPath)
        os.makedirs(extractPath)
        try:
            fn = os.path.join(compressPath, "tempfile")
            with open(fn, "w") as f:
                f.write("testfile contents")
            name = s.archive_file_or_directory(fn, "tempfile")
            s.unpack_file_or_directory(
                name, os.path.join(extractPath, "tempfile")
            )
            with open(os.path.join(extractPath, "tempfile"), "r") as f:
                self.assertEqual(f.read(), "testfile contents")
        finally:
            shutil.rmtree(tempPath)

    def test_archive_and_extract_dir(self):
        tempPath = os.path.join(os.getcwd(), "tests", "temp")
        compressPath = os.path.join(tempPath, "compress")
        extractPath = os.path.join(tempPath, "extract")

        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))
        s = S3Interface(m, "b", tempPath)

        os.makedirs(compressPath)
        os.makedirs(extractPath)
        try:
            for i in range(1, 10):
                # add files to the zip root dir
                with open(
                    os.path.join(compressPath, "tempfile{0}".format(i)), "w"
                ) as f:
                    f.write("testfile contents {0}".format(i))
                # now add some subdirectories and files
                subdir = os.path.join(compressPath, str(i))
                os.makedirs(subdir)
                with open(
                    os.path.join(subdir, "subdir_tempfile{0}".format(i)), "w"
                ) as f:
                    f.write("subdir testfile contents {0}".format(i))

            name = s.archive_file_or_directory(compressPath, "tempfile")
            s.unpack_file_or_directory(name, extractPath)
            for i in range(1, 10):
                with open(
                    os.path.join(extractPath, "tempfile{0}".format(i)), "r"
                ) as f:
                    self.assertEqual(
                        f.read(), "testfile contents {0}".format(i)
                    )
                subdir = os.path.join(extractPath, str(i))
                with open(
                    os.path.join(subdir, "subdir_tempfile{0}".format(i)), "r"
                ) as f:
                    self.assertEqual(
                        f.read(), "subdir testfile contents {0}".format(i)
                    )
        finally:
            shutil.rmtree(tempPath)

    def test_uploadCompressedFile(self):
        tempPath = os.path.join(os.getcwd(), "tests", "temp")
        compressPath = os.path.join(tempPath, "compress")

        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))

        s = S3Interface(m, "b", tempPath)
        os.makedirs(compressPath)
        try:

            def func(localPath, keyName):
                ext = os.path.splitext(localPath)[1]
                self.assertEqual(keyName, "keyPrefix/docName" + ext)
                result = glob.glob(
                    "{0}.*".format(os.path.join(tempPath, "docName"))
                )
                self.assertTrue(len(result) == 1)
                self.assertEqual(result[0], localPath)

            s.bucket.bind_upload_file_method(func)

            with open(os.path.join(compressPath, "tempfile"), "w") as f:
                f.write("testfile contents")

            s.upload_compressed(
                "keyPrefix", "docName", os.path.join(compressPath, "tempfile")
            )
        finally:
            shutil.rmtree(tempPath)

    def test_uploadCompressedDirectory(self):
        tempPath = os.path.join(os.getcwd(), "tests", "temp")
        compressPath = os.path.join(tempPath, "compress")

        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))

        s = S3Interface(m, "b", tempPath)
        os.makedirs(compressPath)
        try:

            def func(localPath, keyName):
                ext = os.path.splitext(localPath)[1]
                self.assertEqual(keyName, "keyPrefix/docName" + ext)
                result = glob.glob(
                    "{0}.*".format(os.path.join(tempPath, "docName"))
                )
                self.assertTrue(len(result) == 1)
                self.assertEqual(result[0], localPath)

            s.bucket.bind_upload_file_method(func)

            for i in range(1, 10):
                with open(
                    os.path.join(compressPath, "tempfile{0}".format(i)), "w"
                ) as f:
                    f.write("testfile contents {0}".format(i))

            s.upload_compressed("keyPrefix", "docName", compressPath)
        finally:
            shutil.rmtree(tempPath)

    def test_downloadCompressedFile(self):
        tempPath = os.path.join(os.getcwd(), "tests", "temp")
        compressPath = os.path.join(tempPath, "compress")
        extractPath = os.path.join(tempPath, "extract")

        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))

        s = S3Interface(m, "b", tempPath)
        os.makedirs(compressPath)
        os.makedirs(extractPath)
        try:

            def func(keyName, localPath):
                ext = os.path.splitext(localPath)[1]
                self.assertEqual(keyName, "keyPrefix/docpath/docName" + ext)

            s.bucket.bind_download_file_method(func)
            fn = os.path.join(compressPath, "tempfile")
            with open(fn, "w") as f:
                f.write("testfile contents")
            s.archive_file_or_directory(fn, "docpath_docName")
            s.download_compressed(
                "keyPrefix",
                "docpath/docName",
                os.path.join(extractPath, "tempfile"),
            )
            path = os.path.join(extractPath, "tempfile")
            with open(path, "r") as f:
                self.assertEqual(f.read(), "testfile contents")
            os.remove(path)
        finally:
            shutil.rmtree(tempPath)

    def test_downloadCompressedDirectory(self):
        tempPath = os.path.join(os.getcwd(), "tests", "temp")
        compressPath = os.path.join(tempPath, "compress")
        extractPath = os.path.join(tempPath, "extract")

        m = MockS3Resource()
        m.bind_bucket_method(lambda name: MockS3Bucket(name))

        s = S3Interface(m, "b", tempPath)
        os.makedirs(compressPath)
        os.makedirs(extractPath)
        try:

            def func(keyName, localPath):
                ext = os.path.splitext(localPath)[1]
                self.assertEqual(keyName, "keyPrefix/docpath/docName" + ext)

            s.bucket.bind_download_file_method(func)

            for i in range(1, 10):
                with open(
                    os.path.join(compressPath, "tempfile{0}".format(i)), "w"
                ) as f:
                    f.write("testfile contents {0}".format(i))
            s.archive_file_or_directory(compressPath, "docpath_docName")
            s.download_compressed("keyPrefix", "docpath/docName", extractPath)
            for i in range(1, 10):
                with open(
                    os.path.join(extractPath, "tempfile{0}".format(i)), "r"
                ) as f:
                    self.assertEqual(
                        f.read(), "testfile contents {0}".format(i)
                    )
        finally:
            shutil.rmtree(tempPath)


if __name__ == "__main__":
    unittest.main()
