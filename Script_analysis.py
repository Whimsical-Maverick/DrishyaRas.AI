import re
import json
import fitz  # PyMuPDF

def post_process_script(elements):
    """
    Cleans up a list of parsed script elements using a multi-pass approach.
    """
    
    # Pass 1: Combine consecutive elements of the same type (action, dialogue).
    if not elements:
        return []
        
    combined_pass = [elements[0]]
    for i in range(1, len(elements)):
        prev = combined_pass[-1]
        curr = elements[i]
        if curr['type'] in ('action', 'dialogue') and curr['type'] == prev['type']:
            prev['content'] += ' ' + curr['content']
        else:
            combined_pass.append(curr)

    # Pass 2: Merge split character names (e.g., CHARACTER: "MRS.", DIALOGUE: "SESTERO")
    merged_char_pass = []
    i = 0
    while i < len(combined_pass):
        current = combined_pass[i]
        if i + 1 < len(combined_pass):
            next_elem = combined_pass[i+1]
            # Heuristic: If a character is followed by a "dialogue" that is short, all-caps, and seems like a name.
            if current['type'] == 'character' and next_elem['type'] == 'dialogue' and next_elem['content'].isupper() and len(next_elem['content'].split()) < 3:
                current['content'] = f"{current['content'].strip()} {next_elem['content'].strip()}"
                i += 1 # Skip the next element as it's been merged
        merged_char_pass.append(current)
        i += 1
        
    # Pass 3: Split elements that were incorrectly identified as 'action'
    # e.g. "GREG I'm heading out!" -> CHARACTER: GREG, DIALOGUE: I'm heading out!
    final_pass = []
    char_dialogue_re = re.compile(r'^([A-Z][A-Z\s0-9\'’.-]+(?:\s*\((?:V\.O\.|O\.S\.)\))?)\s+([a-z\(].*|[A-Z].*)$')
    for element in merged_char_pass:
        if element['type'] == 'action':
            content = element['content']
            match = char_dialogue_re.match(content)
            # Add heuristics to avoid misinterpreting titles or scene headings
            if match and len(match.group(1).split()) < 4 and not content.startswith(('INT.', 'EXT.')) and page_num > 1:
                char_name = match.group(1).strip()
                dialogue = match.group(2).strip()
                final_pass.append({'type': 'character', 'content': char_name})
                if dialogue:
                    final_pass.append({'type': 'dialogue', 'content': dialogue})
                continue
        final_pass.append(element)
        
    return final_pass


def parse_screenplay_pdf(pdf_path):
    """
    Parses a screenplay PDF file page by page into a structured list.
    """
    global page_num # Make page_num accessible to post-processing
    structured_pages = []
    
    doc = fitz.open(pdf_path)

    scene_heading_re = re.compile(r'^\s*(INT\.|EXT\.)')
    transition_re = re.compile(r'([A-Z\s]+TO:|FADE (?:IN|OUT):)$')
    # Relaxed character regex, relies more on post-processing now.
    character_re = re.compile(r'^\s{15,}([A-Z][A-Z\s0-9\'’.-]+(?:\s*\((?:V\.O\.|O\.S\.)\))?)$')
    parenthetical_re = re.compile(r'^\s*\([^)]+\)$')

    for page_num, page in enumerate(doc, 1):
        script_text = page.get_text()
        lines = script_text.split('\n')
        page_elements = []

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.isdigit():
                continue
            
            # Skip header/footer artifacts
            if "THE DISASTER ARTIST" in stripped_line and page_num > 1:
                continue

            if scene_heading_re.match(line):
                page_elements.append({'type': 'scene_heading', 'content': stripped_line})
            elif transition_re.search(stripped_line):
                page_elements.append({'type': 'transition', 'content': stripped_line})
            elif character_re.match(line):
                page_elements.append({'type': 'character', 'content': stripped_line})
            elif parenthetical_re.match(line):
                page_elements.append({'type': 'parenthetical', 'content': stripped_line.strip('()')})
            else:
                if page_elements and page_elements[-1]['type'] in ['character', 'parenthetical']:
                    page_elements.append({'type': 'dialogue', 'content': stripped_line})
                else:
                    page_elements.append({'type': 'action', 'content': stripped_line})
        
        cleaned_elements = post_process_script(page_elements)
        if cleaned_elements:
            structured_pages.append({
                'page': page_num,
                'elements': cleaned_elements
            })

    doc.close()
    return structured_pages

if __name__ == "__main__":
    PDF_FILE_NAME = r'sample_tests\The_Disaster_Artist_Script.pdf'
    
    print("INSTRUCTIONS:")
    print("1. Please run 'pip install PyMuPDF' in your terminal if you haven't already.")
    print(f"2. Place '{PDF_FILE_NAME}' in the same directory as this Python script ('script_parser.py').")
    print("3. Run this script. It will read the PDF and create 'parsed_script.json'.\n")

    try:
        parsed_data = parse_screenplay_pdf(PDF_FILE_NAME)

        if not parsed_data:
            print("Could not parse the PDF. Please check the file name and instructions.")
        else:
            with open('parsed_script.json', 'w', encoding='utf-8') as f:
                # ensure_ascii=False will write the original characters (e.g., ’)
                # instead of Unicode escape sequences (e.g., \u2019).
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)

            print("✅ Successfully parsed the PDF script!")
            print(f"   Processed {len(parsed_data)} pages.")
            print("   'parsed_script.json' has been created with the page-by-page structured data.")
            
            if parsed_data:
                print("\n--- Sample Parsed Elements from Page 3 ---")
                # Find page 3 to show a more relevant example
                page_3_data = next((item for item in parsed_data if item["page"] == 3), None)
                if page_3_data:
                    # ensure_ascii=False also makes the console output more readable.
                    print(json.dumps(page_3_data, indent=2, ensure_ascii=False))
                else:
                    print("Could not find data for page 3.")


    except FileNotFoundError:
        print(f"❌ ERROR: '{PDF_FILE_NAME}' not found. Please follow the instructions.")
    except ImportError:
        print("❌ ERROR: PyMuPDF is not installed correctly. Please run 'pip install PyMuPDF'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

