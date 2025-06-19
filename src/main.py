import logging
from src.command_processor import CommandProcessor
from src.gui_main import CommandModifierGUI
from src.utils import setup_logging, cleanup

def main():
    setup_logging()  # Use utils.py logging setup
    logging.info("Application started (F12 clipboard mode with GUI)")

    command_processor = CommandProcessor()
    gui = CommandModifierGUI(command_processor)
    command_processor.set_gui(gui)

    try:
        gui.run()
    except Exception as e:
        logging.error(f"Application crashed: {str(e)}")
    finally:
        logging.info("Application shutdown completed")
        cleanup()  # Clean up logging handlers

if __name__ == "__main__":
    main()