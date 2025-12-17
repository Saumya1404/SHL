import re
import json

INPUT_FILE = "data/catalog.json"
OUTPUT_FILE = "data/catalog_cleaned.json"

def extract_minutes(text):
    if not isinstance(text, str):
        return None
    if "=" in text:
         return text.split('=',1)[1].strip()
    return text.split()

    


def main():
    try:
        with open(INPUT_FILE,"r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            if "assessment_length" in item:
                duration_text = item["assessment_length"]
                minutes = extract_minutes(duration_text)
                if minutes is not None:
                    item["assessment_duration"] = minutes
                    count += 1
                else:
                    item["assessment_duration"] = None
            else:
                item["assessment_duration"] = None
                item["assessment_length"] = None

        with open(OUTPUT_FILE,"w", encoding="utf-8") as f:
            json.dump(data,f, indent=2)
        print(f"updated {count} items ")
    except FileNotFoundError:
        print(f"Input file '{INPUT_FILE}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{INPUT_FILE}'.")

if __name__ == "__main__":
    main()

