import json

from django.contrib.auth import get_user_model
from django.test import Client

from core.base_test import BaseTest
from core.seed_evidence import EvidenceSession, main


class TestSeedEvidence(BaseTest):
    def logged_in_client(self, sessionid: str) -> Client:
        client = Client()
        client.cookies["sessionid"] = sessionid
        return client

    def test_session_cookie_authenticates_admin(self):
        issued = EvidenceSession("evidence").issue()

        with_cookie = self.logged_in_client(issued["sessionid"]).get("/admin/")
        without_cookie = Client().get("/admin/")

        assert issued["username"] == "evidence"
        assert with_cookie.status_code == 200
        assert without_cookie.status_code == 302
        assert without_cookie.url.startswith("/admin/login/")

    def test_second_run_reuses_the_user(self):
        first = EvidenceSession("evidence").issue()
        second = EvidenceSession("evidence").issue()

        assert get_user_model().objects.filter(username="evidence").count() == 1
        assert first["sessionid"] != second["sessionid"]
        assert self.logged_in_client(first["sessionid"]).get("/admin/").status_code == 200
        assert self.logged_in_client(second["sessionid"]).get("/admin/").status_code == 200

    def test_password_is_unusable_and_never_printed(self, capsys, settings):
        settings.DEBUG = True

        assert main([]) == 0

        printed = json.loads(capsys.readouterr().out)
        user = get_user_model().objects.get(username="evidence")
        assert set(printed) == {"username", "sessionid"}
        assert not user.has_usable_password()
        assert user.password not in json.dumps(printed)

    def test_refuses_when_debug_is_off(self, capsys, settings):
        settings.DEBUG = False

        assert main([]) == 1

        assert capsys.readouterr().out == ""
        assert not get_user_model().objects.filter(username="evidence").exists()
