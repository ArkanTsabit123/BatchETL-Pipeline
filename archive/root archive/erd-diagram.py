"""
ERD Diagram Generator for BatchETL Pipeline
High resolution professional ERD diagram with optimized layout
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os


def generate_erd_diagram():
    """
    Generate high resolution professional ERD diagram
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
        'table_title': 32,
        'header': 20,
        'cell': 18,
        'cell_pk': 18,
        'section_title': 24,
        'section_sub': 18,
        'rule_header': 18,
        'rule_cell': 16,
        'notes_title': 22,
        'notes_text': 18,
        'legend_text': 18
    }
    
    COLORS = {
        'primary': '#1a5276',
        'secondary': '#2E86C1',
        'index': '#E67E22',
        'quality': '#1ABC9C',
        'white': '#FFFFFF',
        'row_even': '#F8F9FA',
        'row_odd': '#FFFFFF',
        'text_dark': '#1A1A1A',
        'text_medium': '#444444',
        'text_light': '#777777',
        'border': '#D5D8DC',
        'pk_highlight': '#FFF3CD'
    }
    
    # =========================================================================
    # TITLE SECTION
    # =========================================================================
    ax.text(20, 27.0, 'Entity Relationship Diagram', 
            fontsize=FONT['title'], fontweight='bold', ha='center', color=COLORS['primary'])
    ax.text(20, 26.2, 'fact_trips Table Structure', 
            fontsize=FONT['subtitle'], ha='center', color=COLORS['text_medium'], style='italic')
    
    # =========================================================================
    # MAIN TABLE
    # =========================================================================
    table_x = 2.0
    table_y = 9.0
    table_w = 22.0
    table_h = 16.5
    
    table_bg = FancyBboxPatch(
        (table_x, table_y), table_w, table_h,
        boxstyle="round,pad=0.15",
        facecolor='#F0F8FF',
        edgecolor=COLORS['primary'],
        linewidth=3.5
    )
    ax.add_patch(table_bg)
    
    # Table Header
    header_bg = FancyBboxPatch(
        (table_x + 0.2, table_y + table_h - 1.0), table_w - 0.4, 0.9,
        boxstyle="round,pad=0.05",
        facecolor=COLORS['primary'],
        edgecolor=COLORS['primary'],
        linewidth=1
    )
    ax.add_patch(header_bg)
    ax.text(20, table_y + table_h - 0.5, 'fact_trips', 
            fontsize=FONT['table_title'], fontweight='bold', ha='center', va='center', color='white')
    
    # Column Headers
    headers = ['Column', 'Type', 'Nullable', 'Notes']
    header_positions = [4.5, 10.5, 15.5, 20.5]
    
    for i, header in enumerate(headers):
        ax.text(header_positions[i], table_y + table_h - 1.4, header, 
                fontsize=FONT['header'], fontweight='bold', ha='center', va='center', 
                color='white')
    
    # Table Data
    columns = [
        {'name': 'trip_id', 'type': 'SERIAL', 'nullable': 'NOT NULL', 'notes': 'PRIMARY KEY', 'pk': True},
        {'name': 'vendor_id', 'type': 'INTEGER', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'pickup_datetime', 'type': 'TIMESTAMP', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'dropoff_datetime', 'type': 'TIMESTAMP', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'passenger_count', 'type': 'INTEGER', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'trip_distance', 'type': 'FLOAT', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'fare_amount', 'type': 'FLOAT', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'total_amount', 'type': 'FLOAT', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'payment_type', 'type': 'INTEGER', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'pickup_hour', 'type': 'INTEGER', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'pickup_day', 'type': 'VARCHAR(20)', 'nullable': 'NULL', 'notes': '', 'pk': False},
        {'name': 'pickup_month', 'type': 'INTEGER', 'nullable': 'NULL', 'notes': '', 'pk': False}
    ]
    
    row_height = 1.15
    start_y = table_y + table_h - 2.0
    
    for i, col in enumerate(columns):
        y_pos = start_y - (i * row_height)
        
        # Row background
        if col['pk']:
            row_color = COLORS['pk_highlight']
        else:
            row_color = COLORS['row_even'] if i % 2 == 0 else COLORS['row_odd']
        
        row_bg = FancyBboxPatch(
            (table_x + 0.2, y_pos - row_height + 0.1), table_w - 0.4, row_height - 0.1,
            boxstyle="round,pad=0.02",
            facecolor=row_color,
            edgecolor=COLORS['border'],
            linewidth=0.5
        )
        ax.add_patch(row_bg)
        
        # Column values
        col_name = col['name']
        if col['pk']:
            col_name = f"{col_name} 🔑"
            ax.text(4.5, y_pos - row_height/2 + 0.15, col_name, 
                    fontsize=FONT['cell_pk'], fontweight='bold', ha='center', va='center', 
                    color=COLORS['primary'])
        else:
            ax.text(4.5, y_pos - row_height/2 + 0.15, col_name, 
                    fontsize=FONT['cell'], ha='center', va='center', color=COLORS['text_dark'])
        
        ax.text(10.5, y_pos - row_height/2 + 0.15, col['type'], 
                fontsize=FONT['cell'], ha='center', va='center', color=COLORS['text_medium'])
        ax.text(15.5, y_pos - row_height/2 + 0.15, col['nullable'], 
                fontsize=FONT['cell'], ha='center', va='center', color=COLORS['text_medium'])
        
        if col['notes']:
            ax.text(20.5, y_pos - row_height/2 + 0.15, col['notes'], 
                    fontsize=FONT['cell'], fontweight='bold', ha='center', va='center', 
                    color=COLORS['primary'])
    
    # =========================================================================
    # INDEXES SECTION
    # =========================================================================
    index_x = 25.5
    index_y = 14.0
    index_w = 12.5
    index_h = 5.0
    
    index_bg = FancyBboxPatch(
        (index_x, index_y), index_w, index_h,
        boxstyle="round,pad=0.15",
        facecolor='#FDF2E9',
        edgecolor=COLORS['index'],
        linewidth=3
    )
    ax.add_patch(index_bg)
    
    ax.text(index_x + index_w/2, index_y + index_h - 0.5, 'INDEXES', 
            fontsize=FONT['section_title'], fontweight='bold', ha='center', 
            color=COLORS['index'])
    
    indexes = [
        {'name': 'idx_pickup_datetime', 'purpose': 'Faster time-based queries'},
        {'name': 'idx_pickup_day', 'purpose': 'Faster day-of-week aggregation'},
        {'name': 'idx_fare_amount', 'purpose': 'Faster fare-based filtering'}
    ]
    
    for i, idx in enumerate(indexes):
        y_pos = index_y + index_h - 1.2 - (i * 1.3)
        ax.text(index_x + 0.8, y_pos, f'• {idx["name"]}', 
                fontsize=FONT['section_sub'], fontweight='bold', ha='left', va='center', 
                color=COLORS['text_dark'])
        ax.text(index_x + 0.8, y_pos - 0.4, idx['purpose'], 
                fontsize=FONT['rule_cell'], ha='left', va='center', 
                color=COLORS['text_medium'], style='italic')
    
    # =========================================================================
    # DATA QUALITY RULES SECTION
    # =========================================================================
    quality_x = 25.5
    quality_y = 7.5
    quality_w = 12.5
    quality_h = 6.0
    
    quality_bg = FancyBboxPatch(
        (quality_x, quality_y), quality_w, quality_h,
        boxstyle="round,pad=0.15",
        facecolor='#E8F8F5',
        edgecolor=COLORS['quality'],
        linewidth=3
    )
    ax.add_patch(quality_bg)
    
    ax.text(quality_x + quality_w/2, quality_y + quality_h - 0.5, 'DATA QUALITY RULES', 
            fontsize=FONT['section_title'], fontweight='bold', ha='center', 
            color=COLORS['quality'])
    
    # Rule headers
    headers = ['Rule', 'Condition', 'Action']
    header_positions = [quality_x + 1.5, quality_x + 5.5, quality_x + 10.0]
    
    for i, header in enumerate(headers):
        ax.text(header_positions[i], quality_y + quality_h - 1.0, header, 
                fontsize=FONT['rule_header'], fontweight='bold', ha='center', va='center', 
                color=COLORS['text_dark'])
    
    rules = [
        {'rule': 'trip_distance', 'condition': '> 0', 'action': 'Filter'},
        {'rule': 'fare_amount', 'condition': '> 0', 'action': 'Filter'},
        {'rule': 'trip_distance', 'condition': '< 100 miles', 'action': 'Remove Outlier'},
        {'rule': 'fare_amount', 'condition': '< $500', 'action': 'Remove Outlier'},
        {'rule': 'Critical columns', 'condition': 'NOT NULL', 'action': 'Drop Row'}
    ]
    
    for i, rule in enumerate(rules):
        y_pos = quality_y + quality_h - 1.6 - (i * 0.85)
        ax.text(quality_x + 1.5, y_pos, rule['rule'], 
                fontsize=FONT['rule_cell'], ha='center', va='center', 
                color=COLORS['text_dark'])
        ax.text(quality_x + 5.5, y_pos, rule['condition'], 
                fontsize=FONT['rule_cell'], ha='center', va='center', 
                color=COLORS['text_medium'])
        ax.text(quality_x + 10.0, y_pos, rule['action'], 
                fontsize=FONT['rule_cell'], fontweight='bold', ha='center', va='center', 
                color=COLORS['quality'] if rule['action'] == 'Filter' else COLORS['text_dark'])
    
    # =========================================================================
    # LEGEND
    # =========================================================================
    legend_x = 25.5
    legend_y = 4.0
    legend_w = 12.5
    legend_h = 2.8
    
    legend_bg = FancyBboxPatch(
        (legend_x, legend_y), legend_w, legend_h,
        boxstyle="round,pad=0.15",
        facecolor='#FAFAFA',
        edgecolor='#CCCCCC',
        linewidth=2.5,
        alpha=0.95
    )
    ax.add_patch(legend_bg)
    
    ax.text(legend_x + legend_w/2, legend_y + legend_h - 0.3, 'LEGEND', 
            fontsize=FONT['section_title'], fontweight='bold', ha='center', 
            color=COLORS['text_dark'])
    
    legend_items = [
        {'label': 'Primary Key', 'color': COLORS['pk_highlight'], 'border': COLORS['primary']},
        {'label': 'Indexes', 'color': '#FDF2E9', 'border': COLORS['index']},
        {'label': 'Quality Rules', 'color': '#E8F8F5', 'border': COLORS['quality']}
    ]
    
    for i, item in enumerate(legend_items):
        x_pos = legend_x + 1.0 + (i * 3.8)
        rect = patches.Rectangle(
            (x_pos, legend_y + 0.5), 0.5, 0.35,
            facecolor=item['color'], edgecolor=item['border'], linewidth=2.5
        )
        ax.add_patch(rect)
        ax.text(x_pos + 0.7, legend_y + 0.65, item['label'], 
                fontsize=FONT['legend_text'], va='center', color=COLORS['text_dark'])
    
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
        '1. fact_trips is the central fact table optimized for analytical queries',
        '2. trip_id is an auto-incrementing surrogate primary key',
        '3. Time dimensions (hour, day, month) are extracted from pickup_datetime',
        '4. Three indexes optimize query performance for common filters',
        '5. Data quality rules ensure clean and valid data in the warehouse'
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
        'screenshots/erd-diagram.png',
        dpi=DPI,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='none',
        pad_inches=0.4
    )
    plt.close()
    
    print("=" * 80)
    print("ERD DIAGRAM GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"File: screenshots/erd-diagram.png")
    print(f"Size: {FIG_WIDTH} x {FIG_HEIGHT} inches")
    print(f"Resolution: {DPI} DPI")
    print(f"Total Pixels: {FIG_WIDTH * DPI} x {FIG_HEIGHT * DPI}")
    print("=" * 80)


if __name__ == "__main__":
    generate_erd_diagram()