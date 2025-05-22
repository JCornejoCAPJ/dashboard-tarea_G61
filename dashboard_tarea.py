import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np

# --- Configuración de la Página ---
st.set_page_config(layout="wide", page_title="Análisis de Ventas - Tienda de Conveniencia")

# --- Cargar Datos ---
@st.cache_data
def cargar_datos():
    df_ventas = pd.read_csv('data.csv')
    df_ventas['Date'] = pd.to_datetime(df_ventas['Date'])
    return df_ventas

df = cargar_datos()

# --- Título Principal del Dashboard ---
st.title('Análisis Visual de Ventas de Tienda de Conveniencia')
st.write("Este dashboard presenta un análisis de las ventas y el comportamiento de los clientes.")
st.markdown("---")

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("Filtros del Dashboard")

# Filtro de Rango de Fechas
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input(
    "Rango de fechas:",
    value=(min_date, max_date), min_value=min_date, max_value=max_date, format="YYYY-MM-DD"
)

# Filtro de Sucursal (Branch) General
branch_options_all = sorted(df['Branch'].unique().tolist())
selected_branches_general = st.sidebar.multiselect(
    "Selecciona Sucursal(es):",
    options=branch_options_all, default=branch_options_all
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros Específicos por Gráfico:")

# Filtros para Distribución de Calificaciones
selected_customer_types_rating = st.sidebar.multiselect(
    "Tipo(s) de Cliente (Calificaciones):",
    options=sorted(df['Customer type'].unique().tolist()),
    default=sorted(df['Customer type'].unique().tolist())
)

# Filtros para Gasto por Tipo de Cliente y Relación Cogs/Ingreso
product_line_options_all_with_todas = ['Todas'] + sorted(df['Product line'].unique().tolist())
selected_product_line_filter = st.sidebar.selectbox(
    "Línea de Producto (Gasto Cliente / Rel. Cogs-Ingreso):",
    options=product_line_options_all_with_todas, index=0
)

# Filtro para Variables de Correlación
numerical_cols_options = ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs', 'gross income', 'Rating']
selected_numerical_cols_corr = st.sidebar.multiselect(
    "Variables para Matriz de Correlación:",
    options=numerical_cols_options,
    default=numerical_cols_options # Por defecto todas
)

# --- Preparar DataFrames filtrados (La lógica general se mantiene y se aplica a df_filtered_primary) ---
df_filtered_primary = df.copy()
# Aplicar filtro de fecha
if len(date_range) == 2:
    start_date, end_date = date_range
    start_date_dt = pd.to_datetime(start_date); end_date_dt = pd.to_datetime(end_date)
    df_filtered_primary = df_filtered_primary[(df_filtered_primary['Date'] >= start_date_dt) & (df_filtered_primary['Date'] <= end_date_dt)]
else:
    df_filtered_primary = pd.DataFrame(columns=df.columns)

# Aplicar filtro de sucursal general
title_desc_branch_general = "Todas las Sucursales"
if selected_branches_general:
    if len(selected_branches_general) != len(branch_options_all):
        df_filtered_primary = df_filtered_primary[df_filtered_primary['Branch'].isin(selected_branches_general)]
        title_desc_branch_general = f"Suc: {', '.join(selected_branches_general)}"
elif not df_filtered_primary.empty:
    df_filtered_primary = pd.DataFrame(columns=df.columns)


# --- DataFrames y Títulos para cada Gráfico (se actualizan para usar df_filtered_primary) ---
# Gráfico 1: Evolución de Ventas
df_evol_ventas = df_filtered_primary.copy()
title_evol_ventas = f"({title_desc_branch_general})" if not df_evol_ventas.empty else "(Sin datos para filtros)"

# Gráfico 2: Ingresos (ahora gross income)por Línea de Producto
# df_income_by_product = df_filtered_primary.copy()
# title_income_by_product = f"({title_desc_branch_general})" if not df_income_by_product.empty else "(Sin datos para filtros)"
df_gross_income_by_product = df_filtered_primary.copy() # Usamos un nuevo nombre de DataFrame para claridad
title_gross_income_by_product = f"({title_desc_branch_general})" if not df_gross_income_by_product.empty else "(Sin datos para filtros)"


# Gráfico 3: Distribución de Calificaciones
df_rating_distribution = df_filtered_primary.copy()
rating_filter_desc_parts = [title_desc_branch_general] if title_desc_branch_general != "Todas las Sucursales" else []
if selected_customer_types_rating:
    if len(selected_customer_types_rating) != len(df['Customer type'].unique()):
        df_rating_distribution = df_rating_distribution[df_rating_distribution['Customer type'].isin(selected_customer_types_rating)]
        rating_filter_desc_parts.append(f"Tipo Cli: {', '.join(selected_customer_types_rating)}")
elif not df_rating_distribution.empty:
    df_rating_distribution = pd.DataFrame(columns=df.columns)
title_suffix_rating_final = " | ".join(rating_filter_desc_parts) if rating_filter_desc_parts else "General"
if df_rating_distribution.empty : title_suffix_rating_final = "(Sin datos para filtros)"

# Gráfico 4: Gasto por Tipo de Cliente
df_customer_spending = df_filtered_primary.copy()
title_parts_spending = [title_desc_branch_general] if title_desc_branch_general != "Todas las Sucursales" else []
if selected_product_line_filter != 'Todas':
    df_customer_spending = df_customer_spending[df_customer_spending['Product line'] == selected_product_line_filter]
    title_parts_spending.append(f"Línea Prod: {selected_product_line_filter}")
title_suffix_spending = " | ".join(title_parts_spending) if title_parts_spending else "General"
if df_customer_spending.empty : title_suffix_spending = "(Sin datos para filtros)"

# Gráfico 5: Relación Cogs vs Gross Income
df_cogs_income = df_filtered_primary.copy()
title_suffix_cogs_income_parts = [title_desc_branch_general] if title_desc_branch_general != "Todas las Sucursales" else []
if selected_product_line_filter != 'Todas':
    df_cogs_income = df_cogs_income[df_cogs_income['Product line'] == selected_product_line_filter]
    title_suffix_cogs_income_parts.append(f"Línea Prod: {selected_product_line_filter}")
title_suffix_cogs_income = " | ".join(title_suffix_cogs_income_parts) if title_suffix_cogs_income_parts else "General"
if df_cogs_income.empty : title_suffix_cogs_income = "(Sin datos para filtros)"

# Gráfico 6: Métodos de Pago Preferidos
df_payment_methods = df_filtered_primary.copy()
title_suffix_payment = title_desc_branch_general
if df_payment_methods.empty : title_suffix_payment = "(Sin datos para filtros)"

# Gráfico 7: Matriz de Correlación
df_correlation = df_filtered_primary.copy() # Se basa en los filtros generales de fecha y sucursal
title_suffix_correlation = title_desc_branch_general
if df_correlation.empty : title_suffix_correlation = "(Sin datos para filtros)"


# --- CUERPO PRINCIPAL DEL DASHBOARD ---
st.header("Análisis Exploratorio")
# --- Gráfico 1: Evolución de las Ventas Totales ---

st.subheader("Evolución de las Ventas Totales")
if not df_evol_ventas.empty:
    daily_sales = df_evol_ventas.groupby(df_evol_ventas['Date'].dt.date)['Total'].sum().reset_index()
    daily_sales['Date'] = pd.to_datetime(daily_sales['Date'])
    daily_sales = daily_sales.sort_values(by='Date')
    fig1, ax1 = plt.subplots(figsize=(18, 7))
    sns.lineplot(data=daily_sales, x='Date', y='Total', marker='o', ax=ax1)
    ax1.set_title(f'Evolución de Ventas Totales {title_evol_ventas}', fontsize=16)
    ax1.set_xlabel('Fecha', fontsize=12); ax1.set_ylabel('Ventas Totales', fontsize=12)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right'); fig1.tight_layout(); ax1.grid(True)
    st.pyplot(fig1)
else:
    st.write(f"No hay datos para los filtros seleccionados en 'Evolución de Ventas'.")
st.markdown("---")

# --- Gráfico 2: Ingreso BRUTO por Línea de Producto ---
st.subheader("Ingreso Bruto por Línea de Producto") 
if not df_gross_income_by_product.empty:
    # Agrupar por 'Product line' y sumar el 'gross income'.
    income_by_product_line_agg = df_gross_income_by_product.groupby('Product line')['gross income'].sum().sort_values(ascending=False).reset_index()

    fig2, ax2 = plt.subplots(figsize=(12, 7))
    # Usar 'gross income' para el eje x del barplot
    sns.barplot(data=income_by_product_line_agg, x='gross income', y='Product line', hue='Product line', palette='viridis', orient='h', legend=False, ax=ax2)
    
    ax2.set_title(f'Ingreso BRUTO por Línea de Producto {title_gross_income_by_product}', fontsize=16) # Título del gráfico actualizado
    ax2.set_xlabel('Ingreso Bruto (gross income)', fontsize=12) # Etiqueta del eje X actualizada
    ax2.set_ylabel('Línea de Producto', fontsize=12)
    fig2.tight_layout(); ax2.grid(axis='x', linestyle='--', alpha=0.7)
    st.pyplot(fig2)
else:
    st.write(f"No hay datos para los filtros seleccionados para Ingreso Bruto por Línea de Producto.")
st.markdown("---")

# --- Gráfico 3: Distribución de la Calificación de Clientes ---
st.subheader("Distribución de la Calificación de Clientes")
if not df_rating_distribution.empty:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.histplot(df_rating_distribution['Rating'], kde=True, bins=10, color='skyblue', ax=ax3)
    mean_rating = df_rating_distribution['Rating'].mean()
    median_rating = df_rating_distribution['Rating'].median()
    ax3.axvline(mean_rating, color='red', linestyle='dashed', linewidth=1.5, label=f'Media: {mean_rating:.2f}')
    ax3.axvline(median_rating, color='green', linestyle='dashed', linewidth=1.5, label=f'Mediana: {median_rating:.2f}')
    ax3.set_title(f'Distribución de Calificación de Clientes ({title_suffix_rating_final})', fontsize=16)
    ax3.set_xlabel('Calificación (Rating)', fontsize=12); ax3.set_ylabel('Frecuencia', fontsize=12)
    ax3.legend(); ax3.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig3)
