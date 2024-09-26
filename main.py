import threading
import time
from node import Node
from client import KVStoreClient
from load_balancer import start_load_balancer
from config import NUM_NODES
from utils import setup_logger

logger = setup_logger(__name__)

def main():
  # Create nodes
  nodes = [Node(i, []) for i in range(NUM_NODES)]
  
  # Update nodes list for each node
  for node in nodes:
    node.nodes = nodes

  # Start nodes
  for node in nodes:
    threading.Thread(target=node.start).start()

  # Start load balancer
  threading.Thread(target=start_load_balancer).start()

  # Wait for nodes and load balancer to start
  time.sleep(5)

  # Create a client
  client = KVStoreClient("test_user")

  # Perform some operations
  logger.info("Setting key1 to value1")
  print(client.set("key1", "value1"))

  logger.info("Getting key1")
  print(client.get("key1"))

  logger.info("Deleting key1")
  print(client.delete("key1"))

  logger.info("Getting non-existent key")
  print(client.get("non_existent_key"))

if __name__ == "__main__":
  main()