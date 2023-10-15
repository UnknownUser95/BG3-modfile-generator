from __future__ import annotations

import struct

from modsettings import auto_str, divide_chunks


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
class FileEntryV18:
	FileEntry18Format = "=256sIHBBII"
	FileEntry18Struct = struct.Struct(FileEntry18Format)

	SIZE = struct.calcsize(FileEntry18Format)

	def __init__(self, buffer):
		entry = FileEntryV18.FileEntry18Struct.unpack(buffer)

		self.name = entry[0].replace(b'\x00', b'').decode("UTF-8")
		offset_in_file_1 = entry[1]
		offset_in_file_2 = entry[2]

		self.offset_in_file = (offset_in_file_2 << 32) | offset_in_file_1

		self.archive_part = entry[3]
		self.flags = entry[4]
		self.size_on_disk = entry[5]
		self.uncompressed_size = entry[6]

	@staticmethod
	def from_buffer(buffer: bytes) -> list[FileEntryV18]:
		if len(buffer) % FileEntryV18.SIZE != 0:
			raise ValueError(f"buffer has an invalid size! ({len(buffer)})")
		return [FileEntryV18(item) for item in list(divide_chunks(buffer, FileEntryV18.SIZE))]