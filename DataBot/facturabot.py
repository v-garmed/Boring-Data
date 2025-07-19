import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def analizar_facturas(csv_path):
    df = pd.read_csv(csv_path)
    
    # Normalizar columnas: minúsculas y sin espacios
    df.columns = df.columns.str.lower().str.strip()
    
    # Columnas requeridas
    required_cols = {
        "fecha": None,
        "cliente": None,
        "producto": None,
        "cantidad": None,
        "precio unitario": None
    }
    
    # Buscar columnas reales que coincidan con las esperadas
    for col in df.columns:
        col_norm = col.lower().strip()
        for key in required_cols:
            if key == col_norm:
                required_cols[key] = col
                break
    
    # Verificar columnas faltantes
    faltantes = [k for k,v in required_cols.items() if v is None]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el archivo: {faltantes}")
    
    # Renombrar columnas para uso interno
    df.rename(columns={v: k for k, v in required_cols.items()}, inplace=True)
    
    # Calcular columna total
    df["total"] = df["cantidad"] * df["precio unitario"]
    
    # Agrupar y calcular totales
    resumen_general = df["total"].sum()
    por_cliente = df.groupby("cliente")["total"].sum().sort_values(ascending=False)
    por_producto = df.groupby("producto")["total"].sum().sort_values(ascending=False)
    
    return df, resumen_general, por_cliente, por_producto

def generar_graficas(por_cliente, por_producto, df):
    os.makedirs("output", exist_ok=True)
    
    # Gráfica ventas por cliente
    plt.figure(figsize=(8,4))
    por_cliente.plot(kind="bar", color="skyblue")
    plt.title("Ventas por Cliente")
    plt.ylabel("Total ($)")
    plt.tight_layout()
    plt.savefig("output/ventas_por_cliente.png")
    plt.close()
    
    # Gráfica ventas por producto (valor)
    plt.figure(figsize=(8,4))
    por_producto.plot(kind="bar", color="orange")
    plt.title("Ventas por Producto (Valor)")
    plt.ylabel("Total ($)")
    plt.tight_layout()
    plt.savefig("output/ventas_por_producto.png")
    plt.close()
    
    # Gráfica cantidad total productos vendidos
    plt.figure(figsize=(10,5))
    cantidad_por_producto = df.groupby("producto")["cantidad"].sum()
    cantidad_por_producto.plot(kind="bar", color="green")
    plt.title("Cantidad Total de Productos Vendidos")
    plt.ylabel("Unidades Vendidas")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/cantidad_productos.png")
    plt.close()

def generar_pdf(df, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Facturación", ln=True, align="C")

    # Estadísticas clave
    cliente_mayor = df.groupby("cliente")["total"].sum().idxmax()
    gasto_mayor = df.groupby("cliente")["total"].sum().max()
    producto_top = df.groupby("producto")["cantidad"].sum().idxmax()
    unidades_top = df.groupby("producto")["cantidad"].sum().max()
    producto_valor_top = df.groupby("producto")["total"].sum().idxmax()
    valor_top = df.groupby("producto")["total"].sum().max()

    resumen = (
        f"Durante el periodo analizado se facturó un total de ${total:.2f} pesos. "
        f"El cliente que más compró fue '{cliente_mayor}' con un total de ${gasto_mayor:.2f}. "
        f"El producto con mayor cantidad de unidades vendidas fue '{producto_top}' con {unidades_top} unidades. "
        f"Además, el producto que generó más ingresos fue '{producto_valor_top}' con ${valor_top:.2f}."
    )

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, resumen)

    # Insertar gráficas
    if os.path.exists("output/ventas_por_cliente.png"):
        pdf.image("output/ventas_por_cliente.png", w=180)
        pdf.ln(5)
    if os.path.exists("output/ventas_por_producto.png"):
        pdf.image("output/ventas_por_producto.png", w=180)
        pdf.ln(5)
    if os.path.exists("output/cantidad_productos.png"):
        pdf.image("output/cantidad_productos.png", w=180)
        pdf.ln(5)

    # Guardar PDF
    output_path = "output/reporte_factura.pdf"
    pdf.output(output_path)

    return output_path

# Para pruebas rápidas
if __name__ == "__main__":
    archivo = "input/factura_ejemplo.csv"
    df, total, clientes, productos = analizar_facturas(archivo)
    generar_graficas(clientes, productos, df)
    pdf_path = generar_pdf(df, total)
    print(f"✅ Reporte generado: {pdf_path}")
