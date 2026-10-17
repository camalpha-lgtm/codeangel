import argparse
import json
import os
import sys

import django

SETTINGS_MODULE = "{{package}}.settings"
SESSION_LIFETIME_SECONDS = 3600


class EvidenceSession:
    def __init__(self, username: str) -> None:
        self.username = username

    def user(self):
        from django.contrib.auth import get_user_model

        user, created = get_user_model().objects.get_or_create(
            username=self.username,
            defaults={"is_staff": True, "is_superuser": True},
        )
        if created:
            user.set_unusable_password()
            user.save()
        return user

    def issue(self) -> dict[str, str]:
        from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY
        from django.contrib.sessions.backends.db import SessionStore

        user = self.user()
        session = SessionStore()
        session[SESSION_KEY] = str(user.pk)
        session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.set_expiry(SESSION_LIFETIME_SECONDS)
        session.save()
        return {"username": user.get_username(), "sessionid": session.session_key}


class EvidenceCommand:
    def __init__(self, argv: list[str]) -> None:
        parser = argparse.ArgumentParser(prog="python -m core.seed_evidence")
        parser.add_argument("--username", default="evidence")
        self.arguments = parser.parse_args(argv)

    def run(self) -> int:
        from django.conf import settings

        if not settings.DEBUG:
            sys.stderr.write("refusing to create an evidence session while DEBUG is off\n")
            return 1
        sys.stdout.write(json.dumps(EvidenceSession(self.arguments.username).issue()) + "\n")
        return 0


def main(argv: list[str] | None = None) -> int:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()
    return EvidenceCommand(sys.argv[1:] if argv is None else argv).run()


if __name__ == "__main__":
    sys.exit(main())
