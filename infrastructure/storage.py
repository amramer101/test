import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError


class StorageService:
    def __init__(self, storage_backend=None):
        self.storage_backend = storage_backend or FileSystemStorage()

    def upload_file(self, file, path):
        """
        Uploads a file to the specified path using the configured storage backend.
        """
        try:
            file_path = os.path.join(path, file.name)
            saved_path = self.storage_backend.save(file_path, file)
            return self.storage_backend.url(saved_path)
        except Exception as e:
            raise ValidationError(f"Error uploading file: {str(e)}")

    def delete_file(self, path):
        """
        Deletes a file from the storage backend.
        """
        try:
            if self.storage_backend.exists(path):
                self.storage_backend.delete(path)
        except Exception as e:
            raise ValidationError(f"Error deleting file: {str(e)}")

    def list_files(self, path):
        """
        Lists all files in the specified directory.
        """
        try:
            if self.storage_backend.exists(path):
                return self.storage_backend.listdir(path)[1]  # Returns files only
            return []
        except Exception as e:
            raise ValidationError(f"Error listing files: {str(e)}")

    def get_file_url(self, path):
        """
        Retrieves the URL for a file stored in the backend.
        """
        try:
            if self.storage_backend.exists(path):
                return self.storage_backend.url(path)
            raise ValidationError("File does not exist.")
        except Exception as e:
            raise ValidationError(f"Error retrieving file URL: {str(e)}")
