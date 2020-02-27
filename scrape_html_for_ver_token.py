from bs4 import BeautifulSoup
soup = BeautifulSoup('first-get.html', 'html.parser')
print(soup.prettify())