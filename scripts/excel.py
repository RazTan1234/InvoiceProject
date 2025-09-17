import os
import pandas as pd
from datetime import datetime


def generate_test_excel():
    """Generează un fișier Excel de test cu facturi fictive."""

    # Coloanele obligatorii pentru facturi
    columns = [
        "Număr factură",
        "Data emiterii",
        "Tip factură",
        "Monedă",
        "ID legal vânzător",
        "ID TVA vânzător",
        "Nume cumpărător",
        "ID legal cumpărător",
        "ID TVA cumpărător",
        "Stradă cumpărător",
        "Oraș cumpărător",
        "Județ cumpărător",
        "Țară cumpărător",
        "Termeni plată",
        "Linii factură (produse)",
        "Valoare totală fără TVA",
        "Total TVA",
        "Total plată",
    ]

    # Construim 5 facturi fictive
    today = datetime.today().strftime("%Y-%m-%d")
    data = []
    for i in range(1, 6):
        row = [
            f"INV-100{i}",         # Număr factură
            today,                 # Data emiterii
            "Factura",             # Tip factură
            "RON",                 # Monedă
            "RO1234567",           # ID legal vânzător
            "RO123456789",         # ID TVA vânzător
            f"Cumpărător {i}",     # Nume cumpărător
            f"CUI{i}XYZ",          # ID legal cumpărător
            f"TVA{i}XYZ",          # ID TVA cumpărător
            f"Strada {i}",         # Stradă cumpărător
            f"Oras {i}",           # Oraș cumpărător
            f"Judet {i}",          # Județ cumpărător
            "RO",                  # Țară cumpărător
            "15 zile",             # Termeni plată
            f"Produs {i}, Cantitate {i}",  # Linii factură
            100 * i,               # Valoare totală fără TVA
            19 * i,                # Total TVA
            119 * i,               # Total plată
        ]
        data.append(row)

    # Creăm DataFrame-ul
    df = pd.DataFrame(data, columns=columns)

    # Pregătim calea de salvare
    base_dir = os.path.dirname(os.path.abspath(__file__))   # folderul `core/`
    output_dir = os.path.join(base_dir, "..", "data", "input_samples")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.abspath(os.path.join(output_dir, "Facturi_Test.xlsx"))

    # Scriem fișierul Excel
    df.to_excel(file_path, index=False)

    print(f"✅ Fișier de test generat: {file_path}")


if __name__ == "__main__":
    generate_test_excel()
