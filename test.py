from newsapi import NewsApiClient
import requests
import json

# Init
newsapi = NewsApiClient(api_key='4d05b1bf662540e38cdcb3f04920577f')

# /v2/top-headlines
# top_headlines = newsapi.get_top_headlines(q='bitcoin',
#                                           sources='bbc-news,the-verge',
#                                           category='business',
#                                           language='en',
#                                           country='us')


# all_articles = newsapi.get_everything(sources='bbc-news,the-verge',
#                                       domains='bbc.co.uk,techcrunch.com',
#                                       from_param='2022-04-16',
#                                       to='2017-12-12',
#                                       language='en',
#                                       sort_by='relevancy',
#                                       page_size=6, page=1)
# obj = json.dumps(all_articles)
# print(obj[0])
# print(type(all_articles['articles']))
# for a in all_articles['articles']:
#     print(a['urlToImage'])
# top_headlines = newsapi.get_top_headlines(language='en')
# print(top_headlines)
head = requests.get('https://newsapi.org/v2/top-headlines?country=in&apiKey=4d05b1bf662540e38cdcb3f04920577f')
data =  head.json()
print(data['articles'])

# print(type(all_articles))