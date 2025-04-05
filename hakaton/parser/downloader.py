from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests


class HTMLDownloader:
    @staticmethod
    def download_page(url, timeout=10):
        """
        Загружает HTML страницы по URL
        :param url: URL страницы для загрузки
        :param timeout: Таймаут запроса в секундах
        :return: словарь {success: bool, html: str, error: str}
        """
        result = {
            'success': False,
            'html': None,
            'error': None,
            'url': url,
            'base_url': urljoin(url, '/')  # Базовый URL для относительных путей
        }
        
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            result['html'] = response.text
            result['success'] = True
        except requests.exceptions.RequestException as e:
            result['error'] = f"Ошибка загрузки: {str(e)}"
        except Exception as e:
            result['error'] = f"Неизвестная ошибка: {str(e)}"
            
        return result

