import os
import platform
import sys
from enum import Enum
from io import BufferedReader
from shutil import copyfile

match platform.system():
	case "Linux":
		if len(sys.argv) < 2:
			raise OSError("path to SteamLibrary folder must be given!")

		STEAM_LIBRARY_FOLDER: str = sys.argv[1]
		DATA_DIR: str = f"{STEAM_LIBRARY_FOLDER}/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3"
	case "Windows": # TODO: check if this works
		LOCAL_APPDATA: str = os.environ['LOCALAPPDATA']
		DATA_DIR: str = f"{LOCAL_APPDATA}/Larian Studios/Baldur's Gate 3"
	case _: # TODO: is MacOS the same as Linux?
		print(f"'{platform.system()}' is not supported")
		exit(1)

MOD_DIR: str = f"{DATA_DIR}/Mods"
MODSETTINGS_DIR: str = f"{DATA_DIR}/PlayerProfiles/Public/"
MODSETTINGS_FILE: str = f"{MODSETTINGS_DIR}/modsettings.lsx"
MODSETTINGS_BACKUP_FILE: str = f"{MODSETTINGS_DIR}/modsettings-backup.lsx"
MODSETTINGS_FALLBACK_FILE: str = "./modsettings.lsx"

if not os.path.exists(MODSETTINGS_BACKUP_FILE):
	copyfile(MODSETTINGS_FILE, MODSETTINGS_BACKUP_FILE)
	print("backup file created")


SIGNATURE: bytes = b'LSPK'
SIGNATURE_SIZE: int = len(SIGNATURE)
INT_FORMAT: str = "little"


class VariableSize(int, Enum):
	Byte = 1
	Int16 = 2
	Int32 = 4
	Int64 = 8


def read_int(file: BufferedReader, var_type: VariableSize) -> int:
	return int.from_bytes(file.read(var_type), INT_FORMAT)


class SeekOffset(int, Enum):
	BEGINNING = 0
	CURRENT_POSITION = 1
	END = 2


# Folder	LSString
# Name		LSString
# UUID		FixedString
# Version	int32
# 	OR
# Version64	int64		only used by Gustav? ignore for now
# MD5		LSString
class LSDataTypes(str, Enum):
	LS_STRING = "LSString"
	LSW_STRING = "LSWString"
	FIXED_STRING = "FixedString"
	INT32 = "int32"
	INT64 = "int64"


class ModInfoVariables(tuple, Enum):
	FOLDER = ("Folder", LSDataTypes.LSW_STRING)
	NAME = ("Name", LSDataTypes.FIXED_STRING)
	UUID = ("UUID", LSDataTypes.FIXED_STRING)
	MD5 = ("MD5", LSDataTypes.LS_STRING)
	VERSION32 = ("Version", LSDataTypes.INT32)
	VERSION64 = ("Version64", LSDataTypes.INT64)


ALL_MOD_INFO_KEYS_NAMES: list[str] = [val[0] for val in ModInfoVariables]


def auto_str(cls):
	def __str__(self):
		return '%s(%s)' % (
			type(self).__name__,
			', '.join('%s=%s' % item for item in vars(self).items())
		)
	cls.__str__ = __str__
	return cls


def auto_repr(cls):
	def __repr__(self):
		return '%s(%s)' % (
			type(self).__name__,
			', '.join('%s=%s' % item for item in vars(self).items())
		)
	cls.__repr__ = __repr__
	return cls


def from_buffer(cls):
	@classmethod
	def from_buffer(cls, buffer: bytes) -> list:
		if len(buffer) % cls.SIZE != 0:
			raise ValueError(f"buffer has an invalid size! ({len(buffer)})")

		return [cls(item) for item in divide_chunks(buffer, cls.SIZE)]

	cls.from_buffer = from_buffer
	return cls


def _div_chunks(l, n):
	# looping till length l
	for i in range(0, len(l), n):
		yield l[i:i + n]


def divide_chunks(l, n) -> list:
	return list(_div_chunks(l, n))
