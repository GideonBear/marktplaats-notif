import sys

from marktplaats import SearchQuery


def main() -> int:
    print("Hello world!")
    print(SearchQuery("fiets", limit=1).get_listings()[0].title)
    return 0


if __name__ == '__main__':
    sys.exit(main())
