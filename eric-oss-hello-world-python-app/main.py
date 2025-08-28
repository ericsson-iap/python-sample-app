#!/usr/bin/env python3
"""
Flask Application for Hello World Service

This Python script defines a Flask application that implements a simple "Hello World" service
along with a health check and metrics endpoints.
"""
import time
from flask import abort
from flask import Flask
from login import login
from mtls_logging import MtlsLogging, Severity
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import (
    disable_created_metrics,
    make_wsgi_app,
    CollectorRegistry,
    Counter,
)

SERVICE_PREFIX = "python_hello_world"


class Application(Flask):
    """The Flask application itself. Subclassed for testing."""

    def __init__(self):
        super().__init__(__name__)
        disable_created_metrics()
        self.counters = {"total_requests": 0}
        self.session = {"token": None, "expiry_time": 0}
        self.create_metrics()
        self.wsgi_app = DispatcherMiddleware(
            self.wsgi_app,
            {"/sample-app/python/metrics": make_wsgi_app(registry=self.registry)},
        )
        self.logger = MtlsLogging()

        @self.route("/sample-app/python/")
        def root():
            """This route returns a 400 Bad Request HTTP response."""
            self.logger.log(
                "400 Bad request: User tried accessing '/sample-app/python/'",
                Severity.INFO,
            )
            abort(400)

        @self.route("/sample-app/python/hello")
        def hello():
            """
            This route performs a login operation and returns
            a simple "Hello World!" greeting and increments the
            total request counter.
            """
            self.update_session()
            self.requests_total.inc()
            self.logger.log("200 OK: Hello World!", Severity.INFO)
            return "Hello World!\n"

        @self.route("/sample-app/python/health")
        def health():
            """
            This route provides a simple health check endpoint, returning "Ok" to
            indicate that the application is healthy.
            """
            self.update_session()
            self.logger.log("200 OK: Health check", Severity.DEBUG)
            return "Ok\n"

    def update_session(self):
        """Refresh session if it expires."""
        if int(time.time()) >= self.session["expiry_time"]:
            try:
                self.session["token"], self.session["expiry_time"] = login()
            except Exception as e:
                # since the token isn't used for anything,
                # this is just a WARNING level log instead of ERROR
                self.logger.log(f"Login failed: {e}", Severity.WARNING)

    def create_metrics(self):
        self.registry = CollectorRegistry()
        self.requests_total = Counter(
            namespace=SERVICE_PREFIX,
            name="requests_total",
            documentation="Total number of API requests",
        )
        self.registry.register(self.requests_total)


if __name__ == "__main__":
    instance = Application()
    instance.run(host="0.0.0.0", port="8050")
