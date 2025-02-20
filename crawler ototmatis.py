import requests
from bs4 import BeautifulSoup

 
def search_engine(query, engine):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        if engine == "google":
            url = f"https://www.google.com/search?q={query}"
        elif engine == "bing":
            url = f"https://www.bing.com/search?q={query}"
        elif engine == "yahoo":
            url = f"https://search.yahoo.com/search?p={query}"
        elif engine == "duckduckgo":
            url = f"https://duckduckgo.com/?q={query}"
        elif engine == "ecosia":
            url = f"https://www.ecosia.org/search?q={query}"
        elif engine == "startpage":
            url = f"https://www.startpage.com/sp/search?q={query}"
        elif engine == "yandex":
            url = f"https://yandex.com/search/?text={query}"
        elif engine == "baidu":
            url = f"https://www.baidu.com/s?wd={query}"  # Simplified Baidu URL
        elif engine == "naver":
            url = f"https://search.naver.com/search.naver?query={query}"
        elif engine == "ask":
            url = f"https://www.ask.com/web?q={query}"
        elif engine == "aol":
            url = f"https://search.aol.com/aol/search?q={query}"
        elif engine == "dogpile":
            url = f"https://www.dogpile.com/search?q={query}"
        elif engine == "excite":
            url = f"https://www.excite.com/search/web?q={query}"
        elif engine == "info":
            url = f"https://www.info.com/search?q={query}"
        elif engine == "lycos":
            url = f"https://search.lycos.com/?q={query}"
        elif engine == "metacrawler":
            url = f"https://www.metacrawler.com/metacrawler/search?q={query}"
        elif engine == "msn":
            url = f"https://www.msn.com/en-us/search?q={query}"
        elif engine == "petal":
            url = f"https://petalsearch.com/search?q={query}"
        elif engine == "qwant":
            url = f"https://www.qwant.com/?q={query}"
        elif engine == "rambler":
            url = f"https://nova.rambler.ru/search?query={query}"
        elif engine == "searchcom":
            url = f"https://www.search.com/search?q={query}"
        elif engine == "sogou":
            url = f"https://www.sogou.com/web?query={query}"
        elif engine == "swisscows":
            url = f"https://swisscows.com/en/web?query={query}"
        elif engine == "teoma":
            url = f"https://search.teoma.com/search?q={query}"
        elif engine == "walla":
            url = f"https://walla.co.il/?q={query}"
        elif engine == "webcrawler":
            url = f"https://www.webcrawler.com/serp?q={query}"
        elif engine == "wolframalpha":
            url = f"https://www.wolframalpha.com/input/?i={query}"
        elif engine == "zapmeta":
            url = f"https://www.zapmeta.com/web?q={query}"
        elif engine == "192com":
            url = f"https://www.192.com/search/people?q={query}"
        elif engine == "abacho":
            url = f"https://www.abacho.com/search.php?q={query}"
        elif engine == "accoona":
            url = f"https://www.accoona.com/search.php?q={query}"
        elif engine == "acoon":
            url = f"https://www.acoon.com/search.php?q={query}"
        elif engine == "adalta":
            url = f"https://www.adalta.com/search?q={query}"
        elif engine == "adfind":
            url = f"https://www.adfind.com/search?q={query}"
        elif engine == "aeiwi":
            url = f"https://www.aeiwi.com/search?q={query}"
        elif engine == "alltheweb":
            url = f"https://www.alltheweb.com/search?q={query}"
        elif engine == "ansearch":
            url = f"https://www.ansearch.com/search?q={query}"
        elif engine == "arianna":
            url = f"https://www.arianna.it/search?q={query}"
        elif engine == "arios":
            url = f"https://www.arios.com/search?q={query}"
        elif engine == "auone":
            url = f"https://auone.jp/search?q={query}"
        elif engine == "avivo":
            url = f"https://www.avivo.com/search?q={query}"
        elif engine == "azekon":
            url = f"https://www.azekon.com/search?q={query}"
        elif engine == "baidubrother":
            url = f"https://www.baidubrother.com/search?q={query}"
        elif engine == "beekio":
            url = f"https://beek.io/?s={query}"
        elif engine == "befun":
            url = f"https://www.befun.com/search?q={query}"
        elif engine == "biglobe":
            url = f"https://search.biglobe.ne.jp/q/{query}"
        elif engine == "blitzsuche":
            url = f"https://www.blitzsuche.de/start.php?q={query}"
        elif engine == "bluewin":
            url = f"https://www.bluewin.ch/fr/search.html?q={query}"
        elif engine == "boardreader":
            url = f"https://boardreader.com/s/{query}"
        elif engine == "boxxet":
            url = f"https://www.boxxet.com/search?q={query}"
        elif engine == "brainboost":
            url = f"https://www.brainboost.com/search?q={query}"
        elif engine == "bravo":
            url = f"https://www.bravo.de/suche?s={query}"
        elif engine == "business":
            url = f"https://www.business.com/directory/search/?q={query}"
        elif engine == "cauti":
            url = f"https://www.cauti.com/search?q={query}"
        elif engine == "centrata":
            url = f"https://www.centrata.com/search?q={query}"
        elif engine == "chacha":
            url = f"https://www.chacha.com/search?q={query}"
        elif engine == "chlubber":
            url = f"https://www.chlubber.com/search?q={query}"
        elif engine == "clipular":
            url = f"https://clipular.com/search?q={query}"
        elif engine == "cluuz":
            url = f"https://www.cluuz.com/search?q={query}"
        elif engine == "cnn":
            url = f"https://edition.cnn.com/search?q={query}"
        elif engine == "coccinelles":
            url = f"https://www.coccinelles.fr/recherche.php?q={query}"
        elif engine == "colibrism":
            url = f"https://colibri.sm/search?q={query}"
        elif engine == "cosmos":
            url = f"https://www.cosmos.com.my/search?q={query}"
        elif engine == "crawler":
            url = f"https://www.crawler.com/search?q={query}"
        else:  # Handle unknown engines
            print(f"Engine '{engine}' not supported.")
            return None

        response = requests.get(url, headers=headers, verify=True, timeout=delay)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        results = []
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and href.startswith('http'):
                results.append(href)
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error during {engine.capitalize()} search: {e}")
        return None


