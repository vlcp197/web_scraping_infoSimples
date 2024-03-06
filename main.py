from bs4 import BeautifulSoup
from collections import Counter
import json
import requests
import re

url = 'https://infosimples.com/vagas/desafio/commercia/product.html'

resposta_final = {}

STAR = "★"
response = requests.get(url)

parsed_html = BeautifulSoup(response.content, 'html.parser')

title = parsed_html.select_one('h2#product_title').get_text()
brand = parsed_html.select_one('.brand').get_text()

categories = parsed_html.select_one('.current-category').get_text()
categories = re.split(">", categories)
categories = [category.replace(" ", "").replace('\n', "")
              for category in categories]

description = parsed_html.select_one('.proddet')
description = description.find_all("p")
description = [d.get_text() for d in description]
description = " ".join(description).strip()

skus = parsed_html.find_all("div", {"class": "card"})
skus = [{"name": item.select_one(".prod-nome").get_text().strip(),
         "current_price": float(item.select_one(".prod-pnow").get_text().replace("R$", "").replace(",", ".").strip()) if item.select_one(".prod-pnow") is not None else None,
         "old_price": float(item.select_one(".prod-pold").get_text()
                            .replace("R$", "")
                            .replace(",", ".").strip()) if item.select_one(".prod-pold") is not None else None,
         "available": False if "not-avaliable" in item["class"] else True}
        for item in skus]

properties = parsed_html.find_all("table")[0].get_text()
properties = re.split("\n+", properties)
properties = list(filter(None, properties))
properties = dict(zip(properties[::2], properties[1::2]))

reviews = parsed_html.find_all("div", {"class": "analisebox"})
reviews = [{"name": review.find(class_="analiseusername").get_text(),
            "date": review.find(class_="analisedate").get_text(),
            "score": int(Counter(review.find(class_="analisestars").get_text())[STAR]),
            "text": review.find("p").get_text()}
           for review in reviews]

reviews_average_score = parsed_html.find("div", {"id": "comments"}).find("h4")
reviews_average_score = float(re.search(
    r"\d\.\d", reviews_average_score.get_text()).group())

resposta_final['title'] = title
resposta_final["brand"] = brand
resposta_final["categories"] = categories
resposta_final["description"] = description
resposta_final["skus"] = skus
resposta_final["properties"] = properties
resposta_final["reviews"] = reviews
resposta_final["reviews_average_score"] = reviews_average_score
resposta_final["url"] = url

json_resposta_final = json.dumps(resposta_final)

with open('produto.json', 'w', encoding="utf-8") as arquivo_json:
    # arquivo_json.write(json_resposta_final)
    json.dump(resposta_final, arquivo_json, ensure_ascii=False)
