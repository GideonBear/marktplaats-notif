import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, NoReturn

from marktplaats import SearchQuery, Listing

from marktplaats_notif import notifiers
from marktplaats_notif.config import get_config, load_config
from marktplaats_notif.notifier import Notifier


LIMIT = 30


def filter_listing(l: Listing) -> bool:
    return l.title not in get_config()["general"]["title_blacklist"]


def query_from_search(search: dict[str, Any], offered_since: datetime, notifier: Notifier) -> list[Listing]:
    if "distance" in search:
        search["distance"] *= 1000  # marktplaats-py expects meters
    listings = SearchQuery(
        **search,
        limit=LIMIT,
        offered_since=offered_since,
    ).get_listings()

    listings = list(filter(filter_listing, listings))

    if len(listings) >= 30:
        # TODO: implement pagination and remove this warning
        notifier.notify_warning(f"The search limit of {LIMIT} was reached during this search. You are missing searches.")
    if len(listings) > 30:
        notifier.notify_error(f"The search limit of {LIMIT} was exceeded by the API somehow. This should not happen at all.")

    return listings


def main() -> NoReturn:
    print("Started")
    load_config()
    # TODO: Support other notification channels?
    notifier: Notifier = notifiers.Ntfy(get_config())
    notifier.notify_started()

    # Check for new listings from before it was started.
    #  This results in duplicates but reduces the chance to miss something.
    last_send_time = datetime.now() - timedelta(seconds=get_config()["general"]["interval"])

    while True:
        # Load configuration again to make sure it's up to date
        #  from potential changes by the web-interface
        try:
            load_config()
        except Exception:
            notifier.notify_exception("during config load")
            continue

        print(f"Doing round from {last_send_time}, total of {datetime.now() - last_send_time}...")

        # TODO: deduplicate listings
        listings = defaultdict(list)
        for search_i, search in enumerate(get_config()["search"]):
            print(f"Search: {search["query"]}")
            try:
                current_listings = query_from_search(search, last_send_time, notifier)
            except Exception:
                notifier.notify_exception("during search")
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

        time.sleep(get_config()["general"]["interval"])


if __name__ == '__main__':
    main()
