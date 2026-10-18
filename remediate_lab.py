import boto3
import pyotp
import time
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

# Correction 1 : politique de mot de passe.
iam.update_account_password_policy(
    MinimumPasswordLength=14,
    RequireUppercaseCharacters=True,
    RequireLowercaseCharacters=True,
    RequireNumbers=True,
    RequireSymbols=True
)
print("[FIX] Longueur minimale configurée à 14.")

# Correction 2 : blocage public du bucket de test.
s3.put_public_access_block(
    Bucket=BUCKET,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True
    }
)
print("[FIX] Les quatre options de blocage public sont activées.")

# Correction 3 : tentative d'activation du MFA virtuel.
try:
    devices = iam.list_mfa_devices(UserName=ADMIN_USER)["MFADevices"]
    if devices:
        print("[INFO] Un dispositif MFA est déjà associé.")
    else:
        device = iam.create_virtual_mfa_device(
            VirtualMFADeviceName="audit-admin-mfa"
        )["VirtualMFADevice"]
        seed = device["Base32StringSeed"]
        if isinstance(seed, bytes):
            seed = seed.decode("utf-8")
        totp = pyotp.TOTP(seed)
        code1 = totp.now()
        # Attendre la période suivante pour générer le deuxième code.
        time.sleep(max(1, 31 - int(time.time()) % 30))
        code2 = totp.now()
        iam.enable_mfa_device(
            UserName=ADMIN_USER,
            SerialNumber=device["SerialNumber"],
            AuthenticationCode1=code1,
            AuthenticationCode2=code2
        )
        print("[FIX] Dispositif MFA virtuel associé dans le simulateur.")
except Exception as e:
    print("[WARN] MFA virtuel non activé par ce scénario.")
    print("Détail technique :", str(e))
    print("Consulte les journaux et conserve ce résultat comme limite du test.")

print("\nCorrection terminée ; il faut relancer l'audit.")