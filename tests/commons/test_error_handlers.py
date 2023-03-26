from unittest.mock import MagicMock, patch

from main.controllers.item import ItemsOperations
from main.libs.log import ServiceLogger


def test_not_found_request_fail(client, users):
    response = client.get("/hello")
    assert response.status_code == 404


@patch.object(
    ItemsOperations, "get", MagicMock(side_effect=Exception("Something went wrong"))
)
def test_exception_handler_fail(client, users):
    # Set up a mock response object
    response = client.get("/items")
    ServiceLogger(__name__).info(message="response is: {}".format(response.json))
    assert response.status_code == 500
