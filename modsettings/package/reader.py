import os.path

import modsettings.package.v18.reader
from modsettings.formats import ModInfo

NODE_MODULE_INFO = "ModuleInfo"
BEGINNING_OF_FILE = 0


def read_package(pak_path: str) -> ModInfo | None:
	# TODO: check version and use correct uncompressor
	with open(pak_path, "rb") as file:
		file.seek(0, BEGINNING_OF_FILE)
		return modsettings.package.v18.reader.read_package_v18(file)
