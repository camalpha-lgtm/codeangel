import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class BaseTest:
    def setup_method(self):
        self.client = APIClient()
