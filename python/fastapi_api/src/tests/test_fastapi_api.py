import asyncio

from httpx import AsyncClient


async def test_create_plant(client: AsyncClient) -> None:
    response = await client.post(
        "/plants",
        json={
            "name": "Oak",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Angiospermae",
            "plant_class": "Eudicots",
            "is_edible": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Oak"
    assert data["is_edible"] is False
    assert "id" in data


async def test_get_plant(client: AsyncClient) -> None:
    # Create a plant
    create_response = await client.post(
        "/plants",
        json={
            "name": "Maple",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Angiospermae",
            "plant_class": "Eudicots",
            "is_edible": True,
        },
    )
    created_plant = create_response.json()

    # Retrieve the plant
    response = await client.get(f"/plants/{created_plant['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maple"
    assert data["is_edible"] is True


async def test_update_plant(client: AsyncClient) -> None:
    # Create a plant
    create_response = await client.post(
        "/plants",
        json={
            "name": "Pine",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Pinophyta",
            "plant_class": "Pinopsida",
            "is_edible": False,
        },
    )
    created_plant = create_response.json()

    # Update the plant
    response = await client.patch("/plants", json={"id": created_plant["id"], "name": "Scotch Pine", "is_edible": True})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Scotch Pine"
    assert data["is_edible"] is True


async def test_delete_plant(client: AsyncClient) -> None:
    # Create a plant
    create_response = await client.post(
        "/plants",
        json={
            "name": "Fern",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Polypodiophyta",
            "plant_class": "Polypodiopsida",
            "is_edible": False,
        },
    )
    created_plant = create_response.json()

    # Delete the plant
    response = await client.delete(f"/plants/{created_plant['id']}")
    assert response.status_code == 200

    # Try to get the deleted plant
    get_response = await client.get(f"/plants/{created_plant['id']}")
    assert get_response.status_code == 404


async def test_list_plants(client: AsyncClient) -> None:
    # Create multiple plants
    plants = [
        {
            "name": "Birch",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Angiospermae",
            "plant_class": "Eudicots",
            "is_edible": False,
        },
        {
            "name": "Willow",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Angiospermae",
            "plant_class": "Eudicots",
            "is_edible": False,
        },
        {
            "name": "Cedar",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Pinophyta",
            "plant_class": "Pinopsida",
            "is_edible": False,
        },
    ]

    for plant in plants:
        await client.post("/plants", json=plant)

    # Get all plants
    response = await client.get("/plants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # We use >= because there might be plants from previous tests
    assert all(plant["name"] in [p["name"] for p in data] for plant in plants)


async def test_concurrent_plant_creation(client: AsyncClient) -> None:
    # Prepare data for multiple plants
    plants_to_create = [
        {
            "name": f"Flower{i}",
            "kingdom": "Plantae",
            "clade": "Tracheophytes",
            "division": "Angiospermae",
            "plant_class": "Eudicots",
            "is_edible": False,
        }
        for i in range(10)
    ]

    # Create plants concurrently
    async def create_plant(plant_data):
        response = await client.post("/plants", json=plant_data)
        assert response.status_code == 200
        return response.json()

    created_plants = await asyncio.gather(*[create_plant(plant) for plant in plants_to_create])

    # Verify all plants were created
    assert len(created_plants) == 10
    created_names = {plant["name"] for plant in created_plants}
    assert created_names == {f"Flower{i}" for i in range(10)}

    # Verify we can retrieve all created plants
    response = await client.get("/plants")
    assert response.status_code == 200
    all_plants = response.json()

    created_ids = {plant["id"] for plant in created_plants}
    retrieved_ids = {plant["id"] for plant in all_plants if plant["name"].startswith("Flower")}
    assert created_ids == retrieved_ids
