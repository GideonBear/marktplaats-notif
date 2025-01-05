import sys
import time
from datetime import datetime
from typing import Any

import requests
from marktplaats import SearchQuery, Listing

from marktplaats_notif.config import config


ICON = "https://user-images.githubusercontent.com/20847106/64513789-988b7500-d2e9-11e9-91e9-fef666b1e3c0.png"


def query_from_search(search: dict[str, Any], offered_since: datetime) -> list[Listing]:
    return SearchQuery(**search, limit=30, offered_since=offered_since).get_listings()


def prepare_header(s: str) -> bytes:
    return s.encode()


def notify(listing: Listing) -> None:
    resp = requests.post(
        config["notifications"]["ntfy"]["endpoint"],
        data=f"Location: {listing.location.city}\n{listing.description}",
        headers={
            "Title": prepare_header(f"{listing.title} ({listing.price_as_string_nl()})"),
            "Click": prepare_header(listing.link),
            "Attach": prepare_header(listing.images[0].extra_large),
            "Icon": prepare_header(ICON),
        },
    )
    if not resp.status_code == 200:
        raise Exception("Failed to send notification", resp)


def main() -> int:
    print("Started")

    last_send_time = datetime.now()
    while True:
        print(f"Doing round from {last_send_time}, total of {datetime.now() - last_send_time}...")

        for search in config["search"]:
            print(f"Search: {search["query"]}")
            for listing in query_from_search(search, last_send_time):
                print(f"Notifying for listing: {listing.title}")
                notify(listing)
            print("Done")
        print("Done round")
        last_send_time = datetime.now()

        time.sleep(config["general"]["interval"])


if __name__ == '__main__':
    sys.exit(main())
