from scraper.crawler import WebsiteCrawler
from utils.url_utils import normalize_url


def main():

    print("=" * 60)
    print("          AskTheWeb - RAG Powered Website Chatbot")
    print("=" * 60)

    try:

        url = normalize_url(input("\nEnter Website URL: "))

        crawler = WebsiteCrawler()

        pages = crawler.crawl(url)

        print("\n✅ Website crawled successfully!\n")

        print(f"Total Pages Crawled : {len(pages)}")

        for index, page in enumerate(pages, start=1):

            print("-" * 60)
            print(f"Page {index}")
            print(f"Title       : {page['title']}")
            print(f"Text Length : {len(page['text'])} characters")
            print(f"Valid Links : {len(page['links'])}")

    except Exception as e:

        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()