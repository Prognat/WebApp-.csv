import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

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

    from io import StringIO
    data_str = "\n".join(lines[header_index:]) # Verwandelt die Daten in einen String bsp: "TIME,CH1\n1,1\n..."
    df = pd.read_csv(StringIO(data_str))
    return df

source = ColumnDataSource(data=dict(x=[], y=[])) # Hier werden die Daten für das Plot gespeichert (Welche Nummern auf den Achsen sind)

plot = figure(title="CSV Data Plot", height=300, width=300)
plot.line('x', 'y', source=source, line_width=2) # Daten von source werden als Linie geplottet

df = load_data('Ex1_HP_Diff.csv')
print(df)