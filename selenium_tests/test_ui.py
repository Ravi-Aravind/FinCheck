import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_home_page_loads(browser):
    driver,base=browser
    driver.get(base+'/')
    assert 'Review transaction' in driver.find_element(By.TAG_NAME,'h1').text


def submit(driver,base,amount,location='India'):
    driver.get(base+'/')
    driver.find_element(By.ID,'transaction_id').send_keys('SEL-'+uuid.uuid4().hex[:12])
    driver.find_element(By.ID,'amount').send_keys(str(amount))
    driver.find_element(By.ID,'location').send_keys(location)
    driver.find_element(By.ID,'submit-button').click()
    return WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.CLASS_NAME,'score')))


def test_legitimate_submission(browser):
    driver,base=browser
    submit(driver,base,1200)
    assert driver.find_element(By.CLASS_NAME,'pill').text=='LEGITIMATE'


def test_suspicious_submission(browser):
    driver,base=browser
    submit(driver,base,150000,'Atlantis')
    assert driver.find_element(By.CLASS_NAME,'pill').text=='SUSPICIOUS'


def test_history_contains_created_transaction(browser):
    driver,base=browser
    identifier='SEL-'+uuid.uuid4().hex[:12]
    driver.get(base+'/')
    driver.find_element(By.ID,'transaction_id').send_keys(identifier)
    driver.find_element(By.ID,'amount').send_keys('100')
    driver.find_element(By.ID,'location').send_keys('India')
    driver.find_element(By.ID,'submit-button').click()
    WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.CLASS_NAME,'score')))
    driver.get(base+'/history')
    WebDriverWait(driver,5).until(EC.text_to_be_present_in_element((By.ID,'history-body'),identifier))
    assert identifier in driver.find_element(By.ID,'history-body').text


def test_invalid_form_has_native_validation(browser):
    driver,base=browser
    driver.get(base+'/')
    form=driver.find_element(By.ID,'analysis-form')
    assert driver.execute_script('return arguments[0].checkValidity()',form) is False
