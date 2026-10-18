import json
from datetime import datetime, timezone

with open("evidence.json", encoding="utf-8") as f:
    data = json.load(f)

guidance = {
    "C1 - MFA Root": (
        "À vérifier dans AWS réel",
        "Activer et vérifier le MFA du compte Root."
    ),
    "C2 - Absence de clés Root": (
        "À vérifier dans AWS réel",
        "Confirmer qu'aucune clé d'accès Root n'existe."
    ),
    "C3 - Administrateur IAM de test": (
        "Selon résultat",
        "Vérifier l'identité, les permissions et le besoin métier."
    ),
    "C4 - MFA de l'utilisateur IAM": (
        "ÉLEVÉ si FAIL",
        "Associer un MFA et vérifier sa présence via l'API."
    ),
    "C5 - Longueur minimale du mot de passe": (
        "MOYEN si FAIL",
        "Configurer une longueur minimale d'au moins 14 caractères."
    ),
    "C6 - Blocage public du bucket S3": (
        "ÉLEVÉ si FAIL",
        "Activer les quatre options de blocage public du bucket."
    ),
    "C7 - Blocage public S3 au niveau du compte": (
        "À vérifier dans AWS réel",
        "Contrôler le paramétrage S3 Control au niveau du compte."
    )
}

lines = [
    "# Rapport professionnel d'audit de sécurité",
    "",
    "**Projet :** AWS Security Audit Lab",
    f"**Date du rapport (UTC) :** {datetime.now(timezone.utc).isoformat()}",
    "**Environnement :** Moto local avec Docker et boto3",
    "**Périmètre :** IAM et S3 simulés ; aucune ressource AWS réelle.",
    "",
    "## 1. Résumé exécutif",
    "",
    "Cet audit teste des contrôles inspirés des bonnes pratiques AWS.",
    "Les résultats concernent uniquement le simulateur local.",
    "",
    "## 2. Résultats",
    "",
    "| Contrôle | Statut | Preuve observée |",
    "|---|---|---|"
]

for c in data["checks"]:
    evidence = c["evidence"].replace("|", "/").replace("\n", " ")
    lines.append(
        f"| {c['control']} | **{c['status']}** | {evidence} |"
    )

summary = data["summary"]
lines += [
    "",
    "## 3. Synthèse des résultats",
    "",
    f"- PASS : {summary.get('PASS', 0)}",
    f"- FAIL : {summary.get('FAIL', 0)}",
    f"- NOT_TESTABLE : {summary.get('NOT_TESTABLE', 0)}",
    "",
    "## 4. Recommandations et priorités",
    ""
]

for c in data["checks"]:
    priority, recommendation = guidance.get(
        c["control"], ("À examiner", "Analyser le résultat.")
    )
    if c["status"] != "PASS":
        lines.append(f"### {c['control']}")
        lines.append(f"- **Statut :** {c['status']}")
        lines.append(f"- **Priorité :** {priority}")
        lines.append(f"- **Recommandation :** {recommendation}")
        if c.get("limitation"):
            lines.append(f"- **Limite :** {c['limitation']}")
        lines.append("")

lines += [
    "## 5. Méthodologie",
    "",
    "1. Préparation d'un scénario de test local.",
    "2. Interrogation des API simulées via boto3.",
    "3. Comparaison des configurations avec les règles attendues.",
    "4. Conservation des résultats JSON et CSV.",
    "5. Correction des écarts testables et nouvelle exécution.",
    "",
    "## 6. Limites et conclusion",
    "",
    "Moto n'est pas un compte AWS réel. Les résultats ne prouvent pas",
    "l'état du MFA Root, l'absence de clés Root ni la configuration",
    "S3 Control au niveau du compte AWS réel.",
    "Un contrôle NOT_TESTABLE exige une vérification complémentaire.",
    "Ce document est un rapport de laboratoire, pas un certificat AWS."
]

with open("report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("Rapport détaillé généré : report.md")
print("Résumé :", summary)