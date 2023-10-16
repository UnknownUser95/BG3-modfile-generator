import struct

from modsettings import auto_str, INT_FORMAT


# IMPORTANT: '=' in the format causes the size to be standard, instead of native
# e.g. 'IQI' is 20B, while '=IQI' is 16B


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

@auto_str
class LSPKHeader16:
	LSPKHeader16Format: str = "=IQIBB16sH"
	LSPKHeader16Struct: struct.Struct = struct.Struct(LSPKHeader16Format)

	SIZE = struct.calcsize(LSPKHeader16Format)

	def __init__(self, buffer: bytes):
		header = LSPKHeader16.LSPKHeader16Struct.unpack(buffer)

		self.version: int = header[0]
		self.file_list_offset: int = header[1]
		self.file_list_size: int = header[2]
		self.flags: int = header[3]
		self.priority: int = header[4]
		self.md5: bytes = header[5]
		self.num_parts: int = header[6]


# [StructLayout(LayoutKind.Sequential, Pack = 1)]
# internal struct LSPKHeader13
# {
#     public UInt32 Version;
#     public UInt32 FileListOffset;
#     public UInt32 FileListSize;
#     public UInt16 NumParts;
#     public Byte Flags;
#     public Byte Priority;
#     [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
#     public byte[] Md5;
# }

@auto_str
class LSPKHeader13:
	LSPKHeader13Format: str = "=IIIHBB16s"
	LSPKHeader13Struct: struct.Struct = struct.Struct(LSPKHeader13Format)

	SIZE = struct.calcsize(LSPKHeader13Format)

	def __init__(self, buffer: bytes):
		header = LSPKHeader13.LSPKHeader13Struct.unpack(buffer)

		self.version: int = header[0]
		self.file_list_offset: int = header[1]
		self.file_list_size: int = header[2]
		self.num_parts: int = header[3]
		self.flags: int = header[4]
		self.priority: int = header[5]
		self.md5: bytes = header[6]
