import tomllib
import traceback
from pathlib import Path

import tomli_w
from flask import Flask, render_template, flash, redirect, request, abort
from marktplaats import get_l1_categories, get_l2_categories_by_parent, category_from_name, L2Category

from marktplaats_notif.config import config_file, schema

app = Flask(__name__)
app.config["SECRET_KEY"] = "582a4ea1ffc728b84927802a2f64c19057885baf148a661a5203ba8cf0768b4d"


def get_config() -> dict:
    with config_file.open("rb") as file:
        # Load the config file. Do schema validation (and manipulation),
        #  but don't do the extra things that the `load_config` function does
        #  (like populating with global).
        return schema.validate(tomllib.load(file))


def set_config(config: dict) -> None:
    # Reverse the changes done by the schema
    for search in (config["global"], *config["search"]):
        if "category" in search:
            search["category"] = search["category"].name

    schema.validate(config)

    config_backups = Path("config_backups")
    config_backups.mkdir(exist_ok=True)
    backup_num = len(list(config_backups.glob("config_*.toml"))) + 1
    config_backup = config_backups / f"config_{backup_num}.toml"
    config_backup.write_text(config_file.read_text())

    with config_file.open("wb") as file:
        tomli_w.dump(config, file)


@app.route("/")
def route_index():
    config = get_config()

    selected_l1_categories = []
    selected_l2_categories = []
    for search in (config["global"], *config["search"]):
        if "category" in search:
            selected_category = search["category"]
            if isinstance(selected_category, L2Category):
                selected_l2_category = selected_category
                selected_l1_category = selected_l2_category.parent
            else:
                selected_l1_category = selected_category
                selected_l2_category = None
        else:
            selected_l1_category = None
            selected_l2_category = None

        selected_l1_categories.append(selected_l1_category)
        selected_l2_categories.append(selected_l2_category)

    return render_template(
        "index.html",
        searches=(config["global"], *config["search"]),
        config=config,
        l1_categories=list(get_l1_categories()),
        l2_categories_by_parent=get_l2_categories_by_parent(),
        category_from_name=category_from_name,
        selected_l1_categories=selected_l1_categories, # if category == (search.get('category') or category_from_name(search['category'])) or category == (search.get('category') or category_from_name(search['category'])).parent
        selected_l2_categories=selected_l2_categories, # if category == (search.get('category') or category_from_name(search['category']))
    )


@app.route("/api/update", methods=["POST"])
def route_api_update():
    try:
        if "update" in request.form:
            return update_update()
        elif "add_search" in request.form:
            return update_add_search()
        elif "delete_search" in request.form:
            return update_delete_search()
        else:
            abort(400)

    except Exception:
        traceback.print_exc()
        raise


def update_update():
    keys = {
        key: request.form.getlist(f"{key}[]")
        for key in ("query", "price_from", "price_to", "zip_code", "distance", "l1_category", "l2_category")
    }

    searches = [
        {key: value[i] for key, value in keys.items() if value[i]}
        for i in range(len(keys["query"]))
    ]

    for search in searches:
        if "price_from" in search:
            search["price_from"] = int(search["price_from"])
        if "price_to" in search:
            search["price_to"] = int(search["price_to"])
        if "distance" in search:
            search["distance"] = int(search["distance"])

        if "l2_category" in search:
            search["category"] = category_from_name(search["l2_category"])
            if not search["category"]:
                flash(f"Unexpected error: Invalid category {search['l2_category']}")  # Should never happen
                return redirect("/")
            elif "l1_category" not in search:
                flash(f"Unexpected error: Missing l1_category")  # Should never happen
                return redirect("/")
            elif category_from_name(search["l1_category"]) != search["category"].parent:
                flash(f"Unexpected error: Category {search['l2_category']} is not a subcategory of {search['l1_category']}")  # Should never happen
                return redirect("/")

            del search["l1_category"]
            del search["l2_category"]

        elif "l1_category" in search:
            search["category"] = category_from_name(search["l1_category"])
            if not search["category"]:
                flash(f"Unexpected error: Invalid category {search['l1_category']}")  # Should never happen
                return redirect("/")

            del search["l1_category"]

    config = {
        "general": {
            "interval": int(request.form["general.interval"]),
        },
        "notifications": {
            "ntfy": {
                "endpoint": request.form["notifications.ntfy.endpoint"],
            },
        },
        "global": searches[0],
        "search": searches[1:],
    }

    set_config(config)
    flash("Success, config written")
    return redirect("/")


def update_add_search():
    config = get_config()
    config["search"].append({})
    set_config(config)
    flash("Success, empty search added")
    return redirect("/")


def update_delete_search():
    search_i = int(request.form["delete_search"])
    config = get_config()
    config["search"].pop(search_i)
    set_config(config)
    flash(f"Success, removed search {search_i}")
    return redirect("/")
