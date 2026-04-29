import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import time
import xml.etree.ElementTree as ET
import re  # Necesaria para el Ejercicio 3 (Expresiones Regulares)

# ==========================================
# CEREBRO MATEMÁTICO: CONVERSIÓN AFD A ER (EJERCICIO 2)
# ==========================================
class ConvertidorAFD_ER:
    def __init__(self, datos_afd):
        estado_ini_nuevo = "Qi"
        estado_fin_nuevo = "Qf"
        final = ""
        
        self.estados = [e['id'] for e in datos_afd['estados']]
        self.transiciones = [{"origen": t["de"], "destino": t["a"], "lectura": t["lee"]} for t in datos_afd['transiciones']]
        self.inicial_original = datos_afd['inicial']
        self.finales_originales = list(datos_afd['finales'])
        
        self.estados.append(estado_ini_nuevo)
        self.estados.append(estado_fin_nuevo)
        
        self.transiciones.append({"origen": estado_ini_nuevo, "destino": self.inicial_original, "lectura": "ε"})
        
        for final in self.finales_originales:
            self.transiciones.append({"origen": final, "destino": estado_fin_nuevo, "lectura": "ε"})
            
        self.estados_a_eliminar = [e for e in self.estados if e not in (estado_ini_nuevo, estado_fin_nuevo)]

    def ejecutar_siguiente_paso(self):
        q_elim = ""
        entrantes = []
        salientes = []
        bucles = []
        str_bucle = ""
        nuevas_transiciones = []
        r1 = ""
        r3 = ""
        r1_fmt = ""
        r3_fmt = ""
        nueva_ruta = ""
        t = {}
        ent = {}
        sal = {}

        if not self.estados_a_eliminar:
            for t in self.transiciones:
                if t["origen"] == "Qi" and t["destino"] == "Qf":
                    return t["lectura"]
            return "∅"

        q_elim = self.estados_a_eliminar.pop(0)
        
        entrantes = [t for t in self.transiciones if t['destino'] == q_elim and t['origen'] != q_elim]
        salientes = [t for t in self.transiciones if t['origen'] == q_elim and t['destino'] != q_elim]
        bucles = [t for t in self.transiciones if t['origen'] == q_elim and t['destino'] == q_elim]
        
        str_bucle = f"({bucles[0]['lectura']})*" if bucles else ""
        
        for ent in entrantes:
            for sal in salientes:
                r1 = ent['lectura']
                r3 = sal['lectura']
                
                r1_fmt = r1 if len(r1) == 1 else f"({r1})"
                r3_fmt = r3 if len(r3) == 1 else f"({r3})"
                
                nueva_ruta = f"{r1_fmt}{str_bucle}{r3_fmt}".replace("ε", "")
                
                nuevas_transiciones.append({
                    "origen": ent['origen'],
                    "destino": sal['destino'],
                    "lectura": nueva_ruta if nueva_ruta else "ε"
                })
                
        self.transiciones = [t for t in self.transiciones if t['origen'] != q_elim and t['destino'] != q_elim]
        self.transiciones.extend(nuevas_transiciones)
        self._simplificar_transiciones_paralelas()
        self.estados.remove(q_elim)
        
        return f"Se eliminó el estado: {q_elim}"

    def _simplificar_transiciones_paralelas(self):
        dic_trans = {}
        trans_simplificadas = []
        clave = ()
        unidas = ""
        t = {}
        o = ""
        d = ""
        lecturas = []
        
        for t in self.transiciones:
            clave = (t["origen"], t["destino"])
            if clave not in dic_trans:
                dic_trans[clave] = []
            dic_trans[clave].append(t["lectura"])
            
        for (o, d), lecturas in dic_trans.items():
            if len(lecturas) > 1:
                unidas = " U ".join(lecturas)
                trans_simplificadas.append({"origen": o, "destino": d, "lectura": f"({unidas})"})
            else:
                trans_simplificadas.append({"origen": o, "destino": d, "lectura": lecturas[0]})
                
        self.transiciones = trans_simplificadas

