import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, TextInput, Button, Div
from bokeh.io import curdoc
from bokeh.layouts import column

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

plot = figure(title="CSV Data Plot", height=800, width=1800, output_backend="webgl")
plot.line('x', 'y', source=source, line_width=2) # Daten von source werden als Linie geplottet

# UI-Elemente
file_path_input = TextInput(value="", title="Enter path to .csv file:")
load_button = Button(label="Load .csv")
status_div = Div(text="Enter a valid path and press Load")

# Funktion zum Laden der Daten
def load_file():
    path = file_path_input.value.strip()
    if not path:
        status_div.text = "Please enter a file path."
        return
    try:
        df = load_data(path)
        x = df.iloc[:, 0] # Wählt die erste Spalte aus
        y = df.iloc[:, 1]
        source.data = dict(x=x, y=y) # Aktualisiert die Daten im Plot

        plot.xaxis.axis_label = df.columns[0] # Setzt die Beschriftung der X-Achse
        plot.yaxis.axis_label = df.columns[1]

        status_div.text = f"Loaded and plotting columns: {df.columns[0]} vs {df.columns[1]} (Showing {len(df)} points)"
    except Exception as e:
        status_div.text = f"Error loading file: {e}"
        source.data = dict(x=[], y=[]) # Cleart Plot

load_button.on_click(load_file)

curdoc().add_root(column(file_path_input, load_button, status_div, plot))
curdoc().title = "CSV WebApp"