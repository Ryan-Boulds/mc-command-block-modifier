# Updated on 09:40 PM CDT, Monday, July 07, 2025
import logging
import pyperclip
import tkinter as tk
from tkinter import ttk
from src.command_modifier import process_command, set_laser_preset, set_lightbeam_preset

def adjust_offset(offset_var, change):
    try:
        current = float(offset_var.get())
        offset_var.set(str(current + change))
    except ValueError:
        offset_var.set(str(change))
    logging.debug(f"Adjusted offset: {offset_var.get()}")

def toggle_always_on_top(gui):
    gui.root.attributes('-topmost', gui.always_on_top.get())
    logging.debug(f"Always on top set to: {gui.always_on_top.get()}")

def start_record_keybind(gui):
    gui.is_recording_key = True
    gui.key_bind.set("Press a key...")
    gui.root.bind("<Key>", lambda event: gui.record_keybind(event))
    logging.debug("Started recording keybind")

def record_keybind(gui, event):
    if gui.is_recording_key:
        key = event.keysym
        if key:
            gui.key_bind.set(key)
            gui.root.unbind("<Key>")
            gui.is_recording_key = False
            gui.root.bind(key, lambda e: gui.process_clipboard())
            from src.settings import save_settings
            gui.settings["key_bind"] = key
            save_settings(gui.settings)
            gui.update_keybind_notes()
            logging.debug(f"Recorded keybind: {key}")

def update_keybind_notes(gui):
    pass

def process_clipboard(gui):
    try:
        active_tab = gui.notebook.tab(gui.notebook.select(), "text").lower()
        logging.debug(f"Processing clipboard for tab: {active_tab}")
        clipboard_content = pyperclip.paste().strip()

        if active_tab == "generate laser":
            # Generate laser command with fixed decimal parts
            try:
                coords = gui.clipboard_parser.parse_coordinates(clipboard_content)
                if coords:
                    gui.laser_x.set(str(int(float(coords[0]))))
                    gui.laser_y.set(str(int(float(coords[1]))))
                    gui.laser_z.set(str(int(float(coords[2]))))
                    logging.debug(f"Autofilled integer coordinates: {coords}")
                    gui.print_to_text(f"Autofilled integer coordinates from clipboard: {[str(int(float(coord))) for coord in coords]}", "coord")
                gui.generate_laser_initial_commands()
            except ValueError as e:
                logging.error(f"Error processing clipboard: {e}")
                gui.print_to_text(f"Error: Invalid clipboard format. Use '/summon minecraft:block_display 0.0 0.0 0.0' or 'X Y Z' format.", "normal")
        elif active_tab == "generate end beam":
            try:
                coords = gui.clipboard_parser.parse_coordinates(clipboard_content)
                if coords:
                    gui.origin_x.set(coords[0])
                    gui.origin_y.set(coords[1])
                    gui.origin_z.set(coords[2])
                    gui.target_x.set(coords[0])
                    gui.target_y.set(coords[1])
                    gui.target_z.set(coords[2])
                    logging.debug(f"Autofilled coordinates: {coords}")
                    gui.print_to_text(f"Autofilled coordinates from clipboard: {coords}", "coord")
                gui.generate_end_beam_commands()
            except ValueError as e:
                logging.error(f"Error processing clipboard: {e}")
                gui.print_to_text(f"Error: Invalid clipboard format. Use '/summon minecraft:block_display 0.0 0.0 0.0' or 'X Y Z' format.", "normal")
        else:
            modified_command = process_command(gui, clipboard_content)
            gui.copy_to_clipboard(modified_command)
    except Exception as e:
        logging.error(f"Error processing clipboard: {e}")
        gui.print_to_text(f"Error processing clipboard: {e}", "normal")

def generate_laser_initial_commands(gui):
    try:
        x = float(gui.laser_x.get()) if gui.laser_x.get() else 0
        y = float(gui.laser_y.get()) if gui.laser_y.get() else 0
        z = float(gui.laser_z.get()) if gui.laser_z.get() else 0
        # Apply fixed decimal parts
        x = float(f"{int(x):.0f}.000000")
        y = float(f"{int(y):.0f}.500000")
        z = float(f"{int(z):.0f}.000001")
        tag = gui.laser_tag.get() if gui.laser_tag.get() else "beam1"
        block_type = gui.laser_block.get().replace("__", ":") if gui.laser_block.get() else "minecraft:lime_concrete"
        beam_scale = float(gui.laser_length.get()) if gui.laser_length.get() else -150.0

        command = (
            f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f} '
            f'{{block_state:{{Name:"{block_type}"}},'
            f'transformation:{{translation:[0.5f,0.0f,0.0f],'
            f'scale:[0.1f,0.1f,{beam_scale:.6f}f],'
            f'left_rotation:[0.0f,0.0f,0.0f,1.0f],'
            f'right_rotation:[0.0f,0.0f,0.0f,1.0f]}},'
            f'brightness:15728880,shadow:false,billboard:"fixed",Tags:["{tag}"]}}'
        )
        if hasattr(gui, 'laser_cmd_text') and gui.laser_cmd_text.winfo_exists():
            gui.laser_cmd_text.delete("1.0", tk.END)
            gui.laser_cmd_text.insert("1.0", command)
        gui.copy_to_clipboard(command)
        logging.debug(f"Generated laser command: {command}")
        gui.print_to_text(f"Generated Command: {command}", "command")
    except ValueError as e:
        logging.error(f"Error generating laser command: {e}")
        gui.print_to_text("Error: Please enter valid numbers for coordinates and length.", "normal")

