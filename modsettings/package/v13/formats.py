from __future__ import annotations

import struct

from modsettings import auto_str, from_buffer


# [StructLayout(LayoutKind.Sequential, Pack = 1)]
# internal struct FileEntry13
# {
#     [MarshalAs(UnmanagedType.ByValArray, SizeConst = 256)]
#     public byte[] Name
#     public UInt32 OffsetInFile;
#     public UInt32 SizeOnDisk;
#     public UInt32 UncompressedSize;
#     public UInt32 ArchivePart;
#     public UInt32 Flags;
#     public UInt32 Crc;
# }


@auto_str
@from_buffer
class FileEntryV13:
	FileEntryV13Format: str = "=256sIIIIII"
	FileEntryV13Struct: struct.Struct = struct.Struct(FileEntryV13Format)

	SIZE = struct.calcsize(FileEntryV13Format)

	def __init__(self, buffer: bytes):
		entry = FileEntryV13.FileEntryV13Struct.unpack(buffer)

		self.name: str = entry[0].replace(b'\x00', b'').decode("UTF-8")
		self.offset_in_file: int = entry[1]
		self.size_on_disk: int = entry[2]
		self.uncompressed_size: int = entry[3]
		self.archive_part: int = entry[4]
		self.flags: int = entry[5]
		self.crc: int = entry[6]
