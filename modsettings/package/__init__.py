import tempfile
from enum import Enum
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from modsettings import SeekOffset, ALL_MOD_INFO_KEYS_NAMES
from modsettings.common import ModInfo


# [Flags]
# public enum PackageFlags
# {
#     /// <summary>
#     /// Allow memory-mapped access to the files in this archive.
#     /// </summary>
#     AllowMemoryMapping = 0x02,
#     /// <summary>
#     /// All files are compressed into a single LZ4 stream
#     /// </summary>
#     Solid = 0x04,
#     /// <summary>
#     /// Archive contents should be preloaded on game startup.
#     /// </summary>
#     Preload = 0x08
# };

class PackageFlags(int, Enum):
	ALLOW_MEM_MAPPING = 0x02
	SOLID = 0x04
	PRELOAD = 0x08


def has_flag(header_flags: int, flag: PackageFlags) -> bool:
	return (header_flags & flag) == flag


class InvalidDataException(BaseException):
	pass


def read_meta(uncompressed_file: bytes) -> ModInfo:
	modinfo: dict[str, str | int] = {key: None for key in ALL_MOD_INFO_KEYS_NAMES}
	NODE_MODULE_INFO: str = "ModuleInfo"

	# TODO: is the meta file the same for all versions?
	with tempfile.TemporaryFile() as tmp:
		tmp.write(uncompressed_file)
		tmp.flush()
		tmp.seek(SeekOffset.BEGINNING)

		meta: ElementTree = ElementTree.parse(tmp)
		# print(meta)
		root: Element = meta.getroot()

		# both Dependencies and ModuleInfo are 'node' elements
		nodes: list[Element] = root.findall("./region/node/children/")
		for node in nodes:
			if node.get('id') == NODE_MODULE_INFO:
				for n in node.findall("./attribute"):
					node_id = n.get('id')
					if node_id in ALL_MOD_INFO_KEYS_NAMES:
						modinfo[node_id] = n.get('value')

	return ModInfo.from_dict(modinfo)
