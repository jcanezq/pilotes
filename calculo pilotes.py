#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Título: Cálculo de Cimentaciones con Pilotes
Descripción: Módulo interactivo que implementa métodos teóricos y dinámicos 
             para estimar la capacidad de carga última de pilotes en arena y
             arcilla, basados en el Capítulo 11 de 'Cimentaciones con pilotes'.
=============================================================================
"""

import math

def meyerhof_punta_arena(Nq_star, phi_grados, pa, L, D, Ap):
    """
    Calcula la capacidad de punta última (Qp) en arena usando el método de Meyerhof.
    
    Parámetros:
    Nq_star : Factor de capacidad de carga de Meyerhof (de tabla/gráfica)
    phi_grados : Ángulo de fricción del suelo en grados
    pa : Presión atmosférica (aprox. 100 kN/m2)
    L : Longitud de empotramiento del pilote
    D : Diámetro o ancho del pilote
    Ap : Área de la sección transversal de la punta del pilote
    """
    phi_rad = math.radians(phi_grados)
    
    # Límite q_l
    ql = 0.5 * pa * Nq_star * math.tan(phi_rad)
    
    # Capacidad teórica (asumiendo q' = peso_especifico * L, pero sin conocer gamma, usamos el límite)
    # En la práctica, se calcularía q' * Nq_star y se limita por ql.
    # Esta función retorna el valor máximo posible (límite) por seguridad.
    Qp_limite = Ap * ql
    return Qp_limite


def capacidad_punta_arcilla(cu, Ap):
    """
    Calcula la capacidad de punta última (Qp) en arcilla saturada (phi = 0).
    
    Parámetros:
    cu : Cohesión no drenada en la punta del pilote (kN/m2)
    Ap : Área de la punta (m2)
    """
    Nc_star = 9.0
    return Ap * cu * Nc_star


def friccion_arena_spt(N60, pa, perimetro, L, alto_desplazamiento=True):
    """
    Estima la resistencia por fricción (Qs) en arena basado en correlaciones SPT (Meyerhof).
    
    Parámetros:
    N60 : Valor promedio de penetración estándar
    pa : Presión atmosférica (100 kN/m2)
    perimetro : Perímetro de la sección del pilote (m)
    L : Longitud del pilote (m)
    alto_desplazamiento : Booleano, True para pilotes hincados de alto desplazamiento (concreto, tubo cerrado)
                          False para pilotes de bajo desplazamiento (perfil H)
    """
    if alto_desplazamiento:
        f_prom = 0.02 * pa * N60
    else:
        f_prom = 0.01 * pa * N60
        
    return perimetro * L * f_prom


def friccion_arcilla_metodo_alfa(alpha, cu, perimetro, L):
    """
    Calcula la resistencia superficial (Qs) en arcilla usando el método alfa.
    
    Parámetros:
    alpha : Factor empírico de adhesión
    cu : Cohesión no drenada promedio a lo largo del fuste (kN/m2)
    perimetro : Perímetro del pilote (m)
    L : Longitud (m)
    """
    f = alpha * cu
    return perimetro * L * f


def formula_hincado_enr_modificada(E, W_R, h, S, C, n, W_p):
    """
    Estima la capacidad última del pilote (Qu) mediante la fórmula ENR modificada durante el hincado.
    
    Parámetros:
    E : Eficiencia del martinete (ej. 0.7 - 0.9)
    W_R : Peso del ariete (kN)
    h : Altura de caída del ariete (mm)
    S : Penetración promedio por golpe (mm)
    C : Constante (2.54 mm para martinetes de vapor, 25.4 mm caída libre)
    n : Coeficiente de restitución (ej. 0.4 - 0.5)
    W_p : Peso del pilote y casquete (kN)
    """
    energia = E * W_R * h
    termino_pesos = (W_R + (n**2) * W_p) / (W_R + W_p)
    Qu = (energia / (S + C)) * termino_pesos
    return Qu

def run_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox
    import math

    def calcular_arcilla():
        try:
            diametro = float(ent_diametro.get())
            longitud = float(ent_longitud.get())
            cu_suelo = float(ent_cu.get())
            alpha_suelo = float(ent_alpha.get())
            
            area = (math.pi * diametro**2) / 4
            perimetro = math.pi * diametro
            
            Qp = capacidad_punta_arcilla(cu_suelo, area)
            Qs = friccion_arcilla_metodo_alfa(alpha_suelo, cu_suelo, perimetro, longitud)
            Qu = Qp + Qs
            
            resultados = (
                "--- Resultados: Cálculo en Arcilla ---\n"
                f"Diámetro: {diametro} m, Longitud: {longitud} m\n"
                f"Cohesión (cu): {cu_suelo} kN/m2, Alfa: {alpha_suelo}\n"
                "----------------------------------------\n"
                f"Resistencia de punta (Qp): {Qp:.2f} kN\n"
                f"Fricción lateral (Qs):   {Qs:.2f} kN\n"
                f"Capacidad última total (Qu): {Qu:.2f} kN\n"
            )
            txt_resultados.delete(1.0, tk.END)
            txt_resultados.insert(tk.END, resultados)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos en todos los campos.")

    def calcular_enr():
        try:
            E = float(ent_e.get())
            W_R = float(ent_wr.get())
            h = float(ent_h.get())
            S = float(ent_s.get())
            C = float(ent_c.get())
            n = float(ent_n.get())
            W_p = float(ent_wp.get())
            
            Qu = formula_hincado_enr_modificada(E, W_R, h, S, C, n, W_p)
            
            resultados = (
                "--- Resultados: Fórmula ENR Modificada ---\n"
                f"Eficiencia: {E}, Peso ariete: {W_R} kN, Altura caída: {h} mm\n"
                f"Penetración: {S} mm, Constante C: {C} mm\n"
                f"Restitución n: {n}, Peso pilote: {W_p} kN\n"
                "------------------------------------------\n"
                f"Capacidad última (Qu) durante el hincado: {Qu:.2f} kN\n"
            )
            txt_resultados.delete(1.0, tk.END)
            txt_resultados.insert(tk.END, resultados)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos en todos los campos.")

    def calcular_spt():
        try:
            diametro = float(ent_diametro_spt.get())
            longitud = float(ent_longitud_spt.get())
            pa = float(ent_pa_spt.get())
            n60 = float(ent_n60_spt.get())
            
            area = (math.pi * diametro**2) / 4
            perimetro = math.pi * diametro
            
            # Qp
            L_D = longitud / diametro
            qp_calculado = 0.4 * pa * n60 * L_D
            qp_limite = 4 * pa * n60
            qp = min(qp_calculado, qp_limite)
            Qp = area * qp
            
            # Qs (asumiendo alto desplazamiento)
            Qs = friccion_arena_spt(n60, pa, perimetro, longitud, alto_desplazamiento=True)
            Qu = Qp + Qs
            
            resultados = (
                "--- Resultados: Cálculo SPT en Arena (Meyerhof) ---\n"
                f"Diámetro: {diametro} m, Longitud: {longitud} m\n"
                f"N60: {n60}, pa: {pa} kN/m2\n"
                "---------------------------------------------------\n"
                f"Resistencia de punta (Qp): {Qp:.2f} kN\n"
                f"Fricción lateral (Qs):   {Qs:.2f} kN\n"
                f"Capacidad última total (Qu): {Qu:.2f} kN\n"
            )
            txt_resultados.delete(1.0, tk.END)
            txt_resultados.insert(tk.END, resultados)
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos en todos los campos.")

    root = tk.Tk()
    root.title("Cálculo de Cimentaciones con Pilotes")
    
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    style.configure('TNotebook.Tab', padding=[15, 8], font=('Segoe UI', 10, 'bold'))
    style.map('TNotebook.Tab',
              background=[('selected', '#005fb8'), ('!selected', '#e1e1e1')],
              foreground=[('selected', 'white'), ('!selected', 'black')])
    
    notebook = ttk.Notebook(root)
    notebook.pack(padx=10, pady=10, expand=True, fill='both')

    # Frame Arcilla
    frame_arcilla = ttk.Frame(notebook)
    frame_arcilla.pack(fill='both', expand=True)
    notebook.add(frame_arcilla, text='Arcilla (Método Alfa)')
    
    ttk.Label(frame_arcilla, text="Diámetro del pilote (m):").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    ent_diametro = ttk.Entry(frame_arcilla)
    ent_diametro.grid(row=0, column=1, padx=10, pady=10)
    
    ttk.Label(frame_arcilla, text="Longitud del pilote (m):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    ent_longitud = ttk.Entry(frame_arcilla)
    ent_longitud.grid(row=1, column=1, padx=10, pady=10)
    
    ttk.Label(frame_arcilla, text="Cohesión cu (kN/m2):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    ent_cu = ttk.Entry(frame_arcilla)
    ent_cu.grid(row=2, column=1, padx=10, pady=10)
    
    ttk.Label(frame_arcilla, text="Factor de adhesión alfa:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    ent_alpha = ttk.Entry(frame_arcilla)
    ent_alpha.grid(row=3, column=1, padx=10, pady=10)
    
    ttk.Button(frame_arcilla, text="Calcular", command=calcular_arcilla).grid(row=4, column=0, columnspan=2, pady=20)

    # Frame ENR
    frame_enr = ttk.Frame(notebook)
    frame_enr.pack(fill='both', expand=True)
    notebook.add(frame_enr, text='Fórmula ENR')
    
    ttk.Label(frame_enr, text="Eficiencia del martinete (E):").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    ent_e = ttk.Entry(frame_enr)
    ent_e.grid(row=0, column=1, padx=10, pady=5)
    
    ttk.Label(frame_enr, text="Peso del ariete W_R (kN):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    ent_wr = ttk.Entry(frame_enr)
    ent_wr.grid(row=1, column=1, padx=10, pady=5)
    
    ttk.Label(frame_enr, text="Altura de caída h (mm):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    ent_h = ttk.Entry(frame_enr)
    ent_h.grid(row=2, column=1, padx=10, pady=5)
    
    ttk.Label(frame_enr, text="Penetración S (mm):").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    ent_s = ttk.Entry(frame_enr)
    ent_s.grid(row=3, column=1, padx=10, pady=5)
    
    ttk.Label(frame_enr, text="Constante C (mm):").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    ent_c = ttk.Entry(frame_enr)
    ent_c.grid(row=4, column=1, padx=10, pady=5)
    
    ttk.Label(frame_enr, text="Restitución n:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
    ent_n = ttk.Entry(frame_enr)
    ent_n.grid(row=5, column=1, padx=10, pady=5)

    ttk.Label(frame_enr, text="Peso del pilote W_p (kN):").grid(row=6, column=0, padx=10, pady=5, sticky='e')
    ent_wp = ttk.Entry(frame_enr)
    ent_wp.grid(row=6, column=1, padx=10, pady=5)
    
    ttk.Button(frame_enr, text="Calcular", command=calcular_enr).grid(row=7, column=0, columnspan=2, pady=15)
    
    # Frame SPT
    frame_spt = ttk.Frame(notebook)
    frame_spt.pack(fill='both', expand=True)
    notebook.add(frame_spt, text='Arena (SPT Meyerhof)')
    
    ttk.Label(frame_spt, text="Diámetro del pilote (m):").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    ent_diametro_spt = ttk.Entry(frame_spt)
    ent_diametro_spt.grid(row=0, column=1, padx=10, pady=10)
    
    ttk.Label(frame_spt, text="Longitud del pilote (m):").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    ent_longitud_spt = ttk.Entry(frame_spt)
    ent_longitud_spt.grid(row=1, column=1, padx=10, pady=10)
    
    ttk.Label(frame_spt, text="Presión atmosférica pa (kN/m2):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    ent_pa_spt = ttk.Entry(frame_spt)
    ent_pa_spt.insert(0, "100")
    ent_pa_spt.grid(row=2, column=1, padx=10, pady=10)
    
    ttk.Label(frame_spt, text="N60 promedio:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    ent_n60_spt = ttk.Entry(frame_spt)
    ent_n60_spt.grid(row=3, column=1, padx=10, pady=10)
    
    ttk.Button(frame_spt, text="Calcular", command=calcular_spt).grid(row=4, column=0, columnspan=2, pady=20)
    
    # Frame Resultados
    frame_res = ttk.LabelFrame(root, text="Resultados y Reporte")
    frame_res.pack(fill='both', expand=True, padx=10, pady=10)
    
    txt_resultados = tk.Text(frame_res, height=10, width=60)
    txt_resultados.pack(padx=10, pady=10)
    
    # Centrar la ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.mainloop()

if __name__ == "__main__":
    run_gui()
