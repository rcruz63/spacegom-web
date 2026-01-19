import sys
import os

# Ensure we can import app
sys.path.append(os.getcwd())

from app.database import init_db, engine
from sqlalchemy import inspect

def check_and_fix():
    print("Checking database schema...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Existing tables: {tables}")
        
        if "trade_orders" in tables:
            print("TradeOrder table already exists.")
        else:
            print("TradeOrder table MISSING. Creating...")
            init_db()
            print("init_db() returned.")
            
            # Verify
            inspector = inspect(engine)
            if "trade_orders" in inspector.get_table_names():
                print("SUCCESS: TradeOrder table created.")
            else:
                print("FAILURE: TradeOrder table still missing.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_fix()
