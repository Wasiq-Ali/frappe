import frappe


def execute():
	frappe.reload_doctype("System Settings")
	frappe.db.set_value("System Settings", None, "time_format", "12 Hour")
	frappe.db.set_default("time_format", "12 Hour")
