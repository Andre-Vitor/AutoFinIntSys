from engine import get_market_answer

try:
    response = get_market_answer("What are the latest trends?")
    print("--- LCEL TEST SUCCESSFUL ---")
    print(f"Response: {response}")
except Exception as e:
    print("--- LCEL TEST FAILED ---")
    print(e)