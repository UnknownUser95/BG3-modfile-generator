from __future__ import annotations

import struct

from modsettings import auto_str, from_buffer


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
@from_buffer
class FileEntryV18:
	FileEntry18Format = "=256sIHBBII"
	FileEntry18Struct = struct.Struct(FileEntry18Format)

	SIZE = struct.calcsize(FileEntry18Format)

	def __init__(self, buffer):
		entry = FileEntryV18.FileEntry18Struct.unpack(buffer)

		self.name: str = entry[0].replace(b'\x00', b'').decode("UTF-8")
		offset_in_file_1: int = entry[1]
		offset_in_file_2: int = entry[2]

		self.offset_in_file: int = (offset_in_file_2 << 32) | offset_in_file_1

		self.archive_part: int = entry[3]
		self.flags: int = entry[4]
		self.size_on_disk: int = entry[5]
		self.uncompressed_size: int = entry[6]
