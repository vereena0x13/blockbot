from time import sleep
from selenium import webdriver
import random
import signal



SPEED = 0.1

def ssleep(n):
    sleep(n * SPEED)



def attempt_predicate(fn, max_retries, delay, *args):
    i = 0
    while i < max_retries:
        i += 1
        if fn(*args):
            return
        sleep(delay)
    raise Exception("out of retries")



def get_tweets():
    return driver.find_elements('xpath', '//article[@data-testid="tweet"]')


def get_promoted_tweets():
    return list(filter(is_promoted, get_tweets()))


def wait_for_tweets():
    attempt_predicate(lambda: len(get_tweets()) > 0, 5, 1)


def is_promoted(twat):
    try:
        # TODO: this can probably (maybe?) still have false positives...
        twat.find_element('xpath', './/span[.="Promoted"]') \
            .find_element('xpath', '../..') \
            .find_element('tag name', 'svg')
        return True
    except:
        return False


def scroll_to(element):
    # TODO: this works until we've blocked accounts and the tweets disappear
    # i assume this is because the tweets do disappear and everything gets offset
    # by the height of said tweets. maybe we could just save the height of each
    # tweet and use that as an offset in here? *shrugs*
    desired_y = (element.size['height'] / 2) + element.location['y']
    window_h = driver.execute_script('return window.innerHeight')
    window_y = driver.execute_script('return window.pageYOffset')
    current_y = (window_h / 2) + window_y
    scroll_y_by = int(desired_y - current_y + random.randint(-10, 10))
    for i in range(1, scroll_y_by, int(scroll_y_by/42)):
        driver.execute_script("window.scrollTo(0, arguments[0]);", i)
        ssleep(random.uniform(0.003, 0.006))



opts = webdriver.ChromeOptions()
opts.add_argument("user-data-dir=selenium")
#opts.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=opts)


driver.get('https://twitter.com/')
wait_for_tweets()


log = open("block_log.txt", "a")



def signal_handler(sig, frame):
    log.close()
    driver.quit() # TODO: make this actually work properly...
    exit(0)

signal.signal(signal.SIGINT, signal_handler)



def block_tweeter(twat):
    scroll_to(twat)

    username = twat.find_element('xpath', './/div[@data-testid="User-Name"]').get_attribute('textContent')
    handle = username[username.rfind('@'):]
    log.write(handle)
    log.write('\n')
    log.flush()

    dots = twat.find_element('xpath', './/div[@data-testid="caret"]')
    dots.click()

    ssleep(random.uniform(0.35, 0.7))

    block = driver.find_element('xpath', '//div[@data-testid="block"]')
    block.click()

    ssleep(random.uniform(0.35, 0.7))

    block = driver.find_element('xpath', '//div[@data-testid="confirmationSheetConfirm"]')
    block.click()

    print("Blocked " + handle)



while True:
    twats = get_promoted_tweets()
    if len(twats) == 0:
        driver.refresh()
        wait_for_tweets()
    else:
        for twat in twats:
            if is_promoted(twat):
                try:
                    block_tweeter(twat)
                except:
                    driver.refresh()
                    wait_for_tweets()
                    break
            ssleep(random.uniform(0.125, 0.25))
