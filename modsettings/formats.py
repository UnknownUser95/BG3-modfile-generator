from __future__ import annotations

import struct

from modsettings import auto_str, ModInfoVariables, auto_repr


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
class LSPKHeader16:
	LSPKHeader16Format = "=IQIBB16sH"
	LSPKHeader16Struct = struct.Struct(LSPKHeader16Format)

	SIZE = struct.calcsize(LSPKHeader16Format)

	def __init__(self, buffer):
		header = LSPKHeader16.LSPKHeader16Struct.unpack(buffer)

		self.version = header[0]
		self.file_list_offset = header[1]
		self.file_list_size = header[2]
		self.flags = header[3]
		self.priority = header[4]
		self.md5 = header[5]
		self.num_parts = header[6]


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
			data[ModInfoVariables.NAME[0]],
			data[ModInfoVariables.FOLDER[0]],
			data[ModInfoVariables.UUID[0]],
			data[ModInfoVariables.MD5[0]],
			data[ModInfoVariables.VERSION32[0]],
			data[ModInfoVariables.VERSION64[0]]
		)

