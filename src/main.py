# Updated on 08:20 PM CDT, Monday, July 07, 2025
import logging
import tkinter as tk
from src.command_processor import CommandProcessor
from src.gui_main import CommandModifierGUI
from src.utils import setup_logging, cleanup

def main():
    try:
        setup_logging()  # Configure logging
        logging.info("Application started (F12 clipboard mode with GUI)")

        # Initialize Tkinter root
        root = tk.Tk()

        # Initialize CommandProcessor
        command_processor = CommandProcessor()
        if not hasattr(command_processor, 'set_gui'):
            logging.error("CommandProcessor does not have set_gui method")
            raise AttributeError("CommandProcessor missing set_gui method")

        # Initialize GUI
        gui = CommandModifierGUI(root)
        command_processor.set_gui(gui)

        # Run the application
        root.mainloop()
    except Exception as e:
        logging.error(f"Application crashed: {str(e)}", exc_info=True)
        raise
    finally:
        logging.info("Application shutdown completed")
        cleanup()  # Clean up logging handlers

if __name__ == "__main__":
    main()