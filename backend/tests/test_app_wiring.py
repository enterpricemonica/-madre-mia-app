"""Does the REAL application work — not a stand-in assembled by the tests?

Until now conftest built its own FastAPI instance from a handful of routers.
That tests the routers, but never the app that actually ships: its CORS policy,
its middleware, the routers main.py forgets to register, or a route declared
directly on `app`. This file is about the real thing.
"""


def test_root_endpoint_answers(client):
    """Declared directly on `app`, so the old parallel app could not see it."""
    r = client.get("/")
    assert r.status_code == 200
    assert "Madre Mia" in r.json()["message"]


def test_every_router_is_registered(client):
    """A router that exists but is never included is invisible until a customer
    hits a 404. Check one representative path per router."""
    for path in ["/menu/", "/tables/", "/orders/", "/health"]:
        r = client.get(path)
        assert r.status_code != 404, f"{path} is not wired into the app"


def test_unknown_origin_never_gets_an_authenticated_grant(client):
    """The real failure mode, which checking for a literal "*" would miss.

    Starlette does not echo "*" when credentials are on — it echoes the caller's
    own Origin. So the header to watch is not the wildcard; it is any arbitrary
    origin coming back *together with* Allow-Credentials, which is a standing
    invitation for any website to act as the logged-in owner.
    """
    r = client.get("/", headers={"Origin": "https://sitio-malicioso.example"})
    allowed = r.headers.get("access-control-allow-origin")
    credentials = r.headers.get("access-control-allow-credentials")

    if credentials == "true":
        assert allowed != "https://sitio-malicioso.example", (
            "an arbitrary origin was granted credentialed access"
        )
