import re
import json

INPUT_FILE = "data/catalog.json"
OUTPUT_FILE = "data/catalog_cleaned.json"

test_type_map = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

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
        count_types = 0
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
            if "test_type" in item and isinstance(item["test_type"], list):
                original_types = item["test_type"]
                item["test_type"] = [test_type_map.get(code,code) for code in original_types]
                if item["test_type"] != original_types:
                        count_types += 1

        with open(OUTPUT_FILE,"w", encoding="utf-8") as f:
            json.dump(data,f, indent=2)
        print(f"updated {count} items ")
    except FileNotFoundError:
        print(f"Input file '{INPUT_FILE}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file '{INPUT_FILE}'.")

if __name__ == "__main__":
    main()

