import frappe
from frappe import _
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, nowdate


def execute(filters=None):
	today = getdate(nowdate())
	start_date = get_first_day(add_months(today, -11))
	end_date = get_last_day(today)

	monthly_quantities = frappe.db.sql(
		"""
		SELECT
			DATE_FORMAT(dispatch.dispatch_date, '%%Y-%%m') AS month_key,
			SUM(detail.quantity) AS quantity
		FROM `tabTruckon` dispatch
		INNER JOIN `tabTruckon Detail` detail ON detail.parent = dispatch.name
		WHERE dispatch.docstatus = 1
			AND dispatch.status = 'Scheduled'
			AND dispatch.dispatch_date BETWEEN %s AND %s
		GROUP BY month_key
		""",
		(start_date, end_date),
		as_dict=True,
	)
	quantities_by_month = {row.month_key: flt(row.quantity) for row in monthly_quantities}

	labels = []
	values = []
	data = []
	for month_offset in range(12):
		month_start = get_first_day(add_months(start_date, month_offset))
		month_key = month_start.strftime("%Y-%m")
		month_label = month_start.strftime("%b %Y")
		quantity = quantities_by_month.get(month_key, 0)

		labels.append(month_label)
		values.append(quantity)
		data.append({"month": month_label, "quantity": quantity})

	chart = {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Qty"), "values": values}],
		},
		"type": "line",
		"fieldtype": "Float",
	}

	return get_columns(), data, None, chart


def get_columns():
	return [
		{
			"label": _("Month"),
			"fieldname": "month",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Qty"),
			"fieldname": "quantity",
			"fieldtype": "Float",
			"width": 120,
		},
	]
