import argparse
import pathlib
import sys
from alive_progress import alive_bar
from organistion_list import OrganisationList
from organisation import Organisation
from playwright.sync_api import sync_playwright

class scraper:
    def __init__(self, website: str, out_dir: pathlib.Path):
        self.website = website
        self.output_dir = out_dir

    def scrape(self, category: str, location: str, item_count: int) -> OrganisationList:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto(self.website, timeout=10000)
            page.wait_for_timeout(1000)

            page.locator('//input[@id="searchboxinput"]').fill(category + " " +location)
            page.wait_for_timeout(1000)

            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)

            place_addr = "{}/place".format(self.website)
            page.hover('//a[contains(@href, "{}")]'.format(place_addr))

            previously_counted = 0
            print("Navigating search results ...")

            with alive_bar() as bar:
                while True:
                    page.mouse.wheel(0, 10000)
                    page.wait_for_timeout(3000)
                    current_count = page.locator('//a[contains(@href, "{}")]'.format(place_addr)).count()

                    if current_count == previously_counted:
                        # In case retrieved all available listings then break from loop so as not to run infinitely 
                        listings = page.locator('//a[contains(@href, "{}")]'.format(place_addr)).all()
                        print("Retrieved all available: {}".format(len(listings)))
                        break
                    elif current_count >= item_count:
                        listings = page.locator('//a[contains(@href, "{}")]'.format(place_addr)).all()[:item_count]
                        print("Total Organistations retrieved: {}".format(len(listings)))
                        bar()
                        break
                    else:
                        previously_counted = current_count
                        print("Running Total: {}".format(current_count))
                        bar()
        
            org_list = OrganisationList(out_dir)
            print("Processing organistion data ...")

            with alive_bar(len(listings)) as bar:
                for listing in listings:
                    listing.click()
                    page.wait_for_timeout(5000)

                    name_attribute = 'aria-label'
                    location_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    contact_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    average_review_count_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//span'
                    average_review_points_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                    org_obj = Organisation()

                    if listing.get_attribute(name_attribute) is not None:
                        if len(listing.get_attribute(name_attribute)) >= 1:
                            org_obj.organisation_name = listing.get_attribute(name_attribute)
                    else:
                        org_obj.organisation_name = ""

                    if page.locator(location_xpath).count() > 0:
                        org_obj.organisation_location = page.locator(location_xpath).all()[0].inner_text()
                    else:
                        org_obj.organisation_location = ""

                    if page.locator(website_xpath).count() > 0:
                        org_obj.website = page.locator(website_xpath).all()[0].inner_text()
                    else:
                        org_obj.website = ""

                    if page.locator(contact_number_xpath).count() > 0:
                        org_obj.contact_number = page.locator(contact_number_xpath).all()[0].inner_text()
                    else:
                        org_obj.contact_number = ""

                    if page.locator(average_review_count_xpath).count() > 0:
                        org_obj.average_review_count = int(page.locator(average_review_count_xpath).inner_text().split()[0]
                            .replace(',', '').strip())
                    else:
                        org_obj.average_review_count = 0

                    if page.locator(average_review_points_xpath).count() > 0:
                        org_obj.average_review_points = float(page.locator(average_review_points_xpath).get_attribute(name_attribute).split()[0].replace(',', '.').strip())
                    else:
                        org_obj.average_review_points = 0.0

                    org_list.business_list.append(org_obj)
                    bar()

            browser.close()
            return org_list    


def main(category: str, location: str, item_count: int, out_dir: pathlib.Path):
    if not out_dir.exists():
        print("Output directory {} does not exist, creating it".format(out_dir))
        out_dir.mkdir(parents=True, exist_ok=True)
    elif not out_dir.is_dir():
        print("Output directory {} is not a directory, you must specify a directory".format(out_dir))
        sys.exit(1)

    scrapper_instance = scraper("https://www.google.com/maps", out_dir)
    org_list = scrapper_instance.scrape(category, location, item_count)

    org_list.save_to_csv(f"{category}_in_{location}_google_maps")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=True, type=int, help="the directory to monitor")

    parser = argparse.ArgumentParser(prog='Google Maps Webscapper',
                                     description='Collects business data from Google Maps')
    parser.add_argument("-c", "--category", help="the business type to search for", type=str, required=True)
    parser.add_argument("-l", "--location", help="the map location to search", type=str, required=True)
    parser.add_argument("-n", "--number", help="the number of businesses search for", type=int, default=500)
    parser.add_argument('-o', '--out_directory', help='the location to save the data', type=pathlib.Path, required=False, default=pathlib.Path('./output'))

    parsed_args = parser.parse_args()
    out_dir=parsed_args.out_directory

    main(category=parsed_args.category, location=parsed_args.location, item_count=parsed_args.number, out_dir=out_dir)

