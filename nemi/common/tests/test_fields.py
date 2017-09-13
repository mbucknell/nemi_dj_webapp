"""
Tests for `common.fields.NEMIFileField`
"""
import os
import random
import shutil
import tempfile

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.fields.files import FileDescriptor
from django.test import TestCase

from ..fields import NEMIFileField


class CustomValidNameStorage(FileSystemStorage):
    def get_valid_name(self, name):
        # mark the name to show that this was called
        return name + '_valid'


temp_storage_location = tempfile.mkdtemp()
temp_storage = FileSystemStorage(location=temp_storage_location)
FILE_SUFFIX_REGEX = '[A-Za-z0-9]{7}'


class Storage(models.Model):
    def custom_upload_to(self, filename):
        return 'foo'

    def random_upload_to(self, filename):
        # This returns a different result each time,
        # to make sure it only gets called once.
        return '%s/%s' % (random.randint(100, 999), filename)

    normal = NEMIFileField(storage=temp_storage, upload_to='tests')


class FileFieldStorageTests(TestCase):
    def tearDown(self):
        shutil.rmtree(temp_storage_location)

    def _storage_max_filename_length(self, storage):
        """
        Query filesystem for maximum filename length (e.g. AUFS has 242).
        """
        dir_to_test = storage.location
        while not os.path.exists(dir_to_test):
            dir_to_test = os.path.dirname(dir_to_test)
        try:
            return os.pathconf(dir_to_test, 'PC_NAME_MAX')
        except Exception:  #pylint: disable=W0703
            return 255  # Should be safe on most backends

    def test_files(self):
        self.assertIsInstance(Storage.normal, FileDescriptor)

        # An object without a file has limited functionality.
        obj1 = Storage()
        self.assertEqual(obj1.normal.name, "")
        with self.assertRaises(ValueError):
            obj1.normal.size  #pylint: disable=W0104

        # Saving a file enables full functionality.
        obj1.normal.save("django_test.txt", ContentFile("content"))
        self.assertEqual(obj1.normal.name, "tests/django_test.txt")
        self.assertEqual(obj1.normal.size, 7)
        self.assertEqual(obj1.normal.read(), b"content")
        obj1.normal.close()

        # File objects can be assigned to FileField attributes, but shouldn't
        # get committed until the model it's attached to is saved.
        obj1.normal = SimpleUploadedFile("assignment.txt", b"content")
        dirs, files = temp_storage.listdir("tests")
        self.assertEqual(dirs, [])
        self.assertNotIn("assignment.txt", files)

        obj1.save()
        dirs, files = temp_storage.listdir("tests")
        self.assertEqual(sorted(files), ["assignment.txt", "django_test.txt"])

        # Save another file with the same name.
        obj2 = Storage()
        obj2.normal.save("django_test.txt", ContentFile("more content"))
        obj2_name = obj2.normal.name
        self.assertRegex(obj2_name, "tests/django_test_%s.txt" % FILE_SUFFIX_REGEX)
        self.assertEqual(obj2.normal.size, 12)
        obj2.normal.close()

        # Deleting an object does not delete the file it uses.
        obj2.delete()
        obj2.normal.save("django_test.txt", ContentFile("more content"))
        self.assertNotEqual(obj2_name, obj2.normal.name)
        self.assertRegex(obj2.normal.name, "tests/django_test_%s.txt" % FILE_SUFFIX_REGEX)
        obj2.normal.close()

    def test_filefield_read(self):
        # Files can be read in a little at a time, if necessary.
        obj = Storage.objects.create(
            normal=SimpleUploadedFile("assignment.txt", b"content"))
        obj.normal.open()
        self.assertEqual(obj.normal.read(3), b"con")
        self.assertEqual(obj.normal.read(), b"tent")
        self.assertEqual(list(obj.normal.chunks(chunk_size=2)), [b"co", b"nt", b"en", b"t"])
        obj.normal.close()

    def test_filefield_write(self):
        # Files can be written to.
        obj = Storage.objects.create(normal=SimpleUploadedFile('rewritten.txt', b'content'))
        with obj.normal as normal:
            normal.open('wb')
            normal.write(b'updated')
        obj.refresh_from_db()
        self.assertEqual(obj.normal.read(), b'updated')
        obj.normal.close()

    def test_filefield_reopen(self):
        obj = Storage.objects.create(normal=SimpleUploadedFile('reopen.txt', b'content'))
        with obj.normal as normal:
            normal.open()
        obj.normal.open()
        obj.normal.file.seek(0)
        obj.normal.close()

    def test_duplicate_filename(self):
        # Multiple files with the same name get _(7 random chars) appended to them.
        objs = [Storage(), Storage()]
        for o in objs:
            o.normal.save("multiple_files.txt", ContentFile("Same Content"))
        try:
            names = [o.normal.name for o in objs]
            self.assertEqual(names[0], "tests/multiple_files.txt")
            self.assertRegex(names[1], "tests/multiple_files_%s.txt" % FILE_SUFFIX_REGEX)
        finally:
            for o in objs:
                o.delete()

    def test_filefield_pickling(self):
        # Push an object into the cache to make sure it pickles properly
        obj = Storage()
        obj.normal.save("django_test.txt", ContentFile("more content"))
        obj.normal.close()
        cache.set("obj", obj)
        self.assertEqual(cache.get("obj").normal.name, "tests/django_test.txt")
