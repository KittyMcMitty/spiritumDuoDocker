from dataclasses import dataclass
from random import randint
from time import sleep
from typing import List
import pytest
from os import environ
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


@dataclass
class ServerEndpoints():
    app: str
    api: str


@dataclass
class RoleDetails():
    name: str
    permissions: List[str]


@dataclass
class PathwayDetails():
    name: str
    clinical_requests: List[str]


@dataclass
class MdtDetails():
    location: str


@dataclass
class UserDetails():
    username: str
    password: str
    department: str
    email: str
    firstName: str
    lastName: str
    roles: List[str]
    pathways: List[str]


@pytest.fixture
def endpoints():
    hostname: str = (
            'SELENIUM_HOSTNAME' in environ
            and (
                environ['SELENIUM_HOSTNAME']
            ) or 'http://localhost'
        )
    return ServerEndpoints(
        app=hostname + "/app",
        api=hostname + "/api"
    )


@pytest.fixture
def driver():
    browser_choice: str = (
        'SELENIUM_BROWSER_CLIENT' in environ
        and environ['SELENIUM_BROWSER_CLIENT']
        or 'firefox'
    ).lower()

    if browser_choice == "firefox":
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--start-maximized")
        driver = webdriver.Firefox(
            # service=FirefoxService(GeckoDriverManager().install()),
            options=options
        )
        driver.set_window_size(1920, 1080)

    elif browser_choice == "chromium":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-dev-shm-using")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--ignore-certificate-errors")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager(
                chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )
        driver.set_window_size(1920, 1080)

    elif browser_choice == "safari":
        driver = webdriver.Safari()
        driver.set_window_size(1920, 1080)
        driver.switch_to.frame(0)  # set frame to default, safari fix?

    elif browser_choice == "edge":
        options = EdgeOptions()

        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-dev-shm-using")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--ignore-certificate-errors")

        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()),
            options=options,
        )

        driver.set_window_size(1920, 1080)

    driver.implicitly_wait(10)
    yield driver
    driver.close()


@pytest.fixture
def login_user(driver: webdriver.Remote, endpoints: ServerEndpoints):

    driver.get(endpoints.app)
    # username field
    driver.find_element(By.NAME, "username").send_keys("demo-1-2")

    # password field
    driver.find_element(By.NAME, "password").send_keys("22password1")

    # submit button
    driver.find_element(By.ID, "submit").send_keys(Keys.ENTER)


@pytest.fixture
def test_role(
    driver: webdriver.Remote, endpoints: ServerEndpoints,
    login_user: None
):

    role_details = RoleDetails(
        name="test-role",
        permissions=["AUTHENTICATED"]
    )

    sleep(1)
    driver.get(f"{endpoints.app}/admin")
    driver.find_element(
        By.XPATH,
        "//li[contains(text(), 'Roles management')]"
    ).click()

    driver.find_element(
        By.XPATH,
        "//li[contains(text(), 'Create role')]"
    ).click()

    driver.find_element(By.NAME, "name").send_keys(
        role_details.name
    )

    permissions_section = driver.find_element(
        By.XPATH, "//*[contains(text(), 'Role permissions')]/../div"
    )

    for permission in role_details.permissions:
        permissions_section.click()

        permissions_section.find_element(
            By.XPATH, f".//div/*[contains(text(), '{permission}')]"
        ).click()

    submit = driver.find_element(
        By.XPATH, "//button[contains(text(), 'Create role')]"
    )
    submit.click()

    return role_details


