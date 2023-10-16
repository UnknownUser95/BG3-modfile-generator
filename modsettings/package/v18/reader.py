from io import BufferedReader

import lz4.block

from modsettings import VariableSize, SeekOffset, read_int
from modsettings.common import ModInfo
from modsettings.package import read_meta
from modsettings.package.headers import LSPKHeader16
from modsettings.package.v18.formats import FileEntryV18


def read_package_v18(file: BufferedReader) -> ModInfo | None:
	header = LSPKHeader16(file.read(LSPKHeader16.SIZE))
	# print(header)

	if header.version != 18:
		raise ValueError(f"version {header.version} is not supported by the V18 decompressor")

	file.seek(header.file_list_offset, SeekOffset.BEGINNING)

	num_files: int = read_int(file, VariableSize.Int32)
	# print("Files:", num_files)

	buf_size: int = num_files * FileEntryV18.SIZE
	# print("required buffer:", buf_size)

	compressed_size: int = read_int(file, VariableSize.Int32)
	# print("compressed size:", compressed_size)

	compressed_file_list: bytes = file.read(compressed_size)
	# print(compressed_file_list)

	decompressed: bytes = lz4.block.decompress(compressed_file_list, uncompressed_size=buf_size)
	# print(decompressed)

	files: list[FileEntryV18] = FileEntryV18.from_buffer(decompressed)

	modinfo: ModInfo | None = None

	for f in files:
		# print(f)
		if not f.name.endswith("meta.lsx"):
			continue

		has_meta = True

		# print("using", f.name)

		file.seek(f.offset_in_file, SeekOffset.BEGINNING)
		file_data: bytes = file.read(f.size_on_disk)

		# some packages have an uncompressed meta file
		try:
			uncompressed_file: bytes = lz4.block.decompress(file_data, uncompressed_size=f.uncompressed_size)
		except lz4.block.LZ4BlockError:
			uncompressed_file: bytes = file_data

		# print(uncompressed_file.decode("UTF-8"))

		modinfo = read_meta(uncompressed_file)

	# print(modinfo)
	return modinfo
