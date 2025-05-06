#!/usr/bin/env python3

import os
import subprocess
import sys
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

def convert_code_to_pdf(code_file_path, output_dir):
    base_filename = os.path.splitext(os.path.basename(code_file_path))[0]
    pdf_filename = f"{base_filename}.pdf"
    output_pdf_path = os.path.join(output_dir, pdf_filename)
    original_filename = os.path.basename(code_file_path)

    print(f"---> Attempting to convert '{original_filename}' to '{pdf_filename}'")

    try:
        print(f"     Reading code from '{code_file_path}'...")
        try:
            with open(code_file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            print(f"     Read {len(code_content)} characters.")
        except UnicodeDecodeError:
            print(f"     Skipping '{original_filename}': Not a text file (UnicodeDecodeError).")
            return
        except Exception as e:
            print(f"     Skipping '{original_filename}': Error reading file: {e}")
            return

        if not code_content.strip():
            print(f"     Skipping '{original_filename}': File is empty or contains only whitespace.")
            return

        print(f"     Determining syntax highlighter for '{original_filename}'...")
        try:
            lexer = get_lexer_for_filename(code_file_path, stripall=True)
            print(f"     Found lexer by filename: {lexer.name}")
        except ClassNotFound:
            print(f"     Lexer not found by filename, trying to guess from content...")
            try:
                lexer = guess_lexer(code_content, stripall=True)
                print(f"     Guessed lexer from content: {lexer.name}")
            except ClassNotFound:
                print(f"     Could not determine a lexer for '{original_filename}'. Skipping.")
                return

        print(f"     Generating HTML with lexer '{lexer.name}'...")
        formatter = HtmlFormatter(
            style='default',
            full=True,
            linenos='inline',
            cssclass='codehilite',
            title=original_filename
        )
        highlighted_html = highlight(code_content, lexer, formatter)
        print(f"     HTML generated (length: {len(highlighted_html)}).")

        print(f"     Calling wkhtmltopdf to create '{output_pdf_path}'...")
        command = [
            'wkhtmltopdf',
            '--enable-local-file-access', 
            '-',
            output_pdf_path
        ]
        print(f"     Executing command: {' '.join(command)}")

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=highlighted_html.encode('utf-8'))

        if stdout:
            print(f"     wkhtmltopdf stdout:\n{stdout.decode('utf-8', errors='ignore')}")
        if stderr:
            decoded_stderr = stderr.decode('utf-8', errors='ignore')
            if "Done" in decoded_stderr or "Exit with code 0" in decoded_stderr or not decoded_stderr.strip() :
                 print(f"     wkhtmltopdf stderr (likely status messages):\n{decoded_stderr}")
            else:
                 print(f"     wkhtmltopdf ERROR output:\n{decoded_stderr}", file=sys.stderr)


        print(f"     wkhtmltopdf process finished with return code: {process.returncode}")

        if process.returncode == 0:
            if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                 print(f"     SUCCESS: PDF file created at '{output_pdf_path}'.")
            elif os.path.exists(output_pdf_path):
                 print(f"     WARNING: PDF created at '{output_pdf_path}' but it is empty. wkhtmltopdf might have had issues with the HTML content.", file=sys.stderr)
            else:
                 print(f"     WARNING: wkhtmltopdf exited successfully (code 0) but output PDF not found at '{output_pdf_path}'. Check permissions or path.", file=sys.stderr)
        else:
            print(f"     ERROR: wkhtmltopdf failed for '{original_filename}' with return code {process.returncode}. Check stderr above for details.", file=sys.stderr)

    except FileNotFoundError:
        print(f"     ERROR: Could not find file '{code_file_path}'. This shouldn't happen if listed by os.listdir.", file=sys.stderr)
    except Exception as e:
        print(f"     ERROR: An unexpected error occurred processing '{original_filename}': {type(e).__name__} - {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def main():
    print("--- Entering main() ---")
    sys.stdout.flush()

    try:
        current_dir = os.getcwd()
        output_dir = current_dir
        processed_files_count = 0
        script_name = os.path.basename(__file__)

        print(f"--- Code to PDF Converter (Universal) ---")
        print(f"Script name is: '{script_name}' (will be excluded from conversion)")
        print(f"Scanning for code files in directory: '{current_dir}'")

        print("\nItems found in directory:")
        try:
            all_items = os.listdir(current_dir)
        except OSError as e:
            print(f"Error listing directory '{current_dir}': {e}", file=sys.stderr)
            return

        if not all_items:
            print("(Directory is empty)")
        else:
            for item_name in all_items:
                print(f"- {item_name}")
        print("-" * 20)
        sys.stdout.flush()

        for filename in all_items:
            if filename == script_name:
                print(f"\nIgnoring script: '{filename}'")
                continue

            file_path = os.path.join(current_dir, filename)

            if os.path.isfile(file_path):
                convert_code_to_pdf(file_path, output_dir)
                processed_files_count +=1
            else:
                print(f"\nIgnoring directory or non-file: '{filename}'")
            sys.stdout.flush()

        print("-" * 20)
        if processed_files_count == 0:
             print("RESULT: No other files to process were found in this directory.")
        else:
            print(f"RESULT: Attempted to process {processed_files_count} file(s)")


    except Exception as e:
        print(f"\n!!! UNEXPECTED ERROR INSIDE main() !!!", file=sys.stderr)
        print(f"Error Type: {type(e).__name__}", file=sys.stderr)
        print(f"Error Details: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    finally:
        print("--- Exiting main() ---")
        sys.stdout.flush()

if __name__ == "__main__":
    print("Checking for wkhtmltopdf...")
    sys.stdout.flush()
    try:
        process_check = subprocess.run(['wkhtmltopdf', '--version'], check=True, capture_output=True, text=True)
        print(f"wkhtmltopdf found: {process_check.stdout.strip()}")
        sys.stdout.flush()
        main()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error during wkhtmltopdf check: {e}", file=sys.stderr)
        print("FATAL: 'wkhtmltopdf' command not found or failed to execute.", file=sys.stderr)
        print("Please ensure wkhtmltopdf is installed and in your system's PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n!!! UNEXPECTED ERROR BEFORE main() CALL !!!", file=sys.stderr)
        print(f"Error Type: {type(e).__name__}", file=sys.stderr)
        print(f"Error Details: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    print("--- Script execution finished ---")
