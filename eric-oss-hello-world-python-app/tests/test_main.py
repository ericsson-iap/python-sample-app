"""Tests which cover the routes of the application"""


def test_get_root_returns_bad_response(client):
    """
    GET to "/"
    400 Bad Request
    """
    response = client.get("/sample-app/python/")
    assert response.status_code == 400


def test_get_hello_returns_hello_world(client):
    """
    GET to "/hello"
    200 OK
    Body "Hello World!\n"
    """
    response = client.get("/sample-app/python/hello")
    assert [response.text, response.status_code] == ["Hello World!\n", 200]


def test_get_metrics_returns_metrics(client):
    """
    GET to "/metrics"
    200 OK
    Body containing Prometheus-compatible metrics
    """
    response = client.get("/sample-app/python/metrics")
    assert response.status_code == 200
    assert "eric_oss_hello_world_python_app_requests_total 0.0" in response.text


def test_metrics_does_not_expose_created(client):
    """
    GET to "/metrics"
    200 OK
    Body does not contain _created gauges for Prometheus-compatible metrics
    """
    response = client.get("/sample-app/python/metrics")
    assert response.status_code == 200
    assert "_created" not in response.text


def test_metrics_successfully_increments(client):
    """
    GET to "/metrics"
    200 OK
    Body containing metrics which have incremented by 1
    """
    client.get("/sample-app/python/hello")
    response = client.get("/sample-app/python/metrics")
    assert response.status_code == 200
    assert "eric_oss_hello_world_python_app_requests_total 1.0" in response.text


def test_get_health_returns_health_check(client):
    """
    GET to "/health"
    200 OK
    Body "Ok\n"
    """
    response = client.get("/sample-app/python/health")
    assert [response.text, response.status_code] == ["Ok\n", 200]
