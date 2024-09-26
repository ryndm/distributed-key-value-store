import hashlib
import logging
import json
import os
from cryptography.fernet import Fernet
import jwt
from config import LOG_LEVEL, LOG_FORMAT, AUTH_SECRET_KEY, ENCRYPTION_KEY

def hash_key(key):
  return hashlib.md5(key.encode()).hexdigest()

def setup_logger(name):
  logger = logging.getLogger(name)
  logger.setLevel(LOG_LEVEL)
  handler = logging.StreamHandler()
  handler.setFormatter(logging.Formatter(LOG_FORMAT))
  logger.addHandler(handler)
  return logger

class ConsistentHash:
  def __init__(self, nodes, virtual_nodes=100):
    self.nodes = nodes
    self.virtual_nodes = virtual_nodes
    self.ring = {}
    self._build_ring()

  def _build_ring(self):
    for node in self.nodes:
      for i in range(self.virtual_nodes):
        key = self._hash(f"{node}:{i}")
        self.ring[key] = node

  def _hash(self, key):
    return hashlib.md5(key.encode()).hexdigest()

  def get_node(self, key):
    if not self.ring:
      return None
    hash_key = self._hash(key)
    for node_hash in sorted(self.ring.keys()):
      if node_hash >= hash_key:
        return self.ring[node_hash]
    return self.ring[sorted(self.ring.keys())[0]]

# Encryption
def encrypt_value(value):
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(json.dumps(value).encode()).decode()

def decrypt_value(encrypted_value):
    f = Fernet(ENCRYPTION_KEY)
    return json.loads(f.decrypt(encrypted_value.encode()))

# Authentication
def generate_auth_token(username):
  try:
    return jwt.encode({'username': username}, AUTH_SECRET_KEY, algorithm='HS256')
  except AttributeError:
    return jwt.encode({'username': username}, AUTH_SECRET_KEY, algorithm='HS256').decode('utf-8')

def verify_auth_token(token):
  try:
    jwt.decode(token, AUTH_SECRET_KEY, algorithms=['HS256'])
    return True
  except jwt.exceptions.InvalidTokenError:
    return False

# Data persistence
def save_to_disk(data, filename):
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  with open(filename, 'w') as f:
      json.dump(data, f)

def load_from_disk(filename):
  if os.path.exists(filename):
    with open(filename, 'r') as f:
      return json.load(f)
  return {}