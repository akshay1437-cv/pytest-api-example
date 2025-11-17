from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_


# ---------------------------------------------------------------------------
# TEST 1 — Validate schema for GET /pets/1
# ---------------------------------------------------------------------------
def test_pet_schema():
    test_endpoint = "/pets/1"

    response = api_helpers.get_api_data(test_endpoint)

    # 1) Validate the response status code
    assert response.status_code == 200

    # 2) Validate the full response JSON against schemas.pet
    validate(instance=response.json(), schema=schemas.pet)

    # 3) Additional validation
    body = response.json()
    assert "id" in body
    assert "name" in body
    assert "status" in body
    assert isinstance(body["id"], int)
    assert_that(body["status"], is_(body["status"]))  # sanity check


# ---------------------------------------------------------------------------
# TEST 2 — Validate GET /pets/findByStatus including all available statuses
# ---------------------------------------------------------------------------

ALL_STATUSES = ["available", "pending", "sold"]

@pytest.mark.parametrize("status", ALL_STATUSES)
def test_find_by_status_200(status):
    test_endpoint = "/pets/findByStatus"
    params = {"status": status}

    response = api_helpers.get_api_data(test_endpoint, params)

    # 1) Validate the response code
    assert response.status_code == 200

    pets = response.json()

    # 2) Validate the 'status' property for each object
    for pet in pets:
        assert pet["status"] == status

        # 3) Validate the schema of each object
        validate(instance=pet, schema=schemas.pet)

        # 4) Validate required fields
        assert "id" in pet
        assert "name" in pet


# ---------------------------------------------------------------------------
# TEST 3 — Validate /pets/{pet_id} returns 404 for invalid ID
# ---------------------------------------------------------------------------
def test_get_by_id_404():
    invalid_pet_id = 999999999  # guaranteed to not exist
    test_endpoint = f"/pets/{invalid_pet_id}"

    response = api_helpers.get_api_data(test_endpoint)

    # 1) Validate the appropriate 404 response
    assert response.status_code == 404

    # 2) Validate the error message
    body = response.json()
    assert "message" in body
    assert_that(body["message"], contains_string("not found"))
