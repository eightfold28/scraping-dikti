import requests
import csv
import json
from sets import Set

rest_url = 'https://forlap.ristekdikti.go.id/ajax/listPT/'

univ_ids = Set([])

with open('data_univ.csv', 'rb') as csv_file:
	data_univ = csv.DictReader(csv_file)
	field_names = ['univ_id']
	for row in data_univ:
		response = requests.get(rest_url + row['univ_name'].replace('&', '%26').replace('(', '%28').replace(')', '%29'))
		if response.status_code == 200:
			parsed_response = json.loads(response.text)
			univ_arr = parsed_response['items']
			print(univ_arr)
			if len(univ_arr) > 0:
				for univ_id in univ_arr:
					univ_ids.add(univ_id['value'])
				

with open('data_univ_id.csv', 'w') as csv_file_writer:
	csv_writer = csv.DictWriter(csv_file_writer, fieldnames=field_names)
	csv_writer.writeheader()
	for univ_id in univ_ids:
		csv_writer.writerow({ 'univ_id': str(univ_id) })