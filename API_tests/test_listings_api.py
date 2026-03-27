def test_manager_can_create_and_list_listings(client, auth_headers):
    manager_headers = auth_headers("api_listing_manager", "manager-pass-123", "manager")

    create_response = client.post(
        "/api/v1/listings",
        data={
            "title": "Studio Unit 11",
            "description": "Compact studio with balcony access.",
            "price_amount": "950.00",
            "status": "draft",
        },
        headers=manager_headers,
    )
    assert create_response.status_code == 200
    listing = create_response.json()
    assert listing["title"] == "Studio Unit 11"
    assert listing["status"] == "draft"

    list_response = client.get("/api/v1/listings", headers=manager_headers)
    assert list_response.status_code == 200
    listings = list_response.json()
    assert len(listings) == 1
    assert listings[0]["title"] == "Studio Unit 11"


def test_non_manager_cannot_create_listings(client, auth_headers):
    resident_headers = auth_headers("api_listing_resident", "resident-pass-123", "resident")

    create_response = client.post(
        "/api/v1/listings",
        data={
            "title": "Unauthorized Listing",
            "description": "Residents should not create listings.",
            "status": "draft",
        },
        headers=resident_headers,
    )

    assert create_response.status_code == 403
    assert create_response.json()["detail"] == "Only manager role can manage listings"
