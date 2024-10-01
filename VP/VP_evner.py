import tkinter as tk
from tkinter import messagebox, filedialog
import json

class Character:
    def __init__(self):
        self.name = ""
        self.race = ""
        self.lp_max = 0
        self.abilities = []
        self.free_spells_granted_for_paladin = False
        self.free_spells_granted_for_priest = False
        self.free_spells_granted_for_warrior = False
        self.free_spells_granted_for_alchemist = False
        self.free_spells_granted_for_witch = False
        self.free_spells_granted_for_druid = False
        self.free_spells_granted_for_runesmith = False
        self.free_spells_granted_for_wizard = False
        self.spent_ep = 0
        self.total_ep = 1000  # Default starting EP
        self.selected_god = None  # Track the selected god

    def load_from_file(self, filename):
        """Load the character data from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.name = data.get('name', "")
                self.race = data.get('race', "")
                self.abilities = data.get('abilities', [])
                self.lp_max = data.get('lp_max', 0)
                self.spent_ep = data.get('spent_ep', 0)
                self.total_ep = data.get('total_ep', 1000)
                self.selected_god = data.get('selected_god', None)  # Load the selected god

                for abilities in self.abilities:
                    if "alkymi_" in abilities:
                        self.free_spells_granted_for_alchemist = True
                    if "druid_" in abilities:
                        self.free_spells_granted_for_druid = True
                    if "witch_" in abilities:
                        self.free_spells_granted_for_witch = True
                    if "warrior_" in abilities:
                        self.free_spells_granted_for_warrior = True
                    if "paladin_" in abilities:
                        self.free_spells_granted_for_paladin = True
                    if "priest_" in abilities:
                        self.free_spells_granted_for_priest = True
                    if "runesmith_" in abilities:
                        self.free_spells_granted_for_runesmith = True
                    if "shaman_" in abilities:
                        self.free_spells_granted_for_shaman = True
                    if "wizard_" in abilities:
                        self.free_spells_granted_for_wizard = True
                    
        except FileNotFoundError:
            print(f"File {filename} not found. Loading empty character.")
        except json.JSONDecodeError:
            print(f"Error parsing {filename}. Please check the file format.")

    def save_to_file(self, filename):
        """Save the character data to a JSON file."""
        data = {
            'name': self.name,
            'race': self.race,
            'abilities': self.abilities,
            'lp_max': self.lp_max,
            'spent_ep': self.spent_ep,
            'total_ep': self.total_ep,
            'selected_god': self.selected_god  # Save the selected god
        }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def remaining_ep(self):
        """Calculate the remaining EP."""
        return self.total_ep - self.spent_ep

    def select_god(self, god_id):
        """Select a god for the character, preventing multiple selections."""
        if self.selected_god is None:
            self.selected_god = god_id
        else:
            raise ValueError(f"God already selected: {self.selected_god}")


    def has_ability(self, ability_id):
        """Check if the character has a specific ability."""
        return ability_id in self.abilities

    def add_ability(self, ability_id, cost):
        """Add an ability to the character if they have enough EP."""
        if self.remaining_ep() >= cost:
            if ability_id not in self.abilities:
                self.abilities.append(ability_id)
                self.spent_ep += cost
            else:
                raise ValueError(f"Ability {ability_id} is already purchased.")
        else:
            raise ValueError(f"Not enough EP to purchase {ability_id}. Cost: {cost}, Remaining EP: {self.remaining_ep()}")

    def remove_ability(self, ability_id):
        """Remove an ability from the character and refund its cost."""
        if ability_id in self.abilities:
            self.abilities.remove(ability_id)
            # Normally you would need to track the cost of the ability to refund properly
            # This could be an enhancement: Add ability costs to the data structure
        else:
            raise ValueError(f"Ability {ability_id} not found.")

    def set_name(self, name):
        """Set the character's name."""
        self.name = name

    def set_race(self, race):
        """Set the character's race."""
        self.race = race

    def choose_god(self, god_id):
        """Choose a god for the character, allowing only one selection."""
        if self.selected_god is None:
            self.selected_god = god_id
        else:
            raise ValueError("A god has already been selected. You cannot choose more than one god.")

    def reset_god(self):
        """Reset the god selection (if you want to allow changing the god)."""
        self.selected_god = None

    def __repr__(self):
        return f"Character(name={self.name}, race={self.race}, abilities={self.abilities}, remaining_ep={self.remaining_ep()}, selected_god={self.selected_god})"

