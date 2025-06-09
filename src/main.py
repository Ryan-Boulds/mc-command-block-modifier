import logging
from src.command_processor import CommandProcessor
from src.gui import CommandModifierGUI

def main():
    logging.basicConfig(
        filename="C:/Users/ryant/IdeaProjects/MInecraft Command Block Modifiers/logs/survey.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
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

if __name__ == "__main__":
    main()