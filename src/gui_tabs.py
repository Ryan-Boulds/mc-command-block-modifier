# Updated on 03:30 PM CDT, Thursday, June 19, 2025
import tkinter as tk
from tkinter import ttk
from src.command_modifier import set_laser_preset, set_lightbeam_preset

def create_modifier_gui(frame, pos_vars, target_vars, title_prefix, gui):
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
        tk.Button(scrollable_frame, text="▲", command=lambda v=var: gui.adjust_offset(v, 1), font=("Arial", 8), width=2).grid(row=i+2, column=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="▼", command=lambda v=var: gui.adjust_offset(v, -1), font=("Arial", 8), width=2).grid(row=i+2, column=3, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.autofill_coordinates([target_vars[0], target_vars[1], target_vars[2]]), font=("Arial", 8)).grid(row=5, column=0, columnspan=5, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="BeamTarget Mover (summon only)", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=6, column=0, columnspan=5, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X:", target_vars[0]), ("Y:", target_vars[1]), ("Z:", target_vars[2])]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+7, column=0, pady=0, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+7, column=1, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="▲", command=lambda v=var: gui.adjust_offset(v, 1), font=("Arial", 8), width=2).grid(row=i+7, column=2, pady=0, sticky="w")
        tk.Button(scrollable_frame, text="▼", command=lambda v=var: gui.adjust_offset(v, -1), font=("Arial", 8), width=2).grid(row=i+7, column=3, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.autofill_coordinates([target_vars[0], target_vars[1], target_vars[2]]), font=("Arial", 8)).grid(row=10, column=0, columnspan=5, pady=2, sticky="w")

    if title_prefix == "Command":
        gui.cmd_text_cmd = tk.Text(scrollable_frame, height=2, width=40)
        gui.cmd_text_cmd.grid(row=11, column=0, columnspan=4, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd_text_cmd.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=11, column=4, pady=2, sticky="w")
    elif title_prefix == "Set":
        gui.cmd_text_set = tk.Text(scrollable_frame, height=2, width=40)
        gui.cmd_text_set.grid(row=11, column=0, columnspan=4, pady=2, sticky="w")
        tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd_text_set.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=11, column=4, pady=2, sticky="w")
    tk.Button(scrollable_frame, text="Generate", command=lambda: gui.process_clipboard(), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=12, column=0, columnspan=5, pady=5, sticky="w")
    tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=13, column=0, columnspan=5, pady=2, sticky="w")

