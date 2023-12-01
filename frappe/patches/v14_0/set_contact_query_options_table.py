import frappe


def execute():
	options_str = frappe.db.get_single_value("Contact Us Settings", "query_options", cache=False)
	if not options_str:
		return

	query_options = options_str.replace(",", "\n").split("\n")
	query_options = [opt.strip() for opt in query_options]
	query_options = [opt for i, opt in enumerate(query_options) if opt or i == 0]

	do_not_set_default_option = 1 if query_options[0] else 0

	frappe.reload_doc("doctype", "website", "contact_us_settings")

	doc = frappe.get_single("Contact Us Settings")

	doc.query_options = []
	for opt in query_options:
		if opt:
			doc.append("query_options", {"option": opt})

	doc.update_child_table("query_options")
	doc.db_set("do_not_set_default_option", do_not_set_default_option, update_modified=False)
