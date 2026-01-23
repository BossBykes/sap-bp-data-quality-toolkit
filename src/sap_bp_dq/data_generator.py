from __future__ import annotations
from pathlib import Path
import random
import string
import pandas as pd


def _random_person_name(rng: random.Random) -> str:
    first = [
        "Anna", "John", "Mary", "David", "Fatima", "Lukas", "Noah", "Emma",
        "Paul", "Lea", "Mina", "Sam", "Ibrahim", "Sofia", "Klara", "Ben"
    ]
    last = [
        "Müller", "Schmidt", "Weber", "Fischer", "Wagner", "Becker", "Hoffmann",
        "Koch", "Richter", "Klein", "Wolf", "Neumann", "Schwarz", "Ikechukwu"
    ]
    return f"{rng.choice(first)} {rng.choice(last)}"


def _random_company_name(rng: random.Random) -> str:
    stems = [
        "RWE", "E.ON", "BASF", "Bosch", "Siemens", "thyssenkrupp", "Henkel",
        "Evonik", "Continental", "Infineon", "SAP", "Deutsche Bahn"
    ]
    suffixes = ["AG", "GmbH", "SE", "KG", "Group", "Holding"]
    extra = ["Energy", "Trading", "Solutions", "Industries", "Services", "Logistics"]
    # Add variety so we don't constantly repeat the same exact name
    tag = "".join(rng.choices(string.ascii_uppercase, k=2))
    return f"{rng.choice(stems)} {rng.choice(extra)} {tag} {rng.choice(suffixes)}"


def generate_sample_data(rows: int, out_path: Path, seed: int = 42) -> None:
    rng = random.Random(seed)

    cities = [
        "Essen", "Dortmund", "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
        "Düsseldorf", "Stuttgart", "Leipzig", "Bremen", "Hanover", "Nuremberg"
    ]
    countries = ["DE", "NL", "BE", "FR", "GB", "US", "NG"]

    data = []
    for i in range(rows):
        bp_type = rng.choice(["PERSON", "COMPANY"])

        if bp_type == "PERSON":
            name = _random_person_name(rng)
            email = f"user{i}@example.com"
            if rng.random() < 0.07:
                email = "bad-email"
        else:
            name = _random_company_name(rng)
            email = None  # many company master data records may not have a direct email

        # Intentionally inject some messy data
        if rng.random() < 0.08:
            name = name + "  "  # trailing spaces

        phone = f"0{rng.randint(100, 999)}{rng.randint(100000, 999999)}"
        if rng.random() < 0.05:
            phone = "12"  # too short

        country = rng.choice(countries)
        city = rng.choice(cities)

        # Missing fields sometimes
        if rng.random() < 0.06:
            city = None

        data.append(
            {
                "bp_id": f"BP{i:05d}",
                "bp_type": bp_type,
                "name": name,
                "email": email,
                "phone": phone,
                "country": country,
                "city": city,
            }
        )

    # Inject a small, controlled number of duplicates (realistic)
    # Create 10 duplicates: 5 exact, 5 fuzzy
    if rows >= 50:
        dup_indices = rng.sample(range(0, rows), k=10)
        base_indices = rng.sample(range(0, rows), k=10)

        for k in range(10):
            src = base_indices[k]
            dst = dup_indices[k]

            # Copy key fields so they become duplicates on name/city/country
            data[dst]["name"] = data[src]["name"]
            data[dst]["city"] = data[src]["city"]
            data[dst]["country"] = data[src]["country"]

            # Make half of them fuzzy by adding spacing changes
            if k >= 5 and isinstance(data[dst]["name"], str):
                data[dst]["name"] = data[dst]["name"].replace(" ", "  ", 1)

    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)