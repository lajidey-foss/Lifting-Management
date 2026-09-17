// Copyright (c) 2026, Jide Olayinka [Pivotage Integrated] and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Wallet", {
	refresh(frm) {
        if(!frm.is_new()) {
			frm.add_custom_button(__('Truckon'),
				function() {
					frm.trigger("make_truckons")
				}, __('Create'));	
			
		}

	},
    make_truckons: function(frm) {
		frappe.model.open_mapped_doc({
			method: "lifting_management.lifting.doctype.payment_wallet.payment_wallet.create_truckon",
			frm: frm
		})
	},
});
