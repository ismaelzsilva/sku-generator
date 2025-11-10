import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Kave SKUs Generator")

model_variant = ""

model_variant = st.text_input("Model Variant").upper()


fabric = False
material = False

if model_variant != "":
    st.text("¿Con que se va a poder personalizar?")
    fabric = st.checkbox("Fabric")
    material = st.checkbox("Material")

if fabric or material:
    st.text("¿Que afectan al precio?")

if fabric and st.checkbox("Fabric "):
    fabric_changes_price = True
else:
    fabric_changes_price = False

if material and st.checkbox("Material "):
    material_changes_price = True
else:
    material_changes_price = False

fabric_tiers = []

if fabric_changes_price:
    fabric_tiers = [tier.strip() for tier in st.text_input(
        "Tiers, separated by commas. Ex: 'A,B,C'").upper().split(",") if tier.strip()]
    for tier in fabric_tiers:
        if not tier.isalpha() or len(tier) != 1:
            st.error(f"Error en: {tier}. Solo se aceptan letras individuales.")
            fabric_tiers.remove(tier)
    fabric_tiers = set(fabric_tiers)

material = []

if material_changes_price:
    material = [m.strip() for m in st.text_input(
        "Materials, separated by commas. Ex: 'MTK001,MTK002,MTK003'").upper().split(",") if m.strip()]

st.session_state["materials_options"] = material if material_changes_price else []

skus = []

if fabric and material:
    if fabric_changes_price and material_changes_price:
        skus = [f"{model_variant}{m}PER{f}" for m in material for f in fabric_tiers]
    elif fabric_changes_price:
        skus = [f"{model_variant}PER{f}" for f in fabric_tiers]
    elif material_changes_price:
        skus = [f"{model_variant}{m}" for m in material]
elif fabric:
    skus = [f"{model_variant}PER{f}" for f in fabric_tiers]
elif material:
    skus = [f"{model_variant}{m}" for m in material]

stock_records = []

if len(skus) >= 1 and st.checkbox("Añadir productos de stock"):

    # Inicializar contador de filas
    if "stock_rows" not in st.session_state:
        st.session_state.stock_rows = 1

    col_add, col_del = st.columns([1, 1])
    if col_add.button("➕ Añadir producto de stock"):
        st.session_state.stock_rows += 1
    if col_del.button("➖ Eliminar último") and st.session_state.stock_rows > 1:
        st.session_state.stock_rows -= 1

    st.session_state.fabric_customizable = fabric
    st.session_state.material_customizable = material

    for i in range(st.session_state.stock_rows):
        fabric_customizable = st.session_state.get(
            "fabric_customizable", False)
        material_customizable = st.session_state.get(
            "material_customizable", False)

        st.markdown(f"Producto de stock {i+1}")

        field_defs = []
        if material_customizable:
            field_defs += ["material_code", "material_mtk"]
        if fabric_customizable:
            field_defs += ["fabric_code", "fabric_mtk"]

        cols = st.columns(len(field_defs)) if field_defs else []

        row_values = {}
        for idx, field_name in enumerate(field_defs):
            if field_name == "material_mtk":
                opciones = [""] + st.session_state.get("materials_options", [])
                val = cols[idx].selectbox(
                    "MTK", opciones, key=f"{field_name}_{i}")
            elif field_name == "fabric_mtk":
                val = cols[idx].text_input(
                    "MTK", key=f"{field_name}_{i}").upper()
            else:
                val = cols[idx].text_input(
                    "Code", key=f"{field_name}_{i}").upper()
            row_values[field_name] = val

        if all(row_values.values()):
            stock_records.append(row_values)

    if stock_records:
        stock_df = pd.DataFrame(stock_records)
        # append stock products to skus
        for _, row in stock_df.iterrows():
            sku_parts = [model_variant]
            if material_changes_price and row["material_code"]:
                sku_parts.append(row["material_code"])
            if fabric_changes_price and row["fabric_code"]:
                sku_parts.append(f"PER{row['fabric_code']}")
            skus.append("".join(sku_parts))

        st.markdown("---")

show_skus = False

if fabric_changes_price and len(fabric_tiers) > 0 and material_changes_price and len(material) > 0:
    show_skus = True
elif fabric_changes_price and len(fabric_tiers) > 0 and not material_changes_price:
    show_skus = True
elif material_changes_price and len(material) > 0 and not fabric_changes_price:
    show_skus = True

if show_skus:
    st.subheader("SKUs generados")
    for sku in skus:
        st.text(sku)


def generate_xlsx(skus, model_variant, collection):

    data = {
        "sku": skus,
        "model_variant": [model_variant] * len(skus),
        "collection": [collection] * len(skus),
        "fabric_mtk": ["" for _ in skus],
        "material_mtk": ["" for _ in skus],
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='SKUs')
    return output.getvalue()


collection = ""

if show_skus:
    collection = st.text_input("Collection Name", placeholder="Ej: blok")

if show_skus and collection != "":
    st.download_button(
        label="Descargar SKUs",
        data=generate_xlsx(skus, model_variant, collection),
        file_name="kave_skus.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
