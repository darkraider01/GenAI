import json
import re

def process_response(clean_json):
    try:
        # First attempt with strict=False to handle some control characters
        parsed = json.loads(clean_json, strict=False)
        return parsed, "strict=False"
    except json.JSONDecodeError:
        # If it still fails, it's likely literal newlines/tabs inside strings.
        # Use regex to find strings and escape literal newlines within them.
        def replace_newlines(match):
            return match.group(0).replace('\n', '\\n').replace('\r', '\\r')
        
        # Regex for JSON strings: " (anything but " or \", or escaped chars) "
        fixed_json = re.sub(r'"(.*?)"', replace_newlines, clean_json, flags=re.DOTALL)
        parsed = json.loads(fixed_json, strict=False)
        return parsed, "regex_fix"

def test_json_parsing():
    print("Running JSON Parsing Fix Tests...")
    
    # Test Case 1: Simple JSON (Already works)
    case1 = '{"title": "Valid JSON", "content": "No issues here."}'
    parsed1, method1 = process_response(case1)
    assert parsed1["title"] == "Valid JSON"
    print(f"Test Case 1 passed using: {method1}")

    # Test Case 2: Literal newlines in string (Current failure case)
    case2 = '{\n"title": "Literal Newline",\n"methodology": "Line 1\nLine 2"\n}'
    try:
        parsed2, method2 = process_response(case2)
        assert parsed2["methodology"] == "Line 1\nLine 2"
        print(f"Test Case 2 passed using: {method2}")
    except Exception as e:
        print(f"Test Case 2 FAILED: {e}")
        raise

    # Test Case 3: Mixed content with escaped and literal newlines
    case3 = '{"title": "Mixed", "content": "Escaped\\nNewline and Literal\nNewline"}'
    parsed3, method3 = process_response(case3)
    assert "Escaped\nNewline and Literal\nNewline" in parsed3["content"]
    print(f"Test Case 3 passed using: {method3}")

    # Test Case 4: Literal tabs and other control chars
    case4 = '{"title": "Tabs", "content": "Tab\there"}'
    parsed4, method4 = process_response(case4)
    # strict=False should handle literal tabs
    assert "Tab\there" in parsed4["content"]
    print(f"Test Case 4 passed using: {method4}")

    print("\nAll JSON parsing tests PASSED!")

if __name__ == "__main__":
    test_json_parsing()
