# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, cint
from frappe.model.document import Document
from frappe.core.doctype.notification_count.notification_count import add_notification_count
from six import string_types
from frappe.model.base_document import get_controller
import json


class SMSSettings(Document):
	pass


@frappe.whitelist()
def send_sms(receiver_list,
		message,
		success_msg=True,
		notification_type=None,
		reference_doctype=None,
		reference_name=None,
		party_doctype=None,
		party_name=None):

	receiver_list = clean_receiver_nos(receiver_list)

	args = frappe._dict({
		'receiver_list': receiver_list,
		'message': message,
		'success_msg': success_msg,
		'notification_type': notification_type,
		'reference_doctype': reference_doctype,
		'reference_name': reference_name,
		'party_doctype': party_doctype,
		'party_name': party_name,
		'doc': get_doc_for_triggers(reference_doctype, reference_name)
	})

	run_before_send_methods(args)
	validate_and_send(args)
	run_after_send_methods(args)


def send_template_sms(notification_type, reference_doctype=None, reference_name=None, doc=None):
	from frappe.core.doctype.sms_template.sms_template import get_sms_template, render_sms_template

	if not doc and reference_doctype and reference_name:
		doc = frappe.get_doc(reference_doctype, reference_name)
	if not doc:
		frappe.throw(_("SMS could not be sent because reference document not provided"))

	for_notification_type_str = " for Notification Type {0}".format(notification_type) if notification_type else ""

	args = frappe._dict(doc.run_method("get_sms_args", notification_type=notification_type))
	args.reference_doctype = doc.doctype
	args.reference_name = doc.name
	if not args:
		frappe.throw(_("SMS not supported for {0}{1}").format(args.reference_doctype, for_notification_type_str))

	args.receiver_list = clean_receiver_nos(args.get('receiver_list'))
	if not args.receiver_list:
		frappe.throw(_("SMS receiver number not available for {0} {1}").format(args.reference_doctype, args.reference_name))

	sms_template = get_sms_template(args.reference_doctype, notification_type)
	if not sms_template:
		frappe.throw(_("SMS Template not available for {0}{1}").format(args.reference_doctype, for_notification_type_str))

	message = render_sms_template(sms_template, doc)
	if not message:
		frappe.throw(_("SMS Message empty for {0} {1}{2}")
			.format(args.reference_doctype, args.reference_name, for_notification_type_str))

	args.update({
		'message': message,
		'notification_type': notification_type,
		'doc': doc,
		'success_msg': args.get('success_msg') or True
	})

	run_before_send_methods(args)
	validate_and_send(args)
	run_after_send_methods(args)


def validate_and_send(args):
	if not frappe.get_cached_value('SMS Settings', None, 'sms_gateway_url'):
		frappe.throw(_("Please Update SMS Settings"))

	if not args.get('receiver_list'):
		frappe.throw(_("No valid Mobile Number provided"))

	if not args.get('message'):
		frappe.throw(_("No SMS message provided"))

	args['message'] = frappe.safe_decode(args.get('message')).encode('utf-8')

	send_via_gateway(args)


def run_before_send_methods(args):
	doc = args.get('doc')
	if doc:
		doc.run_method("validate_notification", notification_medium="SMS",
			notification_type=args.get('notification_type'), args=args)
		add_notification_count(doc, args.get('notification_type'), 'SMS', update=True)


def run_after_send_methods(args):
	doc = args.get('doc')
	if doc:
		doc.run_method("after_send_notification", notification_medium="SMS",
			notification_type=args.get('notification_type'), args=args)
		doc.notify_update()


def get_doc_for_triggers(reference_doctype, reference_name):
	if not reference_doctype or not reference_name:
		return

	try:
		controller = get_controller(reference_doctype)
		has_validate_notification = hasattr(controller, "validate_notification")
		has_after_send_notification = hasattr(controller, "after_send_notification")
		if has_validate_notification or has_after_send_notification:
			doc = frappe.get_doc(reference_doctype, reference_name)
			return doc
	except ImportError:
		pass


