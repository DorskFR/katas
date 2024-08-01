import json

from httpx import AsyncClient


async def test_create_planet(client: AsyncClient) -> None:
    planet_data = {
        "name": "Mars",
        "mass": 6.39e23,
        "volume": 1.6318e11,
        "temperature": 210,
        "composition": json.dumps(["iron", "nickel", "sulfur"]),
        "aphelion": 249200000,
        "perihelion": 206700000,
        "orbital_speed": 24.007,
        "satellite_count": 2,
    }

    response = await client.post("/planets/", json=planet_data)
    assert response.status_code == 201
    created_planet = response.json()
    assert created_planet["name"] == "Mars"


async def test_get_planet(client: AsyncClient) -> None:
    # First, create a planet
    planet_data = {
        "name": "Venus",
        "mass": 4.867e24,
        "volume": 9.2843e11,
        "temperature": 737,
        "composition": json.dumps(["carbon dioxide", "nitrogen"]),
        "aphelion": 108939000,
        "perihelion": 107477000,
        "orbital_speed": 35.02,
        "satellite_count": 0,
    }
    create_response = await client.post("/planets/", json=planet_data)
    created_planet = create_response.json()

    # Now, get the planet
    response = await client.get(f"/planets/{created_planet['id']}")
    assert response.status_code == 200
    retrieved_planet = response.json()
    assert retrieved_planet["name"] == "Venus"


async def test_update_planet(client: AsyncClient) -> None:
    # First, create a planet
    planet_data = {
        "name": "Jupiter",
        "mass": 1.898e27,
        "volume": 1.4313e15,
        "temperature": 165,
        "composition": json.dumps(["hydrogen", "helium"]),
        "aphelion": 816620000,
        "perihelion": 740520000,
        "orbital_speed": 13.07,
        "satellite_count": 79,
    }
    create_response = await client.post("/planets/", json=planet_data)
    created_planet = create_response.json()

    # Now, update the planet
    update_data = {"satellite_count": 80}
    response = await client.patch(f"/planets/{created_planet['id']}", json=update_data)
    assert response.status_code == 200
    updated_planet = response.json()
    assert updated_planet["satellite_count"] == 80


async def test_delete_planet(client: AsyncClient) -> None:
    # First, create a planet
    planet_data = {
        "name": "Saturn",
        "mass": 5.683e26,
        "volume": 8.2713e14,
        "temperature": 134,
        "composition": json.dumps(["hydrogen", "helium", "ice"]),
        "aphelion": 1514500000,
        "perihelion": 1352550000,
        "orbital_speed": 9.69,
        "satellite_count": 82,
    }
    create_response = await client.post("/planets/", json=planet_data)
    created_planet = create_response.json()

    # Now, delete the planet
    response = await client.delete(f"/planets/{created_planet['id']}")
    assert response.status_code == 200

    # Verify that the planet is deleted
    get_response = await client.get(f"/planets/{created_planet['id']}")
    assert get_response.status_code == 404


async def test_list_planets(client: AsyncClient) -> None:
    # Create multiple planets
    planets = [
        {
            "name": "Mercury",
            "mass": 3.3011e23,
            "volume": 6.083e10,
            "temperature": 440,
            "composition": json.dumps(["iron", "nickel"]),
            "aphelion": 69816900,
            "perihelion": 46001200,
            "orbital_speed": 47.36,
            "satellite_count": 0,
        },
        {
            "name": "Earth",
            "mass": 5.97237e24,
            "volume": 1.08321e12,
            "temperature": 288,
            "composition": json.dumps(["nitrogen", "oxygen"]),
            "aphelion": 152100000,
            "perihelion": 147095000,
            "orbital_speed": 29.78,
            "satellite_count": 1,
        },
    ]

    for planet in planets:
        await client.post("/planets/", json=planet)

    # Now, list all planets
    response = await client.get("/planets/")
    assert response.status_code == 200
    planet_list = response.json()
    assert len(planet_list) >= 2
    assert any(planet["name"] == "Mercury" for planet in planet_list)
    assert any(planet["name"] == "Earth" for planet in planet_list)
