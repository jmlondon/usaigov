import httpx

# Update to include the explicit federal gateway pathing segment
BASE_URL = "https://api.doc.usai.gov/api/v1"
API_KEY = ""

print("Querying USAi.gov model directory...")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

try:
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/models", headers=headers)
        
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            print(f"\nSuccess! Found {len(models_data)} models:\n")
            print(f"{'PROVIDER':<15} | {'EXACT MODEL ID (Copy this!)'}")
            print("-" * 55)
            for m in models_data:
                provider = m.get("owned_by", "Unknown")
                model_id = m.get("id")
                print(f"{provider:<15} | {model_id}")
        else:
            print(f"Failed. Status Code: {response.status_code}")
            print(response.text)
except Exception as e:
    print(f"Error connecting: {e}")