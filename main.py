import pandas as pd
import matplotlib.pyplot as plt


# Anzahl an Gleitkommastellen werden auf 15 gesetzt
pd.set_option('display.precision', 15)
# Setzt die Anzeige von Gleitkommazahlen auf 15 signifikante Stellen (entfernt unnötige Nullen)
pd.set_option('display.float_format', lambda x: f'{x:.15g}')

def load_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        if ',' in lines[i]:
            try:
                # Checkt ob die Zeile darunter nur voller Zahlen ist um sicherzustellen, dass es sich um die Masseneinheiten handelt
                _ = [float(x) for x in lines[i + 1].strip().split(',')]
                header_index = i
                break
            except ValueError:
                continue
    else:
        raise ValueError("Header nicht gefunden.")

    # skiprows = Skippt alles bis es die Masseneinheiten gefunden hat
    df = pd.read_csv(file_path, skiprows=header_index)
    return df

df = load_data('Ex1_HP_Diff.csv')
print(df)

# Plotten der Daten
"""
x_label, y_label = df.columns[:2] # [:2] = Nimmt die ersten 2 Wörter als x und y Achse 

plt.figure(figsize=(10, 6))
plt.plot(df[x_label], df[y_label])
plt.xlabel(x_label)
plt.ylabel(y_label)
plt.grid(True)
plt.tight_layout()
plt.show()
"""