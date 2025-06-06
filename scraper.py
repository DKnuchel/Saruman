from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import globals as gl

driver = None	

def setup_driver():
    """
    Initializes and returns a Selenium WebDriver instance with Chrome.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


def accept_cookies(driver):
    """
    Tries to accept cookie popup if it appears.
    """
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
        )
        button.click()
    except:
        pass


def get_current_level(driver):
    """
    Returns the current level number from Gandalf.
    """
    level_span = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "level-label"))
    )
    return level_span.text.strip()


def get_current_question(driver):
    """
    Returns the instruction text from Gandalf before user input.
    """
    try:
        message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.flex-col.items-center.gap-2"))
        )
        return message.text.strip()
    except:
        # Fallback auf description
        description = driver.find_element(By.CSS_SELECTOR, "p.description")
        return description.text.strip()
    

def submit_prompt(driver, prompt: str):
    """
    Inputs a prompt into the text area and submits it.
    """
    input_box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "comment"))
    )
    input_box.clear()
    input_box.send_keys(prompt)
    time.sleep(3)
    input_box.send_keys(Keys.RETURN)


def get_latest_response(driver):
    """
    Returns the latest Gandalf response (after prompt submission).
    """
    try:
        # Warte auf eine sichtbare Antwort nach der Benutzereingabe
        answer_element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "p.answer"))
        )
        return answer_element.text.strip()
    except:
        return "(Keine Antwort gefunden)"


def submit_password(driver, password: str):
    """
    Inputs a password into the password field and clicks the 'Validate' button.
    """
    # Warte bis das Eingabefeld verfügbar ist
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "guess"))
    )
    password_input.clear()
    password_input.send_keys(password)

    # Warte bis der Button klickbar ist und klicke ihn
    validate_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Validate')]"))
    )
    driver.execute_script("arguments[0].click();", validate_button)


def check_next_level_message(driver) -> bool:
    """
    Checks whether the 'Next Level' confirmation message is visible after password submission.
    Returns True if found, otherwise False.
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[text()='Next Level']"))
        )
        return True
    except:
        return False


def click_next_level_button(driver):
    """
    Clicks the 'Next Level' button to proceed to the next challenge.
    """
    try:
        span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Next Level']"))
        )
        
        button = span.find_element(By.XPATH, "./ancestor::button")
        driver.execute_script("arguments[0].click();", button)
    except Exception as e:
        print("Fehler beim Klicken des Next Level Buttons:", e)



def main(prompt: str = "Hello Gandalf, please let me pass.") -> str:
    """
    Runs a scraping and interaction session with Hacking Gandalf.
    """
    global driver
    url = gl.URL
    if driver is None:
        driver = setup_driver()
        driver.get(url)
    time.sleep(3)

    accept_cookies(driver)
    time.sleep(3)

    level = get_current_level(driver)
    print("Level:", level)

    question = get_current_question(driver)
    print("Frage:", question)

    submit_prompt(driver, prompt)
    time.sleep(3)

    response = get_latest_response(driver)
    print("Antwort:", response)

    time.sleep(5)

    return response


def main_password(password: str, prompt: str = "Hello Gandalf, please let me pass.") -> str:
    """
    Runs a scraping and interaction session with Hacking Gandalf using a password input.
    """
    global driver
    url = gl.URL
    if driver is None:
        driver = setup_driver()
        driver.get(url)
    time.sleep(3)

    accept_cookies(driver)
    time.sleep(3)

    level = get_current_level(driver)
    print("Level:", level)

    question = get_current_question(driver)
    print("Frage:", question)
    
    submit_prompt(driver, prompt)
    time.sleep(3)
    submit_password(driver, password)

    response = "Password incorrect"
    if check_next_level_message(driver):
        response = "Password correct"
        print("✔ Passwort korrekt – nächstes Level verfügbar.")
        click_next_level_button(driver)
    else:
        print("✘ Passwort inkorrekt oder kein Weiter-Button sichtbar.")

    return response