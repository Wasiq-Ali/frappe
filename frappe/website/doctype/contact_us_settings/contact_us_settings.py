# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document

class ContactUsSettings(Document):

	def on_update(self):
		from frappe.website.render import clear_cache
		clear_cache()


def update_website_context(context):
	context['contact_us_settings'] = frappe.get_cached_doc("Contact Us Settings", None).as_dict()