else:
    st.write(f"No hay datos de calificación para filtros: {title_suffix_rating_final}.")
st.markdown("---")

# --- Gráfico 4: Comparación del Gasto por Tipo de Cliente ---
st.subheader("Comparación del Gasto por Tipo de Cliente")
if not df_customer_spending.empty:
    fig4, ax4 = plt.subplots(figsize=(8, 7))
    sns.boxplot(data=df_customer_spending, x='Customer type', y='Total', hue='Customer type', palette='pastel', legend=False, ax=ax4)
    ax4.set_title(f'Comparación del Gasto Total por Tipo de Cliente ({title_suffix_spending})', fontsize=16)
    ax4.set_xlabel('Tipo de Cliente', fontsize=12); ax4.set_ylabel('Gasto Total (Total)', fontsize=12)
    ax4.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig4)
else:
    st.write(f"No hay datos de gasto por tipo de cliente para filtros: {title_suffix_spending}.")
st.markdown("---")

# --- Gráfico 5: Relación entre Costo (cogs) y Ganancia Bruta (gross income) ---
st.subheader("Relación entre Costo y Ganancia Bruta")
if not df_cogs_income.empty:
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_cogs_income, x='cogs', y='gross income', alpha=0.5, ax=ax5)
    correlation_cogs_income = df_cogs_income['cogs'].corr(df_cogs_income['gross income'])
    ax5.set_title(f'Relación Costo vs. Ganancia Bruta ({title_suffix_cogs_income})\nCorrelación: {correlation_cogs_income:.2f}', fontsize=14)
    ax5.set_xlabel('Costo de Bienes Vendidos (cogs)', fontsize=12); ax5.set_ylabel('Ganancia Bruta (gross income)', fontsize=12)
    ax5.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig5)
