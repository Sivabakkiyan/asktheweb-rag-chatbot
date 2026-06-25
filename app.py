from scraper.crawler import WebsiteCrawler
from scraper.parser import WebsiteParser
from utils.url_utils import normalize_url


def main():

    print("=" * 60)
    print("        AskTheWeb - RAG Powered Website Chatbot")
    print("=" * 60)

    url = input("\nEnter Website URL: ").strip()

    crawler = WebsiteCrawler()
    parser = WebsiteParser()

    try:

        html = crawler.fetch_page(url)

        page = parser.parse(html, url)

        print("\n✅ Website fetched successfully!\n")

        print(f"Title       : {page['title']}")
        print(f"Text Length : {len(page['text'])} characters")
        print(f"Links Found : {len(page['links'])}")

    except Exception as e:

        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()