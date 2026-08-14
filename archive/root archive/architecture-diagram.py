"""
Architecture Diagram Generator for BatchETL Pipeline
High resolution professional system architecture diagram with optimized layout
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os


def add_arrow_label(ax, x, y_start, y_end, label, color, fontsize=18):
    """Helper function to add consistent arrow labels"""
    mid_y = (y_start + y_end) / 2
    ax.text(x + 2.0, mid_y, label, 
            fontsize=fontsize, color=color, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                     edgecolor='none', alpha=0.9))


def add_legend(ax):
    """Add color legend to the diagram"""
    COLORS = {
        'orchestration': '#FFF3E0',
        'orchestration_border': '#E65100',
        'processing': '#E8F5E9',
        'processing_border': '#1B5E20',
        'storage': '#F3E5F5',
        'storage_border': '#4A148C',
        'visualization': '#FFF8E1',
        'visualization_border': '#F57F17'
    }
    
    legend_items = [
        ('Orchestration', COLORS['orchestration'], COLORS['orchestration_border']),
        ('Processing', COLORS['processing'], COLORS['processing_border']),
        ('Storage', COLORS['storage'], COLORS['storage_border']),
        ('Visualization', COLORS['visualization'], COLORS['visualization_border'])
    ]
    
    legend_x = 36.0
    legend_y = 28.0
    
    bg = FancyBboxPatch(
        (legend_x - 0.5, legend_y - 2.0), 4.5, 2.4,
        boxstyle="round,pad=0.15",
        facecolor='#FAFAFA',
        edgecolor='#CCCCCC',
        linewidth=2,
        alpha=0.95
    )
    ax.add_patch(bg)
    
    ax.text(legend_x + 2.0, legend_y + 0.1, 'LEGEND', 
            fontsize=16, fontweight='bold', ha='center', color='#1A1A1A')
    
    for i, (label, color, border) in enumerate(legend_items):
        y_pos = legend_y - 0.5 - (i * 0.4)
        rect = patches.Rectangle(
            (legend_x + 0.2, y_pos), 0.4, 0.25,
            facecolor=color, edgecolor=border, linewidth=2.5
        )
        ax.add_patch(rect)
        ax.text(legend_x + 0.8, y_pos + 0.12, label, 
                fontsize=13, va='center', color='#1A1A1A')


def generate_architecture_diagram():
    """
    Generate high resolution professional system architecture diagram
    """
    
    # =========================================================================
    # HIGH RESOLUTION SETTINGS - INCREASED
    # =========================================================================
    FIG_WIDTH = 40          # Increased from 32
    FIG_HEIGHT = 28         # Increased from 24
    DPI = 600               # Increased from 300
    
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    ax.set_xlim(0, FIG_WIDTH)
    ax.set_ylim(0, FIG_HEIGHT)
    ax.axis('off')
    
    # =========================================================================
    # FONT SIZES - ADJUSTED FOR HIGHER RESOLUTION
    # =========================================================================
    FONT = {
        'title': 48,              # Increased from 40
        'subtitle': 32,           # Increased from 26
        'tech_stack': 24,         # Increased from 20
        'layer_title': 32,        # Increased from 26
        'layer_sub': 22,          # Increased from 18
        'box_title': 34,          # Increased from 28
        'box_sub': 24,            # Increased from 20
        'box_tech': 20,           # Increased from 16
        'arrow_label': 24,        # Increased from 20
        'notes_title': 20,        # Increased from 16
        'notes_text': 16,         # Increased from 12
        'legend_title': 20,       # Increased from 16
        'legend_text': 16,        # Increased from 13
        'step_number': 22,        # Increased from 18
        'container_label': 26     # Increased from 22
    }
    
    COLORS = {
        'primary': '#0D47A1',
        'secondary': '#1565C0',
        'orchestration': '#FFF3E0',
        'orchestration_border': '#E65100',
        'processing': '#E8F5E9',
        'processing_border': '#1B5E20',
        'storage': '#F3E5F5',
        'storage_border': '#4A148C',
        'visualization': '#FFF8E1',
        'visualization_border': '#F57F17',
        'white': '#FFFFFF',
        'text_dark': '#1A1A1A',
        'text_medium': '#444444',
        'text_light': '#777777',
        'arrow': '#1565C0',
        'step': '#E53935',
        'container_bg': '#F5F9FF',
        'divider': '#CCCCCC'
    }
    
    # =========================================================================
    # TITLE SECTION
    # =========================================================================
    ax.text(20, 26.5, 'BatchETL Pipeline Architecture', 
            fontsize=FONT['title'], fontweight='bold', ha='center', color=COLORS['primary'])
    ax.text(20, 25.8, 'End-to-End Data Engineering Pipeline', 
            fontsize=FONT['subtitle'], ha='center', color=COLORS['text_medium'], style='italic')
    ax.text(20, 25.0, 'Apache Airflow  |  Pandas  |  PostgreSQL  |  Streamlit', 
            fontsize=FONT['tech_stack'], ha='center', color=COLORS['text_light'])
    
    # =========================================================================
    # LEGEND
    # =========================================================================
    add_legend(ax)
    
    # =========================================================================
    # MAIN CONTAINER
    # =========================================================================
    main_bg = FancyBboxPatch(
        (2.0, 0.8), 36.0, 23.5,
        boxstyle="round,pad=0.3",
        facecolor=COLORS['container_bg'], 
        edgecolor=COLORS['primary'], 
        linewidth=4,
        alpha=0.5
    )
    ax.add_patch(main_bg)
    
    container_label_bg = FancyBboxPatch(
        (14.0, 23.5), 12.0, 0.8,
        boxstyle="round,pad=0.08",
        facecolor=COLORS['primary'],
        edgecolor=COLORS['primary'],
        linewidth=1,
        alpha=0.1
    )
    ax.add_patch(container_label_bg)
    ax.text(20, 23.8, 'DOCKER CONTAINER ENVIRONMENT', 
            fontsize=FONT['container_label'], fontweight='bold', ha='center', color=COLORS['primary'])
    
    # =========================================================================
    # LAYER 1: ORCHESTRATION
    # =========================================================================
    layer1_y = 19.5
    layer1_h = 3.6
    
    layer1_bg = FancyBboxPatch(
        (3.0, layer1_y), 34.0, layer1_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['orchestration'], 
        edgecolor=COLORS['orchestration_border'], 
        linewidth=3.5
    )
    ax.add_patch(layer1_bg)
    
    ax.text(20, layer1_y + layer1_h - 0.6, 'ORCHESTRATION LAYER (Airflow)', 
            fontsize=FONT['layer_title'], fontweight='bold', ha='center', color=COLORS['orchestration_border'])
    
    dag_box = FancyBboxPatch(
        (6.5, layer1_y + 0.6), 27.0, 1.8,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['white'], 
        edgecolor=COLORS['orchestration_border'], 
        linewidth=3.5
    )
    ax.add_patch(dag_box)
    
    ax.text(20, layer1_y + 2.0, 'dags/etl_pipeline.py', 
            fontsize=FONT['box_title'], fontweight='bold', ha='center', color=COLORS['text_dark'])
    ax.text(20, layer1_y + 1.0, 'Schedule: @daily  |  Retries: 1  |  Owner: data_engineer', 
            fontsize=FONT['layer_sub'], ha='center', color=COLORS['text_medium'])
    
    ax.axhline(y=layer1_y, color=COLORS['divider'], linewidth=2, linestyle='--', alpha=0.5)
    
    # =========================================================================
    # ARROW 1 - SHORTER (1/4 of original)
    # =========================================================================
    # Original distance: layer1_y (19.5) to 13.5 = 6.0
    # New distance: 1/4 = 1.5
    arrow1_end = layer1_y - 1.5  # 18.0
    
    add_arrow_label(ax, 20, layer1_y, arrow1_end, 'Triggers DAG', COLORS['arrow'], FONT['arrow_label'])
    ax.annotate(
        '', 
        xy=(20, arrow1_end), 
        xytext=(20, layer1_y),
        arrowprops=dict(
            arrowstyle='->,head_width=1.4,head_length=0.9',
            lw=7,
            color=COLORS['arrow']
        )
    )
    
    # =========================================================================
    # LAYER 2: PROCESSING
    # =========================================================================
    layer2_y = 13.5
    layer2_h = 4.5
    
    layer2_bg = FancyBboxPatch(
        (3.0, layer2_y), 34.0, layer2_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['processing'], 
        edgecolor=COLORS['processing_border'], 
        linewidth=3.5
    )
    ax.add_patch(layer2_bg)
    
    ax.text(20, layer2_y + layer2_h - 0.6, 'PROCESSING LAYER (Python + Pandas)', 
            fontsize=FONT['layer_title'], fontweight='bold', ha='center', color=COLORS['processing_border'])
    
    # ETL boxes - Larger
    box_w = 8.5
    box_h = 2.6
    gap = 2.0
    total_width = (box_w * 3) + (gap * 2)
    start_x = (FIG_WIDTH - total_width) / 2
    
    etl_boxes = [
        {'x': start_x, 'label': 'EXTRACT', 'sub': 'extract.py', 'tech': 'Pandas'},
        {'x': start_x + box_w + gap, 'label': 'TRANSFORM', 'sub': 'transform.py', 'tech': 'Pandas'},
        {'x': start_x + (box_w + gap) * 2, 'label': 'LOAD', 'sub': 'load.py', 'tech': 'SQLAlchemy'}
    ]
    
    for idx, box in enumerate(etl_boxes):
        x = box['x']
        y = layer2_y + 0.8
        
        bx = FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.15",
            facecolor=COLORS['white'], 
            edgecolor=COLORS['processing_border'], 
            linewidth=3.5
        )
        ax.add_patch(bx)
        
        ax.text(x + box_w/2, y + box_h - 0.6, box['label'], 
                fontsize=FONT['box_title'], fontweight='bold', ha='center', color=COLORS['processing_border'])
        ax.text(x + box_w/2, y + box_h - 1.2, box['sub'], 
                fontsize=FONT['box_sub'], ha='center', color=COLORS['text_dark'])
        ax.text(x + box_w/2, y + 0.5, box['tech'], 
                fontsize=FONT['box_tech'], ha='center', color=COLORS['text_light'])
        
        circle = patches.Circle(
            (x + 0.7, y + box_h - 0.6), 0.4, 
            facecolor=COLORS['step'], edgecolor='#B71C1C', linewidth=3
        )
        ax.add_patch(circle)
        ax.text(x + 0.7, y + box_h - 0.6, str(idx + 1), 
                fontsize=FONT['step_number'], fontweight='bold', ha='center', va='center', color='white')
    
    # ETL Arrows
    for i in range(2):
        x1 = start_x + box_w + (i * (box_w + gap))
        x2 = x1 + gap
        ax.annotate(
            '',
            xy=(x2, layer2_y + 2.1),
            xytext=(x1, layer2_y + 2.1),
            arrowprops=dict(
                arrowstyle='->,head_width=0.9,head_length=0.7',
                lw=7,
                color=COLORS['processing_border']
            )
        )
    
    ax.axhline(y=layer2_y + layer2_h, color=COLORS['divider'], linewidth=2, linestyle='--', alpha=0.5)
    
    # =========================================================================
    # ARROW 2 - SHORTER (1/4 of original)
    # =========================================================================
    # Original distance: layer2_y (13.5) to 5.5 = 8.0
    # New distance: 1/4 = 2.0
    arrow2_end = layer2_y - 2.0  # 11.5
    
    add_arrow_label(ax, 20, layer2_y, arrow2_end, 'Load Data', COLORS['arrow'], FONT['arrow_label'])
    ax.annotate(
        '', 
        xy=(20, arrow2_end), 
        xytext=(20, layer2_y),
        arrowprops=dict(
            arrowstyle='->,head_width=1.4,head_length=0.9',
            lw=7,
            color=COLORS['arrow']
        )
    )
    
    # =========================================================================
    # LAYER 3: STORAGE
    # =========================================================================
    layer3_y = 8.0
    layer3_h = 3.0
    
    layer3_bg = FancyBboxPatch(
        (3.0, layer3_y), 34.0, layer3_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['storage'], 
        edgecolor=COLORS['storage_border'], 
        linewidth=3.5
    )
    ax.add_patch(layer3_bg)
    
    ax.text(20, layer3_y + layer3_h - 0.5, 'STORAGE LAYER', 
            fontsize=FONT['layer_title'], fontweight='bold', ha='center', color=COLORS['storage_border'])
    
    storage_boxes = [
        {'x': start_x, 'label': 'Raw CSV', 'sub': '2.96M rows'},
        {'x': start_x + box_w + gap, 'label': 'Staging', 'sub': '2.87M rows'},
        {'x': start_x + (box_w + gap) * 2, 'label': 'PostgreSQL 15', 'sub': 'Data Warehouse'}
    ]
    
    for box in storage_boxes:
        x = box['x']
        y = layer3_y + 0.5
        
        bx = FancyBboxPatch(
            (x, y), box_w, 1.8,
            boxstyle="round,pad=0.15",
            facecolor=COLORS['white'], 
            edgecolor=COLORS['storage_border'], 
            linewidth=3.5
        )
        ax.add_patch(bx)
        
        ax.text(x + box_w/2, y + 1.2, box['label'], 
                fontsize=FONT['box_sub'], fontweight='bold', ha='center', color=COLORS['storage_border'])
        ax.text(x + box_w/2, y + 0.5, box['sub'], 
                fontsize=FONT['box_tech'], ha='center', color=COLORS['text_medium'])
    
    # Storage arrows
    for i in range(2):
        x1 = start_x + box_w + (i * (box_w + gap))
        x2 = x1 + gap
        ax.annotate(
            '',
            xy=(x2, layer3_y + 1.5),
            xytext=(x1, layer3_y + 1.5),
            arrowprops=dict(
                arrowstyle='->,head_width=0.9,head_length=0.7',
                lw=7,
                color=COLORS['storage_border']
            )
        )
    
    # Additional arrows from processing to each storage
    for i in range(3):
        x_pos = start_x + (i * (box_w + gap)) + box_w/2
        ax.annotate(
            '',
            xy=(x_pos, layer3_y + layer3_h),
            xytext=(x_pos, layer2_y + layer2_h),
            arrowprops=dict(
                arrowstyle='->,head_width=0.6,head_length=0.5',
                lw=4,
                color=COLORS['arrow'],
                linestyle='dotted',
                alpha=0.4
            )
        )
    
    ax.axhline(y=layer3_y + layer3_h, color=COLORS['divider'], linewidth=2, linestyle='--', alpha=0.5)
    
    # =========================================================================
    # ARROW 3 - SHORTER (1/4 of original)
    # =========================================================================
    # Original distance: layer3_y (8.0) to 2.0 = 6.0
    # New distance: 1/4 = 1.5
    arrow3_end = layer3_y - 1.5  # 6.5
    
    add_arrow_label(ax, 20, layer3_y, arrow3_end, 'Query Data', COLORS['arrow'], FONT['arrow_label'])
    ax.annotate(
        '', 
        xy=(20, arrow3_end), 
        xytext=(20, layer3_y),
        arrowprops=dict(
            arrowstyle='->,head_width=1.4,head_length=0.9',
            lw=7,
            color=COLORS['arrow']
        )
    )
    
    # =========================================================================
    # LAYER 4: VISUALIZATION
    # =========================================================================
    layer4_y = 4.5
    layer4_h = 1.8
    
    layer4_bg = FancyBboxPatch(
        (3.0, layer4_y), 34.0, layer4_h,
        boxstyle="round,pad=0.15",
        facecolor=COLORS['visualization'], 
        edgecolor=COLORS['visualization_border'], 
        linewidth=3.5
    )
    ax.add_patch(layer4_bg)
    
    ax.text(20, layer4_y + layer4_h - 0.3, 'VISUALIZATION LAYER (Streamlit)', 
            fontsize=FONT['layer_title'], fontweight='bold', ha='center', color=COLORS['visualization_border'])
    
    dash_box = FancyBboxPatch(
        (6.5, layer4_y + 0.15), 27.0, 0.9,
        boxstyle="round,pad=0.08",
        facecolor=COLORS['white'], 
        edgecolor=COLORS['visualization_border'], 
        linewidth=3.5
    )
    ax.add_patch(dash_box)
    
    ax.text(20, layer4_y + 0.8, 'Streamlit Dashboard', 
            fontsize=FONT['box_title'], fontweight='bold', ha='center', color=COLORS['visualization_border'])
    ax.text(20, layer4_y + 0.35, '5 KPIs  |  4 Charts  |  3 Filters  |  < 200ms', 
            fontsize=FONT['layer_sub'], ha='center', color=COLORS['text_medium'])
    
    circle = patches.Circle(
        (4.8, layer4_y + 0.65), 0.35, 
        facecolor=COLORS['step'], edgecolor='#B71C1C', linewidth=3
    )
    ax.add_patch(circle)
    ax.text(4.8, layer4_y + 0.65, '4', 
            fontsize=FONT['step_number'], fontweight='bold', ha='center', va='center', color='white')
    
    # =========================================================================
    # NOTES SECTION
    # =========================================================================
    notes_y = 0.05
    notes_bg = FancyBboxPatch(
        (3.0, notes_y), 28.0, 1.2,
        boxstyle="round,pad=0.08",
        facecolor='#FAFAFA', 
        edgecolor='#CCCCCC', 
        linewidth=2.5,
        alpha=0.95
    )
    ax.add_patch(notes_bg)
    
    ax.text(4.0, notes_y + 0.9, 'NOTES:', 
            fontsize=FONT['notes_title'], fontweight='bold', color=COLORS['text_dark'])
    
    notes = [
        '1. Orchestration Layer: Airflow schedules and monitors the ETL pipeline',
        '2. Processing Layer: Python scripts with Pandas perform data transformations',
        '3. Storage Layer: PostgreSQL stores the final fact_trips table',
        '4. Visualization Layer: Streamlit provides real-time analytics dashboard',
        '5. All services run inside Docker containers for consistency and portability'
    ]
    
    for i, note in enumerate(notes):
        ax.text(4.0, notes_y + 0.7 - (i * 0.14), note, 
                fontsize=FONT['notes_text'], color=COLORS['text_medium'])
    
    # =========================================================================
    # SAVE - High Resolution
    # =========================================================================
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    
    plt.tight_layout(pad=3.0)
    plt.savefig(
        'screenshots/architecture-diagram.png', 
        dpi=DPI,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none',
        pad_inches=0.4
    )
    plt.close()
    
    print("=" * 80)
    print("ARCHITECTURE DIAGRAM GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"File: screenshots/architecture-diagram.png")
    print(f"Size: {FIG_WIDTH} x {FIG_HEIGHT} inches")
    print(f"Resolution: {DPI} DPI")
    print(f"Total Pixels: {FIG_WIDTH * DPI} x {FIG_HEIGHT * DPI}")
    print(f"Total Megapixels: {(FIG_WIDTH * DPI * FIG_HEIGHT * DPI) / 1000000:.1f} MP")
    print("=" * 80)
    print("IMPROVEMENTS:")
    print(f"  - DPI: 300 -> {DPI} (+100%)")
    print(f"  - Size: 32x24 -> {FIG_WIDTH}x{FIG_HEIGHT} (+25%)")
    print(f"  - Font Sizes: Increased 20-30%")
    print(f"  - Arrows: Shortened to 1/4 of original length")
    print("=" * 80)


if __name__ == "__main__":
    generate_architecture_diagram()