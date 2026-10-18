# Rapport professionnel d'audit de sécurité

**Projet :** AWS Security Audit Lab
**Date du rapport (UTC) :** 2026-10-18T20:00:07.772740+00:00
**Environnement :** Moto local avec Docker et boto3
**Périmètre :** IAM et S3 simulés ; aucune ressource AWS réelle.

## 1. Résumé exécutif

Cet audit teste des contrôles inspirés des bonnes pratiques AWS.
Les résultats concernent uniquement le simulateur local.

## 2. Résultats

| Contrôle | Statut | Preuve observée |
|---|---|---|
| C1 - MFA Root | **NOT_TESTABLE** | Moto ne représente pas fidèlement la configuration de sécurité Root. |
| C2 - Absence de clés Root | **NOT_TESTABLE** | Les clés d'accès Root réelles ne sont pas accessibles dans ce laboratoire. |
| C3 - Administrateur IAM de test | **PASS** | audit-admin existe et possède la politique AdministratorAccess simulée. |
| C4 - MFA de l'utilisateur IAM | **PASS** | 1 dispositif(s) MFA associé(s) dans Moto. |
| C5 - Longueur minimale du mot de passe | **PASS** | Minimum configuré : 14 caractères ; objectif : 14. |
| C6 - Blocage public du bucket S3 | **PASS** | Les quatre options de blocage public sont activées. |
| C7 - Blocage public S3 au niveau du compte | **NOT_TESTABLE** | Ce test de bucket ne prouve pas le paramétrage S3 Control au niveau du compte. |

## 3. Synthèse des résultats

- PASS : 4
- FAIL : 0
- NOT_TESTABLE : 3

## 4. Recommandations et priorités

### C1 - MFA Root
- **Statut :** NOT_TESTABLE
- **Priorité :** À vérifier dans AWS réel
- **Recommandation :** Activer et vérifier le MFA du compte Root.
- **Limite :** À vérifier dans un vrai compte AWS.

### C2 - Absence de clés Root
- **Statut :** NOT_TESTABLE
- **Priorité :** À vérifier dans AWS réel
- **Recommandation :** Confirmer qu'aucune clé d'accès Root n'existe.
- **Limite :** À vérifier dans un vrai compte AWS.

### C7 - Blocage public S3 au niveau du compte
- **Statut :** NOT_TESTABLE
- **Priorité :** À vérifier dans AWS réel
- **Recommandation :** Contrôler le paramétrage S3 Control au niveau du compte.
- **Limite :** Vérification réelle requise dans un compte AWS.

## 5. Méthodologie

1. Préparation d'un scénario de test local.
2. Interrogation des API simulées via boto3.
3. Comparaison des configurations avec les règles attendues.
4. Conservation des résultats JSON et CSV.
5. Correction des écarts testables et nouvelle exécution.

## 6. Limites et conclusion

Moto n'est pas un compte AWS réel. Les résultats ne prouvent pas
l'état du MFA Root, l'absence de clés Root ni la configuration
S3 Control au niveau du compte AWS réel.
Un contrôle NOT_TESTABLE exige une vérification complémentaire.
Ce document est un rapport de laboratoire, pas un certificat AWS.
