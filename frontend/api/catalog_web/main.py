"""The catalog web service: read the catalog and submit products for review."""

import logging

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from infrahub_sdk.exceptions import Error as InfrahubError

from catalog_web.catalog import CatalogCache
from catalog_web.infrahub import get_client
from catalog_web.submissions import Submission, SubmissionError, submit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Catalog web service", docs_url=None, redoc_url=None, openapi_url=None)
cache = CatalogCache()

UNAVAILABLE = "The catalog is not available right now. Try again later."


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/catalog")
async def catalog() -> dict:
    try:
        return await cache.get(get_client())
    except (httpx.HTTPError, InfrahubError):
        logger.exception("reading the catalog failed")
        raise HTTPException(status_code=503, detail=UNAVAILABLE)


@app.post("/api/submissions", status_code=201)
async def submissions(submission: Submission) -> dict[str, str]:
    try:
        reference = await submit(get_client(), submission)
    except SubmissionError as error:
        return JSONResponse(status_code=error.status_code, content={"detail": error.message})
    except (httpx.HTTPError, InfrahubError):
        logger.exception("saving a submission failed")
        return JSONResponse(
            status_code=502,
            content={"detail": "Your submission was not saved. Nothing was created. Please try again."},
        )
    return {"reference": reference}
