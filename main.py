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
    profile_dir_dict = [
        {"profile": "Profile 7", "recursion": 10},
        {"profile": "Profile 6", "recursion": 10},
        {"profile": "Profile 1", "recursion": 30}
    ]
    search_history = []

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

                driver.get("https://www.bing.com")

                search_count = 0
                for _ in range(profile_dir["recursion"]):
                    search_count += 1
                    search_target = ""
                    is_search_target_unique = False
                    
                    while not is_search_target_unique:
                        search_target = random.choice(search).lower()
                        if not search_target in search_history:
                            search_history.append(search_target)
                            is_search_target_unique = True

                    search_box = driver.find_element(By.NAME, "q")
                    search_box.send_keys(search_target)
                    search_box.submit()
                    
                    search_interval = random.randint(int(os.environ.get('MIN_SEARCH_INTERVAL')), int(os.environ.get('MAX_SEARCH_INTERVAL')))
                    log_progress(driver, profile_dir, profile_dir["recursion"], search_count, search_interval)

                    search_box = driver.find_element(By.NAME, "q")
                    search_box.clear()

            except Exception as e:
                print("Error during WebDriver execution:", e)
    finally:
        if 'driver' in locals():
            driver.quit()

def kill_edge_processes():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill existing Edge processes: {e}")

def log_progress(driver, profile, total_search_num, search_count, search_interval):
    print("-------------------------------------------------")
    for i in range(1, search_interval + 1):
        percentage = (i / search_interval) * 100
        print(f"{profile.get("profile")} | Search #{search_count} out of {total_search_num} ({percentage:.2f}%)")

        if random.choice([0, 1]) == 1:
            total_scroll_distance = random.randint(200, 500)
            scroll_step = 1
            current_scroll = 0
            while current_scroll < total_scroll_distance:
                driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_step)
                current_scroll += scroll_step
        
        time.sleep(0.1)

if __name__ == "__main__":
    main()
