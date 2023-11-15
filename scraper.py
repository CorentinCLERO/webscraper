import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
import pandas as pd
nltk.download('stopwords')
nltk.download('punkt')

# Configuration initiale
base_url = 'https://www.developpez.net/forums/f2196/javascript/bibliotheques-frameworks/react'
visited_urls = set()
max_pages = 5  # Nombre maximal de pages à visiter
word_count = Counter()  # Compteur pour la fréquence des mots
stop_words = set(stopwords.words('french'))  # Stop words en français


def get_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # S'assure que la requête a réussi
        return response
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'An error occurred: {err}')


def clean_and_count_words(text):
    # Nettoyer le texte et enlever la ponctuation
    words = nltk.word_tokenize(text.lower())
    words = [word for word in words if word.isalpha() and word not in stop_words]

    # Mettre à jour le compteur de mots
    word_count.update(words)


def get_all_pages(url, pages_visited):
    if pages_visited >= max_pages:  # Vérifie si le nombre maximal de pages a été visité
        return pages_visited  # Retourne le compteur de pages actuel

    response = get_page(url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Compte et nettoie les mots seulement si ce n'est pas la page de base
        if url != base_url:
            text = soup.get_text()
            clean_and_count_words(text)
            pages_visited += 1  # Incrémente le compteur de pages
            # Affiche l'URL actuelle et le nombre de pages visitées
            print(f"Visiting ({pages_visited}): {url}")

        # Si c'est la page de base, trouvez les liens dans les titres de thread
        if url == base_url:
            thread_links = soup.select('h3.threadtitle a.title')
            for link in thread_links:
                href = link.get('href')
                if href and not href.startswith('http'):
                    href = f"{base_url.rstrip('/forums/f2196/javascript/bibliotheques-frameworks/react')}{href}"

                if href not in visited_urls and pages_visited < max_pages:
                    visited_urls.add(href)
                    # Mise à jour récursive du compteur
                    pages_visited = get_all_pages(href, pages_visited)
                    time.sleep(1)  # Pause pour éviter de surcharger le serveur
    return pages_visited  # Retourne le compteur mis à jour


# Démarre le processus avec 0 page visitée initialement
visited_count = get_all_pages(base_url, 0)
print(f"Total pages visited: {visited_count}")

# Affiche les mots les plus courants
print(word_count.most_common(10))
most_common_words = word_count.most_common(10)

# Transformation en DataFrame pour une utilisation facile avec seaborn
df_words = pd.DataFrame(most_common_words, columns=['word', 'frequency'])

# Création du graphique
plt.figure(figsize=(10, 8))
sns.barplot(x='frequency', y='word', data=df_words, palette='viridis')
plt.title('Top 10 des mots les plus fréquents')
plt.xlabel('Fréquence')
plt.ylabel('Mot')
plt.show()
