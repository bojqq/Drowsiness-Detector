import multiprocessing
import os

# Bind to the PORT environment variable (Render provides this)
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}"

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

