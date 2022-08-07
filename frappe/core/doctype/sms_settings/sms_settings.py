# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe import _, throw, msgprint
from frappe.utils import nowdate

from frappe.model.document import Document
from six import string_types


class SMSSettings(Document):
	pass


def validate_receiver_nos(receiver_list):
	validated_receiver_list = []
	for d in receiver_list:
		# remove invalid character
		for x in [' ','-', '(', ')']:
			d = d.replace(x, '')

		validated_receiver_list.append(d)

	if not validated_receiver_list:
		throw(_("Please enter valid mobile nos"))

	return validated_receiver_list


@frappe.whitelist()
def get_contact_number(contact_name=None, ref_doctype=None, ref_name=None):
	"returns mobile number of the contact"
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


@frappe.whitelist()
def send_sms(receiver_list, msg, success_msg=True, type=None,
		reference_doctype=None, reference_name=None, party_doctype=None, party_name=None):

	import json
	if isinstance(receiver_list, string_types):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	receiver_list = validate_receiver_nos(receiver_list)

	arg = {
		'receiver_list': receiver_list,
		'message': frappe.safe_decode(msg).encode('utf-8'),
		'success_msg': success_msg,
		'type': type,
		'reference_doctype': reference_doctype,
		'reference_name': reference_name,
		'party_doctype': party_doctype,
		'party_name': party_name,
	}

	if frappe.db.get_value('SMS Settings', None, 'sms_gateway_url'):
		send_via_gateway(arg)
	else:
		msgprint(_("Please Update SMS Settings"))


def send_via_gateway(arg):
	ss = frappe.get_doc('SMS Settings', 'SMS Settings')
	headers = get_headers(ss)

	args = {ss.message_parameter: arg.get('message')}
	for d in ss.get("parameters"):
		if not d.header:
			args[d.parameter] = d.value

	success_list = []
	fail_list = []
	for d in arg.get('receiver_list'):
		args[ss.receiver_parameter] = d
		response = send_request(ss.sms_gateway_url, args, headers, ss.use_post)

		if validate_response(response, ss):
			success_list.append(d)
		else:
			fail_list.append({'number': d, 'error': get_error_message(response, ss)})

	fail_message_list = ["{0} ({1})".format(d.get('number'), d.get('error') or 'Unknown Error') for d in fail_list]

	if len(success_list) > 0:
		args.update(arg)
		create_sms_log(args, success_list)
		if arg.get('success_msg'):
			frappe.msgprint(_("SMS sent to the following numbers:<br>{0}").format("<br>".join(success_list)))
			if fail_message_list:
				frappe.msgprint(_("SMS failed for the following numbers:<br>{0}").format("<br>".join(fail_message_list)))
	else:
		frappe.throw(_("SMS could not be sent{0}").format("<br>{0}".format(fail_message_list[0]) if fail_message_list else ""))


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
		if args.get('subject') or args.get('type'):
			subject = "{0} SMS".format(args.get('subject') or args.get('type'))

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
