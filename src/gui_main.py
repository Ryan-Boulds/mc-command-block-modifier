# Updated on 02:14 PM CDT, Friday, June 13, 2025
import logging
import tkinter as tk
from tkinter import ttk
from src.gui_tabs import create_modifier_gui, create_change_block_gui, create_generate_laser_gui, create_generate_end_beam_gui, create_settings_gui, create_terminal_gui, create_rename_tag_gui
from src.gui_utils import adjust_offset, toggle_always_on_top, start_record_keybind, record_keybind, update_keybind_notes, process_clipboard, process_command, generate_laser_initial_commands, generate_laser_rotation_commands, generate_end_beam_commands, autofill_coordinates, toggle_terminal, print_to_text, on_closing, show_window, show_settings, copy_to_clipboard
from src.command_processor import CommandProcessor
from src.settings import load_settings, save_settings

class CommandModifierGUI:
    def __init__(self, command_processor: CommandProcessor):
        self.root = tk.Tk()
        self.root.title("Minecraft Command Modifier")
        self.root.configure(bg='#f0f0f0')
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.command_processor = command_processor
        self.settings = load_settings()
        self.always_on_top = tk.BooleanVar(value=self.settings.get("always_on_top", False))
        self.key_bind = tk.StringVar(value=self.settings.get("key_bind", "F12"))
        self.is_recording_key = False
        self.is_destroyed = False
        self.terminal_visible = False  # Hidden by default
        self.setup_gui()
        self.toggle_always_on_top()
        self.root.bind(self.key_bind.get(), lambda e: self.process_clipboard())
        logging.info("Application started. Copy a command, press %s to process.", self.key_bind.get())
        self.print_to_text(f"Application started. Copy a command, press {self.key_bind.get()} to process.\n")

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.set_coord_frame = ttk.Frame(self.notebook)
        self.command_frame = ttk.Frame(self.notebook)
        self.change_block_frame = ttk.Frame(self.notebook)
        self.generate_laser_frame = ttk.Frame(self.notebook)
        self.rename_tag_frame = ttk.Frame(self.notebook)
        self.generate_end_beam_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.set_coord_frame, text="Set Coordinates")
        self.notebook.add(self.command_frame, text="Command Modifier")
        self.notebook.add(self.change_block_frame, text="Change Block")
        self.notebook.add(self.generate_laser_frame, text="Generate Laser")
        self.notebook.add(self.rename_tag_frame, text="Rename tag/group")
        self.notebook.add(self.generate_end_beam_frame, text="Generate End Beam")
        self.notebook.add(self.settings_frame, text="Settings")

        self.pos_x_offset = tk.StringVar(value="0")
        self.pos_y_offset = tk.StringVar(value="0")
        self.pos_z_offset = tk.StringVar(value="0")
        self.target_x_offset = tk.StringVar(value="0")
        self.target_y_offset = tk.StringVar(value="0")
        self.target_z_offset = tk.StringVar(value="0")
        self.pos_x_set = tk.StringVar(value="0")
        self.pos_y_set = tk.StringVar(value="0")
        self.pos_z_set = tk.StringVar(value="0")
        self.target_x_set = tk.StringVar(value="0")
        self.target_y_set = tk.StringVar(value="0")
        self.target_z_set = tk.StringVar(value="0")
        self.block_text = tk.StringVar(value="minecraft:lime_concrete")  # Default value
        self.tag_text = tk.StringVar(value="beam1")  # Default value for new tag
        self.origin_x = tk.StringVar(value="0")  # Autofilled with 0
        self.origin_y = tk.StringVar(value="0")  # Autofilled with 0
        self.origin_z = tk.StringVar(value="0")  # Autofilled with 0
        self.target_x = tk.StringVar(value="0")  # Autofilled with 0
        self.target_y = tk.StringVar(value="0")  # Autofilled with 0
        self.target_z = tk.StringVar(value="0")  # Autofilled with 0
        self.laser_x = tk.StringVar(value="0")
        self.laser_y = tk.StringVar(value="0")
        self.laser_z = tk.StringVar(value="0")
        self.laser_tag = tk.StringVar(value="beam1")
        self.laser_block = tk.StringVar(value="minecraft:lime_concrete")  # Updated to match default
        self.laser_length = tk.StringVar(value="-100")  # Renamed from Z-Scale
        self.laser_rot_x = tk.StringVar(value="0")
        self.laser_rot_y = tk.StringVar(value="1")

        create_modifier_gui(self.command_frame, [self.pos_x_offset, self.pos_y_offset, self.pos_z_offset], [self.target_x_offset, self.target_y_offset, self.target_z_offset], "Command", self)
        create_modifier_gui(self.set_coord_frame, [self.pos_x_set, self.pos_y_set, self.pos_z_set], [self.target_x_set, self.target_y_set, self.target_z_set], "Set", self)
        create_change_block_gui(self.change_block_frame, self)
        create_generate_laser_gui(self.generate_laser_frame, self)
        create_rename_tag_gui(self.rename_tag_frame, self)
        create_generate_end_beam_gui(self.generate_end_beam_frame, self)
        create_settings_gui(self.settings_frame, self)
        create_terminal_gui(self.main_frame, self)

    def on_tab_change(self, event):
        active_tab = self.notebook.tab(self.notebook.select(), "text")
        if active_tab == "Command Modifier":
            self.terminal_text.config(height=3)
        elif active_tab == "Set Coordinates":
            self.terminal_text.config(height=3)
        elif active_tab == "Change Block":
            self.terminal_text.config(height=3)
        elif active_tab == "Generate Laser":
            self.terminal_text.config(height=2)
        elif active_tab == "Generate End Beam":
            self.terminal_text.config(height=2)
        elif active_tab == "Settings":
            self.terminal_text.config(height=4)
        # Add case for Rename tag/group if needed
        elif active_tab == "Rename tag/group":
            self.terminal_text.config(height=3)

    def adjust_offset(self, offset_var, change):
        return adjust_offset(offset_var, change)

    def toggle_always_on_top(self):
        return toggle_always_on_top(self)

    def start_record_keybind(self):
        return start_record_keybind(self)

    def record_keybind(self, event):
        return record_keybind(self, event)

    def update_keybind_notes(self):
        return update_keybind_notes(self)

    def on_closing(self):
        return on_closing(self)

    def show_window(self):
        return show_window(self)

    def show_settings(self):
        return show_settings(self)

    def copy_to_clipboard(self, command):
        return copy_to_clipboard(self, command)

    def process_clipboard(self):
        return process_clipboard(self)

    def process_command(self, command):
        return process_command(self, command)

    def generate_laser_initial_commands(self):
        return generate_laser_initial_commands(self)

    def generate_laser_rotation_commands(self):
        return generate_laser_rotation_commands(self)

    def generate_end_beam_commands(self):
        return generate_end_beam_commands(self)

    def autofill_coordinates(self, vars_list):
        return autofill_coordinates(self, vars_list)

    def toggle_terminal(self):
        return toggle_terminal(self)

    def print_to_text(self, message, tags="normal"):
        return print_to_text(self, message, tags)

    def run(self):
        self.root.mainloop()