"""Log creator for APIs

This package allows user to create logs on an API easly, tracing the time spent along the whole running and
along defined parts of code, and sending the entire log to an ElasticSearch server.

Example of use: to be created.
"""

import os
import time

from logger.crypto import Crypto

from pprint import pprint
from elasticsearch import Elasticsearch

from dotenv import load_dotenv, find_dotenv


class APIException(Exception):
    """Creates an special Exception for APIs."""

    CRAWLER = "CrawlerError"
    PARSE = "ParseError"
    ELEMENT = "ElementError"
    FILE = "FileError"
    REQUEST = "RequestError"
    CAPTCHA = "CaptchaError"

    def __init__(self, message, status_code=None, exception_type=None, error_name=CRAWLER):
        Exception.__init__(self)
        if not exception_type:
            exception_type = type(self).__name__
        self.message = f"{exception_type}: {message}"
        if status_code is not None:
            self.status_code = status_code
        self.error = error_name

    def to_dict(self):
        rv = self.__dict__
        rv["status_code"] = self.status_code
        return rv


class Logger:
    """Manager for log creation."""

    CRAWLER = "CrawlerError"
    PARSE = "ParseError"
    ELEMENT = "ElementError"
    FILE = "FileError"
    REQUEST = "RequestError"
    CAPTCHA = "CaptchaError"

    def __init__(self, app: str = None, route: str = "/", method: str = None, env_path=""):
        self.app = app
        self.route = route
        self.method = method
        self.status_code = 200
        self.inputs: list = []
        self.parts: list = []
        self.part: dict = {}
        self.part_start_time = 0.0
        self.running_time = None

        self.exception_info = None
        self.exception_type = None
        self.exception_message = None

        self.error_name = None
        self.exception_message = None

        if not env_path:
            env_path = find_dotenv()
        load_dotenv(env_path)

        print(env_path)

        CLOUD_ID = os.getenv(
            "CLOUD_ID"
        )  # "thales-test:c291dGhhbWVyaWNhLWVhc3QxLmdjcC5lbGFzdGljLWNsb3VkLmNvbSQ2MzU3NzkxYjM0ZWM0YWRmYjNhMjNiN2E0NjI5ODQyOSRlNzE4NmUxNmQwYjU0MDVkYTBhY2U3ODlkZDk1ODMzMA=="
        USERNAME = os.getenv("USERNAME")  # "elastic"
        PASSWORD = os.getenv("PASSWORD")  # "zRXefzq5wgRFa7wvEqfuokhD"

        print(CLOUD_ID)
        print(USERNAME)
        print(PASSWORD)

        self.es = Elasticsearch(cloud_id=CLOUD_ID, http_auth=(USERNAME, PASSWORD))

    def add_input(self, data, hashed=False):
        if hashed:
            crypto = Crypto()

        if type(data) == dict:
            for param in data:
                value = data[param]
                if hashed:
                    value = crypto.encrypt(value)

                inp = {"name": param, "value": value, "hashed": hashed}
                self.inputs.append(inp)

        elif type(data) in [list, tuple]:
            for value in data:
                if hashed:
                    value = crypto.encrypt(value)

                inp = {"name": len(self.inputs), "value": value, "hashed": hashed}

                self.inputs.append(inp)

        else:
            value = data
            if hashed:
                value = crypto.encrypt(value)

            inp = {"name": len(self.inputs), "value": value, "hashed": hashed}

            self.inputs.append(inp)

    def clear_log(self):
        self.status_code = 200
        self.inputs: list = []
        self.parts: list = []
        self.part: dict = {}
        self.part_start_time = 0
        self.running_time = None

        self.exception_info = None
        self.exception_type = None
        self.exception_message = None

        self.error_name = None
        self.exception_message = None

        self.dict = {}

    def set_log(self, error_name, message=""):
        self.error_name = error_name
        self.exception_message = message

    def clear(self):
        self.error_name = None
        self.exception_message = None

    def start_time(self):
        self.running_start_time = time.time()

    def start_part(self, part_name: str = None):
        if not part_name:
            part_name = f"part{len(self.parts)}"
        if self.part:
            self.part["duration"] = time.time() - self.part_start_time
            self.parts.append(self.part)
            self.part = {}
        self.part["name"] = part_name
        self.part_start_time = time.time()

    def stop_part(self):
        if self.part:
            self.part["duration"] = time.time() - self.part_start_time
            self.parts.append(self.part)
            self.part = {}

    def exception(self, exception=None, message=None, status_code=500, exception_type=None, verbose=False):
        if exception:
            self.exception_message = str(exception) if not self.exception_message else self.exception_message
            self.exception_type = type(exception).__name__
        self.exception_message = message if message else self.exception_message
        self.exception_type = exception_type if exception_type else self.exception_type

        self.status_code = status_code

        self.exception_info = {
            "error_message": self.exception_message,
            "error_name": self.error_name,
            "status_code": self.status_code,
            "exception_type": self.exception_type,
        }

        self.send_log()
        if verbose:
            return APIException(message=self.exception_message, error_name=self.error_name, status_code=self.status_code)

    def send_log(self):
        self.stop_part()
        self.running_time = time.time() - self.running_start_time

        log = self.to_dict()

        pprint(log)

        # res = es.index(index='logs', body=log)

    def to_dict(self):
        if type(self.method) == str:
            self.method = self.method.upper()

        self.dict = {
            "app": self.app,
            "route": self.route,
            "method": self.method,
            "inputs": self.inputs,
            "running": {"parts": self.parts, "running_time": self.running_time, "status_code": self.status_code},
        }

        if self.exception_info:
            self.dict["exception"] = self.exception_info

        return self.dict

    def tracelog(self, object):
        self.last_trace = object
