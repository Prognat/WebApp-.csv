import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FileInput, Div, Select
from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
import base64
from io import StringIO
from bokeh.palettes import Category10 # Für Farben der Linien

color_palette = Category10[10]  # Palette für die Farben der Linien

# Funktion zum Einlesen der CSV-Datei (auch wenn Kommentare davorstehen etc.)
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

    data_str = "\n".join(lines[header_index:])  # Verwandelt die Daten in einen String bsp: "TIME,CH1\n1,1\n..."
    df = pd.read_csv(StringIO(data_str))
    return df

source = ColumnDataSource(data=dict(xs=[], ys=[], labels=[], colors=[]))  # Hier werden die Daten für das Plot gespeichert (Welche Nummern auf den Achsen sind) // xs = Liste von X-Werden für jede Datei, labels = DateiName/Spaltennamen für die Legende, colors = Farbe der Linie

plot = figure(title="CSV Data Plot", height=600, width=1000, output_backend="webgl", sizing_mode="stretch_width")

# UI-Elemente
file_input = FileInput(accept=".csv", styles={"margin-bottom": "10px"})  # Ermöglicht das Hochladen der Datei

status_div = Div(
    text="Upload a .csv file to plot data",
    styles={"font-size": "14px", "color": "#555", "margin-bottom": "15px"}  # Zeigt Statusnachricht an
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

# Funktion zum Zeichnen der Linien im Plot, da Bokeh nicht direkt mehrere Linien gleichzeitig zeichnen kann, wird hier eine Schleife verwendet
def draw_lines():
    plot.renderers = []
    for x, y, color, label in zip(source.data['xs'], source.data['ys'], source.data['colors'], source.data['labels']):
        plot.line(x, y, line_width=2, color=color, legend_label=label)

# Callback für Dropdown-Auswahl der Y-Achse
def update_plot_y_axis(attr, old, new):
    if new is None or new == "":
        return
    current_df = curdoc().all_data[-1]['df']  # Nimmt die zuletzt geladene Datei
    y = current_df[new]
    curdoc().all_data[-1]['y'] = y  # Aktualisiert die Y-Daten der zuletzt geladenen Datei
    source.data['ys'][-1] = y
    draw_lines()
    plot.yaxis.axis_label = new
    status_div.text = f"Showing latest file column: {current_df.columns[0]} vs {new} (Showing {len(current_df)} points)"

# Funktion zum Laden der Daten
def load_file(attr, old, new):
    if not new:
        status_div.text = "No File Uploaded."
        return
    
    if not hasattr(curdoc(), "all_data"):
        curdoc().all_data = [] # Liste zum Speichern aller geladenen Daten

    try:
        decoded = base64.b64decode(new).decode('utf-8')
        df = load_data(decoded)

        x = df.iloc[:, 0]  # Wählt die erste Spalte aus
        y_col = df.columns[1] # Zum speichern des Y-Achsen Spaltennamens
        y = df[y_col]

        color = color_palette[len(curdoc().all_data) % len(color_palette)]  # Wählt eine Farbe aus der Palette basierend auf der Anzahl der geladenen Dateien

        curdoc().all_data.append(dict(df=df, x=x, y=y, label=y_col, color=color)) # Speicher Daten

        # Updated source.data
        source.data = dict(
            xs=[d["x"] for d in curdoc().all_data],
            ys=[d["y"] for d in curdoc().all_data],
            labels=[d["label"] for d in curdoc().all_data],
            colors=[d["color"] for d in curdoc().all_data]
        )

        # DropDown nur für letzte Datei
        if len(df.columns) > 2:
            options = list(df.columns[1:])
            y_axis_select.options = options
            y_axis_select.value = options[0]
            y_axis_select.disabled = False
        else:
            y_axis_select.options = []
            y_axis_select.value = None
            y_axis_select.disabled = True

        draw_lines()

        plot.xaxis.axis_label = df.columns[0]  # Setzt die Beschriftung der X-Achse
        plot.yaxis.axis_label = y_axis_select.value if y_axis_select.value else y_col  # Auswählbar ansonsten die erste Y-Achse

        status_div.text = f"Loaded and plotting {len(curdoc().all_data)} file(s), latest: {df.columns[0]} vs {plot.yaxis.axis_label} (Showing {len(df)} points)"
    except Exception as e:
        status_div.text = f"<b style='color: red;'>Error loading file:</b> {e}"
        source.data = dict(x=[], y=[])  # Cleart Plot
        y_axis_select.options = []
        y_axis_select.value = None
        y_axis_select.disabled = True

# Event Listener für Änderungen
file_input.on_change("value", load_file)
y_axis_select.on_change("value", update_plot_y_axis)

# Layout mit Dropdown Sehbar aber anfangs leer
controls = column(
    Div(text="<h2>CSV Data Plotter</h2>", styles={"margin-bottom": "10px"}),
    file_input,
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