# ==========================================
# CEREBRO MATEMÁTICO: MOTOR AFN / AFN-λ / MINIMIZACIÓN
# ==========================================
class MotorAutomata:
    def __init__(self, datos_json):
        estado = {}
        t = {}
        origen = ""
        destino = ""
        simbolo = ""
        
        self.inicial = datos_json.get('inicial', '')
        self.finales = set(datos_json.get('finales', []))
        self.alfabeto = set(datos_json.get('alfabeto', []))
        self.transiciones = {}
        
        for estado in datos_json.get('estados', []):
            self.transiciones[estado['id']] = {}
            
        for t in datos_json.get('transiciones', []):
            origen = t['de']
            destino = t['a']
            simbolo = t['lee']
            
            if simbolo not in self.transiciones[origen]:
                self.transiciones[origen][simbolo] = set()
            self.transiciones[origen][simbolo].add(destino)

    def clausura_lambda(self, estados_actuales):
        clausura = set(estados_actuales)
        pila = list(estados_actuales)
        estado_actual = ""
        destinos_lambda = []
        destino = ""
        
        while pila:
            estado_actual = pila.pop()
            if 'λ' in self.transiciones.get(estado_actual, {}):
                destinos_lambda = self.transiciones[estado_actual]['λ']
                for destino in destinos_lambda:
                    if destino not in clausura:
                        clausura.add(destino)
                        pila.append(destino)
        return clausura

    def mover(self, estados_actuales, simbolo):
        destinos = set()
        estado = ""
        
        for estado in estados_actuales:
            if simbolo in self.transiciones.get(estado, {}):
                destinos.update(self.transiciones[estado][simbolo])
        return destinos

    def simular_cadena_paso_a_paso(self, cadena):
        historial = []
        estados_activos = set()
        i = 0
        simbolo = ""
        estados_alcanzados = set()
        es_aceptada = False
        
        estados_activos = self.clausura_lambda({self.inicial})
        
        historial.append({
            "paso": 0,
            "simbolo": "INICIO (λ)",
            "estados_activos": sorted(list(estados_activos))
        })
        
        for i, simbolo in enumerate(cadena):
            estados_alcanzados = self.mover(estados_activos, simbolo)
            estados_activos = self.clausura_lambda(estados_alcanzados)
            
            historial.append({
                "paso": i + 1,
                "simbolo": simbolo,
                "estados_activos": sorted(list(estados_activos)) if estados_activos else ["Ø (Muerte)"]
            })
            if not estados_activos:
                break
                
        es_aceptada = bool(estados_activos.intersection(self.finales))
        return es_aceptada, historial

    def minimizar_afd(self):
        alcanzables = set([self.inicial])
        pila = [self.inicial]
        est = ""
        sim = ""
        dest = []
        estados_eliminados = set()
        f_alcanzables = set()
        nf_alcanzables = set()
        particiones = []
        cambio = True
        nuevas_particiones = []
        grupo = []
        subgrupos = {}
        estado = ""
        firma = []
        destinos = []
        destino = ""
        idx = -1
        i = 0
        p = []
        nuevas_transiciones = []
        nombres_grupos = {}
        nombre = ""
        rep = ""
        origen = ""
        
        # 1. Eliminar inalcanzables
        while pila:
            est = pila.pop()
            for sim in self.alfabeto:
                dest = list(self.transiciones.get(est, {}).get(sim, set()))
                if dest and dest[0] not in alcanzables:
                    alcanzables.add(dest[0])
                    pila.append(dest[0])

        estados_eliminados = set(self.transiciones.keys()) - alcanzables

        # 2. Inicializar particiones
        f_alcanzables = self.finales.intersection(alcanzables)
        nf_alcanzables = alcanzables - f_alcanzables

        if f_alcanzables: particiones.append(f_alcanzables)
        if nf_alcanzables: particiones.append(nf_alcanzables)

        # 3. Refinar particiones
        while cambio:
            cambio = False
            nuevas_particiones = []
            for grupo in particiones:
                if len(grupo) <= 1:
                    nuevas_particiones.append(grupo)
                    continue

                subgrupos = {}
                for estado in grupo:
                    firma = []
                    for sim in sorted(list(self.alfabeto)):
                        destinos = list(self.transiciones.get(estado, {}).get(sim, set()))
                        destino = destinos[0] if destinos else None
                        idx = -1
                        for i, p in enumerate(particiones):
                            if destino in p:
                                idx = i
                                break
                        firma.append(idx)
                    firma = tuple(firma)
                    if firma not in subgrupos:
                        subgrupos[firma] = set()
                    subgrupos[firma].add(estado)

                nuevas_particiones.extend(subgrupos.values())
                if len(subgrupos) > 1:
                    cambio = True
            particiones = nuevas_particiones

        # 4. Construir Autómata Minimizado
        for grupo in particiones:
            nombre = "q{" + ",".join(sorted(list(grupo))) + "}"
            for est in grupo:
                nombres_grupos[est] = nombre

        for grupo in particiones:
            rep = list(grupo)[0]
            origen = nombres_grupos[rep]
            for sim in sorted(list(self.alfabeto)):
                destinos = list(self.transiciones.get(rep, {}).get(sim, set()))
                if destinos:
                    dest = destinos[0]
                    nuevas_transiciones.append({
                        "de": origen,
                        "lee": sim,
                        "a": nombres_grupos[dest]
                    })

        return {
            "eliminados": estados_eliminados,
            "particiones": particiones,
            "nuevas_transiciones": nuevas_transiciones
        }
    
    def convertir_afnd_a_afd(self):
        alfabeto_real = []
        inicial_afd = frozenset()
        estados_afd = []
        pila_procesamiento = []
        transiciones_afd = []
        estado_actual = frozenset()
        sim = ""
        alcanzables = set()
        destino_clausura = frozenset()
        finales_afd = []
        est = frozenset()
        
        alfabeto_real = sorted([s for s in self.alfabeto if s != 'λ'])
        
        inicial_afd = frozenset(self.clausura_lambda({self.inicial}))
        
        estados_afd = [inicial_afd]
        pila_procesamiento = [inicial_afd]
        
        while pila_procesamiento:
            estado_actual = pila_procesamiento.pop(0)
            
            for sim in alfabeto_real:
                alcanzables = self.mover(estado_actual, sim)
                
                if not alcanzables:
                    continue 
                    
                destino_clausura = frozenset(self.clausura_lambda(alcanzables))
                
                transiciones_afd.append({
                    "de": estado_actual,
                    "lee": sim,
                    "a": destino_clausura
                })
                
                if destino_clausura not in estados_afd:
                    estados_afd.append(destino_clausura)
                    pila_procesamiento.append(destino_clausura)
                    
        finales_afd = [est for est in estados_afd if est.intersection(self.finales)]
        
        return {
            "inicial": inicial_afd,
            "estados": estados_afd,
            "transiciones": transiciones_afd,
            "finales": finales_afd,
            "alfabeto": alfabeto_real
        }