class AbilityManager:
    def __init__(self, char, root, ability_file, ep_label, app, new_menu_buttons=None):
        self.app = app
        self.character = char
        self.root = root
        self.ability_file = ability_file
        self.ability_data = self.load_abilities(ability_file)
        self.ability_buttons = {}
        self.new_menu_buttons = new_menu_buttons or {}  # Keep track of new menu buttons
        self.ep_label = ep_label

        # Track if the character has already selected a god
        self.selected_god = self.character.selected_god

        # Create a frame for ability buttons (left side)
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Create a scrollable canvas for abilities (left side)
        self.ability_canvas = tk.Canvas(self.left_frame)
        self.ability_scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.ability_canvas.yview)
        self.ability_scrollable_frame = tk.Frame(self.ability_canvas)

        self.ability_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.ability_canvas.configure(scrollregion=self.ability_canvas.bbox("all"))
        )

        self.ability_canvas.create_window((0, 0), window=self.ability_scrollable_frame, anchor="nw")
        self.ability_canvas.configure(yscrollcommand=self.ability_scrollbar.set)

        self.ability_canvas.pack(side="left", fill="both", expand=True)
        self.ability_scrollbar.pack(side="right", fill="y")

        # Create a frame for new menu buttons (right side)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.update_ability_buttons()

    def load_abilities(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_ability_data(self, ability_id):
        # Look for the ability data by its ID in the loaded ability data
        for ability in self.ability_data:
            if ability['id'] == ability_id:
                return ability
        return None  # Return None if no matching ability is found

    def get_highest_spell_level(self, school):
        # Check the highest spell level the player has for a given school
        max_level = 0
        for ability_id in self.character.abilities:
            ability_data = self.get_ability_data(ability_id)  # A method to get ability data by its ID
            if ability_data and ability_data.get('school') == school:
                max_level = max(max_level, ability_data.get('grade', 0))
        return max_level
    
    def purchase_ability(self, ability):
        try:
            ability_type = ability.get('type', None)  # Safely get the 'type' key or None
            
            # Handle god selection for Paladins and Priests
            if ability_type == 'god':
                self.character.select_god(ability['id'])
                self.update_ability_buttons()

                # Grant free spells based on the current menu
                if "paladin" in self.ability_file:  # We're in the Paladin menu
                    if not self.character.free_spells_granted_for_paladin:
                        self.grant_free_paladin_abilities()

                elif "præst" in self.ability_file:  # We're in the Priest menu
                    if not self.character.free_spells_granted_for_priest:
                        self.grant_free_priest_abilities()

            # Handle free abilities for Warriors when entering the warrior menu for the first time
            elif ability_type == 'warrior_free':
                if not self.character.free_abilities_granted_for_warrior:
                    if self.ability_file == "Filer/standardevner.json":
                        self.ability_data = self.load_abilities("Filer/kriger.json")
                        self.grant_free_warrior_abilities()
                        self.ability_data = self.load_abilities("Filer/standardevner.json")

            elif ability_type == 'priest_free':
                if not self.character.free_abilities_granted_for_priest:
                    if self.ability_file == "Filer/standardevner.json":
                        self.ability_data = self.load_abilities("priest.json")
                        self.grant_free_priest_abilities()
                        self.ability_data = self.load_abilities("Filer/standardevner.json")
            
            elif ability_type == 'paladin_free':
                if not self.character.free_abilities_granted_for_paladin:
                    if self.ability_file == "Filer/standardevner.json":
                        self.ability_data = self.load_abilities("Filer/paladin.json")
                        self.grant_free_paladin_abilities()
                        self.ability_data = self.load_abilities("Filer/standardevner.json")
            
            elif ability_type == 'druid_free':
                if not self.character.free_abilities_granted_for_druid:
                    if self.ability_file == "Filer/standardevner.json":
                        self.ability_data = self.load_abilities("Filer/druide.json")
                        self.grant_free_paladin_abilities()
                        self.ability_data = self.load_abilities("Filer/standardevner.json")
            else:
                # Handle regular ability purchasing
                self.character.add_ability(ability['id'], ability['cost'])
                self.update_ep_display()

                if "trolddom" in self.ability_file:
                    self.app.update_class_info("Wizard")

                if "druide" in self.ability_file:
                    self.app.update_class_info("Druid")

                if "paladin" in self.ability_file:
                    self.app.update_class_info("Paladin")

                if "heks" in self.ability_file:
                    self.app.update_class_info("Witch")

                if "præst" in self.ability_file:
                    self.app.update_class_info("Priest")


                # 0Re-check for new abilities that may have been unlocked
                self.update_ability_buttons()

                # Check if the purchased ability unlocks a new menu
                self.check_menu_unlocks(ability['id'])

        except ValueError as e:
            messagebox.showerror("Fejl", str(e))


    def update_ability_buttons(self):
        self.ability_data = self.load_abilities(self.ability_file)
        # Clear existing ability buttons (left side)
        for widget in self.ability_scrollable_frame.winfo_children():
            widget.destroy()
        # Re-create buttons for abilities that are available
        for ability in self.ability_data:
            # Skip abilities already purchased (they will be greyed out later)
            if self.character.has_ability(ability['id']):
                self.create_disabled_button(ability)
                continue
            
            ability_type = ability.get('type', None)

            # Check for alchemy abilities
            if "alkymi" in self.ability_file:
                if self.check_alchemy_prereqs(ability):
                    self.create_ability_button(ability)


            # Check for paladin abilities
            elif "paladin" in self.ability_file:
                if self.check_paladin_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for priest abilities
            elif "præst" in self.ability_file:
                if self.check_priest_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for warrior abilities
            elif "kriger" in self.ability_file:
                if self.check_warrior_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for druid abilities
            elif "druide" in self.ability_file:
                if self.check_druid_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for mage abilities
            elif "trolddom" in self.ability_file:
                if self.check_wizard_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for shaman abilities
            elif "shaman" in self.ability_file:
                if self.check_shaman_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for witch abilities
            elif "heks" in self.ability_file:
                if self.check_witch_prereqs(ability):
                    self.create_ability_button(ability)

            # Check for runesmith abilities
            elif "runesmed" in self.ability_file:
                if self.check_runesmith_prereqs(ability):
                    self.create_ability_button(ability)

            # General abilities or abilities with no specific class
            else:
                if self.check_prerequisites(ability):
                    self.create_ability_button(ability)

        # Ensure new menu buttons are recreated and stay on the right side
        for name, button in self.new_menu_buttons.items():
            if not button.winfo_ismapped():
                button.pack(side="top", pady=5)  # Ensure the button is visible

    def create_disabled_button(self, ability):
        # Create a disabled button for purchased abilities
        ability_button = tk.Button(
            self.ability_scrollable_frame,
            text=f"{ability['name']} - Købt",
            state=tk.DISABLED
        )
        ability_button.pack(pady=5)

    def create_ability_button(self, ability):
        ability_type = ability.get('type', None)
        if ability_type == 'god' and ability['id'] == self.character.selected_god:
            self.create_disabled_button(ability)  # Grey out selected god
            return
        # Create a button for available abilities
        ability_button = tk.Button(
            self.ability_scrollable_frame,
            text=f"{ability['name']} - {ability['cost']} EP",
            command=lambda: self.purchase_ability(ability)
        )
        ability_button.pack(pady=5)
        self.ability_buttons[ability['id']] = ability_button

    def check_prerequisites(self, ability):
        if ability['id'] == "ability_kamptraening":
            ability_set = set(self.character.abilities)
            if {"ability_koordination_2", "ability_klatre"}.issubset(ability_set) and len({"ability_afstandsvaaben", "ability_tovaabenbrug"}.intersection(ability_set)) > 0:
                return True
            if {"ability_ekstra_livspoint_1", "ability_styrke"}.issubset(ability_set):
                return True
            if {"ability_skjoldbrug", "ability_overvaagenhed_1"}.issubset(ability_set) and len({"ability_laese_skrive_darconsk","ability_laese_skrive_eislonsk","ability_laese_skrive_emyriansk","ability_laese_skrive_garkiharn","ability_laese_skrive_garklin","ability_laese_skrive_oldparavisk","ability_laese_skrive_paravisk","ability_laese_skrive_runeskrift","ability_laese_skrive_taishen","ability_laese_skrive_tharkinsk","ability_laese_skrive_tziztisk","ability_laese_skrive_zarabinsk"}.intersection(ability_set)) > 0:
                return True
            return False
        # Get the prerequisites from the ability (can be None, dict, or list)
        prereqs = ability.get('prerequisite', {})

        # If prereqs is None, the ability has no prerequisites
        if prereqs is None:
            return True

        # Check if it's a dictionary with 'requires_abilities' or 'requires_one_of'
        if isinstance(prereqs, dict):
            # Check required abilities
            required_abilities = prereqs.get('requires_abilities', [])
            if isinstance(required_abilities, str):  # Handle single prerequisite case
                required_abilities = [required_abilities]

            for req in required_abilities:
                if req not in self.character.abilities:
                    return False

            if prereqs.get('lp_max_needed',None):
                if prereqs.get('lp_max_needed') > self.character.lp_max:
                    return False
            # Check 'one of' abilities (optional)
            requires_one_of = prereqs.get('requires_one_of', [])
            if requires_one_of:
                if isinstance(requires_one_of, str):  # Handle single prerequisite case
                    requires_one_of = [requires_one_of]

                if not any(req in self.character.abilities for req in requires_one_of):
                    return False

            # All prerequisites are met
            return True

        # In case of unexpected format (shouldn't happen but safety check)
        return False

    def create_god_button(self, ability):
        # Create a button for selecting a god
        god_button = tk.Button(
            self.ability_scrollable_frame,
            text=f"{ability['name']} - Vælg Gud",
            command=lambda: self.select_god(ability)
        )
        god_button.pack(pady=5)
        self.ability_buttons[ability['id']] = god_button
    
    def select_god(self, god_id):
        self.character.selected_god = god_id
        # Refresh the menu to show only relevant abilities
        self.update_ability_buttons()

    def check_paladin_prereqs(self, ability):
        prereqs = ability.get('prerequisite', {})

        # 1. If no god is selected, only allow god selection
         # If no god is selected, only show god buttons
        if self.character.selected_god is None:
            if 'god' in ability['type']:
                return True  # Show god selection
            return False  # Block all other abilities until a god is selected

        # If a god is selected, grey out other god buttons and remove them from the view
        if 'god' in ability['type']:
            return ability['id'] == self.character.selected_god  # Grey out selected god
        
        # 2. If the player has reached Paladin level 4 and no codex is chosen, only show codex options
        if 'codex' in ability['type']:
            has_codex = False
            for ability_2 in self.character.abilities:
                if 'codex' in ability_2:
                    has_codex = True
            if self.character.has_ability('paladin_level_4') and (has_codex == False or ability == ability_2):
                return True
            else:
                return False
        # 3. Ensure that only the selected god's abilities (spells) are shown
        selected_god = self.character.selected_god.replace("god_", "")
        if 'school' in ability and ability['school'] != selected_god and ability['school'] != 'almen':
            return False  # Hide spells from other gods' schools
        
        # 4. Handle paladin spell level requirements for levels and spells
        spell_reqs = False
        if prereqs != None:
            spell_reqs = prereqs.get('requires_spells', None)
        if spell_reqs:
            # Check if the player has at least one Almen and one God school spell of the required level
            almen_level_required = spell_reqs.get('almen', 0)
            god_school_level_required = spell_reqs.get('gudeskole', 0)

            # Check player's current Almen and God school spell levels
            player_almen_level = self.get_highest_spell_level('almen')
            player_god_school_level = self.get_highest_spell_level(selected_god)

            # Ensure the player meets the required levels for Almen and God school spells
            if player_almen_level < almen_level_required or player_god_school_level < god_school_level_required:
                return False

        # 5. Handle abilities that require previous levels (e.g., 'requires_ability')
        required_ability = False
        if prereqs != None:
            required_ability = prereqs.get('requires_ability', None)
        if required_ability and not self.character.has_ability(required_ability):
            return False

        # 6. Allow abilities with no prerequisites (e.g., Level 1 spells)
        if prereqs is None:
            return True

        # Everything is fine; allow this ability to be displayed
        return True

    def check_priest_prereqs(self, ability):
        prereqs = ability.get('prerequisite', {})

        # 1. If no god is selected, only allow god selection
        if self.character.selected_god is None:
            if 'god' in ability['type']:
                return True  # Show god selection
            return False  # Block all other abilities until a god is selected

        # If a god is selected, grey out other god buttons and remove them from the view
        if 'god' in ability['type']:
            return ability['id'] == self.character.selected_god  # Grey out selected god

        # 2. Ensure that only the selected god's abilities (spells) are shown
        selected_god = self.character.selected_god.replace("god_", "")
        if 'school' in ability and ability['school'] != selected_god and ability['school'] != 'almen':
            return False  # Hide spells from other gods' schools

        if prereqs is None:
            return True

        # 3. Handle priest spell level requirements for spells and levels
        spell_reqs = prereqs.get('requires_spells', None)
        if spell_reqs:
            # Check if the player has at least one Almen and one God school spell of the required level
            almen_level_required = spell_reqs.get('almen', 0)
            god_school_level_required = spell_reqs.get('gudeskole', 0)

            # Check player's current Almen and God school spell levels
            player_almen_level = self.get_highest_spell_level('almen')
            player_god_school_level = self.get_highest_spell_level(selected_god)

            # Ensure the player meets the required levels for Almen and God school spells
            if player_almen_level < almen_level_required or player_god_school_level < god_school_level_required:
                return False

        # 4. Handle abilities that require previous levels (e.g., 'requires_ability')
        required_ability = prereqs.get('requires_ability', None)
        if required_ability and not self.character.has_ability(required_ability):
            return False

        # 5. Allow abilities with no prerequisites (e.g., Level 1 spells)

        # Everything is fine; allow this ability to be displayed
        return True

    # Example of a Warrior-specific prerequisite check
    def check_warrior_prereqs(self, ability):
        #prereqs = ability.get('prerequisite', {})
        if ability.get('prerequisite', None) != None:
            prereqs = ability.get('prerequisite', {})
        else:
            prereqs = []
        ability_set = set(self.character.abilities)
        if ability['id'] == "warrior_ability_level_1_agility":
            if {"ability_koordination_2", "ability_klatre"}.issubset(ability_set) and len({"ability_afstandsvaaben", "ability_tovaabenbrug"}.intersection(ability_set)) > 0:
                return True
            return False
        if ability['id'] == "warrior_ability_level_1_strength":
            if {"ability_ekstra_livspoint_1", "ability_styrke"}.issubset(ability_set):
                return True
            return False
        if ability['id'] == "warrior_ability_level_1_tactics":
            if {"ability_skjoldbrug", "ability_overvaagenhed_1"}.issubset(ability_set) and len({"ability_laese_skrive_darconsk","ability_laese_skrive_eislonsk","ability_laese_skrive_emyriansk","ability_laese_skrive_garkiharn","ability_laese_skrive_garklin","ability_laese_skrive_oldparavisk","ability_laese_skrive_paravisk","ability_laese_skrive_runeskrift","ability_laese_skrive_taishen","ability_laese_skrive_tharkinsk","ability_laese_skrive_tziztisk","ability_laese_skrive_zarabinsk"}.intersection(ability_set)) > 0:
                return True
            return False
        
        if ability['id'] in ["warrior_ability_level_1_ridderkamp","warrior_ability_level_1_ethaandetfaegtekunst","warrior_ability_level_1_spydkamp","warrior_ability_level_1_bueskydning","warrior_ability_level_1_dobbeltvaebnetkamp","warrior_ability_level_1_tohaandsvaabenkamp"]:
            if "warrior_spell_udoedelighed" in self.character.abilities or "warrior_spell_anti_magisk_tilfoersel" in self.character.abilities:
                if "warrior_spell_jernets_faestning" in self.character.abilities or "warrior_spell_nyrestoed" in self.character.abilities or "warrior_spell_beskidt_kamp" in self.character.abilities or "warrior_spell_skyggernes_pil" in self.character.abilities or "warrior_spell_ren_loyalitet" in self.character.abilities or "warrior_spell_symbolets_magt" in self.character.abiltiies:
                    return True
            return False
        
        if not 'requires_ability' in prereqs:
            if ability['grade'] == 1:
                return len({"warrior_ability_level_1_strength", "warrior_ability_level_1_agility", "warrior_ability_level_1_tactics"}.intersection(ability_set)) > 0
            elif ability['grade'] == 2:
                return len({"warrior_ability_level_2_strength", "warrior_ability_level_2_agility", "warrior_ability_level_2_tactics"}.intersection(ability_set)) > 0
            else:
                return len({"warrior_ability_level_3_strength", "warrior_ability_level_3_agility", "warrior_ability_level_3_tactics"}.intersection(ability_set)) > 0

        almen_1 = {"warrior_spell_overlevelsesinstinkt","warrior_spell_det_glatte_sind"}
        almen_2 = {"warrior_spell_standhaftighed","warrior_spell_kampberedskab"}
        styrke_1 = {"warrior_spell_muskelbundt","warrior_spell_tykpandet"}
        styrke_2 = {"warrior_spell_bastion","warrior_spell_troldeslag"}
        smidighed_1 = {"warrior_spell_camouflage","warrior_spell_hvem_er_du"}
        smidighed_2 = {"warrior_spell_spejder","warrior_spell_smidig_kamp"}
        taktik_1 = {"warrior_spell_lederskab","warrior_spell_rustningsspecialisering"}
        taktik_2 = {"warrior_spell_faellesskab","warrior_spell_bannerherre"}

        if ability['id'] == "warrior_ability_level_2_strength":
            return len(styrke_1.intersection(ability_set)) > 0 and len(almen_1.intersection(ability_set)) > 0
        if ability['id'] == "warrior_ability_level_3_strength":
            return len(styrke_2.intersection(ability_set)) > 0 and len(almen_2.intersection(ability_set)) > 0
        if ability['id'] == "warrior_ability_level_2_agility":
            return len(smidighed_1.intersection(ability_set)) > 0 and len(almen_1.intersection(ability_set)) > 0
        if ability['id'] == "warrior_ability_level_3_agility":
            return len(smidighed_2.intersection(ability_set)) > 0 and len(almen_2.intersection(ability_set)) > 0
        if ability['id'] == "warrior_ability_level_2_tactics":
            return len(taktik_1.intersection(ability_set)) > 0 and len(almen_1.intersection(ability_set)) > 0
        if ability['id'] == "warrior_ability_level_3_tactics":
            return len(taktik_2.intersection(ability_set)) > 0 and len(almen_2.intersection(ability_set)) > 0

        if prereqs != None and 'requires_ability' in prereqs:
            required_abilities = prereqs['requires_ability']
            if required_abilities not in self.character.abilities:
                return False
        return True

    # Example of a Druid-specific prerequisite check
    def check_druid_prereqs(self, ability):
        """Check if the prerequisites for a druid ability or spell are met."""
        
        # Helper function to find an ability by ID in ability_data
        def find_ability_by_id(ability_id):
            return next((a for a in self.ability_data if a['id'] == ability_id), None)
        
        # Get the type of the ability
        ability_type = ability.get('type', None)

        # 1. If the ability is a druid_ability
        if ability_type == "druid_ability":
            prerequisite = ability.get('prerequisite', {})
            required_grade = prerequisite.get('grade', None)
            required_ability = prerequisite.get('required_ability', None)

            # Check if the required_ability is not None and ensure the player has it
            if required_ability and required_ability not in self.character.abilities:
                return False

            # If this ability is not "druid_ability_grad_5" or "druid_ability_grad_6"
            if ability['id'] not in ['druid_ability_grad_5', 'druid_ability_grad_6']:
                # Check if the player has at least 2 druid_spell abilities with the required grade
                matching_spells_count = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and
                    found_ability.get('type') == 'druid_spell' and found_ability.get('grade') == required_grade
                )
                if matching_spells_count < 2:
                    return False

            # For "druid_ability_grad_5" and "druid_ability_grad_6", only check required_ability
            return True

        # 2. If the ability is a druid_spell
        elif ability_type == "druid_spell":
            # Check if the ability has a requires_ability in prerequisites
            required_ability = ability['prerequisite'].get('requires_ability', None)
            if required_ability and required_ability not in self.character.abilities:
                return False
            
            # If the check passes, the prerequisites are met for a druid_spell
            return True

        # If the ability doesn't match any known type, return False by default
        return False


    # Example of a Witch-specific prerequisite check
    def check_witch_prereqs(self, ability):
        """Check if the prerequisites for a witch ability are met."""
        
        # Helper function to find an ability by ID in ability_data
        def find_ability_by_id(ability_id):
            return next((a for a in self.ability_data if a['id'] == ability_id), None)

        # Check the type of the ability
        ability_type = ability.get('type', None)

        # 1. If the ability is a witch_ritual
        if ability_type == "witch_ritual":
            # Check for requires_spells in prerequisites
            requires_spells = ability['prerequisite'].get('requires_spells', 0)
            if requires_spells > 0:
                # Count how many witch_spell abilities the character has
                witch_spells_count = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and found_ability.get('type') == 'witch_spell'
                )
                if witch_spells_count < requires_spells:
                    return False

            # Check for requires_spell in prerequisites (requires a specific spell)
            required_spell = ability['prerequisite'].get('requires_spell', None)
            if required_spell and required_spell not in self.character.abilities:
                return False

            # Check for requires_blood_rituals in prerequisites
            requires_blood_rituals = ability['prerequisite'].get('requires_blood_rituals', 0)
            if requires_blood_rituals > 0:
                # Count how many witch_ritual abilities the character has
                blood_rituals_count = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and found_ability.get('type') == 'witch_ritual'
                )
                if blood_rituals_count < requires_blood_rituals:
                    return False

            # If all checks pass, the prerequisites are met for a witch_ritual
            return True

        # 2. If the ability is a witch_spell
        elif ability_type == "witch_spell":
            if ability.get('grade', None) > 1:
                # Check for requires_ability in prerequisites (requires a specific ability)
                required_ability = ability['prerequisite'].get('requires_ability', None)
                if required_ability and required_ability not in self.character.abilities:
                    return False

            # If the check passes, the prerequisites are met for a witch_spell
            return True

        # 3. If the ability is a witch_ability
        elif ability_type == "witch_ability":
            # Check for grade in prerequisites
            required_grade = ability['prerequisite'].get('grade', None)
            if required_grade:
                # Count how many witch_spell abilities with the same grade the character has
                matching_spells_count = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and found_ability.get('type') == 'witch_spell' and found_ability.get('grade') == required_grade
                )
                if matching_spells_count < 2:
                    return False

            # If the check passes, the prerequisites are met for a witch_ability
            return True

        # If the ability doesn't match any known type, return False by default
        return False

    # Example of a Runesmith-specific prerequisite check
    def check_runesmith_prereqs(self, ability):
        """Check if the prerequisites for a runesmith ability or spell are met."""
        
        # Helper function to find an ability by ID in ability_data
        def find_ability_by_id(ability_id):
            return next((a for a in self.ability_data if a['id'] == ability_id), None)

        # 1. If the ability is "runesmith_invester_kraft"
        if ability['id'] == "runesmith_invester_kraft":
            required_ability = ability['prerequisite'].get('requires_ability', None)
            # Check if the player has the required ability
            if required_ability and required_ability not in self.character.abilities:
                return False
            return True

        # 2. If the ability is of type "runesmith_ability"
        elif ability.get('type') == "runesmith_ability":
            prerequisite = ability.get('prerequisite', {})
            required_ability = prerequisite.get('requires_ability', None)
            required_grade = prerequisite.get('grade', None)

            # Check if the player has the required ability
            if required_ability and required_ability not in self.character.abilities:
                return False

            # Check if the player has at least 2 runesmith_spell abilities with the required grade
            if required_grade:
                matching_spells_count = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and
                    found_ability.get('type') == 'runesmith_spell' and found_ability.get('grade') == required_grade
                )
                if matching_spells_count < 2:
                    return False

            return True

        # 3. If the ability is of type "runesmith_spell"
        elif ability.get('type') == "runesmith_spell":
            prerequisite = ability.get('prerequisite', None)
            if prerequisite:
                required_ability = prerequisite.get('requires_ability', None)
                # Check if the player has the required ability
                if required_ability and required_ability not in self.character.abilities:
                    return False
            return True

        # If the ability type doesn't match any of the above, return False by default
        return False

    # Example of a Shaman-specific prerequisite check
    def check_shaman_prereqs(self, ability):
        prereqs = ability.get('prerequisite', {})
        if prereqs != None and 'requires_ability' in prereqs:
            required_ability = prereqs['requires_ability']
            if required_ability not in self.character.abilities:
                return False
        return True

    # Example of a Wizard-specific prerequisite check
    def check_wizard_prereqs(self, ability):
        """Check if the prerequisites for a wizard ability or spell are met."""

        # Helper function to find an ability by ID in ability_data
        def find_ability_by_id(ability_id):
            # Ensure we are looking up the full ability data from ability_data based on the ability ID
            return next((a for a in self.ability_data if a['id'] == ability_id), None)

        # Get the type and school of the current ability being checked
        ability_type = ability.get('type', None)
        ability_school = ability.get('school', None)

        # 1. Handle the three specific level 1 abilities
        if ability['id'] in ["wizard_level_1_elementalisme", "wizard_level_1_mentalisme", "wizard_level_1_morticisme"]:
            level_1_abilities = [
                "wizard_level_1_elementalisme", "wizard_level_1_mentalisme", "wizard_level_1_morticisme"
            ]
            level_1_owned = [a for a in level_1_abilities if a in self.character.abilities]

            # If the player doesn't have any of the level 1 abilities, show them all
            if not level_1_owned:
                return True

            # If the player has one, only show the others if they have a level 3 ability
            level_3_abilities = [
                "wizard_level_3_elementalisme", "wizard_level_3_mentalisme", "wizard_level_3_morticisme"
            ]
            if len(level_1_owned) == 1 and ability['id'] not in level_1_owned:
                if any(lvl3 in self.character.abilities for lvl3 in level_3_abilities):
                    return True
                else:
                    return False

            # If the player has two, don't show the third one
            if len(level_1_owned) == 2 and ability['id'] not in level_1_owned:
                return False

            return True  # Show the abilities the player already has

        # 2. Handle "wizard_ability" type (excluding the three specific abilities)
        elif ability_type == "wizard_ability":
            prerequisite = ability.get('prerequisite', {})
            required_ability = prerequisite.get('requires_ability', None)

            # Check if the player has the required ability
            if required_ability and required_ability not in self.character.abilities:
                return False

            # Get the required number of spells based on the ability's grade
            required_grade = ability.get('grade', None)
            if required_grade:
                # Count spells in the same school as the ability by cross-referencing character abilities with ability_data
                matching_school_spells = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and
                    found_ability.get('type') == 'wizard_spell' and found_ability.get('school') == ability_school
                )

                # Count spells in the "almen" school
                almen_school_spells = sum(
                    1 for ability_id in self.character.abilities
                    if (found_ability := find_ability_by_id(ability_id)) and
                    found_ability.get('type') == 'wizard_spell' and found_ability.get('school') == 'almen'
                )

                # Check if the player has the required number of spells in both schools
                if matching_school_spells < required_grade or almen_school_spells < required_grade:
                    return False

            return True

        # 3. Handle "wizard_spell" type
        elif ability_type == "wizard_spell":
            if ability_school == "almen":
                # Check if the player has a wizard_ability with the same grade
                required_grade = ability.get('grade', None)
                if required_grade:
                    matching_abilities = sum(
                        1 for ability_id in self.character.abilities
                        if (found_ability := find_ability_by_id(ability_id)) and
                        found_ability.get('type') == 'wizard_ability' and found_ability.get('grade') == required_grade
                    )
                    if matching_abilities == 0:
                        return False
            else:
                # Check if the player has the required ability in prerequisites
                required_ability = ability.get('prerequisite', {}).get('requires_ability', None)
                if required_ability and required_ability not in self.character.abilities:
                    return False

            return True

        # 4. Handle "wizard_ekstra_mana"
        elif ability['type'] == "wizard_special_ability":
            required_spell = ability.get('prerequisite', {}).get('requires_spell', None)
            if required_spell and required_spell not in self.character.abilities:
                return False
            return True

        # Default return False if none of the conditions are met
        return False



    # Example of an Alchemy-specific prerequisite check
    def check_alchemy_prereqs(self, ability):
        prereqs = ability.get('prerequisite', {})
        
        # 1. Check for abilities with 'lower_level_recipes_required'
        lower_recipes_required = None
        current_grade = None
        lower_recipes_required = prereqs.get('lower_level_recipes_required', None)
        current_grade = prereqs.get('grade', None)

        if lower_recipes_required is not None and current_grade is not None:
            previous_grade = current_grade - 1

            # Find the player's abilities that have a grade in the prerequisite
            recipes_of_previous_grade = [
                ab for ab in self.character.abilities
                if self.get_ability_data(ab) is not None and
                'prerequisite' in self.get_ability_data(ab) and 
                self.get_ability_data(ab)['prerequisite'].get('grade', 0) == previous_grade
            ]

            # Find the player's abilities that are of the current grade
            recipes_of_current_grade = [
                ab for ab in self.character.abilities
                if self.get_ability_data(ab) is not None and
                'prerequisite' in self.get_ability_data(ab) and 
                self.get_ability_data(ab)['prerequisite'].get('grade', 0) == current_grade
            ]
            # If the player doesn't have enough recipes of the previous level, block all recipes of the current level
            if len(recipes_of_previous_grade) < lower_recipes_required:
                return False

            # If the player has enough current-level recipes, hide all remaining recipes of the current level
            if len(recipes_of_current_grade) >= len(recipes_of_previous_grade) and current_grade != 1:
                return False

        # 2. Check for prerequisite abilities ('requires_ability')
        required_abilities = prereqs.get('requires_abilities', None)
        if required_abilities is not None:
            for required_ability in required_abilities:
                if not self.character.has_ability(required_ability):
                    return False

        # 3. Allow abilities with no prerequisites
        if prereqs is None:
            return True

        # 4. Allow all other abilities by default
        return True





    # Fallback for standard abilities
    def check_standard_prereqs(self, ability):
        # Get the prerequisites from the ability (make sure it's a dict or default to an empty dict)
        prereqs = ability.get('prerequisite', {})
        
        # If prereqs is None, treat it as no prerequisites
        if prereqs is None:
            return True

        # Check if specific abilities are required
        if prereqs != None and 'requires_abilities' in prereqs:
            required_abilities = prereqs['requires_abilities']
            for req in required_abilities:
                if req not in self.character.abilities:
                    return False

        # All prerequisites met, return True
        return True


    # Other methods (create_ability_button, create_disabled_button, purchase_ability, etc.) remain unchanged...

    def update_ep_display(self):
        self.ep_label.config(text=f"EP tilbage: {self.character.remaining_ep()}")

    def grant_free_alchemist_abilities(self):
        """Grant two free alchemist abilities: one from a specific list and one with grade 1 prerequisites."""
        for abilities in self.character.abilities:
            if "alkymi_" in abilities:
                self.character.free_spells_granted_for_alchemist = True

        if self.character.free_spells_granted_for_alchemist:
            return  # Don't grant spells again if they've already been granted

        # 1. First ability: Choose between 'alkymi_bloedning' or 'alkymi_alkymisk_analyse'
        alchemist_options = [
            ability for ability in self.ability_data
            if ability['id'] in ['alkymi_bloedning', 'alkymi_alkymisk_analyse']
        ]
        first_ability = self.prompt_ability_choice(alchemist_options, "Vælg en gratis alkymist evne")

        # 2. Second ability: Choose from abilities with 'grade' in prerequisites, and 'grade' == 1
        grade_1_abilities = [
            ability for ability in self.ability_data
            if ability.get('prerequisite') and ability['prerequisite'].get('grade') == 1
        ]
        if grade_1_abilities:
            second_ability = self.prompt_ability_choice(grade_1_abilities, "Vælg en gratis evne med grad 1")

            # Add the chosen abilities to the character for free
            self.character.add_ability(first_ability['id'], 0)
            self.character.add_ability(second_ability['id'], 0)

        else:
            # If no abilities with grade 1 are found, show a message
            print("No abilities with grade 1 prerequisites found.")
            self.character.add_ability(first_ability['id'], 0)

        # Update the ability buttons to reflect the new abilities
        self.update_ability_buttons()

        # Mark free alchemist abilities as granted
        self.character.free_spells_granted_for_alchemist = True

    def grant_free_priest_abilities(self):
        """Grant two free first-level spells from the Priest's Almen or god school."""
        for abilities in self.character.abilities:
            if "priest_" in abilities:
                self.character.free_spells_granted_for_priest = True

        if self.character.free_spells_granted_for_priest:
            return  # Don't grant spells again if they've already been granted

        # Ensure a god is selected
        if self.character.selected_god is None:
            return

        selected_god = self.character.selected_god.replace("god_", "")

        # Filter to get first-level spells from Almen or the selected god's school
        free_spells = [
            ability for ability in self.ability_data
            if 'priest_spell' in ability['id']  # Make sure we're looking for priest spells
            and (ability['school'] == 'almen' or ability['school'] == selected_god)
            and (
                ability.get('prerequisite') is None  # Spells with no prerequisite are level 1
                or (ability.get('prerequisite', {}).get('grade') == 1)  # Spells with grade 1
            )
        ]

        if not free_spells:  # If no free spells are available, show a message and return
            messagebox.showinfo("Information", "Der er ingen gratis besværgelser tilgængelige.")
            return

        # Player selects two spells
        chosen_spell_1 = self.prompt_ability_choice(free_spells, "Vælg en gratis førstegradbesværgelse")
        free_spells.remove(chosen_spell_1)
        chosen_spell_2 = self.prompt_ability_choice(free_spells, "Vælg endnu en gratis førstegradbesværgelse")

        # Add the chosen abilities to the player's character under the Priest class
        self.character.add_ability(chosen_spell_1['id'], 0)
        self.character.add_ability(chosen_spell_2['id'], 0)

        # Update the ability buttons immediately
        self.update_ability_buttons()

        # Mark that free spells have been granted for the priest system
        if hasattr(self, 'priest_window') and self.priest_window is not None:
            self.priest_window.destroy()
            self.priest_window = None
        elif self.character.free_spells_granted_for_priest == False and self.character.free_spells_granted_for_paladin == False:
            self.root.destroy()
            
        self.character.free_spells_granted_for_priest = True

    def grant_free_paladin_abilities(self):
        for abilities in self.character.abilities:
            if "paladin_" in abilities:
                self.character.free_spells_granted_for_paladin = True

        """Grant two free first-level spells from the Paladin's Almen or god school."""
        if self.character.free_spells_granted_for_paladin:
            return  # Don't grant spells again if they've already been granted

        # Ensure a god is selected
        if self.character.selected_god is None:
            return

        selected_god = self.character.selected_god.replace("god_", "")

        # Get first-level spells from Almen or the selected god for Paladins
        free_spells = [
            ability for ability in self.ability_data
            if 'paladin_spell' in ability['id']
            and (ability.get('prerequisite') is None or ability['prerequisite'].get('grade', 0) == 1)
            and (ability['school'] == 'almen' or ability['school'] == selected_god)
        ]

        if not free_spells:  # If no free spells are available, show a message and return
            messagebox.showinfo("Information", "Der er ingen gratis besværgelser tilgængelige.")
            return

        # Player chooses two spells
        chosen_spell_1 = self.prompt_ability_choice(free_spells, "Vælg en gratis førstegradbesværgelse")
        free_spells.remove(chosen_spell_1)
        chosen_spell_2 = self.prompt_ability_choice(free_spells, "Vælg en anden gratis førstegradbesværgelse")

        # Add the chosen abilities to the player's character under the Paladin class
        self.character.add_ability(chosen_spell_1['id'], 0)
        self.character.add_ability(chosen_spell_2['id'], 0)

        # Update the ability buttons and mark free spells as granted for Paladin

        self.update_ability_buttons()
        
        if hasattr(self, 'paladin_window') and self.paladin_window is not None:
            self.paladin_window.destroy()
            self.paladin_window = None
        elif self.character.free_spells_granted_for_paladin == False and self.character.free_spells_granted_for_priest == False:
            self.root.destroy()
        self.character.free_spells_granted_for_paladin = True

    def grant_free_warrior_abilities(self):
        for abilities in self.character.abilities:
            if "warrior_" in abilities:
                self.character.free_spells_granted_for_warrior = True

        """Grant three free warrior abilities upon entering the warrior menu for the first time."""
        if self.character.free_spells_granted_for_warrior:
            return  # Don't grant spells again if they've already been granted

        # First ability: Choose any ability for which the character meets warrior prerequisites
        warrior_abilities = [ability for ability in self.ability_data if self.check_warrior_prereqs(ability)]
        first_ability = self.prompt_ability_choice(warrior_abilities, "Vælg en gratis førstegradskrigerevne")

        # Second ability: Choose from abilities with grade 1 and discipline 'den_almen_disciplin'
        general_discipline_abilities = [
            ability for ability in self.ability_data
            if ability.get('grade') == 1 and ability.get('discipline') == "den_almen_disciplin"
        ]
        second_ability = self.prompt_ability_choice(general_discipline_abilities, "Vælg en gratis almen disciplin evne")

        # Third ability: Choose from abilities with grade 1 and the same discipline as the first ability
        discipline_of_first_ability = first_ability.get('discipline', None)
        matching_discipline_abilities = [
            ability for ability in self.ability_data
            if ability.get('grade') == 1 and ability.get('discipline') == discipline_of_first_ability
            and ability['id'] != first_ability['id']  # Ensure the third ability isn't the same as the first one
            and ability['id'] != second_ability['id']  # Ensure the third ability isn't the same as the second one
        ]
        third_ability = self.prompt_ability_choice(matching_discipline_abilities, f"Vælg en gratis evne fra disciplinen {discipline_of_first_ability}")

        # Add the chosen abilities to the character for free
        self.character.add_ability(first_ability['id'], 0)
        self.character.add_ability(second_ability['id'], 0)
        self.character.add_ability(third_ability['id'], 0)

        # Mark free warrior abilities as granted
        self.character.free_spells_granted_for_warrior = True
        self.update_ability_buttons()

    # Grant free abilities for Druid
    def grant_free_druid_abilities(self):
        for abilities in self.character.abilities:
            if "druid_" in abilities:
                self.character.free_spells_granted_for_druid = True
        
        """Grant one free druid spell for which the player meets the prerequisites."""
        if self.character.free_spells_granted_for_druid:
            return  # Don't grant spells again if they've already been granted
        
        # Filter the list of druid spells for which the character meets the prerequisites
        available_spells = [
            ability for ability in self.ability_data
            if ability.get('type') == 'druid_spell' and self.check_druid_prereqs(ability)
        ]

        # Ensure there are available spells to choose from
        if not available_spells:
            print("No druid spells available that meet the prerequisites.")
            return

        # Let the player choose one free spell from the available spells
        chosen_spell = self.prompt_ability_choice(available_spells, "Vælg en gratis druidebesværgelse")

        # Add the chosen spell to the character for free
        self.character.add_ability(chosen_spell['id'], 0)

        # Update the ability buttons to reflect the new ability
        self.update_ability_buttons()

        # Mark free druid spells as granted (add this flag to your character class)
        self.character.free_spells_granted_for_druid = True

    # Grant free abilities for Witch
    def grant_free_witch_abilities(self):
        for abilities in self.character.abilities:
            if "witch_" in abilities:
                self.character.free_spells_granted_for_witch = True

        """Grant two free witch spells of type 'witch_spell' and grade 1."""
        if self.character.free_spells_granted_for_witch:
            return  # Don't grant spells again if they've already been granted
        
        # Filter the list to get only witch spells with grade 1
        grade_1_spells = [
            ability for ability in self.ability_data
            if ability.get('type') == 'witch_spell' and ability.get('grade') == 1
        ]
        
        # Ensure there are enough grade 1 witch spells to choose from
        if len(grade_1_spells) < 2:
            print("Not enough grade 1 witch spells available.")
            return

        # First ability: Let the player choose one spell from the grade 1 witch spells
        first_spell = self.prompt_ability_choice(grade_1_spells, "Vælg en gratis heksebesværgelse (grad 1)")

        # Add the chosen spells to the character for free
        self.character.add_ability(first_spell['id'], 0)

        # Update the ability buttons to reflect the new abilities
        self.update_ability_buttons()

        # Mark free witch spells as granted (add this flag to your character class)
        self.character.free_spells_granted_for_witch = True

    # Grant free abilities for Runesmith
    def grant_free_runesmith_abilities(self):
        for abilities in self.character.abilities:
            if "runesmith_" in abilities:
                self.character.free_spells_granted_for_runesmith = True
        
        """Grant one free Runesmith spell for which the player meets the prerequisites."""
        if self.character.free_spells_granted_for_runesmith:
            return  # Don't grant spells again if they've already been granted

        # Filter the list of runesmith spells for which the character meets the prerequisites
        available_spells = [
            ability for ability in self.ability_data
            if ability.get('type') == 'runesmith_spell' and self.check_runesmith_prereqs(ability)
        ]

        # Ensure there are available spells to choose from
        if not available_spells:
            print("No runesmith spells available that meet the prerequisites.")
            return

        # Let the player choose one free spell from the available spells
        chosen_spell = self.prompt_ability_choice(available_spells, "Vælg en gratis runesmed besværgelse")

        # Add the chosen spell to the character for free
        self.character.add_ability(chosen_spell['id'], 0)

        # Update the ability buttons to reflect the new ability
        self.update_ability_buttons()

        # Mark free runesmith spells as granted (add this flag to your character class)
        self.character.free_spells_granted_for_runesmith = True

        # Runesmiths get one first-level spell
        free_spells = [ability for ability in self.ability_data
                    if 'runesmith_spell' in ability['id']
                    and 'grade' in ability['prerequisite']
                    and ability['prerequisite']['grade'] == 1]

        if not free_spells:
            return

        # Player chooses one free spell
        chosen_spell = self.prompt_ability_choice(free_spells, "Vælg en første niveau runesmedefortryllelse")
        self.character.add_ability(chosen_spell['id'], 0)

    # Grant free abilities for Shaman (no free abilities)
    def grant_free_shaman_abilities(self):
        # Shamans don't get free abilities, so no action needed
        pass

    # Grant free abilities for Mage (Trolddom)
    def grant_free_wizard_abilities(self):
        for abilities in self.character.abilities:
            if "wizard_" in abilities:
                self.character.free_spells_granted_for_wizard = True

        """Grant three free wizard abilities based on player choices."""
        if self.character.free_spells_granted_for_wizard:
            return  # Don't grant spells again if they've already been granted
        
        # 1. First ability: Choose between the three special wizard level 1 abilities
        first_options = [
            ability for ability in self.ability_data
            if ability['id'] in ["wizard_level_1_elementalisme", "wizard_level_1_mentalisme", "wizard_level_1_morticisme"]
        ]
        first_ability = self.prompt_ability_choice(first_options, "Vælg en gratis første niveau troldmands evne")

        # 2. Second ability: Choose from abilities of type 'wizard_spell', school 'almen', and grade 1
        second_options = [
            ability for ability in self.ability_data
            if ability.get('type') == 'wizard_spell' and ability.get('school') == 'almen' and ability.get('grade') == 1
        ]
        
        # Ensure there are valid second options
        if not second_options:
            print("No valid second ability options available.")
            return
        
        second_ability = self.prompt_ability_choice(second_options, "Vælg en gratis almen besværgelse af første grad")

        # 3. Third ability: Choose from abilities of type 'wizard_spell', school equal to first ability, and grade 1
        selected_school = first_ability.get('school', None)  # Get the school of the first ability
        third_options = [
            ability for ability in self.ability_data
            if ability.get('type') == 'wizard_spell' and ability.get('school') == selected_school and ability.get('grade') == 1
        ]
        
        # Ensure there are valid third options
        if not third_options:
            print(f"No valid third ability options available for the school {selected_school}.")
            return
        
        third_ability = self.prompt_ability_choice(third_options, f"Vælg en gratis besværgelse fra skolen {selected_school}")

        # Add the chosen abilities to the character for free
        self.character.add_ability(first_ability['id'], 0)
        self.character.add_ability(second_ability['id'], 0)
        self.character.add_ability(third_ability['id'], 0)

        # Update the ability buttons to reflect the new abilities
        self.update_ability_buttons()

        # Mark free wizard abilities as granted (add this flag to your character class)
        self.character.free_spells_granted_for_wizard = True



    def prompt_ability_choice(self, ability_list, prompt_message):
        # Create a dialog window to prompt the user for a selection
        choice_window = tk.Toplevel(self.root)
        choice_window.title(prompt_message)

        chosen_ability = tk.StringVar()

        # Function to capture the user's selection and close the window
        def select_ability():
            choice_window.destroy()

        # Display all available abilities as radio buttons
        for ability in ability_list:
            tk.Radiobutton(
                choice_window,
                text=ability['name'],
                variable=chosen_ability,
                value=ability['id']
            ).pack(anchor="w")

        # Add a submit button to confirm the choice
        tk.Button(choice_window, text="Vælg", command=select_ability).pack()

        # Wait for the user to make a choice
        choice_window.wait_window()

        # Find the selected ability from the list and return it
        selected_ability = next((ability for ability in ability_list if ability['id'] == chosen_ability.get()), None)

        return selected_ability

    def check_menu_unlocks(self, ability_id):
        unlocks = {
            "ability_alkymi": ("Alkymievner", "Filer/alkymi.json"),
            "ability_guddommelig_vassal": ("Paladinevner", "Filer/paladin.json"),
            "ability_hellig_ed": ("Præsteevner", "Filer/præst.json"),
            "ability_kaste_skrive_magi": ("Trolddomsevner", "Filer/trolddom.json"),
            "ability_shamanisme": ("Shamanevner", "Filer/shaman.json"),
            "ability_skyggepagt": ("Hekseevner", "Filer/heks.json"),
            "ability_vogter_af_naturens_sjael": ("Druideevner", "Filer/druide.json"),
            "ability_kamptraening": ("Krigerevner", "Filer/kriger.json"),
            "ability_runesmedning": ("Runesmedevner", "Filer/runesmed.json")
        }

        # Unlock the menu if required
        if ability_id in unlocks:
            name, file = unlocks[ability_id]
            self.create_new_menu_button(name, file)

    def create_new_menu_button(self, name, file):
        # Only create a new button if one doesn't already exist
        if name not in self.new_menu_buttons:
            new_menu_button = tk.Button(
                self.right_frame,  # Ensure it's added to the right frame (separate from the main ability buttons)
                text=name,
                command=lambda: self.open_new_menu(file)
            )
            new_menu_button.pack(pady=5)
            self.new_menu_buttons[name] = new_menu_button

    def open_new_menu(self, new_ability_file):
        #Opens a new menu for a given ability file (like Paladin, Priest, or Warrior), unless free abilities need to be granted first.
        
        # Check for Paladin free spells or god selection
        if "paladin" in new_ability_file:
            if not self.character.selected_god:
                # Call method to prompt god selection for Paladins
                self.paladin_window = tk.Toplevel(self.root)
                ability_manager = AbilityManager(self.character, self.paladin_window, "Filer/paladin.json", self.ep_label, self)
                return
            elif not self.character.free_spells_granted_for_paladin:
                if self.ability_file == "Filer/standardevner.json":
                    self.ability_data = self.load_abilities("Filer/paladin.json")
                    self.grant_free_paladin_abilities()
                    self.ability_data = "Filer/standardevner.json"
                return

        # Check for Priest free spells or god selection
        elif "præst" in new_ability_file:
            if not self.character.selected_god:

                # Call method to prompt god selection for Priests
                self.priest_window = tk.Toplevel(self.root)
                ability_manager = AbilityManager(self.character, self.priest_window, "Filer/præst.json", self.ep_label, self)
                return
            elif not self.character.free_spells_granted_for_priest:
                if self.ability_file == "Filer/standardevner.json":
                    self.ability_data = self.load_abilities("Filer/præst.json")
                    self.grant_free_priest_abilities()
                    self.ability_data = "Filer/standardevner.json"
                return

        # Check for Warrior free abilities
        elif "kriger" in new_ability_file:
            if not self.character.free_spells_granted_for_warrior:
                if self.ability_file == "Filer/standardevner.json":
                    self.ability_data = self.load_abilities("Filer/kriger.json")
                    self.grant_free_warrior_abilities()
                    self.ability_data = "Filer/standardevner.json"
                return
        
        elif "alkymi" in new_ability_file:
            if not self.character.free_spells_granted_for_alchemist:
                self.ability_data = self.load_abilities("Filer/alkymi.json")
                self.grant_free_alchemist_abilities()
                self.ability_data = "Filer/standardevner.json"
                return
        
        elif "heks" in new_ability_file:
            if not self.character.free_spells_granted_for_witch:
                self.ability_data = self.load_abilities("Filer/heks.json")
                self.grant_free_witch_abilities()
                self.ability_data = "Filer/standardevner.json"
                return
        
        elif "druide" in new_ability_file:
            if not self.character.free_spells_granted_for_druid:
                self.ability_data = self.load_abilities("Filer/druide.json")
                self.grant_free_druid_abilities()
                self.ability_data = "Filer/standardevner.json"
                return
            
        elif "runesmed" in new_ability_file:
            if not self.character.free_spells_granted_for_runesmith:
                self.ability_data = self.load_abilities("Filer/runesmed.json")
                self.grant_free_runesmith_abilities()
                self.ability_data = "Filer/standardevner.json"
                return
            
        elif "trolddom" in new_ability_file:
            if not self.character.free_spells_granted_for_wizard:
                self.ability_data = self.load_abilities("Filer/trolddom.json")
                self.grant_free_wizard_abilities()
                self.ability_data = "Filer/standardevner.json"
                return

        # If none of the above conditions apply, open the class menu
        new_window = tk.Toplevel(self.root)

        # Open the new ability menu in a separate window
        ability_manager = AbilityManager(self.character, new_window, new_ability_file, self.ep_label, self.app) 

        # Now we can call update_class_info based on the class
        if "paladin" in new_ability_file:
            self.app.update_class_info("Paladin")
        elif "præst" in new_ability_file:
            self.app.update_class_info("Priest")
        elif "druide" in new_ability_file:
            self.app.update_class_info("Druid")
        elif "heks" in new_ability_file:
            self.app.update_class_info("Witch")
        elif "trolddom" in new_ability_file:
            self.app.update_class_info("Wizard")

        # Update self.ability_data with the new menu's data
        self.ability_data = ability_manager.ability_data
        self.update_ability_buttons()  # Load and display the abilities for the selected menu

