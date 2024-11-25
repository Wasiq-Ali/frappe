import frappe
from frappe import _
import re


mobile_regex = re.compile(r'^(?:\+971|00971|0)(?:50|52|53|54|55|56|57|58)[0-9]{7}$')

def validate_mobile_uae(mobile_no, throw=True):
	if frappe.db.get_default("country") != 'United Arab Emirates':
		return True

	if not mobile_no:
		return False

	if (
		(mobile_no[:1] == "+" and mobile_no[:4] != "+971")
		or (mobile_no[:2] == "00" and mobile_no[:5] != "00971")
	):
		return True

	if not mobile_regex.match(mobile_no):
		if throw:
			frappe.throw(_("Invalid UAE Mobile No."))

		return False

	return True
