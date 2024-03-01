import sys
import subprocess
import pkg_resources
import os
import logging
from transformers import pipeline
import pyperclip

# Check and install missing dependencies
required = {'transformers', 'pyperclip'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print("Installing missing dependencies...")
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

# Suppress parallelism in tokenizers to avoid the warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress certain warnings from transformers
logging.getLogger("transformers").setLevel(logging.ERROR)

def summarize_notes(notes, model_name="t5-small", max_length=150, min_length=40):
    summarizer = pipeline("summarization", model=model_name)
    summary = summarizer(notes, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def start_summarizing_notes(settings):
    continue_summarizing = True

    while continue_summarizing:
        date = input("Enter the date (YY/MM/DD):\n")

        print("Paste your notes here (Place '==' on a new line to end notes):")
        notes = ""
        while True:
            line = input()
            if line.strip() == "==":
                break
            notes += line + "\n"

        summary = summarize_notes(notes, max_length=settings["max_length"], min_length=settings["min_length"])
        formatted_summary = f"{date} - {summary}\n"

        print("\n--- Summary (copied to clipboard) ---\n")
        print(formatted_summary)
        print("--- End of Summary ---\n")

        # Copying summary to clipboard
        pyperclip.copy(formatted_summary)

        # Saving summary to a file if requested
        if settings["save_to_file"]:
            with open("summaries.txt", "a") as file:
                file.write(formatted_summary + "\n")

        # Check if the user wants to summarize another set of notes
        another = input("Do you want to summarize another set of notes? (y/n): ").lower()
        continue_summarizing = another.startswith('y')

def change_settings(settings):
    new_max_length = input(f"Enter new max summary length (current: {settings['max_length']}): ")
    settings["max_length"] = int(new_max_length) if new_max_length.isdigit() else settings["max_length"]

    new_min_length = input(f"Enter new min summary length (current: {settings['min_length']}): ")
    settings["min_length"] = int(new_min_length) if new_min_length.isdigit() else settings["min_length"]

    save_to_file = input("Do you want to save summaries to a file? (y/n): ").lower().startswith('y')
    settings["save_to_file"] = save_to_file

def main_menu():
    settings = {
        "max_length": 150,
        "min_length": 40,
        "save_to_file": True
    }

    while True:
        print("\n--- Summarizer Menu ---")
        print("1. Start Summarizing Notes")
        print("2. Change Settings")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            start_summarizing_notes(settings)
        elif choice == '2':
            change_settings(settings)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()
