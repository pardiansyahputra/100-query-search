import requests
from bs4 import BeautifulSoup
import webbrowser
import customtkinter as ctk # Menggunakan CustomTkinter
import json
import threading
import time
import os
import tkinter as tk # Tetap gunakan tkinter untuk messagebox dan simpledialog
from tkinter import messagebox, simpledialog # Import spesifik

ctk.set_appearance_mode("System") # Default system mode
ctk.set_default_color_theme("blue") # Default color theme

# --- Fungsi Parser Spesifik untuk Setiap Mesin Pencari ---
# Penting: Struktur HTML mesin pencari sering berubah.
# Parser ini mungkin perlu disesuaikan di masa mendatang jika ada perubahan di situs.

def parse_google_results(soup):
    results = []
    for g_result in soup.find_all('div', class_='g'):
        link_tag = g_result.find('a', href=True)
        if link_tag and link_tag['href'].startswith('http'):
            href = link_tag['href']
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
        response = requests.get(url, headers=headers, verify=True, timeout=15) # Meningkatkan timeout
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
            # Fallback parser: Ambil semua link yang valid. 
            # Ini mungkin tidak seakurat parser spesifik.
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Hanya tambahkan jika itu adalah URL web lengkap
                if href.startswith('http://') or href.startswith('https://'):
                    parsed_results.append(href)
            
        return {"engine": engine_name, "status": "Success", "message": "Pencarian berhasil.", "results": parsed_results[:20]} # Batasi 20 hasil

    except requests.exceptions.Timeout:
        return {"engine": engine_name, "status": "Error", "message": f"Permintaan ke {engine_name.capitalize()} habis waktu (timeout).", "results": []}
    except requests.exceptions.RequestException as e:
        return {"engine": engine_name, "status": "Error", "message": f"Terjadi kesalahan saat mencari di {engine_name.capitalize()}: {e}", "results": []}
    except Exception as e:
        return {"engine": engine_name, "status": "Error", "message": f"Terjadi kesalahan tak terduga: {e}", "results": []}

class SearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Pencari Universal")
        self.geometry("1000x650") 

        self.engines_file = "search_engines.json"
        self.available_engines = self.load_engines()

        # Inisialisasi kategori dengan daftar kosong
        self.engine_categories = {
            "Umum": [], 
            "Gambar": [],
            "Video": [],
            "Berita": [],
            "Akademik": [],
            "Sosial": [],
            "Belanja": [],
            "Tanya Jawab": []
        }
        self.listboxes_by_category = {} # Akan menampung frame scrollable untuk setiap kategori
        self._current_selected_engine = None
        self._search_in_progress = False

        self.config_file = "app_config.json"
        self.load_config()

        self.create_widgets()
        # Panggil update_all_category_listboxes setelah widget dibuat
        self.update_all_category_listboxes()
        
    def load_engines(self):
        """Memuat daftar mesin pencari dari file JSON atau menggunakan default."""
        try:
            with open(self.engines_file, 'r') as f:
                engines = json.load(f)
                # Validasi format dasar
                if not all(isinstance(k, str) and isinstance(v, str) and '{query}' in v for k, v in engines.items()):
                    raise ValueError("Format file mesin pencari tidak valid.")
                return engines
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # Jika file tidak ada, rusak, atau format tidak valid, gunakan default
            print("File search_engines.json tidak ditemukan atau rusak. Membuat dari default.")
            default_engines = {
                # --- Mesin Pencari Umum ---
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
                "cnn": "https://edition.cnn.com/search?q={query}", # Ini juga bisa masuk berita, tapi karena `cnn` spesifik, bisa di umum
                "coccinelles": "https://www.coccinelles.fr/recherche.php?q={query}",
                "colibrism": "https://colibri.sm/search?q={query}",
                "cosmos": "https://www.cosmos.com.my/search?q={query}",
                "crawler": "https://www.crawler.com/search?q={query}",
                
                # --- Mesin Pencari Gambar ---
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

                # --- Mesin Pencari Video ---
                "youtube": "https://www.youtube.com/results?search_query={query}", # Ini url yang sedikit aneh, mungkin perlu dicek
                "vimeo": "https://vimeo.com/search?q={query}",
                "dailymotion": "https://www.dailymotion.com/search/{query}",
                "metacafe": "https://www.metacafe.com/videos/?query={query}",
                "twitch_channels": "https://www.twitch.tv/search?query={query}&type=channels",
                "twitch_videos": "https://www.twitch.tv/search?query={query}&type=videos",
                "internet_archive_videos": "https://archive.org/details/movies?query={query}",

                # --- Mesin Pencari Berita ---
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

                # --- Mesin Pencari Akademik/Ilmiah ---
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

                # --- Platform Media Sosial (untuk mencari di dalam platform) ---
                "twitter": "https://twitter.com/search?q={query}",
                "instagram": "https://www.instagram.com/explore/tags/{query}/",
                "tiktok": "https://www.tiktok.com/tag/{query}",
                "facebook": "https://www.facebook.com/search/top/?q={query}",
                "reddit": "https://www.reddit.com/search/?q={query}",
                "linkedin": "https://www.linkedin.com/search/results/all/?keywords={query}",
                "tumblr": "https://www.tumblr.com/search/{query}",
                "pinterest_social": "https://www.pinterest.com/search/pins/?q={query}", # Duplikat dengan images, tapi relevan di sini juga

                # --- Situs Belanja/E-commerce ---
                "amazon": "https://www.amazon.com/s?k={query}",
                "tokopedia": "https://www.tokopedia.com/search?st=product&q={query}",
                "shopee": "https://shopee.co.id/search?keyword={query}",
                "ebay": "https://www.ebay.com/sch/i.html?_nkw={query}",
                "etsy": "https://www.etsy.com/search?q={query}",
                "alibaba": "https://www.alibaba.com/trade/search?SearchText={query}",

                # --- Situs Tanya Jawab ---
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
        """Menyimpan daftar mesin pencari ke file JSON."""
        with open(self.engines_file, 'w') as f:
            json.dump(engines, f, indent=4)

    def load_config(self):
        """Memuat konfigurasi aplikasi dari file dan menerapkan tema."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'theme' in config:
                        ctk.set_appearance_mode(config['theme'])
            except json.JSONDecodeError:
                pass
        
    def save_config(self):
        """Menyimpan konfigurasi aplikasi ke file."""
        config = {'theme': ctk.get_appearance_mode()}
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def toggle_theme(self):
        """Mengganti tema antara terang dan gelap menggunakan CustomTkinter."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "Dark" if current_mode == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        self.save_config()

    def create_widgets(self):
        """Membuat semua elemen GUI."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_column_frame = ctk.CTkFrame(main_frame)
        left_column_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        input_frame = ctk.CTkFrame(left_column_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=5, padx=5)
        

        ctk.CTkLabel(input_frame, text="Istilah Pencarian:").grid(row=0, column=0, sticky="w", pady=5)
        self.query_entry = ctk.CTkEntry(input_frame, width=300)
        self.query_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.query_entry.bind("<Return>", self.start_search_thread)

        ctk.CTkLabel(input_frame, text="Pilih Mesin Pencari:").grid(row=1, column=0, sticky="w", pady=5)
        
        engine_options = ["All Engines"] + sorted(self.available_engines.keys())
        self.engine_combobox = ctk.CTkComboBox(input_frame, values=engine_options, width=285)
        self.engine_combobox.set("google") # Set default
        self.engine_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        self.manage_engines_button = ctk.CTkButton(input_frame, text="Kelola Mesin Pencari", command=self.open_manage_engines_window)
        self.manage_engines_button.grid(row=1, column=2, padx=5, pady=5)

        self.open_browser_var = ctk.BooleanVar(value=False)
        self.open_browser_checkbox = ctk.CTkCheckBox(input_frame, text="Buka di Browser Otomatis (Setiap Hasil)", variable=self.open_browser_var)
        self.open_browser_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        self.search_button = ctk.CTkButton(input_frame, text="Cari", command=self.start_search_thread)
        self.search_button.grid(row=3, column=0, columnspan=3, pady=10)

        self.theme_toggle_button = ctk.CTkButton(input_frame, text="Toggle Tema (Terang/Gelap)", command=self.toggle_theme)
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
        
        ctk.CTkLabel(results_frame, text="Hasil Pencarian", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.results_text = ctk.CTkTextbox(results_frame, wrap="word", width=55, height=20)
        self.results_text.pack(fill="both", expand=True)
        self.results_text.configure(state="disabled")

        # Kolom Kanan: Daftar Mesin Pencari untuk Jelajah Langsung (dengan Tabs)
        right_column_frame = ctk.CTkFrame(main_frame)
        right_column_frame.pack(side="right", fill="both", padx=(10, 0))

        ctk.CTkLabel(right_column_frame, text="Klik ganda nama mesin pencari untuk membuka di browser:", font=ctk.CTkFont(size=12)).pack(pady=5, padx=5)

        self.direct_search_tabview = ctk.CTkTabview(right_column_frame)
        self.direct_search_tabview.pack(fill="both", expand=True)

        for category_name in self.engine_categories.keys():
            self.direct_search_tabview.add(category_name)
            tab_frame = self.direct_search_tabview.tab(category_name)
            
            scrollable_frame = ctk.CTkScrollableFrame(tab_frame)
            scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.listboxes_by_category[category_name] = scrollable_frame

    def open_selected_engine_in_browser_ctk(self, engine_key):
        """Membuka mesin pencari yang dipilih di browser."""
        query = self.query_entry.get().strip()

        url_template = self.available_engines.get(engine_key)
        if url_template:
            if query:
                full_url = url_template.format(query=query)
                messagebox.showinfo("Membuka Browser", f"Membuka {engine_key.replace('_', ' ').title()} dengan pencarian untuk '{query}'...")
            else:
                # Coba ekstrak base URL. Ini mungkin perlu disesuaikan untuk URL yang sangat tidak standar.
                # Misalnya, jika URL template-nya "https://example.com/search?q={query}", kita ambil "https://example.com"
                parsed_url = url_template.split('{query}')[0]
                if '?' in parsed_url:
                    base_url = parsed_url.split('?')[0]
                elif '/' in parsed_url and parsed_url.endswith('/'):
                    base_url = parsed_url.rstrip('/')
                else:
                    base_url = parsed_url

                # Pastikan URL dimulai dengan protokol
                if not base_url.startswith(('http://', 'https://')):
                    # Ini asumsi, bisa jadi ada URL yang tidak standar
                    base_url = f"https://{base_url.replace('www.', '', 1).split('/')[0]}"

                full_url = base_url
                messagebox.showinfo("Membuka Browser", f"Membuka halaman utama {engine_key.replace('_', ' ').title()}...")

            try:
                webbrowser.open_new_tab(full_url)
            except Exception as e:
                messagebox.showerror("Gagal Membuka Browser", f"Tidak dapat membuka browser untuk {engine_key.replace('_', ' ').title()}: {e}")
        else:
            messagebox.showerror("Error", f"URL untuk {engine_key.replace('_', ' ').title()} tidak ditemukan.")

    def get_categorized_engines(self):
        """Helper function to categorize engines based on common keywords."""
        categorized = {k: [] for k in self.engine_categories.keys()}
        
        for engine_key in sorted(self.available_engines.keys()):
            added_to_category = False
            lower_key = engine_key.lower()

            # Prioritaskan kategori spesifik
            # Gambar
            if any(k in lower_key for k in ["image", "images", "photo", "unsplash", "pexels", "pixabay", "shutterstock", "deviantart", "getty_images", "google_arts_culture"]):
                categorized["Gambar"].append(engine_key)
                added_to_category = True
            # Video
            if any(k in lower_key for k in ["video", "youtube", "vimeo", "dailymotion", "twitch", "metacafe", "internet_archive_videos"]):
                categorized["Video"].append(engine_key)
                added_to_category = True
            # Berita
            if any(k in lower_key for k in ["news", "reuters", "bbc", "cnn", "al_jazeera", "guardian", "times", "press", "kompas", "detik"]):
                categorized["Berita"].append(engine_key)
                added_to_category = True
            # Akademik
            if any(k in lower_key for k in ["scholar", "pubmed", "semantic", "wolframalpha", "researchgate", "academia", "jstor", "sciencedirect", "ieee", "arxiv", "philpapers", "ssrn"]):
                categorized["Akademik"].append(engine_key)
                added_to_category = True
            # Sosial
            if any(k in lower_key for k in ["twitter", "instagram", "tiktok", "facebook", "reddit", "linkedin", "tumblr", "pinterest_social"]):
                categorized["Sosial"].append(engine_key)
                added_to_category = True
            # Belanja
            if any(k in lower_key for k in ["amazon", "shop", "tokopedia", "shopee", "ebay", "etsy", "alibaba"]):
                categorized["Belanja"].append(engine_key)
                added_to_category = True
            # Tanya Jawab
            if any(k in lower_key for k in ["quora", "stack", "answers", "ask", "wikihow", "superuser", "ubuntu", "server_fault", "math_stack_exchange", "physics_stack_exchange", "chemistry_stack_exchange"]):
                categorized["Tanya Jawab"].append(engine_key)
                added_to_category = True
            
            # Jika belum ditambahkan ke kategori spesifik, masukkan ke "Umum"
            if not added_to_category:
                categorized["Umum"].append(engine_key)
                
        # Hapus duplikasi dalam setiap kategori dan urutkan
        for cat in categorized:
            categorized[cat] = sorted(list(set(categorized[cat])))
            
        return categorized

    def update_all_category_listboxes(self):
        """Memperbarui semua Listbox di setiap tab."""
        dynamic_categories = self.get_categorized_engines()

        for category_name in self.engine_categories.keys():
            scrollable_frame = self.listboxes_by_category.get(category_name)
            if not scrollable_frame:
                continue

            # Hapus semua widget yang ada di dalam scrollable_frame
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
        """Memulai pencarian di thread terpisah agar GUI tetap responsif."""
        if self._search_in_progress:
            messagebox.showinfo("Peringatan", "Pencarian sedang berlangsung. Mohon tunggu hingga selesai.")
            return

        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Peringatan", "Mohon masukkan istilah pencarian.")
            return

        selected_engine = self.engine_combobox.get()
        if not selected_engine:
            messagebox.showwarning("Peringatan", "Mohon pilih mesin pencari.")
            return
            
        self._search_in_progress = True
        self.set_gui_state_on_search(True)
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")
        self.status_label.configure(text="Memulai pencarian...")
        self.progress_bar.start()

        search_thread = threading.Thread(target=self.perform_search_logic, args=(query, selected_engine, self.open_browser_var.get()))
        search_thread.daemon = True # Biarkan thread mati jika aplikasi utama ditutup
        search_thread.start()

    def perform_search_logic(self, query, selected_engine, open_in_browser):
        """Logika utama untuk melakukan pencarian di satu atau semua mesin pencari."""
        engines_to_search = []
        if selected_engine == "All Engines":
            engines_to_search = sorted(self.available_engines.keys())
        else:
            engines_to_search = [selected_engine]

        total_engines = len(engines_to_search)
        results_buffer = []

        for i, engine_name in enumerate(engines_to_search):
            # Update status di GUI (harus di main thread)
            self.after(0, lambda e=engine_name, i=i, t=total_engines: 
                        self.status_label.configure(text=f"Mencari '{query}' di {e.replace('_', ' ').title()} ({i+1}/{t})..."))
            
            engine_url_template = self.available_engines.get(engine_name)
            if not engine_url_template:
                results_buffer.append({"engine": engine_name, "status": "Error", "message": f"URL untuk '{engine_name}' tidak ditemukan.", "results": []})
                continue

            result_data = search_engine(query, engine_name, engine_url_template)
            results_buffer.append(result_data)
            
            # Tambahkan jeda antar pencarian untuk menghindari IP diblokir
            if i < total_engines - 1:
                time.sleep(0.5)

        # Setelah semua pencarian selesai, update GUI (di main thread)
        self.after(0, lambda: self.display_all_results(results_buffer, open_in_browser))
        self.after(0, self.reset_gui_state)

    def display_all_results(self, all_results_data, open_in_browser):
        """Menampilkan hasil pencarian yang dikumpulkan di CTkTextbox."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        for result_data in all_results_data:
            self.results_text.insert("end", f"=== Hasil dari {result_data['engine'].replace('_', ' ').title()} ===\n", "header_tag")
            if result_data["status"] == "Success":
                if result_data["results"]:
                    for i, res_url in enumerate(result_data["results"]):
                        self.results_text.insert("end", f"{i+1}. {res_url}\n")
                        if open_in_browser:
                            try:
                                webbrowser.open_new_tab(res_url)
                                # Memberi jeda kecil agar tidak membuka terlalu banyak tab sekaligus
                                time.sleep(0.1) 
                            except Exception as e:
                                self.results_text.insert("end", f"  Gagal membuka URL: {res_url} ({e})\n")
                else:
                    self.results_text.insert("end", f"Tidak ada hasil ditemukan dari {result_data['engine'].replace('_', ' ').title()} untuk kueri ini.\n")
            else:
                self.results_text.insert("end", f"Terjadi kesalahan: {result_data['message']}\n", "error_tag")
            
            self.results_text.insert("end", "\n" + "="*50 + "\n\n")
        
        self.results_text.configure(state="disabled")
        self.results_text.see("end") # Gulir ke bagian bawah

    def set_gui_state_on_search(self, disabled):
        """Mengatur status widget GUI (aktif/nonaktif) selama pencarian."""
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
        """Merestorasi keadaan GUI setelah pencarian selesai."""
        self.progress_bar.stop()
        self.status_label.configure(text="Pencarian Selesai.")
        self._search_in_progress = False
        self.set_gui_state_on_search(False)
        
    def open_manage_engines_window(self):
        """Membuka jendela baru untuk mengelola mesin pencari."""
        if self._search_in_progress:
            messagebox.showwarning("Peringatan", "Tidak dapat membuka jendela manajemen saat pencarian sedang berlangsung.")
            return

        manage_window = ctk.CTkToplevel(self)
        manage_window.title("Kelola Mesin Pencari")
        manage_window.geometry("500x400")
        manage_window.transient(self) # Membuat jendela manajemen di atas jendela utama
        manage_window.grab_set() # Memblokir interaksi dengan jendela lain sampai jendela ini ditutup

        frame_list = ctk.CTkFrame(manage_window)
        frame_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.engines_list_scrollable_frame = ctk.CTkScrollableFrame(frame_list)
        self.engines_list_scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.engines_labels = {} # Untuk menyimpan referensi label
        self.update_engines_listbox()

        frame_buttons = ctk.CTkFrame(manage_window, fg_color="transparent")
        frame_buttons.pack(fill="x", pady=5)

        ctk.CTkButton(frame_buttons, text="Tambah Baru", command=self.add_new_engine).pack(side="left", padx=5)
        ctk.CTkButton(frame_buttons, text="Edit URL", command=self.edit_engine_url).pack(side="left", padx=5)
        ctk.CTkButton(frame_buttons, text="Hapus Terpilih", command=self.delete_selected_engine).pack(side="left", padx=5)
        ctk.CTkButton(frame_buttons, text="Tutup", command=manage_window.destroy).pack(side="right", padx=5)

        # Menangani penutupan jendela manajemen
        manage_window.protocol("WM_DELETE_WINDOW", lambda: self.on_manage_window_close(manage_window))

    def update_engines_listbox(self):
        """Memperbarui daftar mesin pencari di jendela manajemen."""
        # Hapus semua label yang ada
        for label in self.engines_labels.values():
            label.destroy()
        self.engines_labels = {}

        # Tambahkan label baru untuk setiap mesin pencari
        for name, url_template in sorted(self.available_engines.items()):
            label = ctk.CTkLabel(self.engines_list_scrollable_frame, text=f"{name}: {url_template}", anchor="w")
            label.pack(fill="x", pady=2, padx=5)
            label.bind("<Button-1>", lambda e, n=name: self._select_engine_label(e, n))
            self.engines_labels[name] = label
            
        self._current_selected_engine = None # Reset pilihan setelah update

    def _select_engine_label(self, event, engine_name):
        """Menangani pemilihan label mesin pencari di jendela manajemen."""
        # Reset warna semua label
        for label in self.engines_labels.values():
            label.configure(fg_color="transparent")
            
        # Set warna label yang dipilih
        event.widget.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]) # Menggunakan warna tema tombol
        self._current_selected_engine = engine_name


    def add_new_engine(self):
        """Menambahkan mesin pencari baru."""
        name = simpledialog.askstring("Tambah Mesin Pencari", "Masukkan Nama Mesin Pencari (contoh: my_custom_search):", parent=self)
        if name:
            name = name.lower().strip() # Bersihkan nama
            if not name:
                messagebox.showwarning("Peringatan", "Nama mesin pencari tidak boleh kosong.", parent=self)
                return
            if name in self.available_engines:
                messagebox.showwarning("Peringatan", f"Mesin pencari '{name}' sudah ada.", parent=self)
                return
            url_template = simpledialog.askstring("Tambah Mesin Pencari", f"Masukkan URL untuk '{name}' (gunakan {{query}} sebagai placeholder, contoh: https://example.com/search?q={{query}}):", parent=self)
            if url_template:
                url_template = url_template.strip() # Bersihkan URL
                if '{query}' not in url_template:
                    messagebox.showwarning("Peringatan", "URL harus mengandung '{query}' sebagai placeholder.", parent=self)
                    return
                self.available_engines[name] = url_template
                self.save_engines(self.available_engines)
                self.update_engines_listbox()
                self.update_main_combobox()
                self.update_all_category_listboxes() 
                messagebox.showinfo("Berhasil", f"Mesin pencari '{name}' berhasil ditambahkan.", parent=self)

    def edit_engine_url(self):
        """Mengedit URL mesin pencari yang sudah ada."""
        if not self._current_selected_engine: # Menggunakan self._current_selected_engine
            messagebox.showwarning("Peringatan", "Pilih mesin pencari yang ingin diedit.", parent=self)
            return

        name = self._current_selected_engine
        current_url = self.available_engines.get(name)

        new_url_template = simpledialog.askstring("Edit URL Mesin Pencari", f"Edit URL untuk '{name}':", initialvalue=current_url, parent=self)
        if new_url_template:
            new_url_template = new_url_template.strip()
            if '{query}' not in new_url_template:
                messagebox.showwarning("Peringatan", "URL harus mengandung '{query}' sebagai placeholder.", parent=self)
                return
            self.available_engines[name] = new_url_template
            self.save_engines(self.available_engines)
            self.update_engines_listbox()
            self.update_main_combobox()
            self.update_all_category_listboxes()
            messagebox.showinfo("Berhasil", f"URL untuk '{name}' berhasil diperbarui.", parent=self)

    def delete_selected_engine(self):
        """Menghapus mesin pencari yang dipilih."""
        if not self._current_selected_engine: # Menggunakan self._current_selected_engine
            messagebox.showwarning("Peringatan", "Pilih mesin pencari yang ingin dihapus.", parent=self)
            return

        name_to_delete = self._current_selected_engine

        response = messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus '{name_to_delete}'?", parent=self)
        
        if response:
            if name_to_delete in self.available_engines:
                del self.available_engines[name_to_delete]
                self.save_engines(self.available_engines)
                self.update_engines_listbox()
                self.update_main_combobox()
                self.update_all_category_listboxes() # Perbarui daftar langsung
                messagebox.showinfo("Berhasil", f"Mesin pencari '{name_to_delete}' berhasil dihapus.", parent=self)
            else:
                messagebox.showerror("Error", f"Mesin pencari '{name_to_delete}' tidak ditemukan.", parent=self)
    
    def update_main_combobox(self):
        """Memperbarui pilihan di combobox utama."""
        engine_options = ["All Engines"] + sorted(self.available_engines.keys())
        self.engine_combobox.configure(values=engine_options) # PENTING: Gunakan .configure() untuk CustomTkinter

        # Jika pilihan sebelumnya tidak ada lagi, atur default
        if self.available_engines:
            current_selection = self.engine_combobox.get()
            if current_selection not in self.available_engines and current_selection != "All Engines":
                if "google" in self.available_engines:
                    self.engine_combobox.set("google") 
                elif len(engine_options) > 1: # Jika ada opsi selain "All Engines"
                    self.engine_combobox.set(engine_options[1]) # Pilih yang pertama setelah "All Engines"
                else:
                     self.engine_combobox.set("") # Jika tidak ada mesin sama sekali
        else:
            self.engine_combobox.set("") # Jika tidak ada mesin pencari

    def on_manage_window_close(self, manage_window):
        """Fungsi yang dipanggil saat jendela manajemen ditutup."""
        manage_window.destroy()
        self.focus_set() # PENTING: Cukup self.focus_set() untuk jendela utama CustomTkinter
        self.update_main_combobox()
        self.update_all_category_listboxes() # Pastikan daftar langsung diperbarui juga

if __name__ == "__main__":
    app = SearchApp()
    app.mainloop()
