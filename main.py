import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FileInput, Div, Select
from bokeh.io import curdoc
from bokeh.layouts import column
import base64
from io import StringIO

def load_data(file_path):
    lines = file_path.splitlines()

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

    data_str = "\n".join(lines[header_index:]) # Verwandelt die Daten in einen String bsp: "TIME,CH1\n1,1\n..."
    df = pd.read_csv(StringIO(data_str))
    return df

source = ColumnDataSource(data=dict(x=[], y=[])) # Hier werden die Daten für das Plot gespeichert (Welche Nummern auf den Achsen sind)

plot = figure(title="CSV Data Plot", height=800, width=1800, output_backend="webgl")
line_renderer = plot.line('x', 'y', source=source, line_width=2) # Daten von source werden als Linie geplottet

# UI-Elemente
file_input = FileInput(accept=".csv")
status_div = Div(text="Upload a .csv file to plot data")

y_axis_select = Select(title="Choose Y-Axis", options=[], value=None)

def update_plot_y_axis(attr, old, new):
    if new is None or new == "":
        return
    y = current_df[new]
    source.data = dict(x=current_df.iloc[:, 0], y=y)
    plot.yaxis.axis_label = new
    status_div.text = f"Showing columns: {current_df.columns[0]} vs {new} (Showing {len(current_df)} points)"

# Funktion zum Laden der Daten
def load_file(attr, old, new):
    global current_df

    if not new:
        status_div.text = "No File Uploaded."
        source.data = dict(x=[], y=[])
        y_axis_select.options = []
        y_axis_select.value = None
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