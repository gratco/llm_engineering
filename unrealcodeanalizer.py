import os
import re
import openai
import clang.cindex as cl

# Set your OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Initialize Clang
cl.Config.set_library_file("/usr/lib/llvm-10/lib/libclang.so")  # Adjust for your system
cl.Index.create()

# Function to recursively find all Unreal C++ files
def get_cpp_files(directory, extensions=[".cpp", ".h"]):
    """Recursively find all C++ files in an Unreal Engine project."""
    cpp_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                cpp_files.append(os.path.join(root, file))
    return cpp_files

# Function to find divide-by-zero errors using regex
def find_divide_by_zero(code, filename):
    """Finds divide by zero errors using regex."""
    lines = code.split("\n")
    for i, line in enumerate(lines, start=1):
        if re.search(r'\b\/\s*0\b', line):
            print(f"⚠️ Divide by zero detected in {filename} at line {i}: {line.strip()}")

# Function to check for performance issues in Unreal Tick functions
def check_tick_performance(code, filename):
    """Detects expensive operations inside Unreal's Tick function."""
    if "void Tick(" in code:
        if "for (" in code or ".Num()" in code:
            print(f"⚠️ Potential performance issue in Tick function in {filename}. Consider optimizing loops.")

# Function to check for raw pointer misuse
def check_raw_pointers(code, filename):
    """Detects raw pointer usage that should be replaced with smart pointers."""
    if "AActor*" in code:
        print(f"⚠️ Raw pointer detected in {filename}. Consider using TWeakObjectPtr or TSharedPtr.")

# Function to extract a relevant Unreal function
def extract_function(code):
    """Extracts Unreal functions to analyze instead of truncating."""
    match = re.search(r"(void\s+\w+\s*\(.*?\)\s*\{[\s\S]+?\})", code)
    return match.group(0) if match else code[:1000]  # Use extracted function or fallback to truncation

# Function to analyze code using GPT-4
def ask_llm_about_code(code):
    """Sends Unreal C++ code to OpenAI GPT-4 for analysis."""
    function_code = extract_function(code)
    prompt = f"""Analyze the following Unreal Engine C++ function:

{function_code}

Does this code follow Unreal best practices? Suggest improvements."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Main function to analyze a full Unreal project
def analyze_unreal_project(directory):
    """Scans an Unreal Engine C++ project for issues."""
    print(f"🔍 Scanning Unreal Engine project: {directory}\n")
    cpp_files = get_cpp_files(directory)
    for file in cpp_files:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
            print(f"Analyzing {file}...")
            find_divide_by_zero(code, file)
            check_tick_performance(code, file)
            check_raw_pointers(code, file)
            print("GPT-4 Feedback:")
            print(ask_llm_about_code(code))
            print("\n---\n")

# Run the script
if __name__ == "__main__":
    analyze_unreal_project("/path/to/UnrealProject")  # Change this path to your Unreal project folder
