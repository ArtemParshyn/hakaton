import os

import django
from bs4 import BeautifulSoup
import requests
from RNF import *
from hakaton.api.models import Tag, NewsItem
from hakaton.api.serializer import NewsSerializer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hakaton.settings')

# Initialize Django
django.setup()

# Now import your Django models
from hakaton.api.models import Tag, NewsItem

def parse_news_item(html_content, index=0):
    soup = BeautifulSoup(html_content, 'html.parser')
    news_items = soup.find_all('div', class_='news-item')

    if index >= len(news_items):
        return None

    news_item = news_items[index]

    date_element = news_item.find('div', class_='news-date')
    date = date_element.get_text(strip=True) if date_element else 'Дата не найдена'

    title_element = news_item.find('a', class_='news-title')
    title = title_element.get_text(strip=True) if title_element else 'Заголовок не найден'
    title_link = title_element['href'] if title_element else None

    return {
        'date': date,
        'title': title,
        'link': title_link
    }


def actions(link):
    n = 0
    if (quest_on_db) != True:
        downloader_result = HTMLDownloader.download_page(link)
        print("\n\n\n")
        parsed_data = RSCF.parse_news_html(
            downloader_result['html'],
            downloader_result['base_url'])
        loading_on_db(parsed_data)
        n += 1
    else:
        return


url = 'https://rscf.ru/news/'
response = requests.get(url)
html_content = response.text

first_news = parse_news_item(html_content, 0)
print(first_news)

fifth_news = parse_news_item(html_content, 4)
print(fifth_news)

# url = "https://rscf.ru/" + first_news['link']
# downloader_result = HTMLDownloader.download_page(url)
#
# if downloader_result['success']:
#     parsed_data = RSCF.parse_news_html(
#         downloader_result['html'],
#         downloader_result['base_url']
#     )
#     print(parsed_data)
# else:
#     print(f"Ошибка при загрузке страницы: {downloader_result['error']}")
#

def loading_on_db(parsed_data):
    serializer = NewsSerializer(data={
        'title': 'Новая статья',
        'content': 'Текст статьи...',
        'tags': [Tag.objects.get(name=i) for i in parsed_data["tags"]],
        'sources': [{'name': 'Reuters'}]
    })

    if serializer.is_valid():
        news_item = serializer.save()
    pass


def quest_on_db(date, title, link):
    return NewsItem.objects.all().get(title=title).exists()

quest_on_db(1, 'Битва за урожай: российские ученые вывели особо опасных для колорадского жука микробов', 1)