import streamlit as st
import pandas as pd
import openpyxl
import numpy as np

def procesar_excel(file):
    try:
        df = pd.read_excel(file)
        servicios = []
        
        # Obtener lista de perfiles (columnas)
        perfiles = [col for col in df.columns if col not in ['Unnamed: 0', 'ITEM', 'SERVICIOS']]
        
        # Procesar cada servicio
        for _, row in df.iterrows():
            servicio = row['SERVICIOS']
            if pd.isna(servicio):
                continue
                
            perfiles_data = []
            total_horas = 0
            total_costo = 0
            
            # Procesar cada perfil
            for perfil in perfiles:
                valor = row[perfil]
                horas = convertir_tiempo(valor)
                costo_hora = obtener_costo_hora(perfil)
                costo = horas * costo_hora
                
                if horas > 0:
                    perfiles_data.append({
                        'perfil': perfil,
                        'horas': horas,
                        'costo_hora': costo_hora,
                        'costo': costo
                    })
                    
                total_horas += horas
                total_costo += costo
            
            if perfiles_data:
                servicios.append({
                    'servicio': servicio,
                    'perfiles': perfiles_data,
                    'total_horas': total_horas,
                    'total_costo': total_costo
                })
                
        return servicios
    except Exception as e:
        st.error(f"Error procesando Excel: {str(e)}")
        return None

def convertir_tiempo(valor):
    if pd.isna(valor):
        return 0
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str) and '/' in valor:
        try:
            nums = [float(x) for x in valor.split('/')]
            return sum(nums) / len(nums)
        except:
            return 0
    return 0

def obtener_costo_hora(perfil):
    # Diccionario de costos por perfil
    costos = {
        'Director creativo': 50,
        'Ejecutivo de producción': 35,
        # ... resto de perfiles y costos
    }
    return costos.get(perfil, 25)  # 25 como valor por defecto

def main():
    st.set_page_config(page_title="Calculadora de Tiempos", layout="wide")
    
    st.title("Calculadora de Tiempos y Costos")
    
    uploaded_file = st.file_uploader("Selecciona el archivo Excel", type=['xlsx'])
    
    if uploaded_file:
        servicios = procesar_excel(uploaded_file)
        
        if servicios:
            # 1. Tabla Resumen de Todos los Servicios
            st.header("Resumen General de Servicios")
            resumen_servicios = []
            for servicio in servicios:
                resumen_servicios.append({
                    'Servicio': servicio['servicio'],
                    'Cantidad de Perfiles': len(servicio['perfiles']),
                    'Total Horas': servicio['total_horas'],
                    'Costo Base': servicio['total_costo'],
                    'Costo Final': servicio['total_costo'] * 1.15
                })
            
            df_resumen = pd.DataFrame(resumen_servicios)
            st.dataframe(
                df_resumen,
                column_config={
                    'Servicio': st.column_config.TextColumn('Servicio'),
                    'Cantidad de Perfiles': st.column_config.NumberColumn('N° Perfiles'),
                    'Total Horas': st.column_config.NumberColumn('Total Horas', format="%.2f"),
                    'Costo Base': st.column_config.NumberColumn('Costo Base', format="S/ %.2f"),
                    'Costo Final': st.column_config.NumberColumn('Costo Final (15%)', format="S/ %.2f")
                },
                hide_index=True,
                use_container_width=True
            )

            # 2. Detalle por Servicio
            st.header("Detalle por Servicio")
            servicio_seleccionado = st.selectbox(
                "Selecciona un servicio para ver detalles",
                options=[s['servicio'] for s in servicios]
            )
            
            for servicio in servicios:
                if servicio['servicio'] == servicio_seleccionado:
                    # Información básica
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Perfiles", len(servicio['perfiles']))
                    with col2:
                        st.metric("Total Horas", f"{servicio['total_horas']:.2f}")
                    with col3:
                        st.metric("Costo Final", f"S/ {servicio['total_costo'] * 1.15:.2f}")
                    
                    # Tabla detallada de perfiles
                    st.subheader("Desglose por Perfil")
                    df_perfiles = pd.DataFrame(servicio['perfiles'])
                    
                    # Ordenar por horas descendente
                    df_perfiles = df_perfiles.sort_values('horas', ascending=False)
                    
                    st.dataframe(
                        df_perfiles,
                        column_config={
                            'perfil': st.column_config.TextColumn('Perfil'),
                            'horas': st.column_config.NumberColumn('Horas', format="%.2f"),
                            'costo_hora': st.column_config.NumberColumn('Costo/Hora', format="S/ %.2f"),
                            'costo': st.column_config.NumberColumn('Costo Total', format="S/ %.2f")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # 3. Resumen de Costos
                    st.subheader("Resumen de Costos")
                    costo_base = servicio['total_costo']
                    margen = costo_base * 0.15
                    costo_final = costo_base + margen
                    
                    df_costos = pd.DataFrame([
                        {'Concepto': 'Costo Base', 'Monto': costo_base},
                        {'Concepto': 'Margen (15%)', 'Monto': margen},
                        {'Concepto': 'Costo Final', 'Monto': costo_final}
                    ])
                    
                    st.dataframe(
                        df_costos,
                        column_config={
                            'Concepto': st.column_config.TextColumn('Concepto'),
                            'Monto': st.column_config.NumberColumn('Monto', format="S/ %.2f")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    break

            # 4. Totales del Proyecto
            st.header("Totales del Proyecto")
            total_horas_proyecto = sum(s['total_horas'] for s in servicios)
            total_costo_base = sum(s['total_costo'] for s in servicios)
            total_costo_final = total_costo_base * 1.15
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Horas Proyecto", f"{total_horas_proyecto:.2f}")
            with col2:
                st.metric("Costo Base Proyecto", f"S/ {total_costo_base:.2f}")
            with col3:
                st.metric("Costo Final Proyecto", f"S/ {total_costo_final:.2f}")

if __name__ == "__main__":
    main()