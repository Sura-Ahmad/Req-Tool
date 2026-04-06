def test_get_domains_jordan(client):
    response = client.get("/domains/?country=JO")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["country"] == "JO"

def test_get_domains_invalid_country(client):
    response = client.get("/domains/?country=XX")
    assert response.status_code == 404

def test_get_questions_valid_domain(client):
    domains = client.get("/domains/?country=JO").json()
    domain_id = domains[0]["id"]
    response = client.get(f"/domains/{domain_id}/questions")
    assert response.status_code == 200

def test_get_questions_invalid_domain(client):
    response = client.get("/domains/00000000-0000-0000-0000-000000000000/questions")
    assert response.status_code == 404