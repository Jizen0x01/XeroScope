import os
from pathlib import Path
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox, StringVar, OptionMenu
import configparser
import xml.etree.ElementTree as ET
import json

class XeroScopeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("XeroScope")
        self.geometry("235x220")

        # Lock resizing of the frame
        self.resizable(False, False)

        icon_path = "assets/icon.ico"  # Path to your icon file
        if os.path.exists(icon_path):
            self.iconbitmap(default=icon_path)

        self.xero_folder_path = self.find_xero_folder()
        if not self.xero_folder_path:
            messagebox.showerror("Error", "Xero folder not found. Please make sure Xero is installed.")
            self.destroy()
        else:
            self.selected_weapon = StringVar(self)
            self.selected_weapon.set("Select Weapon")
            self.selected_crosshair = StringVar(self)
            self.selected_crosshair.set("")
            self.create_widgets()

        self.changed_crosshairs = {}

    def save_config(self, xero_folder):
        # Save the configuration to the config.ini file
        config = configparser.ConfigParser()
        config["Settings"] = {"XeroFolderPath": str(xero_folder)}
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def find_xero_folder(self):
        home_dir = Path(os.path.expanduser("~"))
        for root, dirs, files in os.walk(home_dir):
            if "Xero" in dirs:
                xero_folder = Path(root) / "Xero"
                if (xero_folder / "crosshairs").exists() and (xero_folder / "xml").exists():
                    self.save_config(xero_folder)
                    return xero_folder
        return None

    def select_crosshair(self):
        weapon_id = self.selected_weapon.get().split(" - ")[0]  # Extract weapon ID
        if weapon_id == "Select Weapon":
            messagebox.showerror("Error", "Please select a weapon.")
            return

        crosshair_file = filedialog.askopenfilename(title="Select Crosshair Image",
                                                     filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.dds")])
        if crosshair_file:
            # Copy the crosshair image to the Xero crosshairs folder
            crosshair_ext = os.path.splitext(crosshair_file)[1]
            crosshair_dest = self.xero_folder_path / "crosshairs" / f"{weapon_id}{crosshair_ext}"
            shutil.copyfile(crosshair_file, crosshair_dest)
            # Update the selected crosshair variable
            self.selected_crosshair.set(f"{weapon_id}{crosshair_ext}")

    def update_crosshair(self):
        weapon_id = self.selected_weapon.get().split(" - ")[0]  # Extract weapon ID
        if weapon_id == "Select Weapon":
            messagebox.showerror("Error", "Please select a weapon.")
            return

        crosshair_path = self.selected_crosshair.get()
        if not crosshair_path:
            messagebox.showerror("Error", "Please select a crosshair.")
            return

        # Update the crosshair path in the crosshairs.xml file
        crosshair_xml_path = self.xero_folder_path / "xml" / "crosshairs.xml"
        if not os.path.exists(crosshair_xml_path):
            messagebox.showerror("Error", "Crosshairs XML file not found.")
            return

        tree = ET.parse(crosshair_xml_path)
        root = tree.getroot()

        for crosshair in root.findall(".//crosshair"):
            if crosshair.attrib.get("id") == weapon_id:
                crosshair.set("path", crosshair_path)
                break

        tree.write(crosshair_xml_path)

        messagebox.showinfo("Success", "Crosshair updated successfully.")

    def reset_to_default(self):
        default_xml_path = Path("default") / "crosshairs.xml"
        if not default_xml_path.exists():
            messagebox.showerror("Error", "Default XML file not found.")
            return

        xero_xml_path = self.xero_folder_path / "xml" / "crosshairs.xml"
        shutil.copyfile(default_xml_path, xero_xml_path)
        messagebox.showinfo("Success", "Reset to default successful.")

    def fix_plasma(self):
        fixed_xml_path = Path("fixed") / "crosshairs.xml"
        if not fixed_xml_path.exists():
            messagebox.showerror("Error", "Fixed XML file not found.")
            return

        xero_xml_path = self.xero_folder_path / "xml" / "crosshairs.xml"
        shutil.copyfile(fixed_xml_path, xero_xml_path)
        messagebox.showinfo("Success", "Fixed Plasma successful.")

    def create_widgets(self):
        # Add widgets here
        crosshairs_xml_path = self.xero_folder_path / "xml" / "crosshairs.xml"
        if not os.path.exists(crosshairs_xml_path):
            messagebox.showerror("Error", "Crosshairs XML file not found.")
            self.destroy()
            return

        # Parse crosshairs XML file to extract weapon IDs and paths
        weapons = {}
        tree = ET.parse(crosshairs_xml_path)
        root = tree.getroot()
        for crosshair in root.findall("crosshair"):
            weapon_id = crosshair.attrib.get("id")
            path = crosshair.attrib.get("path")
            weapons[weapon_id] = path

        # Read weapon names from JSON file
        weapon_names = {}
        with open("weapons.json", "r") as file:
            weapons_data = json.load(file)
            weapon_names = {weapon_id: name for weapon_id, name in weapons_data.items()}

        # Combo box to select weapons
        weapons_menu = ctk.CTkComboBox(self, variable=self.selected_weapon,
                                        values=[f"{weapon_id} - {weapon_names[weapon_id]}" for weapon_id in weapons.keys()])
        weapons_menu.pack(pady=10)

        # Button to select crosshair
        select_button = ctk.CTkButton(self, text="Select Crosshair", command=self.select_crosshair)
        select_button.pack(pady=5)

        # Button to update crosshair
        update_button = ctk.CTkButton(self, text="Update Crosshair", command=self.update_crosshair)
        update_button.pack(pady=5)

        # Button to reset to default
        reset_button = ctk.CTkButton(self, text="Reset to Default", command=self.reset_to_default)
        reset_button.pack(pady=5)

        # Button to fix plasma
        fix_plasma_button = ctk.CTkButton(self, text="Fix Plasma", command=self.fix_plasma)
        fix_plasma_button.pack(pady=5)

if __name__ == "__main__":
    app = XeroScopeApp()
    app.mainloop()