@pytest.fixture
def test_pathways(
    driver: webdriver.Remote, endpoints: ServerEndpoints,
    login_user: None
):
    pathway_details = [
        PathwayDetails(
            name="Test pathway",
            clinical_requests=[
                "Referral letter (Referral letter (record artifact))"
            ]
        ),
        PathwayDetails(
            name="Test pathway two",
            clinical_requests=[
                "Referral letter (Referral letter (record artifact))"
            ]
        )
    ]

    sleep(1)
    for pathway in pathway_details:
        driver.get(f"{endpoints.app}/admin")
        driver.find_element(
            By.XPATH,
            "//li[contains(text(), 'Pathway management')]"
        ).click()

        driver.find_element(
            By.XPATH,
            "//li[contains(text(), 'Create pathway')]"
        ).click()

        driver.find_element(By.NAME, "name").send_keys(
            pathway.name
        )

        requests_section = driver.find_element(
            By.XPATH, "//*[contains(text(), 'Clinical request types')]/../div"
        )

        for requests in pathway.clinical_requests:
            requests_section.click()

            requests_section.find_element(
                By.XPATH, f".//div/*[contains(text(), '{requests}')]"
            ).click()

        submit = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Create pathway')]"
        )
        submit.click()

    return pathway_details


@pytest.fixture
def test_mdt(
    driver: webdriver.Remote, endpoints: ServerEndpoints,
    login_user: None
): 
    mdt_details = MdtDetails(
        location="test location"
    )
    sleep(1)
    driver.get(f"{endpoints.app}/mdt")
    driver.find_element(
        By.XPATH,
        "//button[contains(text(), 'Create MDT')]"
    ).click()

    date_selector = driver.find_element(
        By.XPATH, "//*[contains(text(), 'Date of MDT')]")
    date_selector.click()

    date_selection = driver.find_elements(
        By.CLASS_NAME, "react-datepicker__day")
    date_selection[-2].click()

    location_input = driver.find_element(By.NAME, "location")
    location_input.send_keys(mdt_details.location)

    modal = driver.find_element(By.CLASS_NAME, "modal-content")

    submit_button = modal.find_element(
        By.XPATH, ".//button[contains(text(), 'Create')]")
    submit_button.click()

    driver.find_element(
        By.XPATH, "//button[contains(text(), 'Close')]"
    ).click()

    return mdt_details


@pytest.fixture
def test_user(
    driver: webdriver.Remote, endpoints: ServerEndpoints,
    login_user: None
):
    user_details = UserDetails(
        username="test_user_" + str(randint(1, 100)),
        password="test password",
        department="test department",
        email=f"test{randint(1, 100)}@test.com",
        firstName="test",
        lastName="runner",
        roles=["admin"],
        pathways=["cancer demo 1"],
    )

    sleep(1)
    driver.get(f"{endpoints.app}/admin")
    driver.find_element(
        By.XPATH,
        "//li[contains(text(), 'Users')]"
    ).click()

    driver.find_element(
        By.XPATH,
        "//li[contains(text(), 'Create user')]"
    ).click()

    driver.find_element(By.NAME, "firstName").send_keys(
        user_details.firstName
    )
    driver.find_element(By.NAME, "lastName").send_keys(
        user_details.lastName
    )
    driver.find_element(By.NAME, "username").send_keys(
        user_details.username
    )
    driver.find_element(By.NAME, "password").send_keys(
        user_details.password
    )
    driver.find_element(By.NAME, "email").send_keys(
        user_details.email
    )
    driver.find_element(By.NAME, "department").send_keys(
        user_details.department
    )
    driver.find_element(By.NAME, 'isActive').click()

    roles_section = driver.find_element(
        By.XPATH, "//label[contains(text(), 'Roles')]"
    )
    roles_input = roles_section.find_element(By.XPATH, "./div")

    for role in user_details.roles:
        roles_input.click()
        roles_input.find_element(
            By.XPATH, f".//*[contains(text(), '{role}')]"
        ).click()

    pathways_section = driver.find_element(
        By.XPATH, "//label[contains(text(), 'Pathways')]"
    )
    pathways_input = pathways_section.find_element(By.XPATH, "./div")
    for pathway in user_details.pathways:
        pathways_input.click()
        pathway = pathways_input.find_element(
            By.XPATH, f".//div/*[contains(text(), '{pathway}')]"
        )

    pathway.click()

    submit = driver.find_element(
        By.XPATH, "//button[contains(text(), 'Create User')]"
    )
    submit.click()

    return user_details
