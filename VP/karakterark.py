import tkinter as tk
from tkinter import filedialog
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def load_json_file(file_path=None):
    """Helper function to load a JSON file."""
    if file_path is None:
        # This is for when the user selects a file interactively
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window
        initial_dir = os.getcwd()
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")],initialdir=initial_dir)

    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def create_pdf(character_data, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # Set up the page size and margins
    width, height = A4
    c.setFont("Helvetica", 12)
    c.setTitle("Karakterark")
    
    # Set the starting y-coordinate for the header (closer to the top)
    header_y = height - 40  # Adjust this as needed

    # Header - Add fields for Navn, Karakter, Hold, Brugt EP, Resterende EP
    c.drawString(50, header_y, "Navn: ________________")
    c.drawString(230, header_y, "Karakter: ________________")
    c.drawString(410, header_y, "Hold: ________________")

    # Move down for the next line of the header
    header_y -= 20

    # Calculating Brugt EP and Resterende EP
    spent_ep = character_data.get('spent_ep', 0)
    total_ep = character_data.get('total_ep', 0)
    remaining_ep = total_ep - spent_ep

    # Add calculated EP fields
    c.drawString(50, header_y, f"Brugt EP: {spent_ep}")
    c.drawString(250, header_y, f"Resterende EP: {remaining_ep}")

    return c

def get_ability_name(ability_id, standard_abilities, class_files=None):
    # First, look in standard abilities
    for ability in standard_abilities:
        if ability['id'] == ability_id:
            return ability['name']

    # If not found, optionally look in class files if provided
    if class_files:
        for class_file in class_files:
            class_abilities = load_json_file(class_file)
            for ability in class_abilities:
                if ability['id'] == ability_id:
                    return ability['name']
    
    # Return the ID as fallback if name not found
    return "None"


def process_general_abilities(character_data, standard_abilities):
    left_column_abilities = {}

    # Iterate through character abilities and group by base ability ID (before the last '_')
    for ability_id in character_data['abilities']:
        # Split the ID into the base ID and the last part (which might be an integer)
        parts = ability_id.rsplit('_', 1)
        
        # Check if the last part of the ID is a digit (to identify leveled abilities)
        if len(parts) == 2 and parts[1].isdigit() and "wizard_ekstra_mana" not in ability_id:
            base_id = parts[0]
            current_level = int(parts[1])
            
            # Keep track of the highest level for this base ability
            if base_id in left_column_abilities:
                left_column_abilities[base_id] = max(left_column_abilities[base_id], current_level)
            else:
                left_column_abilities[base_id] = current_level
        else:
            # Non-leveled abilities (without an integer suffix)
            left_column_abilities[ability_id] = None  # No level, but we still want to track it

    # Retrieve the names for the abilities using only standard_abilities
    named_abilities = {}
    for base_id, level in left_column_abilities.items():
        if level is not None:
            # For leveled abilities, reconstruct the full ability ID with the highest level
            ability_id = f"{base_id}_{level}"
        else:
            # For non-leveled abilities, the ID remains the same
            ability_id = base_id

        # Fetch the ability name using the ID
        ability_name = get_ability_name(ability_id, standard_abilities)
        if ability_name != "None":
            named_abilities[ability_name] = level
    return named_abilities


def process_class_abilities(character_data, class_files, standard_abilities, calculate_stat_fn):
    right_column_data = {}

    for class_file in class_files:
        class_name = class_file.split('/')[-1].split('.')[0].capitalize()
        class_abilities = load_json_file(class_file)

        # Track the highest "Grad" ability
        grad_abilities = {}

        # Find all abilities of this class by matching IDs
        class_abilities_in_character = []
        for ability_id in character_data['abilities']:
            # Check if the ability ID is in the class abilities
            if ability_id in [ca['id'] for ca in class_abilities]:
                # Fetch the name using the ID
                ability_name = get_ability_name(ability_id, standard_abilities, class_files)

                # Handle "Grad " logic here (for abilities with levels)
                if "Grad " in ability_name and " Grad" in ability_name:
                    base_name = ability_name.rsplit(" Grad ", 1)[0]
                    grad_level = int(ability_name.rsplit(" Grad ", 1)[1])
                    if base_name not in grad_abilities or grad_level > grad_abilities[base_name]:
                        grad_abilities[base_name] = grad_level
                elif "Grad " in ability_name:
                    base_name = ability_name.rsplit("Grad ", 1)[0]
                    grad_level = int(ability_name.rsplit("Grad ", 1)[1])
                    if base_name not in grad_abilities or grad_level > grad_abilities[base_name]:
                        grad_abilities[base_name] = grad_level
                else:
                    class_abilities_in_character.append(ability_name)

        # Add the highest "Grad" abilities to the class abilities
        grad_ability_list = [f"{base_name} Grad {grad_level}" for base_name, grad_level in grad_abilities.items()]

        # If any abilities were found, add them to the right column, with Grad abilities on top
        if class_abilities_in_character or grad_ability_list:
            right_column_data[class_name] = {
                "grad_abilities": grad_ability_list,
                "abilities": class_abilities_in_character,
                "stat": calculate_stat_fn(character_data, class_name, class_abilities_in_character)
            }

    return right_column_data


def calculate_stat_fn(character_data, class_name, abilities):
    if class_name == "Druide":
        ability_file = "Filer/druide.json"
        total_hjerteslag = 2  # Start with 2        
        # Load the druid abilities from Filer/druide.json
        ability_data = load_json_file(ability_file)
            
        # Iterate through character abilities
        for ability_id in character_data['abilities']:
                
            # Check for abilities with "druid_ability" in their ID
            if "druid_ability" in ability_id:
                # Get the last character of the ID, which should be a number between 2 and 6
                last_char = ability_id[-1]
                if last_char.isdigit() and 2 <= int(last_char) <= 6:
                    total_hjerteslag += int(last_char)
                
            # Check for abilities with "druid_spell" in their ID
            elif "druid_spell" in ability_id:
                # Find the corresponding ability in Filer/druide.json
                spell = next((a for a in ability_data if a['id'] == ability_id), None)
                if spell and 'grade' in spell:
                    total_hjerteslag += spell['grade']
        
        return "(Hjerteslag: " + str(total_hjerteslag)+")"
    elif class_name == "Trolddom":
        # Load the wizard abilities from Filer/trolddom.json
        ability_file = "Filer/trolddom.json"
        ability_data = load_json_file(ability_file)

        # Initialize total mana
        total_mana = 0

        # Loop through character abilities
        for ability_id in character_data['abilities']:
            # Check if the ability is a wizard spell
            if "wizard_spell" in ability_id:
                # Find the corresponding ability in Filer/trolddom.json to get its grade
                spell = next((a for a in ability_data if a['id'] == ability_id), None)
                if spell:
                    # Add mana based on the grade (3 mana per grade level)
                    total_mana += spell['grade'] * 3

            # Check if the ability is a wizard ekstra mana
            elif "wizard_ekstra_mana" in ability_id:
                # Add 6 mana for each ekstra mana ability
                total_mana += 6
        return "(Mana: " + str(total_mana)+")"
    elif class_name == "Præst":
        total_gudetro = 0  # Start with 0
        
        # Load the priest abilities from Filer/præst.json
        ability_file = "Filer/præst.json"
        ability_data = load_json_file(ability_file)
            
        # Iterate through character abilities
        for ability_id in character_data['abilities']:
                
            # Check for abilities with "priest_spell" in their ID
            if "priest_spell" in ability_id:
                # Find the corresponding ability in Filer/præst.json
                spell = next((a for a in ability_data if a['id'] == ability_id), None)
                if spell and 'grade' in spell:
                    total_gudetro += spell['grade'] * 3
        return "(Gudetro: " + str(total_gudetro)+")"
    elif class_name == "Paladin":
        total_tro = 0  # Start with 0
        
        # Load the paladin abilities from Filer/paladin.json
        ability_file = "Filer/paladin.json"
        ability_data = load_json_file(ability_file)
            
        # Iterate through character abilities
        for ability_id in character_data['abilities']:
                
            # Check for abilities with "paladin_spell" in their ID
            if "paladin_spell" in ability_id:
                # Find the corresponding ability in Filer/paladin.json
                spell = next((a for a in ability_data if a['id'] == ability_id), None)
                if spell and 'grade' in spell:
                    total_tro += spell['grade'] * 3
        return "(Tro: " + str(total_tro)+")"
    elif class_name == "Heks":
        total_skyggeskaar = 1  # Start with 1
        
        # Load the witch abilities from witch.json
        ability_file = "Filer/heks.json"
        ability_data = load_json_file(ability_file)
            
        # Iterate through character abilities
        for ability_id in character_data['abilities']:
                
            # Check for abilities with "witch_ability" in their ID
            if "witch_ability" in ability_id:
                # Get the last character of the ID, which should be a number
                last_char = ability_id[-1]
                if last_char.isdigit():
                    total_skyggeskaar += int(last_char)
                
            # Check for abilities with "witch_spell" in their ID
            elif "witch_spell" in ability_id:
                # Find the corresponding ability in witch.json
                spell = next((a for a in ability_data if a['id'] == ability_id), None)
                if spell and 'grade' in spell:
                    total_skyggeskaar += spell['grade']
        return "(Skyggeskår: " + str(total_skyggeskaar)+")"
    # Add other classes here
    return ""

def add_abilities_to_pdf(c, general_abilities, class_abilities, starting_height):
    current_y = starting_height
    page_bottom_margin = 50
    row_height = 20

    # Left column: General abilities
    c.drawString(50, current_y, "Generelle Evner:")
    current_y -= row_height

    for ability_name, level in general_abilities.items():
        # Check if there's enough space, if not, start a new page
        if current_y <= page_bottom_margin:
            c.showPage()
            current_y = starting_height
            #c.drawString(50, current_y, "Generelle Evner (fortsat):")
            current_y -= row_height

        if level:  # Only print levels if they exist
            #ability_text = f"{ability_name} niveau {level}"
            ability_text = f"{ability_name}"
        else:
            ability_text = ability_name
        
        # Draw the ability text
        c.drawString(50, current_y, ability_text)

        # Draw border (rect) around the text
        c.rect(45, current_y - 5, 200, row_height)

        current_y -= row_height

    # Right column: Class abilities
    current_y = starting_height
    c.drawString(300, current_y, "Klasseevner:")
    current_y -= row_height

    for class_name, data in class_abilities.items():
        # Check if there's enough space for the class section
        if current_y <= page_bottom_margin:
            c.showPage()
            current_y = starting_height
            #c.drawString(300, current_y, "Klasse Evner (fortsat):")
            current_y -= row_height

        # Print class name with its stat
        c.setFont("Helvetica-Bold", 12)
        c.drawString(300, current_y, f"{class_name} {data['stat']}")
        c.setFont("Helvetica", 12)
        c.rect(295, current_y - 5, 200, row_height)
        current_y -= row_height

        # Print Grad abilities first
        for grad_ability in data.get("grad_abilities", []):
            if current_y <= page_bottom_margin:
                c.showPage()
                current_y = starting_height
                #c.drawString(300, current_y, "Klasse Evner (fortsat):")
                current_y -= row_height

            c.drawString(300, current_y, grad_ability)
            c.rect(295, current_y - 5, 200, row_height)
            current_y -= row_height

        # Print regular class abilities
        for ability_name in data['abilities']:
            if current_y <= page_bottom_margin:
                c.showPage()
                current_y = starting_height
                #c.drawString(300, current_y, "Klasse Evner (fortsat):")
                current_y -= row_height

            c.drawString(300, current_y, ability_name)
            c.rect(295, current_y - 5, 200, row_height)
            current_y -= row_height

        # Add a blank line between classes for spacing
        current_y -= row_height


def main():
    # Load the character JSON interactively
    character_data = load_json_file()

    # Load standard abilities from the specific JSON file
    standard_abilities = load_json_file("Filer/standardevner.json")

    # Class-specific files (just an example)
    class_files = [
        "Filer/alkymi.json", "Filer/druide.json", "Filer/heks.json", "Filer/kriger.json",
        "Filer/paladin.json", "Filer/præst.json", "Filer/runesmed.json", "Filer/shaman.json", "Filer/trolddom.json"
    ]
    
    # Process general abilities (only from standardevner.json)
    general_abilities = process_general_abilities(character_data, standard_abilities)

    # Class-specific abilities (loaded separately)
    class_abilities = process_class_abilities(character_data, class_files, standard_abilities, calculate_stat_fn)

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask the user where they want to save the PDF file
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Save PDF As")

    if not file_path:  # If the user cancels, return without doing anything
        return

    # Create PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    
    # Add header info and calculated EP
    c = create_pdf(character_data, file_path)
    
    # Add the abilities to the PDF
    add_abilities_to_pdf(c, general_abilities, class_abilities, 750)

    c.save()

if __name__ == "__main__":
    main()
