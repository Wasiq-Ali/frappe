import frappe


def validate_mobile_nos(mobile_no, throw=True):
	if frappe.db.get_default("country") == 'Pakistan':
		from frappe.regional.pakistan import validate_mobile_pakistan
		return validate_mobile_pakistan(mobile_no, throw=throw)
	elif frappe.db.get_default("country") == 'United Arab Emirates':
		from frappe.regional.uae import validate_mobile_uae
		return validate_mobile_uae(mobile_no, throw=throw)
	else:
		return bool(mobile_no)
