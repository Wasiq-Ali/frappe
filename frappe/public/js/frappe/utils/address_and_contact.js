frappe.provide('frappe.contacts')

$.extend(frappe.contacts, {
	clear_address_and_contact: function(frm) {
		$(frm.fields_dict['address_html'].wrapper).html("");
		frm.fields_dict['contact_html'] && $(frm.fields_dict['contact_html'].wrapper).html("");
	},

	render_address_and_contact: function(frm) {
		// render address
		if(frm.fields_dict['address_html'] && "addr_list" in frm.doc.__onload) {
			$(frm.fields_dict['address_html'].wrapper)
				.html(frappe.render_template("address_list",
					frm.doc.__onload))
				.find(".btn-address").on("click", function() {
					frappe.new_doc("Address");
				});
		}

		// render contact
		if(frm.fields_dict['contact_html'] && "contact_list" in frm.doc.__onload) {
			$(frm.fields_dict['contact_html'].wrapper)
				.html(frappe.render_template("contact_list",
					frm.doc.__onload))
				.find(".btn-contact").on("click", function() {
					frappe.new_doc("Contact");
				}
			);
		}
	},
	get_last_doc: function(frm) {
		const reverse_routes = frappe.route_history.reverse();
		const last_route = reverse_routes.find(route => {
			return route[0] === 'Form' && route[1] !== frm.doctype
		})
		let doctype = last_route && last_route[1];
		let docname = last_route && last_route[2];

		if (last_route && last_route.length > 3)
			docname = last_route.slice(2).join("/");

		return {
			doctype,
			docname
		}
	},

	get_all_phone_numbers: function () {
		var link_doctype;
		var link_name;

		if (frappe.dynamic_link && frappe.dynamic_link.doc) {
			link_doctype = frappe.dynamic_link.doctype;
			link_name = frappe.dynamic_link.doc[frappe.dynamic_link.fieldname]
		}

		if (frappe.dynamic_link.doc) {
			if (link_doctype && link_name) {
				return frappe.call({
					method: "frappe.contacts.doctype.contact.contact.get_all_phone_numbers",
					args: {
						link_doctype: link_doctype,
						link_name: link_name,
					},
					callback: function (r) {
						if (r.message) {
							if (!frappe.dynamic_link.doc.__onload) {
								frappe.dynamic_link.doc.__onload = {}
							}
							frappe.dynamic_link.doc.__onload.phone_nos = r.message;
						}
					},
				})
			} else {
				if (!frappe.dynamic_link.doc.__onload) {
					frappe.dynamic_link.doc.__onload = {}
				}
				frappe.dynamic_link.doc.__onload.phone_nos = [];
			}
		}
	},

	set_phone_no_select_options: function (frm, fieldname, checkbox_field) {
		var all_phone_nos = [];
		if (frm.doc.__onload && frm.doc.__onload.phone_nos) {
			all_phone_nos = frm.doc.__onload.phone_nos;
		}

		var phone_nos = checkbox_field ? all_phone_nos.filter(d => d[checkbox_field]) : all_phone_nos;
		phone_nos = phone_nos.map(d => d.phone);

		var already_set = frm.doc[fieldname];
		if (already_set && !phone_nos.includes(already_set)) {
			 phone_nos.push(already_set);
		}

		frm.set_df_property(fieldname, 'options', [''].concat(phone_nos));
	},
})