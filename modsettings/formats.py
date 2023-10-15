from __future__ import annotations
import struct

from modsettings import auto_str, ModInfoKeys, auto_repr


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
	LSPKHeader16Format = "=IQIBB16sH"
	LSPKHeader16Struct = struct.Struct(LSPKHeader16Format)

	SIZE = struct.calcsize(LSPKHeader16Format)

	def __init__(self, buffer):
		header = LSPKHeader.LSPKHeader16Struct.unpack(buffer)

		self.version = header[0]
		self.file_list_offset = header[1]
		self.file_list_size = header[2]
		self.flags = header[3]
		self.priority = header[4]
		self.md5 = header[5]
		self.num_parts = header[6]


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
	FileEntry18Format = "=256sIHBBII"
	FileEntry18Struct = struct.Struct(FileEntry18Format)

	SIZE = struct.calcsize(FileEntry18Format)

	def __init__(self, buffer):
		entry = FileEntry.FileEntry18Struct.unpack(buffer)

		self.name = entry[0].replace(b'\x00', b'').decode("UTF-8")
		offset_in_file_1 = entry[1]
		offset_in_file_2 = entry[2]

		self.offset_in_file = offset_in_file_1 | (offset_in_file_2 << 32)  # TODO: make this better

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


@auto_str
@auto_repr
class ModInfo:
	def __init__(self, name: str, folder: str, uuid: str, md5: bytes, version32: int, version64: int):
		self.folder = folder
		self.name = name
		self.uuid = uuid
		self.md5 = md5
		self.version32 = version32
		self.version64 = version64

	@classmethod
	def from_dict(cls, data: dict[str, str | int | bytes]) -> ModInfo:
		return cls(
			data[ModInfoKeys.NAME[0]],
			data[ModInfoKeys.FOLDER[0]],
			data[ModInfoKeys.UUID[0]],
			data[ModInfoKeys.MD5[0]],
			data[ModInfoKeys.VERSION32[0]],
			data[ModInfoKeys.VERSION64[0]]
		)

