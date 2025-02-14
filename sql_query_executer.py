import requests
import sqlite3  # Change this for MySQL/PostgreSQL if needed

# API Endpoint
API_URL = "http://127.0.0.1:8000/generate_sql/?natural_query=List all students enrolled in the Computer Science department."

def fetch_sql_from_api(api_url):
    """Fetch SQL query from API response"""
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()  # Assuming API returns JSON
        return data.get("sql_query")  # Extract SQL query
    else:
        print(f"Error: Unable to fetch query, Status Code {response.status_code}")
        return None

def execute_sql_query(query):
    """Execute the SQL query on SQLite"""
    conn = sqlite3.connect("your_database")  # SQLite database
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch query results
        conn.commit()
        return results
    except Exception as e:
        return [f"SQL Execution Error: {e}"]
    finally:
        conn.close()

# Fetch SQL from API
sql_query = fetch_sql_from_api(API_URL)
print(sql_query)


if sql_query:
    # Remove newline characters from SQL query
    clean_query = " ".join(sql_query.split())

    # Execute SQL and print output
    output = execute_sql_query(clean_query)
    print("Query Output:", output)
else:
    print("No query received from API.")