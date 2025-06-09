import logging
import re
import pyperclip
import keyboard
import tkinter as tk
from typing import Tuple, List, Optional

class CommandProcessor:
    def __init__(self):
        self.setup_keyboard_hook()

    def setup_keyboard_hook(self):
        keyboard.add_hotkey('F12', self.on_f12_press)
        logging.info("F12 keyboard hook initialized")

    def on_f12_press(self):
        logging.info("F12 pressed - capturing clipboard command")
        command = pyperclip.paste()
        if command.strip():
            if hasattr(self, 'gui'):
                self.gui.process_command(command)
            else:
                logging.error("GUI not set for command processing")
        else:
            if hasattr(self, 'gui'):
                self.gui.print_to_text("", "normal")
                self.gui.print_to_text("Input Command:", "normal")
                self.gui.print_to_text("Clipboard is empty or invalid. Copy a command before pressing F12.", "normal")
                self.gui.print_to_text("", "normal")

    def set_gui(self, gui):
        self.gui = gui

    def get_offsets(self, pos_x_offset: tk.StringVar, pos_y_offset: tk.StringVar, pos_z_offset: tk.StringVar,
                    target_x_offset: tk.StringVar, target_y_offset: tk.StringVar, target_z_offset: tk.StringVar) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        try:
            pos_offsets = (
                int(pos_x_offset.get()),
                int(pos_y_offset.get()),
                int(pos_z_offset.get())
            )
            target_offsets = (
                int(target_x_offset.get()),
                int(target_y_offset.get()),
                int(target_z_offset.get())
            )
            return pos_offsets, target_offsets
        except ValueError:
            logging.warning("Invalid offset values entered, using 0")
            return (0, 0, 0), (0, 0, 0)

    def get_set_values(self, pos_x_set: tk.StringVar, pos_y_set: tk.StringVar, pos_z_set: tk.StringVar,
                       target_x_set: tk.StringVar, target_y_set: tk.StringVar, target_z_set: tk.StringVar) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        try:
            pos_set = (
                int(pos_x_set.get()),
                int(pos_y_set.get()),
                int(pos_z_set.get())
            )
            target_set = (
                int(target_x_set.get()),
                int(target_y_set.get()),
                int(target_z_set.get())
            )
            return pos_set, target_set
        except ValueError:
            logging.warning("Invalid set values entered, using 0")
            return (0, 0, 0), (0, 0, 0)

    def modify_coordinates(self, command: str, use_set: bool, pos_x_var: tk.StringVar, pos_y_var: tk.StringVar, pos_z_var: tk.StringVar,
                           target_x_var: tk.StringVar, target_y_var: tk.StringVar, target_z_var: tk.StringVar,
                           block_text: tk.StringVar) -> Tuple[str, List[int], Optional[str]]:
        logging.debug(f"Modifying coordinates for command: {command}")
        if use_set:
            pos_values, target_values = self.get_set_values(pos_x_var, pos_y_var, pos_z_var, target_x_var, target_y_var, target_z_var)
        else:
            pos_offsets, target_offsets = self.get_offsets(pos_x_var, pos_y_var, pos_z_var, target_x_var, target_y_var, target_z_var)

        original_coords = [int(x) for x in re.findall(r'-?\d+\b', command) if x.lstrip('-').isdigit()]
        original_block = None
        block_match = re.search(r'(?:setblock\s+-?\d+\s+-?\d+\s+-?\d+\s+)(minecraft:\w+|\w+)', command)
        if block_match:
            original_block = block_match.group(1)

        summon_pattern = re.compile(r'(summon end_crystal\s+)(-?\d+)(\s+)(-?\d+)(\s+)(-?\d+)(.*?(?:BeamTarget:\{|\],\{).*?X:)(-?\d+)(.*?Y:)(-?\d+)(.*?Z:)(-?\d+)(.*?\}\})')
        summon_match = summon_pattern.search(command)
        if summon_match:
            logging.debug(f"Summon match groups: {summon_match.groups()}")
            x1 = pos_values[0] if use_set else int(summon_match.group(2)) + pos_offsets[0]
            y1 = pos_values[1] if use_set else int(summon_match.group(4)) + pos_offsets[1]
            z1 = pos_values[2] if use_set else int(summon_match.group(6)) + pos_offsets[2]
            x2 = target_values[0] if use_set else int(summon_match.group(8)) + target_offsets[0]
            y2 = target_values[1] if use_set else int(summon_match.group(10)) + target_offsets[1]
            z2 = target_values[2] if use_set else int(summon_match.group(12)) + target_offsets[2]
            result = f"{summon_match.group(1)}{x1}{summon_match.group(3)}{y1}{summon_match.group(5)}{z1}{summon_match.group(7)}{x2}{summon_match.group(9)}{y2}{summon_match.group(11)}{z2}{summon_match.group(13)}"
            logging.debug(f"Summon command modified: {result}")
            return result, original_coords, None

        coords_pattern = r'-?\d+(?:\s*-?\d+){2}'
        coords_match = re.search(coords_pattern, command)
        if coords_match and "summon" in command and not summon_match:
            logging.debug(f"Malformed summon input detected, extracting coordinates: {coords_match.group()}")
            coords = re.findall(r'-?\d+', coords_match.group())
            if len(coords) >= 3:
                x1, y1, z1 = map(int, coords[:3])
                x2, y2, z2 = target_values if use_set else (x1 + target_offsets[0], y1 + target_offsets[1], z1 + target_offsets[2])
                beam_target_match = re.search(r'BeamTarget:\{.*?X:(-?\d+).*?Y:(-?\d+).*?Z:(-?\d+).*?\}', command)
                if beam_target_match:
                    x2 = target_values[0] if use_set else int(beam_target_match.group(1)) + target_offsets[0]
                    y2 = target_values[1] if use_set else int(beam_target_match.group(2)) + target_offsets[1]
                    z2 = target_values[2] if use_set else int(beam_target_match.group(3)) + target_offsets[2]
                result = f"summon end_crystal {x1} {y1} {z1} {{ShowBottom:0b,Invulnerable:1b,Tags:[\"laser\"],BeamTarget:{{X:{x2},Y:{y2},Z:{z2}}}}}"
                original_coords = [x1, y1, z1] + ([int(beam_target_match.group(1)), int(beam_target_match.group(2)), int(beam_target_match.group(3))] if beam_target_match else [])
                logging.debug(f"Reconstructed summon command: {result}")
                return result, original_coords, None

        setblock_pattern = re.compile(r'(setblock\s+)(-?\d+)(\s+)(-?\d+)(\s+)(-?\d+)(\s+(minecraft:\w+|\w+))')
        setblock_match = setblock_pattern.search(command)
        if setblock_match:
            logging.debug(f"Setblock match groups: {setblock_match.groups()}")
            x = pos_values[0] if use_set else int(setblock_match.group(2)) + pos_offsets[0]
            y = pos_values[1] if use_set else int(setblock_match.group(4)) + pos_offsets[1]
            z = pos_values[2] if use_set else int(setblock_match.group(6)) + pos_offsets[2]
            original_block_text = setblock_match.group(7)
            new_block_text = block_text.get().strip() if self.gui.notebook.tab(self.gui.notebook.select(), "text") == "Change Block" else original_block_text
            result = f"{setblock_match.group(1)}{x}{setblock_match.group(3)}{y}{setblock_match.group(5)}{z} {new_block_text}"  # Added space before new_block_text
            logging.debug(f"Setblock command modified: {result}")
            return result, original_coords, original_block_text

        kill_pattern = re.compile(r'(kill @e\[[^]]*x=)(-?\d+)([^,]*,\s*y=)(-?\d+)([^,]*,\s*z=)(-?\d+)([^]]*\])')
        kill_match = kill_pattern.search(command)
        if kill_match:
            logging.debug(f"Kill match groups: {kill_match.groups()}")
            x = pos_values[0] if use_set else int(kill_match.group(2)) + pos_offsets[0]
            y = pos_values[1] if use_set else int(kill_match.group(4)) + pos_offsets[1]
            z = pos_values[2] if use_set else int(kill_match.group(6)) + pos_offsets[2]
            result = f"{kill_match.group(1)}{x}{kill_match.group(3)}{y}{kill_match.group(5)}{z}{kill_match.group(7)}"
            logging.debug(f"Kill command modified: {result}")
            return result, original_coords, None

        logging.debug("No modification applied")
        return command, original_coords, None
