# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe.model.document import Document
from frappe.utils import clean_whitespace


class ContactUsSettings(Document):
	def validate(self):
		for i, d in enumerate(self.get("query_options")):
			d.option = clean_whitespace(d.option)

		self.query_options = [d for i, d in enumerate(self.query_options) if d or i == 0]
		for i, d in enumerate(self.get("query_options")):
			d.idx = i + 1

	def on_update(self):
		from frappe.website.utils import clear_cache
		clear_cache()


def update_website_context(context):
	doc = frappe.get_cached_doc("Contact Us Settings", None).as_dict()

	doc.query_options_table = doc.query_options

	if doc.query_options:
		doc.query_options = [d.option for i, d in enumerate(doc.query_options) if d]
		if doc.do_not_set_default_option:
			doc.query_options.insert(0, "")
	else:
		doc.query_options = ["Sales", "Support", "General"]

	context['contact_us_settings'] = doc
