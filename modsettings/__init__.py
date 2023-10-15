import platform
import os
import sys
from dataclasses import dataclass
from shutil import copyfile
from enum import Enum


class FileSizes(int, Enum):
	Byte = 1
	UInt16 = 2
	UInt32 = 4
	UInt64 = 8


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


class ModInfoKeys(tuple, Enum):
	FOLDER = ("Folder", LSDataTypes.LSW_STRING)
	NAME = ("Name", LSDataTypes.FIXED_STRING)
	UUID = ("UUID", LSDataTypes.FIXED_STRING)
	MD5 = ("MD5", LSDataTypes.LS_STRING)
	VERSION32 = ("Version", LSDataTypes.INT32)
	VERSION64 = ("Version64", LSDataTypes.INT64)


ALL_MOD_INFO_KEYS_NAMES = [val.value[0] for val in ModInfoKeys]


match platform.system():
	case "Linux":
		STEAM_LIBRARY_FOLDER = sys.argv[1]
		DATA_DIR = f"{STEAM_LIBRARY_FOLDER}/steamapps/compatdata/1086940/pfx/drive_c/users/steamuser/AppData/Local/Larian Studios/Baldur's Gate 3"
	case "Windows":
		# TODO: check if this works
		LOCAL_APPDATA = os.environ['LOCALAPPDATA']
		DATA_DIR = f"{LOCAL_APPDATA}/Larian Studios/Baldur's Gate 3"
	case _:
		print(f"'{platform.system()}' is not supported")
		exit(1)

MOD_DIR = f"{DATA_DIR}/Mods"
MODSETTINGS_DIR = f"{DATA_DIR}/PlayerProfiles/Public/"
MODSETTINGS_FILE = f"{MODSETTINGS_DIR}/modsettings.lsx"
MODSETTINGS_BACKUP_FILE = f"{MODSETTINGS_DIR}/modsettings-backup.lsx"
MODSETTINGS_FALLBACK_FILE = "./modsettings.lsx"

if not os.path.exists(MODSETTINGS_BACKUP_FILE):
	copyfile(MODSETTINGS_FILE, MODSETTINGS_BACKUP_FILE)
	print("backup file created")


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
