import time

from flask import (
    current_app,
    g,
    redirect,
    request
)
from pukr import PukrLog


def get_app_logger() -> PukrLog:
    return current_app.extensions['logg']


def log_before():
    g.start_time = time.perf_counter()


def log_after(response):
    total_time = time.perf_counter() - g.start_time
    time_ms = int(total_time * 1000)
    get_app_logger().info(f'Timing: {time_ms}ms [{request.method}] -> {request.path}')
    return response


def clear_trailing_slash():
    req_path = request.path
    if req_path != '/' and req_path.endswith('/'):
        return redirect(req_path[:-1])
