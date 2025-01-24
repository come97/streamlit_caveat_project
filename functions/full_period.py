from datetime import datetime
# Générer la liste complète des mois entre janvier 2022 et le mois actuel
def generate_full_period(start_date, end_date):
    current_date = start_date
    full_period = []
    while current_date <= end_date:
        full_period.append(current_date)
        # Passer au mois suivant
        next_month = current_date.month % 12 + 1
        next_year = current_date.year + (current_date.month // 12)
        current_date = datetime(next_year, next_month, 1)
    return full_period
