from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from util import global_var as g
from util.exception import ErrorException

WAIT_TIMEOUT_SEC = 10  # 等待网络延迟，最多10秒
head_less = False  # 不显示浏览器

def create() -> WebDriver:
    """

    :rtype: WebDriver
    """
    # 创建一个Browser
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    options.add_argument("start-maximized")  # https://stackoverflow.com/a/26283818/1689770
    options.add_argument("enable-automation")  # https://stackoverflow.com/a/43840128/1689770

    # 无头
    if head_less:
        options.add_argument("--headless")  # only if you are ACTUALLY running headless

    # 无图像
    options.add_argument("blink-settings=imagesEnabled=false")

    options.add_argument("--no-sandbox")  # https://stackoverflow.com/a/50725918/1689770
    options.add_argument("--disable-dev-shm-usage")  # https://stackoverflow.com/a/50725918/1689770
    options.add_argument("--disable-driver-side-navigation")  # https://stackoverflow.com/a/49123152/1689770
    options.add_argument(
        "--disable-gpu")  # https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc

    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
    })
    # myBrowser.execute_script('document.title = "' + gConfigInfo.email + '必中！"')
    driver.implicitly_wait(10)
    return driver


def destroy(driver: WebDriver):
    if driver is not None:
        if driver.service.is_connectable():
            driver.quit()

def open_login_page(driver, country):
    driver.get("https://ais.usvisa-info.com/en-%s/niv/users/sign_in" % country)
    # 等待commit按钮真正出现，才代表成功打开了login页面
    try:
        element_present = EC.presence_of_element_located((By.NAME, "commit"))
        WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
        return True
    except TimeoutException:
        return False

def login(driver, user_name, password):
    email_box = driver.find_element(By.ID, "user_email")
    email_box.clear()
    email_box.send_keys(user_name)
    password_box = driver.find_element(By.ID, "user_password")
    password_box.clear()
    password_box.send_keys(password)
    driver.execute_script("document.getElementById('policy_confirmed').click()")
    signin_button = driver.find_element(By.NAME, "commit")
    signin_button.click()

def move_from_group_to_pay(driver: WebDriver):

    # Continue
    continue_button_xpath = "//a[contains(text(), 'Continue')]"
    element_present = EC.presence_of_element_located((By.XPATH, continue_button_xpath))
    WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
    continue_button = driver.find_element(By.XPATH, continue_button_xpath)
    continue_button.click()

    # Choose action
    pay_button_xpath = "//a[contains(text(), 'Pay Visa Fee')]"
    element_present = EC.presence_of_element_located((By.XPATH, pay_button_xpath))
    WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
    banner = driver.find_element(By.TAG_NAME, 'h5')
    banner.click()
    element_present = EC.element_to_be_clickable((By.XPATH, pay_button_xpath))
    WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
    pay_button = driver.find_element(By.XPATH, pay_button_xpath)
    pay_button.click()

    # 取得session
    current_url = driver.current_url
    schedule_id = current_url.split("/")[-2]
    session = driver.get_cookie("_yatri_session")["value"]
    user_agent = driver.execute_script("return navigator.userAgent")

    return schedule_id, session, user_agent

def get_grp_by_ivr(driver: WebDriver, input_ivr):
    grp_list = driver.find_elements(By.CSS_SELECTOR, ".application.card")

    for grp in grp_list:
        ivr = grp.find_element(By.CSS_SELECTOR, ".medium-12.columns.text-right  strong").text
        if ivr == input_ivr:
            return grp

    return None

STATUS_ATTEND_APPOINTMENT = 1
STATUS_SCHEDULE_APPOINTMENT = 2

def get_status(grp: WebElement) -> int:
    status = grp.find_element(By.CLASS_NAME, "status").text
    if status.find("Attend Appointment") >= 0:
        return STATUS_ATTEND_APPOINTMENT
    elif status.find("Schedule Appointment") >= 0:
        return STATUS_SCHEDULE_APPOINTMENT
    else:
        return -1


def get_appl_list_by_grp(grp: WebElement):
    appl_list = []

    row_list = grp.find_elements(By.XPATH, "./table/tbody/tr")
    for row in row_list:
        col_list = row.find_elements(By.XPATH, "./td")
        link = row.find_element(By.XPATH, ".//a[contains(text(), 'Details')]")
        url = link.get_attribute('href')
        splited_url = url.split("/")
        schedule_id = splited_url[-3]
        appl_id = splited_url[-1]

        appl = {
            "Applicant Name": col_list[0].text,
            "Passport": col_list[1].text,
            "DS-160": col_list[2].text,
            "Visa Class": col_list[3].text,
            "Status": col_list[4].text,
            "Document Return": (col_list[4].text.find("Courier Shipping Number") != -1),
            "Schedule ID": schedule_id,
            "Applicant ID": appl_id
        }
        appl_list.append(appl)

    return appl_list


def move_from_group_to_action(grp: WebElement):
    continue_btn = grp.find_element(By.LINK_TEXT, "Continue")
    continue_btn.click()


