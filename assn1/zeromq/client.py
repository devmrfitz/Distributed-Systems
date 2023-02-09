import sys
import zmq

port = "5555"

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Collecting updates from weather server...")
socket.connect(f"tcp://localhost:{port}")

# Subscribe to zipcode, default is NYC, 10001
topicfilter = "1000"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

# Process 5 updates
total_value = 0
for update_nbr in range(5):
    string = socket.recv()
    topic, messagedata = string.split()
    total_value += int(messagedata)
    print(topic.decode(), messagedata.decode())

print("Average messagedata value for topic '%s' was %dF" %
      (topicfilter, total_value / 5))
