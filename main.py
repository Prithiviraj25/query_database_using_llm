from fastapi import FastAPI
from llama_cpp import Llama
import re
import sqlparse
DATABASE_SCHEMA = """
Tables:
1. users
   - user_id (INT, PRIMARY KEY)
   - college_email (TEXT, UNIQUE, NOT NULL)
   - hashed_password (TEXT, NOT NULL)
   - role (TEXT, NOT NULL)  # Dean, HoD, Teacher, Student
   - phone_number (TEXT, UNIQUE, NULLABLE)
   - salary (FLOAT, NULLABLE)  # Only for Faculty
   - created_at (DATETIME, DEFAULT CURRENT_TIMESTAMP)

2. deans
   - user_id (INT, PRIMARY KEY, FOREIGN KEY → users.user_id)

3. hods
   - user_id (INT, PRIMARY KEY, FOREIGN KEY → users.user_id)
   - department (TEXT, NOT NULL)

4. teachers
   - user_id (INT, PRIMARY KEY, FOREIGN KEY → users.user_id)
   - subject (TEXT, NOT NULL)
   - department_id (INT, FOREIGN KEY → hods.user_id)

5. students
   - user_id (INT, PRIMARY KEY, FOREIGN KEY → users.user_id)
   - enrollment_number (TEXT, UNIQUE, NOT NULL)
   - course (TEXT, NOT NULL)
   - year (INT, NOT NULL)
   - department_id (INT, FOREIGN KEY → hods.user_id)
   - teacher_id (INT, FOREIGN KEY → teachers.user_id)

6. marks
   - id (INT, PRIMARY KEY)
   - student_id (INT, FOREIGN KEY → students.user_id)
   - subject (TEXT, NOT NULL)
   - marks_obtained (FLOAT, NOT NULL)
   - max_marks (FLOAT, NOT NULL)

7. attendance
   - id (INT, PRIMARY KEY)
   - student_id (INT, FOREIGN KEY → students.user_id)
   - date (DATE, NOT NULL)
   - status (TEXT, NOT NULL)  # Present/Absent

Relationships:
- users.role determines the type of user (Dean, HoD, Teacher, Student).
- deans.user_id is a foreign key referencing users.user_id.
- hods.user_id is a foreign key referencing users.user_id.
- teachers.user_id is a foreign key referencing users.user_id.
- teachers.department_id is a foreign key referencing hods.user_id.
- students.user_id is a foreign key referencing users.user_id.
- students.department_id is a foreign key referencing hods.user_id.
- students.teacher_id is a foreign key referencing teachers.user_id.
- marks.student_id is a foreign key referencing students.user_id.
- attendance.student_id is a foreign key referencing students.user_id.
"""
query="List all students enrolled in the Computer Science department."
# Initialize FastAPI app
app = FastAPI()

# Load your local Llama 3.2 Q5 GGUF model
llm = Llama(model_path="/Users/prithivi/Desktop/demo/my_models/llama-3.2-1b-q4_k_m.gguf", n_ctx=2048)

# Function to extract SQL query using regex
def extract_sql_query(text):
    sql_pattern = r"SELECT\b.*?;"  # Matches an SQL SELECT statement ending with ;
    match = re.search(sql_pattern, text, re.DOTALL)
    return match.group(0) if match else "No valid SQL query found."

@app.get("/generate_sql/")
def generate_sql(natural_query:str):
    # Prompt Llama to generate SQL query
    # prompt = f"Generate an SQL query for: {natural_query}."
    prompt = f"""
    Given the following database schema:
    {DATABASE_SCHEMA}

    Generate an SQL query to:
    {natural_query} 
    """
    response = llm(prompt, max_tokens=1000)

    # Extract response text and filter out only the SQL query
    generated_text = response["choices"][0]["text"].strip()
    sql_query = extract_sql_query(generated_text)
    sql_query=sqlparse.format(sql_query, reindent=True, keyword_case="upper")
    sql_query=sql_query.replace("\n", " ")

    return {"sql_query": sql_query}

# Run using: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

