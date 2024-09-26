import socket
import threading
import json
import random
from utils import setup_logger, verify_auth_token
from config import HOST, LOAD_BALANCER_PORT, NUM_NODES, PORT_RANGE_START, SOCKET_TIMEOUT

logger = setup_logger(__name__)

class LoadBalancer:
  def __init__(self):
    self.nodes = [PORT_RANGE_START + i for i in range(NUM_NODES)]
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((HOST, LOAD_BALANCER_PORT))
    self.sock.listen(5)

  def start(self):
    logger.info(f"Load balancer starting on port {LOAD_BALANCER_PORT}")
    while True:
      client, addr = self.sock.accept()
      threading.Thread(target=self.handle_client, args=(client,)).start()

  def handle_client(self, client):
    try:
      data = client.recv(1024).decode('utf-8')
      command = json.loads(data)
      if not verify_auth_token(command.get('token')):
        response = {"error": "Invalid or missing auth token"}
      else:
        node = self.choose_node()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_sock:
          node_sock.settimeout(SOCKET_TIMEOUT)
          node_sock.connect((HOST, node))
          node_sock.sendall(data.encode('utf-8'))
          response = node_sock.recv(1024).decode('utf-8')
      client.sendall(response.encode('utf-8'))
    except Exception as e:
      logger.error(f"Error in load balancer: {str(e)}")
    finally:
      client.close()

  def choose_node(self):
    return random.choice(self.nodes)

def start_load_balancer():
  load_balancer = LoadBalancer()
  load_balancer.start()

if __name__ == "__main__":
  start_load_balancer()