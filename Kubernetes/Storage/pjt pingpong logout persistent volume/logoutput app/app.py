import time
import uuid
from datetime import datetime, timezone

output_file = "log.txt"

try:
    while True:
        # Generate UTC Timestamp with milliseconds
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"
        
        # Generate a UUID4 suffix
        random_suffix = str(uuid.uuid4())

        log_entry = f"{timestamp}: {random_suffix}\n"
        
        with open(output_file, "a") as f:
            f.write(log_entry)
        
        print(log_entry.strip())
        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopped.")   