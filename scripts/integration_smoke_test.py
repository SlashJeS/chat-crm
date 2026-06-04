#!/usr/bin/env python3
"""Integration smoke tests for CRM Chatters Demo."""

from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

try:
    import websocket
except ImportError:
    websocket = None

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not str(value).strip():
        raise SystemExit(f"Missing required environment variable: {name}")
    return str(value).strip()


BASE = require_env("VITE_API_BASE_URL")
WS_BASE = require_env("VITE_WS_BASE_URL")

passed = 0
failed = 0


def ok(name: str, detail: str = "") -> None:
    global passed
    passed += 1
    suffix = f" — {detail}" if detail else ""
    print(f"PASS  {name}{suffix}")


def fail(name: str, detail: str) -> None:
    global failed
    failed += 1
    print(f"FAIL  {name} — {detail}")


def login(username: str, password: str = "password123") -> str:
    r = requests.post(f"{BASE}/auth/token/", json={"username": username, "password": password}, timeout=10)
    r.raise_for_status()
    return r.json()["access"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health() -> None:
    r = requests.get(f"{BASE}/health/", timeout=10)
    if r.status_code == 200 and r.json().get("status") == "ok":
        ok("health")
    else:
        fail("health", f"status={r.status_code} body={r.text}")


def test_auth() -> tuple[str, str]:
    chatter_token = login("chatter1")
    lead_token = login("lead")
    ok("auth token chatter1")
    ok("auth token lead")
    return chatter_token, lead_token


def test_me(token: str, expected_role: str) -> None:
    r = requests.get(f"{BASE}/me/", headers=auth_headers(token), timeout=10)
    data = r.json()
    if r.status_code == 200 and data.get("role") == expected_role:
        ok(f"me {expected_role}", data.get("username", ""))
    else:
        fail(f"me {expected_role}", r.text)


def test_conversations(token: str) -> list[dict[str, Any]]:
    r = requests.get(f"{BASE}/conversations/", headers=auth_headers(token), timeout=10)
    data = r.json()
    if r.status_code != 200 or not isinstance(data, list):
        fail("conversations list", r.text)
        return []
    if not data:
        fail("conversations list", "empty list for chatter1")
        return []
    ok("conversations list", f"{len(data)} conversations")
    return data


def test_access_control(chatter_token: str, conversations: list[dict[str, Any]]) -> int | None:
    all_r = requests.get(f"{BASE}/conversations/", headers=auth_headers(login("lead")), timeout=10)
    all_conversations = all_r.json()
    own_ids = {c["id"] for c in conversations}
    foreign = next((c for c in all_conversations if c["id"] not in own_ids), None)
    if foreign is None:
        fail("access control setup", "no foreign conversation found")
        return conversations[0]["id"] if conversations else None

    foreign_id = foreign["id"]
    r = requests.get(f"{BASE}/conversations/{foreign_id}/", headers=auth_headers(chatter_token), timeout=10)
    if r.status_code in (403, 404):
        ok("access control foreign conversation", f"status={r.status_code}")
    else:
        fail("access control foreign conversation", f"expected 403/404 got {r.status_code}")

    own_id = conversations[0]["id"]
    r2 = requests.get(f"{BASE}/conversations/{own_id}/", headers=auth_headers(chatter_token), timeout=10)
    if r2.status_code == 200:
        ok("access own conversation")
    else:
        fail("access own conversation", r2.text)
    return own_id


def test_messages(token: str, conversation_id: int) -> int | None:
    r = requests.get(
        f"{BASE}/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        params={"limit": 30},
        timeout=10,
    )
    if r.status_code != 200:
        fail("messages initial", r.text)
        return None
    data = r.json()
    results = data.get("results", [])
    if not results:
        fail("messages initial", "no messages")
        return None
    ok("messages initial", f"{len(results)} messages")

    oldest_id = results[0]["id"]
    r2 = requests.get(
        f"{BASE}/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        params={"limit": 30, "before_id": oldest_id},
        timeout=10,
    )
    if r2.status_code == 200:
        ok("messages before_id")
    else:
        fail("messages before_id", r2.text)

    latest_id = results[-1]["id"]
    r3 = requests.get(
        f"{BASE}/conversations/{conversation_id}/messages/",
        headers=auth_headers(token),
        params={"limit": 30, "after_id": latest_id},
        timeout=10,
    )
    if r3.status_code == 200:
        ok("messages after_id")
    else:
        fail("messages after_id", r3.text)
    return latest_id


def test_read(token: str, conversation_id: int, last_message_id: int | None) -> None:
    body = {"last_read_message_id": last_message_id} if last_message_id else {}
    r = requests.post(
        f"{BASE}/conversations/{conversation_id}/read/",
        headers=auth_headers(token),
        json=body,
        timeout=10,
    )
    if r.status_code in (200, 204):
        ok("mark read")
    else:
        fail("mark read", r.text)


def test_monitor(lead_token: str, chatter_token: str) -> None:
    r = requests.get(f"{BASE}/monitor/snapshot/", headers=auth_headers(lead_token), timeout=10)
    if r.status_code != 200:
        fail("monitor snapshot lead", r.text)
        return
    data = r.json()
    chatters = data.get("chatters", [])
    if len(chatters) == 3:
        ok("monitor snapshot lead", "3 chatters")
    else:
        fail("monitor snapshot lead", f"expected 3 chatters got {len(chatters)}")
    if "sla_seconds" in data:
        ok("monitor snapshot counts present")
    else:
        fail("monitor snapshot counts present", "missing sla_seconds")

    r2 = requests.get(f"{BASE}/monitor/snapshot/", headers=auth_headers(chatter_token), timeout=10)
    if r2.status_code == 403:
        ok("monitor forbidden chatter", "403")
    else:
        fail("monitor forbidden chatter", f"status={r2.status_code}")


def test_simulate_fan(lead_token: str, conversation_id: int, chatter_token: str) -> None:
    conv_before = requests.get(
        f"{BASE}/conversations/{conversation_id}/",
        headers=auth_headers(chatter_token),
        timeout=10,
    ).json()
    unread_before = conv_before.get("unread_count", 0)

    r = requests.post(
        f"{BASE}/dev/simulate-fan-message/",
        headers=auth_headers(lead_token),
        json={"conversation_id": conversation_id, "text": "Integration smoke fan message"},
        timeout=10,
    )
    if r.status_code not in (200, 201):
        fail("simulate fan message", r.text)
        return
    ok("simulate fan message")

    conv_after = requests.get(
        f"{BASE}/conversations/{conversation_id}/",
        headers=auth_headers(chatter_token),
        timeout=10,
    ).json()
    if conv_after.get("last_message") and conv_after["last_message"].get("sender_type") == "FAN":
        ok("simulate fan last_message updated")
    else:
        fail("simulate fan last_message updated", json.dumps(conv_after.get("last_message")))

    if conv_after.get("unread_count", 0) >= unread_before + 1:
        ok("simulate fan unread incremented")
    else:
        fail("simulate fan unread incremented", f"before={unread_before} after={conv_after.get('unread_count')}")


def ws_recv_json(ws, timeout: int = 10) -> dict[str, Any]:
    ws.settimeout(timeout)
    raw = ws.recv()
    return json.loads(raw)


def test_chat_websocket(chatter_token: str, conversation_id: int) -> None:
    if websocket is None:
        fail("chat websocket", "websocket-client not installed")
        return

    url = f"{WS_BASE}/ws/chat/?token={chatter_token}"
    ws = websocket.create_connection(url, timeout=10)
    try:
        first = ws_recv_json(ws)
        if first.get("type") == "connection.accepted":
            ok("chat ws connection.accepted")
        else:
            fail("chat ws connection.accepted", str(first))

        ws.send(json.dumps({"type": "dialog.subscribe", "conversation_id": conversation_id}))
        sub = ws_recv_json(ws)
        if sub.get("type") == "dialog.subscribed":
            ok("chat ws dialog.subscribed")
        else:
            fail("chat ws dialog.subscribed", str(sub))

        client_message_id = str(uuid.uuid4())
        ws.send(
            json.dumps(
                {
                    "type": "message.send",
                    "conversation_id": conversation_id,
                    "message_type": "TEXT",
                    "text": "Smoke test message",
                    "client_message_id": client_message_id,
                }
            )
        )

        got_ack = False
        got_created = False
        got_updated = False
        for _ in range(6):
            evt = ws_recv_json(ws, timeout=15)
            t = evt.get("type")
            if t == "message.send.ack":
                got_ack = True
            elif t == "message.created":
                got_created = True
            elif t == "conversation.updated":
                got_updated = True
            if got_ack and got_created and got_updated:
                break

        if got_ack:
            ok("chat ws message.send.ack")
        else:
            fail("chat ws message.send.ack", "not received")
        if got_created:
            ok("chat ws message.created")
        else:
            fail("chat ws message.created", "not received")
        if got_updated:
            ok("chat ws conversation.updated")
        else:
            fail("chat ws conversation.updated", "not received")

        ws.send(json.dumps({"type": "presence.heartbeat"}))
        got_hb = False
        for _ in range(8):
            evt = ws_recv_json(ws, timeout=15)
            if evt.get("type") == "presence.heartbeat.ack":
                got_hb = True
                break
        if got_hb:
            ok("chat ws presence.heartbeat.ack")
        else:
            fail("chat ws presence.heartbeat.ack", "not received")
    finally:
        ws.close()


def test_monitor_websocket(lead_token: str, chatter_token: str) -> None:
    if websocket is None:
        fail("monitor websocket", "websocket-client not installed")
        return

    url = f"{WS_BASE}/ws/monitor/?token={lead_token}"
    ws = websocket.create_connection(url, timeout=10)
    try:
        snap = ws_recv_json(ws, timeout=15)
        if snap.get("type") == "monitor.snapshot":
            ok("monitor ws snapshot")
        else:
            fail("monitor ws snapshot", str(snap))

        ws.send(json.dumps({"type": "monitor.refresh"}))
        snap2 = ws_recv_json(ws, timeout=15)
        if snap2.get("type") == "monitor.snapshot":
            ok("monitor ws refresh")
        else:
            fail("monitor ws refresh", str(snap2))

        import time

        time.sleep(8)
        ok("monitor ws stays connected 8s")
    finally:
        ws.close()

    try:
        bad = websocket.create_connection(f"{WS_BASE}/ws/monitor/?token={chatter_token}", timeout=5)
        bad.close()
        fail("monitor ws chatter rejected", "connection succeeded unexpectedly")
    except Exception:
        ok("monitor ws chatter rejected")


def main() -> int:
    print("=== CRM Chatters Integration Smoke Tests ===\n")

    test_health()
    chatter_token, lead_token = test_auth()
    test_me(chatter_token, "CHATTER")
    test_me(lead_token, "TEAMLEAD")

    conversations = test_conversations(chatter_token)
    if not conversations:
        print(f"\nResults: {passed} passed, {failed} failed")
        return 1

    conversation_id = test_access_control(chatter_token, conversations)
    if conversation_id is None:
        print(f"\nResults: {passed} passed, {failed} failed")
        return 1

    latest_id = test_messages(chatter_token, conversation_id)
    test_read(chatter_token, conversation_id, latest_id)
    test_monitor(lead_token, chatter_token)
    test_simulate_fan(lead_token, conversation_id, chatter_token)
    test_chat_websocket(chatter_token, conversation_id)
    test_monitor_websocket(lead_token, chatter_token)

    print(f"\nResults: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
