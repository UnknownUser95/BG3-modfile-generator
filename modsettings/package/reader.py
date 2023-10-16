import os.path

import modsettings.package.v18.reader
from modsettings import SeekOffset, VariableSize, SIGNATURE_SIZE, SIGNATURE, read_int
from modsettings.common import ModInfo


# see lslib/LSLib/LS/PackageReader.cs -- ReadFileListV18 and ReadPackageV18


def read_package(pak_path: str) -> ModInfo | None:
	# TODO: check version and use correct uncompressor
	with open(pak_path, "rb") as file:
		file.seek(-8, SeekOffset.END)

		header_size: int = read_int(file, VariableSize.Int32)
		signature: bytes = file.read(SIGNATURE_SIZE)

		if signature == SIGNATURE:
			file.seek(-header_size, SeekOffset.END)
			# return modsettings.package.v13.reader.read_package_v13(file)
			raise NotImplementedError(13)

		file.seek(0, SeekOffset.BEGINNING)
		signature: bytes = file.read(SIGNATURE_SIZE)

		if signature == SIGNATURE:
			version: int = read_int(file, VariableSize.Int32)
			match version:
				case 10:
					raise NotImplementedError(10)
				case 15:
					raise NotImplementedError(15)
				case 16:
					raise NotImplementedError(16)
				case 18:
					file.seek(SIGNATURE_SIZE, SeekOffset.BEGINNING)
					return modsettings.package.v18.reader.read_package_v18(file)
				case _:
					raise ValueError(f"Unknown version: {version}")

		file.seek(0, SeekOffset.BEGINNING)
		version: int = read_int(file, VariableSize.Int32)

		if version == 7 or version == 9:
			raise NotImplementedError(7, 9)

		raise ValueError("No valid package version found")
