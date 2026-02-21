"""
╔═══════════════════════════════════════════════════╗
║   MAISON ÉLITE  ·  Ontology Explorer              ║
║   Semantic Web · Fine Dining Restaurant Domain    ║
╚═══════════════════════════════════════════════════╝

Requirements : Python 3.8+ (tkinter ships with Python — no pip needed)
Run          : python ontology_explorer.py
OWL file     : place maison_elite.owl in the same folder,
               OR the app will open a file picker.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM  ·  Obsidian & Amber — Luxury Noir
# ─────────────────────────────────────────────────────────────────────────────
BG        = "#0A0A0B"
SURFACE   = "#111113"
CARD      = "#18181B"
CARD_HOV  = "#1F1F23"
BORDER    = "#242428"
GOLD      = "#C9A96E"
GOLD_DIM  = "#7A6240"
AMBER     = "#E8B84B"
CREAM     = "#EDE8DF"
MUTED     = "#5E5C6A"
SAGE      = "#608A72"
ROSE      = "#8A5050"
SELECTED  = "#1E1B14"

FONT_TITLE  = ("Georgia",     22, "bold")
FONT_H2     = ("Georgia",     11, "bold")
FONT_BODY   = ("Georgia",      9)
FONT_CODE   = ("Courier New",  9)
FONT_BADGE  = ("Courier New",  8)
FONT_MICRO  = ("Courier New",  7)

NS     = "http://maison-elite.org/ontology#"
OWL_NS = "http://www.w3.org/2002/07/owl#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDS_NS = "http://www.w3.org/2000/01/rdf-schema#"

CLASS_ICONS = {
    "Restaurant": "🏛", "HeadChef": "👑", "SousChef": "🔪",
    "PastryChef": "🍮", "Chef": "👨‍🍳", "VIPCustomer": "◆",
    "RegularCustomer": "◇", "Customer": "○",
    "Starter": "○", "MainCourse": "●", "Dessert": "♦",
    "Dish": "▸", "DegustationMenu": "◈", "ALaCarteMenu": "≡",
    "SeasonalMenu": "✦", "Menu": "≡",
    "Reservation": "📅", "Ingredient": "◉", "Award": "★",
}

# ─────────────────────────────────────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────────────────────────────────────
def local(uri):
    if not uri:
        return ""
    return uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]

def parse_owl(path):
    tree = ET.parse(path)
    root = tree.getroot()
    classes     = {}
    sub_classes = defaultdict(list)
    obj_props   = {}
    data_props  = {}
    individuals = {}

    for c in root.findall(f"{{{OWL_NS}}}Class"):
        uri = c.get(f"{{{RDF_NS}}}about")
        if uri:
            n = local(uri)
            classes[n] = {"uri": uri, "subClassOf": []}
            for s in c.findall(f"{{{RDS_NS}}}subClassOf"):
                p = s.get(f"{{{RDF_NS}}}resource")
                if p:
                    classes[n]["subClassOf"].append(local(p))
                    sub_classes[local(p)].append(n)

    for p in root.findall(f"{{{OWL_NS}}}ObjectProperty"):
        uri = p.get(f"{{{RDF_NS}}}about")
        if uri:
            d = p.find(f"{{{RDS_NS}}}domain")
            r = p.find(f"{{{RDS_NS}}}range")
            obj_props[local(uri)] = {
                "domain": local(d.get(f"{{{RDF_NS}}}resource")) if d is not None else "—",
                "range":  local(r.get(f"{{{RDF_NS}}}resource")) if r is not None else "—",
            }

    for p in root.findall(f"{{{OWL_NS}}}DatatypeProperty"):
        uri = p.get(f"{{{RDF_NS}}}about")
        if uri:
            doms = [local(d.get(f"{{{RDF_NS}}}resource"))
                    for d in p.findall(f"{{{RDS_NS}}}domain")
                    if d.get(f"{{{RDF_NS}}}resource")]
            rng = p.find(f"{{{RDS_NS}}}range")
            data_props[local(uri)] = {
                "domains": doms,
                "range": local(rng.get(f"{{{RDF_NS}}}resource")) if rng is not None else "—",
            }

    for ind in root.findall(f"{{{OWL_NS}}}NamedIndividual"):
        uri = ind.get(f"{{{RDF_NS}}}about")
        if not uri:
            continue
        name       = local(uri)
        types      = []
        assertions = []

        for t in ind.findall(f"{{{RDF_NS}}}type"):
            r = t.get(f"{{{RDF_NS}}}resource")
            if r and OWL_NS not in r:
                types.append(local(r))

        for child in ind:
            tag = child.tag
            if tag.startswith(f"{{{NS}}}"):
                prop = local(tag)
                ref  = child.get(f"{{{RDF_NS}}}resource")
                val  = local(ref) if ref else (child.text or "").strip()
                if val:
                    assertions.append((prop, val))

        individuals[name] = {
            "uri": uri, "types": types, "assertions": assertions,
        }

    return classes, sub_classes, obj_props, data_props, individuals


def dominant_type(info, priority):
    for p in priority:
        if p in info["types"]:
            return p
    return info["types"][0] if info["types"] else "Other"


def group_individuals(individuals):
    priority = [
        "Restaurant", "HeadChef", "SousChef", "PastryChef",
        "VIPCustomer", "RegularCustomer",
        "Starter", "MainCourse", "Dessert",
        "DegustationMenu", "ALaCarteMenu", "SeasonalMenu",
        "Reservation", "Ingredient", "Award",
    ]
    tab_map = {
        "Restaurant": "Restaurant",
        "HeadChef": "Chefs", "SousChef": "Chefs", "PastryChef": "Chefs",
        "VIPCustomer": "Customers", "RegularCustomer": "Customers",
        "Starter": "Dishes", "MainCourse": "Dishes", "Dessert": "Dishes",
        "DegustationMenu": "Menus", "ALaCarteMenu": "Menus", "SeasonalMenu": "Menus",
        "Reservation": "Reservations",
        "Ingredient": "Ingredients",
        "Award": "Awards",
    }
    groups = defaultdict(list)
    for name, info in individuals.items():
        dt  = dominant_type(info, priority)
        tab = tab_map.get(dt, "Other")
        groups[tab].append(name)
    for k in groups:
        groups[k].sort(key=lambda x: (
            individuals[x]["types"][0] if individuals[x]["types"] else "",
            next((v for p, v in individuals[x]["assertions"] if p == "name"), x)
        ))
    return groups

# ─────────────────────────────────────────────────────────────────────────────
# WIDGET HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def make_scrollable(parent, bg=BG):
    outer  = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
    sb     = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=bg)
    win   = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _resize(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(win, width=e.width)

    canvas.bind("<Configure>", _resize)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _scroll(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    for w in (canvas, inner):
        w.bind("<MouseWheel>", _scroll)
        w.bind("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        w.bind("<Button-5>",   lambda e: canvas.yview_scroll(1, "units"))

    return outer, inner, canvas


def star_str(r):
    try:
        v = float(r)
    except:
        return ""
    full  = int(v)
    frac  = v - full
    half  = 1 if frac >= 0.25 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty + f"  {v:.1f}"


def add_chip(parent, text, fg=GOLD, bg=CARD):
    f = tk.Frame(parent, bg=bg, padx=7, pady=3)
    f.pack(side="left", padx=(0, 5))
    tk.Label(f, text=text, font=FONT_BADGE, bg=bg, fg=fg).pack()
    return f


def divider(parent, color=BORDER, pady=(8, 0)):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=pady)


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    TABS = ["Restaurant", "Dishes", "Chefs", "Menus",
            "Customers", "Reservations", "Ingredients",
            "Awards", "Schema", "Query"]

    def __init__(self, owl_path):
        super().__init__()
        self.owl_path = owl_path
        (self.classes, self.sub_classes,
         self.obj_props, self.data_props,
         self.individuals) = parse_owl(owl_path)
        self.groups   = group_individuals(self.individuals)
        self.sel_item = None
        self.sel_tab  = tk.StringVar(value="")
        self._list_rows = {}

        self.title("Maison Élite · Ontology Explorer")
        self.configure(bg=BG)
        self.geometry("1180x760")
        self.minsize(960, 600)

        self._configure_ttk()
        self._build_skeleton()
        self._switch_tab("Restaurant")

    def _configure_ttk(self):
        s = ttk.Style(self)
        try:    s.theme_use("clam")
        except: pass
        s.configure("Vertical.TScrollbar",
                    troughcolor=SURFACE, background=BORDER,
                    arrowcolor=MUTED, bordercolor=SURFACE,
                    darkcolor=SURFACE, lightcolor=SURFACE, relief="flat")

    def _build_skeleton(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        logo = tk.Frame(hdr, bg=SURFACE)
        logo.pack(side="left", padx=20, fill="y")
        tk.Label(logo, text="◆", font=("Georgia", 16), bg=SURFACE, fg=GOLD
                 ).pack(side="left", pady=16)
        tk.Label(logo, text="  MAISON ÉLITE", font=("Georgia", 13, "bold"),
                 bg=SURFACE, fg=CREAM).pack(side="left")
        tk.Label(logo, text="  ·  Ontology Explorer", font=("Georgia", 9),
                 bg=SURFACE, fg=MUTED).pack(side="left")

        stat_f = tk.Frame(hdr, bg=SURFACE)
        stat_f.pack(side="right", padx=20, fill="y")
        for txt, val in [("instances", len(self.individuals)),
                          ("classes", len(self.classes)),
                          ("properties", len(self.obj_props)+len(self.data_props))]:
            v = tk.Frame(stat_f, bg=SURFACE)
            v.pack(side="left", padx=12, pady=14)
            tk.Label(v, text=str(val), font=("Georgia", 13, "bold"),
                     bg=SURFACE, fg=GOLD).pack()
            tk.Label(v, text=txt, font=FONT_MICRO, bg=SURFACE, fg=MUTED).pack()

        tk.Frame(self, bg=GOLD_DIM, height=1).pack(fill="x")

        # Tab bar
        self._tabbar = tk.Frame(self, bg=SURFACE, height=40)
        self._tabbar.pack(fill="x")
        self._tabbar.pack_propagate(False)
        self._tab_lbl = {}
        for t in self.TABS:
            l = tk.Label(self._tabbar, text=t.upper(), font=FONT_BADGE,
                         bg=SURFACE, fg=MUTED, padx=14, pady=11, cursor="hand2")
            l.pack(side="left")
            l.bind("<Button-1>", lambda e, tab=t: self._switch_tab(tab))
            l.bind("<Enter>",    lambda e, b=l, tab=t:
                   b.configure(fg=CREAM) if self.sel_tab.get() != tab else None)
            l.bind("<Leave>",    lambda e, b=l, tab=t:
                   b.configure(fg=GOLD if self.sel_tab.get() == tab else MUTED))
            self._tab_lbl[t] = l

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self._sidebar = tk.Frame(body, bg=SURFACE, width=232)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")
        self._main = tk.Frame(body, bg=BG)
        self._main.pack(side="left", fill="both", expand=True)

    # ── Tab switching ─────────────────────────────────────────────────────
    def _switch_tab(self, tab):
        prev = self.sel_tab.get()
        if prev in self._tab_lbl:
            self._tab_lbl[prev].configure(fg=MUTED)
        self.sel_tab.set(tab)
        if tab in self._tab_lbl:
            self._tab_lbl[tab].configure(fg=GOLD)
        self.sel_item = None
        self._list_rows = {}
        for w in self._sidebar.winfo_children(): w.destroy()
        for w in self._main.winfo_children():    w.destroy()

        if tab in ("Restaurant", "Dishes", "Chefs", "Menus",
                   "Customers", "Reservations", "Ingredients", "Awards"):
            self._view_entity(tab)
        elif tab == "Schema":
            self._view_schema(tab)
        elif tab == "Query":
            self._view_query(tab)

    # ─────────────────────────────────────────────────────────────────────
    # ENTITY LIST + DETAIL
    # ─────────────────────────────────────────────────────────────────────
    def _view_entity(self, tab):
        items = self.groups.get(tab, [])

        hf = tk.Frame(self._sidebar, bg=SURFACE)
        hf.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(hf, text=tab.upper(), font=FONT_BADGE,
                 bg=SURFACE, fg=GOLD).pack(side="left")
        tk.Label(hf, text=f"  {len(items)}", font=FONT_CODE,
                 bg=SURFACE, fg=MUTED).pack(side="left")
        divider(self._sidebar, pady=(0, 0))

        scroll_out, inner, _ = make_scrollable(self._sidebar, SURFACE)
        scroll_out.pack(fill="both", expand=True)
        self._list_rows = {}

        for item in items:
            info  = self.individuals.get(item, {})
            dname = next((v for p, v in info.get("assertions", []) if p == "name"), item)
            dname = dname[:35] + "…" if len(dname) > 37 else dname
            types = info.get("types", [])
            icon  = next((CLASS_ICONS.get(t) for t in types if t in CLASS_ICONS), "·")

            row = tk.Frame(inner, bg=SURFACE, cursor="hand2")
            row.pack(fill="x")
            indicator = tk.Frame(row, bg=SURFACE, width=3)
            indicator.place(x=0, y=0, relheight=1)
            inner_row = tk.Frame(row, bg=SURFACE)
            inner_row.pack(fill="x", padx=(10, 8))
            icon_l = tk.Label(inner_row, text=icon, font=FONT_CODE,
                              bg=SURFACE, fg=MUTED, width=2)
            icon_l.pack(side="left", pady=8)
            name_l = tk.Label(inner_row, text=dname, font=FONT_BODY,
                              bg=SURFACE, fg=CREAM, anchor="w")
            name_l.pack(side="left", fill="x", expand=True, pady=8)
            sub = types[0] if types else ""
            if sub and sub != tab:
                tk.Label(inner_row, text=sub, font=FONT_MICRO,
                         bg=SURFACE, fg=MUTED).pack(side="right", padx=(0, 4))

            def _click(e, i=item, r=row, nl=name_l, ind=indicator, t=tab):
                self._select(i, r, nl, ind, t)

            all_ws = (row, inner_row, icon_l, name_l)
            for w in all_ws:
                w.bind("<Button-1>", _click)
                w.bind("<Enter>",    lambda e, r2=row, nl2=name_l, ir=inner_row, il=icon_l, i2=item:
                       (r2.configure(bg=CARD_HOV), nl2.configure(bg=CARD_HOV),
                        ir.configure(bg=CARD_HOV), il.configure(bg=CARD_HOV))
                       if self.sel_item != i2 else None)
                w.bind("<Leave>",    lambda e, r2=row, nl2=name_l, ir=inner_row, il=icon_l, i2=item:
                       (r2.configure(bg=SELECTED if i2==self.sel_item else SURFACE),
                        nl2.configure(bg=SELECTED if i2==self.sel_item else SURFACE),
                        ir.configure(bg=SELECTED if i2==self.sel_item else SURFACE),
                        il.configure(bg=SELECTED if i2==self.sel_item else SURFACE)))

            self._list_rows[item] = (row, name_l, indicator, inner_row, icon_l)

        if items:
            r, l, ind, ir, il = self._list_rows[items[0]]
            self._select(items[0], r, l, ind, tab)

    def _select(self, item, row, name_lbl, indicator, tab):
        if self.sel_item and self.sel_item in self._list_rows:
            pr, pl, pi, pir, pil = self._list_rows[self.sel_item]
            for w in (pr, pl, pir, pil): w.configure(bg=SURFACE)
            pi.configure(bg=SURFACE)
        self.sel_item = item
        row.configure(bg=SELECTED)
        name_lbl.configure(bg=SELECTED)
        indicator.configure(bg=GOLD)
        for w in self._main.winfo_children(): w.destroy()
        self._render_detail(item, tab)

    def _render_detail(self, item, tab):
        info       = self.individuals.get(item, {})
        assertions = info.get("assertions", [])
        by_prop    = defaultdict(list)
        for p, v in assertions:
            by_prop[p].append(v)

        types = info.get("types", [])
        icon  = next((CLASS_ICONS.get(t) for t in types if t in CLASS_ICONS), "◦")
        dname = by_prop.get("name", [item])[0]

        scroll_out, pad, _ = make_scrollable(self._main, BG)
        scroll_out.pack(fill="both", expand=True)
        content = tk.Frame(pad, bg=BG)
        content.pack(padx=40, pady=32, fill="x")

        # Hero
        hero = tk.Frame(content, bg=BG)
        hero.pack(fill="x", pady=(0, 4))
        tk.Label(hero, text=icon, font=("Georgia", 18),
                 bg=BG, fg=GOLD_DIM).pack(side="left", padx=(0, 10))
        title_col = tk.Frame(hero, bg=BG)
        title_col.pack(side="left", fill="x", expand=True)
        tk.Label(title_col, text=dname, font=FONT_TITLE,
                 bg=BG, fg=CREAM, anchor="w").pack(anchor="w")
        chips_row = tk.Frame(title_col, bg=BG)
        chips_row.pack(anchor="w", pady=(5, 0))
        for t in types:
            add_chip(chips_row, t, fg=GOLD, bg=CARD)

        if "rating" in by_prop:
            r_row = tk.Frame(content, bg=BG)
            r_row.pack(anchor="w", pady=(6, 0))
            tk.Label(r_row, text=star_str(by_prop["rating"][0]),
                     font=("Georgia", 12), bg=BG, fg=AMBER).pack(side="left")

        divider(content, GOLD_DIM, pady=(14, 14))

        skip      = {"name", "rating"}
        multi_p   = ["includes", "containsIngredient", "employs",
                     "earnedAward", "receivedAward", "hasMenu", "hasReservation"]
        simple_p  = [(p, v[0] if len(v)==1 else ", ".join(v))
                     for p, v in by_prop.items()
                     if p not in skip and p not in multi_p]
        rel_p     = [(p, by_prop[p]) for p in multi_p if p in by_prop]

        if simple_p:
            tk.Label(content, text="DETAILS", font=FONT_MICRO,
                     bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 6))
            grid = tk.Frame(content, bg=BG)
            grid.pack(fill="x", pady=(0, 16))
            col_a = tk.Frame(grid, bg=BG)
            col_a.pack(side="left", fill="x", expand=True, padx=(0, 6))
            col_b = tk.Frame(grid, bg=BG)
            col_b.pack(side="left", fill="x", expand=True)
            for i, (prop, val) in enumerate(simple_p):
                target = col_a if i % 2 == 0 else col_b
                self._scalar_card(target, prop, val)

        if rel_p:
            divider(content, BORDER, pady=(4, 12))
            tk.Label(content, text="RELATIONS", font=FONT_MICRO,
                     bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 6))
            for prop, vals in rel_p:
                self._relation_group(content, prop, vals)

        divider(content, BORDER, pady=(18, 10))
        uri_card = tk.Frame(content, bg=CARD, padx=14, pady=10)
        uri_card.pack(fill="x")
        tk.Label(uri_card, text="URI", font=FONT_MICRO, bg=CARD, fg=MUTED).pack(anchor="w")
        tk.Label(uri_card, text=info.get("uri", "—"), font=FONT_CODE,
                 bg=CARD, fg=GOLD_DIM, wraplength=680, justify="left"
                 ).pack(anchor="w", pady=(3, 0))

    def _scalar_card(self, parent, prop, val):
        card = tk.Frame(parent, bg=CARD, padx=12, pady=9)
        card.pack(fill="x", pady=3)
        tk.Label(card, text=prop, font=FONT_MICRO, bg=CARD, fg=MUTED).pack(anchor="w")
        display, color = val, CREAM
        if prop == "price":
            try: display = f"${float(val):.2f}"
            except: pass
            color = SAGE
        elif prop == "calories":
            display = f"{val} kcal"; color = MUTED
        elif prop == "isVegan":
            display = "✓ Vegan" if val.lower()=="true" else "✗ Not Vegan"
            color = SAGE if val.lower()=="true" else MUTED
        elif prop == "confirmed":
            display = "✓ Confirmed" if val.lower()=="true" else "⚑ Pending"
            color = SAGE if val.lower()=="true" else ROSE
        elif prop == "seasonal":
            display = "✦ Seasonal" if val.lower()=="true" else "● Year-round"
            color = AMBER if val.lower()=="true" else MUTED
        elif prop == "reservationDate":
            display = val.replace("T", "  ·  ")
        elif prop == "yearsExperience":
            display = f"{val} years"
        elif prop == "partySize":
            display = f"Party of {val}"
        tk.Label(card, text=display, font=FONT_H2, bg=CARD, fg=color,
                 anchor="w").pack(anchor="w", pady=(2, 0))

    def _relation_group(self, parent, prop, values):
        section = tk.Frame(parent, bg=BG)
        section.pack(fill="x", pady=(0, 10))
        tk.Label(section, text=prop.upper(), font=FONT_MICRO, bg=BG, fg=MUTED
                 ).pack(anchor="w", pady=(0, 5))
        wrap = tk.Frame(section, bg=BG)
        wrap.pack(fill="x")
        for val in values:
            ref = self.individuals.get(val)
            if ref:
                dname = next((v for p2, v in ref["assertions"] if p2=="name"), val)
                rtypes = ref.get("types", [])
                icon  = next((CLASS_ICONS.get(t) for t in rtypes if t in CLASS_ICONS), "·")
                pill  = tk.Frame(wrap, bg=CARD, padx=10, pady=6, cursor="hand2")
                pill.pack(side="left", padx=(0, 6), pady=2)
                tk.Label(pill, text=f"{icon}  {dname}", font=FONT_BODY,
                         bg=CARD, fg=GOLD).pack()
                pill.bind("<Button-1>", lambda e, v=val: self._jump(v))
                pill.bind("<Enter>", lambda e, pp=pill: pp.configure(bg=CARD_HOV))
                pill.bind("<Leave>", lambda e, pp=pill: pp.configure(bg=CARD))
            else:
                tk.Label(wrap, text=val, font=FONT_BODY, bg=BG, fg=CREAM
                         ).pack(side="left", padx=(0, 10))

    def _jump(self, individual_id):
        info = self.individuals.get(individual_id)
        if not info: return
        tab_map = {
            "Restaurant": "Restaurant", "HeadChef": "Chefs", "SousChef": "Chefs",
            "PastryChef": "Chefs", "VIPCustomer": "Customers",
            "RegularCustomer": "Customers", "Starter": "Dishes",
            "MainCourse": "Dishes", "Dessert": "Dishes",
            "DegustationMenu": "Menus", "ALaCarteMenu": "Menus",
            "SeasonalMenu": "Menus", "Reservation": "Reservations",
            "Ingredient": "Ingredients", "Award": "Awards",
        }
        priority = list(tab_map.keys())
        dt  = dominant_type(info, priority)
        tab = tab_map.get(dt, "")
        if tab:
            self._switch_tab(tab)
            if individual_id in self._list_rows:
                r, l, ind, ir, il = self._list_rows[individual_id]
                self._select(individual_id, r, l, ind, tab)

    # ─────────────────────────────────────────────────────────────────────
    # SCHEMA VIEW
    # ─────────────────────────────────────────────────────────────────────
    def _view_schema(self, tab):
        tk.Label(self._sidebar, text="CLASS TREE", font=FONT_MICRO,
                 bg=SURFACE, fg=MUTED, pady=10).pack(anchor="w", padx=16)
        divider(self._sidebar, pady=(0, 4))
        scroll_out, inner, _ = make_scrollable(self._sidebar, SURFACE)
        scroll_out.pack(fill="both", expand=True)

        root_classes = [c for c, info in self.classes.items() if not info["subClassOf"]]

        def tree_item(pf, cls, depth=0):
            prefix = "  " * depth + ("└ " if depth else "")
            tk.Label(pf, text=f"{prefix}{cls}", font=FONT_CODE, bg=SURFACE,
                     fg=CREAM if depth==0 else MUTED, anchor="w", pady=3
                     ).pack(fill="x", padx=8)
            for child in sorted(self.sub_classes.get(cls, [])):
                tree_item(pf, child, depth+1)

        for rc in sorted(root_classes):
            tree_item(inner, rc)

        scroll_out2, pad2, _ = make_scrollable(self._main, BG)
        scroll_out2.pack(fill="both", expand=True)
        content = tk.Frame(pad2, bg=BG)
        content.pack(padx=40, pady=32, fill="x")

        tk.Label(content, text="Ontology Schema", font=FONT_TITLE,
                 bg=BG, fg=CREAM).pack(anchor="w")
        tk.Label(content, text=(f"{len(self.classes)} classes  ·  "
                                f"{len(self.obj_props)} object properties  ·  "
                                f"{len(self.data_props)} data properties"),
                 font=FONT_BODY, bg=BG, fg=MUTED).pack(anchor="w", pady=(4, 16))
        divider(content, GOLD_DIM)

        tk.Label(content, text="OBJECT PROPERTIES", font=FONT_MICRO,
                 bg=BG, fg=MUTED, pady=(16, 0)).pack(anchor="w")
        for name, info in sorted(self.obj_props.items()):
            row = tk.Frame(content, bg=CARD, padx=14, pady=10)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=name, font=FONT_H2, bg=CARD, fg=GOLD).pack(anchor="w")
            ar = tk.Frame(row, bg=CARD)
            ar.pack(anchor="w", pady=(3, 0))
            tk.Label(ar, text=info["domain"], font=FONT_CODE, bg=CARD, fg=CREAM).pack(side="left")
            tk.Label(ar, text="  ——▶  ", font=FONT_CODE, bg=CARD, fg=MUTED).pack(side="left")
            tk.Label(ar, text=info["range"],  font=FONT_CODE, bg=CARD, fg=CREAM).pack(side="left")

        divider(content, BORDER, pady=(16, 8))
        tk.Label(content, text="DATA PROPERTIES", font=FONT_MICRO,
                 bg=BG, fg=MUTED, pady=(8, 0)).pack(anchor="w")
        for name, info in sorted(self.data_props.items()):
            row = tk.Frame(content, bg=CARD, padx=14, pady=10)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=name, font=FONT_H2, bg=CARD, fg=GOLD_DIM).pack(anchor="w")
            domains = ", ".join(info["domains"]) if info["domains"] else "—"
            rr = tk.Frame(row, bg=CARD)
            rr.pack(anchor="w", pady=(3, 0))
            tk.Label(rr, text=f"domain: {domains}   range: {info['range']}",
                     font=FONT_CODE, bg=CARD, fg=MUTED).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────
    # QUERY VIEW
    # ─────────────────────────────────────────────────────────────────────
    def _view_query(self, tab):
        tk.Label(self._sidebar, text="QUERY GUIDE", font=FONT_MICRO,
                 bg=SURFACE, fg=MUTED, pady=10).pack(anchor="w", padx=16)
        divider(self._sidebar, pady=(0, 6))
        hints = [
            ("dish:truffle",    "dishes with truffle"),
            ("chef:karim",      "dishes by chef"),
            ("price:<30",       "dishes under $30"),
            ("price:>50",       "dishes over $50"),
            ("rating:>4.7",     "highly rated"),
            ("vegan",           "vegan dishes"),
            ("confirmed",       "confirmed bookings"),
            ("pending",         "unconfirmed"),
            ("party:>4",        "large parties"),
            ("seasonal",        "seasonal ingredients"),
            ("award:michelin",  "michelin awards"),
            ("vip",             "VIP customers"),
            ("visits:>20",      "loyal customers"),
            ("<any text>",      "full-text search"),
        ]
        for cmd, desc in hints:
            row = tk.Frame(self._sidebar, bg=SURFACE)
            row.pack(fill="x", padx=10, pady=1)
            tk.Label(row, text=cmd, font=FONT_CODE, bg=SURFACE, fg=GOLD,
                     width=16, anchor="w").pack(side="left")
            tk.Label(row, text=desc, font=FONT_MICRO, bg=SURFACE, fg=MUTED,
                     anchor="w").pack(side="left")

        pad = tk.Frame(self._main, bg=BG)
        pad.pack(padx=40, pady=28, fill="both", expand=True)
        tk.Label(pad, text="Smart Query", font=FONT_TITLE, bg=BG, fg=CREAM).pack(anchor="w")
        tk.Label(pad, text="Filter the entire ontology in real-time",
                 font=FONT_BODY, bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 14))
        divider(pad, GOLD_DIM)

        entry_frame = tk.Frame(pad, bg=CARD, padx=12, pady=8)
        entry_frame.pack(fill="x", pady=12)
        self._qvar = tk.StringVar()
        entry = tk.Entry(entry_frame, textvariable=self._qvar,
                         font=("Georgia", 11), bg=CARD, fg=CREAM,
                         insertbackground=GOLD, relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=4)
        entry.bind("<Return>", lambda e: self._run_query())
        tk.Button(entry_frame, text="SEARCH ▶", font=FONT_BADGE,
                  bg=GOLD_DIM, fg=CREAM, relief="flat", padx=12, cursor="hand2",
                  command=self._run_query).pack(side="right")

        presets = [
            ("★ Rating > 4.8",    "rating:>4.8"),
            ("💰 Price < $30",    "price:<30"),
            ("🌿 Vegan",           "vegan"),
            ("✓ Confirmed",       "confirmed"),
            ("⚑ Pending",        "pending"),
            ("✦ Seasonal",       "seasonal"),
            ("◆ VIP Customers",  "vip"),
            ("★ Awards",         "award:"),
            ("👑 Sofia's Dishes", "chef:sofia"),
        ]
        prow = tk.Frame(pad, bg=BG)
        prow.pack(anchor="w", pady=(0, 14))
        for label, q in presets:
            b = tk.Label(prow, text=label, font=FONT_CODE, bg=CARD,
                         fg=GOLD, padx=8, pady=5, cursor="hand2")
            b.pack(side="left", padx=(0, 5), pady=2)
            b.bind("<Button-1>", lambda e, qq=q: (self._qvar.set(qq), self._run_query()))
            b.bind("<Enter>",    lambda e, bb=b: bb.configure(bg=CARD_HOV))
            b.bind("<Leave>",    lambda e, bb=b: bb.configure(bg=CARD))

        self._qresult = tk.Frame(pad, bg=BG)
        self._qresult.pack(fill="both", expand=True)

    def _run_query(self):
        for w in self._qresult.winfo_children(): w.destroy()
        q = self._qvar.get().strip().lower()
        results = []

        for item, info in self.individuals.items():
            a     = {p: v for p, v in info.get("assertions", [])}
            types = [t.lower() for t in info.get("types", [])]
            name  = a.get("name", item).lower()
            all_t = " ".join([item.lower(), name] + [v.lower() for _, v in info.get("assertions", [])])
            match = False

            if q.startswith("dish:"):
                kw = q[5:]
                if any(t in ("starter","maincourse","dessert") for t in types):
                    match = kw in all_t
            elif q.startswith("chef:"):
                kw = q[5:]
                if any(t in ("starter","maincourse","dessert") for t in types):
                    chef_id = a.get("preparedBy","")
                    if chef_id:
                        ci = self.individuals.get(chef_id, {})
                        cn = next((v for p,v in ci.get("assertions",[]) if p=="name"),"").lower()
                        match = kw in cn
            elif q.startswith("price:<"):
                try:
                    limit = float(q[7:])
                    match = "price" in a and float(a["price"]) < limit
                except: pass
            elif q.startswith("price:>"):
                try:
                    limit = float(q[7:])
                    match = "price" in a and float(a["price"]) > limit
                except: pass
            elif q.startswith("rating:>"):
                try:
                    limit = float(q[8:])
                    match = "rating" in a and float(a["rating"]) > limit
                except: pass
            elif q == "vegan":
                match = a.get("isVegan","false").lower() == "true"
            elif q == "confirmed":
                match = "reservation" in types and a.get("confirmed","false").lower() == "true"
            elif q == "pending":
                match = "reservation" in types and a.get("confirmed","true").lower() == "false"
            elif q == "seasonal":
                match = "ingredient" in types and a.get("seasonal","false").lower() == "true"
            elif q == "vip":
                match = "vipcustomer" in types
            elif q.startswith("party:>"):
                try:
                    limit = int(q[7:])
                    match = "reservation" in types and int(a.get("partySize",0)) > limit
                except: pass
            elif q.startswith("visits:>"):
                try:
                    limit = int(q[8:])
                    match = int(a.get("totalVisits",0)) > limit
                except: pass
            elif q.startswith("award:"):
                kw = q[6:]
                if "award" in types:
                    match = not kw or kw in all_t
            elif q.startswith("ingredient:"):
                kw = q[11:]
                if "ingredient" in types:
                    match = kw in all_t
            elif q:
                match = q in all_t

            if match:
                results.append((item, info, a))

        tk.Label(self._qresult, text=f"  {len(results)} result{'s' if len(results)!=1 else ''}",
                 font=FONT_CODE, bg=BG, fg=MUTED, pady=4).pack(anchor="w")
        divider(self._qresult, BORDER, pady=(2, 8))

        if not results:
            tk.Label(self._qresult, text="No matches found.",
                     font=FONT_BODY, bg=BG, fg=MUTED).pack(anchor="w")
            return

        scroll_out, inner, _ = make_scrollable(self._qresult, BG)
        scroll_out.pack(fill="both", expand=True)

        tab_map = {
            "Restaurant": "Restaurant", "HeadChef": "Chefs", "SousChef": "Chefs",
            "PastryChef": "Chefs", "VIPCustomer": "Customers",
            "RegularCustomer": "Customers", "Starter": "Dishes",
            "MainCourse": "Dishes", "Dessert": "Dishes",
            "DegustationMenu": "Menus", "ALaCarteMenu": "Menus",
            "SeasonalMenu": "Menus", "Reservation": "Reservations",
            "Ingredient": "Ingredients", "Award": "Awards",
        }
        priority = list(tab_map.keys())

        for item, info, a in results:
            types = info.get("types", [])
            icon  = next((CLASS_ICONS.get(t) for t in types if t in CLASS_ICONS), "·")
            dname = a.get("name", item)
            dt    = dominant_type(info, priority)

            card = tk.Frame(inner, bg=CARD, padx=16, pady=12, cursor="hand2")
            card.pack(fill="x", pady=3)
            hrow = tk.Frame(card, bg=CARD)
            hrow.pack(fill="x")
            tk.Label(hrow, text=icon, font=FONT_CODE, bg=CARD, fg=MUTED
                     ).pack(side="left", padx=(0, 8))
            tk.Label(hrow, text=dname, font=FONT_H2, bg=CARD, fg=GOLD
                     ).pack(side="left")
            chips_row = tk.Frame(card, bg=CARD)
            chips_row.pack(anchor="w", pady=(4, 2))
            for t in types:
                add_chip(chips_row, t, fg=GOLD_DIM, bg=SURFACE)

            facts = []
            for key, label in [("rating","★"), ("price","$"), ("partySize","party"),
                                ("calories","kcal"), ("origin","from"), ("year","yr")]:
                if key in a:
                    v = a[key]
                    if key == "price":  v = f"${float(v):.2f}"
                    elif key == "rating": v = f"★ {float(v):.1f}"
                    elif key == "partySize": v = f"party of {v}"
                    elif key == "calories": v = f"{v} kcal"
                    elif key == "year": v = f"{v}"
                    else: v = f"{label} {v}"
                    facts.append(str(v))
            if facts:
                tk.Label(card, text="   ".join(facts[:4]),
                         font=FONT_CODE, bg=CARD, fg=MUTED).pack(anchor="w")

            card.bind("<Button-1>", lambda e, i=item: self._jump(i))
            card.bind("<Enter>",    lambda e, c=card: c.configure(bg=CARD_HOV))
            card.bind("<Leave>",    lambda e, c=card: c.configure(bg=CARD))


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    path = None
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for c in ["maison_elite.owl",
              os.path.join(script_dir, "maison_elite.owl"),
              "hello1.owl",
              os.path.join(script_dir, "hello1.owl")]:
        if os.path.exists(c):
            path = c
            break

    if not path:
        root_tmp = tk.Tk()
        root_tmp.withdraw()
        path = filedialog.askopenfilename(
            title="Locate your OWL ontology file",
            filetypes=[("OWL Files", "*.owl *.rdf"), ("All Files", "*.*")]
        )
        root_tmp.destroy()

    if not path:
        print("No OWL file selected.")
        sys.exit(0)

    App(path).mainloop()