print("="*20)
print("WHAT DO YOU WANT TO SEARCH\n*\n*")
print("-1.search within 100 searches simultaneously\n-2.web browser\n-3.exit")


while True:
    var=int(input("ENTER YOUR CHOICE :"))
     
    if var==1:

        try:

            if __name__ == "__main__":
                delay=int(input("enter timeout duration :"))
                print("COMMAND FOR SPECIFIC SEARCH :\n*\n1.use double quotes for specific search         2.use + to ensure inclusion in search\n3.use - for exclusion in search           4.search for specific file type (typefile:)\n====================")
                query = input("WHAT DO YOU WANT TO SEARCH : ")
                engines = ["google", "bing", "yahoo", "duckduckgo", "ecosia", "startpage", "yandex", "baidu", "naver", "ask", "aol", "dogpile", "excite", "info", "lycos", "metacrawler", "msn", "petal", "qwant", "rambler", "searchcom", "sogou", "swisscows", "teoma", "walla", "webcrawler", "wolframalpha", "zapmeta", "192com", "abacho", "accoona", "acoon", "adalta", "adfind", "aeiwi", "alltheweb", "ansearch", "arianna", "arios", "auone", "avivo", "azekon", "baidubrother", "beekio", "befun", "biglobe", "blitzsuche", "bluewin", "boardreader", "boxxet", "brainboost", "bravo", "business", "cauti", "centrata", "chacha", "chlubber", "clipular", "cluuz", "cnn", "coccinelles", "colibrism", "cosmos", "crawler"]  # Add your engines here

                for engine in engines:
                    results = search_engine(query, engine)
                    if results:
                        print(f"\n{engine.capitalize()} Results:")
                        for result in results:
                            print(result)
                    print("-" * 20)  # Separator between engines

        except ValueError:
            print("your command failed....")

    elif var==2:
        import webbrowser

        try:
            print("===")
            print("example >>>WWW.GOOGLE.COM ")
            goto=str(input("enter the URL  :"))
            webbrowser.open(goto)
        except:
            print("enter it as the example..")

    elif var ==3:
        break

    else:
        print("PLEASE ENTER A VALID CHOICE.....")
