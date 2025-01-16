"""Script to download read history from goodreads.com"""

from playwright.sync_api import sync_playwright
import os
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv('.env')

def save_results(results):
    """Save results to a file."""
    books_list = pd.DataFrame(results)
    if os.path.exists('output/book_list.csv'):
        saved_list = pd.read_csv('output/book_list.csv')
        # join saved_list and books_list, drop duplicates on field isbn
        books_list = pd.concat([saved_list, books_list]).drop_duplicates(subset='field isbn13')
    books_list.to_csv('output/book_list.csv', index=False)

def close_modal(page):
    """Close modal if it exists."""
    # Define the selector for the button
    modal_close_button = "body > div:nth-child(4) > div > div > div.modal__close"

    # Check if the button exists
    modal_close_button = page.query_selector(modal_close_button)
    if modal_close_button:
        print("Button found! Clicking on it.")
        modal_close_button.click()

def download_good_read_histories():
    """Download read history from goodreads.com."""

    with sync_playwright() as playwright_enginge:
        browser = playwright_enginge.chromium.launch(headless=False)
        page = browser.new_page()
        starting_url = os.environ['source_read_url']
        page.goto(starting_url)
        start_time = time.time()
        keys_to_keep = ['field title', 'field author', 'field isbn', 'field isbn13', 'field asin', 'field num_pages', 'field avg_rating', 'field num_ratings', 'field date_pub', 'field date_pub_edition', 'field rating', 'field shelves', 'field review', 'field notes', 'field comments', 'field votes', 'field read_count', 'field date_started', 'field date_read', 'field date_added', 'field owned', 'field format', 'field actions']

        # Define the selector for the button
        next_button_selector = "#reviewPagination > a.next_page"

        results = {field: [] for field in keys_to_keep}

        previous_iteration = 0

        while True:
            time.sleep(0.5)
            collected_all_items = False
            page.wait_for_selector("#booksBody")
            table_rows = page.query_selector_all("#booksBody tr")
            close_modal(page)
            # Iterate over each row
            for row in table_rows:
                print("New Row:")
                # Select all <td> elements within the current row
                table_data_cells = row.query_selector_all("td")
                for td in table_data_cells:
                    # Extract the class attribute
                    td_class = td.get_attribute("class") or "No class"
                    # Extract the text content
                    td_text = td.text_content().strip()
                    if td_class in results.keys():
                        results[td_class].append(td_text)
            save_results(results)

            num_new_items = len(results['field title']) - previous_iteration
            next_button_is_visible = page.is_visible(next_button_selector)

            # Check if the button exists
            if next_button_is_visible:
                button = page.query_selector(next_button_selector)
                print("Button found! Clicking on it.")
                try:
                    button.click(timeout=90*1000)
                except Exception as err:
                    print(err)
            else:
                print("Button not found.")
                break

        save_results(results)
        print(f"Time taken: {time.time() - start_time}")
        browser.close()


if __name__ == '__main__':
    download_good_read_histories()

