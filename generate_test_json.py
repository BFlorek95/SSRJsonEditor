#!/usr/bin/env python3
"""
Script to generate test JSON files of various sizes for testing the JSON editor.
"""

import json
import random
import string
import sys


def random_string(length=10):
    """Generate a random string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_nested_object(depth=0, max_depth=5, items_per_level=10):
    """Generate a nested JSON object."""
    if depth >= max_depth:
        # Return leaf values
        return random.choice([
            random_string(20),
            random.randint(0, 1000000),
            random.random() * 1000,
            True,
            False,
            None
        ])

    obj = {}
    for i in range(items_per_level):
        key = f"key_{depth}_{i}_{random_string(5)}"

        # Randomly choose structure
        choice = random.choice(['nested', 'array', 'value'])

        if choice == 'nested':
            obj[key] = generate_nested_object(depth + 1, max_depth, items_per_level)
        elif choice == 'array':
            array_size = random.randint(5, 20)
            obj[key] = [
                generate_nested_object(depth + 1, max_depth, max(2, items_per_level // 2))
                for _ in range(array_size)
            ]
        else:
            obj[key] = generate_nested_object(max_depth, max_depth, items_per_level)

    return obj


def generate_large_array(size=1000):
    """Generate a large array."""
    return [
        {
            "id": i,
            "name": random_string(20),
            "email": f"{random_string(10)}@example.com",
            "age": random.randint(18, 80),
            "active": random.choice([True, False]),
            "balance": round(random.random() * 10000, 2),
            "tags": [random_string(8) for _ in range(random.randint(3, 10))],
            "metadata": {
                "created": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "updated": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "notes": random_string(100)
            }
        }
        for i in range(size)
    ]


def generate_test_file(filename, target_size_mb, structure='mixed'):
    """Generate a test JSON file of approximately target size."""
    print(f"Generating {filename} (target: ~{target_size_mb} MB, structure: {structure})...")

    target_size_bytes = target_size_mb * 1024 * 1024
    data = {}

    if structure == 'nested':
        # Deep nested structure
        items_per_level = 20
        max_depth = 8
        section_count = 0

        while True:
            section_count += 1
            data[f"section_{section_count}"] = generate_nested_object(0, max_depth, items_per_level)

            # Check size
            test_json = json.dumps(data, indent=2)
            current_size = len(test_json.encode('utf-8'))

            if current_size >= target_size_bytes:
                break

            if section_count % 10 == 0:
                print(f"  Progress: {current_size / 1024 / 1024:.1f} MB / {target_size_mb} MB")

    elif structure == 'array':
        # Large flat array
        batch_size = 1000
        data = []

        while True:
            data.extend(generate_large_array(batch_size))

            # Check size
            test_json = json.dumps(data, indent=2)
            current_size = len(test_json.encode('utf-8'))

            if current_size >= target_size_bytes:
                break

            if len(data) % 10000 == 0:
                print(f"  Progress: {current_size / 1024 / 1024:.1f} MB / {target_size_mb} MB ({len(data)} items)")

    else:  # mixed
        # Mix of structures
        data = {
            "users": generate_large_array(5000),
            "config": generate_nested_object(0, 6, 15),
            "logs": [],
            "metadata": {
                "version": "1.0",
                "generated": "2024-01-01",
                "description": "Test data for JSON editor"
            }
        }

        # Add log entries
        log_count = 0
        while True:
            data["logs"].append({
                "id": log_count,
                "timestamp": f"2024-01-01T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}",
                "level": random.choice(["INFO", "WARNING", "ERROR", "DEBUG"]),
                "message": random_string(100),
                "details": generate_nested_object(0, 3, 5)
            })
            log_count += 1

            if log_count % 1000 == 0:
                test_json = json.dumps(data, indent=2)
                current_size = len(test_json.encode('utf-8'))

                if current_size >= target_size_bytes:
                    break

                if log_count % 5000 == 0:
                    print(f"  Progress: {current_size / 1024 / 1024:.1f} MB / {target_size_mb} MB")

    # Write to file
    print(f"  Writing to file...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Report final size
    import os
    final_size = os.path.getsize(filename)
    print(f"  Complete! Final size: {final_size / 1024 / 1024:.2f} MB")
    print()


def main():
    print("JSON Test File Generator")
    print("========================\n")

    # Generate test files of various sizes
    test_files = [
        ("test_small.json", 1, "mixed"),          # 1 MB - quick test
        ("test_medium.json", 10, "nested"),       # 10 MB - medium nested
        ("test_large_array.json", 50, "array"),   # 50 MB - large array
        ("test_large_mixed.json", 100, "mixed"),  # 100 MB - mixed structure
    ]

    # Optional: Generate 2GB file if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--huge":
        test_files.append(("test_huge.json", 2048, "mixed"))  # 2 GB
        print("WARNING: Generating 2GB file. This will take several minutes...")
        print()

    for filename, size, structure in test_files:
        try:
            generate_test_file(filename, size, structure)
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print(f"Error generating {filename}: {e}\n")

    print("Generation complete!")
    print("\nTo generate a 2GB test file, run:")
    print("  python generate_test_json.py --huge")


if __name__ == '__main__':
    main()
