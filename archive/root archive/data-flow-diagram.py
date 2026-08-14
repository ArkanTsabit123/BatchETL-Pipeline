"""
Data Flow Diagram Generator for BatchETL Pipeline
High resolution professional data flow diagram with optimized layout
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os


def generate_dataflow_diagram():
    """
    Generate high resolution professional data flow diagram
    """
    
    # =========================================================================
    # HIGH RESOLUTION SETTINGS
    # =========================================================================
    FIG_WIDTH = 40
    FIG_HEIGHT = 28
    DPI = 600
    
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    ax.set_xlim(0, FIG_WIDTH)
    ax.set_ylim(0, FIG_HEIGHT)
    ax.axis('off')
    
    # =========================================================================
    # FONT SIZES
    # =========================================================================
    FONT = {
        'title': 48,
        'subtitle': 32,
        'step_title': 36,
        'step_sub': 26,
        'box_label': 24,
        'box_value': 20,
        'action_label': 18,
        'action_desc': 16,
        'arrow_label': 24,
        'notes_title': 22,
        'notes_text': 18,
        'data_label': 20
    }
    
    COLORS = {
        'extract': '#FF6B6B',
        'extract_border': '#CC0000',
        'transform': '#4ECDC4',
        'transform_border': '#008080',
        'load': '#45B7D1',
        'load_border': '#0066CC',
        'visualize': '#96CEB4',
        'visualize_border': '#228B22',
        'white': '#FFFFFF',
        'text_dark': '#1A1A1A',
        'text_medium': '#444444',
        'text_light': '#777777',
        'arrow': '#1565C0',
        'step': '#E53935',
        'data_box': '#F9E79F',
        'data_border': '#D4AC0D',
        'container_bg': '#F5F9FF'
    }
    
    # =========================================================================
    # TITLE SECTION
    # =========================================================================
    ax.text(20, 27.0, 'Data Flow Pipeline', 
            fontsize=FONT['title'], fontweight='bold', ha='center', color=COLORS['text_dark'])
    ax.text(20, 26.2, 'Extract  ->  Transform  ->  Load  ->  Visualize', 
            fontsize=FONT['subtitle'], ha='center', color=COLORS['text_medium'], style='italic')
    
    # =========================================================================
    # STEP 1: EXTRACT
    # =========================================================================
    step1_y = 20.5
    step1_h = 4.0
    
    step1_bg = FancyBboxPatch(
        (2.0, step1_y), 36.0, step1_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['extract'],
        edgecolor=COLORS['extract_border'],
        linewidth=3.5,
        alpha=0.15
    )
    ax.add_patch(step1_bg)
    
    # Step number circle
    circle = patches.Circle((3.5, step1_y + step1_h - 0.6), 0.5, 
                            facecolor=COLORS['extract_border'], 
                            edgecolor='white', linewidth=3)
    ax.add_patch(circle)
    ax.text(3.5, step1_y + step1_h - 0.6, '1', 
            fontsize=28, fontweight='bold', ha='center', va='center', color='white')
    
    ax.text(20, step1_y + step1_h - 0.6, 'STEP 1: EXTRACT (extract.py)', 
            fontsize=FONT['step_title'], fontweight='bold', ha='center', color=COLORS['extract_border'])
    
    # Detail boxes
    details = [
        {'label': 'INPUT', 'value': 'data/raw/taxi_data.csv', 'x': 7.0},
        {'label': 'ACTION', 'value': 'pd.read_csv() -> DataFrame', 'x': 20.0},
        {'label': 'OUTPUT', 'value': 'data/staging/taxi_raw.csv', 'x': 33.0}
    ]
    
    for detail in details:
        bx = FancyBboxPatch(
            (detail['x'] - 4.5, step1_y + 0.6), 9.0, 1.8,
            boxstyle="round,pad=0.1",
            facecolor=COLORS['white'],
            edgecolor=COLORS['extract_border'],
            linewidth=2.5
        )
        ax.add_patch(bx)
        ax.text(detail['x'], step1_y + 1.9, detail['label'], 
                fontsize=FONT['box_label'], fontweight='bold', ha='center', 
                color=COLORS['extract_border'])
        ax.text(detail['x'], step1_y + 1.1, detail['value'], 
                fontsize=FONT['box_value'], ha='center', color=COLORS['text_dark'])
    
    ax.text(20, step1_y + 0.2, 'Time: ~1 second  |  Rows: 2,964,624', 
            fontsize=FONT['step_sub'], ha='center', color=COLORS['text_medium'], style='italic')
    
    # =========================================================================
    # DATA FLOW LABEL 1
    # =========================================================================
    data_bg1 = FancyBboxPatch(
        (16.5, 19.0), 7.0, 0.8,
        boxstyle="round,pad=0.08",
        facecolor=COLORS['data_box'],
        edgecolor=COLORS['data_border'],
        linewidth=2.5
    )
    ax.add_patch(data_bg1)
    ax.text(20, 19.4, 'Raw Data', 
            fontsize=FONT['data_label'], fontweight='bold', ha='center', color='#7D6608')
    
    # Arrow 1
    ax.annotate(
        '',
        xy=(20, 19.0),
        xytext=(20, step1_y),
        arrowprops=dict(
            arrowstyle='->,head_width=1.2,head_length=0.8',
            lw=7,
            color=COLORS['arrow']
        )
    )
    
    # =========================================================================
    # STEP 2: TRANSFORM
    # =========================================================================
    step2_y = 13.5
    step2_h = 5.0
    
    step2_bg = FancyBboxPatch(
        (2.0, step2_y), 36.0, step2_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['transform'],
        edgecolor=COLORS['transform_border'],
        linewidth=3.5,
        alpha=0.15
    )
    ax.add_patch(step2_bg)
    
    circle = patches.Circle((3.5, step2_y + step2_h - 0.6), 0.5, 
                            facecolor=COLORS['transform_border'], 
                            edgecolor='white', linewidth=3)
    ax.add_patch(circle)
    ax.text(3.5, step2_y + step2_h - 0.6, '2', 
            fontsize=28, fontweight='bold', ha='center', va='center', color='white')
    
    ax.text(20, step2_y + step2_h - 0.6, 'STEP 2: TRANSFORM (transform.py)', 
            fontsize=FONT['step_title'], fontweight='bold', ha='center', color=COLORS['transform_border'])
    
    # Transform actions - 5 boxes in 2 rows
    actions = [
        {'label': '1. Drop duplicates', 'desc': 'Remove duplicate records', 'x': 5.0, 'row': 0},
        {'label': '2. Drop nulls', 'desc': 'On critical columns', 'x': 12.0, 'row': 0},
        {'label': '3. Convert datetime', 'desc': 'Pickup & dropoff times', 'x': 19.0, 'row': 0},
        {'label': '4. Feature engineering', 'desc': 'Hour, day, month', 'x': 26.0, 'row': 0},
        {'label': '5. Filter outliers', 'desc': 'Distance < 100, Fare < 500', 'x': 33.0, 'row': 0}
    ]
    
    for action in actions:
        bx = FancyBboxPatch(
            (action['x'] - 3.0, step2_y + 1.8 - (action['row'] * 1.8)), 6.0, 1.2,
            boxstyle="round,pad=0.08",
            facecolor=COLORS['white'],
            edgecolor='#B2DFDB',
            linewidth=2
        )
        ax.add_patch(bx)
        ax.text(action['x'], action['row'] * -0.4 + step2_y + 2.6, action['label'], 
                fontsize=FONT['action_label'], fontweight='bold', ha='center', 
                color=COLORS['text_dark'])
        ax.text(action['x'], action['row'] * -0.4 + step2_y + 2.1, action['desc'], 
                fontsize=FONT['action_desc'], ha='center', color=COLORS['text_medium'], 
                style='italic')
    
    ax.text(20, step2_y + 0.2, 'Output: data/staging/taxi_clean.csv  |  Rows: 2,869,525  |  Time: ~5-8 seconds', 
            fontsize=FONT['step_sub'], ha='center', color=COLORS['text_medium'], style='italic')
    
    # =========================================================================
    # DATA FLOW LABEL 2
    # =========================================================================
    data_bg2 = FancyBboxPatch(
        (16.5, 12.0), 7.0, 0.8,
        boxstyle="round,pad=0.08",
        facecolor=COLORS['data_box'],
        edgecolor=COLORS['data_border'],
        linewidth=2.5
    )
    ax.add_patch(data_bg2)
    ax.text(20, 12.4, 'Clean Data', 
            fontsize=FONT['data_label'], fontweight='bold', ha='center', color='#7D6608')
    
    # Arrow 2
    ax.annotate(
        '',
        xy=(20, 12.0),
        xytext=(20, step2_y),
        arrowprops=dict(
            arrowstyle='->,head_width=1.2,head_length=0.8',
            lw=7,
            color=COLORS['arrow']
        )
    )
    
    # =========================================================================
    # STEP 3: LOAD
    # =========================================================================
    step3_y = 7.5
    step3_h = 3.8
    
    step3_bg = FancyBboxPatch(
        (2.0, step3_y), 36.0, step3_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['load'],
        edgecolor=COLORS['load_border'],
        linewidth=3.5,
        alpha=0.15
    )
    ax.add_patch(step3_bg)
    
    circle = patches.Circle((3.5, step3_y + step3_h - 0.6), 0.5, 
                            facecolor=COLORS['load_border'], 
                            edgecolor='white', linewidth=3)
    ax.add_patch(circle)
    ax.text(3.5, step3_y + step3_h - 0.6, '3', 
            fontsize=28, fontweight='bold', ha='center', va='center', color='white')
    
    ax.text(20, step3_y + step3_h - 0.6, 'STEP 3: LOAD (load.py)', 
            fontsize=FONT['step_title'], fontweight='bold', ha='center', color=COLORS['load_border'])
    
    details = [
        {'label': 'INPUT', 'value': 'taxi_clean.csv', 'x': 7.0},
        {'label': 'ACTION', 'value': 'df.to_sql() with SQLAlchemy', 'x': 20.0},
        {'label': 'OUTPUT', 'value': 'PostgreSQL fact_trips', 'x': 33.0}
    ]
    
    for detail in details:
        bx = FancyBboxPatch(
            (detail['x'] - 4.5, step3_y + 0.5), 9.0, 1.7,
            boxstyle="round,pad=0.1",
            facecolor=COLORS['white'],
            edgecolor=COLORS['load_border'],
            linewidth=2.5
        )
        ax.add_patch(bx)
        ax.text(detail['x'], step3_y + 1.7, detail['label'], 
                fontsize=FONT['box_label'], fontweight='bold', ha='center', 
                color=COLORS['load_border'])
        ax.text(detail['x'], step3_y + 1.0, detail['value'], 
                fontsize=FONT['box_value'], ha='center', color=COLORS['text_dark'])
    
    ax.text(20, step3_y + 0.2, 'Time: ~3-5 seconds  |  Mode: Append', 
            fontsize=FONT['step_sub'], ha='center', color=COLORS['text_medium'], style='italic')
    
    # =========================================================================
    # DATA FLOW LABEL 3
    # =========================================================================
    data_bg3 = FancyBboxPatch(
        (15.5, 6.0), 9.0, 0.8,
        boxstyle="round,pad=0.08",
        facecolor=COLORS['data_box'],
        edgecolor=COLORS['data_border'],
        linewidth=2.5
    )
    ax.add_patch(data_bg3)
    ax.text(20, 6.4, 'Database Records', 
            fontsize=FONT['data_label'], fontweight='bold', ha='center', color='#7D6608')
    
    # Arrow 3
    ax.annotate(
        '',
        xy=(20, 6.0),
        xytext=(20, step3_y),
        arrowprops=dict(
            arrowstyle='->,head_width=1.2,head_length=0.8',
            lw=7,
            color=COLORS['arrow']
        )
    )
    
    # =========================================================================
    # STEP 4: VISUALIZE
    # =========================================================================
    step4_y = 2.0
    step4_h = 3.5
    
    step4_bg = FancyBboxPatch(
        (2.0, step4_y), 36.0, step4_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['visualize'],
        edgecolor=COLORS['visualize_border'],
        linewidth=3.5,
        alpha=0.15
    )
    ax.add_patch(step4_bg)
    
    circle = patches.Circle((3.5, step4_y + step4_h - 0.6), 0.5, 
                            facecolor=COLORS['visualize_border'], 
                            edgecolor='white', linewidth=3)
    ax.add_patch(circle)
    ax.text(3.5, step4_y + step4_h - 0.6, '4', 
            fontsize=28, fontweight='bold', ha='center', va='center', color='white')
    
    ax.text(20, step4_y + step4_h - 0.6, 'STEP 4: VISUALIZE (Streamlit Dashboard)', 
            fontsize=FONT['step_title'], fontweight='bold', ha='center', color=COLORS['visualize_border'])
    
    features = [
        {'label': 'Query', 'value': 'PostgreSQL', 'x': 6.0},
        {'label': 'KPIs', 'value': '5 metrics', 'x': 13.0},
        {'label': 'Charts', 'value': '4 types', 'x': 20.0},
        {'label': 'Filters', 'value': '3 filters', 'x': 27.0},
        {'label': 'Response', 'value': '< 200ms', 'x': 34.0}
    ]
    
    for feature in features:
        bx = FancyBboxPatch(
            (feature['x'] - 2.5, step4_y + 0.5), 5.0, 1.5,
            boxstyle="round,pad=0.08",
            facecolor=COLORS['white'],
            edgecolor='#A9DFBF',
            linewidth=2
        )
        ax.add_patch(bx)
        ax.text(feature['x'], step4_y + 1.5, feature['label'], 
                fontsize=FONT['box_label'], fontweight='bold', ha='center', 
                color=COLORS['text_medium'])
        ax.text(feature['x'], step4_y + 0.9, feature['value'], 
                fontsize=FONT['box_value'], ha='center', color=COLORS['text_dark'])
    
    # =========================================================================
    # NOTES SECTION
    # =========================================================================
    notes_y = 0.1
    notes_bg = FancyBboxPatch(
        (2.0, notes_y), 28.0, 1.6,
        boxstyle="round,pad=0.1",
        facecolor='#FAFAFA',
        edgecolor='#CCCCCC',
        linewidth=3,
        alpha=0.95
    )
    ax.add_patch(notes_bg)
    
    ax.text(3.0, notes_y + 1.25, 'NOTES:', 
            fontsize=FONT['notes_title'], fontweight='bold', color=COLORS['text_dark'])
    
    notes = [
        '1. Extract: Reads raw CSV into Pandas DataFrame and stages it',
        '2. Transform: Cleans data, removes duplicates, filters outliers, adds features',
        '3. Load: Inserts transformed data into PostgreSQL using SQLAlchemy',
        '4. Visualize: Streamlit queries PostgreSQL for real-time analytics',
        '5. Total rows processed: 2,964,624 -> 2,869,525 after cleaning'
    ]
    
    for i, note in enumerate(notes):
        ax.text(3.0, notes_y + 0.95 - (i * 0.17), note, 
                fontsize=FONT['notes_text'], color=COLORS['text_medium'])
    
    # =========================================================================
    # SAVE
    # =========================================================================
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    
    plt.tight_layout(pad=3.0)
    plt.savefig(
        'screenshots/data-flow-diagram.png',
        dpi=DPI,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none',
        pad_inches=0.4
    )
    plt.close()
    
    print("=" * 80)
    print("DATA FLOW DIAGRAM GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"File: screenshots/data-flow-diagram.png")
    print(f"Size: {FIG_WIDTH} x {FIG_HEIGHT} inches")
    print(f"Resolution: {DPI} DPI")
    print(f"Total Pixels: {FIG_WIDTH * DPI} x {FIG_HEIGHT * DPI}")
    print("=" * 80)


if __name__ == "__main__":
    generate_dataflow_diagram()