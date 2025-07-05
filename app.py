import dash
from dash import dcc, html, Output, Input
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc

# Fixed parameters
N_galaxies = 200
field_size = 100
ellipticity = 0.6
np.random.seed(42)

# Galaxy positions
x = np.random.uniform(0, field_size, N_galaxies)
y = np.random.uniform(0, field_size, N_galaxies)

# Base random orientations
theta_random = np.random.uniform(0, np.pi, N_galaxies)

# Alignment functions
def apply_intrinsic_alignment(theta, strength=0.0, preferred_angle=0.0):
    return (1 - strength) * theta + strength * preferred_angle

def apply_lensing_shear(theta, shear_angle=0.0, shear_strength=0.0):
    return theta + shear_strength * np.cos(theta - shear_angle)

# Create ellipse traces
def make_ellipses(x, y, theta, e=ellipticity):
    traces = []
    for xi, yi, t in zip(x, y, theta):
        w = 1.0
        h = w * e
        # Ellipse perimeter
        t_vals = np.linspace(0, 2*np.pi, 30)
        ex = (w/2)*np.cos(t_vals)
        ey = (h/2)*np.sin(t_vals)
        # Rotate
        ex_rot = np.cos(t)*(ex) - np.sin(t)*(ey)
        ey_rot = np.sin(t)*(ex) + np.cos(t)*(ey)
        # Translate
        ex_final = ex_rot + xi
        ey_final = ey_rot + yi
        trace = go.Scatter(
            x=ex_final,
            y=ey_final,
            mode='lines',
            line=dict(color='blue', width=1),
            showlegend=False
        )
        traces.append(trace)
    return traces

# Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY],  title="Galaxy Intrinsic Alignment")

server = app.server

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Markdown("""
            # Galaxy Intrinsic Alignment Simulator
            
            By Simone Spedicato, 2025. [Source code here](https://github.com/SimoneSped/cosmology_focus_project).
            """)
        ], style={"margin":"1em"})
    ]),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label("Intrinsic Alignment Strength:", id="ia-label"),
            dcc.Slider(
                id='ia-strength',
                min=0,
                max=1,
                step=0.05,
                value=0.0,
                marks={0: '0', 0.5: '0.5', 1: '1'}
            ),
            dbc.Tooltip(
                "Controls how strongly galaxies tend to align toward the preferred angle.",
                target="ia-label",
                placement="right"
            ),
            html.Br(),
            html.Label("Lensing Shear Strength:", id="lensing-label"),
            dcc.Slider(
                id='shear-strength',
                min=0,
                max=1,
                step=0.05,
                value=0.0,
                marks={0: '0', 0.5: '0.5', 1: '1'}
            ),
            dbc.Tooltip(
                "Strength of the simulated gravitational lensing distortion.",
                target="lensing-label",
                placement="right"
            ),
            html.Br(),
            html.Label("Preferred Alignment Angle (degrees):", id="preferred-angle-label"),
            dcc.Slider(
                id='preferred-angle',
                min=0,
                max=180,
                step=5,
                value=45,
                marks={0: '0°', 45: '45°', 90: '90°', 135: '135°', 180: '180°'}
            ),
            dbc.Tooltip(
                "The angle toward which galaxies tend to align.",
                target="preferred-angle-label",
                placement="right"
            ),
            html.Br(),
            html.Label("Shear Direction (degrees):", id="shear-label"),
            dcc.Slider(
                id='shear-angle',
                min=0,
                max=180,
                step=5,
                value=90,
                marks={0: '0°', 45: '45°', 90: '90°', 135: '135°', 180: '180°'}
            ),
            dbc.Tooltip(
                "The direction from which gravitational shear is applied.",
                target="shear-label",
                placement="right"
            ),
            html.Br(),
            # dbc.Label("Number of Galaxies:"),
            # dbc.Input(
            #     id="num-galaxies",
            #     type="number",
            #     min=10,
            #     max=5000,
            #     step=10,
            #     value=200,   # default number
            #     debounce=True  # only triggers when user finishes typing or presses Enter
            # ),
            # html.Br(),
            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Checklist(
                        options=[
                            {"label": "Overlay vectors", "value": "show_vectors"}
                        ],
                        value=[],
                        id="vector-toggle",
                        switch=True
                    ),
                    html.Br(),
                    dbc.Label("Shear Pattern:"),
                    dcc.Dropdown(
                        id="shear-pattern",
                        options=[
                            {"label": "Uniform Shear", "value": "uniform"},
                            {"label": "Radial Shear", "value": "radial"},
                            {"label": "Tangential Shear", "value": "tangential"}
                        ],
                        value="uniform",
                        clearable=False
                    ),
                ], title="Other Settings")
            ], start_collapsed = True)
        ], width=3, style={"margin":"1em"}),
        dbc.Col([
            dcc.Graph(id='galaxy-plot'),
        ], width=4),
        dbc.Col([
            dcc.Graph(id='histogram'),
        ], width=4),
    ]),
])

