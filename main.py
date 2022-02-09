import requests, pytz, json
from datetime import datetime
API_ENDPOINT = "https://us-central1-marcy-playground.cloudfunctions.net/ordoroCodingTest"

# Determine if during the month of April normalized to the UTC timezone
def is_april(login_date):
	if login_date is not None and len(login_date) > 0:
		datetime_obj = datetime.strptime(login_date, "%Y-%m-%dT%X%z")
		utc_datetime = datetime_obj.astimezone(pytz.utc)
		return utc_datetime.date().month == 4
	else:
		return False

# Get the data from the API
def get_data_generator():
	response = requests.get(API_ENDPOINT)
	if response.status_code == 200:
		print("Data api call successful")
		return (entry for entry in response.json()["data"])
	else:
		print("Data api call unsuccessful with status code {}".format(response.status_code))
		return None

# Parse the data and get the unique emails, unique emails that logged in in april, and domains with multiple users
def parse_data(data):
	emails = []
	april_emails = []
	domain_count = {}
	for entry in data:
		login_date, email = entry["login_date"], entry["email"]
		if email is not None:
			emails.append(email)

			if is_april(login_date):
				april_emails.append(email)

			domain = email.split("@")[1]
			if domain in domain_count:
				domain_count[domain] = domain_count[domain] + 1
			else:
				domain_count[domain] = 1

	unique_emails = list(set(emails))
	unique_april_emails = list(set(april_emails))
	multi_user_domains = {domain:count for domain, count in domain_count.items() if count > 1}
	return unique_emails, unique_april_emails, multi_user_domains

# Format the data to be in the message format we want
def format_data(unique_emails, unique_april_emails, multi_user_domains):
	message = {
				"your_email_address": 'bartee260@gmail.com',
				"unique_emails": unique_emails,
				"user_domain_counts": multi_user_domains,
				"april_emails": unique_april_emails
	}
	return message


# Send the data as json via API
def send_data(message):
	response = requests.post(API_ENDPOINT, json = message,)
	if response.status_code == 200 or response.status_code == 201:
		print("data post successful")
		return True
	else:
		print("data post unsuccessful with status code {}".format(response.status_code))
		return False

def main():

	data = get_data_generator()

	if data is not None:

		unique_emails, unique_april_emails, multi_user_domains = parse_data(data)

		message = format_data(unique_emails, unique_april_emails, multi_user_domains)

		send_data(message)

if __name__ == "__main__":
	main()