import json

with open("data.json") as json_file:
    json_data = json.load(json_file)['results']['collection1']
# x = json.dumps(json_data)
# json1_data = json.loads(x)
# print json1_data
# all_data = json_data["results"]['collection1']

for d in json_data:
	ex = d['exhibit']
	artist = d['artist']
	src = d['image']['src']
	alt = d['image']['alt']
	title = d['title']
	# text = d['period']['text']
	link = d['period']['href']
	info = d['desc']
	print ex
	print artist
	print src
	print alt
	print title
	# print text
	print link
	print info