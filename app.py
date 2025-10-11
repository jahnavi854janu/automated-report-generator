import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Automated Report Generator",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .upload-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def analyze_data(df):
    """Analyze the dataframe and generate insights"""
    analysis = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'missing_values': df.isnull().sum().to_dict(),
        'summary_stats': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
    }
    return analysis

def create_visualizations(df, numeric_cols):
    """Create visualizations for the report"""
    charts = []
    
    if len(numeric_cols) > 0:
        # Bar chart
        fig1 = px.bar(df, x=df.index[:10], y=numeric_cols[0], 
                     title=f'{numeric_cols[0]} - Top 10 Records',
                     color_discrete_sequence=['#667eea'])
        img_bytes1 = fig1.to_image(format="png", width=800, height=400)
        charts.append(img_bytes1)
        
        # Line chart if there are at least 2 numeric columns
        if len(numeric_cols) >= 2:
            fig2 = px.line(df[:20], x=df.index[:20], y=numeric_cols[1],
                          title=f'{numeric_cols[1]} - Trend Analysis',
                          color_discrete_sequence=['#764ba2'])
            img_bytes2 = fig2.to_image(format="png", width=800, height=400)
            charts.append(img_bytes2)
    
    return charts

def generate_pdf_report(df, analysis, charts):
    """Generate a formatted PDF report using ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    elements.append(Paragraph("Automated Data Analysis Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                             styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_data = [
        ['Total Records', str(analysis['total_rows'])],
        ['Total Columns', str(analysis['total_columns'])],
        ['Numeric Columns', str(len(analysis['numeric_columns']))],
        ['Categorical Columns', str(len(analysis['categorical_columns']))]
    ]
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f7fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Column Information
    elements.append(Paragraph("Column Information", heading_style))
    elements.append(Paragraph(f"<b>Numeric Columns:</b> {', '.join(analysis['numeric_columns']) if analysis['numeric_columns'] else 'None'}", 
                             styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Categorical Columns:</b> {', '.join(analysis['categorical_columns']) if analysis['categorical_columns'] else 'None'}", 
                             styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Statistical Summary
    if analysis['summary_stats']:
        elements.append(Paragraph("Statistical Summary", heading_style))
        for col, stats in list(analysis['summary_stats'].items())[:3]:  # First 3 numeric columns
            elements.append(Paragraph(f"<b>{col}</b>", styles['Heading3']))
            stats_data = [[k, f"{v:.2f}" if isinstance(v, float) else str(v)] 
                         for k, v in stats.items()]
            stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f7fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 12))
    
    # Data Preview
    elements.append(PageBreak())
    elements.append(Paragraph("Data Preview (First 10 Rows)", heading_style))
    preview_data = [df.columns.tolist()] + df.head(10).values.tolist()
    
    # Truncate long strings
    preview_data = [[str(cell)[:20] + '...' if len(str(cell)) > 20 else str(cell) 
                    for cell in row] for row in preview_data]
    
    col_widths = [letter[0] / len(df.columns) - 20 for _ in df.columns]
    preview_table = Table(preview_data, colWidths=col_widths)
    preview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')])
    ]))
    elements.append(preview_table)
    
    # Add visualizations
    if charts:
        elements.append(PageBreak())
        elements.append(Paragraph("Data Visualizations", heading_style))
        for i, chart_bytes in enumerate(charts):
            img_buffer = BytesIO(chart_bytes)
            img = Image(img_buffer, width=6*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Main app
st.title("📊 Automated Report Generation System")
st.markdown("### Upload your data and generate professional PDF reports instantly")

# File upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your data file (CSV, Excel)", 
                                type=['csv', 'xlsx', 'xls'],
                                help="Upload a CSV or Excel file to generate automated reports")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
        
        # Display data preview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
        
        with col2:
            st.subheader("📈 Quick Stats")
            st.metric("Total Rows", len(df))
            st.metric("Total Columns", len(df.columns))
            st.metric("Missing Values", df.isnull().sum().sum())
        
        # Analyze data
        with st.spinner("🔍 Analyzing data..."):
            analysis = analyze_data(df)
        
        # Display analysis
        st.subheader("🔬 Data Analysis")
        
        tab1, tab2, tab3 = st.tabs(["📊 Statistics", "📉 Visualizations", "🔍 Missing Values"])
        
        with tab1:
            if analysis['numeric_columns']:
                st.write("**Numeric Columns Summary:**")
                st.dataframe(df[analysis['numeric_columns']].describe(), use_container_width=True)
            else:
                st.info("No numeric columns found in the dataset.")
        
        with tab2:
            if analysis['numeric_columns']:
                for col in analysis['numeric_columns'][:2]:
                    fig = px.histogram(df, x=col, title=f'Distribution of {col}',
                                     color_discrete_sequence=['#667eea'])
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns available for visualization.")
        
        with tab3:
            missing_df = pd.DataFrame({
                'Column': analysis['missing_values'].keys(),
                'Missing Count': analysis['missing_values'].values()
            })
            missing_df = missing_df[missing_df['Missing Count'] > 0]
            if len(missing_df) > 0:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("✨ No missing values found!")
        
        # Generate report button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Generate PDF Report", use_container_width=True):
                with st.spinner("🎨 Creating your professional report..."):
                    # Create visualizations
                    charts = create_visualizations(df, analysis['numeric_columns'])
                    
                    # Generate PDF
                    pdf_buffer = generate_pdf_report(df, analysis, charts)
                    
                    st.success("✅ Report generated successfully!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please make sure your file is properly formatted.")

else:
    # Show instructions when no file is uploaded
    st.info("👆 Upload a file to get started!")
    
    with st.expander("📖 How to use this app"):
        st.markdown("""
        1. **Upload your data file** (CSV or Excel format)
        2. **Review the data preview** and analysis
        3. **Click 'Generate PDF Report'** to create a professional report
        4. **Download your report** and use it for your needs
        
        **Supported file formats:**
        - CSV (.csv)
        - Excel (.xlsx, .xls)
        """)
    
    with st.expander("🎯 Features"):
        st.markdown("""
        - 📊 Automatic data analysis
        - 📈 Statistical summaries
        - 📉 Data visualizations
        - 📄 Professional PDF reports
        - 🎨 Modern, responsive UI
        - ⚡ Fast processing
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Automated Report Generation System</p>
    </div>
""", unsafe_allow_html=True)