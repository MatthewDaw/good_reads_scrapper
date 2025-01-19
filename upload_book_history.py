"""Upload read list to new good reads account."""
import os

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import pandas as pd
import time
import re
from datetime import datetime
from playwright.sync_api import TimeoutError

load_dotenv('.env')

def delete_book_from_list(book_row):
    books = pd.read_csv('output/book_list_cache.csv')
    new_list = books[books['field isbn13'] != book_row['field isbn13']]
    new_list.to_csv('output/book_list_cache.csv', index=False)


def extract_datetime(date_str):
    # Try to match "Month Day, Year" format
    match = re.search(r"[A-Za-z]{3} \d{1,2}, \d{4}", date_str)
    if match:
        date_str = match.group(0)
        return datetime.strptime(date_str, "%b %d, %Y")

    # If "Day" is missing, match "Month Year" format
    match = re.search(r"[A-Za-z]{3} \d{4}", date_str)
    if match:
        date_str = match.group(0)
        return datetime.strptime(date_str, "%b %Y").replace(day=1)

    return None

def load_books():
    """Load books from a file."""
    books = pd.read_csv('output/book_list_cache.csv')
    return books

def handle_adding_new_book(page, book_row):
    # Click the button
    page.click("//*[@id='__next']/div[2]/main/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/button")
    time.sleep(2)
    times_read = int(book_row['field read_count'].split(' ')[-1])

    if times_read > 0:
        # click on "Read"
        page.click(
            "body > div.Overlay.Overlay--floating > div > div.Overlay__content > div > div:nth-child(3) > div > button")

        # close tags dialog that comes up
        page.click("body > div.Overlay.Overlay--floating > div > div.Overlay__actions > div:nth-child(2) > button")

        # open edit history
        page.click(
            "#__next > div.PageFrame.PageFrame--siteHeaderBanner > main > div.BookPage__gridContainer > div.BookPage__leftColumn > div > div.BookActions > div.BookActions__editActivityButton > a > span:nth-child(2)")

        start_date_time = extract_datetime(book_row['field date_started'])

        finish_date_time = extract_datetime(book_row['field date_read'])
        page.wait_for_selector("div.largePicker.readingSessionDatePicker.startedAtMonth > select", timeout=10000)
        if start_date_time:
            # set started year
            page.select_option(
                "div.readingSessionDatePicker.smallPicker.startedAtYear > select",
                value=str(start_date_time.year)
            )
            # set stated month
            page.select_option(
                "div.largePicker.readingSessionDatePicker.startedAtMonth > select",
                value=str(start_date_time.month)  # Convert the month to a string to match the "value" attribute
            )
            # set started day
            page.select_option(
                "div.readingSessionDatePicker.smallPicker.startedAtDay > select",
                value=str(start_date_time.day)  # Convert the day to a string to match the "value" attribute
            )

        if finish_date_time:
            # set read year
            page.select_option(
                "span.endedAtYear.readingSessionDatePicker.smallPicker > select",
                value=str(finish_date_time.year)
            )

            # set read month
            page.select_option(
                "span.endedAtMonth.largePicker.readingSessionDatePicker > select",
                value=str(finish_date_time.month)  # Convert the month to a string to match the "value" attribute
            )

            # Select the day in the dropdown
            page.select_option(
                "span.endedAtDay.readingSessionDatePicker.smallPicker > select",
                value=str(finish_date_time.day)  # Convert the day to a string to match the "value" attribute
            )
        if start_date_time or finish_date_time:
            # document.querySelector("#readingSessionAddLink")
            page.click('input[id^="review_submit_for_"]')

    else:
        # click on "Want to read"
        page.click("body > div.Overlay.Overlay--floating > div > div.Overlay__content > div > div:nth-child(1) > div > button")

def add_new_book(page, book_row):
    page.goto("https://www.goodreads.com/search?q=&qid=", timeout=90000)
    # Fill the email input field
    email_input_selector = "#search_query_main"
    page.fill("#search_query_main", book_row['field isbn13'].split(" ")[-1])
    page.press(email_input_selector, "Enter")


    button_xpath = "//*[@id='__next']/div[2]/main/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/button"

    time.sleep(2)

    already_entered = False
    try:
        # Wait for the button to be visible
        page.wait_for_selector(button_xpath, timeout=200)

    except TimeoutError:
        already_entered = True
        delete_book_from_list(book_row)

    if not already_entered:
        handle_adding_new_book(page, book_row)
        delete_book_from_list(book_row)


def upload_book_history():
    """Upload read history to goodreads.com."""

    book_list = load_books()

    time_difference = 30

    while 0 < len(book_list) and time_difference > 20:
        last_attempt = time.time()
        try:
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
        except Exception as e:
            time_difference = time.time() - last_attempt
            time.sleep(10)
            book_list = load_books()

if __name__ == '__main__':
    upload_book_history()

