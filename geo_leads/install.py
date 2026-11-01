import frappe

SOURCES = ("landing-audit", "widget", "agent-ia")


def after_install():
    """Cree les sources de leads utilisees par la landing, si le CRM les gere."""
    if not frappe.db.exists("DocType", "CRM Lead Source"):
        return
    for name in SOURCES:
        if not frappe.db.exists("CRM Lead Source", name):
            frappe.get_doc({"doctype": "CRM Lead Source", "source_name": name}).insert(
                ignore_permissions=True
            )
    frappe.db.commit()
