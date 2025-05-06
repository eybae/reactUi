import os
import sys

import grpc
from chirpstack_api import api

# Configuration.

# This must point to the API interface.
server = "localhost:8080"

# The DevEUI for which you want to enqueue the downlink.
#dev_eui = "0101010101010101"

# The API token (retrieved using the web-interface).
api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjZmZWFkYzhjLThjMDYtNDM2MS1iMWUzLWMwYWQ0ODY4ZGNiNyIsInR5cCI6ImtleSJ9.GkWEp3WiRCidd5TkJe5ocmeKdK6vy_4_si2hbitgZ9g"

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
  req.queue_item.data = data         #bytes([0x01, 0x02, 0x03])
  req.queue_item.dev_eui = devId
  req.queue_item.f_port = 2

  try:
      resp = client.Enqueue(req, metadata=auth_token)
      print("✅ Enqueue 성공:", resp.id)
  except grpc.RpcError as e:
      print("❌ gRPC 오류:", e.code(), e.details())

  # Print the downlink id
  print(resp.id)
