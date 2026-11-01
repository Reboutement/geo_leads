"""Point d'entree public pour les demandes de la landing Geo Engineering.

Methode appelee en POST JSON : /api/method/geo_leads.api.create_lead
Aucune cle d'API n'est exposee au navigateur : la methode est publique, limitee en debit,
et ne fait que creer ou completer une fiche CRM Lead.
"""

import re

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

MAX_TEXT = 1000
ALLOWED_SOURCES = {"landing-audit", "widget", "agent-ia"}
PHONE_RE = re.compile(r"[^\d+]")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _clean(value, limit=MAX_TEXT):
    return (str(value or "")).strip()[:limit]


def _normalize_phone(raw):
    phone = PHONE_RE.sub("", _clean(raw, 30))
    return phone if len(re.sub(r"\D", "", phone)) >= 9 else ""


def _split_name(full_name):
    parts = full_name.split(None, 1)
    return parts[0], (parts[1] if len(parts) > 1 else "")


def _build_notes(d):
    symptoms = d.get("symptoms") or []
    if isinstance(symptoms, str):
        symptoms = [symptoms]
    lines = [
        ("Type de demande", _clean(d.get("type"), 40)),
        ("Profil", _clean(d.get("profile"), 40)),
        ("Symptomes", ", ".join(_clean(s, 80) for s in symptoms[:10])),
        ("Creneau de rappel", _clean(d.get("slot"), 40)),
        ("Code postal", _clean(d.get("zip"), 10)),
        ("Message", _clean(d.get("note"))),
        ("Page", _clean(d.get("page"), 300)),
    ]
    return "\n".join(f"{label} : {value}" for label, value in lines if value)


def _add_comment(lead_name, content):
    frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": "CRM Lead",
            "reference_name": lead_name,
            "content": content.replace("\n", "<br>"),
        }
    ).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=60)
def create_lead():
    d = frappe.form_dict

    # Champ piege : un humain ne le remplit jamais.
    if d.get("website"):
        return {"ok": True}

    full_name = _clean(d.get("name"), 140)
    phone = _normalize_phone(d.get("phone"))
    if not full_name or not phone:
        frappe.throw(_("Nom et telephone valides requis."), frappe.ValidationError)

    email = _clean(d.get("email"), 140)
    if email and not EMAIL_RE.match(email):
        email = ""

    source = _clean(d.get("source"), 40)
    if source not in ALLOWED_SOURCES:
        source = "landing-audit"

    notes = _build_notes(d)

    # Meme telephone deja connu : on complete la fiche au lieu d'en creer une seconde.
    existing = frappe.db.get_value("CRM Lead", {"mobile_no": phone}, "name")
    if existing:
        _add_comment(existing, f"Nouvelle demande ({source})\n{notes}")
        return {"ok": True, "duplicate": True}

    first_name, last_name = _split_name(full_name)
    values = {
        "doctype": "CRM Lead",
        "first_name": first_name,
        "last_name": last_name,
        "mobile_no": phone,
        "email": email,
    }
    if frappe.db.exists("CRM Lead Source", source):
        values["source"] = source

    lead = frappe.get_doc(values)
    lead.insert(ignore_permissions=True)
    _add_comment(lead.name, notes)
    return {"ok": True}
