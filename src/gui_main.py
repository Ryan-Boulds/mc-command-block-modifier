# Updated on 09:40 PM CDT, Monday, July 07, 2025
import tkinter as tk
from tkinter import ttk
import logging
from src.gui_tabs import create_modifier_gui, create_change_block_gui, create_generate_laser_gui, create_generate_end_beam_gui, create_settings_gui, create_terminal_gui, create_rename_tag_gui
from src.gui_utils import adjust_offset, toggle_always_on_top, start_record_keybind, record_keybind, process_clipboard, toggle_terminal, print_to_text, on_closing, show_window, show_settings, copy_to_clipboard
from src.clipboard_parser import ClipboardCoordinateParser
from src.command_modifier import process_command, set_laser_preset, set_lightbeam_preset
from src.settings import load_settings, save_settings

class CommandModifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Command Modifier")
        self.root.geometry("600x400")
        self.is_destroyed = False
        self.is_recording_key = False
        self.terminal_visible = False
        self.settings = load_settings()

        # Initialize variables
        self.pos_vars = [tk.StringVar(value="0") for _ in range(3)]
        self.target_vars = [tk.StringVar(value="0") for _ in range(3)]
        self.laser_x = tk.StringVar(value="0")
        self.laser_y = tk.StringVar(value="0")
        self.laser_z = tk.StringVar(value="0")
        self.laser_tag = tk.StringVar(value="beam1")
        self.laser_block = tk.StringVar(value="minecraft:lime_concrete")
        self.laser_length = tk.StringVar(value="-150.0")
        self.laser_rot_x = tk.StringVar(value="0")
        self.laser_rot_y = tk.StringVar(value="1")
        self.origin_x = tk.StringVar(value="0")
        self.origin_y = tk.StringVar(value="0")
        self.origin_z = tk.StringVar(value="0")
        self.target_x = tk.StringVar(value="0")
        self.target_y = tk.StringVar(value="0")
        self.target_z = tk.StringVar(value="0")
        self.always_on_top = tk.BooleanVar(value=self.settings.get("always_on_top", False))
        self.key_bind = tk.StringVar(value=self.settings.get("key_bind", ""))
        self.block_text = tk.StringVar(value="minecraft:lime_concrete")
        self.modify_coords = tk.BooleanVar(value=True)
        self.modify_translation = tk.BooleanVar(value=True)
        self.modify_scale = tk.BooleanVar(value=True)
        self.modify_centering = tk.BooleanVar(value=True)
        self.laser_mode = tk.StringVar(value="")
        self.pos_x_set = tk.StringVar(value="0.0")
        self.pos_y_set = tk.StringVar(value="0.5")
        self.pos_z_set = tk.StringVar(value="0.999999")
        self.trans_x = tk.StringVar(value="0.5")
        self.trans_y = tk.StringVar(value="0.0")
        self.trans_z = tk.StringVar(value="0.0")
        self.beam_scale = tk.StringVar(value="-150.0")
        self.centering_x = tk.StringVar(value="0.0")
        self.centering_y = tk.StringVar(value="0.0")
        self.centering_z = tk.StringVar(value="0.0")
        self.tag_text = tk.StringVar(value="beam1")

        # Create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Create frames
        self.command_frame = ttk.Frame(self.notebook)
        self.set_frame = ttk.Frame(self.notebook)
        self.change_block_frame = ttk.Frame(self.notebook)
        self.generate_laser_frame = ttk.Frame(self.notebook)
        self.generate_end_beam_frame = ttk.Frame(self.notebook)
        self.rename_tag_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.terminal_frame = ttk.Frame(self.root)

        # Add tabs
        self.notebook.add(self.command_frame, text="Modify Laser")
        self.notebook.add(self.set_frame, text="Set Coordinates")
        self.notebook.add(self.change_block_frame, text="Change Block")
        self.notebook.add(self.generate_laser_frame, text="Generate Laser")
        self.notebook.add(self.generate_end_beam_frame, text="Generate End Beam")
        self.notebook.add(self.rename_tag_frame, text="Rename Tag/Group")
        self.notebook.add(self.settings_frame, text="Settings")

        # Create GUIs
        create_modifier_gui(self.command_frame, self.pos_vars, self.target_vars, "Command", self)
        create_modifier_gui(self.set_frame, self.pos_vars, self.target_vars, "Set", self)
        create_change_block_gui(self.change_block_frame, self)
        create_generate_laser_gui(self.generate_laser_frame, self)
        create_generate_end_beam_gui(self.generate_end_beam_frame, self)
        create_rename_tag_gui(self.rename_tag_frame, self)
        create_settings_gui(self.settings_frame, self)
        create_terminal_gui(self.terminal_frame, self)

        # Initialize clipboard parser after GUI setup
        self.clipboard_parser = ClipboardCoordinateParser(self)

        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))

        # Apply always on top setting
        toggle_always_on_top(self)

        # Bind key if exists
        if self.key_bind.get():
            self.root.bind(self.key_bind.get(), lambda e: process_clipboard(self))

    def adjust_offset(self, offset_var, change):
        adjust_offset(offset_var, change)

    def toggle_always_on_top(self):
        toggle_always_on_top(self)

    def start_record_keybind(self):
        start_record_keybind(self)

    def record_keybind(self, event):
        record_keybind(self, event)

    def process_clipboard(self):
        process_clipboard(self)

    def generate_laser_initial_commands(self):
        from src.gui_utils import generate_laser_initial_commands
        generate_laser_initial_commands(self)

    def generate_laser_rotation_commands(self):
        from src.gui_utils import generate_laser_rotation_commands
        generate_laser_rotation_commands(self)

    def generate_end_beam_commands(self):
        from src.gui_utils import generate_end_beam_commands
        generate_end_beam_commands(self)

    def toggle_terminal(self):
        toggle_terminal(self)

    def print_to_text(self, message, tags="normal"):
        print_to_text(self, message, tags)

    def copy_to_clipboard(self, command):
        copy_to_clipboard(self, command)

    def process_command(self, command):
        return process_command(self, command)  # Call process_command from command_modifier.py

    def on_closing(self):
        on_closing(self)

    def show_window(self):
        show_window(self)

    def show_settings(self):
        show_settings(self)