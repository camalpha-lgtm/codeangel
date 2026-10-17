from core.base_test import BaseTest


class TestApiSchema(BaseTest):
    def test_openapi_schema_served(self):
        response = self.client.get("/api/schema/", {"format": "json"})

        assert response.status_code == 200
        assert response.json()["info"]["title"]
