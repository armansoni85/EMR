import multiprocessing
import os


bind = "127.0.0.1:8000"
workers = 2
threads = 3
worker_class = "gthread"
keepalive = 10

secure_scheme_headers = {"X-FORWARDED-PROTO": "https"}

reload = True
errorlog = "-"
accesslog = "-"
loglevel = "debug"
timeout = 300
