import socket
import threading
import json
import os
from utils import setup_logger, hash_key, encrypt_value, decrypt_value, verify_auth_token, save_to_disk, load_from_disk
from config import HOST, SOCKET_TIMEOUT, DATA_DIR
from raft import RaftNode
from prometheus_client import start_http_server, Counter, Gauge

logger = setup_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Number of requests processed', ['method'])
STORAGE_SIZE = Gauge('storage_size', 'Number of keys in storage')

class Node(RaftNode):
  def __init__(self, node_id, nodes):
    super().__init__(node_id, nodes)
    self.port = 5000 + node_id
    self.data = load_from_disk(os.path.join(DATA_DIR, f'node_{node_id}.json'))
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((HOST, self.port))
    self.sock.listen(5)
    self.logger = logger
    STORAGE_SIZE.set(len(self.data))

  def start(self):
    super().start()
    self.logger.info(f"Node starting on port {self.port}")
    start_http_server(8000 + self.node_id)  # Start Prometheus metrics server
    while True:
        client, addr = self.sock.accept()
        threading.Thread(target=self.handle_client, args=(client,)).start()

  def handle_client(self, client):
    client.settimeout(SOCKET_TIMEOUT)
    try:
      while True:
        data = client.recv(1024).decode('utf-8')
        if not data:
          break
        command = json.loads(data)
        if not verify_auth_token(command.get('token')):
          response = {"error": "Invalid or missing auth token"}
        elif command['action'] == 'get':
          response = self.get(command['key'])
          REQUEST_COUNT.labels(method='get').inc()
        elif command['action'] == 'set':
          response = self.set(command['key'], command['value'])
          REQUEST_COUNT.labels(method='set').inc()
        elif command['action'] == 'delete':
          response = self.delete(command['key'])
          REQUEST_COUNT.labels(method='delete').inc()
        else:
          response = {"error": "Invalid action"}
        client.send(json.dumps(response).encode('utf-8'))
    except socket.timeout:
      self.logger.warning(f"Client connection timed out")
    except json.JSONDecodeError:
      self.logger.error(f"Invalid JSON received")
    except Exception as e:
      self.logger.error(f"Error handling client: {str(e)}")
    finally:
      client.close()

  def get(self, key):
    hashed_key = hash_key(key)
    if hashed_key in self.data:
      return {"success": True, "value": decrypt_value(self.data[hashed_key])}
    else:
      return {"success": False, "error": "Key not found"}

  def set(self, key, value):
    if self.state != 'leader':
      return {"success": False, "error": "Not the leader"}
    hashed_key = hash_key(key)
    encrypted_value = encrypt_value(value)
    entry = {'term': self.current_term, 'key': hashed_key, 'value': encrypted_value}
    self.log.append(entry)
    self.data[hashed_key] = encrypted_value
    save_to_disk(self.data, os.path.join(DATA_DIR, f'node_{self.node_id}.json'))
    STORAGE_SIZE.set(len(self.data))
    return {"success": True}

  def delete(self, key):
    if self.state != 'leader':
      return {"success": False, "error": "Not the leader"}
    hashed_key = hash_key(key)
    if hashed_key in self.data:
      entry = {'term': self.current_term, 'key': hashed_key, 'value': None}
      self.log.append(entry)
      del self.data[hashed_key]
      save_to_disk(self.data, os.path.join(DATA_DIR, f'node_{self.node_id}.json'))
      STORAGE_SIZE.set(len(self.data))
      return {"success": True}
    else:
      return {"success": False, "error": "Key not found"}