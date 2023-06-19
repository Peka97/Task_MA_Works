import csv

from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
from bs4.element import Tag

from product import Product


class MetroAPI:
	base_url = 'https://online.metro-cc.ru'
	driver = Chrome()
	path = '.\\result.csv'
	headers = ['ID', 'Name', 'URL', 'Regular Price', 'Promo Price', 'Brand Name']

	def __get_soup(self, url: str) -> BeautifulSoup:
		self.driver.get(url)
		src = self.driver.page_source
		return BeautifulSoup(src, 'html.parser')

	@staticmethod
	def __status_eq_200(soup: BeautifulSoup) -> bool:
		not_found = soup.find('h1', {'class': 'error-page__description-title'})
		return False if not_found else True

	@staticmethod
	def __check_availability(tag: Tag) -> bool:
		out_of_stock = tag.findChild('p', {'is-out-of-stock': 'true'})
		return False if out_of_stock else True

	def get_catalog(self, category: str, subcategory: str) -> list[Product]:
		catalog = []
		page = 1
		counter = 1

		while True:
			url = f'{self.base_url}/category/{category}/{subcategory}?page={page}&order=popularity_desc'
			soup = self.__get_soup(url)
			if not self.__status_eq_200(soup):
				break

			products = soup.findAll('div', {'class': 'product-card__top'})
			if not products:
				break

			for prod in products:
				if self.__check_availability(prod):
					child: Tag = prod.findChild('a', {'data-qa': 'product-card-photo-link'})
					prod_href = child.attrs.get('href')
					prod_url = self.base_url + prod_href
					prod_soup = self.__get_soup(prod_url)
					prod_obj = Product(prod_soup, prod_url)
					catalog.append(prod_obj)
					print(f'\rПродуктов в каталоге: {counter}', end='')
					counter += 1
			page += 1

		return catalog

	def parse_to_csv(self, catalog: list[Product], path: str = None) -> None:
		if not path:
			path = self.path

		with open(path, 'w') as fp:
			writer = csv.writer(fp, delimiter=';')
			writer.writerow(self.headers)
			for prod in catalog:
				prod_info = [
					prod.article,
					prod.name,
					prod.link,
					prod.reg_price,
					prod.promo_price,
					prod.brand_name
				]
				writer.writerow(prod_info)

		print(f'\nСохранено по пути {path}')
