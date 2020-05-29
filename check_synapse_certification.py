#!/usr/bin/env python3

"""
Program: audit_synapse_user.py

*****PLACEHOLDER FOR FUTURE DEVELOPMENT

Purpose: Check a Synapse user to see if they have passed the certified user
         quiz.

Input parameters:

Outputs:

Execution:

"""

import synapseclient
import synapseutils

# From Thomas Yu. {userid} is numeric.
passing_record = syn.restGET("/user/{userid}/bundle?mask=63")

# From Bruce
https://rest-docs.synapse.org/rest/GET/user/id/bundle.html
returns
https://rest-docs.synapse.org/rest/org/sagebionetworks/repo/model/UserBundle.html
need to include "mask=63" in the REST call.
