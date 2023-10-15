from modsettings.formats import FileEntry, LSPKHeader, ModInfo
from modsettings import FileSizes, ALL_MOD_INFO_KEYS_NAMES, BG3_PACKAGE_VERSION
import lz4.block
import tempfile
from xml.etree import ElementTree

NODE_MODULE_INFO = "ModuleInfo"
BEGINNING_OF_FILE = 0


def read_package(pak_path: str) -> ModInfo | None:
	with open(pak_path, 'rb') as file:
		LSPK_signature = file.read(4)  # skip LSPK file intro

		if LSPK_signature != "LSPK".encode("UTF-8"):
			raise ValueError("LSPK intro does not match!")

		header = LSPKHeader(file.read(LSPKHeader.SIZE))
		# print(header)

		if header.version != BG3_PACKAGE_VERSION:
			raise ValueError(f"version {header.version} is not supported")

		file.seek(header.file_list_offset, BEGINNING_OF_FILE)

		num_files = int.from_bytes(file.read(FileSizes.UInt32), "little")
		# print("Files:", num_files)

		buf_size = num_files * FileEntry.SIZE
		# print("required buffer:", buf_size)

		compressed_size = int.from_bytes(file.read(FileSizes.UInt32), "little")
		# print("compressed size:", compressed_size)

		compressed_file_list = file.read(compressed_size)
		# print(compressed_file_list)

		decompressed = lz4.block.decompress(compressed_file_list, uncompressed_size=buf_size)
		# print(decompressed)

		files: list[FileEntry] = FileEntry.from_buffer(decompressed)

		modinfo: dict[str, str | int] = {key: None for key in ALL_MOD_INFO_KEYS_NAMES}

		has_meta: bool = False

		for f in files:
			# print(f)
			if not f.name.endswith("meta.lsx"):
				continue

			has_meta = True

			# print("using", f.name)

			file.seek(f.offset_in_file, BEGINNING_OF_FILE)
			file_data = file.read(f.size_on_disk)

			try:
				uncompressed_file = lz4.block.decompress(file_data, uncompressed_size=f.uncompressed_size)
			except lz4.block.LZ4BlockError:
				uncompressed_file = file_data
			# print(uncompressed_file.decode("UTF-8"))

			with tempfile.TemporaryFile() as tmp:
				tmp.write(uncompressed_file)
				tmp.flush()
				tmp.seek(BEGINNING_OF_FILE)

				meta = ElementTree.parse(tmp)
				# print(meta)
				root = meta.getroot()

				# both Dependencies and ModuleInfo are 'node' elements
				nodes = root.findall("./region/node/children/")
				for node in nodes:
					if node.get('id') == NODE_MODULE_INFO:
						for n in node.findall("./attribute"):
							node_id = n.get('id')
							if node_id in ALL_MOD_INFO_KEYS_NAMES:
								modinfo[node_id] = n.get('value')

		if not has_meta:
			print(f"'{pak_path[pak_path.rfind('/')+1:]}' has no meta file, skipping")
			return None

		print(modinfo)
		return ModInfo.from_dict(modinfo)