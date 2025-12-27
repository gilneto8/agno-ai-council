import logging
import sys
import time
import uuid
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import contextlib

# Configure the logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique ID for the request
        request_id = str(uuid.uuid4())[:8]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = f"{timestamp}_{request_id}.log"
        log_filepath = LOGS_DIR / log_filename
        
        # Create a file to write logs to
        # We use a custom stream that writes to both the file and the original stream
        # so we don't lose console output.
        
        try:
            with open(log_filepath, "a", buffering=1) as log_file:
                # 1. Capture Python Logging
                file_handler = logging.FileHandler(log_filepath)
                file_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                file_handler.setFormatter(formatter)
                
                root_logger = logging.getLogger()
                root_logger.addHandler(file_handler)
                
                # 2. Capture Stdout/Stderr (e.g. for prints or rich output)
                # We define a helper class to tee the output
                class Tee:
                    def __init__(self, original, file):
                        self.original = original
                        self.file = file
                        
                    def write(self, message):
                        self.original.write(message)
                        self.file.write(message)
                        self.file.flush()
                        
                    def flush(self):
                        self.original.flush()
                        self.file.flush()
                        
                    def isatty(self):
                        return getattr(self.original, 'isatty', lambda: False)()
                
                original_stdout = sys.stdout
                original_stderr = sys.stderr
                
                sys.stdout = Tee(original_stdout, log_file)
                sys.stderr = Tee(original_stderr, log_file)
                
                # Add request_id to context if needed, or just log start
                logging.info(f"Starting request {request_id} - {request.method} {request.url}")
                
                try:
                    response = await call_next(request)
                    return response
                except Exception as e:
                    logging.exception(f"Request failed: {e}")
                    raise
                finally:
                    # Cleanup
                    logging.info(f"Finished request {request_id}")
                    
                    # Remove handler
                    root_logger.removeHandler(file_handler)
                    file_handler.close()
                    
                    # Restore streams
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    
        except Exception as e:
            # Fallback if logging setup fails
            print(f"Failed to setup logging for request: {e}")
            return await call_next(request)
