import aiohttp
import lsdb
from hats.io.file_io.file_pointer import get_upath_for_protocol
from upath import UPath

VIZCAT_GAIA_URL = "https://vizcat.cds.unistra.fr/hats:n=10000/gaia_dr3/"


async def _on_request_end(_session, _ctx, params):
    response = params.response
    print(f"{params.method} {params.url} -> {response.status} {response.reason}")
    if response.status >= 400:
        print(f"  response headers: {dict(response.headers)}")
        body = await response.text(errors="replace")
        print(f"  response body: {body}")


async def _on_request_exception(_session, _ctx, params):
    print(f"{params.method} {params.url} -> no response: {params.exception!r}")


async def _get_traced_client(**kwargs):
    """Print every HTTP request/response so failures show the status code the server returned.

    fsspec converts a 404 into a bare FileNotFoundError and drops the response details,
    so we hook into aiohttp directly.
    """
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_end.append(_on_request_end)
    trace_config.on_request_exception.append(_on_request_exception)
    return aiohttp.ClientSession(trace_configs=[trace_config], **kwargs)


def test_from_vizcat():
    # Use a traced client to see the HTTP status code if the request fails.
    gaia = lsdb.open_catalog(
        VIZCAT_GAIA_URL,
        columns=["DR3Name", "RA_ICRS", "DE_ICRS"],
        storage_options={"get_client": _get_traced_client, "client_kwargs": {"timeout": 300}},
    )

    head_frame = gaia.head(10)
    assert len(head_frame) == 10
