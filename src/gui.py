# Updated on 01:40 AM CDT, Friday, June 13, 2025
import logging
import tkinter as tk
from tkinter import ttk
import re
import os
import json
from src.command_processor import CommandProcessor
from src.settings import load_settings, save_settings
from src.viewer3d import Block3DViewer

class CommandModifierGUI:
    def __init__(self, command_processor: CommandProcessor):
        self.root = tk.Tk()
        self.root.title("Minecraft Command Modifier")
        self.root.configure(bg='#f0f0f0')
        self.root.geometry("600x700")
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
        self.generate_end_beam_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.set_coord_frame, text="Set Coordinates")
        self.notebook.add(self.command_frame, text="Command Modifier")
        self.notebook.add(self.change_block_frame, text="Change Block")
        self.notebook.add(self.generate_laser_frame, text="Generate Laser")
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

        self.create_modifier_gui(self.command_frame, [self.pos_x_offset, self.pos_y_offset, self.pos_z_offset], [self.target_x_offset, self.target_y_offset, self.target_z_offset], "Command")
        self.create_modifier_gui(self.set_coord_frame, [self.pos_x_set, self.pos_y_set, self.pos_z_set], [self.target_x_set, self.target_y_set, self.target_z_set], "Set")
        self.create_change_block_gui()
        self.create_generate_laser_gui()
        self.create_generate_end_beam_gui()
        self.create_settings_gui()
        self.create_terminal_gui()

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

    def create_modifier_gui(self, frame, pos_vars, target_vars, title_prefix):
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        tk.Label(scrollable_frame, text=f"{title_prefix} Modifier", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=5, pady=5, sticky="w")
        tk.Label(scrollable_frame, text="Position Move", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, columnspan=5, pady=2, sticky="w")
        for i, (label, var) in enumerate([("X:", pos_vars[0]), ("Y:", pos_vars[1]), ("Z:", pos_vars[2])]):
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+2, column=0, pady=0, sticky="w")
            tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+2, column=1, pady=0, sticky="w")
            tk.Button(scrollable_frame, text="▲", command=lambda v=var: self.adjust_offset(v, 1), font=("Arial", 8), width=2).grid(row=i+2, column=2, pady=0, sticky="w")
            tk.Button(scrollable_frame, text="▼", command=lambda v=var: self.adjust_offset(v, -1), font=("Arial", 8), width=2).grid(row=i+2, column=3, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: self.autofill_coordinates([pos_vars[0], pos_vars[1], pos_vars[2]]), font=("Arial", 8)).grid(row=5, column=0, columnspan=5, pady=2, sticky="w")

        tk.Label(scrollable_frame, text="BeamTarget Mover (summon only)", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=6, column=0, columnspan=5, pady=2, sticky="w")
        for i, (label, var) in enumerate([("X:", target_vars[0]), ("Y:", target_vars[1]), ("Z:", target_vars[2])]):
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+7, column=0, pady=0, sticky="w")
            tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+7, column=1, pady=0, sticky="w")
            tk.Button(scrollable_frame, text="▲", command=lambda v=var: self.adjust_offset(v, 1), font=("Arial", 8), width=2).grid(row=i+7, column=2, pady=0, sticky="w")
            tk.Button(scrollable_frame, text="▼", command=lambda v=var: self.adjust_offset(v, -1), font=("Arial", 8), width=2).grid(row=i+7, column=3, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: self.autofill_coordinates([target_vars[0], target_vars[1], target_vars[2]]), font=("Arial", 8)).grid(row=10, column=0, columnspan=5, pady=2, sticky="w")

        if title_prefix == "Command":
            self.cmd_text_cmd = tk.Text(scrollable_frame, height=2, width=40)
            self.cmd_text_cmd.grid(row=11, column=0, columnspan=4, pady=2, sticky="w")
            tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.cmd_text_cmd.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=11, column=4, pady=2, sticky="w")
        elif title_prefix == "Set":
            self.cmd_text_set = tk.Text(scrollable_frame, height=2, width=40)
            self.cmd_text_set.grid(row=11, column=0, columnspan=4, pady=2, sticky="w")
            tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.cmd_text_set.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=11, column=4, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="Generate", command=lambda: self.process_clipboard(), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=12, column=0, columnspan=5, pady=5, sticky="w")
        tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=13, column=0, columnspan=5, pady=2, sticky="w")

    def create_change_block_gui(self):
        canvas = tk.Canvas(self.change_block_frame)
        scrollbar = ttk.Scrollbar(self.change_block_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.change_block_frame.columnconfigure(0, weight=1)
        self.change_block_frame.rowconfigure(0, weight=1)

        tk.Label(scrollable_frame, text="Change Block Modifier", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
        tk.Label(scrollable_frame, text="New Block Text:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, pady=0, sticky="w")
        tk.Entry(scrollable_frame, textvariable=self.block_text, width=30, bg='#ffffff', font=("Arial", 10)).grid(row=2, column=0, columnspan=2, pady=0, sticky="w")

        tk.Button(scrollable_frame, text="Generate", command=lambda: self.process_clipboard(), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=3, column=0, columnspan=3, pady=5, sticky="w")

        self.change_block_cmd_text = tk.Text(scrollable_frame, height=2, width=40)
        self.change_block_cmd_text.grid(row=4, column=0, columnspan=2, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.change_block_cmd_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=4, column=2, pady=2, sticky="w")
        tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=5, column=0, columnspan=3, pady=2, sticky="w")

    def create_generate_laser_gui(self):
        canvas = tk.Canvas(self.generate_laser_frame)
        scrollbar = ttk.Scrollbar(self.generate_laser_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.generate_laser_frame.columnconfigure(0, weight=1)
        self.generate_laser_frame.rowconfigure(0, weight=1)

        tk.Label(scrollable_frame, text="Generate Laser", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
        for i, (label, var) in enumerate([("X Coordinate:", self.laser_x), ("Y Coordinate:", self.laser_y), ("Z Coordinate:", self.laser_z), ("Tag/Group Name:", self.laser_tag), ("Block Type:", self.laser_block), ("Length:", self.laser_length)]):
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+1, column=0, pady=0, sticky="w")
            tk.Entry(scrollable_frame, textvariable=var, width=20 if i == 4 else 10, bg='#ffffff', font=("Arial", 10)).grid(row=i+1, column=1, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: self.autofill_coordinates([self.laser_x, self.laser_y, self.laser_z]), font=("Arial", 8)).grid(row=7, column=0, columnspan=3, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="Generate", command=self.generate_laser_initial_commands, font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=8, column=0, columnspan=3, pady=5, sticky="w")

        tk.Label(scrollable_frame, text="Spawn Command:", font=("Arial", 10), bg='#f0f0f0').grid(row=9, column=0, pady=0, sticky="w")
        self.cmd1_text = tk.Text(scrollable_frame, height=2, width=40)
        self.cmd1_text.grid(row=10, column=0, columnspan=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.cmd1_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=10, column=2, pady=0, sticky="w")

        tk.Label(scrollable_frame, text="Modify Position:", font=("Arial", 10), bg='#f0f0f0').grid(row=11, column=0, pady=0, sticky="w")
        self.cmd2_text = tk.Text(scrollable_frame, height=2, width=40)
        self.cmd2_text.grid(row=12, column=0, columnspan=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.cmd2_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=12, column=2, pady=0, sticky="w")

        self.cmd3_text = tk.Text(scrollable_frame, height=2, width=40)
        self.cmd3_text.grid(row=13, column=0, columnspan=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.cmd3_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=13, column=2, pady=0, sticky="w")

        tk.Label(scrollable_frame, text="Laser Rotation:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=14, column=0, columnspan=3, pady=2, sticky="w")
        for i, (label, var) in enumerate([("X Rotation:", self.laser_rot_x), ("Y Rotation:", self.laser_rot_y)]):
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+15, column=0, pady=0, sticky="w")
            tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+15, column=1, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Generate", command=self.generate_laser_rotation_commands, font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=17, column=0, columnspan=3, pady=5, sticky="w")

        self.cmd4_text = tk.Text(scrollable_frame, height=2, width=40)
        self.cmd4_text.grid(row=18, column=0, columnspan=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.cmd4_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=18, column=2, pady=0, sticky="w")

        tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=19, column=0, columnspan=3, pady=2, sticky="w")

    def create_generate_end_beam_gui(self):
        canvas = tk.Canvas(self.generate_end_beam_frame)
        scrollbar = ttk.Scrollbar(self.generate_end_beam_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.generate_end_beam_frame.columnconfigure(0, weight=1)
        self.generate_end_beam_frame.rowconfigure(0, weight=1)

        tk.Label(scrollable_frame, text="Generate End Beam", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        tk.Label(scrollable_frame, text="Origin:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, columnspan=2, pady=2, sticky="w")
        for i, (label, var) in enumerate([("X:", self.origin_x), ("Y:", self.origin_y), ("Z:", self.origin_z)]):
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+2, column=0, pady=0, sticky="w")
            tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+2, column=1, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: self.autofill_coordinates([self.origin_x, self.origin_y, self.origin_z]), font=("Arial", 8)).grid(row=5, column=0, columnspan=2, pady=2, sticky="w")

        tk.Label(scrollable_frame, text="Target:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=6, column=0, columnspan=2, pady=2, sticky="w")
        for i, (label, var) in enumerate([("X:", self.target_x), ("Y:", self.target_y), ("Z:", self.target_z)]):
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+7, column=0, pady=0, sticky="w")
            tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+7, column=1, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: self.autofill_coordinates([self.target_x, self.target_y, self.target_z]), font=("Arial", 8)).grid(row=10, column=0, columnspan=2, pady=2, sticky="w")

        tk.Button(scrollable_frame, text="Generate", command=self.generate_end_beam_commands, font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=11, column=0, columnspan=3, pady=5, sticky="w")

        tk.Label(scrollable_frame, text="Spawn Command:", font=("Arial", 10), bg='#f0f0f0').grid(row=12, column=0, pady=0, sticky="w")
        self.spawn_text = tk.Text(scrollable_frame, height=2, width=40)
        self.spawn_text.grid(row=13, column=0, columnspan=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.spawn_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=13, column=2, pady=0, sticky="w")

        tk.Label(scrollable_frame, text="Despawn Command:", font=("Arial", 10), bg='#f0f0f0').grid(row=14, column=0, pady=0, sticky="w")
        self.despawn_text = tk.Text(scrollable_frame, height=2, width=40)
        self.despawn_text.grid(row=15, column=0, columnspan=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: self.copy_to_clipboard(self.despawn_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=15, column=2, pady=0, sticky="w")

        tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=16, column=0, columnspan=3, pady=2, sticky="w")

    def create_settings_gui(self):
        canvas = tk.Canvas(self.settings_frame)
        scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.settings_frame.columnconfigure(0, weight=1)
        self.settings_frame.rowconfigure(0, weight=1)

        tk.Checkbutton(scrollable_frame, text="Always Remains on Top", variable=self.always_on_top, command=self.toggle_always_on_top, bg='#f0f0f0', font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")
        tk.Button(scrollable_frame, text="Press key to record keybind", command=self.start_record_keybind, bg='#4CAF50', fg='#ffffff', font=("Arial", 10)).grid(row=1, column=0, pady=5, sticky="w")
        tk.Button(scrollable_frame, text="Generate 3D Model, Work in Progress", command=self.on_closing, state="disabled", bg='#cccccc', fg='#666666', font=("Arial", 10)).grid(row=2, column=0, pady=5, sticky="w")
        tk.Button(scrollable_frame, text="Generate 2D Model, Work in Progress", command=self.on_closing, state="disabled", bg='#cccccc', fg='#666666', font=("Arial", 10)).grid(row=3, column=0, pady=5, sticky="w")

    def create_terminal_gui(self):
        if not hasattr(self, 'terminal_text') or not self.terminal_text.winfo_exists():
            self.terminal_text = tk.Text(self.main_frame, height=3, font=("Courier", 10), bg='#000000', fg='#ffffff', insertbackground='#ffffff', relief='flat', borderwidth=2, state='disabled', wrap='none')
            self.terminal_text.pack_forget()  # Hidden by default
            v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.terminal_text.yview)
            v_scrollbar.pack_forget()
            self.terminal_text['yscrollcommand'] = v_scrollbar.set
            h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.terminal_text.xview)
            h_scrollbar.pack_forget()
            self.terminal_text['xscrollcommand'] = h_scrollbar.set
            self.terminal_text.tag_configure("command", foreground="#ffffff")
            self.terminal_text.tag_configure("object", foreground="#55aaff")
            self.terminal_text.tag_configure("coord", foreground="#ba42ff")
            self.terminal_text.tag_configure("modified_coord", foreground="#00ff00")
            self.terminal_text.tag_configure("normal", foreground="#ffffff")
            self.terminal_text.tag_configure("block_changed", foreground="#00ff00")
            self.terminal_text.tag_configure("block_unchanged", foreground="#ffffff")
            self.terminal_instruction = tk.Label(self.main_frame, text=f"Copy a command, press set keybind to process.", font=("Normal", 10), bg='#f0f0f0', fg='#555555')
            self.terminal_instruction.pack_forget()

        if not hasattr(self, 'terminal_button') or not self.terminal_button.winfo_exists():
            self.terminal_button = tk.Button(self.main_frame, text="Show Terminal", command=self.toggle_terminal, bg='#4CAF50', fg='#ffffff', font=("Arial", 10))
            self.terminal_button.pack(pady=5)

    def toggle_terminal(self):
        if self.terminal_visible:
            self.terminal_text.pack_forget()
            self.terminal_instruction.pack_forget()
            v_scrollbar = [w for w in self.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'vertical'][0]
            v_scrollbar.pack_forget()
            h_scrollbar = [w for w in self.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'horizontal'][0]
            h_scrollbar.pack_forget()
            self.terminal_visible = False
        else:
            self.terminal_text.pack(expand=True, fill="both", padx=10, pady=5)
            v_scrollbar = [w for w in self.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'vertical'][0]
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar = [w for w in self.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'horizontal'][0]
            h_scrollbar.pack(fill="x")
            self.terminal_instruction.pack(pady=10, fill="x", padx=10)
            self.terminal_visible = True
        self.terminal_button.config(text="Show Terminal" if not self.terminal_visible else "Hide Terminal")

    def print_to_text(self, message, tags="normal"):
        if self.terminal_visible and hasattr(self, 'terminal_text') and self.terminal_text.winfo_exists():
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

    def start_record_keybind(self):
        if not self.is_recording_key:
            self.is_recording_key = True
            self.print_to_text("Press any key to record new keybind...", "normal")
            self.root.bind("<Key>", self.record_keybind)
        else:
            self.print_to_text("Already recording a keybind. Please press a key or wait.", "normal")

    def record_keybind(self, event):
        if self.is_recording_key:
            new_key = event.keysym if event.keysym else event.keycode
            if new_key:
                self.root.unbind("<Key>")
                self.root.unbind(self.settings.get("key_bind", "F12"))
                self.root.bind(new_key, lambda e: self.process_clipboard())
                self.settings["key_bind"] = new_key
                self.key_bind.set(new_key)
                save_settings(self.settings)
                self.is_recording_key = False
                logging.info(f"Key bind updated to {new_key}")
                self.print_to_text(f"Key bind updated to {new_key}.", "normal")
                self.update_keybind_notes()

    def update_keybind_notes(self):
        for frame in [self.command_frame, self.change_block_frame, self.generate_laser_frame, self.generate_end_beam_frame, self.main_frame]:
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label) and "Press" in widget.cget("text"):
                    widget.config(text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.")

    def on_closing(self):
        if not self.is_destroyed:
            self.settings["always_on_top"] = self.always_on_top.get()
            self.settings["key_bind"] = self.key_bind.get()
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
        pyperclip.copy(command.encode('utf-8').decode('utf-8'))  # Ensure UTF-8 encoding
        self.print_to_text(f"Copied to clipboard: {command}", "normal")

    def process_clipboard(self):
        import pyperclip
        clipboard_content = pyperclip.paste().strip()
        if clipboard_content:
            self.process_command(clipboard_content)

    def process_command(self, command):
        active_tab = self.notebook.tab(self.notebook.select(), "text")
        if active_tab not in ["Settings", "Generate Laser", "Generate End Beam"]:
            use_set = active_tab == "Set Coordinates"

            pos_x_var = self.pos_x_set if use_set else self.pos_x_offset
            pos_y_var = self.pos_y_set if use_set else self.pos_y_offset
            pos_z_var = self.pos_z_set if use_set else self.pos_z_offset
            target_x_var = self.target_x_set if use_set else self.target_x_offset
            target_y_var = self.target_y_set if use_set else self.target_y_offset
            target_z_var = self.target_z_set if use_set else self.target_z_offset

            # Normalize command to handle with or without leading /
            if not command.startswith('/'):
                command = '/' + command

            # Initialize variables to avoid UnboundLocalError
            original_coords = None
            original_block = None
            modified_command = command

            # Handle setblock command
            if command.startswith('/setblock'):
                parts = command.strip().split()
                if len(parts) >= 4:
                    x, y, z = parts[1], parts[2], parts[3]
                    original_block = ' '.join(parts[4:]).strip() if len(parts) > 4 else ""
                    new_block = self.block_text.get().strip()
                    # Construct with exactly one space after coordinates
                    modified_command = f"/setblock {x} {y} {z} {new_block}"
                else:
                    modified_command = command  # Fallback if command is malformed

            # Handle block display summon command to replace block state
            elif command.startswith('/summon minecraft:block_display') and 'block_state:{Name:' in command:
                new_block = self.block_text.get().replace('"', r'\"')  # Escape quotes in new block name
                modified_command = re.sub(r'block_state:{Name:"([^"]*)"}', f'block_state:{{"Name":"{new_block}"}}', command, flags=re.DOTALL)
                match = re.search(r'block_state:{Name:"([^"]*)"}', command, flags=re.DOTALL)
                if match:
                    original_block = match.group(1)

            # Apply coordinate modifications for Command Modifier and Set Coordinates tabs
            if active_tab in ["Command Modifier", "Set Coordinates"]:
                modified_command, original_coords, original_block = self.command_processor.modify_coordinates(
                    modified_command, use_set, pos_x_var, pos_y_var, pos_z_var, target_x_var, target_y_var, target_z_var, self.block_text
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
            pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))  # Ensure UTF-8 encoding
            if active_tab == "Command Modifier":
                self.command_frame.winfo_children()[0].winfo_children()[0].nametowidget(self.cmd_text_cmd).delete("1.0", tk.END)
                self.command_frame.winfo_children()[0].winfo_children()[0].nametowidget(self.cmd_text_cmd).insert("1.0", modified_command)
            elif active_tab == "Set Coordinates":
                self.set_coord_frame.winfo_children()[0].winfo_children()[0].nametowidget(self.cmd_text_set).delete("1.0", tk.END)
                self.set_coord_frame.winfo_children()[0].winfo_children()[0].nametowidget(self.cmd_text_set).insert("1.0", modified_command)
            elif active_tab == "Change Block":
                self.change_block_frame.winfo_children()[0].winfo_children()[0].nametowidget(self.change_block_cmd_text).delete("1.0", tk.END)
                self.change_block_frame.winfo_children()[0].winfo_children()[0].nametowidget(self.change_block_cmd_text).insert("1.0", modified_command)
            self.print_to_text("Command copied to clipboard.", "normal")

    def generate_laser_initial_commands(self):
        try:
            x = float(self.laser_x.get())
            y = float(self.laser_y.get())
            z = float(self.laser_z.get())
            block_type = self.laser_block.get().replace("__", ":")
            tag = self.laser_tag.get()
            length = float(self.laser_length.get())

            cmd1 = f'/summon minecraft:block_display {x} {y} {z} {{ block_state:{{Name:"{block_type}"}}, transformation:{{ translation:[0.0f,0.0f,0.0f], scale:[0.1f, 0.1f, {length}f], left_rotation:[0.0f,0.0f,0.0f,1.0f], right_rotation:[0.0f,0.0f,0.0f,1.0f] }}, brightness:15728880, shadow:false, billboard:"fixed", Tags:["{tag}"]}}'
            cmd2 = f'/execute as @e[tag={tag}] at @s run data modify entity @s transformation.translation set value [0.5f,0f,-0f]'
            cmd3 = f'/tp @e[tag={tag},sort=nearest,limit=1] {x} {y+0.5} {z+0.999999}'

            self.cmd1_text.delete("1.0", tk.END)
            self.cmd1_text.insert("1.0", cmd1)
            self.cmd2_text.delete("1.0", tk.END)
            self.cmd2_text.insert("1.0", cmd2)
            self.cmd3_text.delete("1.0", tk.END)
            self.cmd3_text.insert("1.0", cmd3)
        except ValueError:
            self.print_to_text("Error: Please enter valid numbers for coordinates and length.", "normal")

    def generate_laser_rotation_commands(self):
        try:
            tag = self.laser_tag.get()
            rot_x = float(self.laser_rot_x.get())
            rot_y = float(self.laser_rot_y.get())

            cmd4 = f'/execute as @e[tag={tag}] at @s run tp @s ~ ~ ~ ~{rot_x} ~{rot_y}'

            self.cmd4_text.delete("1.0", tk.END)
            self.cmd4_text.insert("1.0", cmd4)
        except ValueError:
            self.print_to_text("Error: Please enter valid numbers for rotations.", "normal")

    def generate_end_beam_commands(self):
        try:
            origin_x = self.origin_x.get()
            origin_y = self.origin_y.get()
            origin_z = self.origin_z.get()
            target_x = self.target_x.get()
            target_y = self.target_y.get()
            target_z = self.target_z.get()

            spawn_cmd = f"summon end_crystal {origin_x} {origin_y} {origin_z} {{ShowBottom:0b,Invulnerable:1b,Tags:[\"laser\"],BeamTarget:{{X:{target_x},Y:{target_y},Z:{target_z}}}}}"
            despawn_cmd = f"kill @e[type=end_crystal,tag=laser,distance=..2,x={origin_x},y={origin_y},z={origin_z}]"

            self.spawn_text.delete("1.0", tk.END)
            self.spawn_text.insert("1.0", spawn_cmd)
            self.despawn_text.delete("1.0", tk.END)
            self.despawn_text.insert("1.0", despawn_cmd)
        except ValueError:
            self.print_to_text("Error: Please enter valid coordinates.", "normal")

    def autofill_coordinates(self, vars_list):
        import pyperclip
        clipboard_content = pyperclip.paste().strip()
        coords = re.match(r'-?\d+\s*-?\d+\s*-?\d+|(-?\d+,)\s*-?\d+\s*-?\d+|(-?\d+,\s*-?\d+,\s*-?\d+)', clipboard_content)
        if coords:
            coords = re.findall(r'-?\d+', clipboard_content)
            if len(coords) >= 3:
                vars_list[0].set(coords[0])
                vars_list[1].set(coords[1])
                vars_list[2].set(coords[2])
                self.print_to_text(f"Autofilled coordinates from clipboard: {clipboard_content}", "normal")
            else:
                self.print_to_text("Error: Clipboard content must contain at least three numbers.", "normal")
        else:
            self.print_to_text("Error: Invalid format. Use 0 0 0, 0,0,0, or 0, 0, 0.", "normal")

    def run(self):
        self.root.mainloop()