# ==========================================
# APLICACIÓN PRINCIPAL (GUI)
# ==========================================
def main():
    root = tk.Tk()
    root.title("Simulador Avanzado AFD/AFN - Proyecto TC")
    root.geometry("1050x750")
    root.eval('tk::PlaceWindow . center')
    root.configure(bg="#f0f2f5")

    style = ttk.Style()
    style.theme_use('clam') 
    style.configure("TFrame", background="#f0f2f5")
    style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1a365d")
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6, background="#2b6cb0", foreground="white")
    style.map("TButton", background=[("active", "#2c5282")])
    style.configure("TLabelframe", background="#ffffff", borderwidth=2)
    style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground="#2d3748", background="#ffffff")
    style.configure("Treeview", font=("Consolas", 10), rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1a202c")
    style.map("Treeview", background=[("selected", "#bee3f8")], foreground=[("selected", "#2b6cb0")])

    app_state = {
        "motor": None, 
        "datos_json": None,
        "convertidor_er": None 
    }

    def escribir_consola(mensaje):
        consola.config(state=tk.NORMAL)
        consola.insert(tk.END, f"> {mensaje}\n")
        consola.see(tk.END)
        consola.config(state=tk.DISABLED)
        root.update()
        time.sleep(0.05)

    def cargar_archivo():
        ruta = ""
        datos = {}
        tree = None
        root_xml = None
        automaton = None
        state = None
        id_estado = ""
        nombre = ""
        trans = None
        origen = ""
        destino = ""
        read_tag = None
        lee = ""
        alfabeto = []
        nombres_estados = []
        i = 0
        t = {}
        tag = ""
        item = ""
        
        ruta = filedialog.askopenfilename(
            title="Descubre tu Autómata", 
            filetypes=[
                ("Todos los soportados", "*.jff *.json *.xml"),
                ("Archivos JFLAP", "*.jff"),
                ("Archivos JSON", "*.json"),
                ("Archivos XML", "*.xml")
            ]
        )
        if not ruta: return
            
        try:
            consola.config(state=tk.NORMAL)
            consola.delete(1.0, tk.END)
            consola.config(state=tk.DISABLED)
            
            escribir_consola(f"Iniciando análisis del archivo: {ruta.split('/')[-1]}...")
            
            if ruta.endswith('.json'):
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                escribir_consola("JSON descifrado con éxito.")
                
            elif ruta.endswith('.jff') or ruta.endswith('.xml'):
                escribir_consola("Detectado formato XML/JFLAP. Parseando nodos...")
                tree = ET.parse(ruta)
                root_xml = tree.getroot()
                automaton = root_xml.find('automaton')
                
                datos = {
                    'estados': [],
                    'transiciones': [],
                    'inicial': '',
                    'finales': [],
                    'alfabeto': set()
                }
                
                for state in automaton.findall('state'):
                    id_estado = state.get('id')
                    nombre = state.get('name')
                    datos['estados'].append({'id': id_estado, 'nombre': nombre})
                    
                    if state.find('initial') is not None:
                        datos['inicial'] = id_estado
                    if state.find('final') is not None:
                        datos['finales'].append(id_estado)
                        
                for trans in automaton.findall('transition'):
                    origen = trans.find('from').text
                    destino = trans.find('to').text
                    read_tag = trans.find('read')
                    lee = read_tag.text if read_tag is not None and read_tag.text else 'λ'
                    
                    datos['transiciones'].append({'de': origen, 'lee': lee, 'a': destino})
                    if lee != 'λ':
                        datos['alfabeto'].add(lee)
                        
                datos['alfabeto'] = list(datos['alfabeto'])
                escribir_consola("Archivo JFLAP traducido a modelo lógico.")

            app_state["datos_json"] = datos
            app_state["motor"] = MotorAutomata(datos)
            
            alfabeto = datos.get('alfabeto', [])
            escribir_consola(f"Extrayendo alfabeto Σ = {{ {', '.join(alfabeto)} }}")
            lbl_alfabeto.config(text=f"Σ = {{ {', '.join(alfabeto)} }}")
            
            nombres_estados = [e['nombre'] for e in datos.get('estados', [])]
            escribir_consola(f"Identificando Q... ({len(nombres_estados)} encontrados)")
            lbl_estados.config(text=f"Q = {{ {', '.join(nombres_estados)} }}")
            lbl_inicial.config(text=f"q0 = {datos.get('inicial', '')}")
            lbl_finales.config(text=f"F = {{ {', '.join(datos.get('finales', []))} }}")
            
            for item in tabla_transiciones.get_children(): tabla_transiciones.delete(item)
                
            escribir_consola("Mapeando función de transición δ...")
            for i, t in enumerate(datos.get("transiciones", [])):
                tag = 'par' if i % 2 == 0 else 'impar'
                tabla_transiciones.insert("", tk.END, values=(f"δ({t['de']}, {t['lee']})", "→", t["a"]), tags=(tag,))
            
            for item in tabla_orig.get_children(): tabla_orig.delete(item)
            for item in tabla_mini.get_children(): tabla_mini.delete(item)
            lbl_stats_min.config(text="Esperando ejecución...")

            app_state["convertidor_er"] = None
            txt_pantalla_er.config(state=tk.NORMAL)
            txt_pantalla_er.delete(1.0, tk.END)
            txt_pantalla_er.config(state=tk.DISABLED)
            lbl_er_resultado.config(text="Expresión Regular Resultante: [Esperando...]", foreground="#2b6cb0")
            btn_paso_er.config(state=tk.DISABLED)

            escribir_consola("¡Autómata ensamblado y listo para simular!")
            messagebox.showinfo("Éxito", "El autómata ha sido cargado.")
            
        except Exception as e:
            escribir_consola(f"[ERROR CRÍTICO] {str(e)}")
            messagebox.showerror("Error", "Archivo inválido o formato incorrecto.")

    header_frame = ttk.Frame(root, padding=15)
    header_frame.pack(fill='x')
    ttk.Label(header_frame, text="Simulador de Autómatas Finitos Deterministas y No Deterministas", style="Header.TLabel").pack()
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    # --- PESTAÑA 1: DEFINICIÓN ---
    tab1 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab1, text="Definición y Carga ")

    panel_izq = ttk.Frame(tab1)
    panel_izq.pack(side=tk.LEFT, fill='y', padx=15, pady=15)
    ttk.Button(panel_izq, text="🔍 Explorar Archivo", command=cargar_archivo).pack(fill='x', pady=(0, 15), ipady=5)

    frame_info = ttk.LabelFrame(panel_izq, text=" 5 Tuplas del Autómata ")
    frame_info.pack(fill='both', expand=True)
    ttk.Label(frame_info, text="Alfabeto:", font=("Segoe UI", 9, "italic")).pack(anchor='w', padx=10, pady=(10,0))
    lbl_alfabeto = ttk.Label(frame_info, text="Σ = { }", font=("Consolas", 12, "bold"), foreground="#2b6cb0")
    lbl_alfabeto.pack(anchor='w', padx=10)
    ttk.Label(frame_info, text="Estados:", font=("Segoe UI", 9, "italic")).pack(anchor='w', padx=10, pady=(10,0))
    lbl_estados = ttk.Label(frame_info, text="Q = { }", font=("Consolas", 11, "bold"), foreground="#2b6cb0")
    lbl_estados.pack(anchor='w', padx=10)
    ttk.Label(frame_info, text="Estado Inicial:", font=("Segoe UI", 9, "italic")).pack(anchor='w', padx=10, pady=(10,0))
    lbl_inicial = ttk.Label(frame_info, text="q0 = ", font=("Consolas", 12, "bold"), foreground="#38a169")
    lbl_inicial.pack(anchor='w', padx=10)
    ttk.Label(frame_info, text="Estados Finales:", font=("Segoe UI", 9, "italic")).pack(anchor='w', padx=10, pady=(10,0))
    lbl_finales = ttk.Label(frame_info, text="F = { }", font=("Consolas", 12, "bold"), foreground="#e53e3e")
    lbl_finales.pack(anchor='w', padx=10, pady=(0, 10))

    panel_der = ttk.Frame(tab1)
    panel_der.pack(side=tk.RIGHT, fill='both', expand=True, padx=15, pady=15)
    frame_tabla = ttk.LabelFrame(panel_der, text=" Función de Transición ")
    frame_tabla.pack(fill='both', expand=True, pady=(0, 10))
    tabla_transiciones = ttk.Treeview(frame_tabla, columns=("origen", "flecha", "destino"), show="headings")
    tabla_transiciones.heading("origen", text="Estado + Lectura")
    tabla_transiciones.heading("flecha", text="")
    tabla_transiciones.heading("destino", text="Destino")
    tabla_transiciones.column("origen", anchor='center', width=200)
    tabla_transiciones.column("flecha", anchor='center', width=50)
    tabla_transiciones.column("destino", anchor='center', width=150)
    scroll_tabla = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla_transiciones.yview)
    tabla_transiciones.configure(yscroll=scroll_tabla.set)
    scroll_tabla.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_transiciones.pack(fill='both', expand=True, padx=2, pady=2)
    tabla_transiciones.tag_configure('par', background='#f7fafc')
    tabla_transiciones.tag_configure('impar', background='#ffffff')

    frame_consola = ttk.LabelFrame(panel_der, text=" Consola ")
    frame_consola.pack(fill='x')
    consola = tk.Text(frame_consola, height=6, bg="#1a202c", fg="#48bb78", font=("Consolas", 10), state=tk.DISABLED)
    consola.pack(fill='both', expand=True, padx=2, pady=2)

    # --- PESTAÑA 2: SIMULACIÓN ---
    tab2 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab2, text="Simulación Paso a Paso ")

    frame_entrada = ttk.Frame(tab2, padding=20)
    frame_entrada.pack(fill='x')
    ttk.Label(frame_entrada, text="Ingresa la cadena:", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
    entry_cadena = ttk.Entry(frame_entrada, font=("Consolas", 14), width=30)
    entry_cadena.pack(side=tk.LEFT, padx=10)
    
    def ejecutar_simulacion():
        cadena = ""
        motor = None
        item = ""
        es_aceptada = False
        historial = []
        paso = {}
        estados_formateados = ""
        tag = ""
        
        if not app_state["motor"]:
            messagebox.showwarning("Alto", "Carga un autómata primero.")
            return
        cadena = entry_cadena.get()
        motor = app_state["motor"]
        
        for item in tabla_simulacion.get_children(): tabla_simulacion.delete(item)
            
        es_aceptada, historial = motor.simular_cadena_paso_a_paso(cadena)
        for paso in historial:
            estados_formateados = f"{{ {', '.join(paso['estados_activos'])} }}"
            tag = 'par' if paso['paso'] % 2 == 0 else 'impar'
            tabla_simulacion.insert("", tk.END, values=(paso['paso'], paso['simbolo'], estados_formateados), tags=(tag,))
            
        if es_aceptada: lbl_resultado.config(text="CADENA ACEPTADA", foreground="#38a169")
        else: lbl_resultado.config(text="CADENA RECHAZADA", foreground="#e53e3e")

    ttk.Button(frame_entrada, text="⚡ Ejecutar", command=ejecutar_simulacion).pack(side=tk.LEFT, padx=10, ipady=4)
    lbl_resultado = ttk.Label(tab2, text="ESPERANDO CADENA...", font=("Segoe UI", 20, "bold"), foreground="#718096")
    lbl_resultado.pack(pady=10)

    frame_recorrido = ttk.LabelFrame(tab2, text=" Trazabilidad de Ramificaciones (AFND) y Clausura λ ")
    frame_recorrido.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    tabla_simulacion = ttk.Treeview(frame_recorrido, columns=("paso", "simbolo", "estados"), show="headings")
    tabla_simulacion.heading("paso", text="Paso")
    tabla_simulacion.heading("simbolo", text="Símbolo Leído")
    tabla_simulacion.heading("estados", text="Conjunto de Estados Activos")
    tabla_simulacion.column("paso", anchor='center', width=80)
    tabla_simulacion.column("simbolo", anchor='center', width=150)
    tabla_simulacion.column("estados", anchor='center', width=500)
    scroll_sim = ttk.Scrollbar(frame_recorrido, orient=tk.VERTICAL, command=tabla_simulacion.yview)
    tabla_simulacion.configure(yscroll=scroll_sim.set)
    scroll_sim.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_simulacion.pack(fill='both', expand=True, padx=2, pady=2)
    tabla_simulacion.tag_configure('par', background='#f7fafc')
    tabla_simulacion.tag_configure('impar', background='#ffffff')

    # --- PESTAÑA 3: MINIMIZACIÓN LADO A LADO ---
    tab3 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab3, text="Minimización y Reducción ")

    frame_controles_min = ttk.Frame(tab3, padding=15)
    frame_controles_min.pack(fill='x')

    def ejecutar_minimizacion():
        item = ""
        datos_orig = []
        i = 0
        t = {}
        tag = ""
        resultado = {}
        estados_orig = 0
        estados_nuevos = 0
        eliminados = 0
        texto_stats = ""
        grupos_fusionados = []
        msg = ""
        
        if not app_state["motor"]:
            messagebox.showwarning("Alto", "Carga un autómata primero.")
            return

        for item in tabla_orig.get_children(): tabla_orig.delete(item)
        for item in tabla_mini.get_children(): tabla_mini.delete(item)

        datos_orig = app_state["datos_json"]["transiciones"]
        for i, t in enumerate(datos_orig):
            tag = 'par' if i % 2 == 0 else 'impar'
            tabla_orig.insert("", tk.END, values=(t["de"], "→", t["a"]), tags=(tag,))

        resultado = app_state["motor"].minimizar_afd()

        for i, t in enumerate(resultado["nuevas_transiciones"]):
            tag = 'par' if i % 2 == 0 else 'impar'
            tabla_mini.insert("", tk.END, values=(t["de"], f"--({t['lee']})-->", t["a"]), tags=(tag,))

        estados_orig = len(app_state["motor"].transiciones)
        estados_nuevos = len(resultado["particiones"])
        eliminados = len(resultado["eliminados"])

        texto_stats = f"Estados Originales: {estados_orig} | Minimizados: {estados_nuevos} | Inalcanzables Eliminados: {eliminados}"
        lbl_stats_min.config(text=texto_stats)

        if estados_orig == estados_nuevos:
            messagebox.showinfo("Información", "El autómata ya está en su forma mínima. No hay estados equivalentes para fusionar.")
        else:
            grupos_fusionados = [f"Grupo Equivalente: {{{','.join(g)}}}" for g in resultado["particiones"] if len(g) > 1]
            msg = "Minimización completada. Se agruparon:\n\n" + "\n".join(grupos_fusionados)
            messagebox.showinfo("Minimización Exitosa", msg)

    ttk.Button(frame_controles_min, text="✂️ Ejecutar Algoritmo Hopcroft", command=ejecutar_minimizacion).pack(side=tk.LEFT, padx=10, ipady=4)
    lbl_stats_min = ttk.Label(frame_controles_min, text="Esperando ejecución...", font=("Segoe UI", 11, "bold"), foreground="#2b6cb0")
    lbl_stats_min.pack(side=tk.LEFT, padx=20)

    frame_tablas_min = ttk.Frame(tab3, padding=10)
    frame_tablas_min.pack(fill='both', expand=True)

    frame_orig = ttk.LabelFrame(frame_tablas_min, text=" Grafo Original ")
    frame_orig.pack(side=tk.LEFT, fill='both', expand=True, padx=5)
    
    tabla_orig = ttk.Treeview(frame_orig, columns=("origen", "flecha", "destino"), show="headings")
    tabla_orig.heading("origen", text="Origen")
    tabla_orig.heading("flecha", text="")
    tabla_orig.heading("destino", text="Destino")
    tabla_orig.column("origen", anchor='center', width=100)
    tabla_orig.column("flecha", anchor='center', width=50)
    tabla_orig.column("destino", anchor='center', width=100)
    
    scroll_orig = ttk.Scrollbar(frame_orig, orient=tk.VERTICAL, command=tabla_orig.yview)
    tabla_orig.configure(yscroll=scroll_orig.set)
    scroll_orig.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_orig.pack(fill='both', expand=True, padx=2, pady=2)
    tabla_orig.tag_configure('par', background='#f7fafc')
    tabla_orig.tag_configure('impar', background='#ffffff')

    frame_mini = ttk.LabelFrame(frame_tablas_min, text=" Grafo Minimizado ")
    frame_mini.pack(side=tk.RIGHT, fill='both', expand=True, padx=5)
    
    tabla_mini = ttk.Treeview(frame_mini, columns=("origen", "flecha", "destino"), show="headings")
    tabla_mini.heading("origen", text="Origen Fusionado")
    tabla_mini.heading("flecha", text="")
    tabla_mini.heading("destino", text="Destino Fusionado")
    tabla_mini.column("origen", anchor='center', width=150)
    tabla_mini.column("flecha", anchor='center', width=60)
    tabla_mini.column("destino", anchor='center', width=150)
    
    scroll_mini = ttk.Scrollbar(frame_mini, orient=tk.VERTICAL, command=tabla_mini.yview)
    tabla_mini.configure(yscroll=scroll_mini.set)
    scroll_mini.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_mini.pack(fill='both', expand=True, padx=2, pady=2)
    tabla_mini.tag_configure('par', background='#ebf8ff')
    tabla_mini.tag_configure('impar', background='#ffffff')

