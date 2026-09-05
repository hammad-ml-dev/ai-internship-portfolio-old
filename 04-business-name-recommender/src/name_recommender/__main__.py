import os

import uvicorn
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from importlib.resources import files as pkg_files

from .api import app


# Mount static frontend
static_dir = str(pkg_files("name_recommender").joinpath("static"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index_redirect():
	return RedirectResponse(url="/static/index.html")


@app.get("/ui")
def ui_page():
	return FileResponse(os.path.join(static_dir, "index.html"))


def run():
	port = int(os.environ.get("PORT", "8000"))
	uvicorn.run("name_recommender.__main__:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
	run()


