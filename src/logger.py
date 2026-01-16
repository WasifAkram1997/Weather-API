import logging
import sys
import os

def setup_logger():
    """Configure logging for the application"""

    #Create logger instance
    logger = logging.getLogger()

    #Retreive environment
    env = os.getenv("ENV", "development")

    #Setting log level based on environment
    if env == "production":
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.DEBUG)

    #Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    #Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logger