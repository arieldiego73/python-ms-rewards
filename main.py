import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
import time
import subprocess
import random
from searches import search

def main():
    print(os.environ.get('USER_DATA_DIR'))

    profile_dir_dict = [
        {"profile": "Profile 7", "recursion": 10},
        {"profile": "Profile 6", "recursion": 10},
        {"profile": "Profile 1", "recursion": 30}
    ]

    try:
        for profile_dir in profile_dir_dict:
            # Ensure the user data directory exists
            if not os.path.exists(os.environ.get('USER_DATA_DIR')):
                print(f"User data directory does not exist: {os.environ.get('USER_DATA_DIR')}")
                return

            # Ensure the profile directory exists
            profile_path = os.path.join(os.environ.get('USER_DATA_DIR'), profile_dir["profile"])
            if not os.path.exists(profile_path):
                print(f"Profile directory does not exist: {profile_path}")
                return

            # Kill any existing Edge processes
            kill_edge_processes()

            # Set up Edge options to use the specified profile
            options = Options()
            options.add_argument(f"user-data-dir={os.environ.get('USER_DATA_DIR')}")
            options.add_argument(f"profile-directory={profile_dir["profile"]}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")

            # Initialize the Edge WebDriver
            service = EdgeService(EdgeChromiumDriverManager().install())

            try:
                driver = webdriver.Edge(service=service, options=options)

                # Adding a short delay before starting to ensure proper initialization
                time.sleep(2)

                # Open the Edge browser and navigate to a search engine
                driver.get("https://www.bing.com")

                search_count = 0
                for _ in range(profile_dir["recursion"]):
                    search_count += 1
                    
                    # Locate the search box, enter a query, and perform the search
                    search_box = driver.find_element(By.NAME, "q")
                    search_box.send_keys(random.choice(search).lower())
                    search_box.submit()
                    
                    search_interval = math.floor(random.uniform(int(os.environ.get('MIN_SEARCH_INTERVAL')), int(os.environ.get('MAX_SEARCH_INTERVAL'))))
                    log_progress(profile_dir, profile_dir["recursion"], search_count, int(search_interval))

                    search_box = driver.find_element(By.NAME, "q")
                    search_box.clear()
                
                # Wait for the results to load (implicit wait)
                driver.implicitly_wait(15)

            except Exception as e:
                print("Error during WebDriver execution:", e)
    finally:
        if 'driver' in locals():
            driver.quit()
            print("DONE! Pweh, another day of MS Reward Points, huh?")

def kill_edge_processes():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill existing Edge processes: {e}")

def log_progress(profile, total_search_num, search_count, search_interval):
    print("-------------------------------------------------")
    for i in range(1, search_interval + 1):
        print(f"{profile.get("profile")} | Search #{search_count} out of {total_search_num} ({search_interval - i} sec/s)")
        time.sleep(1)

if __name__ == "__main__":
    main()
