import dash
from dash import dcc, html, Output, Input
import plotly.graph_objects as go
import numpy as np

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
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Interactive Galaxy Intrinsic Alignment + Lensing Shear"),
    dcc.Graph(id='galaxy-plot'),
    html.Div([
        html.Label("Intrinsic Alignment Strength:"),
        dcc.Slider(
            id='ia-strength',
            min=0,
            max=1,
            step=0.05,
            value=0.0,
            marks={0: '0', 0.5: '0.5', 1: '1'}
        ),
        html.Br(),
        html.Label("Lensing Shear Strength:"),
        dcc.Slider(
            id='shear-strength',
            min=0,
            max=1,
            step=0.05,
            value=0.0,
            marks={0: '0', 0.5: '0.5', 1: '1'}
        ),
    ], style={'width': '60%'}),
    html.Div([
        html.Label("Preferred Alignment Angle (degrees):"),
        dcc.Slider(
            id='preferred-angle',
            min=0,
            max=180,
            step=5,
            value=45,
            marks={0: '0°', 45: '45°', 90: '90°', 135: '135°', 180: '180°'}
        ),
        html.Br(),
        html.Label("Shear Direction (degrees):"),
        dcc.Slider(
            id='shear-angle',
            min=0,
            max=180,
            step=5,
            value=90,
            marks={0: '0°', 45: '45°', 90: '90°', 135: '135°', 180: '180°'}
        ),
    ], style={'width': '60%'}),
    dcc.Graph(id='histogram')
])

@app.callback(
    Output('galaxy-plot', 'figure'),
    Output('histogram', 'figure'),
    Input('ia-strength', 'value'),
    Input('shear-strength', 'value'),
    Input('preferred-angle', 'value'),
    Input('shear-angle', 'value')
)
def update_plot(ia_strength, shear_strength, preferred_angle_deg, shear_angle_deg):
    preferred_angle = np.deg2rad(preferred_angle_deg)
    shear_angle = np.deg2rad(shear_angle_deg)

    theta_ia = apply_intrinsic_alignment(theta_random, ia_strength, preferred_angle)
    theta_all = apply_lensing_shear(theta_ia, shear_angle, shear_strength)

    ellipses = make_ellipses(x, y, theta_all)

    fig = go.Figure(ellipses)
    fig.update_layout(
        width=600,
        height=600,
        xaxis=dict(range=[0, field_size], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, field_size], showgrid=False, zeroline=False),
        title=f"IA: {ia_strength:.2f} @ {preferred_angle_deg}°, Shear: {shear_strength:.2f} @ {shear_angle_deg}°",
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

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
        yaxis_title="Count",
        bargap=0.1
    )

    return fig, hist_fig

if __name__ == '__main__':
    app.run(debug=True)
