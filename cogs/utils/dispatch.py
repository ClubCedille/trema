import os

def dispatch_github_workflow(domaine, nom_club, contexte, github_token):
	# https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event
	url = "https://api.github.com/repos/clubCedille/plateforme-Cedille/actions/workflows/request-grav.yml/dispatches"
	headers = {
		"Accept": "application/vnd.github+json",
		"Authorization": f"token {github_token}",
		"X-GitHub-Api-Version": "2022-11-28"
	}
	data = {
		"ref": "master",
		"inputs": {
			"domaine": domaine,
			"nom_club": nom_club,
			"contexte": contexte
		}
	}

	response = requests.post(url, headers=headers, json=data)

	if response.status_code == 204:
		return True, "Workflow successfully triggered."
	else:
		return False, f"Failed to trigger workflow. Status code: {response.status_code}"

import requests

def post_to_calidum(sender_username, request_service, request_details):
	api_key = os.getenv('CALIDUM_API_KEY')
	url = "https://calidum-rotae.omni.cedille.club"
	service_details = {
		"Sender": {
			"FirstName": sender_username,
			"LastName": "", 
			"Email": ""
		},
		"RequestService": request_service,
		"RequestDetails": request_details
	}

	headers = {
		'Content-Type': 'application/json',
		'X-API-KEY': api_key
	}

	response = requests.post(url, headers=headers, json=service_details)

	if response.status_code == 200:
		print("Posted to Calidum")
		return True
	else:
		print("Failed to post to Calidum")
		return False
