import multiprocessing

# Bind to the PORT environment variable
bind = "0.0.0.0:10000"

# Worker configuration
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased timeout to 120 seconds for MediaPipe processing
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Reload on code changes (disable in production)
reload = False

