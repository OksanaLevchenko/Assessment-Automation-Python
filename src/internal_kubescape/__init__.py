# __init__.py
# Purpose: Initializes the internal_hubspot package and exposes key functions
# Exposing/Elevating the get_hubspot_attachments fucntion to the Package level
# This allows you to call from internal_hubspot import get_hubspot_attachments from main.py wihtout giving the full path to the module.
from .kubescapeImport import importKubescapeData