def send_via_gateway(args):
	ss = frappe.get_cached_doc('SMS Settings', None)
	headers = get_headers(ss)

	request_params = {ss.message_parameter: args.get('message')}
	for d in ss.get("parameters"):
		if not d.header:
			request_params[d.parameter] = d.value

	success_list = []
	fail_list = []
	for d in args.get('receiver_list'):
		request_params[ss.receiver_parameter] = d
		response = send_request(ss.sms_gateway_url, request_params, headers, ss.use_post)

		if validate_response(response, ss):
			success_list.append(d)
		else:
			fail_list.append({'number': d, 'error': get_error_message(response, ss)})

	fail_message_list = ["{0} ({1})".format(d.get('number'), d.get('error') or 'Unknown Error') for d in fail_list]

	if len(success_list) > 0:
		create_sms_log(args, success_list)
		if args.get('success_msg'):
			frappe.msgprint(_("SMS sent to the following numbers:<br>{0}").format("<br>".join(success_list)))
			if fail_message_list:
				frappe.msgprint(_("SMS failed for the following numbers:<br>{0}").format("<br>".join(fail_message_list)))
	else:
		frappe.throw(_("SMS could not be sent{0}").format("<br>{0}".format(fail_message_list[0]) if fail_message_list else ""))


def get_headers(sms_settings=None):
	if not sms_settings:
		sms_settings = frappe.get_doc('SMS Settings', 'SMS Settings')

	headers = {'Accept': "text/plain, text/html, */*"}
	for d in sms_settings.get("parameters"):
		if d.header == 1:
			headers.update({d.parameter: d.value})

	return headers


def send_request(gateway_url, params, headers=None, use_post=False):
	import requests

	if not headers:
		headers = get_headers()

	if use_post:
		response = requests.post(gateway_url, headers=headers, data=params)
	else:
		response = requests.get(gateway_url, headers=headers, params=params)

	response.raise_for_status()
	return response


def validate_response(response, sms_settings=None):
	if not sms_settings:
		sms_settings = frappe.get_doc('SMS Settings', 'SMS Settings')

	if not (200 <= response.status_code < 300):
		return False

	if sms_settings.response_validation:
		valid = frappe.safe_eval(sms_settings.response_validation, eval_locals={'response': response})
		if not valid:
			return False

	return True


def get_error_message(response, sms_settings=None):
	if not sms_settings:
		sms_settings = frappe.get_doc('SMS Settings', 'SMS Settings')

	if sms_settings.error_message:
		return frappe.safe_eval(sms_settings.error_message, eval_locals={'response': response})


# Create SMS Log
# =========================================================
def create_sms_log(args, sent_to):
	message = args['message'].decode('utf-8')

	sl = frappe.new_doc('SMS Log')
	sl.sent_on = nowdate()
	sl.message = message
	sl.no_of_requested_sms = len(args['receiver_list'])
	sl.requested_numbers = "\n".join(args['receiver_list'])
	sl.no_of_sent_sms = len(sent_to)
	sl.sent_to = "\n".join(sent_to)
	sl.flags.ignore_permissions = True
	sl.save()

	"""Make communication entry"""
	if args.get('reference_doctype') and args.get('reference_name'):
		subject = "SMS"
		if args.get('subject') or args.get('notification_type'):
			subject = "{0} SMS".format(args.get('subject') or args.get('notification_type'))

		comm = frappe.get_doc({
			"doctype": "Communication",
			"communication_medium": "SMS",
			"subject": subject or 'SMS',
			"content": message,
			"sent_or_received": "Sent",
			"reference_doctype": args.get('reference_doctype'),
			"reference_name": args.get('reference_name'),
			"sender": frappe.session.user,
			"recipients": "\n".join(sent_to),
			"phone_no": sent_to[0] if len(sent_to) == 1 else None
		})

		if args.get('party_doctype') and args.get('party_name'):
			comm.append("timeline_links", {
				"link_doctype": args.get('party_doctype'),
				"link_name": args.get('party_name')
			})

		comm.insert(ignore_permissions=True)


def clean_receiver_nos(receiver_list):
	if isinstance(receiver_list, string_types):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	cleaned_receiver_list = []
	if not receiver_list:
		return cleaned_receiver_list

	invalid_characters = (' ', '\t', '-', '(', ')')

	for d in receiver_list:
		for char in invalid_characters:
			d = d.replace(char, '')

		if d:
			cleaned_receiver_list.append(d)

	return cleaned_receiver_list


@frappe.whitelist()
def get_contact_number(contact_name=None, ref_doctype=None, ref_name=None):
	mobile_no = None
	if contact_name:
		mobile_no = frappe.db.get_value("Contact", contact_name, "mobile_no")

	if not mobile_no and ref_doctype and ref_name:
		number = frappe.db.sql_list("""
			select c.mobile_no
			from `tabContact` c
			where ifnull(c.mobile_no, '') != ''
				and exists(select dl.name from `tabDynamic Link` dl where dl.parenttype = 'Contact' and dl.parent = c.name
					and link_doctype=%s and link_name=%s)
			limit 1
		""", (ref_doctype, ref_name))

		if number:
			mobile_no = number[0]

	return mobile_no or ''
