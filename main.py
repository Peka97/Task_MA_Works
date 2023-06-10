import requests
from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag
import csv


def get_catalog(response: requests.Response) -> ResultSet:
	soup = BeautifulSoup(response.content, 'html.parser')
	catalog = soup.findAll('div', {
		'class': ['b-common-item', 'b-common-item--catalog-item', 'js-product-item', 'init-product-info']})
	return catalog


def get_url(page_number: int) -> str:
	return f'https://4lapy.ru/catalog/koshki/korm-koshki/?section_id=2&sort=popular&page={page_number}'


def get_id(item: Tag) -> str:
	item_characteristics = item.find('span', text='Артикул')
	id_info = item_characteristics.parent.parent.find('div', class_='b-characteristics-tab__characteristics-value')
	return id_info.text.strip() if id_info else None


def get_link(item: Tag) -> str:
	link_info = item.find('a', class_='b-common-item__description-wrap')
	href = link_info.get('href')
	return f"https://4lapy.ru{href}" if href.startswith('/catalog') else None


def get_name(item: Tag) -> str:
	name_info = item.find('h1', {'class': ['b-title', 'b-title--h1', 'b-title--card']})
	return name_info.text if name_info else None


def get_reg_price(item: Tag) -> str:
	price_info = item.find(
		'span',
		class_=['b-product-information__old-price', 'js-main-old-price', 'js-current-offer-price-old']
	)
	return round(float(price_info.text.strip())) if price_info else None


def get_promo_price(item: Tag) -> str:
	price_info = item.find('span', {
		'class': ['b-product-information__price', 'js-price-product', 'js-current-offer-price', 'js-main-price']})
	return round(float(price_info.text.strip())) if price_info else None


def get_brand(item: Tag) -> str:
	brand_info = item.find('span', {'itemprop': 'brand'})
	return brand_info.text.strip() if brand_info else None


def check_stock(item: Tag) -> bool:
	list_info = item.find(
		'ul', {'class': ['b-product-information__list', 'js-product-information-list']}
	)
	prod_info = list_info.findAll(
		'div', class_='b-product-information__value'
	)
	stock_info = prod_info[-1]

	return True if 'Нет в наличии' not in stock_info else False


def parse_from_link(session: requests.Session, url: str) -> list:
	result = []

	# Получаем каталог товаров и проверяем статус код страницы
	catalog_page = session.get(url)
	if catalog_page.status_code != 200:
		return

	catalog = get_catalog(catalog_page)

	for item in catalog:
		if item:
			link = get_link(item)
			if not link:
				continue

			req = session.get(link)
			current_item = BeautifulSoup(req.content, 'html.parser')
			stock_info = check_stock(current_item)

			if not stock_info:
				continue

			reg_price = get_reg_price(current_item)
			promo_price = get_promo_price(current_item)
			if reg_price is None and promo_price:
				reg_price = promo_price
				promo_price = None

			item_info = [
				get_id(current_item),
				get_name(current_item),
				link,
				reg_price,
				promo_price,
				get_brand(current_item)
			]
			print(item_info)
			result.append(item_info)

	return result


def prepare_csv():
	with open('Task_MA_Works\\result.csv', 'w') as f:
		writer = csv.writer(f, 'excel', delimiter=';')

		# Прописываем заголовки
		fields = ['ID', 'Наименование товара', 'Ссылка на товар', 'Регулярная цена', 'Промо цена', 'Бренд']
		writer.writerow(fields)


def load_to_csv(rows: list[list]) -> None:
	with open('Task_MA_Works\\result.csv', 'a') as f:
		writer = csv.writer(f, 'excel', delimiter=';')
		writer.writerows(rows)


def parsing():
	s = requests.Session()

	# Коды городов для Cookies
	msc_code = '0000073738'
	spb_code = '0000103664'

	# Устанавливаем город
	s.cookies.set('selected_city_code', msc_code)

	# Готовим csv файл
	prepare_csv()

	# Перебираем страницы
	for i in range(1, 1000):
		print('Парсинг страницы #', i)
		four_lapy_url = get_url(i)
		data = parse_from_link(s, four_lapy_url)

		# Проверяем 200 статус код
		if data:
			# Записываем информацию в csv
			load_to_csv(data)
			print('Успешно!')
		else:
			# Выходим, т.к. страниц больше нет
			s.close()
			return


if __name__ == '__main__':
	parsing()
