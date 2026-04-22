from config import SUPABASE_URL, SUPABASE_KEY, MISTRAL_API_KEY
from core.supabase_client import supabase

def test_env():
    print("🔐 Checking environment variables...\n")

    print("SUPABASE_URL:", "OK" if SUPABASE_URL else "MISSING")
    print("SUPABASE_KEY:", "OK" if SUPABASE_KEY else "MISSING")
    print("MISTRAL_API_KEY:", "OK" if MISTRAL_API_KEY else "MISSING")


def test_supabase_connection():
    print("\n🗄️ Testing Supabase connection...\n")

    try:
        # lightweight query (does not require tables yet)
        response = supabase.table("pdf_metadata").select("*").limit(1).execute()

        print("Supabase Query Status: SUCCESS")
        print("Response:", response)

    except Exception as e:
        print("Supabase Connection ERROR ❌")
        print("Reason:", str(e))


if __name__ == "__main__":
    print("\n🚀 RUNNING SYSTEM HEALTH CHECK\n")

    test_env()
    test_supabase_connection()

    print("\n✅ CHECK COMPLETE")