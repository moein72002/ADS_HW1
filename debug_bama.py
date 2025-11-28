import requests
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    # Add other headers if needed, but UA is usually enough for structure check
}
try:
    resp = requests.get("https://bama.ir/car/samand", headers=HEADERS, timeout=10)
    with open("bama_page.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Saved bama_page.html")
except Exception as e:
    print(e)

