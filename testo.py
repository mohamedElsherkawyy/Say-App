import requests

url = "https://hadithapi.com/api/hadiths"
params = {
    "apiKey": "$2y$10$iGzQEOH6XtNrtH86zK9xexFPNKVzny7QFYToeQFiFTmOjGUxZYW"
}

response = requests.get(url, params=params)

data = response.json()

def clean_hadiths(data):
    hadiths = data.get("hadiths", {}).get("data", [])
    
    cleaned = []
    
    for h in hadiths:
        cleaned.append({
            "arabic": h.get("hadithArabic"),
            "english": h.get("hadithEnglish"),
            "book": h.get("book", {}).get("bookName"),
            "chapter": h.get("chapter", {}).get("chapterTitle"),
            "status": h.get("status"),
        })
    
    return cleaned

cleaned_data = clean_hadiths(data)

for h in cleaned_data:
    print(h["arabic"])
    print("-----")