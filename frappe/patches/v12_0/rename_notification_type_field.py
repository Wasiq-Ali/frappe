import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	frappe.rename_doc("core", "doctype", "sms_template")

	if frappe.db.has_column("SMS Template", "type"):
		rename_field("SMS Template", "type", "notification_type")
