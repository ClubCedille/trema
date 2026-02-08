import os
from logger import logger
import aiohttp

async def dispatch_grav_gw(domaine, nom_club, contexte, github_token, skeleton_url=""):
    url = "https://api.github.com/repos/clubCedille/k8s-cedille-production-v2/actions/workflows/request-grav.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    inputs = {
        "domaine": domaine,
        "nom_club": nom_club,
        "contexte": contexte
    }
    if skeleton_url:
        inputs["skeleton_url"] = skeleton_url
    data = {
        "ref": "main",
        "inputs": inputs
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 204:
                return True, "Workflow successfully triggered."
            else:
                response_text = await response.text()
                logger.error(f"Failed to trigger workflow. Status code: {response.status}, Response body: {response_text}")
                return False, f"Failed to trigger workflow. Status code: {response.status}"

async def dispatch_add_member_to_gh_org_gw(username, email, github_token, team_sre, cluster_role, netdata_role):
    url = "https://api.github.com/repos/ClubCedille/Plateforme-Cedille/actions/workflows/add-new-member.yml/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "ref": "master",
        "inputs": {
            "github_username": username,
            "github_email": email,
            "team_sre": "true" if team_sre == "vrai" else "false",
            "cluster_role": cluster_role,
            "netdata_role": netdata_role
        }
    }

    print(data)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 204:
                return True, "User successfully added to the organization."
            else:
                response_text = await response.text()
                logger.error(f"Failed to trigger workflow. Status code: {response.status}, Response body: {response_text}")
                return False, f"Failed to add user to the organization. Status code: {response.status}"

async def post_to_calidum(sender_username, request_service, request_details):
    api_key = os.getenv('CALIDUM_API_KEY')
    url = "https://calidum-rotae.prodv2.cedille.club"
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

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=service_details) as response:
            if response.status == 200:
                logger.info("Successfully posted to Calidum")
                return True
            else:
                logger.error(f"Failed to post to Calidum. Status code: {response.status}")
                return False
