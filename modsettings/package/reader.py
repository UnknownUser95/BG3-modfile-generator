import os.path

import modsettings.package.v18.reader
from modsettings import SeekOffset, VariableSizes, SIGNATURE_SIZE, SIGNATURE, INT_FORMAT
from modsettings.formats import ModInfo

NODE_MODULE_INFO = "ModuleInfo"
BEGINNING_OF_FILE = 0


def read_package(pak_path: str) -> ModInfo | None:
	# TODO: check version and use correct uncompressor
	with open(pak_path, "rb") as file:
		file.seek(-8, SeekOffset.END)

		header_size = int.from_bytes(file.read(VariableSizes.Int32), INT_FORMAT)
		signature = file.read(SIGNATURE_SIZE)

		if signature == SIGNATURE:
			file.seek(-header_size, SeekOffset.END)
			# read v13
			raise NotImplementedError("v13 is not yet implemented")

		file.seek(0, SeekOffset.BEGINNING)
		signature = file.read(SIGNATURE_SIZE)

		if signature == SIGNATURE:
			version = int.from_bytes(file.read(VariableSizes.Int32), INT_FORMAT)
			match version:
				case 10:
					raise NotImplementedError("v10 is not yet implemented")
				case 15:
					raise NotImplementedError("v15 is not yet implemented")
				case 16:
					raise NotImplementedError("v16 is not yet implemented")
				case 18:
					file.seek(SIGNATURE_SIZE, SeekOffset.BEGINNING)
					return modsettings.package.v18.reader.read_package_v18(file)
				case _:
					raise ValueError(f"Unknown version: {version}")

		file.seek(0, SeekOffset.BEGINNING)
		version = int.from_bytes(file.read(VariableSizes.Int32))

		if version == 7 or version == 9:
			raise NotImplementedError("v7/9 is not yet implemented")

		raise ValueError("No valid package version found")
