import boto3
import csv
import json
from datetime import datetime, timezone
from botocore.exceptions import ClientError

ENDPOINT = "http://localhost:5000"
ADMIN_USER = "audit-admin"
BUCKET = "aws-audit-lab-bucket-2026-01"

session = boto3.Session(
    aws_access_key_id="testing",
    aws_secret_access_key="testing",
    region_name="us-east-1"
)
iam = session.client("iam", endpoint_url=ENDPOINT)
s3 = session.client("s3", endpoint_url=ENDPOINT)

checks = []


def record(control, status, evidence, limitation=""):
    checks.append({
        "control": control,
        "status": status,
        "evidence": evidence,
        "limitation": limitation
    })
    print(f"[{status}] {control} — {evidence}")


# C1 : MFA du compte Root.
record(
    "C1 - MFA Root",
    "NOT_TESTABLE",
    "Moto ne représente pas fidèlement la configuration de sécurité Root.",
    "À vérifier dans un vrai compte AWS."
)

# C2 : clés d'accès Root.
record(
    "C2 - Absence de clés Root",
    "NOT_TESTABLE",
    "Les clés d'accès Root réelles ne sont pas accessibles dans ce laboratoire.",
    "À vérifier dans un vrai compte AWS."
)

# C3 : présence d'un utilisateur administratif.
try:
    iam.get_user(UserName=ADMIN_USER)
    attached = iam.list_attached_user_policies(UserName=ADMIN_USER)
    arns = [p["PolicyArn"] for p in attached["AttachedPolicies"]]
    admin_policy = "arn:aws:iam::aws:policy/AdministratorAccess"
    if admin_policy in arns:
        record(
            "C3 - Administrateur IAM de test",
            "PASS",
            f"{ADMIN_USER} existe et possède la politique AdministratorAccess simulée."
        )
    else:
        record(
            "C3 - Administrateur IAM de test",
            "FAIL",
            "Utilisateur trouvé, mais politique administrative absente."
        )
except ClientError as e:
    record(
        "C3 - Administrateur IAM de test",
        "FAIL",
        f"Erreur de vérification : {e.response['Error']['Code']}"
    )

# C4 : MFA de l'utilisateur IAM.
try:
    devices = iam.list_mfa_devices(UserName=ADMIN_USER)["MFADevices"]
    if devices:
        record(
            "C4 - MFA de l'utilisateur IAM",
            "PASS",
            f"{len(devices)} dispositif(s) MFA associé(s) dans Moto."
        )
    else:
        record(
            "C4 - MFA de l'utilisateur IAM",
            "FAIL",
            "Aucun dispositif MFA associé à l'utilisateur de test."
        )
except ClientError as e:
    record(
        "C4 - MFA de l'utilisateur IAM",
        "NOT_TESTABLE",
        f"API indisponible ou erreur : {e.response['Error']['Code']}"
    )

# C5 : longueur minimale du mot de passe.
try:
    policy = iam.get_account_password_policy()["PasswordPolicy"]
    minimum = policy.get("MinimumPasswordLength", 0)
    status = "PASS" if minimum >= 14 else "FAIL"
    record(
        "C5 - Longueur minimale du mot de passe",
        status,
        f"Minimum configuré : {minimum} caractères ; objectif : 14."
    )
except ClientError as e:
    record(
        "C5 - Longueur minimale du mot de passe",
        "FAIL",
        f"Politique inaccessible : {e.response['Error']['Code']}"
    )

# C6 : blocage public du bucket de test.
try:
    config = s3.get_public_access_block(Bucket=BUCKET)[
        "PublicAccessBlockConfiguration"
    ]
    keys = [
        "BlockPublicAcls",
        "IgnorePublicAcls",
        "BlockPublicPolicy",
        "RestrictPublicBuckets"
    ]
    missing = [key for key in keys if not config.get(key, False)]
    if not missing:
        record(
            "C6 - Blocage public du bucket S3",
            "PASS",
            "Les quatre options de blocage public sont activées."
        )
    else:
        record(
            "C6 - Blocage public du bucket S3",
            "FAIL",
            "Options désactivées : " + ", ".join(missing)
        )
except ClientError as e:
    record(
        "C6 - Blocage public du bucket S3",
        "FAIL",
        f"Aucun blocage vérifiable : {e.response['Error']['Code']}"
    )

# C7 : blocage public au niveau du compte AWS.
record(
    "C7 - Blocage public S3 au niveau du compte",
    "NOT_TESTABLE",
    "Ce test de bucket ne prouve pas le paramétrage S3 Control au niveau du compte.",
    "Vérification réelle requise dans un compte AWS."
)

# Produire des preuves horodatées.
report = {
    "project": "AWS Security Audit Lab",
    "environment": "Moto local - simulation",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "checks": checks,
    "summary": {
        status: sum(1 for c in checks if c["status"] == status)
        for status in ("PASS", "FAIL", "NOT_TESTABLE")
    }
}

with open("evidence.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

with open("evidence.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=["control", "status", "evidence", "limitation"]
    )
    writer.writeheader()
    writer.writerows(checks)

with open("report.md", "w", encoding="utf-8") as f:
    f.write("# Rapport d'audit de sécurité\n\n")
    f.write(f"- Environnement : {report['environment']}\n")
    f.write(f"- Date UTC : {report['timestamp_utc']}\n\n")
    f.write("## Résultats\n\n")
    f.write("| Contrôle | Statut | Preuve |\n")
    f.write("|---|---|---|\n")
    for c in checks:
        f.write(
            f"| {c['control']} | {c['status']} | "
            f"{c['evidence'].replace('|', '/')} |\n"
        )
    f.write("\n## Limites\n\n")
    f.write(
        "Les résultats proviennent d'un simulateur local. "
        "Ils ne certifient pas la configuration d'un compte AWS réel.\n"
    )

print("\nRésumé :", report["summary"])
print("Fichiers créés : evidence.json, evidence.csv, report.md")