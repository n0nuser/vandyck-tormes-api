from bs4 import BeautifulSoup as bs
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class Movie(BaseModel):
    """Model for the Movie Information."""

    title: str
    synopsis: str
    release_date: str
    length: int
    trailer: str
    director: str
    cast: str
    genre: list
    available_hours: list


def check_config(CONFIG: dict) -> dict:
    """Validates the configuration file. If it's valid, parses it and returns it.

    Args:
        CONFIG (dict): Config parameters:
            "backlog": int
            "debug": bool
            "host": str
            "log_level": str
            "port": int
            "reload": bool
            "timeout_keep_alive": int
            "workers": int

    Raises:
        ValueError: If parameters are missing in the config file.
        ValueError: If parameters doesn't have a valid type.

    Returns:
        dict: Config file parsed to match the expected format.
    """
    fields = {
        "backlog": int,
        "debug": bool,
        "host": str,
        "log_level": str,
        "port": int,
        "reload": bool,
        "timeout_keep_alive": int,
        "workers": int,
    }

    for field in fields:
        if field not in CONFIG:
            raise ValueError(f"{field} is missing in config file.")

    config = {}
    for field_name, field_value in fields.items():
        try:
            config[field_name] = field_value(CONFIG[field_name])
        except ValueError as e:
            raise ValueError(f"{field_name} is not a valid {field_value}") from e
    return config


#######################################################################################################################


def extract_data(data: bs, simple: bool = False) -> list:
    """From a BeautifulSoup object, extracts the Movie class attributes.

    Args:
        data (bs): BeautifulSoup object with the HTML data.

    Returns:
        list: Returns a list of Movie class objects.
    """
    articles = data.find_all("article")
    movies = []
    for article in articles:
        trailer = article.find("div", {"class": "action-group my-2 text-center"})
        if trailer:
            trailer = trailer.find("a").get("href", "")
        else:
            continue

        info = article.find("div", {"class": "col-md-8"})

        title = info.find("h2").text

        if title is None:
            continue

        synopsis = info.find("p").text

        table_data = info.find("table").find_all("tr")
        for data in table_data:
            if "FECHA ESTRENO" in data.text:
                release_date = data.find("td").text
            elif "DURACIÓN" in data.text:
                length = data.find("td").text
                length = int(length.split(" ")[0])
            elif "DIRECTOR" in data.text:
                director = data.find("td").text
            elif "REPARTO" in data.text:
                cast = data.find("td").text

        genres = data.find_all("a", {"class": "mr-1"})
        genre = [genre.text for genre in genres]

        hours = info.find(
            "div", {"class": "tab-pane fade tab-pane fade show active"}
        ).find_all("a", {"class": "mr-1 mb-1"})
        available_hours = [hour.text for hour in hours]

        if simple:
            movies.append(f"{title} -> {available_hours}")
        else:
            movies.append(
                jsonable_encoder(
                    Movie(
                        title=title,
                        synopsis=synopsis,
                        release_date=release_date,
                        length=length,
                        trailer=trailer,
                        director=director,
                        cast=cast,
                        genre=genre,
                        available_hours=available_hours,
                    )
                )
            )

    return movies
