# Updated on 12:05 PM CDT, Friday, June 13, 2025
import tkinter as tk
import pyperclip
import re
import logging
from tkinter import ttk

def toggle_terminal(gui):
    if gui.terminal_visible:
        gui.terminal_text.pack_forget()
        gui.terminal_instruction.pack_forget()
        v_scrollbar = [w for w in gui.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'vertical'][0]
        v_scrollbar.pack_forget()
        h_scrollbar = [w for w in gui.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'horizontal'][0]
        h_scrollbar.pack_forget()
        gui.terminal_visible = False
    else:
        gui.terminal_text.pack(expand=True, fill="both", padx=10, pady=5)
        v_scrollbar = [w for w in gui.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'vertical'][0]
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar = [w for w in gui.main_frame.winfo_children() if isinstance(w, ttk.Scrollbar) and w['orient'] == 'horizontal'][0]
        h_scrollbar.pack(fill="x")
        gui.terminal_instruction.pack(pady=10, fill="x", padx=10)
        gui.terminal_visible = True
    gui.terminal_button.config(text="Show Terminal" if not gui.terminal_visible else "Hide Terminal")

def print_to_text(gui, message, tags="normal"):
    if gui.terminal_visible and hasattr(gui, 'terminal_text') and gui.terminal_text.winfo_exists():
        gui.terminal_text.configure(state='normal')
        gui.terminal_text.insert(tk.END, message + '\n', tags)
        gui.terminal_text.configure(state='disabled')
        gui.terminal_text.see(tk.END)

def adjust_offset(offset_var, change):
    try:
        current = int(offset_var.get())
        offset_var.set(str(current + change))
    except ValueError:
        offset_var.set("0")

def toggle_always_on_top(gui):
    gui.root.attributes('-topmost', gui.always_on_top.get())
    gui.settings["always_on_top"] = gui.always_on_top.get()
    from src.settings import save_settings
    save_settings(gui.settings)
    logging.info(f"Always on top set to {gui.always_on_top.get()}")

def start_record_keybind(gui):
    if not gui.is_recording_key:
        gui.is_recording_key = True
        gui.print_to_text("Press any key to record new keybind...", "normal")
        gui.root.bind("<Key>", lambda e: record_keybind(gui, e))
    else:
        gui.print_to_text("Already recording a keybind. Please press a key or wait.", "normal")

def record_keybind(gui, event):
    if gui.is_recording_key:
        new_key = event.keysym if event.keysym else event.keycode
        if new_key:
            gui.root.unbind("<Key>")
            gui.root.unbind(gui.settings.get("key_bind", "F12"))
            gui.root.bind(new_key, lambda e: gui.process_clipboard())
            gui.settings["key_bind"] = new_key
            gui.key_bind.set(new_key)
            from src.settings import save_settings
            save_settings(gui.settings)
            gui.is_recording_key = False
            logging.info(f"Key bind updated to {new_key}")
            gui.print_to_text(f"Key bind updated to {new_key}.", "normal")
            update_keybind_notes(gui)

def update_keybind_notes(gui):
    for frame in [gui.command_frame, gui.change_block_frame, gui.generate_laser_frame, gui.generate_end_beam_frame, gui.main_frame]:
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label) and "Press" in widget.cget("text"):
                widget.config(text=f"Press set keybind to take coordinates from command and automatically update clipboard with result. Works with: setblock, summon, tp.")

def on_closing(gui):
    if not gui.is_destroyed:
        gui.settings["always_on_top"] = gui.always_on_top.get()
        gui.settings["key_bind"] = gui.key_bind.get()
        from src.settings import save_settings
        save_settings(gui.settings)
        gui.root.destroy()
        gui.is_destroyed = True

def show_window(gui):
    gui.root.deiconify()

def show_settings(gui):
    gui.root.deiconify()
    gui.notebook.select(gui.settings_frame)

def copy_to_clipboard(gui, command):
    pyperclip.copy(command.encode('utf-8').decode('utf-8'))  # Ensure UTF-8 encoding
    gui.print_to_text(f"Copied to clipboard: {command}", "normal")

