from bs4 import BeautifulSoup as bs
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
import httpx
import logging
import os
import utils
import uvicorn

CONFIG = dict(dotenv_values(".env") or dotenv_values(".env.example"))
if not CONFIG:
    CONFIG = {
        "backlog": os.getenv("backlog", 2048),
        "debug": os.getenv("debug", False),
        "host": os.getenv("host", "0.0.0.0"),
        "log_level": os.getenv("log_level", "trace"),
        "port": os.getenv("port", 8080),
        "reload": os.getenv("reload", True),
        "timeout_keep_alive": os.getenv("timeout_keep_alive", 5),
        "workers": os.getenv("workers", 4),
    }
SAVE = False
CONFIG = utils.check_config(CONFIG)
api = FastAPI()


async def request_treatment(url: str, simple: bool = False) -> JSONResponse:
    """Makes an async request and treats the data.

    Args:
        url (str): URL to make the asynchronous request to.

    Returns:
        JSONResponse: JSON Response with the status code and the content of the response.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, follow_redirects=True, timeout=2)
        if resp.status_code != 200:
            status_code = resp.status_code
            detail = HTTPStatus(status_code).phrase
            return JSONResponse(status_code=status_code, content={"detail": detail})
        soup = bs(resp.text)
        csv = utils.extract_data(soup, simple)
        return JSONResponse(status_code=HTTPStatus.OK, content=csv)


@api.get("/", response_model=utils.Movie)
async def get() -> JSONResponse:
    """Checks the movies for today in Cines Van Dyck."""
    url = "https://www.cinesvandycktormes.com/cartelera"
    return await request_treatment(url)


@api.get("/simple/", response_model=utils.Movie)
async def get() -> JSONResponse:
    """Checks the movies for today in Cines Van Dyck."""
    url = "https://www.cinesvandycktormes.com/cartelera"
    return await request_treatment(url, simple=True)


def start() -> None:
    """Starts the Uvicorn server with the provided configuration."""
    uviconfig = {"app": "api:api", "interface": "asgi3"}
    uviconfig |= CONFIG
    try:
        uvicorn.run(**uviconfig)
    except Exception as e:
        print("Unable to run server.", e)


if __name__ == "__main__":
    start()
