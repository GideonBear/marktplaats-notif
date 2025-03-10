import tomllib
from pathlib import Path
from shutil import copy
from string import digits, ascii_uppercase
from typing import Any

from schema import Schema, And, Optional, Use
from marktplaats import category_from_name


config_dir = Path("/config")
config_file = config_dir / "config.toml"

positive_int = And(int, lambda n: n > 0)

def is_zip_code(s: str) -> bool:
    # This is intentionally strict as 1234AB is the only tested format.
    #  Spaces, lowercase, etc. all might work, but are untested.
    return (
        len(s) == 6
        and all(c in digits for c in s[:4])
        and all(c in ascii_uppercase for c in s[4:])
    )

def is_http(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")

search_schema = {
    Optional("query"): And(str, len),
    Optional("price_from"): int,
    Optional("price_to"): int,
    Optional("zip_code"): And(str, is_zip_code),
    Optional("distance"): int,
    Optional("category"): And(str, len, Use(category_from_name)),  # type: ignore  # type checker error
}

schema = Schema({
    "general": {
        "interval": positive_int,
    },
    "notifications": {
        "ntfy": {
            "endpoint": And(str, is_http),
        }
    },
    "global": search_schema,
    "search": [search_schema],
})


def load_config():
    global config

    if not config_file.exists():
        copy("default_config.toml", config_file)
        print("Default configuration created")

    with config_file.open("rb") as file:
        config = schema.validate(tomllib.load(file))

        # Populate searches with global parameters
        config["search"] = list(map(
            # The search has priority over global; global will only fill omitted parameters
            # TODO: test that this works
            lambda search: config["global"] | search,
            config["search"],
        ))
        del config["global"]

        for search in config["search"]:
            # Allow query to be optional. Empty query has expected result
            if "query" not in search:
                search["query"] = ""


def get_config():
    return config


config: dict[str, Any] = None  # type: ignore