def process_clipboard(gui):
    import pyperclip
    clipboard_content = pyperclip.paste().strip()
    if clipboard_content:
        gui.print_to_text(f"Processing clipboard: {clipboard_content}", "normal")  # Debug print
        gui.process_command(clipboard_content)

def process_command(gui, command):
    active_tab = gui.notebook.tab(gui.notebook.select(), "text")
    if active_tab not in ["Settings", "Generate Laser", "Generate End Beam"]:
        use_set = active_tab == "Set Coordinates"

        pos_x_var = gui.pos_x_set if use_set else gui.pos_x_offset
        pos_y_var = gui.pos_y_set if use_set else gui.pos_y_offset
        pos_z_var = gui.pos_z_set if use_set else gui.pos_z_offset
        target_x_var = gui.target_x_set if use_set else gui.target_x_offset
        target_y_var = gui.target_y_set if use_set else gui.target_y_offset
        target_z_var = gui.target_z_set if use_set else gui.target_z_offset

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
                new_block = gui.block_text.get().strip()
                # Construct with exactly one space after coordinates
                modified_command = f"/setblock {x} {y} {z} {new_block}"
            else:
                modified_command = command  # Fallback if command is malformed

        # Handle block display summon command to replace block state
        elif command.startswith('/summon minecraft:block_display') and 'block_state:' in command:
            new_block = gui.block_text.get().strip().replace('"', r'\"')  # Escape quotes in new block name
            # New regex to handle both quoted and unquoted block_state with nested Name
            modified_command = re.sub(
                r'block_state:(?:{)?(?:\"{)?Name:\"([^\"]*)\"(?:})?(?:\")?',
                f'block_state:{{Name:"{new_block}"}}',
                command,
                flags=re.DOTALL
            )

            match = re.search(r'block_state:(?:{)?(?:\"{)?Name:\"([^\"]*)\"(?:})?(?:\")?', command, flags=re.DOTALL)
            if match:
                original_block = match.group(1)
            gui.print_to_text(f"Debug: Using block text: {gui.block_text.get()}", "normal")  # Debug print

        # Apply coordinate modifications for Command Modifier and Set Coordinates tabs
        if active_tab in ["Command Modifier", "Set Coordinates"]:
            modified_command, original_coords, original_block = gui.command_processor.modify_coordinates(
                modified_command, use_set, pos_x_var, pos_y_var, pos_z_var, target_x_var, target_y_var, target_z_var, gui.block_text
            )

        gui.print_to_text(f"Input Command: {command}", "command")
        if original_coords:
            gui.print_to_text(f"Original Coordinates: {original_coords}", "coord")
        if original_block:
            gui.print_to_text(f"Original Block: {original_block}", "block_unchanged")
        gui.print_to_text(f"Modified Command: {modified_command}", "command")
        if original_coords:
            new_coords = [int(x) for x in re.findall(r'-?\d+\b', modified_command) if x.lstrip('-').isdigit()]
            gui.print_to_text(f"New Coordinates: {new_coords}", "modified_coord")
        if original_block and gui.block_text.get() != original_block:
            gui.print_to_text(f"New Block: {gui.block_text.get()}", "block_changed")

        pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))  # Ensure UTF-8 encoding
        if active_tab == "Command Modifier":
            gui.command_frame.winfo_children()[0].winfo_children()[0].nametowidget(gui.cmd_text_cmd).delete("1.0", tk.END)
            gui.command_frame.winfo_children()[0].winfo_children()[0].nametowidget(gui.cmd_text_cmd).insert("1.0", modified_command)
        elif active_tab == "Set Coordinates":
            gui.set_coord_frame.winfo_children()[0].winfo_children()[0].nametowidget(gui.cmd_text_set).delete("1.0", tk.END)
            gui.set_coord_frame.winfo_children()[0].winfo_children()[0].nametowidget(gui.cmd_text_set).insert("1.0", modified_command)
        elif active_tab == "Change Block":
            gui.change_block_frame.winfo_children()[0].winfo_children()[0].nametowidget(gui.change_block_cmd_text).delete("1.0", tk.END)
            gui.change_block_frame.winfo_children()[0].winfo_children()[0].nametowidget(gui.change_block_cmd_text).insert("1.0", modified_command)
        gui.print_to_text("Command copied to clipboard.", "normal")

