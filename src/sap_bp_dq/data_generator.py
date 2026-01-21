from __future__ import annotations
from pathlib import Path
import random
import pandas as pd

def generate_sample_data(rows: int, out_path: Path, seed: int = 42) -> None:
    random.seed(seed)

    names = ["RWE AG", "Bosch", "Siemens", "Chibuike Ikechukwu", "Matthew Ikechukwu", "Anna Müller", "John Doe"]
    cities = ["Essen", "Dortmund", "Berlin", "Lagos", "Munich", "Hamburg"]
    countries = ["DE", "DE", "DE", "NG", "DE", "NL", "FR"]

    data = []
    for i in range(rows):
        bp_type = random.choice(["PERSON", "COMPANY"])
        name = random.choice(names)

        # Intentionally inject some messy data
        if random.random() < 0.08:
            name = name + "  "  # trailing spaces

        email = None
        if bp_type == "PERSON":
            email = "user{}@example.com".format(i)
            if random.random() < 0.07:
                email = "bad-email"  # invalid email sometimes

        phone = "0{}{}".format(random.randint(100, 999), random.randint(100000, 999999))
        if random.random() < 0.05:
            phone = "12"  # too short

        country = random.choice(countries)
        city = random.choice(cities)

        # Missing fields sometimes
        if random.random() < 0.06:
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

    # Inject duplicates
    if rows >= 10:
        data[3]["name"] = "RWE AG"
        data[4]["name"] = "RWE  AG"  # fuzzy duplicate
        data[4]["city"] = data[3]["city"]
        data[4]["country"] = data[3]["country"]

    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)