from rapidfuzz import process

# Test data from the test
titles = [
    "Hello World",
    "Authentication Helper",
    "Database Connection",
    "HTTP Request Handler",
    "File System Operations",
    "JSON Parser",
    "JSON Generator",
    "Hello World JS",
    "Data Validator",
    "Cache Manager",
    "Configuration Loader",
    "String Utilities",
]

# Test queries
queries = ["world", "hello", "json", "foo", "bar", "baz"]

for query in queries:
    print(f"\nQuery: '{query}'")
    matches = process.extract(query, titles, limit=len(titles), score_cutoff=0)
    for match in matches:
        title, score = match[0], match[1]
        print(f"  '{title}' -> {score}")