def generate_laser_initial_commands(gui):
    try:
        x = float(gui.laser_x.get())
        y = float(gui.laser_y.get())
        z = float(gui.laser_z.get())
        block_type = gui.laser_block.get().replace("__", ":")
        tag = gui.laser_tag.get()
        length = float(gui.laser_length.get())

        cmd1 = f'/summon minecraft:block_display {x} {y} {z} {{ block_state:{{Name:"{block_type}"}}, transformation:{{ translation:[0.0f,0.0f,0.0f], scale:[0.1f, 0.1f, {length}f], left_rotation:[0.0f,0.0f,0.0f,1.0f], right_rotation:[0.0f,0.0f,0.0f,1.0f] }}, brightness:15728880, shadow:false, billboard:"fixed", Tags:["{tag}"]}}'
        cmd2 = f'/execute as @e[tag={tag}] at @s run data modify entity @s transformation.translation set value [0.5f,0f,-0f]'
        cmd3 = f'/tp @e[tag={tag},sort=nearest,limit=1] {x} {y+0.5} {z+0.999999}'

        gui.cmd1_text.delete("1.0", tk.END)
        gui.cmd1_text.insert("1.0", cmd1)
        gui.cmd2_text.delete("1.0", tk.END)
        gui.cmd2_text.insert("1.0", cmd2)
        gui.cmd3_text.delete("1.0", tk.END)
        gui.cmd3_text.insert("1.0", cmd3)
    except ValueError:
        gui.print_to_text("Error: Please enter valid numbers for coordinates and length.", "normal")

def generate_laser_rotation_commands(gui):
    try:
        tag = gui.laser_tag.get()
        rot_x = float(gui.laser_rot_x.get())
        rot_y = float(gui.laser_rot_y.get())

        cmd4 = f'/execute as @e[tag={tag}] at @s run tp @s ~ ~ ~ ~{rot_x} ~{rot_y}'

        gui.cmd4_text.delete("1.0", tk.END)
        gui.cmd4_text.insert("1.0", cmd4)
    except ValueError:
        gui.print_to_text("Error: Please enter valid numbers for rotations.", "normal")

def generate_end_beam_commands(gui):
    try:
        origin_x = gui.origin_x.get()
        origin_y = gui.origin_y.get()
        origin_z = gui.origin_z.get()
        target_x = gui.target_x.get()
        target_y = gui.target_y.get()
        target_z = gui.target_z.get()

        spawn_cmd = f"summon end_crystal {origin_x} {origin_y} {origin_z} {{ShowBottom:0b,Invulnerable:1b,Tags:[\"laser\"],BeamTarget:{{X:{target_x},Y:{target_y},Z:{target_z}}}}}"
        despawn_cmd = f"kill @e[type=end_crystal,tag=laser,distance=..2,x={origin_x},y={origin_y},z={origin_z}]"

        gui.spawn_text.delete("1.0", tk.END)
        gui.spawn_text.insert("1.0", spawn_cmd)
        gui.despawn_text.delete("1.0", tk.END)
        gui.despawn_text.insert("1.0", despawn_cmd)
    except ValueError:
        gui.print_to_text("Error: Please enter valid coordinates.", "normal")

def autofill_coordinates(gui, vars_list):
    import pyperclip
    clipboard_content = pyperclip.paste().strip()
    coords = re.match(r'-?\d+\s*-?\d+\s*-?\d+|(-?\d+,)\s*-?\d+\s*-?\d+|(-?\d+,\s*-?\d+,\s*-?\d+)', clipboard_content)
    if coords:
        coords = re.findall(r'-?\d+', clipboard_content)
        if len(coords) >= 3:
            vars_list[0].set(coords[0])
            vars_list[1].set(coords[1])
            vars_list[2].set(coords[2])
            gui.print_to_text(f"Autofilled coordinates from clipboard: {clipboard_content}", "normal")
        else:
            gui.print_to_text("Error: Clipboard content must contain at least three numbers.", "normal")
    else:
        gui.print_to_text("Error: Invalid format. Use 0 0 0, 0,0,0, or 0, 0, 0.", "normal")