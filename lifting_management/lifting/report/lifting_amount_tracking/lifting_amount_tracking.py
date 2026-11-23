import frappe
from frappe import _
from frappe.utils import getdate


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

	conditions = [
		"dispatch.dispatch_date BETWEEN %s AND %s",
		"dispatch.docstatus < 2",
		"COALESCE(dispatch.status, '') != 'Cancelled'",
	]
	values = [start_date, end_date]

	filter_fields = {
		"truckon": "dispatch.name",
		"payment_wallet": "dispatch.payment_wallet",
		"item": "detail.item",
		"company": "dispatch.company",
		"dispatch_type": "dispatch.dispatch_type",
		"location_from": "dispatch.location_from",
		"status": "dispatch.status",
		"request_order": "dispatch.request_order",
	}
	for filter_name, field_name in filter_fields.items():
		if filters.get(filter_name):
			conditions.append(f"{field_name} = %s")
			values.append(filters[filter_name])

	rows = frappe.db.sql(
		f"""
		SELECT
			dispatch.dispatch_date,
			dispatch.name AS truckon,
			dispatch.status,
			dispatch.payment_wallet,
			dispatch.request_order,
			detail.item,
			item.item_name,
			detail.uom,
			detail.quantity,
			COALESCE(detail.amount, detail.quantity * detail.rate, 0) AS loaded_amount,
			COALESCE(wallet.amount, 0) AS wallet_amount,
			CASE
				WHEN wallet.name IS NULL THEN NULL
				ELSE COALESCE(wallet.amount, 0) - COALESCE(wallet_usage.total_loaded_amount, 0)
			END AS unscheduled_amount,
			dispatch.dispatch_type,
			dispatch.company,
			dispatch.location_from,
			dispatch.plan_order_code
		FROM `tabTruckon` dispatch
		INNER JOIN `tabTruckon Detail` detail ON detail.parent = dispatch.name
		LEFT JOIN `tabItem` item ON item.name = detail.item
		LEFT JOIN `tabPayment Wallet` wallet ON wallet.name = dispatch.payment_wallet
		LEFT JOIN (
			SELECT
				active_dispatch.payment_wallet,
				SUM(COALESCE(active_detail.amount, active_detail.quantity * active_detail.rate, 0))
					AS total_loaded_amount
			FROM `tabTruckon` active_dispatch
			INNER JOIN `tabTruckon Detail` active_detail
				ON active_detail.parent = active_dispatch.name
			WHERE active_dispatch.docstatus < 2
				AND COALESCE(active_dispatch.status, '') != 'Cancelled'
				AND active_dispatch.payment_wallet IS NOT NULL
			GROUP BY active_dispatch.payment_wallet
		) wallet_usage ON wallet_usage.payment_wallet = wallet.name
		WHERE {" AND ".join(conditions)}
		ORDER BY dispatch.dispatch_date, dispatch.name, detail.idx
		""",
		values,
		as_dict=True,
	)

	wallet_groups = {}
	for row in rows:
		group_key = row.payment_wallet or ""
		if group_key not in wallet_groups:
			wallet_groups[group_key] = {
				"payment_wallet": row.payment_wallet,
				"request_order": row.request_order,
				"wallet_amount": row.wallet_amount if row.payment_wallet else None,
				"unscheduled_amount": row.unscheduled_amount,
				"loaded_amount": 0,
				"quantity": 0,
				"children": [],
			}

		group = wallet_groups[group_key]
		group["loaded_amount"] += row.loaded_amount or 0
		group["quantity"] += row.quantity or 0
		row["wallet_amount"] = None
		row["unscheduled_amount"] = None
		row["parent_wallet"] = group_key
		row["indent"] = 1
		group["children"].append(row)

	data = []
	for group in wallet_groups.values():
		data.append(
			{
				"payment_wallet": group["payment_wallet"] or _("No Payment Wallet"),
				"wallet_amount": group["wallet_amount"],
				"request_order": group["request_order"],
				"unscheduled_amount": group["unscheduled_amount"],
				"loaded_amount": group["loaded_amount"],
				"quantity": group["quantity"],
				"parent_wallet": None,
				"indent": 0,
			}
		)
		data.extend(group["children"])

	return get_columns(), data


def get_columns():
	return [
		{
			"label": _("Paid Wallet"),
			"fieldname": "payment_wallet",
			"fieldtype": "Link",
			"options": "Payment Wallet",
			"width": 150,
		},
		{
			"label": _("Request Order"),
			"fieldname": "request_order",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Wallet Amount"),
			"fieldname": "wallet_amount",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Lifted Amount"),
			"fieldname": "loaded_amount",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("UnDispatch Amount"),
			"fieldname": "unscheduled_amount",
			"fieldtype": "Currency",
			"width": 165,
		},
		{
			"label": _("Dispatch Date"),
			"fieldname": "dispatch_date",
			"fieldtype": "Date",
			"width": 105,
		},
		{
			"label": _("Truckon"),
			"fieldname": "truckon",
			"fieldtype": "Link",
			"options": "Truckon",
			"width": 150,
		},
		{
			"label": _("Item"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 130,
		},
		{
			"label": _("Plan Order (SOP Code)"),
			"fieldname": "plan_order_code",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Dispatch Type"),
			"fieldname": "dispatch_type",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100,
		},
	]
