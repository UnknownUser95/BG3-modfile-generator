import os

from modsettings import MOD_DIR, MODSETTINGS_FILE, DATA_DIR
from modsettings.package.reader import read_package

if __name__ != "__main__":
	print("run this as main!")
	exit(1)

print(f"Data directory is   '{DATA_DIR}'")
print(f"Modsettings file is '{MODSETTINGS_FILE}'")

print(f"searching for mods in '{MOD_DIR}'...")

mods = os.listdir(MOD_DIR)
mods = [mod for mod in mods if mod.endswith(".pak")]

print(f"found {len(mods)} mods!")
print()

modinfos = []

for mod in mods:
	print(">>", mod)

	try:
		info = read_package(f"{MOD_DIR}/{mod}")

		if info is None:
			print(f"{mod} has no meta file, skipping")
		else:
			modinfos.append(info)
			print("OK")
	except ValueError as e:
		print(f"could not parse {mod}: {e}")
	except NotImplementedError as e:
		print(f"{mod} is of v{e}, which is not implemented yet")
		print("Please open an issue with your mod at https://github.com/UnknownUser95/BG3-modfile-generator/issues, so that I can properly implement the package version")

	print()

# modinfos = [read_package(f"{MOD_DIR}/{mod}") for mod in mods]

[print(modinfo) for modinfo in modinfos]
