import os
import sys

import grpc
from chirpstack_api import api

# Configuration.

# This must point to the API interface.
server = "localhost:8080"

# The API token (retrieved using the web-interface).
api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6Ijc5Y2RhYjljLTViNDQtNDNhNi04YjVkLTdjZjQ0NmNmNzQ2NCIsInR5cCI6ImtleSJ9.bK0X3K9jq58tAWC8CZ5b3Tgb36Hcr87Dl2koiQwDCkY"

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

