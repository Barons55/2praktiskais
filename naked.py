import requests
import json
import datetime
import time
import yaml

from datetime import datetime
print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')

# 
nasa_api_key = "ANUUrdmtO9aTqhZ4XqSfXkonZODkSPvW8keAKnFi"
nasa_api_url = "https://api.nasa.gov/neo/"

# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
print("Generated today's date: " + str(request_date))

# Pieprasas informaciju no NASA API
print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

# Printe NASA pieprasitas atbildes datus
print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text))

# Izpildas tiaki tad ja status_code vienads ar 200
if r.status_code == 200:
	# parveido json failu ptyhon teksta
	json_data = json.loads(r.text)

	# glabajas vertibas
	ast_safe = []
	ast_hazardous = []
	
	# ja ast_count vienads ar json skaitu tad izdruka
	if 'element_count' in json_data:
		ast_count = int(json_data['element_count'])
		print("Asteroid count today: " + str(ast_count))
		
		# ja ast_coun lielaks par 0 tad izpildas
		if ast_count > 0:
			
			# iegust vertibu no json datiem
			for val in json_data['near_earth_objects'][request_date]:
				# ja ir dotas vertibas tad saglaba datus
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
					tmp_ast_name = val['name']
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					# mekle kilometrus val masiva
					if 'kilometers' in val['estimated_diameter']:
						# mekle min un max ieks val
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						#netiek atrasts min un max
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
					# nav kilometru ieks val masiva
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1
					# pieskir vertibu tmp_ast_hazardous
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']
					
					# izpildas ja vertibas objekta ir vairak par 0
					if len(val['close_approach_data']) > 0:
						# mekle vertibas ieks val masiva un ja ir izpilda
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							#pieskir vertibas
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							# mekle vertibas ieks val masiva un ja ir izpilda
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							# ja netiek atrastas vertibas
							else:
								tmp_ast_speed = -1
							# mekle vertibas ieks val masiva un ja ir izpilda
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							#ja netiek atrastas vertibas
							else:
								tmp_ast_miss_dist = -1
						#ja netiek atrastas vertibas val masiva
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					# ja vertibas iekš objekta ir 0 izdruka tekstu un pieskir vertibas
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1

					print("------------------------------------------------------- >>")
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
		# ja nav asteroidu tuvuma zemei
		else:
			print("No asteroids are going to hit earth today")

	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))
	# ja bistamo asteroidu skaits lielaks par 0
	if len(ast_hazardous) > 0:

		ast_hazardous.sort(key = lambda x: x[4], reverse=False)

		print("Today's possible apocalypse (asteroid impact on earth) times:")
		# izprinte informaciju par asteroidiem
		for asteroid in ast_hazardous:
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))

		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
	# ja bistamo asteroidu skaits ir 0
	else:
		print("No asteroids close passing earth today")
# nespēja sanemt atbildi no NASA API
else:
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
