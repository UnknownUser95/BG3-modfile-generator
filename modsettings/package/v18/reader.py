import tempfile
from io import BufferedReader
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import lz4.block

from modsettings import VariableSizes, ALL_MOD_INFO_KEYS_NAMES, SeekOffset, INT_FORMAT
from modsettings.formats import LSPKHeader16, ModInfo
from modsettings.package.v18.formats import FileEntryV18

NODE_MODULE_INFO: str = "ModuleInfo"


def read_package_v18(file: BufferedReader) -> ModInfo | None:
	header = LSPKHeader16(file.read(LSPKHeader16.SIZE))
	# print(header)

	if header.version != 18:
		raise ValueError(f"version {header.version} is not supported by the V18 decompressor")

	file.seek(header.file_list_offset, SeekOffset.BEGINNING)

	num_files: int = int.from_bytes(file.read(VariableSizes.Int32), INT_FORMAT)
	# print("Files:", num_files)

	buf_size: int = num_files * FileEntryV18.SIZE
	# print("required buffer:", buf_size)

	compressed_size: int = int.from_bytes(file.read(VariableSizes.Int32), INT_FORMAT)
	# print("compressed size:", compressed_size)

	compressed_file_list: bytes = file.read(compressed_size)
	# print(compressed_file_list)

	decompressed: bytes = lz4.block.decompress(compressed_file_list, uncompressed_size=buf_size)
	# print(decompressed)

	files: list[FileEntryV18] = FileEntryV18.from_buffer(decompressed)

	modinfo: dict[str, str | int] = {key: None for key in ALL_MOD_INFO_KEYS_NAMES}

	has_meta: bool = False

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
			uncompressed_file = lz4.block.decompress(file_data, uncompressed_size=f.uncompressed_size)
		except lz4.block.LZ4BlockError:
			uncompressed_file = file_data
		# print(uncompressed_file.decode("UTF-8"))

		with tempfile.TemporaryFile() as tmp:
			tmp.write(uncompressed_file)
			tmp.flush()
			tmp.seek(SeekOffset.BEGINNING)

			meta: ElementTree = ElementTree.parse(tmp)
			# print(meta)
			root: Element = meta.getroot()

			# TODO: is this the same for all versions?
			# both Dependencies and ModuleInfo are 'node' elements
			nodes: list[Element] = root.findall("./region/node/children/")
			for node in nodes:
				if node.get('id') == NODE_MODULE_INFO:
					for n in node.findall("./attribute"):
						node_id = n.get('id')
						if node_id in ALL_MOD_INFO_KEYS_NAMES:
							modinfo[node_id] = n.get('value')

	if not has_meta:
		print("no meta file, skipping")
		return None

	# print(modinfo)
	return ModInfo.from_dict(modinfo)