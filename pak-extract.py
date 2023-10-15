from __future__ import annotations

import struct
from enum import Enum
import lz4.block
from xml.etree import ElementTree


BEGINNING_OF_FILE = 0

def auto_str(cls):
	def __str__(self):
		return '%s(%s)' % (
			type(self).__name__,
			', '.join('%s=%s' % item for item in vars(self).items())
		)
	cls.__str__ = __str__
	return cls


# lz4.frame.decompress(DATA)
# https://python-lz4.readthedocs.io/en/stable/

# LZ4 encoding
# https://docs.python.org/3/library/struct.html#format-characters


class FileSizes(int, Enum):
	Byte = 1
	UInt16 = 2
	UInt32 = 4
	UInt64 = 8


# from lslib/LSLib/LS/PackageCommon.cs -- LSPKHeader16
# [StructLayout(LayoutKind.Sequential, Pack = 1)]
# internal struct LSPKHeader16
# {
#     public UInt32 Version;
#     public UInt64 FileListOffset;
#     public UInt32 FileListSize;
#     public Byte Flags;
#     public Byte Priority;
#     [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
#     public byte[] Md5;
#     public UInt16 NumParts;
# }
# Header:	4 + 8 + 4 + 1 + 1 + 16 + 2 = 36 bytes
# Note: LSPK as intro -> +4 bytes

# see lslib/LSLib/LS/PackageReader.cs -- ReadFileListV18 and ReadPackageV18

# IMPORTANT: '=' in the format causes the size to be standard, instead of native
# e.g. 'IQI' is 20B, while '=IQI' is 16B

# print("LSPKHeader16", struct.calcsize(LSPKHeader16Format))


@auto_str
class LSPKHeader:
	LSPKHeader16Format = f"=IQIBB{'x' * 16}H"
	LSPKHeader16Struct = struct.Struct(LSPKHeader16Format)
	
	SIZE = struct.calcsize(LSPKHeader16Format)
	
	def __init__(self, buffer):
		header = LSPKHeader.LSPKHeader16Struct.unpack(buffer)
		
		self.version = header[0]
		self.file_list_offset = header[1]
		self.file_list_size = header[2]
		self.flags = header[3]
		self.priority = header[4]
		# self.md5 = header[5]
		self.num_parts = header[5]


# from lslib/LSLib/LS/PackageCommon.cs -- FileEntry18
# [StructLayout(LayoutKind.Sequential, Pack = 1)]
# internal struct FileEntry18
# {
#     [MarshalAs(UnmanagedType.ByValArray, SizeConst = 256)]
#     public byte[] Name;
#     public UInt32 OffsetInFile1;
#     public UInt16 OffsetInFile2;
#     public Byte ArchivePart;
#     public Byte Flags;
#     public UInt32 SizeOnDisk;
#     public UInt32 UncompressedSize;
# }


@auto_str
class FileEntry:
	FileEntry18Format = f"=256sIHBBII"
	FileEntry18Struct = struct.Struct(FileEntry18Format)

	SIZE = struct.calcsize(FileEntry18Format)

	def __init__(self, buffer):
		entry = FileEntry.FileEntry18Struct.unpack(buffer)

		self.name = entry[0].replace(b'\x00', b'').decode("UTF-8")
		offset_in_file_1 = entry[1]
		offset_in_file_2 = entry[2]

		self.offset_in_file = offset_in_file_1 | (offset_in_file_2 << 32) # TODO: make this better

		self.archive_part = entry[3]
		self.flags = entry[4]
		self.size_on_disk = entry[5]
		self.uncompressed_size = entry[6]

	@staticmethod
	def _divide_chunks(l, n):
		# looping till length l
		for i in range(0, len(l), n):
			yield l[i:i + n]

	@staticmethod
	def from_buffer(buffer: bytes) -> list[FileEntry]:
		if len(buffer) % FileEntry.SIZE != 0:
			raise ValueError(f"buffer has an invalid size! ({len(buffer)})")

		return [FileEntry(item) for item in list(FileEntry._divide_chunks(buffer, FileEntry.SIZE))]


# print("FileEntry18", struct.calcsize(FileEntry18Format))

# PackageReader line 348 // Read()

# print("LSPKHeader size:", LSPKHeader.SIZE)


with open("ImprovedUI.pak", 'rb') as file:
	LSPK_signature = file.read(4) # skip LSPK file intro
	header = LSPKHeader(file.read(LSPKHeader.SIZE))
	print(header)
	# skip = file.read(header.file_list_offset)
	file.seek(header.file_list_offset, BEGINNING_OF_FILE)

	num_files = int.from_bytes(file.read(FileSizes.UInt32), "little")
	print("Files:", num_files)

	buf_size = num_files * FileEntry.SIZE
	# print("required buffer:", buf_size)

	compressed_size = int.from_bytes(file.read(FileSizes.UInt32), "little")
	# print("compressed size:", compressed_size)

	compressed_file_list = file.read(compressed_size)
	# print(compressed_file_list)

	decompressed = lz4.block.decompress(compressed_file_list, uncompressed_size=buf_size)
	# print(decompressed)

	files = FileEntry.from_buffer(decompressed)

	for f in files:
		print(f)

		file.seek(f.offset_in_file, BEGINNING_OF_FILE)
		file_data = file.read(f.size_on_disk)
		uncompressed_file = lz4.block.decompress(file_data, uncompressed_size=f.uncompressed_size)
		print(uncompressed_file.decode("UTF-8"))
		break
