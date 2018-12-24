#!/usr/bin/python3.7

import json
import os

from shared_flow import send_waypoint
from shared_flow import get_access_token

def route_optimizer(systems):
	with open(systems) as f:
		systems = f.read().splitlines()
	with open("systems_dict") as f:
		systems_id = json.loads(f.read())
	route = [None] * len(systems)
	systems = dict(zip(systems, [i for i in range(len(systems))]))
	response = "http://www.tikktokk.co/route?w="
	print(f"\n{'-' * 18}Level 4 FW Missions Route Optimizer by Spidi{'-' * 18}")
	print("Pass mission systems to optimize your route! (case insensitive)")
	print("To finilize your route type in \"!End\"")
	print("-" * 80)
	print('\n')
	while 1:
		waypoint = input("Waypoint: ").title()
		# print(f"[DEBUG] Input: ({waypoint}, type: {type(waypoint)})")
		if waypoint != "!End":
			if waypoint in systems:
				route[systems[waypoint]] = systems_id[waypoint]
				print("\tWaypoint added!")
			else:
				print("[ERROR] Wrong mission system, try again!")
		else:
			break
	route = list(filter(None.__ne__, route))
	print(f"{'-' * 80}\nRoute optimizing finished!\n")
	# print("Copy this link to pass your route directly to EVE!")
	# print(response + ",".join(route))
	saved_characters = os.listdir("./characters/")
	characters_data = dict()
	character_names = []
	for character_id in saved_characters:
		with open(f"./characters/{character_id}") as f:
			file_data = json.loads(f.read())
			characters_data[character_id] = file_data
			character_names.append((character_id, file_data['character_name']))
	print("Your characters:")
	for index, character in enumerate(character_names, 1):
		print(f"{index}. {character[1]}")
	print('-' * 80)
	print("Type in number of characters you want to load the route onto (eg. \"1 2 3 4\")")
	choosen_characters = input("Characters: ").strip().split(" ")
	print("Starting to import routes...")
	for index in choosen_characters:
		character_id = character_names[int(index)-1][0]
		print(f"Character: {character_names[int(index)-1][1]}")
		print(f"\tGetting access token...")
		access_token = get_access_token(os.environ['CLIENT_ID'], characters_data[character_id]['refresh_token'], verbose=False)
		if access_token:
			print("\tSuccess!")
		print(f"\tImporting route...")
		error = False
		first_waypoint = True
		for waypoint in route:
			custom_waypoint = {}
			if first_waypoint:
				custom_waypoint["clear_other_waypoints"] = "true"
				first_waypoint = False
			res = send_waypoint(access_token, waypoint, custom_waypoint)
			if res.status_code != 204:
				error = True
				print(f"\t[ERROR] Error occured! Waypoint: {waypoint}, character_id: {character_id}, error_code: {res.status_code}")
		if not error:
			print(f"[Success] Route was imported!")
		else:
			print(f"[ERROR] Error occured while importing the route!")
	print('-' * 80)
	print("[Success] Finished importing route to all selected characters")

if __name__ == "__main__":
	route_optimizer("route")