def create_change_block_gui(frame, gui):
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

    tk.Label(scrollable_frame, text="Change Block Modifier", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
    tk.Label(scrollable_frame, text="New Block Text:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.block_text, width=30, bg='#ffffff', font=("Arial", 10)).grid(row=2, column=0, columnspan=2, pady=0, sticky="w")

    tk.Button(scrollable_frame, text="Generate", command=lambda: gui.process_clipboard(), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=3, column=0, columnspan=3, pady=5, sticky="w")

    gui.change_block_cmd_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.change_block_cmd_text.grid(row=4, column=0, columnspan=2, pady=2, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.change_block_cmd_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=4, column=2, pady=2, sticky="w")
    tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=5, column=0, columnspan=3, pady=2, sticky="w")

def create_generate_laser_gui(frame, gui):
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

    tk.Label(scrollable_frame, text="Generate Laser", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
    for i, (label, var) in enumerate([("X Coordinate:", gui.laser_x), ("Y Coordinate:", gui.laser_y), ("Z Coordinate:", gui.laser_z), ("Tag/Group Name:", gui.laser_tag), ("Block Type:", gui.laser_block), ("Length:", gui.laser_length)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+1, column=0, pady=0, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=20 if i == 4 else 10, bg='#ffffff', font=("Arial", 10)).grid(row=i+1, column=1, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.autofill_coordinates([gui.laser_x, gui.laser_y, gui.laser_z]), font=("Arial", 8)).grid(row=7, column=0, columnspan=3, pady=2, sticky="w")
    tk.Button(scrollable_frame, text="Generate", command=gui.generate_laser_initial_commands, font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=8, column=0, columnspan=3, pady=5, sticky="w")

    tk.Label(scrollable_frame, text="Spawn Command:", font=("Arial", 10), bg='#f0f0f0').grid(row=9, column=0, pady=0, sticky="w")
    gui.cmd1_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.cmd1_text.grid(row=10, column=0, columnspan=2, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd1_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=10, column=2, pady=0, sticky="w")

    tk.Label(scrollable_frame, text="Modify Position:", font=("Arial", 10), bg='#f0f0f0').grid(row=11, column=0, pady=0, sticky="w")
    gui.cmd2_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.cmd2_text.grid(row=12, column=0, columnspan=2, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd2_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=12, column=2, pady=0, sticky="w")

    gui.cmd3_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.cmd3_text.grid(row=13, column=0, columnspan=2, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd3_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=13, column=2, pady=0, sticky="w")

    tk.Label(scrollable_frame, text="Laser Rotation:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=14, column=0, columnspan=3, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X Rotation:", gui.laser_rot_x), ("Y Rotation:", gui.laser_rot_y)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+15, column=0, pady=0, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+15, column=1, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Generate", command=gui.generate_laser_rotation_commands, font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=17, column=0, columnspan=3, pady=5, sticky="w")

    gui.cmd4_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.cmd4_text.grid(row=18, column=0, columnspan=2, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.cmd4_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=18, column=2, pady=0, sticky="w")

    tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=19, column=0, columnspan=3, pady=2, sticky="w")

def create_generate_end_beam_gui(frame, gui):
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

    tk.Label(scrollable_frame, text="Generate End Beam", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
    tk.Label(scrollable_frame, text="Origin:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, columnspan=2, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X:", gui.origin_x), ("Y:", gui.origin_y), ("Z:", gui.origin_z)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+2, column=0, pady=0, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+2, column=1, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.autofill_coordinates([gui.origin_x, gui.origin_y, gui.origin_z]), font=("Arial", 8)).grid(row=5, column=0, columnspan=2, pady=2, sticky="w")

    tk.Label(scrollable_frame, text="Target:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=6, column=0, columnspan=2, pady=2, sticky="w")
    for i, (label, var) in enumerate([("X:", gui.target_x), ("Y:", gui.target_y), ("Z:", gui.target_z)]):
        tk.Label(scrollable_frame, text=label, font=("Arial", 10), bg='#f0f0f0').grid(row=i+7, column=0, pady=0, sticky="w")
        tk.Entry(scrollable_frame, textvariable=var, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=i+7, column=1, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.autofill_coordinates([gui.target_x, gui.target_y, gui.target_z]), font=("Arial", 8)).grid(row=10, column=0, columnspan=2, pady=2, sticky="w")

    tk.Button(scrollable_frame, text="Generate", command=gui.generate_end_beam_commands, font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=11, column=0, columnspan=3, pady=5, sticky="w")

    tk.Label(scrollable_frame, text="Spawn Command:", font=("Arial", 10), bg='#f0f0f0').grid(row=12, column=0, pady=0, sticky="w")
    gui.spawn_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.spawn_text.grid(row=13, column=0, columnspan=2, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.spawn_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=13, column=2, pady=0, sticky="w")

    tk.Label(scrollable_frame, text="Despawn Command:", font=("Arial", 10), bg='#f0f0f0').grid(row=14, column=0, pady=0, sticky="w")
    gui.despawn_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.despawn_text.grid(row=15, column=0, columnspan=2, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.despawn_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=15, column=2, pady=0, sticky="w")

    tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=16, column=0, columnspan=3, pady=2, sticky="w")

def create_settings_gui(frame, gui):
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

    tk.Checkbutton(scrollable_frame, text="Always Remains on Top", variable=gui.always_on_top, command=gui.toggle_always_on_top, bg='#f0f0f0', font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")
    tk.Button(scrollable_frame, text="Press key to record keybind", command=gui.start_record_keybind, bg='#4CAF50', fg='#ffffff', font=("Arial", 10)).grid(row=1, column=0, pady=5, sticky="w")
    tk.Button(scrollable_frame, text="Generate 3D Model, Work in Progress", command=gui.on_closing, state="disabled", bg='#cccccc', fg='#666666', font=("Arial", 10)).grid(row=2, column=0, pady=5, sticky="w")
    tk.Button(scrollable_frame, text="Generate 2D Model, Work in Progress", command=gui.on_closing, state="disabled", bg='#cccccc', fg='#666666', font=("Arial", 10)).grid(row=3, column=0, pady=5, sticky="w")

def create_terminal_gui(frame, gui):
    if not hasattr(gui, 'terminal_text') or not gui.terminal_text.winfo_exists():
        gui.terminal_text = tk.Text(frame, height=3, font=("Courier", 10), bg='#000000', fg='#ffffff', insertbackground='#ffffff', relief='flat', borderwidth=2, state='disabled', wrap='none')
        gui.terminal_text.pack_forget()  # Hidden by default
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=gui.terminal_text.yview)
        v_scrollbar.pack_forget()
        gui.terminal_text['yscrollcommand'] = v_scrollbar.set
        h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=gui.terminal_text.xview)
        h_scrollbar.pack_forget()
        gui.terminal_text['xscrollcommand'] = h_scrollbar.set
        gui.terminal_text.tag_configure("command", foreground="#ffffff")
        gui.terminal_text.tag_configure("object", foreground="#55aaff")
        gui.terminal_text.tag_configure("coord", foreground="#ba42f0")
        gui.terminal_text.tag_configure("modified_coord", foreground="#00ff00")
        gui.terminal_text.tag_configure("normal", foreground="#ffffff")
        gui.terminal_text.tag_configure("block_changed", foreground="#00ff00")
        gui.terminal_text.tag_configure("block_unchanged", foreground="#ffffff")
        gui.terminal_instruction = tk.Label(frame, text=f"Copy a command, press set keybind to process.", font=("Normal", 10), bg='#f0f0f0', fg='#555555')
        gui.terminal_instruction.pack_forget()

    if not hasattr(gui, 'terminal_button') or not gui.terminal_button.winfo_exists():
        gui.terminal_button = tk.Button(frame, text="Show Terminal", command=gui.toggle_terminal, bg='#4CAF50', fg='#ffffff', font=("Arial", 10))
        gui.terminal_button.pack(pady=5)

def create_rename_tag_gui(frame, gui):
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

    # Initialize variables
    gui.modify_coords = tk.BooleanVar(value=True)
    gui.modify_translation = tk.BooleanVar(value=True)
    gui.modify_scale = tk.BooleanVar(value=True)
    gui.laser_mode = tk.StringVar(value="")
    gui.pos_x_set = tk.StringVar(value="0.0")
    gui.pos_y_set = tk.StringVar(value="0.5")
    gui.pos_z_set = tk.StringVar(value="0.999999")
    gui.trans_x = tk.StringVar(value="0.5")
    gui.trans_y = tk.StringVar(value="0.0")
    gui.trans_z = tk.StringVar(value="0.0")
    gui.beam_scale = tk.StringVar(value="-150.0")
    gui.centering_x = tk.StringVar(value="0.0")
    gui.centering_y = tk.StringVar(value="0.5")
    gui.centering_z = tk.StringVar(value="0.999999")
    gui.tag_text = tk.StringVar(value="beam1")
    gui.block_text = tk.StringVar(value="minecraft:lime_concrete")

    tk.Label(scrollable_frame, text="Rename Tag/Group Modifier", font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, columnspan=3, pady=5, sticky="w")

    # Coordinate Modification
    tk.Checkbutton(scrollable_frame, text="Modify Coordinates", variable=gui.modify_coords).grid(row=1, column=0, pady=2, sticky="w")
    tk.Label(scrollable_frame, text="X:", font=("Arial", 10), bg='#f0f0f0').grid(row=2, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.pos_x_set, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=2, column=1, pady=0, sticky="w")
    tk.Label(scrollable_frame, text="Y:", font=("Arial", 10), bg='#f0f0f0').grid(row=3, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.pos_y_set, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=3, column=1, pady=0, sticky="w")
    tk.Label(scrollable_frame, text="Z:", font=("Arial", 10), bg='#f0f0f0').grid(row=4, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.pos_z_set, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=4, column=1, pady=0, sticky="w")

    # Translation Modification
    tk.Checkbutton(scrollable_frame, text="Modify Translation", variable=gui.modify_translation).grid(row=5, column=0, pady=2, sticky="w")
    tk.Label(scrollable_frame, text="Trans X:", font=("Arial", 10), bg='#f0f0f0').grid(row=6, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.trans_x, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=6, column=1, pady=0, sticky="w")
    tk.Label(scrollable_frame, text="Trans Y:", font=("Arial", 10), bg='#f0f0f0').grid(row=7, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.trans_y, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=7, column=1, pady=0, sticky="w")
    tk.Label(scrollable_frame, text="Trans Z:", font=("Arial", 10), bg='#f0f0f0').grid(row=8, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.trans_z, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=8, column=1, pady=0, sticky="w")

    # Beam Scale Modification
    tk.Checkbutton(scrollable_frame, text="Modify Scale", variable=gui.modify_scale).grid(row=9, column=0, pady=2, sticky="w")
    tk.Label(scrollable_frame, text="Beam Scale:", font=("Arial", 10), bg='#f0f0f0').grid(row=10, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.beam_scale, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=10, column=1, pady=0, sticky="w")

    # Tag/Group Name
    tk.Label(scrollable_frame, text="Tag/Group Name:", font=("Arial", 10), bg='#f0f0f0').grid(row=11, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.tag_text, width=20, bg='#ffffff', font=("Arial", 10)).grid(row=11, column=1, pady=0, sticky="w")

    # Block Type
    tk.Label(scrollable_frame, text="Block Type:", font=("Arial", 10), bg='#f0f0f0').grid(row=12, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.block_text, width=20, bg='#ffffff', font=("Arial", 10)).grid(row=12, column=1, pady=0, sticky="w")

    # Laser/Lightbeam Buttons for Autofill
    tk.Button(scrollable_frame, text="Laser", command=lambda: set_laser_preset(gui), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=13, column=0, pady=2, sticky="w")
    tk.Button(scrollable_frame, text="Lightbeam", command=lambda: set_lightbeam_preset(gui), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=13, column=1, pady=2, sticky="w")

    # Centering Modifiers
    tk.Label(scrollable_frame, text="Centering Modifiers:", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=14, column=0, columnspan=2, pady=2, sticky="w")
    tk.Label(scrollable_frame, text="X:", font=("Arial", 10), bg='#f0f0f0').grid(row=15, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.centering_x, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=15, column=1, pady=0, sticky="w")
    tk.Label(scrollable_frame, text="Y:", font=("Arial", 10), bg='#f0f0f0').grid(row=16, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.centering_y, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=16, column=1, pady=0, sticky="w")
    tk.Label(scrollable_frame, text="Z:", font=("Arial", 10), bg='#f0f0f0').grid(row=17, column=0, pady=0, sticky="w")
    tk.Entry(scrollable_frame, textvariable=gui.centering_z, width=10, bg='#ffffff', font=("Arial", 10)).grid(row=17, column=1, pady=0, sticky="w")
    tk.Button(scrollable_frame, text="Autofill from Clipboard", command=lambda: gui.autofill_coordinates([gui.centering_x, gui.centering_y, gui.centering_z])).grid(row=18, column=0, columnspan=2, pady=2, sticky="w")

    tk.Button(scrollable_frame, text="Generate", command=lambda: gui.process_clipboard(), font=("Arial", 10), bg='#4CAF50', fg='#ffffff').grid(row=19, column=0, columnspan=2, pady=5, sticky="w")

    gui.rename_tag_cmd_text = tk.Text(scrollable_frame, height=2, width=40)
    gui.rename_tag_cmd_text.grid(row=20, column=0, columnspan=2, pady=2, sticky="w")
    tk.Button(scrollable_frame, text="Copy", command=lambda: gui.copy_to_clipboard(gui.rename_tag_cmd_text.get("1.0", tk.END).strip()), font=("Arial", 10)).grid(row=20, column=2, pady=2, sticky="w")
    tk.Label(scrollable_frame, text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.", font=("Arial", 8), bg='#f0f0f0').grid(row=21, column=0, columnspan=3, pady=2, sticky="w")