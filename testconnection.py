import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    clean_url = database_url.replace("postgresql+psycopg2://", "postgresql://")
    
    print(f"🔍 Testing connection to: {clean_url}")
    
    try:
        conn = psycopg2.connect(clean_url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_connection()

# Alternative: Test with different connection formats
def test_supabase_formats():
    """Test different Supabase connection string formats"""
    
    url1 = "postgresql://postgres:Soravang2702@db.xvlnwnapmrzmxupvbqon.supabase.co:5432/postgres"
    
    url2 = "postgresql://postgres:Soravang2702@db.xvlnwnapmrzmxupvbqon.supabase.co:5432/postgres?sslmode=require"
    
    url3 = "postgresql://postgres:Soravang2702@db.xvlnwnapmrzmxupvbqon.supabase.co:6543/postgres?pgbouncer=true"
    
    print("Try these connection string formats:")
    print(f"1. Direct: {url1}")
    print(f"2. With SSL: {url2}")
    print(f"3. Pooled: {url3}")
    
    print("\nMake sure to:")
    print("- Replace Soravang2702 with your actual database password")
    print("- Check if your Supabase project is active and not paused")
    print("- Verify your network can reach Supabase (try ping db.xvlnwnapmrzmxupvbqon.supabase.co)")