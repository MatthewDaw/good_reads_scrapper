"""Upload read list to new good reads account."""
import os

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import pandas as pd
import time
import re

load_dotenv('.env')

def load_books():
    """Load books from a file."""
    books = pd.read_csv('output/book_list.csv')
    return books

def add_new_book(page, book_row):
    page.goto("https://www.goodreads.com/search?q=&qid=")
    # Fill the email input field
    email_input_selector = "#search_query_main"
    page.fill("#search_query_main", book_row['field isbn13'].split(" ")[-1])
    page.press(email_input_selector, "Enter")


    button_xpath = "//*[@id='__next']/div[2]/main/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/button"

    time.sleep(2)

    # Wait for the button to be visible
    page.wait_for_selector(button_xpath)
    # Click the button
    page.click(button_xpath)

    times_read = int(book_row['field read_count'].split(' ')[-1])

    if times_read > 0:
        # click on "Read"
        page.click("body > div.Overlay.Overlay--floating > div > div.Overlay__content > div > div:nth-child(3) > div > button")

        # close tags dialog that comes up
        page.click("body > div.Overlay.Overlay--floating > div > div.Overlay__actions > div:nth-child(2) > button")

        # open edit history
        page.click("#__next > div.PageFrame.PageFrame--siteHeaderBanner > main > div.BookPage__gridContainer > div.BookPage__leftColumn > div > div.BookActions > div.BookActions__editActivityButton > a > span:nth-child(2)")



    print("think")


def upload_book_history():
    """Upload read history to goodreads.com."""

    with sync_playwright() as playwright_enginge:
        browser = playwright_enginge.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.goodreads.com/ap/signin?language=en_US&openid.assoc_handle=amzn_goodreads_web_na&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.goodreads.com%2Fap-handler%2Fsign-in&siteState=eyJyZXR1cm5fdXJsIjoiaHR0cHM6Ly93d3cuZ29vZHJlYWRzLmNvbS9yZXZpZXcvbGlzdC8xOTMwODgxLWplc3NpY2EtZGF3P3NoZWxmPSNBTEwjIn0%3D")

        account_username = os.environ['account_username']
        account_password = os.environ['account_password']


        # Fill the email input field
        email_input_selector = "input[type='email']"
        page.fill(email_input_selector, account_username)

        # Fill the password input field
        password_input_selector = "input[type='password']"
        page.fill(password_input_selector, account_password)

        page.click("#signInSubmit")

        time.sleep(4)

        book_list = load_books()

        for _, book_row in book_list.iterrows():
            add_new_book(page, book_row)

        browser.close()


if __name__ == '__main__':
    upload_book_history()

