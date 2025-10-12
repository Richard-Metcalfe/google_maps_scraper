import argparse
import pathlib
from organistion_list import OrganistionList
from email_spider import EmailSpider    
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from alive_progress import alive_bar

def run_crawler(domains: list[str]) -> dict:
    retrieved_emails = {}

    def email_retrieved_callback(result, response, spider):
        print(f"Callback with items: {result} from {response.url}")
        if 'emails' in result:
            retrieved_emails.update({response.url: result['emails']})

    # I pretty sure that the spiders are run in sequence in a seperate thead so this should be fine. For large data sets this will be time consuming
    # so shoould look at running in parallel with a CrawlerRunner and Twisted reactor along witha defeered obsject obtained from the crawl method. 
    # Try this but got twisted reactor error as it was already running so need to look at how to handle this. See https://doc.scrapy.org/en/latest/topics/practices.html
    
    settings = get_project_settings()
    settings.set('LOG_LEVEL', 'CRITICAL', priority='cmdline')  # Set log level to INFO
    proc = CrawlerProcess(settings)

    dom_count = len(domains)
    print("Starting email scraping for {} domains ...".format(dom_count))

    if dom_count > 0:
        with alive_bar() as bar:
            for domain in domains:
                print(f"Scraping website: {domain}")
                proc.crawl(EmailSpider, domain=domain, callback=email_retrieved_callback)
                bar()              
            proc.start() # the script will block here until the crawling is finished

    else:
        print("No domains found to scrape")

    print("Email scraping completed.")

    return retrieved_emails

def scape_emails_from_domains(organistions: OrganistionList) -> OrganistionList:
    domains= []

    for org in organistions:
        site = org.website
        if site is not None and site != "":
            # remove the protocol and www from the website to get the domain
            domain = site.replace("http://", "").replace("https://", "").replace("www.", "").split('/')[0]
            domains.append(domain)
        else:
            print(f"No website found for organisation: {org.organisation_name}")

    retrieved_emails = run_crawler(domains)
    #print(retrieved_emails)

    #update the organtistion with the found emails
    for org in organistions:
        site = org.website
        if site is not None and site != "":
            domain = site.replace("http://", "").replace("https://", "").replace("www.", "").split('/')[0]
            print(f"Looking for emails for organisation: {org.organisation_name} at {domain}")
            found_emails = []
            for key in retrieved_emails.keys():
                #print(key)
                if domain in key:
                    found_emails.extend(retrieved_emails[key])

            unique_addresses = set(found_emails)
            email_count = len(unique_addresses)
            if email_count > 0:
                print(f"    -- Found {email_count} : {unique_addresses}")
                org.email = list(unique_addresses)  # Assign the first email found
            else:
                print(f"    -- None found")
                org.email = None
            
        else:
            print(f"No website found for organisation: {org.organisation_name}")
            org.email = None

    return organistions
        

def main(directory: pathlib.Path, filename: str):
    file = directory.joinpath(filename)
 
    org_list = OrganistionList()
    org_list.read_from_csv(file)

    updated_org_list = scape_emails_from_domains(org_list)
    filestem = pathlib.Path(filename).stem
    updated_org_list.save_to_csv(directory, filestem + "_with_emails")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(prog='Email Scraper', description='Retrieves Email Addreses from Websites')
    parser.add_argument('-f', '--file', help='the file containing the csv data', type=pathlib.Path, required=True)
    parser.add_argument('-d', '--directory', help='the location to save the data', type=pathlib.Path, required=False, default=pathlib.Path('./output'))

    parsed_args = parser.parse_args()

    main(directory = parsed_args.directory, filename = parsed_args.file)   