else:
    st.write(f"No hay datos para analizar la relación Costo vs. Ganancia Bruta para filtros: {title_suffix_cogs_income}.")
st.markdown("---")

# --- Gráfico 6: Métodos de Pago Preferidos ---
st.subheader("Métodos de Pago Preferidos")
if not df_payment_methods.empty:
    payment_counts = df_payment_methods['Payment'].value_counts().reset_index()
    payment_counts.columns = ['Payment', 'Count']
    fig6, ax6 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=payment_counts, x='Count', y='Payment', hue='Payment', palette='muted', orient='h', legend=False, ax=ax6)
    ax6.set_title(f'Métodos de Pago Más Frecuentes ({title_suffix_payment})', fontsize=16)
    ax6.set_xlabel('Número de Transacciones', fontsize=12); ax6.set_ylabel('Método de Pago', fontsize=12)
    fig6.tight_layout(); ax6.grid(axis='x', linestyle='--', alpha=0.7)
    st.pyplot(fig6)
else:
    st.write(f"No hay datos de métodos de pago para los filtros seleccionados: {title_suffix_payment}.")
st.markdown("---")

# --- Gráfico 7: Análisis de Correlación Numérica ---
st.subheader("Análisis de Correlación Numérica")
if not df_correlation.empty and selected_numerical_cols_corr:
    df_numerical_selected = df_correlation[selected_numerical_cols_corr]
    if len(df_numerical_selected.columns) < 2: 
        st.write("Por favor, selecciona al menos dos variables para la matriz de correlación.")
    else:
        correlation_matrix = df_numerical_selected.corr()
        fig7, ax7 = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax7)
        ax7.set_title(f'Mapa de Calor de Correlación ({title_suffix_correlation})', fontsize=16)
        st.pyplot(fig7)
elif not selected_numerical_cols_corr:
    st.write("Por favor, selecciona al menos una variable para la matriz de correlación en la barra lateral.")
else:
    st.write(f"No hay datos para generar la matriz de correlación con los filtros actuales: {title_suffix_correlation}.")

# Pie de página
st.markdown("---")
st.caption("Tarea Grupal - Visualización de Datos en Python")