# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document


class ContactUsSettings(Document):
	def on_update(self):
		from frappe.website.utils import clear_cache

		clear_cache()


def update_website_context(context):
	doc = frappe.get_cached_doc("Contact Us Settings", None).as_dict()

	if doc.query_options:
		doc.query_options = doc.query_options.replace(",", "\n").split("\n")
		doc.query_options = [opt.strip() for opt in doc.query_options]
		doc.query_options = [opt for i, opt in enumerate(doc.query_options) if opt or i == 0]
	else:
		doc.query_options = ["Sales", "Support", "General"]

	context['contact_us_settings'] = doc
