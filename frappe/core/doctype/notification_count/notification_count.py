# -*- coding: utf-8 -*-
# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, now_datetime, get_datetime
from frappe.model.document import Document


exclude_from_linked_with = True


class NotificationCount(Document):
	pass


def add_notification_count(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=None, child_name=None, count=1):
	count = cint(count) or 1

	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=child_doctype, child_name=child_name)
	doc.notification_count = cint(doc.notification_count) + count
	doc.last_sent_dt = now_datetime()
	doc.save(ignore_permissions=True)


def get_notification_count(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=None, child_name=None):
	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=child_doctype, child_name=child_name)
	return cint(doc.get('notification_count'))


def set_notification_last_scheduled(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=None, child_name=None):
	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=child_doctype, child_name=child_name)
	doc.last_scheduled_dt = now_datetime()
	doc.save(ignore_permissions=True)


def get_notification_last_scheduled(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=None, child_name=None):
	doc = get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=child_doctype, child_name=child_name)
	return get_datetime(doc.get('last_scheduled_dt')) if doc.get('last_scheduled_dt') else None


def clear_notification_count(reference_doctype, reference_name, child_doctype=None, child_name=None):
	delete_query = "delete from `tabNotification Count` where reference_doctype = %s and reference_name = %s"
	arg_list = [reference_doctype, reference_name]

	if child_doctype and child_name:
		delete_query += " and child_doctype = %s and child_name=%s"
		arg_list += [child_doctype, child_name]

	frappe.db.sql(delete_query, arg_list)


def get_all_notification_count(reference_doctype, reference_name, child_doctype=None, child_name=None):
	if not reference_doctype or not reference_name:
		return []

	filters = {"reference_doctype": reference_doctype, "reference_name": reference_name}
	fields = ["notification_type", "notification_medium", "notification_count"]

	if child_doctype and child_name:
		filters.update({
			"child_doctype": child_doctype,
			"child_name": child_name,
		})

	return frappe.get_all("Notification Count", filters=filters, fields=fields)


def get_notification_count_doc(reference_doctype, reference_name, notification_type, notification_medium, child_doctype=None, child_name=None):
	filters = {
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"notification_type": notification_type,
		"notification_medium": notification_medium
	}

	if child_doctype and child_name:
		filters.update({
			"child_doctype": child_doctype,
			"child_name": child_name
		})

	name = frappe.db.get_value("Notification Count", filters)

	if name:
		doc = frappe.get_doc("Notification Count", name)
	else:
		doc = frappe.get_doc({"doctype": "Notification Count", **filters})

	return doc
