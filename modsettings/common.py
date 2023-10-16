from __future__ import annotations

from modsettings import auto_str, ModInfoVariables, auto_repr


@auto_str
@auto_repr
class ModInfo:
	def __init__(self, name: str, folder: str, uuid: str, md5: bytes, version32: int, version64: int):
		self.folder = folder
		self.name = name
		self.uuid = uuid
		self.md5 = md5
		self.version32 = version32
		self.version64 = version64

	@classmethod
	def from_dict(cls, data: dict[str, str | int | bytes]) -> ModInfo:
		return cls(
			data[ModInfoVariables.NAME[0]],
			data[ModInfoVariables.FOLDER[0]],
			data[ModInfoVariables.UUID[0]],
			data[ModInfoVariables.MD5[0]],
			data[ModInfoVariables.VERSION32[0]],
			data[ModInfoVariables.VERSION64[0]]
		)
