import os
from dotenv import load_dotenv

load_dotenv()


def test_env_vars():
    """Test if all environment variables are set"""
    required_vars = [
        "GROQ_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
    ]

    print("🔍 Checking environment variables...\n")

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set or using placeholder")
            all_set = False

    if all_set:
        print("\n🎉 All environment variables configured!")
    else:
        print("\n⚠️  Some variables missing. Check your .env file")


if __name__ == "__main__":
    test_env_vars()
