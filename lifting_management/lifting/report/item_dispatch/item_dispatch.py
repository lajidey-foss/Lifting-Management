import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	start_date = filters.get("start_date")
	end_date = filters.get("end_date")

	if not start_date or not end_date:
		frappe.throw(_("Start Date and End Date are required"))

	start_date = getdate(start_date)
	end_date = getdate(end_date)
	if start_date > end_date:
		frappe.throw(_("Start Date cannot be after End Date"))

	conditions = ["dispatch.dispatch_date BETWEEN %s AND %s"]
	values = [start_date, end_date]

	if filters.get("dispatch_type"):
		if filters.dispatch_type not in ("DDP", "EXW"):
			frappe.throw(_("Dispatch Type must be DDP or EXW"))
		conditions.append("dispatch.dispatch_type = %s")
		values.append(filters.dispatch_type)

	amount_field = ", COALESCE(SUM(detail.amount), 0) AS total_amount" if filters.get("show_amount") else ""
	rows = frappe.db.sql(
		f"""
		SELECT
			item.name AS item,
			item.item_name AS item_name,
			COALESCE(NULLIF(detail.uom, ''), item.stock_uom) AS uom,
			COALESCE(SUM(detail.quantity), 0) AS total_quantity
			{amount_field}
		FROM `tabTruckon Detail` detail
		INNER JOIN `tabTruckon` dispatch ON dispatch.name = detail.parent
		INNER JOIN `tabItem` item ON item.name = detail.item
		WHERE dispatch.docstatus = 1
			AND {" AND ".join(conditions)}
		GROUP BY item.name, item.item_name, COALESCE(NULLIF(detail.uom, ''), item.stock_uom)
		ORDER BY item.name, uom
		""",
		values,
		as_dict=True,
	)

	data = []
	grand_total_quantity = 0
	grand_total_amount = 0
	for idx, row in enumerate(rows, start=1):
		row["idx"] = idx
		grand_total_quantity += flt(row.total_quantity)
		if filters.get("show_amount"):
			grand_total_amount += flt(row.total_amount)
		data.append(row)

	total_row = {
		"item_name": _("Grand Total"),
		"total_quantity": grand_total_quantity,
		"bold": 1,
	}
	if filters.get("show_amount"):
		total_row["total_amount"] = grand_total_amount
	data.append(total_row)

	return get_columns(filters), data


def get_columns(filters):
	columns = [
		{
			"label": _("S/n"),
			"fieldname": "idx",
			"fieldtype": "Int",
			"width": 50,
		},
		{
			"label": _("Item"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 120,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Total Quantity"),
			"fieldname": "total_quantity",
			"fieldtype": "Float",
			"width": 130,
		},
	]
	if filters.get("show_amount"):
		columns.append(
			{
				"label": _("Total Amount"),
				"fieldname": "total_amount",
				"fieldtype": "Currency",
				"width": 130,
			}
		)
	return columns
