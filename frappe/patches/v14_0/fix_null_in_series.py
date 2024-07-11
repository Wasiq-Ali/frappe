import frappe


def execute():
	frappe.db.sql("delete from tabSeries where current is null")
	frappe.db.commit()
	frappe.db.sql("alter table tabSeries modify current bigint(20) DEFAULT 0 NOT NULL")
