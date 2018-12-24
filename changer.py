#!/usr/bin/python3.7
import json

def change_systems_to_dict(file):
	with open(file) as f:
		systems = f.readlines()
		systems_dict = dict()
		for system in systems:
			system = system.rstrip().split('\t')
			systems_dict[system[1]] = system[0]
		with open('systems_dict', 'w') as g:
			g.write(json.dumps(systems_dict))
	print("Success!")

def map_fw_systems_to_ids(file):
	with open(file) as f:
		fw_systems = f.read().splitlines()
		with open("systems_dict") as g:
			system_ids = json.loads((g.read()))
			with open("fw_systems_id", 'w') as h:
				fw_systems_id = dict()
				for i in fw_systems:
					fw_systems_id[i] = system_ids[i]
				h.write(json.dumps(fw_systems_id))
	print("Success!")


if __name__ == "__main__":
	map_fw_systems_to_ids("route")
