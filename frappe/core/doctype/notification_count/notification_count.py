# -*- coding: utf-8 -*-
# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, now_datetime, get_datetime
from frappe.model.document import Document


exclude_from_linked_with = True


class NotificationCount(Document):
	pass


def add_notification_count(reference_doctype, reference_name, notification_type, notification_medium, count=1):
	count = cint(count) or 1

	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium)
	doc.notification_count = cint(doc.notification_count) + count
	doc.last_sent_dt = now_datetime()
	doc.save(ignore_permissions=True)


def get_notification_count(reference_doctype, reference_name, notification_type, notification_medium):
	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium)
	return cint(doc.get('notification_count'))


def set_notification_last_scheduled(reference_doctype, reference_name, notification_type, notification_medium):
	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium)
	doc.last_scheduled_dt = now_datetime()
	doc.save(ignore_permissions=True)


def get_notification_last_scheduled(reference_doctype, reference_name, notification_type, notification_medium):
	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium)
	return get_datetime(doc.get('last_scheduled_dt')) if doc.get('last_scheduled_dt') else None


def clear_notification_count(reference_doctype, reference_name):
	frappe.db.sql("delete from `tabNotification Count` where reference_doctype = %s and reference_name = %s",
		(reference_doctype, reference_name))


def get_all_notification_count(reference_doctype, reference_name):
	if not reference_doctype or not reference_name:
		return []

	return frappe.get_all("Notification Count",
		filters={"reference_doctype": reference_doctype, "reference_name": reference_name},
		fields=["notification_type", "notification_medium", "notification_count"])


def get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium):
	filters = {
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"notification_type": notification_type,
		"notification_medium": notification_medium
	}

	name = frappe.db.get_value("Notification Count", filters)

	if name:
		doc = frappe.get_doc("Notification Count", name)
	else:
		doc = frappe.get_doc({"doctype": "Notification Count", **filters})

	return doc
