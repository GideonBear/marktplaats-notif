import traceback

import requests
from marktplaats import Listing

from marktplaats_notif.constants import ICON
from marktplaats_notif.notifier import Notifier


def prepare_header(s: str) -> bytes:
    return s.encode()


class Ntfy(Notifier):
    def __init__(self, config):
        config = config["notifications"]["ntfy"]
        self.endpoint = config["endpoint"]

    def post(self, headers: dict[str, str], data: str) -> None:
        resp = requests.post(
            self.endpoint,
            data=data,
            headers={k: prepare_header(v) for k, v in headers.items()},
        )
        if not resp.status_code == 200:
            raise Exception("Failed to send notification", resp)

    def notify_started(self) -> None:
        self.post(
            headers={
                "Title": "marktplaats-notif started.",
                "Tags": "gear",
            },
            data="You will receive notifications via this channel."
        )

    def notify_listing(self, listing: Listing, search_is: list[int]) -> None:
        headers = {
            "Title": f"{listing.title}",
            "Click": listing.link,
            "Icon": ICON,
        }
        if listing.images:
            headers["Attach"] = listing.images[0].extra_large

        price = listing.price_as_string(lang="nl")
        city = listing.location.city
        distance = listing.location.distance / 1000 if listing.location.distance is not None else "(NO ZIP CODE)"
        description = listing.description
        from_searches = ", ".join(map(str, search_is))

        self.post(
            headers=headers,
            data=f"{price} 📍 {city} ({distance} km)\n{description}\nFrom searches: {from_searches}",
        )

    def notify_error(self, error: Exception, context: str) -> None:
        self.post(
            headers={
                "Title": f"marktplaats-notif has had an error {context}.",
                "Tags": "warning"
            },
            data=f"{traceback.format_exc()}"
        )
