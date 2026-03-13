#!/usr/bin/env python3
"""
Batch Processing para enriquecimiento OSINT de múltiples emails
Procesa CSVs/listas de emails y genera features ML para cada uno
"""

import csv
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from osint_email_enrichment import EmailOSINT
from ml_feature_engineering import CreditScoringFeatureEngineer
from example_ml_integration import generate_credit_report


class BatchProcessor:
    """Procesador batch de emails para scoring crediticio"""

    def __init__(self, output_dir: str = "batch_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.results = []
        self.errors = []

    def process_email(self, email: str, user_id: str = None) -> Dict[str, Any]:
        """
        Procesa un email individual

        Args:
            email: Email a procesar
            user_id: ID opcional del usuario

        Returns:
            Diccionario con resultados o error
        """
        try:
            print(f"\n{'='*60}")
            print(f"Procesando: {email}")
            print(f"{'='*60}")

            # 1. Enriquecimiento OSINT
            osint = EmailOSINT(email)
            osint_data = osint.enrich()

            # 2. Feature engineering ML
            engineer = CreditScoringFeatureEngineer(osint_data)
            ml_features = engineer.generate_features()

            # 3. Reporte crediticio
            ml_ready = engineer.to_ml_ready()
            credit_report = generate_credit_report_from_data(ml_ready)

            result = {
                "email": email,
                "user_id": user_id,
                "status": "success",
                "processed_at": datetime.now().isoformat(),
                "osint_data": osint_data,
                "ml_features": engineer.to_dict(),
                "credit_assessment": credit_report
            }

            self.results.append(result)
            return result

        except Exception as e:
            error = {
                "email": email,
                "user_id": user_id,
                "status": "error",
                "error_message": str(e),
                "processed_at": datetime.now().isoformat()
            }
            self.errors.append(error)
            print(f"❌ Error procesando {email}: {e}")
            return error

    def process_csv(self, csv_file: str, email_column: str = "email", id_column: str = None):
        """
        Procesa emails desde un archivo CSV

        Args:
            csv_file: Path al archivo CSV
            email_column: Nombre de la columna con emails
            id_column: Nombre opcional de columna con IDs de usuario
        """
        print(f"\n🔄 Procesando CSV: {csv_file}")
        print(f"   Columna email: {email_column}")
        if id_column:
            print(f"   Columna ID: {id_column}")

        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, 1):
                email = row.get(email_column, '').strip()
                user_id = row.get(id_column) if id_column else f"user_{i}"

                if not email:
                    print(f"⚠️  Fila {i}: email vacío, skipping...")
                    continue

                # Procesar email
                self.process_email(email, user_id)

                # Rate limiting básico (no saturar APIs)
                time.sleep(2.5)  # 2.5 segundos entre requests

        print(f"\n✅ Procesamiento CSV completado")
        print(f"   Total procesados: {len(self.results)}")
        print(f"   Errores: {len(self.errors)}")

    def process_list(self, emails: List[str]):
        """Procesa una lista de emails"""
        print(f"\n🔄 Procesando lista de {len(emails)} emails")

        for i, email in enumerate(emails, 1):
            self.process_email(email, f"user_{i}")
            time.sleep(2.5)  # Rate limiting

        print(f"\n✅ Procesamiento completado")

    def export_results(self, format: str = "json"):
        """
        Exporta resultados a archivos

        Args:
            format: 'json', 'csv', o 'both'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format in ["json", "both"]:
            # Full JSON export
            json_file = self.output_dir / f"batch_results_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump({
                    "metadata": {
                        "processed_at": datetime.now().isoformat(),
                        "total_processed": len(self.results),
                        "total_errors": len(self.errors)
                    },
                    "results": self.results,
                    "errors": self.errors
                }, f, indent=2)
            print(f"\n💾 Resultados JSON: {json_file}")

        if format in ["csv", "both"]:
            # Summary CSV export
            csv_file = self.output_dir / f"batch_summary_{timestamp}.csv"

            with open(csv_file, 'w', newline='') as f:
                if self.results:
                    # Headers
                    fieldnames = [
                        'email', 'user_id', 'status',
                        'overall_trust_score', 'risk_category', 'credit_limit_usd',
                        'account_age_years', 'has_github', 'has_gravatar',
                        'is_disposable_email', 'breach_count',
                        'recommendation'
                    ]

                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for result in self.results:
                        if result['status'] == 'success':
                            ml_feats = result['ml_features']
                            credit = result['credit_assessment']

                            writer.writerow({
                                'email': result['email'],
                                'user_id': result['user_id'],
                                'status': result['status'],
                                'overall_trust_score': ml_feats['overall_trust_score'],
                                'risk_category': credit['risk_assessment']['risk_category'],
                                'credit_limit_usd': credit['suggested_credit_limit_usd'],
                                'account_age_years': ml_feats['account_age_years'],
                                'has_github': ml_feats['has_github'],
                                'has_gravatar': ml_feats['has_gravatar'],
                                'is_disposable_email': ml_feats['is_disposable_email'],
                                'breach_count': ml_feats['breach_count'],
                                'recommendation': credit['risk_assessment']['recommendation']
                            })

                    # Errors CSV
                    if self.errors:
                        errors_csv = self.output_dir / f"batch_errors_{timestamp}.csv"
                        with open(errors_csv, 'w', newline='') as ef:
                            error_writer = csv.DictWriter(ef, fieldnames=['email', 'user_id', 'error_message'])
                            error_writer.writeheader()
                            error_writer.writerows(self.errors)
                        print(f"⚠️  Errores CSV: {errors_csv}")

            print(f"💾 Resumen CSV: {csv_file}")

    def get_statistics(self) -> Dict[str, Any]:
        """Genera estadísticas del batch procesado"""
        if not self.results:
            return {"message": "No hay resultados para analizar"}

        successful = [r for r in self.results if r['status'] == 'success']

        if not successful:
            return {"message": "No hay resultados exitosos"}

        trust_scores = [r['ml_features']['overall_trust_score'] for r in successful]
        credit_limits = [r['credit_assessment']['suggested_credit_limit_usd'] for r in successful]
        account_ages = [r['ml_features']['account_age_years'] for r in successful]

        risk_categories = {}
        for r in successful:
            cat = r['credit_assessment']['risk_assessment']['risk_category']
            risk_categories[cat] = risk_categories.get(cat, 0) + 1

        return {
            "total_processed": len(self.results),
            "successful": len(successful),
            "errors": len(self.errors),
            "trust_score": {
                "mean": sum(trust_scores) / len(trust_scores),
                "min": min(trust_scores),
                "max": max(trust_scores)
            },
            "credit_limit_usd": {
                "mean": sum(credit_limits) / len(credit_limits),
                "min": min(credit_limits),
                "max": max(credit_limits)
            },
            "account_age_years": {
                "mean": sum(account_ages) / len(account_ages),
                "min": min(account_ages),
                "max": max(account_ages)
            },
            "risk_distribution": risk_categories
        }


def generate_credit_report_from_data(ml_ready: Dict[str, Any]) -> Dict[str, Any]:
    """Helper para generar reporte desde ml_ready data"""
    from example_ml_integration import (
        get_credit_score_interpretation,
        calculate_credit_limit_suggestion
    )

    numerical = ml_ready['numerical_features']
    categorical = ml_ready['categorical_features']

    trust_score = numerical['overall_trust_score']
    risk_interp = get_credit_score_interpretation(trust_score)
    credit_limit = calculate_credit_limit_suggestion(numerical)

    return {
        "risk_assessment": risk_interp,
        "suggested_credit_limit_usd": credit_limit,
        "key_scores": {
            "overall_trust": numerical['overall_trust_score'],
            "identity_strength": numerical['identity_strength_score'],
            "activity_engagement": numerical['activity_engagement_score'],
            "security_risk": numerical['security_risk_score']
        }
    }


def main():
    """Demo de batch processing"""
    import sys

    print("\n" + "="*70)
    print("BATCH PROCESSOR - OSINT Credit Scoring")
    print("="*70)

    # Ejemplo de uso
    if len(sys.argv) < 2:
        print("\nUso:")
        print("  1. Procesar CSV:")
        print("     python batch_processing.py input.csv --email-col email --id-col user_id")
        print("\n  2. Procesar lista de emails:")
        print("     python batch_processing.py email1@test.com email2@test.com email3@test.com")
        return

    processor = BatchProcessor(output_dir="batch_results")

    # Detectar si es CSV o lista de emails
    first_arg = sys.argv[1]

    if first_arg.endswith('.csv'):
        # Modo CSV
        csv_file = first_arg
        email_col = "email"
        id_col = None

        # Parse argumentos opcionales
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == "--email-col" and i+1 < len(sys.argv):
                email_col = sys.argv[i+1]
            elif arg == "--id-col" and i+1 < len(sys.argv):
                id_col = sys.argv[i+1]

        processor.process_csv(csv_file, email_col, id_col)

    else:
        # Modo lista de emails
        emails = sys.argv[1:]
        processor.process_list(emails)

    # Exportar resultados
    processor.export_results(format="both")

    # Estadísticas
    stats = processor.get_statistics()
    print("\n" + "="*70)
    print("ESTADÍSTICAS DEL BATCH")
    print("="*70)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
