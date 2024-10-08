import os
import threading
import tkinter as tk
import time_util
import login_util

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from tkinter import messagebox

def checkout_on_edu_ssafy(service, termination_option):
    # Chrome 드라이버 실행
    driver = webdriver.Chrome(service=service)

    # 웹사이트 열기
    driver.get('https://edu.ssafy.com')

    # 로그인 예제 코드 (요소 아이디는 실제 사용 중인 웹사이트에 맞춰 변경해야 함)
    username_input_box = driver.find_element(By.ID, 'userId')
    password_input_box = driver.find_element(By.ID, 'userPwd')

    email, password = login_util.get_user_info()

    username_input_box.send_keys(email)
    password_input_box.send_keys(password)

    # 로그인 버튼 클릭
    login_button = driver.find_element(By.CSS_SELECTOR, 'div.form-btn a')
    login_button.click()

    # 퇴실 체크 버튼 클릭
    check_out_button = driver.find_element(By.ID, 'checkOut')
    check_out_button.click()

    # 확인 버튼 클릭
    ok_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-md.btn-primary.pop-event-close')
    ok_button.click()

    # 시간 체크
    check_out_button = driver.find_element(By.ID, 'checkOut')
    check_out_time = check_out_button.find_element(By.CSS_SELECTOR, '.t1').text
    driver.quit()

    result_window = tk.Tk()
    result_window.title('퇴실 체크 결과')
    result_window.geometry('500x500')

    result_text = f'퇴실 체크 시간: {check_out_time}\n정상적으로 퇴실체크 되었습니다.\n이 창은 1초 후 종료됩니다.'
    result_label = tk.Label(result_window, text= result_text)
    result_label.pack()

    result_window.after(1000, result_window.destroy)
    result_window.mainloop()

    if termination_option:
        # Windows에서 컴퓨터 종료
        os.system("shutdown /s /t 0")

def checkout(root, termination_option, checkout_time):

    root.destroy()
    # 크롬 경로 설정
    driver_path = 'chromedriver.exe'
    service = Service(driver_path)

    # 현재 시간을 초로 환산한 시간
    current_time_of_seconds = time_util.get_server_time(service)

    # 퇴실 체크 시간을 초로 환산한 시간
    checkout_time_of_seconds = checkout_time * 3600

    left_seconds = checkout_time_of_seconds - current_time_of_seconds

    # 이벤트 객체 생성
    show_left_time_event = threading.Event()

    # 카운트다운을 별도 스레드에서 실행
    show_left_time_thread = threading.Thread(target=time_util.show_left_time, args=(max(left_seconds, 0), show_left_time_event))
    show_left_time_thread.start()

    # 카운트다운이 끝날 때까지 대기
    show_left_time_event.wait()

    # 카운트다운 완료 후 로직 실행
    checkout_on_edu_ssafy(service, termination_option)

def main():
    login_information_file = 'login_information.txt'
    register_userinfo_file = 'register_userinfo.exe'
    if not os.path.exists(login_information_file):
        messagebox.showinfo("Alert", f'{login_information_file}가 존재하지 않습니다. {register_userinfo_file}파일을 먼저 실행해 유저 정보를 등록하세요')
        return

    # 윈도우 생성
    root = tk.Tk()
    root.title("register ssafy info")
    root.geometry('400x300')

    # 선택된 값을 저장할 변수
    termination_options = ['즉시 종료', '종료 안함']

    termination_option = tk.StringVar(value = termination_options[0])  # StringVar로 숫자 값 관리

    termination_label = tk.Label(root, text="퇴실체크 후 컴퓨터 종료 여부")
    termination_label.pack(pady=10)
    for option in termination_options:
        # 라디오 버튼 생성
        radio_button = tk.Radiobutton(root, text=option, variable=termination_option, value=option)

        # 라디오 버튼 배치
        radio_button.pack(pady=5)

    checkout_time_label = tk.Label(root, text="퇴실체크 시간 설정")
    checkout_time_label.pack(pady=10)
    checkout_time_options = [['18:00', 18], ['14:00', 14], ['즉시', 0]]
    checkout_time = tk.IntVar(value = checkout_time_options[0][1])
    for time_str, time_value in checkout_time_options:
        # 라디오 버튼 생성
        radio_button = tk.Radiobutton(root, text=time_str, variable=checkout_time, value=time_value)

        # 라디오 버튼 배치
        radio_button.pack(pady=2)

    checkout_button = tk.Button(root, text='퇴실 체크', command=lambda: 
                                checkout(root, termination_option.get() == termination_options[0], checkout_time.get()))
    checkout_button.pack(pady=10)
    
    root.mainloop()

main()