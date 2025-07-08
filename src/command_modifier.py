# Updated on 09:46 PM CDT, Monday, July 07, 2025
import re
import logging
import tkinter as tk
import pyperclip
from tkinter import ttk
from src.clipboard_parser import ClipboardCoordinateParser

def process_command(gui, command):
    active_tab = gui.notebook.tab(gui.notebook.select(), "text").lower()
    logging.debug(f"Active tab: {active_tab}")
    # Normalize command
    if not command.startswith('/'):
        command = '/' + command

    # Initialize modified_command with the input command
    modified_command = command
    original_coords = None
    original_tag = None
    original_translation = None
    original_scale = None
    original_block = None

    if active_tab in ["modify laser", "rename tag/group"]:
        # Get centering offsets
        try:
            center_x = float(gui.centering_x.get()) if gui.centering_x.get() and gui.modify_centering.get() else 0.0
            center_y = float(gui.centering_y.get()) if gui.centering_y.get() and gui.modify_centering.get() else 0.0
            center_z = float(gui.centering_z.get()) if gui.centering_z.get() and gui.modify_centering.get() else 0.0
        except ValueError:
            center_x, center_y, center_z = 0.0, 0.0, 0.0
            logging.warning("Invalid centering modifier values, using defaults (0.0, 0.0, 0.0)")
            gui.print_to_text("Warning: Invalid centering values, using defaults (0.0, 0.0, 0.0)", "normal")

        # If Generate button is clicked with no command or a placeholder, create new command
        if command == '/' or not command.strip('/'):
            try:
                x = float(gui.pos_x_set.get()) + center_x if gui.modify_coords.get() and gui.pos_x_set.get() else 0.0
                y = float(gui.pos_y_set.get()) + center_y if gui.modify_coords.get() and gui.pos_y_set.get() else 0.5
                z = float(gui.pos_z_set.get()) + center_z if gui.modify_coords.get() and gui.pos_z_set.get() else 0.999999
                trans_x = float(gui.trans_x.get()) if gui.modify_translation.get() and gui.trans_x.get() else 0.5
                trans_y = float(gui.trans_y.get()) if gui.modify_translation.get() and gui.trans_y.get() else 0.0
                trans_z = float(gui.trans_z.get()) if gui.modify_translation.get() and gui.trans_z.get() else 0.0
                beam_scale = float(gui.beam_scale.get()) if gui.modify_scale.get() and gui.beam_scale.get() else -150.0
                tag = gui.tag_text.get() if gui.tag_text.get() else "beam1"
                block_type = gui.block_text.get().replace("__", ":") if gui.block_text.get() else "minecraft:lime_concrete"

                modified_command = (
                    f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f} '
                    f'{{block_state:{{Name:"{block_type}"}},'
                    f'transformation:{{translation:[{trans_x:.6f}f,{trans_y:.6f}f,{trans_z:.6f}f],'
                    f'scale:[0.1f,0.1f,{beam_scale:.6f}f],'
                    f'left_rotation:[0.0f,0.0f,0.0f,1.0f],'
                    f'right_rotation:[0.0f,0.0f,0.0f,1.0f]}},'
                    f'brightness:15728880,shadow:false,billboard:"fixed",Tags:["{tag}"]}}'
                )
                logging.debug(f"Generated new command: {modified_command}")
                gui.print_to_text(f"Generated Command: {modified_command}", "command")
            except ValueError as e:
                logging.error(f"Error generating command: {e}")
                gui.print_to_text("Error: Please enter valid numbers for coordinates, translation, and scale.", "normal")
                return command
        else:
            # Extract original coordinates for /summon minecraft:block_display
            coord_match = re.match(r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', command)
            if coord_match:
                x, y, z = map(float, coord_match.groups())
                original_coords = [x, y, z]
                logging.debug(f"Extracted coordinates: {original_coords}")

            # Extract original tag
            new_tag = gui.tag_text.get() if gui.tag_text.get() else "beam1"
            if 'Tags:' in command:
                match = re.search(r'Tags:\s*\["([^"]*)"\]', command, flags=re.DOTALL)
                if match:
                    original_tag = match.group(1)
                    modified_command = re.sub(
                        r'Tags:\s*\["([^"]*)"\]',
                        f'Tags:["{new_tag}"]',
                        modified_command,
                        flags=re.DOTALL
                    )
            elif command.startswith('/execute') or command.startswith('/tp'):
                match = re.search(r'tag=([^,\s\]]+)', command, flags=re.DOTALL)
                if match:
                    original_tag = match.group(1)
                    modified_command = re.sub(
                        r'tag=([^,\s\]]+)',
                        f'tag={new_tag}',
                        modified_command,
                        flags=re.DOTALL
                    )

            # Apply coordinate modifications if requested
            if gui.modify_coords.get() and original_coords:
                try:
                    x = float(gui.pos_x_set.get()) + center_x if gui.pos_x_set.get() else original_coords[0] + center_x
                    y = float(gui.pos_y_set.get()) + center_y if gui.pos_y_set.get() else original_coords[1] + center_y
                    z = float(gui.pos_z_set.get()) + center_z if gui.pos_z_set.get() else original_coords[2] + center_z
                    modified_command = re.sub(
                        r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',
                        f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f}',
                        modified_command
                    )
                except ValueError:
                    logging.warning("Invalid coordinate values, skipping coordinate modification")
                    gui.print_to_text("Warning: Invalid coordinate values, skipping coordinate modification", "normal")

            # Apply translation modifications if requested
            if gui.modify_translation.get():
                try:
                    trans_x = float(gui.trans_x.get())
                    trans_y = float(gui.trans_y.get())
                    trans_z = float(gui.trans_z.get())
                    original_translation = re.search(
                        r'translation:\s*\[(-?\d+\.?\d*f)\s*,\s*(-?\d+\.?\d*f)\s*,\s*(-?\d+\.?\d*f)\s*\]',
                        command,
                        flags=re.DOTALL
                    )
                    if original_translation:
                        original_translation = [original_translation.group(1), original_translation.group(2), original_translation.group(3)]
                    modified_command = re.sub(
                        r'translation:\s*\[(-?\d+\.?\d*f)?\s*,\s*(-?\d+\.?\d*f)?\s*,\s*(-?\d+\.?\d*f)?\s*\]',
                        f'translation:[{trans_x:.6f}f,{trans_y:.6f}f,{trans_z:.6f}f]',
                        modified_command,
                        flags=re.DOTALL
                    )
                except ValueError:
                    logging.warning("Invalid translation values, skipping translation modification")
                    gui.print_to_text("Warning: Invalid translation values, skipping translation modification", "normal")

            # Apply scale modifications if requested
            if gui.modify_scale.get():
                try:
                    beam_scale = float(gui.beam_scale.get())
                    original_scale = re.search(
                        r'scale:\s*\[(-?\d+\.?\d*f)\s*,\s*(-?\d+\.?\d*f)\s*,\s*(-?\d+\.?\d*f)\s*\]',
                        command,
                        flags=re.DOTALL
                    )
                    if original_scale:
                        original_scale = [original_scale.group(1), original_scale.group(2), original_scale.group(3)]
                    modified_command = re.sub(
                        r'scale:\s*\[(-?\d+\.?\d*f)?\s*,\s*(-?\d+\.?\d*f)?\s*,\s*(-?\d+\.?\d*f)?\s*\]',
                        f'scale:[0.1f,0.1f,{beam_scale:.6f}f]',
                        modified_command,
                        flags=re.DOTALL
                    )
                except ValueError:
                    logging.warning("Invalid scale value, skipping scale modification")
                    gui.print_to_text("Warning: Invalid scale value, skipping scale modification", "normal")

        # Log and update GUI
        logging.debug(f"Input Command: {command}")
        if original_coords:
            logging.debug(f"Original Coordinates: {original_coords}")
            gui.print_to_text(f"Original Coordinates: {original_coords}", "coord")
        if original_tag:
            logging.debug(f"Original Tag: {original_tag}")
            gui.print_to_text(f"Original Tag: {original_tag}", "block_unchanged")
        if original_translation:
            logging.debug(f"Original Translation: {original_translation}")
            gui.print_to_text(f"Original Translation: {original_translation}", "block_unchanged")
        if original_scale:
            logging.debug(f"Original Scale: {original_scale}")
            gui.print_to_text(f"Original Scale: {original_scale}", "block_unchanged")
        logging.debug(f"Modified Command: {modified_command}")
        gui.print_to_text(f"Modified Command: {modified_command}", "command")

        # Safely extract new coordinates
        if '/summon' in modified_command:
            coord_match = re.search(r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', modified_command)
            if coord_match:
                new_coords = [float(coord_match.group(1)), float(coord_match.group(2)), float(coord_match.group(3))]
                logging.debug(f"New Coordinates: {new_coords}")
                gui.print_to_text(f"New Coordinates: {new_coords}", "modified_coord")
            else:
                logging.debug("Failed to extract new coordinates due to invalid format")
                gui.print_to_text("Warning: Failed to extract new coordinates.", "normal")

        if original_tag and new_tag != original_tag:
            gui.print_to_text(f"New Tag: {new_tag}", "block_changed")
        if gui.modify_translation.get():
            try:
                gui.print_to_text(f"New Translation: [{float(gui.trans_x.get()):.6f}f,{float(gui.trans_y.get()):.6f}f,{float(gui.trans_z.get()):.6f}f]", "block_changed")
            except ValueError:
                pass
        if gui.modify_scale.get():
            try:
                gui.print_to_text(f"New Scale: [0.1f,0.1f,{float(gui.beam_scale.get()):.6f}f]", "block_changed")
            except ValueError:
                pass

        # Update the textbox
        if hasattr(gui, 'rename_tag_cmd_text') and gui.rename_tag_cmd_text.winfo_exists():
            gui.rename_tag_cmd_text.delete("1.0", tk.END)
            gui.rename_tag_cmd_text.insert("1.0", modified_command)
        else:
            logging.warning("rename_tag_cmd_text not found or not initialized")
            gui.print_to_text("Warning: rename_tag_cmd_text not found or not initialized", "normal")

        pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))
        gui.print_to_text("Command copied to clipboard.", "normal")

    elif active_tab == "change block":
        # Extract original coordinates
        coord_match = re.match(r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', command)
        if coord_match:
            original_coords = [float(coord_match.group(1)), float(coord_match.group(2)), float(coord_match.group(3))]
            logging.debug(f"Extracted coordinates: {original_coords}")

        # Extract original block state
        block_match = re.search(r'block_state:{Name:"([^"]+)"}', command)
        if block_match:
            original_block = block_match.group(1)
            logging.debug(f"Extracted original block: {original_block}")

        # Modify coordinates if requested
        if gui.modify_coords.get() and original_coords:
            try:
                x = float(gui.pos_x_set.get()) if gui.pos_x_set.get() else original_coords[0]
                y = float(gui.pos_y_set.get()) if gui.pos_y_set.get() else original_coords[1]
                z = float(gui.pos_z_set.get()) if gui.pos_z_set.get() else original_coords[2]
                modified_command = re.sub(
                    r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',
                    f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f}',
                    modified_command
                )
            except ValueError:
                logging.warning("Invalid coordinate values, skipping coordinate modification")
                gui.print_to_text("Warning: Invalid coordinate values, skipping coordinate modification", "normal")

        # Modify block state if requested
        new_block = gui.block_text.get().strip() if gui.block_text.get() else (original_block or "minecraft:lime_concrete")
        if new_block and (not original_block or original_block != new_block):
            modified_command = re.sub(
                r'block_state:{Name:"[^"]+"}',
                f'block_state:{{Name:"{new_block}"}}',
                modified_command
            )

        # Log and update GUI
        gui.print_to_text(f"Input Command: {command}", "command")
        if original_coords:
            gui.print_to_text(f"Original Coordinates: {original_coords}", "coord")
        if original_block:
            gui.print_to_text(f"Original Block: {original_block}", "block_unchanged")
        gui.print_to_text(f"Modified Command: {modified_command}", "command")
        if original_coords:
            new_coord_match = re.search(r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', modified_command)
            if new_coord_match:
                new_coords = [float(new_coord_match.group(1)), float(new_coord_match.group(2)), float(new_coord_match.group(3))]
                logging.debug(f"New Coordinates: {new_coords}")
                gui.print_to_text(f"New Coordinates: {new_coords}", "modified_coord")
            else:
                logging.debug("Failed to extract new coordinates due to invalid format")
                gui.print_to_text("Warning: Failed to extract new coordinates.", "normal")
        if original_block and new_block != original_block:
            gui.print_to_text(f"New Block: {new_block}", "block_changed")

        # Update the textbox
        if hasattr(gui, 'change_block_cmd_text') and gui.change_block_cmd_text.winfo_exists():
            gui.change_block_cmd_text.delete("1.0", tk.END)
            gui.change_block_cmd_text.insert("1.0", modified_command)
        else:
            logging.warning("change_block_cmd_text not found or not initialized")
            gui.print_to_text("Warning: change_block_cmd_text not found or not initialized", "normal")

        pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))
        gui.print_to_text("Command copied to clipboard.", "normal")

    elif active_tab == "set coordinates":
        # Extract original coordinates
        coord_match = re.match(r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', command)
        if coord_match:
            original_coords = [float(coord_match.group(1)), float(coord_match.group(2)), float(coord_match.group(3))]
            logging.debug(f"Extracted coordinates: {original_coords}")

        # Modify coordinates if requested
        if gui.modify_coords.get() and original_coords:
            try:
                x = float(gui.pos_x_set.get()) if gui.pos_x_set.get() else original_coords[0]
                y = float(gui.pos_y_set.get()) if gui.pos_y_set.get() else original_coords[1]
                z = float(gui.pos_z_set.get()) if gui.pos_z_set.get() else original_coords[2]
                modified_command = re.sub(
                    r'/summon minecraft:block_display\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',
                    f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f}',
                    modified_command
                )
                gui.print_to_text(f"Original Coordinates: {original_coords}", "coord")
                gui.print_to_text(f"New Coordinates: [{x:.6f}, {y:.6f}, {z:.6f}]", "modified_coord")
            except ValueError:
                logging.warning("Invalid coordinate values, skipping coordinate modification")
                gui.print_to_text("Warning: Invalid coordinate values, skipping coordinate modification", "normal")

        # Update the textbox
        if hasattr(gui, 'cmd_text_set') and gui.cmd_text_set.winfo_exists():
            gui.cmd_text_set.delete("1.0", tk.END)
            gui.cmd_text_set.insert("1.0", modified_command)
        else:
            logging.warning("cmd_text_set not found or not initialized")
            gui.print_to_text("Warning: cmd_text_set not found or not initialized", "normal")

        pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))
        gui.print_to_text("Command copied to clipboard.", "normal")

    elif active_tab == "generate laser":
        # Generate laser command with fixed decimal parts
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

            modified_command = (
                f'/summon minecraft:block_display {x:.6f} {y:.6f} {z:.6f} '
                f'{{block_state:{{Name:"{block_type}"}},'
                f'transformation:{{translation:[0.5f,0.0f,0.0f],'
                f'scale:[0.1f,0.1f,{beam_scale:.6f}f],'
                f'left_rotation:[0.0f,0.0f,0.0f,1.0f],'
                f'right_rotation:[0.0f,0.0f,0.0f,1.0f]}},'
                f'brightness:15728880,shadow:false,billboard:"fixed",Tags:["{tag}"]}}'
            )
            logging.debug(f"Generated new laser command: {modified_command}")
            gui.print_to_text(f"Generated Command: {modified_command}", "command")

            # Update the textbox
            if hasattr(gui, 'laser_cmd_text') and gui.laser_cmd_text.winfo_exists():
                gui.laser_cmd_text.delete("1.0", tk.END)
                gui.laser_cmd_text.insert("1.0", modified_command)
            else:
                logging.warning("laser_cmd_text not found or not initialized")
                gui.print_to_text("Warning: laser_cmd_text not found or not initialized", "normal")

            pyperclip.copy(modified_command.encode('utf-8').decode('utf-8'))
            gui.print_to_text("Command copied to clipboard.", "normal")
        except ValueError as e:
            logging.error(f"Error generating laser command: {e}")
            gui.print_to_text("Error: Please enter valid numbers for coordinates and length.", "normal")

    return modified_command

