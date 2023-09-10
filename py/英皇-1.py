import json
import os
import time
import traceback

import requests
from urllib.parse import urljoin

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

json_dict = {}
exam = 5
start_page = 58
success_save = False
headless = False


def get_btn(text="Continue"):
    buttons_ = driver.find_elements_recursive(by=By.TAG_NAME, value="button")
    for btn_ in buttons_:
        if btn_.text == text:
            return btn_


def find_button_with_text(element, target_text, en_target_text=None):
    buttons = element.find_elements_recursive(by=By.TAG_NAME, value="button")
    for button in buttons:
        if target_text in button.text or (en_target_text and en_target_text in button.text):
            return button
    return None


base_path = "yinghuang/" + str(exam)
base_image_path = "yinghuang/" + str(exam) + "/image"


def print_question_html(page=1):
    lis = list(driver.find_elements_recursive(by=By.XPATH, value="//ul/li"))
    for li in lis:
        find = False
        for li_i in lis:
            # 定位li下的a元素
            link = li_i.find_element(by=By.TAG_NAME, value="a")
            if link.text == str(page):
                find = True
                link.click()
                break
        if find:
            time.sleep(5)
            element = driver.find_element(by=By.ID, value="questionframe")
            inner_html = element.get_attribute("innerHTML")
            json_dict[page] = inner_html

            # 获得下面的img标签并下载图片
            img_tags = element.find_elements(by=By.TAG_NAME, value="img")
            index = 1
            for img_tag in img_tags:
                # 获取当前页面的 URL，用于构建绝对 URL
                cookies = driver.get_cookies()
                cookies_dict = {}
                for cookie in cookies:
                    cookies_dict[cookie['name']] = cookie['value']
                current_url = driver.current_url
                src = img_tag.get_attribute("src")
                # 使用 urljoin 构建绝对 URL
                absolute_src = urljoin(current_url, src)
                response = requests.get(absolute_src, cookies=cookies_dict)
                index_ = str(page) + "_" + str(index)
                if response.status_code == 200:
                    with open(base_image_path + "/" + index_ + ".png", "wb") as file:
                        file.write(response.content)
                    print("Image saved successfully as 'image.jpg'")
                else:
                    print("Failed to fetch the image")
                index += 1
            return page + 1
        else:
            return None


def create_base_dir():
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    if not os.path.exists(base_image_path):
        os.makedirs(base_image_path)


if __name__ == '__main__':
    create_base_dir()
    print("start")
    driver = uc.Chrome(headless=headless, use_subprocess=False)
    print("starting...")
    driver.get('https://cn.abrsm.org/en/our-exams/online-theory/exam-preparation-resources/')

    # 找到 rel="noopene" 的第一个a标签并点击
    links = list(driver.find_elements_recursive(by=By.XPATH, value="//a[@rel='noopener']"))

    first_link = links[exam - 1]
    time.sleep(0.1)
    driver.execute_script("arguments[0].scrollIntoView();", first_link)
    # 获取当前窗口句柄
    main_window = driver.current_window_handle

    first_link.click()

    time.sleep(2)
    # 切换到新打开窗口
    for window in driver.window_handles:
        if window != main_window:
            driver.switch_to.window(window)
            break
    # 等待页面加载成功
    WebDriverWait(driver, 20).until(
        visibility_of_element_located((By.CLASS_NAME, "controls"))
    )
    # 选择class="controls" 的下面的 <select> 并选择option value的值为Chinese Simplified
    controls = list(driver.find_elements_recursive(by=By.ID, value="tags"))

    select = controls[0]

    select_obj = Select(select)
    select_obj.select_by_visible_text("Chinese Simplified")

    # 拿到 class 为 btn 按钮内容为Continue的按钮并点击
    continue_btn = get_btn()
    continue_btn.click()

    WebDriverWait(driver, 20).until(
        visibility_of_element_located((By.ID, "launchbtn"))
    )
    launchbtn = list(driver.find_elements_recursive(by=By.ID, value="launchbtn"))
    launchbtn[0].click()

    continue_btn = get_btn()
    time.sleep(0.1)
    driver.execute_script("arguments[0].scrollIntoView();", continue_btn)
    continue_btn.click()

    WebDriverWait(driver, 20).until(
        visibility_of_element_located((By.ID, "inline-answer"))
    )
    continue_btn = get_btn()
    time.sleep(0.1)
    driver.execute_script("arguments[0].scrollIntoView();", continue_btn)
    continue_btn.click()

    time.sleep(20)
    print("finish")

    page = start_page
    while page is not None:
        try:
            page = print_question_html(page)
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            # 将 json_dict 存入文件
            with open(base_path + "/" + str(exam) + ".json", "w") as json_file:
                json.dump(json_dict, json_file, ensure_ascii=False, indent=4)
            success_save = True
            break

    if not success_save:
        # 将 json_dict 存入文件
        with open(base_path + "/" + str(exam) + ".json", "w") as json_file:
            json.dump(json_dict, json_file, ensure_ascii=False, indent=4)

    try:
        button = find_button_with_text(driver, "结束测试", "End Test")
        if button:
            button.click()
        time.sleep(1)
        launchbtn = list(driver.find_elements_recursive(by=By.ID, value="itemNavModalBtnEnd"))
        launchbtn[0].click()
        time.sleep(1)
        launchbtn = list(driver.find_elements_recursive(by=By.ID, value="confirmEndTestModal-ok"))
        launchbtn[0].click()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    time.sleep(10)
    # 下载当前页面的HTML
    html = driver.page_source
    with open(base_path + "/" + str(exam) + ".html", "w") as file:
        file.write(html)
    time.sleep(500)
    driver.quit()