def generate_laser_rotation_commands(gui):
    try:
        rot_x = float(gui.laser_rot_x.get()) if gui.laser_rot_x.get() else 0.0
        rot_y = float(gui.laser_rot_y.get()) if gui.laser_rot_y.get() else 1.0
        tag = gui.laser_tag.get() if gui.laser_tag.get() else "beam1"
        command = f'/execute as @e[tag={tag}] at @s run tp @s ~ ~ ~ ~{rot_x:.1f} ~{rot_y:.1f}'
        if hasattr(gui, 'laser_rot_cmd_text') and gui.laser_rot_cmd_text.winfo_exists():
            gui.laser_rot_cmd_text.delete("1.0", tk.END)
            gui.laser_rot_cmd_text.insert("1.0", command)
        gui.copy_to_clipboard(command)
        logging.debug(f"Generated rotation command: {command}")
        gui.print_to_text(f"Generated Rotation Command: {command}", "command")
    except ValueError as e:
        logging.error(f"Error generating rotation command: {e}")
        gui.print_to_text("Error: Please enter valid numbers for rotation.", "normal")

def generate_end_beam_commands(gui):
    try:
        origin_x = float(gui.origin_x.get()) if gui.origin_x.get() else 0
        origin_y = float(gui.origin_y.get()) if gui.origin_y.get() else 0
        origin_z = float(gui.origin_z.get()) if gui.origin_z.get() else 0
        target_x = float(gui.target_x.get()) if gui.target_x.get() else 0
        target_y = float(gui.target_y.get()) if gui.target_y.get() else 0
        target_z = float(gui.target_z.get()) if gui.target_z.get() else 0
        commands = [
            f'/summon minecraft:end_crystal {origin_x:.6f} {origin_y:.6f} {origin_z:.6f} {{Tags:["beam1"]}}',
            f'/execute as @e[tag=beam1] at @s run tp @s ~ ~ ~ facing {target_x:.6f} {target_y:.6f} {target_z:.6f}'
        ]
        command = "\n".join(commands)
        if hasattr(gui, 'end_beam_cmd_text') and gui.end_beam_cmd_text.winfo_exists():
            gui.end_beam_cmd_text.delete("1.0", tk.END)
            gui.end_beam_cmd_text.insert("1.0", command)
        gui.copy_to_clipboard(command)
        logging.debug(f"Generated end beam commands: {command}")
        gui.print_to_text(f"Generated Commands:\n{command}", "command")
    except ValueError as e:
        logging.error(f"Error generating end beam commands: {e}")
        gui.print_to_text("Error: Please enter valid numbers for coordinates.", "normal")

def toggle_terminal(gui):
    gui.terminal_visible = not gui.terminal_visible
    if gui.terminal_visible:
        gui.terminal_frame.pack(fill="both", expand=True)
    else:
        gui.terminal_frame.pack_forget()
    logging.debug(f"Terminal visibility set to: {gui.terminal_visible}")

def print_to_text(gui, message, tags="normal"):
    if hasattr(gui, 'terminal_text') and gui.terminal_text.winfo_exists():
        gui.terminal_text.insert(tk.END, message + "\n", tags)
        gui.terminal_text.see(tk.END)
    logging.debug(f"Printed to terminal: {message}")

def on_closing(gui):
    if not gui.is_destroyed:
        gui.is_destroyed = True
        from src.settings import save_settings
        save_settings(gui.settings)
        gui.root.destroy()
        logging.debug("Application closed")

def show_window(gui):
    gui.root.deiconify()
    logging.debug("Window shown")

def show_settings(gui):
    gui.notebook.select(gui.settings_frame)
    logging.debug("Settings tab selected")

def copy_to_clipboard(gui, command):
    pyperclip.copy(command.encode('utf-8').decode('utf-8'))
    gui.print_to_text("Command copied to clipboard.", "normal")