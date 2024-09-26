# Distributed Key-Value Store

## Overview

This project implements a distributed key-value store using a Raft consensus algorithm. It's designed to demonstrate advanced concepts in distributed systems, including consensus, load balancing, data persistence, and security features.

## Features

- **Raft Consensus Algorithm**: Ensures consistency across distributed nodes.
- **Load Balancing**: Distributes client requests across multiple nodes.
- **Data Persistence**: Saves data to disk to prevent data loss on node restarts.
- **Authentication**: Uses JWT tokens for secure client authentication.
- **Encryption**: Encrypts stored values for enhanced security.
- **Monitoring**: Includes Prometheus metrics for system observability.

## Components

1. **Node**: Represents a single server in the distributed system.
2. **Raft Implementation**: Manages consensus among nodes.
3. **Load Balancer**: Distributes incoming requests across nodes.
4. **Client**: Provides an interface for interacting with the key-value store.

## Prerequisites

- Python 3.7+
- Required Python packages:
  - `jwt`
  - `cryptography`
  - `prometheus_client`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/ryndm/distributed-key-value-store.git
   cd distributed-key-value-store
   ```

2. Create Python Virtual Environment:

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required packages:

   ```
   pip install -r requirements.txt
   ```

## Configuration

Edit the `config.py` file to adjust settings such as:
- Number of nodes
- Port ranges
- Timeout values
- Authentication secret key
- Encryption key

## Running the System

1. Start the system:
   ```
   python3 main.py
   ```

   This will start multiple nodes, the load balancer, and run some sample operations.

2. To interact with the system programmatically, use the `KVStoreClient` class:

   ```python
   from client import KVStoreClient

   client = KVStoreClient("your_username")
   
   # Set a value
   client.set("key1", "value1")
   
   # Get a value
   value = client.get("key1")
   
   # Delete a value
   client.delete("key1")
   ```

## Monitoring

Prometheus metrics are exposed on port 8000 + node_id for each node. You can configure a Prometheus server to scrape these endpoints for monitoring.

## Security

- All client requests require a valid JWT token.
- Stored values are encrypted using AES-256.

## Limitations and Future Improvements

- The current implementation is for demonstration purposes and not production-ready.
- Future improvements could include:
  - More sophisticated load balancing algorithms
  - Sharding for improved scalability
  - Admin interface for system management
  - Comprehensive error handling and recovery mechanisms
  - Integration with external monitoring and alerting systems

## Contributing

I've not added many comments explaining my logic. I plan to do that soon to make contributing easier.

Contributions to improve the system are welcome. Please submit a pull request or open an issue to discuss proposed changes.