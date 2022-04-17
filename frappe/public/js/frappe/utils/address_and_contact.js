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

	get_all_contact_nos: function (frm, link_doctype, link_name) {
		if (link_doctype && link_name) {
			return frappe.call({
				method: "frappe.contacts.doctype.contact.contact.get_all_contact_nos",
				args: {
					link_doctype: link_doctype,
					link_name: link_name,
				},
				callback: function (r) {
					frappe.contacts.set_all_contact_nos(frm, r.message);
				},
			})
		}
	},

	set_all_contact_nos: function (frm, contact_nos) {
		if (contact_nos) {
			if (!frm.doc.__onload) {
				frm.doc.__onload = {};
			}
			frm.doc.__onload.contact_nos = contact_nos;
		}
	},

	set_contact_no_select_options: function (frm, fieldname, checkbox_field) {
		var all_contact_nos = [];
		if (frm.doc.__onload && frm.doc.__onload.contact_nos) {
			all_contact_nos = frm.doc.__onload.contact_nos;
		}

		var filtered_contact_nos = checkbox_field ? all_contact_nos.filter(d => d[checkbox_field]) : all_contact_nos;

		var contact_nos = [];
		$.each(filtered_contact_nos, function (i, d) {
			if (!contact_nos.includes(d.phone)) {
				contact_nos.push(d.phone);
			}
		});

		var already_set = frm.doc[fieldname];
		if (already_set && !contact_nos.includes(already_set)) {
			 contact_nos.push(already_set);
		}

		frm.set_df_property(fieldname, 'options', [''].concat(contact_nos));
	},

	get_contacts_from_number: function (frm, phone_no) {
		contacts = [];
		if (phone_no && frm.doc.__onload && frm.doc.__onload.contact_nos) {
			var contacts = frm.doc.__onload.contact_nos.filter(d => d.phone == phone_no);
			contacts = contacts.map(d => d.contact);
		}
		return contacts;
	}
})