import sqlite3
import evaluate

# Load the ROUGE metric
try:
    rouge = evaluate.load('rouge')
    print("ROUGE metric loaded successfully.")
except Exception as e:
    print(f"Error loading ROUGE metric: {e}")
    exit(1)

def fetch_data_from_db():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect("summaries.db")
        cursor = conn.cursor()
        print("Connected to database successfully.")
        
        # Fetch original contents and abstractive summaries
        cursor.execute("SELECT original_content, abstractive_summary FROM summaries")
        rows = cursor.fetchall()
        
        print(f"Fetched {len(rows)} rows from the database.")
        
        # Close the connection
        conn.close()
        print("Database connection closed.")
        
        # Separate references and candidates
        references = [[row[0]] for row in rows]  # Using original content as reference
        candidates = [row[1] for row in rows]    # Using abstractive summaries as candidates
        
        return rows, references, candidates
    except Exception as e:
        print(f"Error fetching data from database: {e}")
        exit(1)

def compute_rouge():
    try:
        rows, references, candidates = fetch_data_from_db()
        
        print("\n--- Checking Correspondence Between References and Candidates ---\n")
        for i, (row, ref, cand) in enumerate(zip(rows, references, candidates)):
            print(f"Row {i+1}:")
            print(f"Original Content: {row[0]}")
            print(f"Reference: {ref[0]}")
            print(f"Candidate: {cand}\n")
        
        print("Computing ROUGE score...")
        results = rouge.compute(predictions=candidates, references=references)
        print("ROUGE Score Computation Successful.")
        print(results)
    except Exception as e:
        print(f"Error computing ROUGE score: {e}")
        exit(1)

if __name__ == "__main__":
    print("Starting ROUGE evaluation script...")
    compute_rouge()
    print("Script execution completed.")
