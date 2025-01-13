import time
from collections import defaultdict
from datetime import datetime
from typing import Any, NoReturn

from marktplaats import SearchQuery, Listing

from marktplaats_notif import notifiers
from marktplaats_notif.config import config


def query_from_search(search: dict[str, Any], offered_since: datetime) -> list[Listing]:
    return SearchQuery(**search, limit=30, offered_since=offered_since).get_listings()


def main() -> NoReturn:
    print("Started")
    # TODO: Support other notification channels?
    notifier = notifiers.Ntfy(config)
    notifier.notify_started()

    last_send_time = datetime.now()
    while True:
        print(f"Doing round from {last_send_time}, total of {datetime.now() - last_send_time}...")

        # TODO: deduplicate listings
        listings = defaultdict(list)
        for search_i, search in enumerate(config["search"]):
            print(f"Search: {search["query"]}")
            try:
                current_listings = query_from_search(search, last_send_time)
            except Exception as e:
                notifier.notify_error(e, "during search")
                continue
            for listing in current_listings:
                listings[listing].append(search_i)
            print("Done")

        print("Notifying...")
        for listing, search_indexes in listings.items():
            print(f"Notifying for listing: {listing.title}: {search_indexes}")
            notifier.notify_listing(listing, search_indexes)

        print("Done round")
        last_send_time = datetime.now()

        time.sleep(config["general"]["interval"])


if __name__ == '__main__':
    main()
