from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class ScienceRFNewsParser:
    @staticmethod
    def parse_news_html(html_content, base_url=''):
        """
        Парсит HTML страницу новости (аналог RSCF.parse_news_html)
        
        :param html_content: HTML страница в виде строки
        :param base_url: Базовый URL для преобразования относительных ссылок
        :return: словарь с данными новости
        """
        return ScienceRFNewsParser.parse_news_page(html_content, base_url)

    @staticmethod
    def parse_news_page(html_content, base_url=''):
        """
        Основной метод парсинга страницы новости
        
        :param html_content: HTML страница в виде строки
        :param base_url: Базовый URL для преобразования относительных ссылок
        :return: словарь с данными новости
        """
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
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Парсинг основных данных
            result['date'] = ScienceRFNewsParser._clean_text(ScienceRFNewsParser._parse_date(soup))
            result['title'] = ScienceRFNewsParser._clean_text(ScienceRFNewsParser._parse_title(soup))
            
            # Парсинг контента
            content_block = soup.find('div', class_='u-news-detail-page__text-content')
            if content_block:
                result['content'] = ScienceRFNewsParser._parse_content(content_block, base_url)
                result['main_image'] = ScienceRFNewsParser._parse_main_image(content_block, base_url)
            
            result['tags'] = ScienceRFNewsParser._parse_tags(soup)
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result

    @staticmethod
    def _clean_text(text):
        """Удаляет неразрывные пробелы и лишние whitespace"""
        if not text:
            return text
        return re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()

    @staticmethod
    def _parse_date(soup):
        date_block = soup.find('time', class_='u-news-detail__date')
        return date_block.get_text(strip=True) if date_block else ''

    @staticmethod
    def _parse_title(soup):
        title_block = soup.find('h1', class_='u-inner-header__title')
        return title_block.get_text(strip=True) if title_block else ''

    @staticmethod
    def _parse_main_image(news_block, base_url):
        # Ищем как обычные img, так и img-wyz
        img = news_block.find(['img', 'img-wyz'])
        if img:
            src = img.get('src')
            if src:
                # Преобразуем в абсолютный URL только если это не уже абсолютный URL
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                
                return {
                    'url': src,
                    'description': ScienceRFNewsParser._clean_text(img.get('alt', ''))
                }
        return {'url': '', 'description': ''}

    @staticmethod
    def _parse_tags(soup):
        return []  # Тегов нет по условию

    @staticmethod
    def _parse_content(content_block, base_url):
        # Клонируем блок, чтобы не изменять оригинальный
        content = BeautifulSoup(str(content_block), 'html.parser')
        
        # Преобразуем все img-wyz в обычные img, оставляя только src
        for img_wyz in content.find_all('img-wyz'):
            src = img_wyz.get('src')
            if src:
                # Создаем новый тег img
                new_img = content.new_tag('img')
                # Преобразуем в абсолютный URL если нужно
                if not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                new_img['src'] = src
                # Заменяем img-wyz на новый img
                img_wyz.replace_with(new_img)
        
        # Обрабатываем обычные изображения - делаем ссылки абсолютными
        for img in content.find_all('img'):
            if img.get('src'):
                img_src = img['src']
                if not img_src.startswith(('http://', 'https://')):
                    img['src'] = urljoin(base_url, img_src)
                # Удаляем все атрибуты кроме src
                for attr in list(img.attrs.keys()):
                    if attr != 'src':
                        del img[attr]
        
        # Очистка ненужных элементов
        for unwanted in content.find_all(['script', 'style']):
            unwanted.decompose()
        
        # Получаем HTML и чистим от неразрывных пробелов
        content_html = str(content)
        content_html = content_html.replace('\xa0', ' ')
        
        return content_html


# Пример использования (как в вашем коде):
if __name__ == "__main__":
    from downloader import HTMLDownloader  # Импорт скачивальщика

    url = "https://наука.рф/news/samye-interesnye-otkrytiya-uchenykh-za-pervuyu-nedelyu-aprelya/"
    downloader_result = HTMLDownloader.download_page(url)

    if downloader_result['success']:
        parsed_data = ScienceRFNewsParser.parse_news_html(
            downloader_result['html'],
            downloader_result['base_url']
        )
        print(parsed_data)
    else:
        print(f"Ошибка при загрузке страницы: {downloader_result['error']}")