import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import UserInvite


def main():
    client = APIClient()
    results = []

    def check(name, cond, detail=""):
        results.append((name, cond, detail))
        status = "PASS" if cond else "FAIL"
        suffix = f" — {detail}" if detail else ""
        print(f"{status} {name}{suffix}")

    with override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"]):
        admin_auth = client.post(
            "/api/auth/token/",
            {"username": "admin", "password": "password123"},
            format="json",
        )
        lead_auth = client.post(
            "/api/auth/token/",
            {"username": "lead", "password": "password123"},
            format="json",
        )
        chatter_auth = client.post(
            "/api/auth/token/",
            {"username": "chatter1", "password": "password123"},
            format="json",
        )
        check("auth admin", admin_auth.status_code == 200)
        check("auth lead", lead_auth.status_code == 200)
        check("auth chatter1", chatter_auth.status_code == 200)

        admin_token = admin_auth.json()["access"]
        lead_token = lead_auth.json()["access"]
        c1_token = chatter_auth.json()["access"]

        r = client.get("/api/admin/users/", HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        check(
            "admin list users",
            r.status_code == 200 and r.json().get("count", 0) >= 5,
            str(r.status_code),
        )

        r = client.get("/api/admin/users/", HTTP_AUTHORIZATION=f"Bearer {lead_token}")
        check("lead 403 admin users", r.status_code == 403, str(r.status_code))

        r = client.get("/api/admin/users/", HTTP_AUTHORIZATION=f"Bearer {c1_token}")
        check("chatter 403 admin users", r.status_code == 403, str(r.status_code))

        r = client.post(
            "/api/admin/invites/",
            {"role": "CHATTER", "email": "newchatter@example.com", "expires_in_hours": 72},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )
        check("admin create CHATTER invite", r.status_code == 201, r.content.decode()[:200])
        chatter_invite = r.json()
        chatter_token = chatter_invite["token"]
        chatter_invite_id = chatter_invite["id"]

        check(
            "invite response has invite_url",
            "invite_url" in chatter_invite and str(chatter_token) in chatter_invite["invite_url"],
            chatter_invite.get("invite_url", ""),
        )
        check(
            "invite response has no password",
            "password" not in chatter_invite,
            str(list(chatter_invite.keys())),
        )

        r = client.get(f"/api/invites/{chatter_token}/")
        check(
            "public fetch invite",
            r.status_code == 200 and r.json().get("is_active_invite") is True,
            str(r.status_code),
        )

        accept_username = f"invited_chatter_{uuid.uuid4().hex[:8]}"
        chosen_password = f"UserChosen-{uuid.uuid4().hex[:12]}"
        r = client.post(
            f"/api/invites/{chatter_token}/accept/",
            {
                "username": accept_username,
                "password": chosen_password,
                "password_confirm": chosen_password,
                "display_name": "Invited Chatter",
                "email": "newchatter@example.com",
            },
            format="json",
        )
        check(
            "public accept invite",
            r.status_code == 201 and r.json().get("message") == "Invite accepted successfully",
            r.content.decode()[:200],
        )
        check(
            "accept response has no password",
            "password" not in r.json(),
            str(list(r.json().keys())),
        )

        login_r = client.post(
            "/api/auth/token/",
            {"username": accept_username, "password": chosen_password},
            format="json",
        )
        check("login with chosen password", login_r.status_code == 200, str(login_r.status_code))

        new_user = User.objects.get(username=accept_username)
        new_user_id = new_user.id

        r = client.post(
            f"/api/invites/{chatter_token}/accept/",
            {
                "username": f"dup_{accept_username}",
                "password": chosen_password,
                "password_confirm": chosen_password,
                "email": "newchatter@example.com",
            },
            format="json",
        )
        check("accepted invite cannot be reused", r.status_code == 400, str(r.status_code))

        r = client.get("/api/admin/users/", HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        user_ids = {u["id"] for u in r.json().get("results", [])}
        check("new user in admin list", new_user_id in user_ids, f"ids={user_ids}")

        r = client.post(
            f"/api/admin/users/{new_user_id}/deactivate/",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )
        check(
            "admin deactivate new user",
            r.status_code == 200 and r.json().get("is_active") is False,
            str(r.status_code),
        )

        admin_user = User.objects.get(username="admin")
        r = client.post(
            f"/api/admin/users/{admin_user.id}/deactivate/",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )
        check("admin cannot deactivate self", r.status_code == 400, str(r.status_code))

        r = client.post(
            "/api/admin/invites/",
            {"role": "TEAMLEAD", "expires_in_hours": 24},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {lead_token}",
        )
        check("lead cannot create invite", r.status_code == 403, str(r.status_code))

        r = client.post(
            "/api/admin/invites/",
            {"role": "TEAMLEAD", "expires_in_hours": 24},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {c1_token}",
        )
        check("chatter cannot create invite", r.status_code == 403, str(r.status_code))

        r = client.post(
            "/api/admin/invites/",
            {"role": "TEAMLEAD", "expires_in_hours": 24},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )
        check("admin create TEAMLEAD invite", r.status_code == 201, r.content.decode()[:200])

        r = client.post(
            "/api/admin/invites/",
            {"role": "ADMIN", "expires_in_hours": 24},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )
        check("admin cannot create ADMIN invite", r.status_code == 400, r.content.decode()[:200])

        invite = UserInvite.objects.get(pk=chatter_invite_id)
        check("invite marked accepted in db", invite.is_accepted, f"status={invite.status}")

    passed = sum(1 for _, cond, _ in results if cond)
    print("---")
    print(f"{passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
