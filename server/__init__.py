import tomllib

from flask import Flask, render_template
from marktplaats import get_l1_categories, get_l2_categories_by_parent, category_from_name, L2Category

from marktplaats_notif.config import config_file, schema

app = Flask(__name__)


@app.route("/")
def route_index():
    with config_file.open("rb") as file:
        config = schema.validate(tomllib.load(file))

    if "category" in config["search"]:
        selected_category = category_from_name(config["search"]["category"])
        if isinstance(selected_category, L2Category):
            selected_l2_category = selected_category
            selected_l1_category = selected_l2_category.parent
        else:
            selected_l1_category = selected_category
            selected_l2_category = None
    else:
        selected_l1_category = None
        selected_l2_category = None

    return render_template(
        "index.html",
        searches=[config["global"], *config["search"]],
        l1_categories=list(get_l1_categories()),
        l2_categories_by_parent=get_l2_categories_by_parent(),
        category_from_name=category_from_name,
        selected_l1_category=selected_l1_category, # if category == (search.get('category') or category_from_name(search['category'])) or category == (search.get('category') or category_from_name(search['category'])).parent
        selected_l2_category=selected_l2_category, # if category == (search.get('category') or category_from_name(search['category']))
    )


@app.route("/write", methods=["POST"])
def route_write():
    ... # TODO
