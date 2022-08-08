import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	if frappe.db.has_column("SMS Template", "type"):
		rename_field("SMS Template", "type", "notification_type")
