ES = {
    "knitwear": "prendas de punto", "tops": "tops", "dresses": "vestidos",
    "bottoms": "faldas y pantalones", "outerwear": "abrigos y chaquetas",
    "white": "blanco", "black": "negro", "grey": "gris", "beige": "beige",
    "brown": "marrón", "cream": "crema", "light pink": "rosa claro",
    "navy": "azul marino", "orange": "naranja", "red": "rojo", "yellow": "amarillo",
    "striped": "rayas", "floral": "flores", "animal print": "animal print",
    "polka dots": "lunares", "checked": "cuadros",
}
GARMENTS = ["knitwear", "tops", "dresses", "bottoms", "outerwear"]

def gaps(own_df, comp_df):
    rows = []
    for g in GARMENTS:
        po = own_df["labels_manual"].str.split("|").apply(lambda x: g in x).mean()
        pc = comp_df["labels_manual"].str.split("|").apply(lambda x: g in x).mean()
        rows.append((abs(po - pc), "prenda", g, po, pc))
    for col, kind in [("color_upper", "color"), ("pattern_final", "patrón")]:
        so = own_df[col].value_counts(normalize=True)
        sc = comp_df[col].value_counts(normalize=True)
        for v in set(so.index) | set(sc.index):
            if v != "solid / other":
                rows.append((abs(so.get(v, 0) - sc.get(v, 0)), kind, v, so.get(v, 0), sc.get(v, 0)))
    return sorted(rows, reverse=True)

def sentence(kind, name, po, pc, own, comp):
    x = ES.get(name, name)
    label = {"prenda": x, "color": f"el color {x}", "patrón": f"el patrón de {x}"}[kind]
    if po > pc:
        return (f"{own} usa más {label} que {comp}: {po:.0%} frente a {pc:.0%} de las fotos. "
                f"Es un rasgo propio: mantenlo y comunícalo.")
    return (f"{comp} usa más {label} que {own}: {pc:.0%} frente a {po:.0%}. "
            f"Oportunidad: probar {label} en la próxima colección.")

def top_insights(df, own, comp, own_name, comp_name, n=5):
    own_df, comp_df = df[df["brand"] == own], df[df["brand"] == comp]
    return [sentence(k, nm, po, pc, own_name, comp_name)
            for _, k, nm, po, pc in gaps(own_df, comp_df)[:n]]