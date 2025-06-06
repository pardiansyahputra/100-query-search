import requests
from bs4 import BeautifulSoup
import webbrowser
import customtkinter as ctk
import json
import threading
import time
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

ctk.set_appearance_mode("System") # Default system mode
ctk.set_default_color_theme("blue") # Default color theme

# --- Specific Parser Functions for Each Search Engine ---
# Important: Search engine HTML structures often change.
# These parsers might need adjustments in the future if site changes occur.

def parse_google_results(soup):
    results = []
    for g_result in soup.find_all('div', class_='g'):
        link_tag = g_result.find('a', href=True)
        if link_tag and link_tag['href'].startswith('http'):
            href = link_tag['href']
            # Filter Google's internal URLs (redirects, cache, search related)
            if "google.com/url?" not in href and \
               "webcache.googleusercontent.com" not in href and \
               "/search?q=" not in href and \
               "accounts.google.com" not in href:
                results.append(href)
    return results

def parse_bing_results(soup):
    results = []
    for b_result in soup.find_all('li', class_='b_algo'):
        link_tag = b_result.find('h2')
        if link_tag:
            a_tag = link_tag.find('a', href=True)
            if a_tag and a_tag['href'].startswith('http'):
                results.append(a_tag['href'])
    return results

def parse_duckduckgo_results(soup):
    results = []
    for result_div in soup.find_all('div', class_='web-result'):
        link_tag = result_div.find('a', class_='result__url', href=True)
        if link_tag and link_tag['href'].startswith('http'):
            results.append(link_tag['href'])
    return results

def search_engine(query, engine_name, engine_url_template, delay=1):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    url = engine_url_template.format(query=query)

    try:
        response = requests.get(url, headers=headers, verify=True, timeout=15) # Increased timeout
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        
        parsed_results = []
        if engine_name.lower() == "google":
            parsed_results = parse_google_results(soup)
        elif engine_name.lower() == "bing":
            parsed_results = parse_bing_results(soup)
        elif engine_name.lower() == "duckduckgo":
            parsed_results = parse_duckduckgo_results(soup)
        else:
            # Fallback parser: Grab all valid links. 
            # This might not be as accurate as specific parsers.
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Only add if it's a full web URL
                if href.startswith('http://') or href.startswith('https://'):
                    parsed_results.append(href)
            
        return {"engine": engine_name, "status": "Success", "message": "Search successful.", "results": parsed_results[:20]} # Limit to 20 results

    except requests.exceptions.Timeout:
        return {"engine": engine_name, "status": "Error", "message": f"Request to {engine_name.capitalize()} timed out.", "results": []}
    except requests.exceptions.RequestException as e:
        return {"engine": engine_name, "status": "Error", "message": f"An error occurred while searching on {engine_name.capitalize()}: {e}", "results": []}
    except Exception as e:
        return {"engine": engine_name, "status": "Error", "message": f"An unexpected error occurred: {e}", "results": []}

class SearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Search Application")
        self.geometry("1000x650") 

        self.engines_file = "search_engines.json"
        self.available_engines = self.load_engines()

        # Initialize categories with empty lists
        self.engine_categories = {
            "General": [], 
            "Images": [],
            "Videos": [],
            "News": [],
            "Academic": [],
            "Social": [],
            "Shopping": [],
            "Q&A": []
        }
        self.listboxes_by_category = {} # Will hold scrollable frames for each category
        self._current_selected_engine = None
        self._search_in_progress = False

        self.config_file = "app_config.json"
        self.load_config()

        self.create_widgets()
        # Call update_all_category_listboxes after widgets are created
        self.update_all_category_listboxes()
        
    def load_engines(self):
        """Loads the list of search engines from a JSON file or uses defaults."""
        try:
            with open(self.engines_file, 'r') as f:
                engines = json.load(f)
                # Basic format validation
                if not all(isinstance(k, str) and isinstance(v, str) and '{query}' in v for k, v in engines.items()):
                    raise ValueError("Invalid search engine file format.")
                return engines
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # If file not found, corrupted, or invalid format, use defaults
            print("search_engines.json not found or corrupted. Creating from defaults.")
            default_engines = {
                # --- General Search Engines ---
                "google": "https://www.google.com/search?q={query}",
                "bing": "https://www.bing.com/search?q={query}",
                "yahoo": "https://search.yahoo.com/search?p={query}",
                "duckduckgo": "https://duckduckgo.com/?q={query}",
                "ecosia": "https://www.ecosia.org/search?q={query}",
                "startpage": "https://www.startpage.com/sp/search?q={query}",
                "yandex": "https://yandex.com/search/?text={query}",
                "baidu": "https://www.baidu.com/s?wd={query}",
                "naver": "https://search.naver.com/search.naver?query={query}",
                "ask": "https://www.ask.com/web?q={query}",
                "aol": "https://search.aol.com/aol/search?q={query}",
                "dogpile": "https://www.dogpile.com/search?q={query}",
                "excite": "https://www.excite.com/search/web?q={query}",
                "info": "https://www.info.com/search?q={query}",
                "lycos": "https://search.lycos.com/?q={query}",
                "metacrawler": "https://www.metacrawler.com/metacrawler/search?q={query}",
                "msn": "https://www.msn.com/en-us/search?q={query}",
                "petal": "https://petalsearch.com/search?q={query}",
                "qwant": "https://www.qwant.com/?q={query}",
                "rambler": "https://nova.rambler.ru/search?query={query}",
                "searchcom": "https://www.search.com/search?q={query}",
                "sogou": "https://www.sogou.com/web?query={query}",
                "swisscows": "https://swisscows.com/en/web?query={query}",
                "teoma": "https://search.teoma.com/search?q={query}",
                "walla": "https://walla.co.il/?q={query}",
                "webcrawler": "https://www.webcrawler.com/serp?q={query}",
                "wolframalpha": "https://www.wolframalpha.com/input/?i={query}",
                "zapmeta": "https://www.zapmeta.com/web?q={query}",
                "192com": "https://www.192.com/search/people?q={query}",
                "abacho": "https://www.abacho.com/search.php?q={query}",
                "accoona": "https://www.accoona.com/search.php?q={query}",
                "acoon": "https://www.acoon.com/search.php?q={query}",
                "adalta": "https://www.adalta.com/search?q={query}",
                "adfind": "https://www.adfind.com/search?q={query}",
                "aeiwi": "https://www.aeiwi.com/search?q={query}",
                "alltheweb": "https://www.alltheweb.com/search?q={query}",
                "ansearch": "https://www.ansearch.com/search?q={query}",
                "arianna": "https://www.arianna.it/search?q={query}",
                "arios": "https://www.arios.com/search?q={query}",
                "auone": "https://auone.jp/search?q={query}",
                "avivo": "https://www.avivo.com/search?q={query}",
                "azekon": "https://www.azekon.com/search?q={query}",
                "baidubrother": "https://www.baidubrother.com/search?q={query}",
                "beekio": "https://beek.io/?s={query}",
                "befun": "https://www.befun.com/search?q={query}",
                "biglobe": "https://search.biglobe.ne.jp/q/{query}",
                "blitzsuche": "https://www.blitzsuche.de/start.php?q={query}",
                "bluewin": "https://www.bluewin.ch/fr/search.html?q={query}",
                "boardreader": "https://boardreader.com/s/{query}",
                "boxxet": "https://www.boxxet.com/search?q={query}",
                "brainboost": "https://www.brainboost.com/search?q={query}",
                "bravo": "https://www.bravo.de/suche?s={query}",
                "business": "https://www.business.com/directory/search/?q={query}",
                "cauti": "https://www.cauti.com/search?q={query}",
                "centrata": "https://www.centrata.com/search?q={query}",
                "chacha": "https://www.chacha.com/search?q={query}",
                "chlubber": "https://www.chlubber.com/search?q={query}",
                "clipular": "https://clipular.com/search?q={query}",
                "cluuz": "https://www.cluuz.com/search?q={query}",
                "cnn": "https://edition.cnn.com/search?q={query}", # This could also go into news, but since `cnn` is specific, it can be general
                "coccinelles": "https://www.coccinelles.fr/recherche.php?q={query}",
                "colibrism": "https://colibri.sm/search?q={query}",
                "cosmos": "https://www.cosmos.com.my/search?q={query}",
                "crawler": "https://www.crawler.com/search?q={query}",
                
                # --- Image Search Engines ---
                "google_images": "https://www.google.com/search?q={query}&tbm=isch",
                "bing_images": "https://www.bing.com/images/search?q={query}",
                "flickr": "https://www.flickr.com/search/?text={query}",
                "pinterest": "https://www.pinterest.com/search/pins/?q={query}",
                "getty_images": "https://www.gettyimages.com/search/{query}",
                "unsplash": "https://unsplash.com/s/photos/{query}",
                "pexels": "https://www.pexels.com/search/{query}/",
                "pixabay": "https://pixabay.com/images/search/{query}/",
                "shutterstock": "https://www.shutterstock.com/search/{query}",
                "deviantart": "https://www.deviantart.com/search?q={query}",
                "google_arts_culture": "https://artsandculture.google.com/search/{query}",

                # --- Video Search Engines ---
                "youtube": "https://www.youtube.com/results?search_query={query}", # This URL is a bit unusual, might need checking
                "vimeo": "https://vimeo.com/search?q={query}",
                "dailymotion": "https://www.dailymotion.com/search/{query}",
                "metacafe": "https://www.metacafe.com/videos/?query={query}",
                "twitch_channels": "https://www.twitch.tv/search?query={query}&type=channels",
                "twitch_videos": "https://www.twitch.tv/search?query={query}&type=videos",
                "internet_archive_videos": "https://archive.org/details/movies?query={query}",

                # --- News Search Engines ---
                "google_news": "https://news.google.com/search?q={query}",
                "bing_news": "https://www.bing.com/news/search?q={query}",
                "reuters": "https://www.reuters.com/search/news?q={query}",
                "bbc_news": "https://www.bbc.com/search?q={query}",
                "cnn_news": "https://edition.cnn.com/search?q={query}",
                "al_jazeera": "https://www.aljazeera.com/search/{query}",
                "the_guardian": "https://www.theguardian.com/search?q={query}",
                "new_york_times": "https://www.nytimes.com/search?query={query}",
                "associated_press": "https://apnews.com/search?q={query}",
                "kompas_id": "https://www.kompas.com/search?q={query}",
                "detik_id": "https://www.detik.com/search?query={query}",

                # --- Academic/Scientific Search Engines ---
                "google_scholar": "https://scholar.google.com/scholar?q={query}",
                "semantic_scholar": "https://www.semanticscholar.org/search?q={query}",
                "pubmed": "https://pubmed.ncbi.nlm.nih.gov/?term={query}",
                "researchgate": "https://www.researchgate.net/search?q={query}",
                "academia_edu": "https://www.academia.edu/search?q={query}",
                "jstor": "https://www.jstor.org/action/doBasicSearch?Query={query}",
                "sciencedirect": "https://www.sciencedirect.com/search?qs={query}",
                "ieee_xplore": "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={query}",
                "arxiv": "https://arxiv.org/search/?query={query}&searchtype=all&source=header",
                "philpapers": "https://philpapers.org/s/{query}",
                "ssrn": "https://papers.ssrn.com/sol3/results.cfm?q={query}",

                # --- Social Media Platforms (for searching within platforms) ---
                "twitter": "https://twitter.com/search?q={query}",
                "instagram": "https://www.instagram.com/explore/tags/{query}/",
                "tiktok": "https://www.tiktok.com/tag/{query}",
                "facebook": "https://www.facebook.com/search/top/?q={query}",
                "reddit": "https://www.reddit.com/search/?q={query}",
                "linkedin": "https://www.linkedin.com/search/results/all/?keywords={query}",
                "tumblr": "https://www.tumblr.com/search/{query}",
                "pinterest_social": "https://www.pinterest.com/search/pins/?q={query}", # Duplicate with images, but relevant here too

                # --- Shopping/E-commerce Sites ---
                "amazon": "https://www.amazon.com/s?k={query}",
                "tokopedia": "https://www.tokopedia.com/search?st=product&q={query}",
                "shopee": "https://shopee.co.id/search?keyword={query}",
                "ebay": "https://www.ebay.com/sch/i.html?_nkw={query}",
                "etsy": "https://www.etsy.com/search?q={query}",
                "alibaba": "https://www.alibaba.com/trade/search?SearchText={query}",

                # --- Q&A Sites ---
                "quora": "https://www.quora.com/search?q={query}",
                "stackoverflow": "https://stackoverflow.com/search?q={query}",
                "wikihow": "https://www.wikihow.com/wikiHow/search?q={query}",
                "superuser_se": "https://superuser.com/search?q={query}",
                "ask_ubuntu_se": "https://askubuntu.com/search?q={query}",
                "server_fault_se": "https://serverfault.com/search?q={query}",
                "math_stack_exchange": "https://math.stackexchange.com/search?q={query}",
                "physics_stack_exchange": "https://physics.stackexchange.com/search?q={query}",
                "chemistry_stack_exchange": "https://chemistry.stackexchange.com/search?q={query}",
            }
            self.save_engines(default_engines)
            return default_engines
        
    def save_engines(self, engines):
        """Saves the list of search engines to a JSON file."""
        with open(self.engines_file, 'w') as f:
            json.dump(engines, f, indent=4)

    def load_config(self):
        """Loads application configuration from a file and applies the theme."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'theme' in config:
                        ctk.set_appearance_mode(config['theme'])
            except json.JSONDecodeError:
                pass
        
    def save_config(self):
        """Saves application configuration to a file."""
        config = {'theme': ctk.get_appearance_mode()}
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def toggle_theme(self):
        """Toggles the theme between light and dark using CustomTkinter."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.save_config()

    def create_widgets(self):
        """Creates all GUI elements."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_column_frame = ctk.CTkFrame(main_frame)
        left_column_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        input_frame = ctk.CTkFrame(left_column_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(input_frame, text="Search Term:").grid(row=0, column=0, sticky="w", pady=5)
        self.query_entry = ctk.CTkEntry(input_frame, width=300)
        self.query_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.query_entry.bind("<Return>", self.start_search_thread)

        ctk.CTkLabel(input_frame, text="Select Search Engine:").grid(row=1, column=0, sticky="w", pady=5)
        
        engine_options = ["All Engines"] + sorted(self.available_engines.keys())
        self.engine_combobox = ctk.CTkComboBox(input_frame, values=engine_options, width=285)
        self.engine_combobox.set("google") # Set default
        self.engine_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        self.manage_engines_button = ctk.CTkButton(input_frame, text="Manage Search Engines", command=self.open_manage_engines_window)
        self.manage_engines_button.grid(row=1, column=2, padx=5, pady=5)

        self.open_browser_var = ctk.BooleanVar(value=False)
        self.open_browser_checkbox = ctk.CTkCheckBox(input_frame, text="Open in Browser Automatically (Each Result)", variable=self.open_browser_var)
        self.open_browser_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        self.search_button = ctk.CTkButton(input_frame, text="Search", command=self.start_search_thread)
        self.search_button.grid(row=3, column=0, columnspan=3, pady=10)

        self.theme_toggle_button = ctk.CTkButton(input_frame, text="Toggle Theme (Light/Dark)", command=self.toggle_theme)
        self.theme_toggle_button.grid(row=4, column=0, columnspan=3, pady=5)

        self.progress_frame = ctk.CTkFrame(left_column_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=5, padx=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, orientation="horizontal")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5, fill="x", expand=True)

        self.status_label = ctk.CTkLabel(self.progress_frame, text="")
        self.status_label.pack(pady=2)

        results_frame = ctk.CTkFrame(left_column_frame)
        results_frame.pack(fill="both", expand=True, padx=5, pady=10)
        
        ctk.CTkLabel(results_frame, text="Search Results", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.results_text = ctk.CTkTextbox(results_frame, wrap="word", width=55, height=20)
        self.results_text.pack(fill="both", expand=True)
        self.results_text.configure(state="disabled")

        # Right Column: Direct Search Engine List (with Tabs)
        right_column_frame = ctk.CTkFrame(main_frame)
        right_column_frame.pack(side="right", fill="both", padx=(10, 0))

        ctk.CTkLabel(right_column_frame, text="Double-click engine name to open in browser:", font=ctk.CTkFont(size=12)).pack(pady=5, padx=5)

        self.direct_search_tabview = ctk.CTkTabview(right_column_frame)
        self.direct_search_tabview.pack(fill="both", expand=True)

        for category_name in self.engine_categories.keys():
            self.direct_search_tabview.add(category_name)
            tab_frame = self.direct_search_tabview.tab(category_name)
            
            scrollable_frame = ctk.CTkScrollableFrame(tab_frame)
            scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.listboxes_by_category[category_name] = scrollable_frame

    def open_selected_engine_in_browser_ctk(self, engine_key):
        """Opens the selected search engine in the browser."""
        query = self.query_entry.get().strip()

        url_template = self.available_engines.get(engine_key)
        if url_template:
            if query:
                full_url = url_template.format(query=query)
                messagebox.showinfo("Opening Browser", f"Opening {engine_key.replace('_', ' ').title()} with search for '{query}'...")
            else:
                # Try to extract base URL. This might need adjustment for very non-standard URLs.
                # E.g., if URL template is "https://example.com/search?q={query}", we take "https://example.com"
                parsed_url = url_template.split('{query}')[0]
                if '?' in parsed_url:
                    base_url = parsed_url.split('?')[0]
                elif '/' in parsed_url and parsed_url.endswith('/'):
                    base_url = parsed_url.rstrip('/')
                else:
                    base_url = parsed_url

                # Ensure URL starts with a protocol
                if not base_url.startswith(('http://', 'https://')):
                    # This is an assumption, some URLs might be non-standard
                    base_url = f"https://{base_url.replace('www.', '', 1).split('/')[0]}"

                full_url = base_url
                messagebox.showinfo("Opening Browser", f"Opening main page of {engine_key.replace('_', ' ').title()}...")

            try:
                webbrowser.open_new_tab(full_url)
            except Exception as e:
                messagebox.showerror("Failed to Open Browser", f"Could not open browser for {engine_key.replace('_', ' ').title()}: {e}")
        else:
            messagebox.showerror("Error", f"URL for {engine_key.replace('_', ' ').title()} not found.")

    def get_categorized_engines(self):
        """Helper function to categorize engines based on common keywords."""
        categorized = {k: [] for k in self.engine_categories.keys()}
        
        for engine_key in sorted(self.available_engines.keys()):
            added_to_category = False
            lower_key = engine_key.lower()

            # Prioritize specific categories
            # Images
            if any(k in lower_key for k in ["image", "images", "photo", "unsplash", "pexels", "pixabay", "shutterstock", "deviantart", "getty_images", "google_arts_culture"]):
                categorized["Images"].append(engine_key)
                added_to_category = True
            # Videos
            if any(k in lower_key for k in ["video", "youtube", "vimeo", "dailymotion", "twitch", "metacafe", "internet_archive_videos"]):
                categorized["Videos"].append(engine_key)
                added_to_category = True
            # News
            if any(k in lower_key for k in ["news", "reuters", "bbc", "cnn", "al_jazeera", "guardian", "times", "press", "kompas", "detik"]):
                categorized["News"].append(engine_key)
                added_to_category = True
            # Academic
            if any(k in lower_key for k in ["scholar", "pubmed", "semantic", "wolframalpha", "researchgate", "academia", "jstor", "sciencedirect", "ieee", "arxiv", "philpapers", "ssrn"]):
                categorized["Academic"].append(engine_key)
                added_to_category = True
            # Social
            if any(k in lower_key for k in ["twitter", "instagram", "tiktok", "facebook", "reddit", "linkedin", "tumblr", "pinterest_social"]):
                categorized["Social"].append(engine_key)
                added_to_category = True
            # Shopping
            if any(k in lower_key for k in ["amazon", "shop", "tokopedia", "shopee", "ebay", "etsy", "alibaba"]):
                categorized["Shopping"].append(engine_key)
                added_to_category = True
            # Q&A
            if any(k in lower_key for k in ["quora", "stack", "answers", "ask", "wikihow", "superuser", "ubuntu", "server_fault", "math_stack_exchange", "physics_stack_exchange", "chemistry_stack_exchange"]):
                categorized["Q&A"].append(engine_key)
                added_to_category = True
            
            # If not added to a specific category, put it in "General"
            if not added_to_category:
                categorized["General"].append(engine_key)
                
        # Remove duplicates within each category and sort
        for cat in categorized:
            categorized[cat] = sorted(list(set(categorized[cat])))
            
        return categorized

    def update_all_category_listboxes(self):
        """Updates all Listboxes in each tab."""
        dynamic_categories = self.get_categorized_engines()

        for category_name in self.engine_categories.keys():
            scrollable_frame = self.listboxes_by_category.get(category_name)
            if not scrollable_frame:
                continue

            # Clear all existing widgets within the scrollable_frame
            for child in scrollable_frame.winfo_children():
                child.destroy()
            
            engines_in_this_tab = dynamic_categories.get(category_name, [])
            
            for engine_key in engines_in_this_tab:
                display_name = engine_key.replace('_', ' ').title() 
                label = ctk.CTkLabel(scrollable_frame, text=display_name, anchor="w")
                label.pack(fill="x", pady=2, padx=5)
                # Binding double-click event
                label.bind("<Double-Button-1>", lambda e, name=engine_key: self.open_selected_engine_in_browser_ctk(name))

    def start_search_thread(self, event=None):
        """Starts the search in a separate thread to keep the GUI responsive."""
        if self._search_in_progress:
            messagebox.showinfo("Warning", "A search is already in progress. Please wait until it completes.")
            return

        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return

        selected_engine = self.engine_combobox.get()
        if not selected_engine:
            messagebox.showwarning("Warning", "Please select a search engine.")
            return
            
        self._search_in_progress = True
        self.set_gui_state_on_search(True)
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")
        self.status_label.configure(text="Starting search...")
        self.progress_bar.start()

        search_thread = threading.Thread(target=self.perform_search_logic, args=(query, selected_engine, self.open_browser_var.get()))
        search_thread.daemon = True # Allow thread to die if main app closes
        search_thread.start()

    def perform_search_logic(self, query, selected_engine, open_in_browser):
        """Main logic for performing search on one or all search engines."""
        engines_to_search = []
        if selected_engine == "All Engines":
            engines_to_search = sorted(self.available_engines.keys())
        else:
            engines_to_search = [selected_engine]

        total_engines = len(engines_to_search)
        results_buffer = []

        for i, engine_name in enumerate(engines_to_search):
            # Update status on GUI (must be on main thread)
            self.after(0, lambda e=engine_name, i=i, t=total_engines: 
                        self.status_label.configure(text=f"Searching for '{query}' on {e.replace('_', ' ').title()} ({i+1}/{t})..."))
            
            engine_url_template = self.available_engines.get(engine_name)
            if not engine_url_template:
                results_buffer.append({"engine": engine_name, "status": "Error", "message": f"URL for '{engine_name}' not found.", "results": []})
                continue

            result_data = search_engine(query, engine_name, engine_url_template)
            results_buffer.append(result_data)
            
            # Add a small delay between searches to avoid IP blocking
            if i < total_engines - 1:
                time.sleep(0.5)

        # After all searches are complete, update GUI (on main thread)
        self.after(0, lambda: self.display_all_results(results_buffer, open_in_browser))
        self.after(0, self.reset_gui_state)

    def display_all_results(self, all_results_data, open_in_browser):
        """Displays collected search results in the CTkTextbox."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        for result_data in all_results_data:
            self.results_text.insert("end", f"=== Results from {result_data['engine'].replace('_', ' ').title()} ===\n", "header_tag")
            if result_data["status"] == "Success":
                if result_data["results"]:
                    for i, res_url in enumerate(result_data["results"]):
                        self.results_text.insert("end", f"{i+1}. {res_url}\n")
                        if open_in_browser:
                            try:
                                webbrowser.open_new_tab(res_url)
                                # Small delay to avoid opening too many tabs at once
                                time.sleep(0.1) 
                            except Exception as e:
                                self.results_text.insert("end", f"  Failed to open URL: {res_url} ({e})\n")
                else:
                    self.results_text.insert("end", f"No results found from {result_data['engine'].replace('_', ' ').title()} for this query.\n")
            else:
                self.results_text.insert("end", f"An error occurred: {result_data['message']}\n", "error_tag")
            
            self.results_text.insert("end", "\n" + "="*50 + "\n\n")
        
        self.results_text.configure(state="disabled")
        self.results_text.see("end") # Scroll to bottom

    def set_gui_state_on_search(self, disabled):
        """Sets the state (enabled/disabled) of GUI widgets during search."""
        state = "disabled" if disabled else "normal"
        self.search_button.configure(state=state)
        self.query_entry.configure(state=state)
        self.engine_combobox.configure(state=state)
        self.manage_engines_button.configure(state=state)
        self.theme_toggle_button.configure(state=state)
        if disabled:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()

    def reset_gui_state(self):
        """Restores GUI state after search is complete."""
        self.progress_bar.stop()
        self.status_label.configure(text="Search Complete.")
        self._search_in_progress = False
        self.set_gui_state_on_search(False)
        
    def open_manage_engines_window(self):
        """Opens a new window to manage search engines."""
        if self._search_in_progress:
            messagebox.showwarning("Warning", "Cannot open management window while a search is in progress.")
            return

        manage_window = ctk.CTkToplevel(self)
        manage_window.title("Manage Search Engines")
        manage_window.geometry("500x400")
        manage_window.transient(self) # Make the management window appear on top of the main window
        manage_window.grab_set() # Block interaction with other windows until this one is closed

        frame_list = ctk.CTkFrame(manage_window)
        frame_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.engines_list_scrollable_frame = ctk.CTkScrollableFrame(frame_list)
        self.engines_list_scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.engines_labels = {} # To store label references
        self.update_engines_listbox()

        frame_buttons = ctk.CTkFrame(manage_window, fg_color="transparent")
        frame_buttons.pack(fill="x", pady=5)

        ctk.CTkButton(frame_buttons, text="Add New", command=self.add_new_engine).pack(side="left", padx=5)
        ctk.CTkButton(frame_buttons, text="Edit URL", command=self.edit_engine_url).pack(side="left", padx=5)
        ctk.CTkButton(frame_buttons, text="Delete Selected", command=self.delete_selected_engine).pack(side="left", padx=5)
        ctk.CTkButton(frame_buttons, text="Close", command=manage_window.destroy).pack(side="right", padx=5)

        # Handle closing of the management window
        manage_window.protocol("WM_DELETE_WINDOW", lambda: self.on_manage_window_close(manage_window))

    def update_engines_listbox(self):
        """Updates the list of search engines in the management window."""
        # Clear all existing labels
        for label in self.engines_labels.values():
            label.destroy()
        self.engines_labels = {}

        # Add new labels for each search engine
        for name, url_template in sorted(self.available_engines.items()):
            label = ctk.CTkLabel(self.engines_list_scrollable_frame, text=f"{name}: {url_template}", anchor="w")
            label.pack(fill="x", pady=2, padx=5)
            label.bind("<Button-1>", lambda e, n=name: self._select_engine_label(e, n))
            self.engines_labels[name] = label
            
        self._current_selected_engine = None # Reset selection after update

    def _select_engine_label(self, event, engine_name):
        """Handles the selection of a search engine label in the management window."""
        # Reset color of all labels
        for label in self.engines_labels.values():
            label.configure(fg_color="transparent")
            
        # Set color of the selected label
        event.widget.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]) # Use button theme color
        self._current_selected_engine = engine_name


    def add_new_engine(self):
        """Adds a new search engine."""
        name = simpledialog.askstring("Add Search Engine", "Enter Search Engine Name (e.g., my_custom_search):", parent=self)
        if name:
            name = name.lower().strip() # Clean name
            if not name:
                messagebox.showwarning("Warning", "Search engine name cannot be empty.", parent=self)
                return
            if name in self.available_engines:
                messagebox.showwarning("Warning", f"Search engine '{name}' already exists.", parent=self)
                return
            url_template = simpledialog.askstring("Add Search Engine", f"Enter URL for '{name}' (use {{query}} as placeholder, e.g., https://example.com/search?q={{query}}):", parent=self)
            if url_template:
                url_template = url_template.strip() # Clean URL
                if '{query}' not in url_template:
                    messagebox.showwarning("Warning", "URL must contain '{query}' as a placeholder.", parent=self)
                    return
                self.available_engines[name] = url_template
                self.save_engines(self.available_engines)
                self.update_engines_listbox()
                self.update_main_combobox()
                self.update_all_category_listboxes() 
                messagebox.showinfo("Success", f"Search engine '{name}' successfully added.", parent=self)

    def edit_engine_url(self):
        """Edits the URL of an existing search engine."""
        if not self._current_selected_engine: # Using self._current_selected_engine
            messagebox.showwarning("Warning", "Please select a search engine to edit.", parent=self)
            return

        name = self._current_selected_engine
        current_url = self.available_engines.get(name)

        new_url_template = simpledialog.askstring("Edit Search Engine URL", f"Edit URL for '{name}':", initialvalue=current_url, parent=self)
        if new_url_template:
            new_url_template = new_url_template.strip()
            if '{query}' not in new_url_template:
                messagebox.showwarning("Warning", "URL must contain '{query}' as a placeholder.", parent=self)
                return
            self.available_engines[name] = new_url_template
            self.save_engines(self.available_engines)
            self.update_engines_listbox()
            self.update_main_combobox()
            self.update_all_category_listboxes()
            messagebox.showinfo("Success", f"URL for '{name}' successfully updated.", parent=self)

    def delete_selected_engine(self):
        """Deletes the selected search engine."""
        if not self._current_selected_engine: # Using self._current_selected_engine
            messagebox.showwarning("Warning", "Please select a search engine to delete.", parent=self)
            return

        name_to_delete = self._current_selected_engine

        response = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{name_to_delete}'?", parent=self)
        
        if response:
            if name_to_delete in self.available_engines:
                del self.available_engines[name_to_delete]
                self.save_engines(self.available_engines)
                self.update_engines_listbox()
                self.update_main_combobox()
                self.update_all_category_listboxes() # Update direct list as well
                messagebox.showinfo("Success", f"Search engine '{name_to_delete}' successfully deleted.", parent=self)
            else:
                messagebox.showerror("Error", f"Search engine '{name_to_delete}' not found.", parent=self)
    
    def update_main_combobox(self):
        """Updates the options in the main combobox."""
        engine_options = ["All Engines"] + sorted(self.available_engines.keys())
        self.engine_combobox.configure(values=engine_options) # IMPORTANT: Use .configure() for CustomTkinter

        # If previous selection no longer exists, set default
        if self.available_engines:
            current_selection = self.engine_combobox.get()
            if current_selection not in self.available_engines and current_selection != "All Engines":
                if "google" in self.available_engines:
                    self.engine_combobox.set("google") 
                elif len(engine_options) > 1: # If there are options other than "All Engines"
                    self.engine_combobox.set(engine_options[1]) # Select the first one after "All Engines"
                else:
                     self.engine_combobox.set("") # If no engines at all
        else:
            self.engine_combobox.set("") # If no search engines

    def on_manage_window_close(self, manage_window):
        """Function called when the management window is closed."""
        manage_window.destroy()
        self.focus_set() # IMPORTANT: Just self.focus_set() for CustomTkinter main window
        self.update_main_combobox()
        self.update_all_category_listboxes() # Ensure direct list is also updated

if __name__ == "__main__":
    app = SearchApp()
    app.mainloop()
