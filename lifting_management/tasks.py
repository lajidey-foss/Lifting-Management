# Copyright (c) 2026, Jide Olayinka [Pivotage] and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    """
    occurs after installing app
    """
    create_lm_custom_fields()
    frappe.db.commit()


def after_migrate():
    """ include function to remove obsolete custom fields """
    create_lm_custom_fields()
    #_remove_obsolete_custom_fields()
    frappe.db.commit()

def create_lm_custom_fields():
    """ coming to you """
    custom_fields = _get_lm_custom_fields()

    create_custom_fields(custom_fields, ignore_validate=True)

def _get_lm_custom_fields():
    """
    return: company, customer, item, sales invoice, salesinvoice item, ...
    """
    return {
        # ─ Sales Invoice 
        "Sales Invoice": [
            {
                "fieldname": "lm_section",
                "label": "HBM Section",
                "fieldtype": "Section Break",
                "insert_after": "subscription_section",
                "collapsible": 1,
            },
            {
                "fieldname": "lm_truckon",
                "label": "Truck On",
                "fieldtype": "Data",
                "insert_after": "lm_section",
                "read_only": 0,
            },
            {
                "fieldname": "lm_allocation",
                "label": "Allocation",
                "fieldtype": "Data",
                "insert_after": "lm_truckon",
                "read_only": 0,
            },
        ],
        # +++ Purchase Invoice ++++++++++++++++++++
        "Purchase Invoice": [
            {
                "fieldname": "lm_section",
                "label": "HBM Section",
                "fieldtype": "Section Break",
                "insert_after": "printing_settings",
                "collapsible": 1,
            },
            {
                "fieldname": "lm_truckon",
                "label": "Truck On",
                "fieldtype": "Data",
                "insert_after": "lm_section",
                "read_only": 0,
            },
        ],
    }

def before_uninstall():
    """ Remove custom fields set by this app"""
    custom_fields = _get_lm_custom_fields()
    all_fieldnames = []
    for doctype, fields in custom_fields.items():
        for f in fields:
            all_fieldnames.append(f["fieldname"])
        frappe.db.delete(
            "Custom Field",
            {"dt": doctype, "fieldname": ["in", [f["fieldname"] for f in fields]]},
        )
    frappe.db.commit()