"""Quick Workato connectivity check — lists folders and recipes."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from generators.generate_workato import WorkatoClient, _load_env_var

api_token = os.environ.get("WORKATO_API_TOKEN") or _load_env_var("WORKATO_API_TOKEN")
email     = os.environ.get("WORKATO_EMAIL")     or _load_env_var("WORKATO_EMAIL")
base_url  = os.environ.get("WORKATO_BASE_URL")  or _load_env_var("WORKATO_BASE_URL") or ""

if not api_token:
    print("WORKATO_API_TOKEN not set"); sys.exit(1)

print(f"Token : {api_token[:12]}...")
print(f"Email : {email}")
print(f"Region: {base_url or 'US (default)'}")

client = WorkatoClient(api_token, email, base_url=base_url or None)
print(f"API base: {client.BASE_URL}\n")

try:
    folders = client.list_folders()
    print(f"Folders ({len(folders)} total):")
    for f in folders[:10]:
        print(f"  [{f.get('id')}] {f.get('name')}")

    recipes = client.list_recipes()
    print(f"\nRecipes ({len(recipes)} total — first 5):")
    for r in (recipes or [])[:5]:
        status = "RUNNING" if r.get("running") else "stopped"
        print(f"  [{r.get('id')}] {r.get('name')} — {status}")

    print("\nWorkato connectivity: OK")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
