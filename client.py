import socket
import json
import time
from utils import setup_logger, generate_auth_token
from config import HOST, LOAD_BALANCER_PORT, MAX_RETRIES, BACKOFF_FACTOR, SOCKET_TIMEOUT

logger = setup_logger(__name__)

class KVStoreClient:
  def __init__(self, username):
    self.load_balancer_address = (HOST, LOAD_BALANCER_PORT)
    self.auth_token = generate_auth_token(username)
    self.logger = logger

  def send_request(self, action, key, value=None):
    request = {'action': action, 'key': key, 'token': self.auth_token}
    if value is not None:
      request['value'] = value

    for attempt in range(MAX_RETRIES):
      try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
          sock.settimeout(SOCKET_TIMEOUT)
          sock.connect(self.load_balancer_address)
          sock.sendall(json.dumps(request).encode('utf-8'))
          response = sock.recv(1024).decode('utf-8')
          return json.loads(response)
      except Exception as e:
        self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
        if attempt < MAX_RETRIES - 1:
          time.sleep(BACKOFF_FACTOR ** attempt)
        else:
          raise Exception("Max retries reached. Operation failed.")

  def get(self, key):
    return self.send_request('get', key)

  def set(self, key, value):
    return self.send_request('set', key, value)

  def delete(self, key):
    return self.send_request('delete', key)