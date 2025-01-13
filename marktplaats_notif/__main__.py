import sys
import time
from collections import defaultdict
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


def notify(listing: Listing | str, search_is: list[int] | None = None) -> None:
    if isinstance(listing, str):
        resp = requests.post(
            config["notifications"]["ntfy"]["endpoint"],
            data="You will receive notifications via this channel.",
            headers={
                "Title": listing,
            }
        )
    else:
        headers = {
            "Title": prepare_header(f"{listing.title}"),
            "Click": prepare_header(listing.link),
            "Icon": prepare_header(ICON),
        }
        if listing.images:
            headers["Attach"] = prepare_header(listing.images[0].extra_large)

        resp = requests.post(
            config["notifications"]["ntfy"]["endpoint"],
            data=f"{listing.price_as_string(lang="nl")} 📍 {listing.location.city} ({listing.location.distance / 1000} km)\n{listing.description}\nFrom search: {", ".join(map(str, search_is))}",
            headers=headers
        )
    if not resp.status_code == 200:
        raise Exception("Failed to send notification", resp)


def main() -> int:
    print("Started")
    notify("marktplaats-notif started.")

    last_send_time = datetime.now()
    while True:
        print(f"Doing round from {last_send_time}, total of {datetime.now() - last_send_time}...")

        # TODO: deduplicate listings
        listings = defaultdict(list)
        for search_i, search in enumerate(config["search"]):
            print(f"Search: {search["query"]}")
            for listing in query_from_search(search, last_send_time):
                listings[listing].append(search_i)
            print("Done")

        print("Notifying...")
        for listing, search_is in listings.items():
            print(f"Notifying for listing: {listing.title}: {search_is}")
            notify(listing, search_is)

        print("Done round")
        last_send_time = datetime.now()

        time.sleep(config["general"]["interval"])


if __name__ == '__main__':
    sys.exit(main())
