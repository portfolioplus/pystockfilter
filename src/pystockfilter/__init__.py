__version__ = "2.3.0"
import os
import sys  
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


import logging

def setup_module_logger(name, level=logging.INFO, file_name=None):
    """
    Sets up a logger with the specified name, logging level, and optional file handler.

    Args:
        name (str): The name of the logger.
        level (int): Logging level, default is logging.INFO.
        file_name (str): Optional file name to write logs to a file.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(ch)
    
    # Optionally add a file handler
    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger

# Configure the module-wide logger
module_logger = setup_module_logger(name="pystockfilter")

# Optionally, add the logger to the module's globals
globals()['logger'] = module_logger