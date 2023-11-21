import frappe
from frappe import _


def validate_ntn_cnic_strn(ntn=None, cnic=None, strn=None):
	import re

	if frappe.db.get_default("country") != 'Pakistan':
		return

	cnic_regex = re.compile(r'^.....-.......-.$')
	ntn_regex = re.compile(r'^.......-.$')
	strn_regex = re.compile(r'^..-..-....-...-..$')

	if ntn and not ntn_regex.match(ntn):
		frappe.throw(_("Invalid NTN. NTN must be in the format #######-#"))
	if cnic and not cnic_regex.match(cnic):
		frappe.throw(_("Invalid CNIC. CNIC must be in the format #####-#######-#"))
	if strn and not strn_regex.match(strn):
		frappe.throw(_("Invalid STRN. STRN must be in the format ##-##-####-###-##"))


def validate_mobile_pakistan(mobile_no, throw=True):
	import re

	if frappe.db.get_default("country") != 'Pakistan':
		return

	if not mobile_no:
		return

	# do not check mobile number validity for international numbers
	if mobile_no[:1] == "+" or mobile_no[:2] == "00":
		return

	mobile_regex = re.compile(r'^03\d\d-\d\d\d\d\d\d\d$')

	if not mobile_regex.match(mobile_no):
		if throw:
			frappe.throw(_("Invalid Mobile No. Pakistani Mobile Nos must be in the format 03##-#######"))

		return False

	return True
