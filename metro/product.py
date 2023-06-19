from bs4 import BeautifulSoup
from bs4.element import Tag


class Product:
	def __init__(self, soup: BeautifulSoup, link: str):
		self.article = self.__get_article(soup)
		self.name = self.__get_name(soup)
		self.link = link
		self.reg_price, self.promo_price = self.__get_prices(soup)
		self.brand_name = self.__get_brand_name(soup)

	@staticmethod
	def __get_article(soup: BeautifulSoup) -> str | None:
		article_tag: Tag = soup.find('p', {'itemprop': 'productID'})
		article = article_tag.getText().replace('Артикул: ', '').strip() if article_tag else None
		return article

	@staticmethod
	def __get_name(soup: BeautifulSoup) -> str | None:
		name_tag: Tag = soup.find('meta', {'itemprop': 'name'})
		name = name_tag.attrs.get('content') if name_tag else None
		return name

	@staticmethod
	def __get_price(tag: Tag) -> str | None:
		rubles_tag = tag.find('span', {'class': 'product-price__sum-rubles'})
		rubles = rubles_tag.getText().strip() if rubles_tag else ''

		penny_tag = tag.find('span', {'class': 'product-price__sum-penny'})
		penny = penny_tag.getText().strip() if penny_tag else ''

		return f'{rubles}{penny}' if rubles or penny else None

	def __get_prices(self, soup: BeautifulSoup) -> str | None:
		prices = soup.findAll('span', {'class': 'product-price__sum'})

		reg_price_tag: Tag = prices[0]
		reg_price = self.__get_price(reg_price_tag)

		promo_price_tag: Tag = prices[1]
		promo_price = self.__get_price(promo_price_tag)

		return reg_price, promo_price

	@staticmethod
	def __get_brand_name(soup: BeautifulSoup) -> str | None:
		brand_name_tag: Tag = soup.find('a',
										{'class': 'product-attributes__list-item-link reset-link active-blue-text'})
		brand_name = brand_name_tag.getText().strip() if brand_name_tag else None
		return brand_name
