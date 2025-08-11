import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FileInput, Div, Select, Spinner
from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
import base64
from io import StringIO
import csv
from bokeh.palettes import Category10  # Für Farben der Linien

color_palette = Category10[10]  # Palette für die Farben der Linien

source = ColumnDataSource(data=dict(xs=[], ys=[], labels=[], colors=[]))  # Hier werden die Daten für das Plot gespeichert

plot = figure(
    title="CSV Data Plot", 
    height=600, width=1000, 
    output_backend="webgl", 
    sizing_mode="stretch_width"
)

# UI-Elemente
file_input = FileInput(
    accept=".csv", 
    styles={"margin-bottom": "10px"}
)  # Ermöglicht das Hochladen der Datei

skip_rows_input = Spinner(
    title="Skip Rows", low=0, step=1, value=0, width=100
)  # Anzahl der zu überspringenden Zeilen

status_div = Div(
    text="Upload a .csv file to plot data",
    styles={"font-size": "14px", "color": "#555", "margin-bottom": "15px"}  
    # Zeigt Statusnachricht an
)

y_axis_select = Select(
    title="Choose Y-Axis",  # Auswahl der Y-Achse (falls mehrere Spalten)
    options=[],
    value=None,
    disabled=True,
    width=250,
    styles={"margin-bottom": "20px"}
)

Warning_Message = Div(
    text="!!! You Cant Upload Large Files !!!",
    styles={"font-size": "15px", "color": "#555", "margin-top": "20px"}
)

# Funktion zum Einlesen der CSV-Datei (auch wenn Kommentare davorstehen etc.)
def load_data(data_str, skip_rows=0):
    # Entferne überflüssige Trennzeichen am Zeilenende
    lines = [line.rstrip(';,\t| ') for line in data_str.splitlines() if line.strip()]

    sample = "\n".join(lines[:10])

    # Versucht das Trennzeichen automatisch zu erkennen
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample)
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ','  # Standard-Trennzeichen, falls Erkennung fehlschlägt

    for i in range(len(lines)):
        try:
            _ = [float(x.strip()) for x in lines[i + 1].split(delimiter)]
            header_index = i
            break
        except:
            continue
    else:
        raise ValueError("Header nicht gefunden.")
    
    data_lines = lines[header_index:]

    if skip_rows > 0:
        data_lines = [data_lines[0]] + data_lines[1 + skip_rows:]

    cleaned_str = "\n".join(data_lines)  # Entfernt alle Zeilen vor dem Header und verwandelt die Daten in einen String

    df = pd.read_csv(StringIO(cleaned_str), delimiter=delimiter)

    df = df.dropna(axis=1, how='all')  # Entfernt leere Spalten
    df.columns = [col.strip() for col in df.columns]  # Entfernt Leerzeichen in den Spaltennamen
    return df

# Funktion zum Zeichnen der Linien im Plot, da Bokeh nicht direkt mehrere Linien gleichzeitig zeichnen kann, wird hier eine Schleife verwendet
def draw_lines():
    plot.renderers = []
    for x, y, color, label in zip(source.data['xs'], source.data['ys'], source.data['colors'], source.data['labels']):
        plot.line(x, y, line_width=2, color=color, legend_label=label)

# Funktion die Auswählbaren Y-Achsen aktualisiert  
def update_y_axis_options():
    if not hasattr(curdoc(), "all_data"):
        return
    
    seen = set()
    unique_cols = []
    for d in curdoc().all_data:
        for col in d['df'].columns[1:]:
            if col.lower() not in seen:
                seen.add(col.lower())
                unique_cols.append(col)

    y_axis_select.options = unique_cols
    if unique_cols:
        y_axis_select.value = unique_cols[0]  # Setzt den Standardwert auf die erste Spalte
        y_axis_select.disabled = False
    else:
        y_axis_select.value = None
        y_axis_select.disabled = True

# Callback für Dropdown-Auswahl der Y-Achse
def update_plot_y_axis(attr, old, new):
    if not new:
        return
    
    new_lower = new.lower()
    xs, ys, labels, colors = [], [], [], []

    for d in curdoc().all_data:
        match_col = None
        # Sucht nach der Spalte, die mit der neuen Y-Achse übereinstimmt
        for col in d['df'].columns[1:]:
            if col.lower() == new_lower:
                match_col = col
                break
        # Zeigt nur die Spalten an, die mit der neuen Y-Achse übereinstimmen
        if match_col:
            xs.append(d['df'].iloc[:, 0])
            ys.append(d['df'][match_col])
            labels.append(d['label'])
            colors.append(d['color'])

    source.data = dict(xs=xs, ys=ys, labels=labels, colors=colors)
    draw_lines()
    plot.yaxis.axis_label = new

file_counter = 0  # Zähler für die Namen in der Legende

# Funktion zum Laden der Daten
def load_file(attr, old, new):
    global file_counter

    if not new:
        status_div.text = "No File Uploaded."
        return
    
    if not hasattr(curdoc(), "all_data"):
        curdoc().all_data = []  # Liste zum Speichern aller geladenen Daten

    try:
        decoded = base64.b64decode(new).decode('utf-8')
        skip_rows = skip_rows_input.value or 0
        df = load_data(decoded, skip_rows=skip_rows)

        x = df.iloc[:, 0]  # Wählt die erste Spalte aus
        file_counter += 1
        file_name = f"File {file_counter}"

        color = color_palette[len(curdoc().all_data) % len(color_palette)]  
        # Wählt eine Farbe aus der Palette basierend auf der Anzahl der geladenen Dateien

        curdoc().all_data.append(dict(df=df, x=x, label=file_name, color=color))  # Speichert Daten

        update_y_axis_options()

        update_plot_y_axis(None, None, y_axis_select.value)

        plot.xaxis.axis_label = df.columns[0]

        status_div.text = f"Loaded {len(curdoc().all_data)} file(s), latest: {file_name} (Showing {len(df)} points)"
    except Exception as e:
        status_div.text = f"<b style='color: red;'>Error loading file:</b> {e}"
        source.data = dict(xs=[], ys=[], labels=[], colors=[])  # Cleart Plot
        y_axis_select.options = []
        y_axis_select.value = None
        y_axis_select.disabled = True

# Event Listener für Änderungen
file_input.on_change("value", load_file)
y_axis_select.on_change("value", update_plot_y_axis)

# Layout mit Dropdown sichtbar aber anfangs leer
controls = column(
    Div(text="<h2>CSV Data Plotter</h2>", styles={"margin-bottom": "10px"}),
    file_input,
    skip_rows_input,
    status_div,
    y_axis_select,
    Warning_Message,
    width=300,
    sizing_mode="fixed",
    styles={
        "border": "1px solid #ddd",
        "padding": "15px",
        "border-radius": "8px",
        "background-color": "#fafafa"
    }
)

layout = row(controls, Spacer(width=20), plot, sizing_mode="stretch_both")  # Kombination der UI-Elemente mit Plot
curdoc().add_root(layout)
curdoc().title = "CSV WebApp"