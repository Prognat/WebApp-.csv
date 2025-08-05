import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FileInput, Div
from bokeh.io import curdoc
from bokeh.layouts import column
import base64
from io import StringIO

def load_data(file_path):
    lines = file_path.splitlines()

    delimiters = [',', ';']
    
    header_index = None
    delimiter_used = None
    
    for delim in delimiters:
        for i in range(len(lines)):
            if delim in lines[i]:
                try:
                    # Checkt ob die Zeile Darunter Nur aus Zahlen besteht
                    _ = [float(x) for x in lines[i + 1].strip().split(delim)]
                    header_index = i
                    delimiter_used = delim
                    break
                except (ValueError, IndexError):
                    continue
        if header_index is not None:
            break
    
    if header_index is None or delimiter_used is None:
        raise ValueError("Header not found or unsupported delimiter.")

    data_str = "\n".join(lines[header_index:]) # Verwandelt die Daten in einen String bsp: "TIME,CH1\n1,1\n..."
    df = pd.read_csv(StringIO(data_str))
    return df

source = ColumnDataSource(data=dict(x=[], y=[])) # Hier werden die Daten für das Plot gespeichert (Welche Nummern auf den Achsen sind)

plot = figure(title="CSV Data Plot", height=800, width=1800, output_backend="webgl")
plot.line('x', 'y', source=source, line_width=2) # Daten von source werden als Linie geplottet

# UI-Elemente
file_input = FileInput(accept=".csv")
status_div = Div(text="Upload a .csv file to plot data")

# Funktion zum Laden der Daten
def load_file(attr, old, new):
    if not new:
        status_div.text = "No File Uploaded."
        source.data = dict(x=[], y=[])
        return
    try:
        decoded = base64.b64decode(new).decode('utf-8')

        df = load_data(decoded)
        x = df.iloc[:, 0] # Wählt die erste Spalte aus
        y = df.iloc[:, 1]
        source.data = dict(x=x, y=y) # Aktualisiert die Daten im Plot

        plot.xaxis.axis_label = df.columns[0] # Setzt die Beschriftung der X-Achse
        plot.yaxis.axis_label = df.columns[1]

        status_div.text = f"Loaded and plotting columns: {df.columns[0]} vs {df.columns[1]} (Showing {len(df)} points)"
    except Exception as e:
        status_div.text = f"Error loading file: {e}"
        source.data = dict(x=[], y=[]) # Cleart Plot

file_input.on_change("value", load_file)

curdoc().add_root(column(file_input, status_div, plot))
curdoc().title = "CSV WebApp"