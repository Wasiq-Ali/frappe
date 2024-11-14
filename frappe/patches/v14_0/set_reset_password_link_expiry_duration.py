import frappe


def execute():
	if frappe.db.get_single_value("System Settings", "reset_password_link_expiry_duration", cache=False):
		frappe.db.set_single_value("System Settings", "reset_password_link_expiry_duration", 86400)
