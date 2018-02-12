
import json
import requests
from time import sleep
import sys


class RecaptchaSolver:

    __clientKey = "not set"

    def __init__(self, captchakey):
        self.__clientKey = captchakey

    def get_balance(self):
        r = requests.post('https://api.anti-captcha.com/get_balance',
                          json={"clientKey": self.__clientKey})

        if r.status_code == requests.codes.ok:
            j = json.loads(r.text)
            if j["errorId"] == 0:
                print("OK")
                return j["balance"]
            else:
                # handles api error
                print(r.text)
        else:
            # handles request error
            print(r.status_code)

    def __get_task_result(self, task_id):
        r = requests.post('https://api.anti-captcha.com/getTaskResult',
                          json={"clientKey": self.__clientKey,
                                "taskId": task_id})

        if r.status_code == requests.codes.ok:
            j = json.loads(r.text)
            if j["errorId"] == 0:
                return j["solution"]
            else:
                # handles api error
                print(r.text)
        else:
            # handles request error
            print(r.status_code)

    def __get_task_status(self, task_id):
        r = requests.post('https://api.anti-captcha.com/getTaskResult',
                          json={"clientKey": self.__clientKey,
                                "taskId": task_id})

        if r.status_code == requests.codes.ok:
            j = json.loads(r.text)
            if j["errorId"] == 0:
                print("OK")
                return j["status"]
            else:
                # handles api error
                print(r.text)
        else:
            # handles request error
            print(r.status_code)

    def __create_task_google_recaptcha(self, website_url, website_key):
        r = requests.post('https://api.anti-captcha.com/createTask',
                          json={"clientKey": self.__clientKey, "task": {
                                  "type": "NoCaptchaTaskProxyless",
                                  "websiteURL": website_url,
                                  "websiteKey": website_key
                              },
                                "softId": 0,
                                "languagePool": "en"
                                })
        if r.status_code == requests.codes.ok:
            j = json.loads(r.text)
            if j["errorId"] == 0:
                print("OK" + r.text)
                return j["taskId"]
            elif j["errorCode"] == "ERROR_NO_SLOT_AVAILABLE":
                sleep(15)
                return self.__create_task_google_recaptcha(website_url,
                                                           website_key)
            else:
                # handles api error
                print(r.text)
        else:
            # handles request error
            print(r.status_code)

    def solve_google_recaptcha(self, website_url, website_key):
        task_id = self.__create_task_google_recaptcha(
            website_url, website_key)
        print("sleeping 15 sec")
        sleep(15)
        current_status = self.__get_task_status(task_id)
        time_s = 15
        while current_status == "processing":
            if time_s > 100:
                print("\n\n\n\nreCaptcha Took too long to solve -> "
                      "please re-run your previous command\n\n\n")
                sys.exit(0)
            print("current status: " + str(current_status))
            print("sleeping 15 sec")
            sleep(15)
            time_s += 15
            current_status = self.__get_task_status(task_id)
            print("current status: " + str(current_status))
        print("\nGoogle reCaptcha solved in " + str(time_s))
        solution = self.__get_task_result(task_id)
        return solution["gRecaptchaResponse"]

    def get_current_key(self):
        return self.__clientKey