import random
import sys
from mitmproxy import io, http
import typing  # noqa


class Writer:
    def __init__(self, path: str) -> None:
        self.f: typing.IO[bytes] = open(path, "wb")
        self.w = io.FlowWriter(self.f)

    def response(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)

    def done(self):
        self.f.close()


addons = [Writer('out1.txt')]