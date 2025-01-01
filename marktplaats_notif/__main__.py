import sys

from marktplaats import SearchQuery

from marktplaats_notif.config import config


def main() -> int:
    print("Hello world!")
    print(config["general"]["interval"])
    print(SearchQuery("fiets", limit=1).get_listings()[0].title)
    return 0


if __name__ == '__main__':
    sys.exit(main())
