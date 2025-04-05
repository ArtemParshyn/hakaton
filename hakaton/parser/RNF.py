from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests



from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class RSCF:
    @staticmethod
    def parse_news_html(html_content, base_url):
        """
        Парсит HTML контент новости
        :param html_content: HTML строка
        :param base_url: Базовый URL для преобразования относительных путей
        :return: словарь с распарсенными данными
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {
            'date': '',
            'title': '',
            'main_image': {'url': '', 'description': ''},
            'content': '',
            'tags': [],
            'success': False,
            'error': None
        }

        try:
            news_block = soup.find('div', class_='b-news-detail')
            if not news_block:
                raise ValueError("Блок новости не найден")

            # Парсинг данных
            result.update({
                'date': RSCF._clean_text(RSCF._parse_date(news_block)),
                'title': RSCF._clean_text(RSCF._parse_title(news_block)),
                'main_image': RSCF._parse_main_image(news_block, base_url),
                'tags': RSCF._parse_tags(news_block),
                'content': RSCF._parse_content(news_block, base_url),
                'success': True
            })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result

    @staticmethod
    def _clean_text(text):
        """Удаляет неразрывные пробелы и лишние whitespace"""
        if not text:
            return text
        return re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()

    @staticmethod
    def _parse_date(news_block):
        date_block = news_block.find('span', class_='news-date-time')
        return date_block.get_text(strip=True) if date_block else ''

    @staticmethod
    def _parse_title(news_block):
        title_block = news_block.find('h1', class_='news-detail-title')
        return title_block.get_text(strip=True) if title_block else ''

    @staticmethod
    def _parse_main_image(news_block, base_url):
        image_block = news_block.find('div', class_='b-news-detail-picture')
        if not image_block:
            return {'url': '', 'description': ''}
            
        img = image_block.find(['img', 'img-wyz'])
        desc = image_block.find('div', class_='news-detail-picture-desc')
        
        img_src = img.get('src') if img else ''
        if img_src and not img_src.startswith(('http://', 'https://')):
            img_src = urljoin(base_url, img_src)
        
        return {
            'url': img_src,
            'description': RSCF._clean_text(desc.get_text(strip=True)) if desc else ''
        }

    @staticmethod
    def _parse_tags(news_block):
        tags_block = news_block.find('div', class_='b-news-detail-tags')
        return [RSCF._clean_text(tag.get_text(strip=True)) for tag in tags_block.find_all('a')] if tags_block else []

    @staticmethod
    def _parse_content(news_block, base_url):
        content_block = news_block.find('div', class_='b-news-detail-content')
        if not content_block:
            return ''
            
        # Клонируем блок, чтобы не изменять оригинальный
        content = BeautifulSoup(str(content_block), 'html.parser')
        
        # Удаляем ненужные блоки
        for unwanted in content.find_all(['div', 'section'], class_=['b-news-detail-tags', 'b-news-detail-see-also']):
            unwanted.decompose()
        
        # Обрабатываем изображения (как обычные img, так и img-wyz)
        for img in content.find_all(['img', 'img-wyz']):
            if img.get('src'):
                img_src = img['src']
                if not img_src.startswith(('http://', 'https://')):
                    img_src = urljoin(base_url, img_src)
                
                # Создаем новый тег img (если это был img-wyz)
                if img.name == 'img-wyz':
                    new_img = content.new_tag('img')
                    new_img['src'] = img_src
                    img.replace_with(new_img)
                else:
                    # Для обычных img оставляем только src
                    img['src'] = img_src
                    for attr in list(img.attrs.keys()):
                        if attr != 'src':
                            del img[attr]
        
        # Получаем HTML и чистим от неразрывных пробелов
        content_html = str(content)
        content_html = content_html.replace('\xa0', ' ')
        
        return content_html

from downloader import HTMLDownloader  # Импорт скачивальщика

url = "https://rscf.ru/news/physics/tonkaya-plenka-znaniy-v-itmo-sozdali-ultratonkie-2d-kristally-dlya-zapisi-i-khraneniya-informatsii/"
downloader_result = HTMLDownloader.download_page(url)

if downloader_result['success']:
    parsed_data = RSCF.parse_news_html(
        downloader_result['html'],
        downloader_result['base_url']
    )
    print(parsed_data)
else:
    print(f"Ошибка при загрузке страницы: {downloader_result['error']}")





# url = "https://rscf.ru/news/found/podvedeny-itogi-otchetnoy-kampanii-po-proektam-zavershennym-v-2024-godu/"
# downloader_result = HTMLDownloader.download_page(url)
# if downloader_result['success']:
#     parsed_data = RSCF.parse_news_html(
#         downloader_result['html'],
#         downloader_result['base_url']
#     )
#     print(parsed_data)