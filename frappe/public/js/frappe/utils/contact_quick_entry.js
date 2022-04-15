frappe.provide('frappe.ui.form');

frappe.ui.form._ContactQuickEntryForm = frappe.ui.form.QuickEntryForm.extend({
	init: function(doctype, after_insert) {
		this._super(doctype, after_insert);
	},

	render_dialog: function() {
		this._super();
		const last_doc = frappe.contacts.get_last_doc(this.doc);
		if(frappe.dynamic_link && frappe.dynamic_link.doc && frappe.dynamic_link.doc.name == last_doc.docname) {
			this.doc.links = [
				{
					idx: 1,
					link_doctype: frappe.dynamic_link.doctype,
					link_name: frappe.dynamic_link.doc[frappe.dynamic_link.fieldname]
				}
			]
		}
	},
});

frappe.ui.form.ContactQuickEntryForm = frappe.ui.form._ContactQuickEntryForm;