import time
import random
import string
from datetime import datetime, timezone

output_file = "log.txt"

try:
    while True:
        # Generate UTC Timestamp with milliseconds
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"
        
        # Generate 6-character alphanumeric string (letters + digits)
        # string.ascii_lowercase + string.digits covers 'a-z' and '0-9'
        chars = string.ascii_lowercase + string.digits
        random_suffix = ''.join(random.choices(chars, k=6))
        
        log_entry = f"{timestamp}: {random_suffix}\n"
        
        with open(output_file, "a") as f:
            f.write(log_entry)
        
        print(log_entry.strip())
        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopped.")   