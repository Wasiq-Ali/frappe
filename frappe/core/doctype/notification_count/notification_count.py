# -*- coding: utf-8 -*-
# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.utils import cint
from frappe.model.document import Document


class NotificationCount(Document):
	pass


def get_notification_count(doc, notification_type, notification_medium):
	if not doc.meta.has_field('notification_count'):
		return 0

	row = doc.get('notification_count',
		{"notification_type": notification_type, "notification_medium": notification_medium})

	row = row[0] if row else {}
	return cint(row.get('notification_count'))


def add_notification_count(doc, notification_type, notification_medium, count=1, update=False):
	df = doc.meta.get_field('notification_count')
	if not df or df.options != "Notification Count" or df.fieldtype != 'Table':
		return

	filters = {"notification_type": notification_type, "notification_medium": notification_medium}

	row = doc.get('notification_count', filters)
	if row:
		row = row[0]
	else:
		row = doc.append('notification_count', filters)
		row.notification_count = 0

	count = cint(count) or 1
	row.notification_count += count

	if update:
		row.db_update()