# --- PESTAÑA 4: CONVERSIÓN AFND -> AFD ---
    tab4 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab4, text="Conversión a AFD (Subconjuntos) ")

    frame_controles_conv = ttk.Frame(tab4, padding=15)
    frame_controles_conv.pack(fill='x')

    def formatear_estado(f_set):
        if not f_set: return "Ø"
        return f"{{ {', '.join(sorted(list(f_set)))} }}"

    def ejecutar_conversion():
        item = ""
        resultado = {}
        est = frozenset()
        es_inicial = ""
        es_final = ""
        nombre = ""
        tag = ""
        i = 0
        t = {}
        origen = ""
        destino = ""
        
        if not app_state["motor"]:
            messagebox.showwarning("Alto", "Carga un autómata primero.")
            return

        for item in tabla_nuevos_estados.get_children(): tabla_nuevos_estados.delete(item)
        for item in tabla_nuevas_trans.get_children(): tabla_nuevas_trans.delete(item)

        resultado = app_state["motor"].convertir_afnd_a_afd()

        for est in resultado["estados"]:
            es_inicial = "SÍ" if est == resultado["inicial"] else "No"
            es_final = "SÍ" if est in resultado["finales"] else "No"
            nombre = formatear_estado(est)
            
            tag = 'final' if es_final == "SÍ" else 'normal'
            tabla_nuevos_estados.insert("", tk.END, values=(nombre, es_inicial, es_final), tags=(tag,))

        for i, t in enumerate(resultado["transiciones"]):
            tag = 'par' if i % 2 == 0 else 'impar'
            origen = formatear_estado(t["de"])
            destino = formatear_estado(t["a"])
            tabla_nuevas_trans.insert("", tk.END, values=(origen, f"--({t['lee']})-->", destino), tags=(tag,))

        lbl_stats_conv.config(text=f"Proceso completado. Se generaron {len(resultado['estados'])} estados deterministas.")

    ttk.Button(frame_controles_conv, text="🔄 Ejecutar Algoritmo de Subconjuntos", command=ejecutar_conversion).pack(side=tk.LEFT, padx=10, ipady=4)
    lbl_stats_conv = ttk.Label(frame_controles_conv, text="Esperando ejecución...", font=("Segoe UI", 11, "bold"), foreground="#2b6cb0")
    lbl_stats_conv.pack(side=tk.LEFT, padx=20)

    frame_tablas_conv = ttk.Frame(tab4, padding=10)
    frame_tablas_conv.pack(fill='both', expand=True)

    frame_est_conv = ttk.LabelFrame(frame_tablas_conv, text=" Determinación de Estados AFD ")
    frame_est_conv.pack(side=tk.LEFT, fill='both', expand=True, padx=5)
    
    tabla_nuevos_estados = ttk.Treeview(frame_est_conv, columns=("nombre", "inicial", "final"), show="headings")
    tabla_nuevos_estados.heading("nombre", text="Nuevo Estado")
    tabla_nuevos_estados.heading("inicial", text="¿Es Inicial?")
    tabla_nuevos_estados.heading("final", text="¿Aceptación?")
    tabla_nuevos_estados.column("nombre", anchor='center', width=180)
    tabla_nuevos_estados.column("inicial", anchor='center', width=80)
    tabla_nuevos_estados.column("final", anchor='center', width=120)
    
    scroll_est_conv = ttk.Scrollbar(frame_est_conv, orient=tk.VERTICAL, command=tabla_nuevos_estados.yview)
    tabla_nuevos_estados.configure(yscroll=scroll_est_conv.set)
    scroll_est_conv.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_nuevos_estados.pack(fill='both', expand=True, padx=2, pady=2)
    
    tabla_nuevos_estados.tag_configure('normal', background='#ffffff')
    tabla_nuevos_estados.tag_configure('final', background='#e6ffed', foreground='#22543d')

    frame_trans_conv = ttk.LabelFrame(frame_tablas_conv, text=" Nueva Tabla de Transiciones AFD ")
    frame_trans_conv.pack(side=tk.RIGHT, fill='both', expand=True, padx=5)
    
    tabla_nuevas_trans = ttk.Treeview(frame_trans_conv, columns=("origen", "flecha", "destino"), show="headings")
    tabla_nuevas_trans.heading("origen", text="Estado Origen")
    tabla_nuevas_trans.heading("flecha", text="")
    tabla_nuevas_trans.heading("destino", text="Estado Destino")
    tabla_nuevas_trans.column("origen", anchor='center', width=150)
    tabla_nuevas_trans.column("flecha", anchor='center', width=60)
    tabla_nuevas_trans.column("destino", anchor='center', width=150)
    
    scroll_trans_conv = ttk.Scrollbar(frame_trans_conv, orient=tk.VERTICAL, command=tabla_nuevas_trans.yview)
    tabla_nuevas_trans.configure(yscroll=scroll_trans_conv.set)
    scroll_trans_conv.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_nuevas_trans.pack(fill='both', expand=True, padx=2, pady=2)
    tabla_nuevas_trans.tag_configure('par', background='#f7fafc')
    tabla_nuevas_trans.tag_configure('impar', background='#ffffff')

    # --- PESTAÑA 5: PRUEBAS MÚLTIPLES ---
    tab5 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab5, text=" Pruebas Múltiples ")

    frame_controles_lotes = ttk.Frame(tab5, padding=15)
    frame_controles_lotes.pack(fill='x')

    def cargar_y_probar_lote():
        ruta = ""
        item = ""
        cadenas = []
        aceptadas = 0
        rechazadas = 0
        i = 0
        cadena = ""
        cadena_a_probar = ""
        es_aceptada = False
        resultado_txt = ""
        tag = ""
        texto_mostrar = ""
        
        if not app_state["motor"]:
            messagebox.showwarning("Alto", "Carga un autómata en la Pestaña 1 primero.")
            return

        ruta = filedialog.askopenfilename(
            title="Selecciona el archivo de cadenas (.txt)", 
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if not ruta: return

        for item in tabla_lotes.get_children(): tabla_lotes.delete(item)

        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                cadenas = [linea.strip() for linea in f if linea.strip()] 

            for i, cadena in enumerate(cadenas):
                cadena_a_probar = "" if cadena.lower() in ["lambda", "λ", "epsilon"] else cadena

                es_aceptada, _ = app_state["motor"].simular_cadena_paso_a_paso(cadena_a_probar)
                
                if es_aceptada:
                    aceptadas += 1
                    resultado_txt = "Aceptada"
                    tag = 'aceptada'
                else:
                    rechazadas += 1
                    resultado_txt = "Rechazada"
                    tag = 'rechazada'
                
                texto_mostrar = cadena if cadena_a_probar else "λ (Cadena Vacía)"
                tabla_lotes.insert("", tk.END, values=(i+1, texto_mostrar, resultado_txt), tags=(tag,))

            lbl_stats_lotes.config(text=f"Total Evaluadas: {len(cadenas)} | Aceptadas: {aceptadas} | Rechazadas: {rechazadas}")
            messagebox.showinfo("Lote Finalizado", f"Se generó el informe para {len(cadenas)} cadenas exitosamente.")

        except Exception as e:
            messagebox.showerror("Error de Lectura", f"No se pudo procesar el archivo:\n{e}")

    ttk.Button(frame_controles_lotes, text="Cargar Archivo .TXT y Evaluar", command=cargar_y_probar_lote).pack(side=tk.LEFT, padx=10, ipady=4)
    lbl_stats_lotes = ttk.Label(frame_controles_lotes, text="Esperando archivo...", font=("Segoe UI", 11, "bold"), foreground="#2b6cb0")
    lbl_stats_lotes.pack(side=tk.LEFT, padx=20)

    frame_tabla_lotes = ttk.LabelFrame(tab5, text=" Informe de Evaluación por Lotes ")
    frame_tabla_lotes.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    tabla_lotes = ttk.Treeview(frame_tabla_lotes, columns=("num", "cadena", "resultado"), show="headings")
    tabla_lotes.heading("num", text="#")
    tabla_lotes.heading("cadena", text="Cadena Evaluada")
    tabla_lotes.heading("resultado", text="Resultado Final")
    
    tabla_lotes.column("num", anchor='center', width=50)
    tabla_lotes.column("cadena", anchor='center', width=400)
    tabla_lotes.column("resultado", anchor='center', width=150)

    scroll_lotes = ttk.Scrollbar(frame_tabla_lotes, orient=tk.VERTICAL, command=tabla_lotes.yview)
    tabla_lotes.configure(yscroll=scroll_lotes.set)
    scroll_lotes.pack(side=tk.RIGHT, fill=tk.Y)
    tabla_lotes.pack(fill='both', expand=True, padx=2, pady=2)

    tabla_lotes.tag_configure('aceptada', background='#e6ffed', foreground='#22543d')
    tabla_lotes.tag_configure('rechazada', background='#fff5f5', foreground='#9b2c2c')

    # ==========================================
    # PESTAÑA 6: CONVERSIÓN AFD -> ER (EJERCICIO 2)
    # ==========================================
    tab6 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab6, text=" Conversión AFD a ER ")

    frame_controles_er = ttk.Frame(tab6, padding=15)
    frame_controles_er.pack(fill='x')

    marco_visual_er = ttk.LabelFrame(tab6, text=" Proceso de Eliminación de Estados ", padding="10")
    marco_visual_er.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
    
    txt_pantalla_er = tk.Text(marco_visual_er, height=15, state=tk.DISABLED, font=("Consolas", 11), bg="#1a202c", fg="#63b3ed")
    txt_pantalla_er.pack(fill=tk.BOTH, expand=True)
    
    lbl_er_resultado = ttk.Label(tab6, text="Expresión Regular Resultante: [Esperando...]", font=("Segoe UI", 14, "bold"), foreground="#2b6cb0")
    lbl_er_resultado.pack(pady=10)

    def actualizar_pantalla_er(texto):
        txt_pantalla_er.config(state=tk.NORMAL)
        txt_pantalla_er.insert(tk.END, texto + "\n")
        txt_pantalla_er.see(tk.END)
        txt_pantalla_er.config(state=tk.DISABLED)

    def iniciar_conversion_er():
        datos = {}
        
        if not app_state["datos_json"]:
            messagebox.showwarning("Alto", "Carga un autómata en la Pestaña 1 primero.")
            return
            
        datos = app_state["datos_json"]
        app_state["convertidor_er"] = ConvertidorAFD_ER(datos)
        
        txt_pantalla_er.config(state=tk.NORMAL)
        txt_pantalla_er.delete(1.0, tk.END)
        txt_pantalla_er.config(state=tk.DISABLED)
        
        actualizar_pantalla_er("=== Iniciando Conversión a Expresión Regular ===")
        actualizar_pantalla_er(f"Estados a eliminar (orden): {app_state['convertidor_er'].estados_a_eliminar}")
        btn_paso_er.config(state=tk.NORMAL)
        lbl_er_resultado.config(text="Expresión Regular Resultante: [En proceso...]", foreground="#2b6cb0")

    def accion_paso_siguiente_er():
        motor_er = app_state["convertidor_er"]
        resultado = ""
        er_final = ""
        t = {}
        
        if motor_er:
            if motor_er.estados_a_eliminar:
                resultado = motor_er.ejecutar_siguiente_paso()
                actualizar_pantalla_er(f"\n--- {resultado} ---")
                for t in motor_er.transiciones:
                    actualizar_pantalla_er(f"δ({t['origen']}) --[ {t['lectura']} ]--> {t['destino']}")
            else:
                er_final = motor_er.ejecutar_siguiente_paso()
                actualizar_pantalla_er("\n=== CONVERSIÓN FINALIZADA ===")
                lbl_er_resultado.config(text=f"Expresión Regular Resultante: {er_final}", foreground="#38a169")
                btn_paso_er.config(state=tk.DISABLED)

    btn_iniciar_er = ttk.Button(frame_controles_er, text="🚀 Iniciar con AFD Actual", command=iniciar_conversion_er)
    btn_iniciar_er.pack(side=tk.LEFT, padx=10, ipady=4)
    
    btn_paso_er = ttk.Button(frame_controles_er, text="⏭️ Eliminar Siguiente Estado", command=accion_paso_siguiente_er, state=tk.DISABLED)
    btn_paso_er.pack(side=tk.LEFT, padx=10, ipady=4)

    # ==========================================
    # PESTAÑA 7: APLICACIÓN PRÁCTICA (EJERCICIO 3)
    # ==========================================
    tab7 = tk.Frame(notebook, bg="#f0f2f5")
    notebook.add(tab7, text=" Casos de Uso (Validadores) ")

    frame_controles_val = ttk.Frame(tab7, padding=15)
    frame_controles_val.pack(fill='x')

    ttk.Label(frame_controles_val, text="Selecciona el Validador:", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
    combo_val = ttk.Combobox(frame_controles_val, values=["Correo Electrónico", "Teléfono Nacional", "Contraseña Segura"], state="readonly", width=25, font=("Consolas", 11))
    combo_val.current(0)
    combo_val.pack(side=tk.LEFT, padx=10)

    marco_ingreso = ttk.Frame(tab7, padding=20)
    marco_ingreso.pack(fill='x')
    
    ttk.Label(marco_ingreso, text="Texto a Validar:", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
    entry_val = ttk.Entry(marco_ingreso, font=("Consolas", 14), width=40)
    entry_val.pack(side=tk.LEFT, padx=10)

    marco_resultados = ttk.LabelFrame(tab7, text=" Resultados y Retroalimentación ", padding="15")
    marco_resultados.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    lbl_patron = ttk.Label(marco_resultados, text="Expresión Regular:", font=("Consolas", 12), foreground="#2b6cb0")
    lbl_patron.pack(anchor='w', pady=5)
    
    lbl_res_val = ttk.Label(marco_resultados, text="Esperando entrada...", font=("Segoe UI", 16, "bold"))
    lbl_res_val.pack(anchor='w', pady=10)
    
    lbl_sugerencia = ttk.Label(marco_resultados, text="", font=("Segoe UI", 11, "italic"), foreground="#4a5568")
    lbl_sugerencia.pack(anchor='w', pady=5)

    def mostrar_afd_equivalente(tipo_val):
        ventana_afd = None
        txt_info = None
        texto_explicativo = ""

        ventana_afd = tk.Toplevel(root)
        ventana_afd.title(f"AFD Equivalente - {tipo_val}")
        ventana_afd.geometry("600x400")
        ventana_afd.configure(bg="#f0f2f5")

        txt_info = tk.Text(ventana_afd, font=("Consolas", 11), bg="#1a202c", fg="#63b3ed", padx=10, pady=10)
        txt_info.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        if tipo_val == "Correo Electrónico":
            texto_explicativo = (
                "ESTADOS DEL AFD (Simplificado):\n"
                "q0: Inicial\n"
                "q1: Leyendo usuario (acepta alfanuméricos y ._%+-)\n"
                "q2: Leyendo arroba (@)\n"
                "q3: Leyendo dominio (acepta alfanuméricos y .-)\n"
                "q4: Leyendo punto (.)\n"
                "q5: Leyendo sufijo (Estado Final, mínimo 2 letras)\n\n"
                "Transiciones principales:\n"
                "δ(q0, [a-z0-9]) -> q1\n"
                "δ(q1, '@') -> q2\n"
                "δ(q2, [a-z0-9]) -> q3\n"
                "δ(q3, '.') -> q4\n"
                "δ(q4, [a-z]) -> q5 (Repite en q5)"
            )
        elif tipo_val == "Teléfono Nacional":
            texto_explicativo = (
                "ESTADOS DEL AFD:\n"
                "q0: Inicial\n"
                "q1..q9: Leyendo dígitos del 1 al 9\n"
                "q10: Estado Final (10mo dígito leído)\n"
                "q_err: Sumidero (si lee letras o más de 10 dígitos)\n\n"
                "Transiciones principales:\n"
                "δ(qi, [0-9]) -> q_{i+1} para i de 0 a 9\n"
                "δ(q10, cualquier) -> q_err"
            )
        else:
            texto_explicativo = (
                "ESTADOS DEL AFD (Intersección de condiciones):\n"
                "Debido a la complejidad (Lookaheads), el AFD equivalente \n"
                "es el producto de tres autómatas más simples:\n"
                "1. Autómata que verifica longitud >= 8\n"
                "2. Autómata que busca al menos una mayúscula [A-Z]\n"
                "3. Autómata que busca al menos un dígito [0-9]\n\n"
                "El estado final es la intersección donde los tres \n"
                "autómatas alcanzan su estado de aceptación."
            )

        txt_info.insert(tk.END, texto_explicativo)
        txt_info.config(state=tk.DISABLED)

    def ejecutar_validacion():
        texto = ""
        tipo = ""
        patron = ""
        es_valido = False
        sugerencia = ""

        texto = entry_val.get()
        tipo = combo_val.get()

        if tipo == "Correo Electrónico":
            patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            sugerencia = "Faltan componentes. Formato esperado: usuario@dominio.com\nRevisa el uso del '@' y el sufijo (ej. '.mx')."
        elif tipo == "Teléfono Nacional":
            patron = r"^\d{10}$"
            sugerencia = "Debe contener exactamente 10 dígitos numéricos consecutivos.\nEjemplo válido: 5512345678."
        else:
            patron = r"^(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$"
            sugerencia = "La contraseña debe tener:\n- Mínimo 8 caracteres\n- Al menos una letra mayúscula\n- Al menos un número."

        lbl_patron.config(text=f"Expresión Regular: {patron}")
        
        es_valido = bool(re.match(patron, texto))

        if es_valido:
            lbl_res_val.config(text="✓ TEXTO VÁLIDO", foreground="#38a169")
            lbl_sugerencia.config(text="El texto cumple perfectamente con el patrón especificado.", foreground="#2f855a")
        else:
            lbl_res_val.config(text="✗ TEXTO INVÁLIDO", foreground="#e53e3e")
            lbl_sugerencia.config(text=f"Sugerencia de corrección:\n{sugerencia}", foreground="#9b2c2c")

    ttk.Button(marco_ingreso, text="✔️ Validar Entrada", command=ejecutar_validacion).pack(side=tk.LEFT, padx=10, ipady=4)
    ttk.Button(marco_ingreso, text="👁️ Ver AFD Equivalente", command=lambda: mostrar_afd_equivalente(combo_val.get())).pack(side=tk.LEFT, padx=10, ipady=4)

    root.mainloop()

if __name__ == "__main__":
    main()