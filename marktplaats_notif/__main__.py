print("Import time")

import sys
import time
from datetime import datetime
from typing import Any

import requests
from marktplaats import SearchQuery, Listing

from marktplaats_notif.config import config


def query_from_search(search: dict[str, Any], offered_since: datetime) -> list[Listing]:
    return SearchQuery(**search, limit=30, offered_since=offered_since).get_listings()


def prepare_header(s: str) -> bytes:
    return s.encode()


def notify(listing: Listing) -> None:
    resp = requests.post(
        config["notifications"]["ntfy"]["endpoint"],
        data=listing.description,
        headers={
            "Title": prepare_header(f"marktplaats-notif: {listing.title} (€ {listing.price_as_string_nl()})"),
            "Click": prepare_header(listing.link),
        },
    )
    if not resp.status_code == 200:
        raise Exception("Failed to send notification", resp)


def main() -> int:
    print("Started")
    while True:
        print("Doing round...")
        last_send_time = datetime.now()

        for search in config["search"]:
            print(f"Search: {search["query"]}")
            for listing in query_from_search(search, last_send_time):
                print(f"Notifying for listing: {listing.title}")
                notify(listing)
            print("Done")
        print("Done round")

        time.sleep(config["general"]["interval"])


if __name__ == '__main__':
    sys.exit(main())
