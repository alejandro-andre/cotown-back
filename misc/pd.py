import requests

API_TOKEN = "7d387f1bde4410bc531fcdcdd8a0492caf30e1cd"
BASE_URL = "https://api.pipedrive.com/v1"


def get_leads(limit=10):
    url = f"{BASE_URL}/leads"
    params = {"api_token": API_TOKEN, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_person(person_id):
    url = f"{BASE_URL}/persons/{person_id}"
    params = {"api_token": API_TOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("data")


def find_person_by_email(email):
    url = f"{BASE_URL}/persons/search"
    params = {"api_token": API_TOKEN, "term": email, "fields": "email", "exact_match": "true"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    items = response.json().get("data", {}).get("items", [])
    return items[0]["item"] if items else None


def get_leads_by_person(person_id, limit=10):
    url = f"{BASE_URL}/leads"
    params = {"api_token": API_TOKEN, "person_id": person_id, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("data") or []


def print_lead(lead):
    person_id = (lead.get("person_id") or {}).get("value") if isinstance(lead.get("person_id"), dict) else lead.get("person_id")
    print(f"Lead ID: {lead['id']}")
    print(f"Título:  {lead['title']}")
    if person_id:
        person = get_person(person_id)
        if person:
            emails = [e["value"] for e in person.get("email", []) if e.get("value")]
            phones = [p["value"] for p in person.get("phone", []) if p.get("value")]
            print(f"Persona: {person.get('name')}")
            print(f"Email:   {', '.join(emails) or '-'}")
            print(f"Teléfono:{', '.join(phones) or '-'}")
    else:
        print("Persona: (sin persona asociada)")
    print("-" * 40)


if __name__ == "__main__":
    email = input("Email a buscar: ").strip()

    person = find_person_by_email(email)
    if not person:
        print("No se encontró ninguna persona con ese email.")
        exit()

    print(f"\nPersona encontrada: {person['name']} (ID: {person['id']})\n")

    leads = get_leads_by_person(person["id"])
    print(f"Leads encontrados: {len(leads)}\n")
    for lead in leads:
        print_lead(lead)
