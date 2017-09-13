from django.db.models.fields.files import FieldFile, FileField


class NEMIFieldFile(FieldFile):
    def save(self, name, content, save=True):
        pass


class NEMIFileField(FileField):
    """
    This `FileField` implements file storage to a BLOB field in the same
    manner as handled by the legacy APEX user interface for PDF uploads.

    The field uses two columns: a BLOB for the contents, and a VARCHAR to store
    the mimetype.
    """
    attr_class = NEMIFieldFile

    # Override FileField parameter validation - we ignore `upload_to`.
    def _check_upload_to(self):
        return []

    def generate_filename(self, instance, filename):
        raise NotImplementedError('This should not be called by NEMIFieldFile')

    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = super(FileField, self).pre_save(model_instance, add)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file.file, save=False)
        return file
