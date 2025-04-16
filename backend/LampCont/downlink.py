import os
import sys

import grpc
from chirpstack_api import api

# Configuration.

# This must point to the API interface.
server = "192.168.10.10:8080"

# The DevEUI for which you want to enqueue the downlink.
#dev_eui = "0101010101010101"

# The API token (retrieved using the web-interface).
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiY2ViYzAwMjMtYjIwMy00ZjA3LWIzOTQtYjZhMjc5MDJiNjg4IiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTYyOTI4Njc1OCwic3ViIjoiYXBpX2tleSJ9.-wmpBZRFZU9k1C0Lk18JLEQKNZoSvVveoP9BQqoZZWQ"

def sendData(devId, data):
  # Connect without using TLS.
  channel = grpc.insecure_channel(server)

  # Device-queue API client.
  client = api.DeviceServiceStub(channel)

  # Define the API key meta-data.
  auth_token = [("authorization", "Bearer %s" % api_token)]

  # Construct request.
  req = api.EnqueueDeviceQueueItemRequest()
  req.queue_item.confirmed = False
  req.queue_item.data = data           #bytes([0x01, 0x02, 0x03])
  req.queue_item.dev_eui = devId
  req.queue_item.f_port = 10

  resp = client.Enqueue(req, metadata=auth_token)

  # Print the downlink id
  print(resp.id)
