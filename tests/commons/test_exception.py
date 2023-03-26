from unittest.mock import MagicMock, patch

from main.commons.exceptions import BaseError
from main.controllers.item import ItemsOperations


@patch.object(
    ItemsOperations,
    "get",
    MagicMock(
        side_effect=BaseError(
            status_code=999, error_code=888, error_message="Custom error message"
        )
    ),
)
def test_custom_exception_fail(client, users):
    response = client.get("/items")
    assert response.status_code == 999
