// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Truckon", {
    refresh(frm) {
        calculate_totals(frm);

        if(!frm.is_new()) {
            frm.add_custom_button(__('Allocate'), () => {
                frm.trigger("allocate_trip");
            }).addClass("btn-danger");
        }
    },
    validate(frm) {
        calculate_totals(frm);
    },
    items_add: calculate_totals,
    items_remove: calculate_totals,
    allocate_trip: function(frm) {
        frappe.model.open_mapped_doc({
            method: "lifting_management.lifting.doctype.truckon.truckon.create_trip",
            frm: frm
        });
    }
});

frappe.ui.form.on("Truckon Detail", {
    quantity: update_line_and_totals,
    rate: update_line_and_totals
});

function update_line_and_totals(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const amount = flt(row.quantity) * flt(row.rate);

    frappe.model.set_value(cdt, cdn, "amount", amount);
    calculate_totals(frm);
}

function calculate_totals(frm) {
    const items = frm.doc.items || [];
    const total_quantity = items.reduce(
        (total, row) => total + flt(row.quantity),
        0
    );
    const total_amount = items.reduce(
        (total, row) => total + flt(row.quantity) * flt(row.rate),
        0
    );

    frm.set_value("total_qty", total_quantity);
    frm.set_value("total_amount", total_amount);
    frm.refresh_field("items");
}
