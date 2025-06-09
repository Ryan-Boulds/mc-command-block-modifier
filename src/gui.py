import logging
import tkinter as tk
from tkinter import ttk
import re
import os
import json
from src.command_processor import CommandProcessor
from src.settings import load_settings, save_settings

class CommandModifierGUI:
    def __init__(self, command_processor: CommandProcessor):
        self.root = tk.Tk()
        self.root.title("Minecraft Command Modifier")
        self.root.configure(bg='#f0f0f0')
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.command_processor = command_processor
        self.settings = load_settings()  # Load settings
        self.always_on_top = tk.BooleanVar(value=self.settings.get("always_on_top", False))
        self.is_destroyed = False  # Flag to track destruction
        self.setup_gui()
        self.toggle_always_on_top()
        logging.info("Application started. Copy a command, press F12 to process.")
        self.print_to_text("Application started. Copy a command, press F12 to process.\n")

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both")

        self.command_frame = ttk.Frame(self.notebook)
        self.set_coord_frame = ttk.Frame(self.notebook)
        self.change_block_frame = ttk.Frame(self.notebook)
        self.generate_laser_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.command_frame, text="Command Modifier")
        self.notebook.add(self.set_coord_frame, text="Set Coordinates")
        self.notebook.add(self.change_block_frame, text="Change Block")
        self.notebook.add(self.generate_laser_frame, text="Generate Laser")
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
        self.block_text = tk.StringVar(value="minecraft:lime_concrete")
        self.origin_x = tk.StringVar(value="")
        self.origin_y = tk.StringVar(value="")
        self.origin_z = tk.StringVar(value="")
        self.target_x = tk.StringVar(value="")
        self.target_y = tk.StringVar(value="")
        self.target_z = tk.StringVar(value="")

        self.create_modifier_gui(self.command_frame, [self.pos_x_offset, self.pos_y_offset, self.pos_z_offset], [self.target_x_offset, self.target_y_offset, self.target_z_offset], "Command")
        self.create_modifier_gui(self.set_coord_frame, [self.pos_x_set, self.pos_y_set, self.pos_z_set], [self.target_x_set, self.target_y_set, self.target_z_set], "Set")
        self.create_change_block_gui()
        self.create_generate_laser_gui()
        self.create_settings_gui()
        self.create_terminal_gui()

    def create_modifier_gui(self, frame, pos_vars, target_vars, title_prefix):
        frame.columnconfigure(4, weight=1)
        tk.Label(frame, text=f"{title_prefix} Modifier", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")
        tk.Label(frame, text="Position Modifiers", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, columnspan=4, pady=5, sticky="w", padx=10)

        for i, (label, var) in enumerate([("X:", pos_vars[0]), ("Y:", pos_vars[1]), ("Z:", pos_vars[2])]):
            tk.Label(frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+2, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+2, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda v=var: self.adjust_offset(v, 1), font=("Arial", 8), width=3).grid(row=i+2, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda v=var: self.adjust_offset(v, -1), font=("Arial", 8), width=3).grid(row=i+2, column=3, padx=5, pady=5, sticky="w")

        tk.Label(frame, text="BeamTarget Modifiers (summon only)", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=5, column=0, columnspan=4, pady=5, sticky="w", padx=10)

        for i, (label, var) in enumerate([("X:", target_vars[0]), ("Y:", target_vars[1]), ("Z:", target_vars[2])]):
            tk.Label(frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+6, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+6, column=1, padx=5, pady=5, sticky="w")
            if title_prefix == "Command":
                tk.Button(frame, text="▲", command=lambda v=var: self.adjust_offset(v, 1), font=("Arial", 8), width=3).grid(row=i+6, column=2, padx=5, pady=5, sticky="w")
                tk.Button(frame, text="▼", command=lambda v=var: self.adjust_offset(v, -1), font=("Arial", 8), width=3).grid(row=i+6, column=3, padx=5, pady=5, sticky="w")

    def create_change_block_gui(self):
        tk.Label(self.change_block_frame, text="Change Block Modifier", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
        tk.Label(self.change_block_frame, text="New Block Text:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, pady=5, sticky="e", padx=10)
        tk.Entry(self.change_block_frame, textvariable=self.block_text, width=30, bg='#ffffff', font=("Arial", 10)).grid(row=1, column=1, pady=5, sticky="w", padx=10)

    def create_generate_laser_gui(self):
        tk.Label(self.generate_laser_frame, text="Generate Laser", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=4, pady=10, sticky="ew")
        tk.Label(self.generate_laser_frame, text="Origin:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, columnspan=4, pady=5, sticky="w", padx=10)

        for i, (label, var) in enumerate([("X:", self.origin_x), ("Y:", self.origin_y), ("Z:", self.origin_z)]):
            tk.Label(self.generate_laser_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+2, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(self.generate_laser_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.generate_laser_frame, text="Target:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=5, column=0, columnspan=4, pady=5, sticky="w", padx=10)

        for i, (label, var) in enumerate([("X:", self.target_x), ("Y:", self.target_y), ("Z:", self.target_z)]):
            tk.Label(self.generate_laser_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+6, column=0, padx=5, pady=5, sticky="e")
            tk.Entry(self.generate_laser_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+6, column=1, padx=5, pady=5, sticky="w")

        tk.Button(self.generate_laser_frame, text="Spawn Laser", command=lambda: self.copy_to_clipboard(f"summon end_crystal {self.origin_x.get()} {self.origin_y.get()} {self.origin_z.get()} {{ShowBottom:0b,Invulnerable:1b,Tags:[\"laser\"],BeamTarget:{{X:{self.target_x.get()},Y:{self.target_y.get()},Z:{self.target_z.get()}}}}}"), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=9, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        tk.Button(self.generate_laser_frame, text="Despawn Laser", command=lambda: self.copy_to_clipboard(f"kill @e[type=end_crystal,tag=laser,distance=..2,x={self.origin_x.get()},y={self.origin_y.get()},z={self.origin_z.get()}]"), font=("Arial", 10), bg='#f44336', fg='#ffffff').grid(row=9, column=2, columnspan=2, pady=10, padx=5, sticky="ew")
        self.generate_laser_frame.bind('<Control-v>', lambda e: self.paste_from_clipboard())

    def create_settings_gui(self):
        tk.Checkbutton(self.settings_frame, text="Always Remains on Top", variable=self.always_on_top, command=self.toggle_always_on_top, bg='#f0f0f0', font=("Arial", 10)).grid(row=0, column=0, pady=5, padx=10, sticky="w")

    def create_terminal_gui(self):
        tk.Label(self.main_frame, text="Terminal Output", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').pack(pady=5, fill="x", padx=10)
        self.terminal_text = tk.Text(self.main_frame, height=5, font=("Courier", 10), bg='#000000', fg='#ffffff', insertbackground='#ffffff', relief='flat', borderwidth=2, state='disabled', wrap='none')
        self.terminal_text.pack(expand=True, fill="both", padx=10, pady=5)
        v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.terminal_text.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.terminal_text['yscrollcommand'] = v_scrollbar.set
        h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.terminal_text.xview)
        h_scrollbar.pack(fill="x")
        self.terminal_text['xscrollcommand'] = h_scrollbar.set
        self.terminal_text.tag_configure("command", foreground="#ffffff")
        self.terminal_text.tag_configure("object", foreground="#55aaff")
        self.terminal_text.tag_configure("coord", foreground="#ba42ff")
        self.terminal_text.tag_configure("modified_coord", foreground="#00ff00")
        self.terminal_text.tag_configure("normal", foreground="#ffffff")
        self.terminal_text.tag_configure("block_changed", foreground="#00ff00")
        self.terminal_text.tag_configure("block_unchanged", foreground="#ffffff")
        tk.Label(self.main_frame, text="Copy a command, press F12 to process.", font=("Normal", 10), bg='#f0f0f0', fg='#555555').pack(pady=10, fill="x", padx=10)

    def print_to_text(self, message, tags="normal"):
        self.terminal_text.configure(state='normal')
        self.terminal_text.insert(tk.END, message + '\n', tags)
        self.terminal_text.configure(state='disabled')
        self.terminal_text.see(tk.END)

    def adjust_offset(self, offset_var, change):
        try:
            current = int(offset_var.get())
            offset_var.set(str(current + change))
        except ValueError:
            offset_var.set("0")

    def toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())
        self.settings["always_on_top"] = self.always_on_top.get()
        save_settings(self.settings)
        logging.info(f"Always on top set to {self.always_on_top.get()}")

    def on_closing(self):
        if not self.is_destroyed:  # Prevent multiple destroy calls
            self.settings["always_on_top"] = self.always_on_top.get()
            save_settings(self.settings)
            self.root.destroy()
            self.is_destroyed = True

    def show_window(self):
        self.root.deiconify()

    def show_settings(self):
        self.root.deiconify()
        self.notebook.select(self.settings_frame)

    def copy_to_clipboard(self, command):
        import pyperclip
        pyperclip.copy(command)
        self.print_to_text(f"Copied to clipboard: {command}", "normal")

    def process_command(self, command):
        active_tab = self.notebook.tab(self.notebook.select(), "text")
        use_set = active_tab == "Set Coordinates"

        pos_x_var = self.pos_x_set if use_set else self.pos_x_offset
        pos_y_var = self.pos_y_set if use_set else self.pos_y_offset
        pos_z_var = self.pos_z_set if use_set else self.pos_z_offset
        target_x_var = self.target_x_set if use_set else self.target_x_offset
        target_y_var = self.target_y_set if use_set else self.target_y_offset
        target_z_var = self.target_z_set if use_set else self.target_z_offset

        modified_command, original_coords, original_block = self.command_processor.modify_coordinates(
            command, use_set, pos_x_var, pos_y_var, pos_z_var, target_x_var, target_y_var, target_z_var, self.block_text
        )

        self.print_to_text(f"Input Command: {command}", "command")
        if original_coords:
            self.print_to_text(f"Original Coordinates: {original_coords}", "coord")
        if original_block:
            self.print_to_text(f"Original Block: {original_block}", "block_unchanged")
        self.print_to_text(f"Modified Command: {modified_command}", "command")
        if original_coords:
            new_coords = [int(x) for x in re.findall(r'-?\d+\b', modified_command) if x.lstrip('-').isdigit()]
            self.print_to_text(f"New Coordinates: {new_coords}", "modified_coord")
        if original_block and self.block_text.get() != original_block:
            self.print_to_text(f"New Block: {self.block_text.get()}", "block_changed")

        import pyperclip
        pyperclip.copy(modified_command)
        self.print_to_text("Command copied to clipboard.", "normal")

    def paste_from_clipboard(self):
        import pyperclip
        clipboard_content = pyperclip.paste().strip()
        if clipboard_content:
            coords = re.findall(r'-?\d+', clipboard_content)
            if len(coords) >= 3:
                self.origin_x.set(coords[0])
                self.origin_y.set(coords[1])
                self.origin_z.set(coords[2])
            self.print_to_text(f"Pasted from clipboard: {clipboard_content} (filled Origin fields)", "normal")

    def run(self):
        self.root.mainloop()