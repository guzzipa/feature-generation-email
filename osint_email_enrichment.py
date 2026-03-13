#!/usr/bin/env python3
"""
OSINT Email Enrichment Demo
Prueba de concepto para enriquecer un feature store con datos públicos basados en email
"""

import hashlib
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from datetime import datetime


class EmailOSINT:
    """Recolector de información OSINT basado en email"""

    def __init__(self, email: str):
        self.email = email.lower().strip()
        self.domain = self._extract_domain()
        self.features = {}

    def _extract_domain(self) -> str:
        """Extrae el dominio del email"""
        return self.email.split('@')[1] if '@' in self.email else ''

    def _make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Realiza una petición HTTP y retorna JSON"""
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"  ⚠️  HTTP Error {e.code} para {url}")
            return None
        except Exception as e:
            print(f"  ⚠️  Error en request: {str(e)}")
            return None

    def validate_email_format(self) -> Dict[str, Any]:
        """Valida el formato del email"""
        print("\n🔍 Validando formato del email...")

        # Regex básico para validación
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, self.email))

        # Detectar tipo de proveedor
        provider_type = "unknown"
        common_providers = {
            "gmail.com": "gmail",
            "yahoo.com": "yahoo",
            "outlook.com": "outlook",
            "hotmail.com": "outlook",
            "icloud.com": "icloud",
        }
        provider_type = common_providers.get(self.domain, "corporate" if self.domain not in common_providers else "unknown")

        result = {
            "is_valid_format": is_valid,
            "provider_type": provider_type,
            "domain": self.domain,
            "is_free_provider": self.domain in common_providers
        }

        print(f"  ✓ Formato válido: {is_valid}")
        print(f"  ✓ Tipo: {provider_type}")
        print(f"  ✓ Dominio: {self.domain}")

        return result

    def check_gravatar(self) -> Dict[str, Any]:
        """Verifica si existe un Gravatar asociado al email"""
        print("\n👤 Buscando Gravatar...")

        # Gravatar usa MD5 hash del email
        email_hash = hashlib.md5(self.email.encode()).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}"
        profile_url = f"https://www.gravatar.com/{email_hash}.json"

        # Intentar obtener perfil JSON
        profile_data = self._make_request(profile_url)

        result = {
            "has_gravatar": profile_data is not None,
            "avatar_url": gravatar_url if profile_data else None,
            "profile_url": profile_url if profile_data else None
        }

        if profile_data and 'entry' in profile_data:
            entry = profile_data['entry'][0]
            result.update({
                "display_name": entry.get('displayName'),
                "profile_urls": [url.get('value') for url in entry.get('urls', [])],
                "accounts": [acc.get('shortname') for acc in entry.get('accounts', [])]
            })
            print(f"  ✓ Gravatar encontrado: {entry.get('displayName', 'N/A')}")
        else:
            print(f"  ○ No se encontró Gravatar")

        return result

    def check_github(self) -> Dict[str, Any]:
        """Busca perfil de GitHub basado en el email"""
        print("\n💻 Buscando en GitHub...")

        # GitHub API permite buscar por email en commits
        # Nota: esto requiere que el email sea público en los commits
        search_url = f"https://api.github.com/search/users?q={self.email}+in:email"

        headers = {
            'User-Agent': 'OSINT-Email-Enrichment',
            'Accept': 'application/vnd.github.v3+json'
        }

        data = self._make_request(search_url, headers)

        result = {
            "github_found": False,
            "username": None,
            "profile_url": None,
            "public_repos": None
        }

        if data and data.get('total_count', 0) > 0:
            user = data['items'][0]
            result.update({
                "github_found": True,
                "username": user.get('login'),
                "profile_url": user.get('html_url'),
                "avatar_url": user.get('avatar_url')
            })
            print(f"  ✓ GitHub encontrado: {user.get('login')}")

            # Obtener más detalles del usuario
            user_url = user.get('url')
            if user_url:
                user_data = self._make_request(user_url, headers)
                if user_data:
                    result.update({
                        "public_repos": user_data.get('public_repos'),
                        "followers": user_data.get('followers'),
                        "created_at": user_data.get('created_at'),
                        "bio": user_data.get('bio'),
                        "company": user_data.get('company'),
                        "location": user_data.get('location')
                    })
        else:
            print(f"  ○ No se encontró perfil de GitHub")

        return result

    def check_breach_status(self) -> Dict[str, Any]:
        """Verifica si el email apareció en brechas de datos (HIBP)"""
        print("\n🔒 Verificando brechas de datos (HIBP)...")

        # Have I Been Pwned API v3 requiere API key para consultas por email
        # Para demo, usamos el endpoint público que solo requiere User-Agent
        # Nota: En producción necesitarías una API key

        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(self.email)}"
        headers = {
            'User-Agent': 'OSINT-Email-Enrichment-Demo',
            'api-version': '3'
        }

        # Nota: HIBP puede retornar 401 sin API key, esto es esperado en demo
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                breaches = json.loads(response.read().decode())
                result = {
                    "has_breaches": True,
                    "breach_count": len(breaches),
                    "breaches": [b.get('Name') for b in breaches[:5]]  # Solo primeras 5
                }
                print(f"  ⚠️  Encontradas {len(breaches)} brechas")
                return result
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  ✓ No se encontraron brechas")
                return {"has_breaches": False, "breach_count": 0}
            elif e.code == 401:
                print(f"  ⚠️  Se requiere API key para HIBP (esperado en demo)")
                return {"has_breaches": None, "breach_count": None, "note": "API key required"}
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")
            return {"has_breaches": None, "breach_count": None, "error": str(e)}

    def analyze_domain(self) -> Dict[str, Any]:
        """Analiza el dominio del email"""
        print("\n🌐 Analizando dominio...")

        result = {
            "domain": self.domain,
            "is_disposable": self._is_disposable_domain(),
            "mx_records_exist": None  # Requeriría DNS lookup
        }

        # Si es dominio corporativo, podríamos usar Clearbit/Hunter.io
        # Para esta demo, solo mostramos la estructura
        if not result["is_disposable"] and self.domain not in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]:
            result["likely_corporate"] = True
            print(f"  ✓ Probablemente email corporativo")
        else:
            result["likely_corporate"] = False

        return result

    def _is_disposable_domain(self) -> bool:
        """Verifica si es un dominio de email temporal/desechable"""
        # Lista reducida de dominios temporales comunes
        disposable_domains = {
            "tempmail.com", "guerrillamail.com", "10minutemail.com",
            "mailinator.com", "throwaway.email", "temp-mail.org"
        }
        return self.domain in disposable_domains

    def enrich(self) -> Dict[str, Any]:
        """Ejecuta todo el proceso de enriquecimiento OSINT"""
        print(f"\n{'='*60}")
        print(f"🔎 OSINT Email Enrichment para: {self.email}")
        print(f"{'='*60}")

        start_time = datetime.now()

        # Ejecutar todas las verificaciones
        self.features = {
            "email": self.email,
            "enrichment_timestamp": datetime.now().isoformat(),
            "validation": self.validate_email_format(),
            "gravatar": self.check_gravatar(),
            "github": self.check_github(),
            "breach_check": self.check_breach_status(),
            "domain_analysis": self.analyze_domain()
        }

        elapsed = (datetime.now() - start_time).total_seconds()
        self.features["enrichment_duration_seconds"] = elapsed

        print(f"\n{'='*60}")
        print(f"✅ Enriquecimiento completado en {elapsed:.2f} segundos")
        print(f"{'='*60}")

        return self.features

    def generate_feature_vector(self) -> Dict[str, Any]:
        """Genera un vector de features para ML/feature store"""
        print("\n📊 Generando vector de features para feature store...")

        features = {
            # Features de validación
            "email_valid": int(self.features["validation"]["is_valid_format"]),
            "is_free_email": int(self.features["validation"]["is_free_provider"]),
            "is_corporate_email": int(self.features["domain_analysis"].get("likely_corporate", False)),
            "is_disposable_email": int(self.features["domain_analysis"]["is_disposable"]),

            # Features de presencia online
            "has_gravatar": int(self.features["gravatar"]["has_gravatar"]),
            "has_github": int(self.features["github"]["github_found"]),
            "github_public_repos": self.features["github"].get("public_repos", 0) or 0,
            "github_followers": self.features["github"].get("followers", 0) or 0,

            # Features de seguridad
            "breach_count": self.features["breach_check"].get("breach_count", 0) or 0,
            "has_breaches": int(self.features["breach_check"].get("has_breaches", False) or False),

            # Metadata
            "enrichment_timestamp": self.features["enrichment_timestamp"],
            "provider_type": self.features["validation"]["provider_type"]
        }

        # Features derivados
        features["online_presence_score"] = (
            features["has_gravatar"] * 0.3 +
            features["has_github"] * 0.5 +
            min(features["github_public_repos"] / 10, 1.0) * 0.2
        )

        features["trust_score"] = (
            features["email_valid"] * 0.4 +
            (1 - features["is_disposable_email"]) * 0.3 +
            (1 - min(features["breach_count"] / 5, 1.0)) * 0.3
        )

        print("\n  Features generados:")
        for key, value in features.items():
            if not key.endswith("_timestamp") and not key.endswith("_type"):
                print(f"    • {key}: {value}")

        return features


def main():
    """Función principal de demo"""
    import sys

    # Solicitar email si no se proporciona como argumento
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("\n📧 Ingresa el email para análisis OSINT: ").strip()

    if not email or '@' not in email:
        print("❌ Email inválido")
        return

    # Ejecutar enriquecimiento
    osint = EmailOSINT(email)
    full_data = osint.enrich()

    # Generar vector de features
    feature_vector = osint.generate_feature_vector()

    # Guardar resultados
    from pathlib import Path
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)  # Crear carpeta si no existe
    output_file = output_dir / f"osint_results_{email.replace('@', '_at_')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "full_data": full_data,
            "feature_vector": feature_vector
        }, f, indent=2)

    print(f"\n💾 Resultados guardados en: {output_file}")

    # Resumen
    print(f"\n" + "="*60)
    print("📈 RESUMEN DE VIABILIDAD PARA FEATURE STORE")
    print("="*60)
    print(f"\n✅ Features obtenidos: {len(feature_vector)}")
    print(f"⏱️  Tiempo de ejecución: {full_data['enrichment_duration_seconds']:.2f}s")
    print(f"🎯 Trust Score: {feature_vector['trust_score']:.2f}")
    print(f"🌟 Online Presence Score: {feature_vector['online_presence_score']:.2f}")

    print("\n💡 RECOMENDACIONES:")
    print("  • Las APIs gratuitas tienen rate limits")
    print("  • HIBP requiere API key ($) para producción")
    print("  • Considera cachear resultados (TTL: 30-90 días)")
    print("  • Ejecutar de forma asíncrona/batch para múltiples usuarios")
    print("  • Agregar más fuentes: Hunter.io, Clearbit, EmailRep")


if __name__ == "__main__":
    main()
