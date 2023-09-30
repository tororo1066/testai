
import requests
from bs4 import BeautifulSoup

url = "https://dak.gg/er/characters/DebiMarlene?teamMode=SQUAD&weaponType=TwoHandSword&tier=diamond_plus"
response = requests.get(url, cookies={"locale": "en"})
soup = BeautifulSoup(response.text, "html.parser")

# CSSセレクタを使用して要素を選択
element = soup.select_one("#content-container > section.bg-contain.bg-no-repeat > dl > div:nth-child(1) > dd")

print(element.next_element.text)
print(element.select_one("#content-container > section.bg-contain.bg-no-repeat > dl > div:nth-child(1) > dd > span").text)
