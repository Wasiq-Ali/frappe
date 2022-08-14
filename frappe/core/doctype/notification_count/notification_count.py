# -*- coding: utf-8 -*-
# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, now_datetime, get_datetime
from frappe.model.document import Document


class NotificationCount(Document):
	pass


def add_notification_count(doc, notification_type, notification_medium, count=1, update=False):
	if not has_notification_count_field(doc):
		return

	count = cint(count) or 1

	row = get_row(doc, notification_type, notification_medium, append_if_missing=True)
	row.notification_count += count
	row.last_sent_dt = now_datetime()

	if update:
		row.db_update()


def get_notification_count(doc, notification_type, notification_medium):
	if not has_notification_count_field(doc):
		return 0

	row = get_row(doc, notification_type, notification_medium, append_if_missing=False)
	return cint(row.get('notification_count'))


def set_notification_last_scheduled(doc, notification_type, notification_medium, update=False):
	if not has_notification_count_field(doc):
		return

	row = get_row(doc, notification_type, notification_medium, append_if_missing=True)
	row.last_scheduled_dt = now_datetime()

	if update:
		row.db_update()


def get_notification_last_scheduled(doc, notification_type, notification_medium):
	if not has_notification_count_field(doc):
		return None

	row = get_row(doc, notification_type, notification_medium, append_if_missing=False)
	return get_datetime(row.get('last_scheduled_dt')) if row.get('last_scheduled_dt') else None


def clear_notification_count(doc, update=False):
	if not has_notification_count_field(doc):
		return None

	doc.set('notification_count', [])

	if update:
		frappe.db.sql("delete from `tabNotification Count` where parenttype = %s and parent = %s",
			(doc.doctype, doc.name))


def get_row(doc, notification_type, notification_medium, append_if_missing):
	filters = {"notification_type": notification_type, "notification_medium": notification_medium}

	row = doc.get('notification_count', filters)
	if row:
		row = row[0]
	elif append_if_missing:
		row = doc.append('notification_count', filters)
		row.notification_count = 0
	else:
		row = frappe._dict()

	return row


def has_notification_count_field(doc):
	df = doc.meta.get_field('notification_count')
	if not df or df.options != "Notification Count" or df.fieldtype != 'Table':
		return False

	return True
