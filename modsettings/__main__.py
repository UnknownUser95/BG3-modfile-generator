import os

from modsettings.package.reader import read_package
from modsettings import MOD_DIR

mods = os.listdir(MOD_DIR)
mods = [mod for mod in mods if mod.endswith(".pak")]

modinfos = []

for mod in mods:
	print(">>", mod)

	try:
		info = read_package(f"{MOD_DIR}/{mod}")

		if info is not None:
			modinfos.append(info)
	except ValueError as e:
		print(f"could not parse {mod}: {e}")
	except NotImplementedError as e:
		print(f"{mod} is of unsupported version")

	print()

# modinfos = [read_package(f"{MOD_DIR}/{mod}") for mod in mods]

[print(modinfo) for modinfo in modinfos]
