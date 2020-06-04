from unittest import TestCase

from starlette.testclient import TestClient

from app.main import app


class ApiTestCase(TestCase):
    """
    Api tests
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health_check(self):
        """
        Ensure health_check endpoint works
        """
        response = self.client.get('/health_check')
        assert response.status_code == 200
        assert response.text == 'This is fine'
