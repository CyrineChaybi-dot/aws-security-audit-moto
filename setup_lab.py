import boto3
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

# 1. Créer l'utilisateur IAM de test.
try:
    iam.get_user(UserName=ADMIN_USER)
    print("[INFO] L'utilisateur existe déjà.")
except iam.exceptions.NoSuchEntityException:
    iam.create_user(UserName=ADMIN_USER)
    print("[OK] Utilisateur IAM créé.")

# 2. Attacher une politique administrative.
admin_policy = "arn:aws:iam::aws:policy/AdministratorAccess"
attached = iam.list_attached_user_policies(UserName=ADMIN_USER)
policy_arns = [p["PolicyArn"] for p in attached["AttachedPolicies"]]
if admin_policy not in policy_arns:
    iam.attach_user_policy(UserName=ADMIN_USER, PolicyArn=admin_policy)
print("[OK] Politique administrative attachée dans le simulateur.")

# 3. Politique de mot de passe volontairement faible.
iam.update_account_password_policy(
    MinimumPasswordLength=8,
    RequireUppercaseCharacters=True,
    RequireLowercaseCharacters=True,
    RequireNumbers=True,
    RequireSymbols=True
)
print("[TEST] Longueur minimale du mot de passe : 8 (faiblesse volontaire).")

# 4. Créer un bucket de test.
try:
    s3.create_bucket(Bucket=BUCKET)
    print("[OK] Bucket de test créé.")
except ClientError as e:
    if e.response["Error"]["Code"] not in (
        "BucketAlreadyOwnedByYou", "BucketAlreadyExists"
    ):
        raise
    print("[INFO] Le bucket existe déjà.")

# 5. Pas de blocage public : l'auditeur devra le détecter.
print("[TEST] Blocage public S3 non configuré volontairement.")
print("\nConfiguration du scénario terminée.")