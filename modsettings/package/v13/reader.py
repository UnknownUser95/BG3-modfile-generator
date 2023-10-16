from io import BufferedReader

import lz4.block
import lz4.frame

from modsettings import SeekOffset, INT_FORMAT, VariableSize, read_int
from modsettings.common import ModInfo
from modsettings.package import PackageFlags, has_flag, InvalidDataException
from modsettings.package.headers import LSPKHeader13
from modsettings.package.v13.formats import FileEntryV13


def read_package_v13(file: BufferedReader) -> ModInfo | None:
	header = LSPKHeader13(file.read(LSPKHeader13.SIZE))

	if header.version != 18:
		raise ValueError(f"version {header.version} is not supported by the V13 decompressor")

	file.seek(header.file_list_offset, SeekOffset.BEGINNING)

	num_files: int = read_int(file, VariableSize.Int32)

	buf_size: int = FileEntryV13.SIZE * num_files

	compressed_file_list: bytes = file.read(header.file_list_size - 4)

	decompressed: bytes = lz4.block.decompress(compressed_file_list, uncompressed_size=buf_size)

	entries: list[FileEntryV13] = FileEntryV13.from_buffer(decompressed)

	meta: ModInfo | None = None

	if has_flag(header.flags, PackageFlags.SOLID):
		uncompressed_total: int = 0
		size_on_disk: int = 0
		first_offset: int = 0xFFFFFFFF
		last_offset: int = 0

		for entry in entries:
			uncompressed_total += entry.uncompressed_size
			size_on_disk += entry.size_on_disk

			if entry.offset_in_file < first_offset:
				first_offset = entry.offset_in_file
			if entry.offset_in_file > last_offset:
				last_offset = entry.offset_in_file + entry.size_on_disk

		if first_offset != 7 or last_offset - first_offset != size_on_disk:
			raise InvalidDataException(f"invalid solid archive! Offsets: {first_offset}/{last_offset}, Size: {size_on_disk}")

		file.seek(0, SeekOffset.BEGINNING)
		frame: bytes = file.read(last_offset)

		decompressed_frame: bytes = lz4.frame.decompress(frame)

		offset: int = 7
		compressed_offset: int = 0

		for entry in entries:
			if entry.offset_in_file != offset:
				raise InvalidDataException("solid archive is not continuous")

			if entry.name.endswith("meta.lsx"):
				meta = read_content(entry, decompressed_frame, compressed_offset)

			offset += entry.size_on_disk
			compressed_offset += entry.uncompressed_size

	return meta


def read_content(entry: FileEntryV13, frame: bytes, offset: int) -> ModInfo:
	# see PackageCommon.cs -- PackagedFileInfo.MakeStream() (254)
	pass