class CharacterApp:
    def __init__(self, root):
        self.root = root
        self.character = Character()

        self.main_menu_frame = tk.Frame(self.root)
        self.main_menu_frame.pack()

        self.load_button = tk.Button(self.main_menu_frame, text="Indlæs karakter", command=self.load_character)
        self.load_button.pack()

        self.save_button = tk.Button(self.main_menu_frame, text="Gem karakter", command=self.save_character)
        self.save_button.pack()

        self.ep_label = tk.Label(self.main_menu_frame, text="EP tilbage: 0")  # Default EP
        self.ep_label.pack()

        self.class_info_labels = {}

    def load_character(self):
        initial_dir = os.getcwd()
        filename = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")],initialdir=initial_dir)
        if filename:
            self.character.load_from_file(filename)
            self.update_character_display()

    def save_character(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            self.character.save_to_file(filename)
            messagebox.showinfo("Succes", "Karakter gemt!")

    def update_character_display(self):
        # Update the EP label to reflect the remaining EP
        self.ep_label.config(text=f"EP tilbage: {self.character.remaining_ep()}")

        # Load the standard abilities and refresh the buttons
        self.ability_manager = AbilityManager(self.character, self.root, "Filer/standardevner.json", self.ep_label, self)
        
        # Ensure that any abilities the character already has are properly used to unlock menus
        for ability_id in self.character.abilities:
            self.ability_manager.check_menu_unlocks(ability_id)

    def update_class_info(self, class_name):
        # Load the appropriate ability file based on the class
        if class_name == "Paladin":
            total_tro = 0  # Start with 0
        
            # Load the paladin abilities from Filer/paladin.json
            ability_file = "Filer/paladin.json"
            ability_data = self.ability_manager.load_abilities(ability_file)
            
            # Iterate through character abilities
            for ability_id in self.character.abilities:
                
                # Check for abilities with "paladin_spell" in their ID
                if "paladin_spell" in ability_id:
                    # Find the corresponding ability in Filer/paladin.json
                    spell = next((a for a in ability_data if a['id'] == ability_id), None)
                    if spell and 'grade' in spell:
                        total_tro += spell['grade'] * 3
        elif class_name == "Priest":
            total_gudetro = 0  # Start with 0
        
            # Load the priest abilities from Filer/præst.json
            ability_file = "Filer/præst.json"
            ability_data = self.ability_manager.load_abilities(ability_file)
            
            # Iterate through character abilities
            for ability_id in self.character.abilities:
                
                # Check for abilities with "priest_spell" in their ID
                if "priest_spell" in ability_id:
                    # Find the corresponding ability in Filer/præst.json
                    spell = next((a for a in ability_data if a['id'] == ability_id), None)
                    if spell and 'grade' in spell:
                        total_gudetro += spell['grade'] * 3

        elif class_name == "Druid":
            ability_file = "Filer/druide.json"
            total_hjerteslag = 2  # Start with 2        
            # Load the druid abilities from Filer/druide.json
            ability_data = self.ability_manager.load_abilities(ability_file)
            
            # Iterate through character abilities
            for ability_id in self.character.abilities:
                
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
        elif class_name == "Witch":
            total_skyggeskaar = 1  # Start with 1
        
            # Load the witch abilities from witch.json
            ability_file = "Filer/heks.json"
            ability_data = self.ability_manager.load_abilities(ability_file)
            
            # Iterate through character abilities
            for ability_id in self.character.abilities:
                
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
        elif class_name == "Wizard":
            # Load the wizard abilities from Filer/trolddom.json
            ability_file = "Filer/trolddom.json"
            ability_data = self.ability_manager.load_abilities(ability_file)

            # Initialize total mana
            total_mana = 0

            # Loop through character abilities
            for ability_id in self.character.abilities:
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
        else:
            ability_file = None


        if ability_file:
            # Load abilities from the corresponding .json file
            ability_data = self.ability_manager.load_abilities(ability_file)

            # Class info logic: Druid as an example
            if class_name == "Druid":
                class_info_text = f"Hjerteslag: {total_hjerteslag}"

            if class_name == "Paladin":
                class_info_text = f"Tro: {total_tro}"
            
            if class_name == "Priest":
                class_info_text = f"Gudetro: {total_gudetro}"

            if class_name == "Witch":
                class_info_text = f"Skyggeskår: {total_skyggeskaar}"

            if class_name == "Wizard":
                class_info_text = f"Mana: {total_mana}"

            # Check if the label for this class exists, and update or create it
            if class_name not in self.class_info_labels:
                # Create a new label for the class and pack it below the EP label
                self.class_info_labels[class_name] = tk.Label(self.main_menu_frame, text=class_info_text)
                self.class_info_labels[class_name].pack(side="top", pady=5)
            else:
                # If the label exists, just update the text
                self.class_info_labels[class_name].config(text=class_info_text)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Karakterhåndtering")
    app = CharacterApp(root)
    root.mainloop()
