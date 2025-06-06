# 🔍 Universal Search Application

A multi-platform desktop application built with Python and CustomTkinter to perform searches across various popular search engines from a single, intuitive interface. Manage, customize, and explore your search results with ease!

## ✨ Key Features

* **Multi-Engine Search:** Search Google, Bing, DuckDuckGo, Yahoo, and many other search engines simultaneously or choose a specific one.
* **Categorized Search Engines:** Search engines are automatically categorized (General, Images, Videos, News, Academic, Social, Shopping, Q&A) for easier navigation.
* **Search Engine Management:** Add, edit, or delete custom search engines directly from the GUI.
* **Automatic Browser Opening:** Option to automatically open search results in your web browser.
* **Modern Interface:** Clean and responsive design using CustomTkinter.
* **Theme Settings:** Toggle between light and dark themes to suit your preference.
* **Direct Search:** Double-click a search engine name in the right-hand tabs to quickly open it in your browser with or without a query.

## 📸 Application Screenshot

![example](https://github.com/user-attachments/assets/d18fd198-95da-46d9-bda7-3afeb9e3d6d8)

## ⚙️ Requirements

Ensure you have **Python 3.x** installed on your system.

You need to install the following Python libraries:

* `customtkinter`
* `requests`
* `beautifulsoup4`

You can easily install them using `pip`, Python's package installer:

```bash
pip install customtkinter requests beautifulsoup4
🚀 Installation & Usage
Download or Clone the Project:
If you're managing the project with Git, you can clone this repository:

Bash

git clone [YOUR_REPOSITORY_URL_HERE]
cd your_project_folder_name
Otherwise, simply download the crawler ototmatis.py file to your chosen directory.

Delete Old Configuration Files (Important!):
If you have run this application before, there might be search_engines.json and app_config.json files storing old configurations. To ensure all the latest search engines are loaded and themes are reset, it's recommended to delete these files:

For Windows users (Command Prompt/PowerShell):
Bash

del search_engines.json
del app_config.json
For macOS/Linux users (Terminal):
Bash

rm search_engines.json
rm app_config.json
Run the Application:
After ensuring all requirements are installed and old configuration files are deleted (if applicable), navigate to the directory where you saved crawler ototmatis.py in your terminal or Command Prompt, then run:

Bash

python "crawler ototmatis.py"
The application will open, and a new search_engines.json file will be created with the complete list of search engines.

📝 How to Use
Once the application is running, you can:

Enter Search Term: Type the query or phrase you want to search for in the input field.
Select Search Engine:
Use the "Select Search Engine" dropdown to choose a specific search engine (e.g., Google, Bing, YouTube).
Select "All Engines" to run your query on all listed search engines.
Open Automatically in Browser: Check the "Open in Browser Automatically (Each Result)" box if you want each search result URL to open in a new browser tab. Be cautious with this option, especially when selecting "All Engines", as it can open many tabs at once.
Start Search: Click the "Search" button or simply press Enter on your keyboard after entering the search term.
View Results: Search results will be displayed in the "Search Results" text area on the left side of the window.
Manage Search Engines: Click the "Manage Search Engines" button to open a separate window where you can:
Add New: Enter a name and URL template for a new search engine ({query} must be used as a placeholder).
Edit URL: Select an existing search engine from the list, then edit its URL template.
Delete Selected: Remove a search engine you no longer want.
Categorized Quick Search: On the right side of the main window, you'll find tabs categorizing search engines (General, Images, Videos, etc.). Double-click a search engine's name within any tab to directly open it in your browser. If a query is present in the search field, it will be used; otherwise, the main page of the search engine will be opened.


🛠️ How Search Works
This application interacts with search engines by sending HTTP requests using the requests library. After receiving the HTML content from the search engine, BeautifulSoup is used to parse the HTML structure and extract relevant search result links.

Important: The HTML structure of search result pages can change over time due to updates by search engines. If you find that results are no longer displayed correctly for a particular search engine, the associated parsing function (parse_google_results, parse_bing_results, etc.) within the code might need adjustment.

✏️ Advanced Customization
The list of search engines is stored in a JSON format. You can customize it not only through the GUI but also by manually editing the search_engines.json file.

Format: Ensure the JSON format remains valid. Each entry is a key-value pair where the key is the search engine name (string, lowercase recommended) and the value is the URL template (string) which must contain {query} as a placeholder for your search term.
JSON

{
    "custom_search_engine_name": "[https://www.example.com/search?q=](https://www.example.com/search?q=){query}",
    "another_engine": "[https://another.search.com/s?text=](https://another.search.com/s?text=){query}&param=value"
}
Applying Manual Changes: After manually editing search_engines.json, you will need to restart the application for the changes to be loaded.


💡 Potential Future Developments
Here are some ideas for future enhancements:

Result Pagination: Implementation to navigate through multiple pages of search results.
Advanced Result Filtering: Adding options to filter results by domain, date, file type, etc.
Search History: Storing and managing a history of search queries and results.
Export Results: Functionality to export search results to common file formats (CSV, TXT, PDF).
Proxy Support: Adding settings to configure HTTP/Socks proxies.
Language/Region Selection: Allowing users to specify search language or region.


🤝 Contribution
Your contributions are highly valued! If you have ideas for improvements, find a bug, or wish to add new features, please:

Open an Issue to report a bug or suggest a feature.
Create a Pull Request with your changes.


⚖️ License
This project is licensed under the MIT License. See the LICENSE file  for more details.
