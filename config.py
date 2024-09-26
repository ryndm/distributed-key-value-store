import os

# Network settings
HOST = 'localhost'
PORT_RANGE_START = 5000
NUM_NODES = 3

# Key-value store settings
REPLICATION_FACTOR = 2

# Networking settings
SOCKET_TIMEOUT = 5  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # for exponential backoff

# Consistent hashing settings
VIRTUAL_NODES = 100

# Logging settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Data persistence settings
DATA_DIR = 'data'

# Consensus settings
RAFT_ELECTION_TIMEOUT = 150  # milliseconds
RAFT_HEARTBEAT_INTERVAL = 50  # milliseconds

# Load balancing settings
LOAD_BALANCER_PORT = 6000

# Authentication settings
AUTH_SECRET_KEY = 'your-secret-key'
TOKEN_EXPIRATION = 3600  # seconds

# Encryption settings
ENCRYPTION_KEY = b'your-32-byte-key'  # 32 bytes for AES-256

# Monitoring settings
PROMETHEUS_PORT = 8000