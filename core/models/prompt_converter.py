# flake8: noqa: E501
from __future__ import annotations

import base64
import hashlib
import logging
import os
import time
import wave
from abc import ABC, abstractmethod
from enum import Enum
from mimetypes import guess_type
from pathlib import Path
from typing import get_args, Literal, Optional, Union
from urllib.parse import urlparse

import aiofiles  # type: ignore

logger = logging.getLogger(__name__)

# ============================ Literals ======================================
# Define allowed categories for validation
AllowedCategories = Literal["seed-prompt-entries", "prompt-memory-entries"]

PromptDataType = Literal[
    "text", "image_path", "audio_path", "video_path", "url", "error"
]

"""
The type of the error in the prompt response
blocked: blocked by an external filter e.g. Azure Filters
none: no exception is raised
processing: there is an exception thrown unrelated to the query
unknown: the type of error is unknown
"""
PromptResponseError = Literal[
    "blocked", "none", "processing", "empty", "unknown"
]

ChatMessageRole = Literal["system", "user", "assistant"]


# ============================ Identifiers ====================================
class Identifier:
    @abstractmethod
    def get_identifier(self) -> dict[str, str]:
        pass

    def __str__(self) -> str:
        return f"{self.get_identifier}"


# ============================ Data Type Serializer =========================
def data_serializer_factory(
    *,
    data_type: PromptDataType,
    value: Optional[str] = None,
    extension: Optional[str] = None,
    category: AllowedCategories,
):
    """
    Factory method to create a DataTypeSerializer instance.

    Args:
        data_type (str): The type of the data (e.g., 'text', 'image_path', 'audio_path').
        value (str): The data value to be serialized.
        extension (Optional[str]): The file extension, if applicable.
        category (AllowedCategories): The category or context for the data (e.g., 'seed-prompt-entries').

    Returns:
        DataTypeSerializer: An instance of the appropriate serializer.

    Raises:
        ValueError: If the category is not provided or invalid.
    """  # noqa: E501
    if not category:
        raise ValueError(
            f"The 'category' argument is mandatory & must be one of these:"
            f" {get_args(AllowedCategories)}."
        )
    if value is not None:
        if data_type == "text":
            return TextDataTypeSerializer(prompt_text=value)
        elif data_type == "image_path":
            return ImagePathDataTypeSerializer(
                category=category, prompt_text=value, extension=extension
            )
        elif data_type == "audio_path":
            return AudioPathDataTypeSerializer(
                category=category, prompt_text=value, extension=extension
            )
        elif data_type == "video_path":
            return VideoPathDataTypeSerializer(
                category=category, prompt_text=value, extension=extension
            )
        elif data_type == "error":
            return ErrorDataTypeSerializer(prompt_text=value)
        elif data_type == "url":
            return URLDataTypeSerializer(
                category=category, prompt_text=value, extension=extension
            )
        else:
            raise ValueError(f"Data type {data_type} not supported")
    else:
        if data_type == "image_path":
            return ImagePathDataTypeSerializer(
                category=category, extension=extension
            )
        elif data_type == "audio_path":
            return AudioPathDataTypeSerializer(
                category=category, extension=extension
            )
        elif data_type == "video_path":
            return VideoPathDataTypeSerializer(
                category=category, extension=extension
            )
        elif data_type == "error":
            return ErrorDataTypeSerializer(prompt_text="")
        else:
            raise ValueError(
                f"Data type {data_type} without prompt text not supported"
            )