@app.callback(
    Output('galaxy-plot', 'figure'),
    Output('histogram', 'figure'),
    [
        Input("ia-strength", "value"),
        Input("shear-strength", "value"),
        Input("preferred-angle", "value"),
        Input("shear-angle", "value"),
        # Input("num-galaxies", "value"),
        Input("vector-toggle", "value"),
        Input("shear-pattern", "value")
    ],
)
# N = 200! 
def update_plot(
    ia_strength,
    shear_strength,
    preferred_angle_deg,
    shear_angle_deg,
    toggle_value,
    shear_pattern
):
    # Convert angles to radians
    preferred_angle = np.deg2rad(preferred_angle_deg)
    shear_angle_uniform = np.deg2rad(shear_angle_deg)

    # Compute shear angles depending on the pattern
    x_centered = x - 0.5
    y_centered = y - 0.5

    if shear_pattern == "uniform":
        shear_angles = np.full(len(x), shear_angle_uniform)
    elif shear_pattern == "radial":
        shear_angles = np.arctan2(y_centered, x_centered) + np.pi/2
    elif shear_pattern == "tangential":
        shear_angles = np.arctan2(y_centered, x_centered)
    else:
        shear_angles = np.zeros(len(x))

    # Intrinsic alignment component
    intrinsic_offset = ia_strength * np.sin(2 * (preferred_angle - theta_random))

    # Shear component (per-galaxy)
    shear_offset = shear_strength * np.sin(2 * (shear_angles - theta_random))

    # Combine all contributions
    theta_all = theta_random + intrinsic_offset + shear_offset

    # Generate ellipses
    ellipses = make_ellipses(x, y, theta_all)

    fig = go.Figure(ellipses)
    fig.update_layout(
        width=550,
        height=550,
        xaxis=dict(range=[0, field_size], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, field_size], showgrid=False, zeroline=False),
        title=f"IA: {ia_strength:.2f} @ {preferred_angle_deg}°, Shear: {shear_strength:.2f} @ {shear_angle_deg}°",
        margin=dict(l=10, r=10, t=40, b=5),
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    # if vectors are to be shown
    show_vectors = "show_vectors" in toggle_value

    if show_vectors:
        # Length of the axis line (adjust as needed)
        axis_length = 2.5

        # Compute start and end points for each line
        x_start = x - 0.5 * axis_length * np.cos(theta_all)
        y_start = y - 0.5 * axis_length * np.sin(theta_all)

        x_end = x + 0.5 * axis_length * np.cos(theta_all)
        y_end = y + 0.5 * axis_length * np.sin(theta_all)

        # Build line segments with None separators
        x_lines = []
        y_lines = []
        for xs, ys, xe, ye in zip(x_start, y_start, x_end, y_end):
            x_lines.extend([xs, xe, None])
            y_lines.extend([ys, ye, None])

        # Add the Scatter trace
        fig.add_trace(
            go.Scatter(
                x=x_lines,
                y=y_lines,
                mode="lines",
                line=dict(color="red", width=1),
                showlegend=False
            )
        )

    # Histogram
    angles_deg = np.degrees(theta_all) % 180  # wrap to [0,180)
    hist_fig = go.Figure()
    hist_fig.add_trace(go.Histogram(
        x=angles_deg,
        nbinsx=30,
        marker_color='purple'
    ))
    hist_fig.update_layout(
        title="Orientation Angle Histogram",
        xaxis_title="Angle (degrees)",
        # yaxis_title="Count",
        bargap=0.1,
        margin=dict(l=20, r=10, t=40, b=0),
    )

    return fig, hist_fig

if __name__ == '__main__':
    app.run(debug=True)
