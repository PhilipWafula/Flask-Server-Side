import pytest
from app.server.utils.phone import process_phone_number


@pytest.mark.parametrize(
    "phone, region, expected",
    [
        ("0712345678", None, "+254712345678"),
        ("+254787654321", None, "+254787654321"),
        ("0765432187", "KE", "+254765432187"),
    ],
)
def test_process_phone_number(
    test_client, initialize_database, phone, region, expected
):
    """
    GIVEN process_phone_number function
    WHEN called with a phone_number WITHOUT and WITH country code
    THEN check that default country code is added if required
    """
    assert process_phone_number(phone, region) == expected
