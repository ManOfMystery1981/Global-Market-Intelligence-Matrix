import os
import time
import sys

# Force unbuffered terminal print parsing
sys.stdout.reconfigure(line_buffering=True)

def purge_stale_marketing_assets(target_directory="./posts", max_age_seconds=172800):
    """
    Scans the local storage partition folder path to identify and purge 
    stale markdown landing page assets older than 48 hours.
    """
    print(f"🧹 Initializing automated content cleanup loop inside: {target_directory}")
    if not os.path.exists(target_directory):
        print("📁 Directory not found. Skipping content processing loop.")
        return

    current_time = time.time()
    purged_count = 0

    try:
        for filename in os.listdir(target_directory):
            file_path = os.path.join(target_directory, filename)
            
            # Target explicit markdown generated files only
            if os.path.isfile(file_path) and filename.endswith(".md"):
                file_modification_time = os.path.getmtime(file_path)
                file_age = current_time - file_modification_time
                
                # Check if the file age crosses our 48-hour system threshold
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    print(f"🗑️ Purged legacy static asset file from disk: {filename}")
                    purged_count += 1
                    
        print(f"✅ Cleanup run complete. Total legacy files cleared from matrix: {purged_count}")
    except Exception as e:
        print(f"⚠️ Content purging loop encountered execution anomalies: {e}")

if __name__ == "__main__":
    purge_stale_marketing_assets()
