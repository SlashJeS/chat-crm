import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APIClient

from apps.conversations.models import Conversation


def main():
    client = APIClient()
    results = []

    def check(name, cond, detail=""):
        results.append((name, cond, detail))
        status = "PASS" if cond else "FAIL"
        suffix = f" — {detail}" if detail else ""
        print(f"{status} {name}{suffix}")

    with override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"]):
        lead = client.post(
            "/api/auth/token/",
            {"username": "lead", "password": "password123"},
            format="json",
        )
        chatter1 = client.post(
            "/api/auth/token/",
            {"username": "chatter1", "password": "password123"},
            format="json",
        )
        chatter2 = client.post(
            "/api/auth/token/",
            {"username": "chatter2", "password": "password123"},
            format="json",
        )
        check("auth lead", lead.status_code == 200)
        check("auth chatter1", chatter1.status_code == 200)
        lead_token = lead.json()["access"]
        c1_token = chatter1.json()["access"]
        c2_token = chatter2.json()["access"]

        r = client.get("/api/lead/conversations/", HTTP_AUTHORIZATION=f"Bearer {lead_token}")
        check(
            "lead GET conversations",
            r.status_code == 200 and r.json().get("count", 0) >= 8,
            str(r.status_code),
        )
        all_convs = r.json()["results"]

        chatter1_user = User.objects.get(username="chatter1")
        r = client.get(
            f"/api/lead/conversations/?assigned_chatter_id={chatter1_user.id}",
            HTTP_AUTHORIZATION=f"Bearer {lead_token}",
        )
        check(
            "lead filter assigned_chatter_id",
            r.status_code == 200 and r.json()["count"] == 3,
            f"count={r.json().get('count')}",
        )

        r = client.get("/api/lead/chatters/workload/", HTTP_AUTHORIZATION=f"Bearer {lead_token}")
        check(
            "lead workload",
            r.status_code == 200 and len(r.json().get("results", [])) == 3,
            str(r.status_code),
        )

        r = client.get("/api/lead/conversations/", HTTP_AUTHORIZATION=f"Bearer {c1_token}")
        check("chatter 403 lead list", r.status_code == 403, str(r.status_code))

        conv = next(c for c in all_convs if c["assigned_chatter"]["username"] == "chatter1")
        conv_id = conv["id"]

        r = client.get("/api/conversations/", HTTP_AUTHORIZATION=f"Bearer {c1_token}")
        c1_before = {c["id"] for c in r.json()}
        check("chatter1 has conv before", conv_id in c1_before)

        chatter2_user = User.objects.get(username="chatter2")
        r = client.post(
            f"/api/lead/conversations/{conv_id}/assign/",
            {"chatter_id": chatter2_user.id},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {lead_token}",
        )
        check(
            "assign to chatter2",
            r.status_code == 200 and r.json()["assigned_chatter"]["username"] == "chatter2",
            r.content.decode()[:200],
        )

        c = Conversation.objects.get(pk=conv_id)
        check("db assigned_chatter", c.assigned_chatter_id == chatter2_user.id)

        r = client.get("/api/conversations/", HTTP_AUTHORIZATION=f"Bearer {c1_token}")
        c1_after = {c["id"] for c in r.json()}
        check("chatter1 lost conv", conv_id not in c1_after, f"ids={c1_after}")

        r = client.get("/api/conversations/", HTTP_AUTHORIZATION=f"Bearer {c2_token}")
        c2_after = {c["id"] for c in r.json()}
        check("chatter2 gained conv", conv_id in c2_after)

        r = client.post(
            f"/api/lead/conversations/{conv_id}/assign/",
            {"chatter_id": User.objects.get(username="lead").id},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {lead_token}",
        )
        check("invalid chatter_id 400", r.status_code == 400, str(r.status_code))

        r = client.get(
            f"/api/lead/conversations/{conv_id}/",
            HTTP_AUTHORIZATION=f"Bearer {lead_token}",
        )
        check("lead detail", r.status_code == 200 and r.json()["id"] == conv_id)

    passed = sum(1 for _, cond, _ in results if cond)
    print("---")
    print(f"{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
