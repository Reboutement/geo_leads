# geo_leads

Application Frappe qui recoit les demandes de la landing Geo Engineering (formulaire, widget, agent IA) dans Frappe CRM.

## Installation

```bash
bench get-app /chemin/vers/geo_leads      # ou depuis votre depot git
bench --site crm.votre-domaine.fr install-app geo_leads
```

Prerequis : Frappe v15 et l'application `crm` installee sur le site.

## Utilisation

Methode publique, POST JSON :

```
POST https://crm.votre-domaine.fr/api/method/geo_leads.api.create_lead
```

Champs : `name`, `phone` (obligatoires), `email`, `zip`, `profile`, `symptoms[]`, `slot`, `note`, `type`, `source` (`landing-audit`, `widget`, `agent-ia`), `page`. Le champ `website` est un piege anti-robots et doit rester vide.

- Limite : 10 appels par minute et par adresse.
- Un telephone deja connu ajoute un commentaire a la fiche existante, sans doublon.
- Les details de la demande sont ajoutes en commentaire de la fiche.

## CORS

Dans `sites/<site>/site_config.json` :

```json
{ "allow_cors": "https://www.votre-site.fr" }
```

## Repartition entre commerciaux

Creez une **Assignment Rule** sur le doctype `CRM Lead` (Round Robin ou Load Balancing).

## Tests

```bash
bench --site <site> run-tests --app geo_leads
```

## Points a verifier

Les noms de champs de `CRM Lead` (`first_name`, `last_name`, `mobile_no`, `email`, `source`) et le doctype `CRM Lead Source` (champ `source_name`) correspondent a Frappe CRM tel que je le connais. Controlez-les sur votre version avant la mise en production.
