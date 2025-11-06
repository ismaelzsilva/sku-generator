import streamlit as st

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
    fabric_tiers = [tier.strip() for tier in st.text_input("Tiers, separated by commas. Ex: 'A,B,C'").upper().split(",") if tier.strip()]
    for tier in fabric_tiers:
        if not tier.isalpha() or len(tier) != 1:
            st.error(f"Error en: {tier}. Solo se aceptan letras individuales.")
            fabric_tiers.remove(tier)
    fabric_tiers = set(fabric_tiers)

material = []

if material_changes_price:
    material = [m.strip() for m in st.text_input("Materials, separated by commas. Ex: 'MTK001,MTK002,MTK003'").upper().split(",") if m.strip()]

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