def set_laser_preset(gui):
    """Set preset values for a laser in the GUI."""
    gui.modify_coords.set(True)
    gui.modify_translation.set(True)
    gui.modify_scale.set(True)
    gui.modify_centering.set(True)
    gui.pos_x_set.set("0.0")
    gui.pos_y_set.set("0.5")
    gui.pos_z_set.set("0.999999")
    gui.trans_x.set("0.5")
    gui.trans_y.set("0.0")
    gui.trans_z.set("0.0")
    gui.beam_scale.set("-150.0")
    gui.centering_x.set("0.0")
    gui.centering_y.set("0.0")
    gui.centering_z.set("0.0")
    gui.tag_text.set("beam1")
    gui.block_text.set("minecraft:lime_concrete")
    gui.laser_mode.set("laser")
    logging.debug("Set laser preset values")
    gui.print_to_text("Applied Laser preset", "normal")

def set_lightbeam_preset(gui):
    """Set preset values for a lightbeam in the GUI."""
    gui.modify_coords.set(True)
    gui.modify_translation.set(True)
    gui.modify_scale.set(True)
    gui.modify_centering.set(True)
    gui.pos_x_set.set("0.0")
    gui.pos_y_set.set("0.5")
    gui.pos_z_set.set("0.999999")
    gui.trans_x.set("0.0")
    gui.trans_y.set("0.0")
    gui.trans_z.set("0.0")
    gui.beam_scale.set("-75.0")
    gui.centering_x.set("0.0")
    gui.centering_y.set("0.0")
    gui.centering_z.set("0.0")
    gui.tag_text.set("lightbeam1")
    gui.block_text.set("minecraft:light_blue_concrete")
    gui.laser_mode.set("lightbeam")
    logging.debug("Set lightbeam preset values")
    gui.print_to_text("Applied Lightbeam preset", "normal")