def have_reschedule_bar(driver: WebDriver):
    try:
        pay_button_xpath = "//a[contains(text(), 'Reschedule Appointment')]"
        element_present = EC.presence_of_element_located((By.XPATH, pay_button_xpath))
        WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
        return True
    except TimeoutException:
        return False


def get_apted_info(grp: WebElement):
    # 取得预约信息，格式如下：
    # Consular Appointment: 21 September, 2022, 09:30 Québec local time at Quebec City
    # Consular Appointment: 7 December, 2022, 11:00 Toronto local time at Toronto — get directions
    # apted_info = "Consular Appointment: 21 September, 2022, 09:30 Québec local time at Quebec City"
    apted_info = grp.find_element(By.CSS_SELECTOR, ".consular-appt").text
    apted_info = apted_info.replace(",", "").replace(" — get directions", "")
    split_all = apted_info.split(" ")
    split_hhmm = split_all[5].split(":")
    split_city = apted_info.split(" at ")
    city_name = split_city[-1]
    day_str, month_str, year_str, hh_str, mm_str = split_all[2], split_all[3], split_all[4], split_hhmm[0], split_hhmm[1]
    year, month, day, hh, mm = int(year_str), g.MONTH[month_str], int(day_str), int(hh_str), int(mm_str)
    return [city_name, (year, month, day, hh, mm)]

def move_from_action_to_schedule(driver: WebDriver, country: str, ppl_cnt: int):
    # 取得schedule页面的URL
    current_url = driver.current_url
    schedule_id = current_url.split("/")[-2]
    SCHEDULE_URL = "https://ais.usvisa-info.com/en-%s/niv/schedule/%s/appointment" % (country, schedule_id)

    # 跳转到schedule页面，并等到city显示出来
    driver.get(SCHEDULE_URL)
    city_elm_id = "appointments_consulate_appointment_facility_id"

    # 如果多余1人的话，需要跳过人员选择页面
    if ppl_cnt > 1:
        element_present = EC.element_to_be_clickable((By.NAME, "commit"))
        WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
        driver.find_element(By.NAME, "commit").click()

    # schedule页面成功显示
    element_present = EC.presence_of_element_located((By.ID, city_elm_id))
    WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)

    # 取得session
    session = driver.get_cookie("_yatri_session")["value"]
    user_agent = driver.execute_script("return navigator.userAgent")

    return schedule_id, session, user_agent

def get_post_base_info(driver: WebDriver, country_code, schedule_id, user_agent):
    post_data = {
        "utf8": driver.find_element(by=By.NAME, value='utf8').get_attribute('value'),
        "authenticity_token": driver.find_element(by=By.NAME, value='authenticity_token').get_attribute(
            'value'),
        "confirmed_limit_message": driver.find_element(by=By.NAME, value='confirmed_limit_message').get_attribute(
            'value'),
        "use_consulate_appointment_capacity": driver.find_element(
            by=By.NAME, value='use_consulate_appointment_capacity').get_attribute('value'),
        "commit": "Schedule+Appointment"
    }
    post_url = "https://ais.usvisa-info.com/en-%s/niv/schedule/%s/appointment" % (country_code, schedule_id)
    post_header = {
        "User-Agent": user_agent,
        "Referer": post_url
    }

    return post_header, post_data


if __name__ == '__main__':
    a = get_apted_info(None)


def is_login_success(driver: WebDriver):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "user-info-footer"))
        WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
        return True
    except TimeoutException:
        return False


def is_wrong_password(driver: WebDriver):
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Invalid email or password')]"))
        WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
        return True
    except TimeoutException:
        return False


def is_ais_maintenance(driver: WebDriver):
    try:
        element_present = EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Doing Maintenance')]"))
        WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
        return True
    except TimeoutException:
        return False

from util import db
def is_tcn_right(driver: WebDriver, country: str, ivr: str, is_tcn: bool):
    tcn_type = db.tcn_def.get(country)[0]
    if tcn_type not in [1, 2, 3]:
        return True

    grp = get_grp_by_ivr(driver, ivr)
    appl_list = get_appl_list_by_grp(grp)
    is_tcn_equal = True
    for appl in appl_list:

        if tcn_type == 1:
            driver.get(f"https://ais.usvisa-info.com/en-{country}/niv/schedule/{appl.get('Schedule ID')}/applicants/{appl.get('Applicant ID')}/edit")
            # 等待commit按钮真正出现，才代表成功打开了login页面
            try:
                element_present = EC.presence_of_element_located((By.NAME, "commit"))
                WebDriverWait(driver, WAIT_TIMEOUT_SEC).until(element_present)
            except TimeoutException:
                raise ErrorException(f"IVR {ivr} tcn检查的时候，无法打开Edit Applicant页面")

            real_tcn = driver.find_element(By.ID, "applicant_traveling_to_apply_true").is_selected()
            if is_tcn == real_tcn:
                continue
            else:
                is_tcn_equal = False
                break

    driver.get(f"https://ais.usvisa-info.com/en-{country}/niv/account")
    if not is_login_success(driver):
        raise ErrorException(f"IVR {ivr} 检查完了tcn，但是无法跳转回主页面了")

    return is_tcn_equal
