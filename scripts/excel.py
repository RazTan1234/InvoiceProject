import pandas as pd

# Date pentru facturi
data = [
    {
        "Nr. Crt.": 1,
        "Număr factură": "FACT-001/2025",
        "Data emiterii": "14.09.2025",
        "Tip factură": "Factură",
        "Monedă": "RON",
        "Nume vânzător": "SRL Test V",
        "ID legal vânzător": "12345678",
        "ID TVA vânzător": "RO12345678",
        "Stradă vânzător": "Str. Ex 1",
        "Oraș vânzător": "București",
        "Județ vânzător": "București",
        "Cod poștal vânzător": "010101",
        "Țară vânzător": "România",
        "Nume cumpărător": "SRL Test C",
        "ID legal cumpărător": "87654321",
        "ID TVA cumpărător": "RO87654321",
        "Stradă cumpărător": "Str. Test 2",
        "Oraș cumpărător": "Cluj-Napoca",
        "Județ cumpărător": "Cluj",
        "Cod poștal cumpărător": "400001",
        "Țară cumpărător": "România",
        "Termeni plată": "30 zile",
        "Linii factură (produse)": "Produs Test 1,10,buc,50,500,S,19;Serviciu Test 2,5,ore,100,500,S,19",
        "Valoare totală fără TVA": 1000,
        "Total TVA": 190,
        "Total plată": 1190
    },
    {
        "Nr. Crt.": 2,
        "Număr factură": "FACT-002/2025",
        "Data emiterii": "14.09.2025",
        "Tip factură": "Factură",
        "Monedă": "RON",
        "Nume vânzător": "SRL Test V",
        "ID legal vânzător": "12345678",
        "ID TVA vânzător": "RO12345678",
        "Stradă vânzător": "Str. Ex 1",
        "Oraș vânzător": "București",
        "Județ vânzător": "București",
        "Cod poștal vânzător": "010101",
        "Țară vânzător": "România",
        "Nume cumpărător": "SRL Alt C",
        "ID legal cumpărător": "98765432",
        "ID TVA cumpărător": "RO98765432",
        "Stradă cumpărător": "Str. Alt 3",
        "Oraș cumpărător": "Timișoara",
        "Județ cumpărător": "Timiș",
        "Cod poștal cumpărător": "300001",
        "Țară cumpărător": "România",
        "Termeni plată": "15 zile",
        "Linii factură (produse)": "Produs Redus,20,kg,10,200,R,9",
        "Valoare totală fără TVA": 200,
        "Total TVA": 18,
        "Total plată": 218
    },
    {
        "Nr. Crt.": 3,
        "Număr factură": "FACT-003/2025",
        "Data emiterii": "15.09.2025",
        "Tip factură": "Notă credit",
        "Monedă": "RON",
        "Nume vânzător": "SRL Test V",
        "ID legal vânzător": "12345678",
        "ID TVA vânzător": "RO12345678",
        "Stradă vânzător": "Str. Ex 1",
        "Oraș vânzător": "București",
        "Județ vânzător": "București",
        "Cod poștal vânzător": "010101",
        "Țară vânzător": "România",
        "Nume cumpărător": "SRL Test C",
        "ID legal cumpărător": "87654321",
        "ID TVA cumpărător": "RO87654321",
        "Stradă cumpărător": "Str. Test 2",
        "Oraș cumpărător": "Cluj-Napoca",
        "Județ cumpărător": "Cluj",
        "Cod poștal cumpărător": "400001",
        "Țară cumpărător": "România",
        "Termeni plată": "30 zile",
        "Linii factură (produse)": "Produs Test 3,5,buc,30,150,S,19",
        "Valoare totală fără TVA": 150,
        "Total TVA": 28.5,
        "Total plată": 178.5
    }
]

# Creează DataFrame
df = pd.DataFrame(data)

# Salvează în Excel
df.to_excel("Facturi_Test.xlsx", index=False, sheet_name="Facturi_Test")

print("Fișierul Facturi_Test.xlsx a fost generat cu succes!")