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
    print(f"🚀 Enqueue 요청: {devId} → {[hex(b) for b in data]}")

    channel = grpc.insecure_channel(server)
    client = api.DeviceServiceStub(channel)
    auth_token = [("authorization", f"Bearer {api_token}")]

    req = api.EnqueueDeviceQueueItemRequest()
    req.queue_item.confirmed = False
    req.queue_item.data = data
    req.queue_item.dev_eui = devId
    req.queue_item.f_port = 2

    try:
        resp = client.Enqueue(req, metadata=auth_token)
        print(f"✅ Enqueue 성공: {devId} → ID: {resp.id}")
    except grpc.RpcError as e:
        print(f"❌ Enqueue 실패: {devId} → {e.code()} - {e.details()}")

