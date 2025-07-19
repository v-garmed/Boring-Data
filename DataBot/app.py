import streamlit as st
import os
from facturabot import analizar_facturas, generar_graficas, generar_pdf

st.set_page_config(page_title="FacturaBot", layout="centered")
st.title("📄 FacturaBot – Generador de Reportes de Facturación")
st.write("Sube tu archivo CSV de facturación y genera un reporte en PDF con estadísticas y gráficas.")

archivo = st.file_uploader("📤 Sube tu archivo CSV", type=["csv"])

if archivo:
    input_dir = "input"
    os.makedirs(input_dir, exist_ok=True)
    input_path = os.path.join(input_dir, "archivo_temporal.csv")

    with open(input_path, "wb") as f:
        f.write(archivo.read())

    try:
        df, total, por_cliente, por_producto = analizar_facturas(input_path)
        generar_graficas(por_cliente, por_producto, df)
        pdf_path = generar_pdf(df, total)

        st.success(f"✅ Total facturado: ${total:.2f}")
        st.image("output/ventas_por_cliente.png", caption="Ventas por Cliente")
        st.image("output/ventas_por_producto.png", caption="Ventas por Producto (Valor)")
        st.image("output/cantidad_productos.png", caption="Cantidad Total de Productos Vendidos")

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Descargar Reporte PDF",
                data=f,
                file_name="reporte_factura.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
