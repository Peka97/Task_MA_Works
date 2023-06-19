from metro_api import MetroAPI


if __name__ == '__main__':
	api = MetroAPI()
	catalog = api.get_catalog('bakaleya', 'makaronnye-izdeliya')
	api.parse_to_csv(catalog)
