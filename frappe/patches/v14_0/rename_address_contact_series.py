import frappe
from frappe.model.naming import make_autoname


def execute():
	frappe.reload_doctype("Address")
	frappe.reload_doctype("Contact")

	addresses = frappe.get_all("Address", pluck="name")
	contacts = frappe.get_all("Contact", pluck="name")

	address_series = frappe.get_meta("Address").autoname
	contact_series = frappe.get_meta("Contact").autoname

	print("Cleaning Contact Names")
	for name in contacts:
		doc = frappe.get_doc("Contact", name)
		doc.clean_contact_name()
		doc.db_update()
		doc.clear_cache()

	print("Cleaning Addresses")
	for name in addresses:
		doc = frappe.get_doc("Address", name)
		doc.clean_address()
		doc.db_update()
		doc.clear_cache()

	print("Renaming {0} Addresses".format(len(addresses)))
	for old_name in addresses:
		new_name = make_autoname(address_series)
		frappe.rename_doc("Address", old_name, new_name, force=True, rebuild_search=False)

	print("Renaming {0} Contacts".format(len(contacts)))
	for old_name in contacts:
		new_name = make_autoname(contact_series)
		frappe.rename_doc("Contact", old_name, new_name, force=True, rebuild_search=False)
