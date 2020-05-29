"""
Program: check_synapse_certification.py

Purpose: Check a Synapse user to see if they have passed the certified user
         quiz.

Input parameters:
    user_profile_num - User Synapse profile number

Outputs: Whether the user is certified or not

Execution: check_synapse_certification.py <user Synapse ID>

"""

import argparse
import synapseclient

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("user_profile_num", type=str,
                        help="Synapse profile number")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    # Per Bruce, need to include mask=63 in the REST call.
    # https://rest-docs.synapse.org/rest/GET/user/id/bundle.html
    # returns
    # https://rest-docs.synapse.org/rest/org/sagebionetworks/repo/model/UserBundle.html
    user_record = syn.restGET(f"/user/{args.user_profile_num}/bundle?mask=63")

    if "displayName" in user_record["userProfile"].keys():
        name_value = user_record["userProfile"]["displayName"]
    else:
        name_value = f"{user_record['userProfile']['firstName']} {user_record['userProfile']['lastName']}"

    if user_record["isCertified"]:
        print(f"{name_value} is a certified user\n")
    else:
        print(f"{name_value} is not a certified user\n")


if __name__ == "__main__":
    main()
