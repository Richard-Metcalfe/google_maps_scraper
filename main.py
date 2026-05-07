import argparse
import pathlib
import sys
from alive_progress import alive_bar
from organistion_list import OrganistionList
from organisation import Organisation
from playwright.sync_api import sync_playwright
from email_scraper import scape_emails_from_domains

class Scraper:
    def __init__(self, website: str, out_dir: pathlib.Path, headless: bool = False):
        self.website = website
        self.output_dir = out_dir
        self.headless = headless

    def scrape(self, category: str, location: str, item_count: int) -> OrganistionList:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            page = browser.new_page()

            page.goto(self.website, timeout=10000)
            page.wait_for_timeout(1000)

            #page.locator('//input[@id="searchboxinput"]').fill(f"{category} {location}", force=True)           
            # Use the role-based locator which is more reliable an id
            search_box = page.get_by_role("combobox", name="Search Google Maps")
            search_box.wait_for(state="visible")            # Click to activate the search box
            search_box.click()

            # Directly fill the search box. Playwright will wait for it to be ready.
            search_box.fill(f"{category} {location}")

            # The input field is often the next element after the button is clicked.
            # You might need to target the input that appears or becomes active.   
            #page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            #page.wait_for_timeout(1000)

            place_addr = f"{self.website}/place"
            page.hover('//a[contains(@href, "{}")]'.format(place_addr)) 

            previously_counted = 0
            print("Navigating search results ...")

            with alive_bar() as bar:
                while True:
                    page.mouse.wheel(0, 10000)
                    locator = page.locator('//a[contains(@href, "{}")]'.format(place_addr))

                    for _ in range(30):  # 30 * 100ms = 3s max
                        current_count = locator.count()
                        if current_count > previously_counted:
                            break
                        page.wait_for_timeout(100)
                    else:
                        # No new results in 3s window
                        current_count = locator.count() 

                    if current_count == previously_counted:
                        # In case retrieved all available listings then break from loop so as not to run infinitely 
                        listings = page.locator('//a[contains(@href, "{}")]'.format(place_addr)).all()
                        print("Retrieved all available: {}".format(len(listings)))
                        bar()
                        break
                    elif current_count >= item_count:
                        listings = page.locator('//a[contains(@href, "{}")]'.format(place_addr)).all()[:item_count]
                        print("Total Organistations retrieved: {}".format(len(listings)))
                        bar()
                        break
                    else:
                        previously_counted = current_count
                        print(f"Running Total: {current_count}")
                        bar()
        
            #org_list = OrganisationList(out_dir)
            org_list = OrganistionList()

            print("Processing organistion data ...")

            name_attribute = 'aria-label'
            location_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            contact_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
            average_review_count_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//span'
            average_review_points_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

            def extract_organisation_data(page, org_name):
                org_obj = Organisation()

                # Cache locators and use `.first` instead of `.all()[0]`
                location_el = page.locator(location_xpath).first
                website_el = page.locator(website_xpath).first
                contact_el = page.locator(contact_number_xpath).first
                avg_review_count_el = page.locator(average_review_count_xpath).first
                avg_review_points_el = page.locator(average_review_points_xpath).first

                # org_name = listing.get_attribute(name_attribute)
                org_obj.organisation_name = org_name if org_name else ""

                # Location
                org_obj.organisation_location = (location_el.inner_text() if location_el.count() > 0 else "")

                # Website
                org_obj.website = (website_el.inner_text() if website_el.count() > 0 else "")

                # Contact number
                org_obj.contact_number = (contact_el.inner_text() if contact_el.count() > 0 else "")

                # Average review count
                if avg_review_count_el.count() > 0:
                    raw_text = avg_review_count_el.inner_text().strip()
                    first_token = raw_text.split()[0]
                    try:
                        org_obj.average_review_count = int(first_token.replace(",", ""))
                    except ValueError:
                        org_obj.average_review_count = 0
                else:
                    org_obj.average_review_count = 0

                # Average review points
                if avg_review_points_el.count() > 0:
                    review_points = avg_review_points_el.get_attribute(name_attribute)
                    if review_points:
                        first_token = review_points.split()[0]
                        try:
                            org_obj.average_review_points = float(first_token.replace(",", "."))
                        except ValueError:
                            org_obj.average_review_points = 0.0
                    else:
                        org_obj.average_review_points = 0.0
                else:
                    org_obj.average_review_points = 0.0

                return org_obj


            with alive_bar(len(listings)) as bar:
                for listing in listings:
                    listing.click()
                    # Wait for the details pane (address) to update instead of sleeping
                    page.locator(location_xpath).first.wait_for(state="visible", timeout=10000)
                    
                    org_obj = extract_organisation_data(page, listing.get_attribute(name_attribute))
                    org_list.append(org_obj)
                    bar()

            browser.close()
            return org_list    

# hardcode website for now
DEFAULT_BASE_URL = "https://www.google.com/maps"

def main(category: str, location: str, item_count: int, out_dir: pathlib.Path, scrape_emails: bool, base_url: str = DEFAULT_BASE_URL):
    if not out_dir.exists():
        print(f"Output directory {out_dir} does not exist, creating it")
        out_dir.mkdir(parents=True, exist_ok=True)
    elif not out_dir.is_dir():
        print(f"Output directory {out_dir} is not a directory, you must specify a directory")
        sys.exit(1)

    scrapper_instance = Scraper(base_url, out_dir)
    org_list = scrapper_instance.scrape(category, location, item_count)

    file_suffix = "google_maps"
    if scrape_emails:
        print("Attempting to retrieve email addresses")
        file_suffix += "_with_emails"
        org_list = scape_emails_from_domains(org_list)
    else:
        print("Skipping email retrieval ...")
 
    org_list.save_to_csv(out_dir, f"{category}_in_{location}_{file_suffix}")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(prog='Google Maps Webscapper', description='Retrieves business data from Google Maps')
    parser.add_argument("-c", "--category", help="the business type to search for", type=str, required=True)
    parser.add_argument("-l", "--location", help="the map location to search", type=str, required=True)
    parser.add_argument("-n", "--number", help="the number of businesses search for", type=int, default=500)
    parser.add_argument('-o', '--out_directory', help='the location to save the data', type=pathlib.Path, required=False, default=pathlib.Path('./output'))
    parser.add_argument('-e', '--scrape_emails', help='attempt to retrieve email address from the web domains found', required=False, default=False, action='store_true')

    parsed_args = parser.parse_args()
    out_dir=parsed_args.out_directory

    result = main(category=parsed_args.category, location=parsed_args.location, item_count=parsed_args.number, out_dir=out_dir, scrape_emails=parsed_args.scrape_emails)

    #print(result)
