import json
from pathlib import Path


CATALOG_PATH = Path("data/catalog_cleaned.json")
MIN_RECORDS = 377


REQUIRED_FIELDS = {
    "name": str,
    "description": str,
    "test_type": list,
    "url": str
}


def validate_schema(record: dict, index: int) -> list:
    errors = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in record:
            errors.append(f"Missing field '{field}'")
            continue

        value = record[field]

        if not isinstance(value, expected_type):
            errors.append(
                f"Field '{field}' has wrong type "
                f"(expected {expected_type.__name__}, got {type(value).__name__})"
            )
            continue

        if expected_type is str and not value.strip():
            errors.append(f"Field '{field}' is empty")

        if field == "test_type":
            if not value:
                errors.append("Field 'test_type' is empty")
            elif not all(isinstance(t, str) and t.strip() for t in value):
                errors.append("Field 'test_type' must contain non-empty strings")

    return errors


def main():
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog not found at {CATALOG_PATH}")

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    total_records = len(catalog)
    print(f"Loaded {total_records} records")

    if total_records < MIN_RECORDS:
        raise ValueError(
            f"Catalog has {total_records} records, "
            f"but minimum required is {MIN_RECORDS}"
        )

    all_errors = []

    for idx, record in enumerate(catalog):
        errors = validate_schema(record, idx)
        if errors:
            all_errors.append({
                "index": idx,
                "errors": errors
            })

    if all_errors:
        print(f"\nSchema validation failed for {len(all_errors)} records:\n")
        for err in all_errors[:10]:  
            print(f"Record {err['index']}:")
            for e in err["errors"]:
                print(f"  - {e}")
        print("\nFix the above errors before proceeding.")
        exit(1)

    print("\nSchema validation PASSED")
    print("Catalog is safe to index into Qdrant.")


if __name__ == "__main__":
    main()
