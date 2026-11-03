import json

import pytest

from app.api import events_crud


def test_create_event(test_app, monkeypatch):
    test_request_payload = {
        "title": "Mekong Jazz Night",
        "city": "Phnom Penh",
        "price_usd": 15.0,
        "seats_left": 320,
    }
    test_response_payload = {"id": 1, **test_request_payload}

    async def mock_post(payload):
        return 1

    monkeypatch.setattr(events_crud, "post", mock_post)

    response = test_app.post("/events/", content=json.dumps(test_request_payload),)

    assert response.status_code == 201
    assert response.json() == test_response_payload


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "Mekong Jazz Night"},
        {"title": "MJ", "city": "Phnom Penh", "price_usd": 15.0, "seats_left": 320},
        {"title": "Mekong Jazz Night", "city": "P", "price_usd": 15.0, "seats_left": 320},
        {"title": "Mekong Jazz Night", "city": "Phnom Penh", "price_usd": -1, "seats_left": 320},
        {"title": "Mekong Jazz Night", "city": "Phnom Penh", "price_usd": 15.0, "seats_left": -5},
    ],
)
def test_create_event_invalid_json(test_app, payload):
    response = test_app.post("/events/", content=json.dumps(payload))
    assert response.status_code == 422


def test_read_event(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "title": "Mekong Jazz Night",
        "city": "Phnom Penh",
        "price_usd": 15.0,
        "seats_left": 320,
    }

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.get("/events/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.get("/events/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.get("/events/0/")
    assert response.status_code == 422


def test_read_all_events(test_app, monkeypatch):
    test_data = [
        {"id": 1, "title": "Mekong Jazz Night", "city": "Phnom Penh", "price_usd": 15.0, "seats_left": 320},
        {"id": 2, "title": "Apsara Dance Gala", "city": "Siem Reap", "price_usd": 25.0, "seats_left": 0},
    ]

    async def mock_get_all():
        return test_data

    monkeypatch.setattr(events_crud, "get_all", mock_get_all)

    response = test_app.get("/events/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_update_event(test_app, monkeypatch):
    test_update_data = {
        "id": 1,
        "title": "Mekong Jazz Night (Late Show)",
        "city": "Phnom Penh",
        "price_usd": 18.0,
        "seats_left": 150,
    }

    async def mock_get(id):
        return True

    monkeypatch.setattr(events_crud, "get", mock_get)

    async def mock_put(id, payload):
        return 1

    monkeypatch.setattr(events_crud, "put", mock_put)

    response = test_app.put("/events/1/", content=json.dumps(test_update_data))
    assert response.status_code == 200
    assert response.json() == test_update_data


VALID_EVENT = {"title": "Mekong Jazz Night", "city": "Phnom Penh", "price_usd": 15.0, "seats_left": 320}


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"city": "Phnom Penh"}, 422],
        [999, VALID_EVENT, 404],
        [1, {**VALID_EVENT, "title": "MJ"}, 422],
        [1, {**VALID_EVENT, "city": "P"}, 422],
        [1, {**VALID_EVENT, "price_usd": -1}, 422],
        [1, {**VALID_EVENT, "seats_left": -1}, 422],
        [0, VALID_EVENT, 422],
    ],
)
def test_update_event_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.put(f"/events/{id}/", content=json.dumps(payload),)
    assert response.status_code == status_code


def test_remove_event(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "title": "Mekong Jazz Night",
        "city": "Phnom Penh",
        "price_usd": 15.0,
        "seats_left": 320,
    }

    async def mock_get(id):
        return test_data

    monkeypatch.setattr(events_crud, "get", mock_get)

    async def mock_delete(id):
        return id

    monkeypatch.setattr(events_crud, "delete", mock_delete)

    response = test_app.delete("/events/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_remove_event_incorrect_id(test_app, monkeypatch):
    async def mock_get(id):
        return None

    monkeypatch.setattr(events_crud, "get", mock_get)

    response = test_app.delete("/events/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

    response = test_app.delete("/events/0/")
    assert response.status_code == 422
