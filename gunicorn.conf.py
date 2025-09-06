import os

bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
workers = 2
threads = 4
worker_class = "sync"
worker_tmp_dir = "/dev/shm"
log_level = "info"
accesslog = "-"
errorlog = "-"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True

