import pandas as pd
import random
from faker import Faker  # ✅ Corrected import

# Initialize Faker
fake = Faker()

# Create 60 demo entries
demo_data = []
interests_list = ["AI", "Web Dev", "Music", "Gaming", "Sports", "Art"]

r_rng = 800

for _ in range(r_rng):
    name = fake.name()
    email = fake.email()
    age = random.randint(18, 70)
    gender = random.choice(["Male", "Female", "Other"])
    dob = fake.date_of_birth(minimum_age=18, maximum_age=70)
    time = fake.time()
    interests = ", ".join(random.sample(interests_list, random.randint(1, 3)))
    bio = fake.sentence(nb_words=10)
    agreed = True

    demo_data.append({
        "Name": name,
        "Email": email,
        "Age": age,
        "Gender": gender,
        "DOB": dob,
        "Time": time,
        "Interests": interests,
        "Bio": bio,
        "Agreed": agreed
    })

# Save to CSV
df = pd.DataFrame(demo_data)
df.to_csv("form_data.csv", index=False)
print(f"✅ form_data.csv created with {r_rng} demo records.")
