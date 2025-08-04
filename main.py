import pandas as pd

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