import time
import random
import threading
from utils import setup_logger

logger = setup_logger(__name__)

class RaftNode:
  def __init__(self, node_id, nodes):
    self.node_id = node_id
    self.nodes = nodes
    self.current_term = 0
    self.voted_for = None
    self.log = []
    self.commit_index = -1
    self.last_applied = -1
    self.state = 'follower'
    self.leader_id = None
    self.votes_received = set()
    self.next_index = {node.node_id: 0 for node in nodes if node.node_id != self.node_id}
    self.match_index = {node.node_id: -1 for node in nodes if node.node_id != self.node_id}
    self.election_timer = None
    self.reset_election_timer()

  def reset_election_timer(self):
    if self.election_timer:
      self.election_timer.cancel()
    timeout = random.uniform(150, 300) / 1000  # Convert to seconds
    self.election_timer = threading.Timer(timeout, self.start_election)
    self.election_timer.start()

  def start_election(self):
    self.state = 'candidate'
    self.current_term += 1
    self.voted_for = self.node_id
    self.votes_received = {self.node_id}
    logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
    self.request_votes()

  def request_votes(self):
    for node in self.nodes:
      if node.node_id != self.node_id:
        threading.Thread(target=self.send_vote_request, args=(node,)).start()

  def send_vote_request(self, node):
    last_log_index = len(self.log) - 1
    last_log_term = self.log[last_log_index]['term'] if self.log else 0
    granted = node.receive_vote_request(self.current_term, self.node_id, last_log_index, last_log_term)
    if granted:
      self.votes_received.add(node.node_id)
      if len(self.votes_received) > len(self.nodes) // 2:
        self.become_leader()

  def receive_vote_request(self, term, candidate_id, last_log_index, last_log_term):
    if term > self.current_term:
      self.current_term = term
      self.state = 'follower'
      self.voted_for = None
    if (term == self.current_term and
      (self.voted_for is None or self.voted_for == candidate_id) and
      (last_log_index >= len(self.log) - 1) and
      (last_log_term >= self.log[-1]['term'] if self.log else 0)):
      self.voted_for = candidate_id
      self.reset_election_timer()
      return True
    return False

  def become_leader(self):
    self.state = 'leader'
    self.leader_id = self.node_id
    logger.info(f"Node {self.node_id} became leader for term {self.current_term}")
    self.send_heartbeat()

  def send_heartbeat(self):
    for node in self.nodes:
      if node.node_id != self.node_id:
        threading.Thread(target=self.send_append_entries, args=(node,)).start()
    if self.state == 'leader':
      threading.Timer(0.05, self.send_heartbeat).start()

  def send_append_entries(self, node):
    prev_log_index = self.next_index[node.node_id] - 1
    prev_log_term = self.log[prev_log_index]['term'] if prev_log_index >= 0 else 0
    entries = self.log[self.next_index[node.node_id]:]
    success = node.receive_append_entries(self.current_term, self.node_id, prev_log_index, prev_log_term, entries, self.commit_index)
    if success:
      self.next_index[node.node_id] = len(self.log)
      self.match_index[node.node_id] = len(self.log) - 1
    else:
      self.next_index[node.node_id] = max(0, self.next_index[node.node_id] - 1)

  def receive_append_entries(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
    if term > self.current_term:
      self.current_term = term
      self.state = 'follower'
      self.voted_for = None
    if term < self.current_term:
      return False
    if prev_log_index >= len(self.log) or (prev_log_index >= 0 and self.log[prev_log_index]['term'] != prev_log_term):
      return False
    self.log = self.log[:prev_log_index+1] + entries
    if leader_commit > self.commit_index:
      self.commit_index = min(leader_commit, len(self.log) - 1)
    self.reset_election_timer()
    return True

  def apply_log(self):
    while True:
      if self.commit_index > self.last_applied:
        self.last_applied += 1
        entry = self.log[self.last_applied]
        logger.info(f"Node {self.node_id} applying log entry: {entry}")
      time.sleep(0.1)

  def start(self):
      threading.Thread(target=self.apply_log, daemon=True).start()