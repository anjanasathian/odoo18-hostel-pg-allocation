/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    get showTenantInvoiceControlPanelButton() {
        if (this.props.resModel !== "hostel.tenant") {
            return false;
        }
        const invoice = this.model?.root?.data?.invoice_id;
        if (!invoice) {
            return false;
        }
        return Boolean(invoice.id || invoice[0]);
    },

    async onTenantInvoiceControlPanelClick() {
        const resId = this.model?.root?.resId;
        if (!resId) {
            return;
        }
        const action = await this.orm.call("hostel.tenant", "action_view_invoice", [[resId]]);
        if (action) {
            this.actionService.doAction(action);
        }
    },
});
