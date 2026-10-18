import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app import create_app
from werkzeug.serving import make_server
from threading import Thread


@pytest.fixture
def browser(tmp_path):
    app=create_app({"TESTING":True,"DATABASE":str(tmp_path/'browser.sqlite3')})
    server=make_server('127.0.0.1',0,app)
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    options=Options()
    if os.environ.get('SELENIUM_HEADLESS','1')=='1': options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    try:
        driver=webdriver.Chrome(options=options)
        driver.set_window_size(1280,900)
        yield driver, f'http://127.0.0.1:{server.server_port}'
        driver.quit()
    finally:
        server.shutdown()
        thread.join(timeout=2)