class DataTypeSerializer(ABC):
    """
    Abstract base class for data type normalizers.

    Responsible for reading and saving multi-modal data types to local disk.
    """

    data_type: PromptDataType
    value: str
    category: str
    data_sub_directory: str
    file_extension: str
    _memory: StorageIO = None
    _file_path: Union[Path, str] = None

    def _get_storage_io(self):
        """
        Retrieve the input datasets storage handle.

        Returns:
        StorageIO: An instance of DiskStorageIO or AzureBlobStorageIO based on the storage configuration.

        Raises:
            ValueError: If the Azure Storage URL is detected but the datasets storage handle is not set.
        """  # noqa: E501
        return DiskStorageIO()

    @abstractmethod
    def data_on_disk(self) -> bool:
        """
        Returns True if the data is stored on disk.
        """

    async def save_data(self, data: bytes) -> None:
        """
        Saves the data to storage.
        """
        file_path = await self.get_data_filename()
        await self._memory.results_storage_io.write_file(file_path, data)
        self.value = str(file_path)

    async def save_b64_image(
        self, data: str, output_filename: str = None
    ) -> None:
        """
        Saves the base64 encoded image to storage.
        Arguments:
            data: string with base64 data
            output_filename (optional, str): filename to store image as.
            Defaults to UUID if not provided
        """
        file_path = output_filename or await self.get_data_filename()
        image_bytes = base64.b64decode(data)
        await self._memory.results_storage_io.write_file(
            file_path, image_bytes
        )
        self.value = str(file_path)

    async def save_formatted_audio(
        self,
        data: bytes,
        output_filename: str = None,
        num_channels: int = 1,
        sample_width: int = 2,
        sample_rate: int = 16000,
    ) -> None:
        """
        Saves the PCM16 of other specially formatted audio data to storage.
        Arguments:
            data: bytes with audio data
            output_filename (optional, str): filename to store audio as. Defaults to UUID if not provided
            num_channels (optional, int): number of channels in audio data. Defaults to 1
            sample_width (optional, int): sample width in bytes. Defaults to 2
            sample_rate (optional, int): sample rate in Hz. Defaults to 16000
        """  # noqa: E501
        file_path = output_filename or await self.get_data_filename()

        with wave.open(str(file_path), "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(data)

        self.value = str(file_path)

    async def read_data(self) -> bytes:
        """
        Reads the data from the storage.

        Returns:
            bytes: The data read from storage.
        """
        if not self.data_on_disk():
            raise TypeError(
                f"Data for data Type {self.data_type} is not stored on disk"
            )

        if not self.value:
            raise RuntimeError("Prompt text not set")

        storage_io = self._get_storage_io()
        # Check if path exists
        file_exists = await storage_io.path_exists(path=self.value)
        if not file_exists:
            raise FileNotFoundError(f"File not found: {self.value}")
        # Read the contents from the path
        return await storage_io.read_file(self.value)

    async def read_data_base64(self) -> str:
        """
        Reads the data from the storage.
        """
        byte_array = await self.read_data()
        return base64.b64encode(byte_array).decode("utf-8")

    async def get_sha256(self) -> str:
        input_bytes: bytes = None

        if self.data_on_disk():
            storage_io = self._get_storage_io()
            file_exists = await storage_io.path_exists(self.value)
            if not file_exists:
                raise FileNotFoundError(f"File not found: {self.value}")

            # Read the data from storage
            input_bytes = await storage_io.read_file(self.value)
        else:
            if isinstance(self.value, str):
                input_bytes = self.value.encode("utf-8")
            else:
                raise ValueError(
                    f"Invalid data type {self.value}, expected str data type."
                )

        hash_object = hashlib.sha256(input_bytes)
        return hash_object.hexdigest()

    async def get_data_filename(self) -> Union[Path, str]:
        """
        Generates or retrieves a unique filename for the data file.
        """
        if self._file_path:
            return self._file_path

        if not self.data_on_disk():
            raise TypeError("Data is not stored on disk")

        if not self.data_sub_directory:
            raise RuntimeError("Data sub directory not set")
        ticks = int(time.time() * 1_000_000)

        results_path = self._memory.results_path

        full_data_directory_path = results_path + self.data_sub_directory
        await self._memory.results_storage_io.create_directory_if_not_exists(  # noqa: E501
            Path(full_data_directory_path)
        )
        self._file_path = Path(
            full_data_directory_path, f"{ticks}.{self.file_extension}"
        )

        return self._file_path

    @staticmethod
    def get_extension(file_path: str) -> str | None:
        """
        Get the file extension from the file path.
        """
        _, ext = os.path.splitext(file_path)
        return ext if ext else None

    @staticmethod
    def get_mime_type(file_path: str) -> str | None:
        """
        Get the MIME type of the file path.
        """
        mime_type, _ = guess_type(file_path)
        return mime_type

    def _is_azure_storage_url(self, path: str) -> bool:
        """
        Validates if the given path is an Azure Storage URL.

        Args:
            path (str): Path or URL to check.

        Returns:
            bool: True if the path is an Azure Blob Storage URL.
        """
        parsed = urlparse(path)
        return (
            parsed.scheme in ("http", "https")
            and "blob.core.windows.net" in parsed.netloc
        )


class TextDataTypeSerializer(DataTypeSerializer):
    def __init__(self, *, prompt_text: str):
        self.data_type = "text"
        self.value = prompt_text

    def data_on_disk(self) -> bool:
        return False


class ErrorDataTypeSerializer(DataTypeSerializer):
    def __init__(self, *, prompt_text: str):
        self.data_type = "error"
        self.value = prompt_text

    def data_on_disk(self) -> bool:
        return False


class URLDataTypeSerializer(DataTypeSerializer):
    def __init__(
        self,
        *,
        category: str,
        prompt_text: str,
        extension: Optional[str] = None,
    ):
        self.data_type = "url"
        self.value = prompt_text
        self.data_sub_directory = f"/{category}/urls"
        self.file_extension = extension if extension else "txt"

    def data_on_disk(self) -> bool:
        return True


class ImagePathDataTypeSerializer(DataTypeSerializer):
    def __init__(
        self,
        *,
        category: str,
        prompt_text: Optional[str] = None,
        extension: Optional[str] = None,
    ):
        self.data_type = "image_path"
        self.data_sub_directory = f"/{category}/images"
        self.file_extension = extension if extension else "png"

        if prompt_text:
            self.value = prompt_text

    def data_on_disk(self) -> bool:
        return True


class AudioPathDataTypeSerializer(DataTypeSerializer):
    def __init__(
        self,
        *,
        category: str,
        prompt_text: Optional[str] = None,
        extension: Optional[str] = None,
    ):
        self.data_type = "audio_path"
        self.data_sub_directory = f"/{category}/audio"
        self.file_extension = extension if extension else "mp3"

        if prompt_text:
            self.value = prompt_text

    def data_on_disk(self) -> bool:
        return True


class VideoPathDataTypeSerializer(DataTypeSerializer):
    def __init__(
        self,
        *,
        category: str,
        prompt_text: Optional[str] = None,
        extension: Optional[str] = None,
    ):
        """
        Serializer for video data paths.

        Args:
            category (str): The category or context for the data.
            prompt_text (Optional[str]): The video path or identifier.
            extension (Optional[str]): The file extension, defaults to 'mp4'.
        """
        self.data_type = "video_path"
        self.data_sub_directory = f"/{category}/videos"
        self.file_extension = extension if extension else "mp4"

        if prompt_text:
            self.value = prompt_text

    def data_on_disk(self) -> bool:
        return True


class SupportedContentType(Enum):
    """
    All supported content types for uploading blobs to provided storage account container.
    See all options here: https://www.iana.org/assignments/media-types/media-types.xhtml
    """  # noqa: E501

    # TODO, add other media supported types
    PLAIN_TEXT = "text/plain"


# ============================ Storage IO ====================================
class StorageIO(ABC):
    """
    Abstract interface for storage systems (local disk).
    """

    @abstractmethod
    async def read_file(self, path: Union[Path, str]) -> bytes:
        """
        Asynchronously reads the file (or blob) from the given path.
        """

    @abstractmethod
    async def write_file(self, path: Union[Path, str], data: bytes) -> None:
        """
        Asynchronously writes data to the given path.
        """

    @abstractmethod
    async def path_exists(self, path: Union[Path, str]) -> bool:
        """
        Asynchronously checks if a file or blob exists at the given path.
        """

    @abstractmethod
    async def is_file(self, path: Union[Path, str]) -> bool:
        """
        Asynchronously checks if the path refers to a file (not a directory or container).
        """  # noqa: E501

    @abstractmethod
    async def create_directory_if_not_exists(
        self, path: Union[Path, str]
    ) -> None:
        """
        Asynchronously creates a directory or equivalent in the storage system if it doesn't exist.
        """  # noqa: E501


class DiskStorageIO(StorageIO):
    """
    Implementation of StorageIO for local disk storage.
    """

    async def read_file(self, path: Union[Path, str]) -> bytes:
        """
        Asynchronously reads a file from the local disk.
        Args:
            path (Union[Path, str]): The path to the file.
        Returns:
            bytes: The content of the file.
        """
        path = self._convert_to_path(path)
        async with aiofiles.open(path, "rb") as file:
            return await file.read()

    async def write_file(self, path: Union[Path, str], data: bytes) -> None:
        """
        Asynchronously writes data to a file on the local disk.
        Args:
            path (Path): The path to the file.
            data (bytes): The content to write to the file.
        """
        path = self._convert_to_path(path)
        async with aiofiles.open(path, "wb") as file:
            await file.write(data)

    async def path_exists(self, path: Union[Path, str]) -> bool:
        """
        Checks if a path exists on the local disk.
        Args:
            path (Path): The path to check.
        Returns:
            bool: True if the path exists, False otherwise.
        """
        path = self._convert_to_path(path)
        return os.path.exists(path)

    async def is_file(self, path: Union[Path, str]) -> bool:
        """
        Checks if the given path is a file (not a directory).
        Args:
            path (Path): The path to check.
        Returns:
            bool: True if the path is a file, False otherwise.
        """
        path = self._convert_to_path(path)
        return os.path.isfile(path)

    async def create_directory_if_not_exists(
        self, path: Union[Path, str]
    ) -> None:
        """
        Asynchronously creates a directory if it doesn't exist on the local disk.
        Args:
            path (Path): The directory path to create.
        """  # noqa: E501
        directory_path = self._convert_to_path(path)
        if not directory_path.exists():
            os.makedirs(directory_path, exist_ok=True)

    def _convert_to_path(self, path: Union[Path, str]) -> Path:
        """
        Converts the path to a Path object if it's a string.
        """
        path = Path(path) if isinstance(path, str) else path
        return path
